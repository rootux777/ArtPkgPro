"""Local ArtPkg intake web UI server with authentication and ownership enforcement."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import threading
import webbrowser
import weakref
from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

import artpkg_intake
import artpkg_archify_projection
import artpkg_archify_runner
import artpkg_intake_auth
import artpkg_pipeline_admission
import artpkg_sealed_handoff
import artpkg_dsh_bridge
import artpkg_coding_handoff
import artpkg_ux_preparation


# 10 MiB limit for uploads (in bytes)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


# Process-local locks for ThreadingHTTPServer. Weak values bound the registry to
# active requests; each caller keeps a strong reference while waiting/holding.
_SESSION_LOCKS: weakref.WeakValueDictionary[Path, Any] = weakref.WeakValueDictionary()
_SESSION_LOCKS_GUARD = threading.Lock()


def _session_lock(resolved_session_dir: Path):
    """Return a shared RLock for an already canonical, owner-checked path."""
    with _SESSION_LOCKS_GUARD:
        lock = _SESSION_LOCKS.get(resolved_session_dir)
        if lock is None:
            lock = threading.RLock()
            _SESSION_LOCKS[resolved_session_dir] = lock
        return lock


@dataclass
class UploadedFile:
    filename: str
    content: bytes
    content_type: str


def pipeline_admission_status(sealing: dict[str, Any]) -> dict[str, Any]:
    configuration = artpkg_pipeline_admission.configuration_status()
    unmet = list(sealing.get("seal_blockers", [])) + list(configuration["unmet_conditions"])
    return {
        **configuration,
        "eligible": sealing.get("completion_result") == "READY_TO_SEAL" and not unmet,
        "unmet_conditions": unmet,
    }


def parse_multipart_upload(content_type: str, body: bytes) -> UploadedFile:
    headers = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
    message = BytesParser(policy=default).parsebytes(headers + body)
    for part in message.iter_parts():
        disposition = part.get_content_disposition()
        if disposition == "form-data" and part.get_param("name", header="content-disposition") == "file":
            filename = part.get_filename() or "pre-artifacts.md"
            return UploadedFile(filename=filename, content=part.get_payload(decode=True) or b"", content_type=part.get_content_type())
    raise ValueError("multipart upload did not include file")


def session_summary(session: dict[str, Any], reviewer: str | None = None) -> dict[str, Any]:
    queues = session.get("review_queues", {})
    summary = {
        "session_id": session.get("session_id"),
        "session_dir": session.get("session_dir"),
        "source": session.get("source"),
        "validation": session.get("validation"),
        "review_queues": queues,
        "queue_counts": {name: len(items) for name, items in queues.items()},
        "question_plan": session.get("question_plan"),
        "review_summary": session.get("review_summary"),
        "human_work_counts": session.get("human_work_counts"),
        "answers_path": session.get("answers_path"),
        "ux_resolution": artpkg_ux_preparation.resolution_status(session.get("document", {"answers": {}})),
    }
    if reviewer is not None:
        try:
            sealing = artpkg_sealed_handoff.review_package(session, reviewer)
            summary["sealing"] = sealing
            pipeline_status = pipeline_admission_status(sealing)
            summary["pipeline_admission"] = pipeline_status
            if pipeline_status["available"] and sealing.get("sealed"):
                existing = artpkg_pipeline_admission.existing_admission(
                    package_id=sealing["package_id"],
                    package_version=sealing["package_version"],
                    submission_id=sealing["submission_id"],
                    package_sha256=sealing["sealed_id"],
                )
                if existing is not None:
                    summary["pipeline_admission"]["result"] = existing
        except artpkg_sealed_handoff.HandoffError as exc:
            completion = artpkg_sealed_handoff.completion_summary(session["document"], session["validation"])
            summary["sealing"] = {**completion, "completion_result": "BLOCKED", "seal_blockers": [str(exc)]}
            summary["pipeline_admission"] = pipeline_admission_status(summary["sealing"])
        except artpkg_pipeline_admission.AdmissionError as exc:
            summary["pipeline_admission"] = {
                **pipeline_status,
                "available": False,
                "eligible": False,
                "unmet_conditions": [str(exc)],
            }
        summary["dsh_handoff"] = artpkg_dsh_bridge.status(session, reviewer)
    return summary


def sealed_zip_response(session_dir: str, sealed_id: str, username: str, workspace: str | Path) -> tuple[dict[str, str], bytes]:
    resolved = resolve_session_dir_with_owner(session_dir, username, workspace)
    with _session_lock(resolved):
        files = artpkg_sealed_handoff.load_sealed_files(resolved, sealed_id)
        body = artpkg_sealed_handoff.deterministic_zip(files)
    headers = {
        "Content-Type": "application/zip",
        "Content-Disposition": f'attachment; filename="artpkg-sealed-{sealed_id}.zip"',
        "Content-Length": str(len(body)),
    }
    return headers, body


def resolve_session_dir(session_dir: str, workspace: str | Path) -> Path:
    intake_sessions_dir = (Path(workspace).expanduser().resolve() / ".artpkg" / "intake_sessions").resolve()
    resolved_session_dir = Path(session_dir).expanduser().resolve()
    try:
        resolved_session_dir.relative_to(intake_sessions_dir)
    except ValueError as exc:
        raise ValueError("session directory is outside the configured intake sessions directory") from exc
    return resolved_session_dir


def resolve_session_dir_with_owner(session_dir: str, username: str, workspace: str | Path) -> Path:
    """
    Resolve session directory and enforce per-user ownership.
    
    Session directory must be:
    1. Within the user's namespace
    2. Formatted as .artpkg/users/{username}/sessions/{session_id}
    
    Raises ValueError if session is outside user's namespace.
    """
    workspace_path = Path(workspace).expanduser().resolve()
    user_sessions_dir = (workspace_path / ".artpkg" / "users" / username / "sessions").resolve()
    
    resolved_session_dir = Path(session_dir).expanduser().resolve()
    
    try:
        resolved_session_dir.relative_to(user_sessions_dir)
    except ValueError as exc:
        raise ValueError("session directory is outside the authenticated user's namespace") from exc
    
    return resolved_session_dir


def load_workspace_session(session_dir: str, workspace: str | Path) -> dict[str, Any]:
    resolved_session_dir = resolve_session_dir(session_dir, workspace)
    session = artpkg_intake.load_intake_session(resolved_session_dir)
    session["session_dir"] = str(resolved_session_dir)
    return session


def load_workspace_session_with_owner(session_dir: str, username: str, workspace: str | Path) -> dict[str, Any]:
    """
    Load session for authenticated user, enforcing ownership.
    
    Raises ValueError if session is outside user's namespace.
    """
    resolved_session_dir = resolve_session_dir_with_owner(session_dir, username, workspace)
    session = artpkg_intake.load_intake_session(resolved_session_dir)
    session["session_dir"] = str(resolved_session_dir)
    return session


def _relocate_paths(value: Any, old_root: Path, new_root: Path) -> Any:
    if isinstance(value, dict):
        return {key: _relocate_paths(item, old_root, new_root) for key, item in value.items()}
    if isinstance(value, list):
        return [_relocate_paths(item, old_root, new_root) for item in value]
    if isinstance(value, str):
        old_prefix = str(old_root)
        if value == old_prefix or value.startswith(old_prefix + os.sep):
            return str(new_root) + value[len(old_prefix):]
    return value


def create_intake_session_for_user(source: Path, username: str, workspace: str | Path, template_path: Path | None = None) -> dict[str, Any]:
    """
    Create a new intake session in the user's namespace.
    
    Session directory will be: .artpkg/users/{username}/sessions/{session_id}
    
    Creates session using artpkg_intake, then moves it to user namespace.
    """
    workspace_path = Path(workspace).expanduser().resolve()
    user_sessions_dir = (workspace_path / ".artpkg" / "users" / username / "sessions").resolve()
    
    # Create session using normal artpkg_intake path first
    session = artpkg_intake.create_intake_session(source, workspace, template_path=template_path)
    
    # Move session to user namespace
    old_session_dir = Path(session["session_dir"])
    session_id = old_session_dir.name
    new_session_dir = user_sessions_dir / session_id
    
    # Create user sessions directory if it doesn't exist
    user_sessions_dir.mkdir(parents=True, exist_ok=True)
    
    # Move the session directory
    shutil.move(str(old_session_dir), str(new_session_dir))
    
    # Relocate session metadata and provenance paths rooted in the old directory.
    session = _relocate_paths(session, old_session_dir, new_session_dir)
    for filename in ("answers.json", "seed.json"):
        path = new_session_dir / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        relocated = _relocate_paths(payload, old_session_dir, new_session_dir)
        path.write_text(json.dumps(relocated, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    
    # Update the session.json file to reflect new path
    artpkg_intake.save_intake_session(session)
    
    return session


def projection_html_response(
    session_dir: str,
    workspace: str | Path,
    username: str | None = None,
) -> tuple[int, dict[str, str], bytes]:
    resolved_session_dir = (
        resolve_session_dir_with_owner(session_dir, username, workspace)
        if username is not None
        else resolve_session_dir(session_dir, workspace)
    )
    with _session_lock(resolved_session_dir):
        html_path = resolved_session_dir / "artpkg-readiness.architecture.html"
        if not html_path.exists():
            raise FileNotFoundError("projection HTML has not been generated")
        body = html_path.read_bytes()
    return 200, {"Content-Type": "text/html; charset=utf-8", "Content-Length": str(len(body))}, body


def decorate_projection_html(html_path: str | Path, mapping_path: str | Path) -> None:
    target = Path(html_path)
    mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    payload = {
        "session_dir": mapping.get("session_dir"),
        "nodes": {
            node.get("archify_id"): node.get("artpkg_review_action")
            for node in mapping.get("nodes", [])
            if node.get("archify_id") and node.get("artpkg_review_action")
        },
    }
    if not payload["nodes"]:
        return
    page = target.read_text(encoding="utf-8")
    if "artpkg-review-actions-data" in page:
        return
    data = json.dumps(payload, ensure_ascii=True).replace("</", "<\\/")
    injection = f"""
<style id="artpkg-review-actions-style">
  .artpkg-review-panel {{ border-top:1px solid rgba(125, 211, 252, .35); margin-top:12px; padding-top:10px; display:grid; gap:7px; }}
  .artpkg-review-panel[hidden] {{ display:none; }}
  .artpkg-review-eyebrow {{ color:#7dd3fc; font-size:10px; font-weight:800; letter-spacing:.09em; text-transform:uppercase; }}
  .artpkg-review-panel p {{ margin:0; color:#c8d7e3; font-size:12px; line-height:1.35; }}
  .artpkg-review-panel a {{ display:inline-flex; width:max-content; border:1px solid #7dd3fc; border-radius:4px; padding:6px 8px; color:#e8f7ff; text-decoration:none; font-size:12px; font-weight:800; }}
</style>
<script id="artpkg-review-actions-data" type="application/json">{data}</script>
<script>
(function () {{
  var dataElement = document.getElementById('artpkg-review-actions-data');
  if (!dataElement) return;
  var data = JSON.parse(dataElement.textContent || '{{}}');
  var chip = document.getElementById('focus-chip');
  if (!chip) return;
  var panel = document.createElement('div');
  panel.className = 'artpkg-review-panel';
  panel.setAttribute('data-artpkg-review-panel', '');
  panel.hidden = true;
  chip.appendChild(panel);
  function hrefFor(action) {{
    var query = new URLSearchParams();
    if (data.session_dir) query.set('dir', data.session_dir);
    if (action.queue) query.set('queue', action.queue);
    if (action.focus) query.set('focus', action.focus);
    return '/?' + query.toString();
  }}
  function render(nodeId) {{
    var action = data.nodes && data.nodes[nodeId];
    panel.textContent = '';
    if (!action) {{ panel.hidden = true; return; }}
    panel.hidden = false;
    var eyebrow = document.createElement('span');
    eyebrow.className = 'artpkg-review-eyebrow';
    eyebrow.textContent = 'ArtPkg review';
    var summary = document.createElement('p');
    summary.textContent = action.summary || 'Open the related ArtPkg review item.';
    var impact = document.createElement('p');
    impact.textContent = action.impact || 'Review this before changing downstream readiness.';
    var link = document.createElement('a');
    var href = hrefFor(action);
    link.href = href;
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = action.label || 'Open in ArtPkg';
    link.addEventListener('click', function (event) {{
      event.preventDefault();
      window.open(href, '_blank', 'noopener');
    }});
    panel.appendChild(eyebrow);
    panel.appendChild(summary);
    panel.appendChild(impact);
        if (action.focus) {{
            panel.appendChild(link);
        }} else {{
            var unavailable = document.createElement('p');
            unavailable.textContent = 'No matching open review item currently maps to this card. Regenerate the visualization after review changes.';
            panel.appendChild(unavailable);
        }}
  }}
  document.addEventListener('click', function (event) {{
    var node = event.target.closest && event.target.closest('[data-node-id]');
    if (node) setTimeout(function () {{ render(node.getAttribute('data-node-id')); }}, 0);
  }}, true);
  document.addEventListener('keyup', function (event) {{
    if (event.key !== 'Enter' && event.key !== ' ') return;
    var node = event.target.closest && event.target.closest('[data-node-id]');
    if (node) setTimeout(function () {{ render(node.getAttribute('data-node-id')); }}, 0);
  }}, true);
  window.addEventListener('hashchange', function () {{
    var match = String(location.hash || '').match(/focus=([^&]+)/);
    if (match) render(decodeURIComponent(match[1]));
  }});
}}());
</script>
"""
    marker = "</body>"
    if marker in page:
        page = page.replace(marker, injection + "\n" + marker, 1)
    else:
        page += injection
    target.write_text(page, encoding="utf-8")


def archify_config_for_session(session: dict[str, Any]) -> artpkg_archify_runner.ArchifyConfig:
    return artpkg_archify_runner.ArchifyConfig(
        node_executable=os.environ.get("ARTPKG_NODE", "node"),
        archify_root=os.environ.get("ARTPKG_ARCHIFY_ROOT", ""),
        quality=os.environ.get("ARTPKG_ARCHIFY_QUALITY", "showcase"),
        receipt_dir=session["session_dir"],
    )


def build_projection_summary(session: dict[str, Any]) -> dict[str, Any]:
    result = artpkg_archify_projection.build_readiness_projection(session)
    config = archify_config_for_session(session)
    html_path = str(Path(result.ir_path).with_suffix(".html"))
    validate = artpkg_archify_runner.run_archify_validate(config, "architecture", result.ir_path)
    Path(html_path).unlink(missing_ok=True)
    deliver = artpkg_archify_runner.run_archify_deliver(config, "architecture", result.ir_path, html_path)
    if deliver.get("ok") is True and Path(html_path).exists():
        decorate_projection_html(html_path, result.mapping_path)
    visual = artpkg_archify_runner.run_archify_visual_check(config, html_path) if deliver.get("ok") is True and Path(html_path).exists() else {
        "ok": False,
        "operation": "visual-check",
        "receipt": {"ok": False, "error": "Archify deliver did not create fresh HTML"},
    }
    ready = deliver.get("ok") is True and Path(html_path).exists()
    error = None if ready else (
        deliver.get("receipt", {}).get("error")
        or deliver.get("stderr")
        or "Archify deliver did not create fresh HTML"
    )
    return {
        "ready": ready,
        "error": error,
        "ir_path": result.ir_path,
        "mapping_path": result.mapping_path,
        "validation_path": result.validation_path,
        "html_path": html_path,
        "archify": {
            "validate": validate,
            "deliver": deliver,
            "visual_check": visual,
        },
    }


class IntakeHandler(BaseHTTPRequestHandler):
    workspace = Path.cwd()
    template_path: Path | None = None

    def _get_authenticated_user(self) -> Optional[str]:
        """
        Extract and validate authenticated user from Authorization header.
        
        Returns username if valid, None otherwise.
        Never logs the header value or decoded credentials.
        """
        auth_header = self.headers.get('Authorization', '')
        username = artpkg_intake_auth.validate_basic_auth(auth_header)
        return username

    def _send_auth_required(self) -> None:
        """Send 401 Unauthorized response."""
        body = json.dumps({"error": "unauthorized"}, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"ArtPkg Intake\"")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_forbidden(self) -> None:
        """Send 403 Forbidden response."""
        body = json.dumps({"error": "forbidden"}, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")
        self.send_response(403)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_payload_too_large(self) -> None:
        """Send 413 Payload Too Large response."""
        body = json.dumps({"error": f"payload too large (max {MAX_UPLOAD_SIZE // (1024*1024)}MiB)"}, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")
        self.send_response(413)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        # Authenticate all GET requests
        username = self._get_authenticated_user()
        if not username:
            self._send_auth_required()
            return
        
        parsed = urlparse(self.path)
        
        if parsed.path in {"/", "/review", "/ux"}:
            try:
                name = ("artpkg_ux_preparation.html" if parsed.path == "/ux" else
                        "artpkg_final_review.html" if parsed.path == "/review" else "artpkg_intake_ui.html")
                html = (Path(__file__).with_name(name)).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
            except Exception as exc:
                self._json(500, {"error": str(exc)})
            return
        
        if parsed.path == "/api/session/ux":
            try:
                params = parse_qs(parsed.query)
                try:
                    resolved = resolve_session_dir_with_owner(params.get("dir", [""])[0], username, self.workspace)
                except ValueError:
                    self._send_forbidden()
                    return
                # Unlike legacy path handling, the new operations reject links and
                # traversal in the original spelling before any filesystem access.
                artpkg_ux_preparation.runtime()
                from ux_harness.paths import safe_path
                safe_path(params.get("dir", [""])[0])
                with _session_lock(resolved):
                    session = load_workspace_session_with_owner(str(resolved), username, self.workspace)
                    operation = params.get("op", ["export"])[0]
                    if operation in {"template", "prompt"}:
                        name = "template_ux_ui_package.md" if operation == "template" else "UX-UI-AGENT-PROMPT.md"
                        result = {"filename": name, "content": (artpkg_ux_preparation.UXPKG_ROOT / "templates" / name).read_text(encoding="utf-8")}
                    elif operation == "export":
                        result = artpkg_ux_preparation.requirements_export(session)
                    elif operation in {"preview", "verify", "resolution"}:
                        coordinator = artpkg_ux_preparation.Preparation(session, username)
                        upload_id = params.get("upload_id", [""])[0]
                        result = (coordinator.preview(upload_id) if operation == "preview" else
                                  coordinator.resolution_questionnaire(upload_id) if operation == "resolution" else
                                  coordinator.verify(upload_id))
                    else:
                        raise ValueError("unknown UX preparation operation")
                self._json(200, result)
            except Exception as exc:
                self._json(400, {"error": str(exc)})
            return

        if parsed.path in {"/api/session", "/api/session/final-review"}:
            try:
                params = parse_qs(parsed.query)
                session_dir = params.get("dir", [""])[0]
                
                # Enforce ownership
                try:
                    resolved = resolve_session_dir_with_owner(session_dir, username, self.workspace)
                except ValueError:
                    self._send_forbidden()
                    return

                with _session_lock(resolved):
                    try:
                        session = load_workspace_session_with_owner(str(resolved), username, self.workspace)
                    except ValueError:
                        self._send_forbidden()
                        return
                    summary = (artpkg_coding_handoff.review_preview(session, username)
                               if parsed.path.endswith("final-review") else session_summary(session, username))
                
                self._json(200, summary)
            except Exception as exc:
                self._json(400, {"error": str(exc)})
            return

        if parsed.path == "/api/session/sealed-download":
            try:
                params = parse_qs(parsed.query)
                headers, body = sealed_zip_response(
                    params.get("dir", [""])[0], params.get("sealed", [""])[0], username, self.workspace,
                )
                self.send_response(200)
                for name, value in headers.items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self._json(404, {"error": str(exc)})
            return
        
        if parsed.path == "/api/session/projection-html":
            try:
                params = parse_qs(parsed.query)
                session_dir = params.get("dir", [""])[0]
                
                # Enforce ownership
                try:
                    resolve_session_dir_with_owner(session_dir, username, self.workspace)
                except ValueError:
                    self._send_forbidden()
                    return
                
                status, headers, body = projection_html_response(session_dir, self.workspace, username)
                self.send_response(status)
                for name, value in headers.items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self._json(404, {"error": str(exc)})
            return
        
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        # Authenticate all POST requests
        username = self._get_authenticated_user()
        if not username:
            self._send_auth_required()
            return
        
        # Check Content-Length before reading body
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "invalid Content-Length"})
            return
        
        if content_length > MAX_UPLOAD_SIZE:
            self._send_payload_too_large()
            return
        
        session_lock = None
        try:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/session/ux-"):
                origin = self.headers.get("Origin")
                if (self.headers.get_content_type() != "application/json"
                        or self.headers.get("X-ArtPkg-UX") != "1"
                        or self.headers.get("Sec-Fetch-Site") == "cross-site"
                        or (origin is not None and origin != "http://" + self.headers.get("Host", ""))):
                    self._send_forbidden()
                    return
                if content_length < 1 or content_length > 2 * 512 * 1024:
                    self._send_payload_too_large()
                    return
            body = self.rfile.read(content_length)
            
            if parsed.path == "/api/intake":
                upload_dir = None
                try:
                    upload = parse_multipart_upload(self.headers.get("Content-Type", ""), body)
                    if Path(upload.filename).suffix.lower() not in {".md", ".markdown", ".txt"}:
                        raise ValueError("unsupported upload type")
                    
                    # Create temporary upload directory
                    upload_dir = Path(tempfile.mkdtemp(prefix="artpkg-upload-"))
                    source = upload_dir / Path(upload.filename).name
                    source.write_bytes(upload.content)
                    
                    try:
                        # Create session in user's namespace
                        session = create_intake_session_for_user(source, username, self.workspace, template_path=self.template_path)
                        self._json(200, session_summary(session, username))
                    finally:
                        # Always clean up temporary upload directory
                        if upload_dir and upload_dir.exists():
                            shutil.rmtree(upload_dir, ignore_errors=True)
                except Exception as exc:
                    # Clean up on error
                    if upload_dir and upload_dir.exists():
                        shutil.rmtree(upload_dir, ignore_errors=True)
                    raise exc
                return

            payload = (artpkg_sealed_handoff.parse_strict_json(body)
                       if parsed.path.startswith("/api/session/ux-") else json.loads(body.decode("utf-8") or "{}"))
            session_dir = payload.get("session_dir", "")
            
            # Enforce ownership on all session operations
            try:
                resolved = resolve_session_dir_with_owner(session_dir, username, self.workspace)
                if parsed.path.startswith("/api/session/ux-"):
                    artpkg_ux_preparation.runtime()
                    from ux_harness.paths import safe_path
                    safe_path(session_dir)
                session_lock = _session_lock(resolved)
                # Acquire BEFORE loading the full document, and retain through
                # persistence and summary generation for every dispatch branch.
                session_lock.acquire()
                session = load_workspace_session_with_owner(str(resolved), username, self.workspace)
            except ValueError:
                self._send_forbidden()
                return

            if parsed.path.startswith("/api/session/ux-"):
                artpkg_ux_preparation.runtime()
                from ux_harness.paths import safe_path
                safe_path(session_dir)
                coordinator = artpkg_ux_preparation.Preparation(session, username)
                operation = parsed.path.removeprefix("/api/session/ux-")
                fields = {
                    "upload": {"session_dir", "filename", "markdown"},
                    "resolve": {"session_dir", "upload_id", "decisions"},
                    "review": {"session_dir", "upload_id", "basis_sha256", "attestation", "exclusions", "type_mappings"},
                    "run": {"session_dir", "upload_id"},
                }
                if operation not in fields or set(payload) != fields[operation]:
                    raise ValueError("unknown UX operation or fields; paths/executables are server-owned")
                if operation == "upload":
                    if not isinstance(payload["markdown"], str):
                        raise ValueError("Markdown upload must be UTF-8 text")
                    result = coordinator.upload(payload["markdown"].encode("utf-8"), payload["filename"])
                elif operation == "resolve":
                    result = coordinator.resolve(payload["upload_id"], payload["decisions"])
                elif operation == "review":
                    result = coordinator.review(payload["upload_id"], payload["basis_sha256"], payload["attestation"],
                                                payload["exclusions"], payload["type_mappings"])
                else:
                    result = coordinator.run(payload["upload_id"])
                self._json(200, result)
                return
            
            if parsed.path == "/api/session/confirm":
                artpkg_intake.confirm_answer(session, payload["question_id"], username)
                self._json(200, session_summary(session, username))
                return

            if parsed.path in {"/api/session/final-review", "/api/session/coding-prepare"}:
                origin = self.headers.get("Origin")
                if (self.headers.get_content_type() != "application/json"
                        or (origin is not None and origin != "http://" + self.headers.get("Host", ""))):
                    self._send_forbidden()
                    return
                if parsed.path.endswith("coding-prepare"):
                    self._json(200, artpkg_coding_handoff.prepare(
                        session, username, payload.get("sealed_id", ""), payload.get("confirmation", "")))
                else:
                    artpkg_coding_handoff.approve_review(
                        session, username, payload.get("basis_sha256", ""), payload.get("confirmation", ""))
                    self._json(200, artpkg_coding_handoff.review_preview(session, username))
                return
            
            if parsed.path == "/api/session/answer":
                artpkg_intake.provide_answer(
                    session,
                    payload["question_id"],
                    payload.get("value"),
                    username,
                    payload.get("state", "PROVIDED"),
                )
                self._json(200, session_summary(session, username))
                return
            
            if parsed.path == "/api/session/reject":
                artpkg_intake.reject_seeded_answer(session, payload["question_id"], payload.get("reason", "Rejected in UI"), username)
                self._json(200, session_summary(session, username))
                return
            
            if parsed.path == "/api/session/record/confirm":
                artpkg_intake.confirm_record(session, payload["record_id"], username)
                self._json(200, session_summary(session, username))
                return

            if parsed.path == "/api/session/record/advance-status":
                artpkg_intake.advance_record_status(session, payload["record_id"], payload["target_status"], username)
                self._json(200, session_summary(session, username))
                return

            if parsed.path == "/api/session/record-section/confirm":
                artpkg_intake.confirm_record_section(session, payload["section"], username)
                self._json(200, session_summary(session, username))
                return

            if parsed.path == "/api/session/intent-summary":
                artpkg_intake.review_intent_summary(session, payload["action"], username)
                self._json(200, session_summary(session, username))
                return
            
            if parsed.path == "/api/session/record/reject":
                artpkg_intake.reject_seeded_record(session, payload["record_id"], payload.get("reason", "Rejected in UI"), username)
                self._json(200, session_summary(session, username))
                return

            if parsed.path in {"/api/session/dsh-send", "/api/session/dsh-transcript"}:
                origin = self.headers.get("Origin")
                if (self.headers.get_content_type() != "application/json"
                        or (origin is not None and origin != "http://" + self.headers.get("Host", ""))):
                    self._send_forbidden()
                    return
                if parsed.path.endswith("dsh-transcript"):
                    self._json(200, artpkg_dsh_bridge.transcript(session, username))
                else:
                    artpkg_dsh_bridge.send(session, username, payload.get("confirmation", ""))
                    self._json(200, session_summary(session, username))
                return

            if parsed.path == "/api/session/seal":
                if "review_basis_sha256" in payload:
                    if (not artpkg_coding_handoff.review_is_current(session)
                            or payload["review_basis_sha256"] != artpkg_coding_handoff.review_digest(session)):
                        raise ValueError("Final review changed; reload and review before sealing")
                preflight = pipeline_admission_status(
                    artpkg_sealed_handoff.review_package(
                        session, username, payload.get("target_binding"),
                    )
                )
                if not preflight["eligible"]:
                    raise artpkg_pipeline_admission.AdmissionError(
                        "ADMISSION_UNAVAILABLE",
                        "; ".join(preflight["unmet_conditions"]),
                    )
                result, _ = artpkg_sealed_handoff.seal_session(
                    session,
                    username,
                    payload.get("confirmation", ""),
                    payload.get("reviewed") is True,
                    payload.get("target_binding"),
                )
                admission = artpkg_pipeline_admission.admit_sealed_package(
                    result.sealed_dir,
                    package_id=result.package_id,
                    package_version=result.package_version,
                    submission_id=result.submission_id,
                    package_sha256=result.sealed_dir.name,
                )
                summary = session_summary(session, username)
                summary["sealed_package"] = {
                    "content_set_sha256": result.content_set_sha256,
                    "package_id": result.package_id,
                    "package_sha256": result.package_sha256,
                    "package_version": result.package_version,
                    "sealed_id": result.sealed_dir.name,
                    "submission_id": result.submission_id,
                }
                summary["pipeline_admission"] = {
                    "available": True,
                    "eligible": True,
                    "unmet_conditions": [],
                    "result": admission,
                }
                self._json(200, summary)
                return
            
            if parsed.path == "/api/session/project":
                summary = session_summary(session, username)
                summary["projection"] = build_projection_summary(session)
                self._json(200, summary)
                return
            
            self._json(404, {"error": "not found"})
        
        except Exception as exc:
            self._json(400, {"error": str(exc)})
        finally:
            if session_lock is not None:
                session_lock.release()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local ArtPkg intake UI with authentication.")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--template", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args(argv)

    # Validate that credentials are configured
    credentials = artpkg_intake_auth.get_configured_credentials()
    if not credentials:
        print("ERROR: No credentials configured. Set ARTPKG_INTAKE_CREDENTIALS or ARTPKG_INTAKE_CREDENTIALS_FILE.")
        return 1

    IntakeHandler.workspace = Path(args.workspace).expanduser().resolve()
    IntakeHandler.template_path = Path(args.template).expanduser().resolve() if args.template else None
    server = ThreadingHTTPServer((args.host, args.port), IntakeHandler)
    url = f"http://{args.host}:{args.port}/"
    configured_users = ", ".join(sorted(credentials.keys()))
    print(f"ArtPkg intake UI running at {url}")
    print(f"Configured users: {configured_users}")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
