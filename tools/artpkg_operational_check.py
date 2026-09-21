#!/usr/bin/env python3
"""Verify that the local ArtPkg services and intake workflow are operational."""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

EXPECTED_STATUS = {"status": "ok", "service": "artpkg", "mode": "read-only-status"}


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


class OperationalCheck:
    def __init__(self) -> None:
        self.results: list[CheckResult] = []

    def pass_(self, name: str, detail: str) -> None:
        self.results.append(CheckResult(name, "PASS", detail))

    def fail(self, name: str, detail: str) -> None:
        self.results.append(CheckResult(name, "FAIL", detail))

    def warn(self, name: str, detail: str) -> None:
        self.results.append(CheckResult(name, "WARN", detail))

    @property
    def ok(self) -> bool:
        return not any(result.status == "FAIL" for result in self.results)


def _authorization(username: str, password: str) -> str:
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _request(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> tuple[int, dict[str, str], bytes]:
    request = Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read()
    except HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read()


def _json_body(body: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{context} did not return valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{context} returned {type(value).__name__}; expected an object")
    return value


def _multipart_file(path: Path) -> tuple[str, bytes]:
    boundary = f"----artpkg-operational-{uuid.uuid4().hex}"
    content = path.read_bytes()
    body = b"".join([
        f"--{boundary}\r\n".encode("ascii"),
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode("utf-8"),
        b"Content-Type: text/markdown\r\n\r\n",
        content,
        b"\r\n",
        f"--{boundary}--\r\n".encode("ascii"),
    ])
    return boundary, body


def _load_password(credentials_file: Path, username: str) -> str:
    password = os.environ.get("ARTPKG_OPERATIONAL_PASSWORD")
    if password:
        return password
    try:
        credentials = json.loads(credentials_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(
            f"credentials file not found: {credentials_file}; set ARTPKG_OPERATIONAL_PASSWORD or --credentials-file"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"credentials file is not valid JSON: {credentials_file}") from exc
    if not isinstance(credentials, dict) or not isinstance(credentials.get(username), str):
        raise ValueError(f"credentials file has no password for user {username!r}")
    return credentials[username]


def _check_http_services(
    report: OperationalCheck,
    status_url: str,
    viewer_url: str,
    intake_url: str,
    authorization: str,
    timeout: float,
) -> bool:
    try:
        status, _, body = _request(status_url, timeout=timeout)
        payload = _json_body(body, "ArtPkg status service")
        if status == 200 and payload == EXPECTED_STATUS:
            report.pass_("artpkg-status", f"{status_url} returned the expected read-only status payload")
        else:
            report.fail("artpkg-status", f"HTTP {status}; unexpected payload {payload!r}")
    except (OSError, URLError, ValueError) as exc:
        report.fail("artpkg-status", str(exc))

    try:
        status, _, body = _request(viewer_url, timeout=timeout)
        if status == 200 and body:
            report.pass_("archify-viewer", f"{viewer_url} returned HTTP 200 ({len(body)} bytes)")
        else:
            report.fail("archify-viewer", f"HTTP {status}; response size {len(body)} bytes")
    except (OSError, URLError) as exc:
        report.fail("archify-viewer", str(exc))

    try:
        status, headers, _ = _request(intake_url, timeout=timeout)
        challenge = headers.get("WWW-Authenticate", "")
        if status == 401 and challenge.lower().startswith("basic "):
            report.pass_("intake-auth-challenge", "unauthenticated request returned HTTP 401 with Basic challenge")
        else:
            report.fail("intake-auth-challenge", f"expected HTTP 401 Basic challenge; received HTTP {status}")

        status, _, body = _request(intake_url, headers={"Authorization": authorization}, timeout=timeout)
        if status == 200 and b"ArtPkg" in body:
            report.pass_("intake-authenticated", f"authenticated intake UI returned HTTP 200 ({len(body)} bytes)")
            return True
        report.fail("intake-authenticated", f"HTTP {status}; intake UI marker not found")
    except (OSError, URLError) as exc:
        report.fail("intake-authenticated", str(exc))
    return False


def _check_workflow(
    report: OperationalCheck,
    intake_url: str,
    authorization: str,
    fixture: Path,
    timeout: float,
) -> None:
    boundary, body = _multipart_file(fixture)
    headers = {
        "Authorization": authorization,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    status, _, response_body = _request(
        f"{intake_url}/api/intake",
        method="POST",
        data=body,
        headers=headers,
        timeout=timeout,
    )
    payload = _json_body(response_body, "intake smoke upload")
    session_dir = payload.get("session_dir")
    if status != 200 or not isinstance(session_dir, str):
        report.fail("intake-workflow", f"HTTP {status}: {payload.get('error') or 'session_dir missing'}")
        return
    report.pass_("intake-workflow", f"fixture created probe session {payload.get('session_id', session_dir)}")

    project_body = json.dumps({"session_dir": session_dir}).encode("utf-8")
    status, _, response_body = _request(
        f"{intake_url}/api/session/project",
        method="POST",
        data=project_body,
        headers={"Authorization": authorization, "Content-Type": "application/json"},
        timeout=timeout,
    )
    payload = _json_body(response_body, "projection generation")
    projection = payload.get("projection")
    if status != 200 or not isinstance(projection, dict):
        report.fail("projection-generation", f"HTTP {status}: {payload.get('error') or 'projection missing'}")
        return
    if projection.get("ready") is not True:
        report.fail("projection-generation", str(projection.get("error") or "projection did not become ready"))
        return

    archify = projection.get("archify", {})
    validate_ok = isinstance(archify.get("validate"), dict) and archify["validate"].get("ok") is True
    deliver_ok = isinstance(archify.get("deliver"), dict) and archify["deliver"].get("ok") is True
    if not validate_ok or not deliver_ok:
        report.fail("projection-generation", f"Archify validate={validate_ok}, deliver={deliver_ok}")
        return
    report.pass_("projection-generation", "Archify validate and deliver succeeded")

    visual = archify.get("visual_check", {})
    if isinstance(visual, dict) and visual.get("ok") is True:
        report.pass_("projection-visual-check", "Archify browser visual check succeeded")
    else:
        error = visual.get("receipt", {}).get("error") if isinstance(visual, dict) else None
        report.warn("projection-visual-check", str(error or "optional Archify visual check did not run"))

    html_url = f"{intake_url}/api/session/projection-html?dir={quote(session_dir, safe='')}"
    status, headers, html = _request(html_url, headers={"Authorization": authorization}, timeout=timeout)
    content_type = headers.get("Content-Type", "")
    if status == 200 and len(html) > 1000 and "text/html" in content_type:
        report.pass_("projection-html", f"generated HTML is fetchable ({len(html)} bytes)")
    else:
        report.fail(
            "projection-html",
            f"HTTP {status}; content type {content_type!r}; response size {len(html)} bytes",
        )


def _print_report(report: OperationalCheck, json_output: bool) -> None:
    if json_output:
        print(json.dumps({"ok": report.ok, "checks": [asdict(result) for result in report.results]}, indent=2))
        return
    for result in report.results:
        print(f"[{result.status}] {result.name}: {result.detail}")
    passed = sum(result.status == "PASS" for result in report.results)
    warned = sum(result.status == "WARN" for result in report.results)
    failed = sum(result.status == "FAIL" for result in report.results)
    print(f"\nArtPkg operational check: {'PASS' if report.ok else 'FAIL'} ({passed} passed, {warned} warnings, {failed} failed)")


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-url", default="http://127.0.0.1:8555/healthz")
    parser.add_argument("--viewer-url", default="http://127.0.0.1:8666/")
    parser.add_argument("--intake-url", default="http://127.0.0.1:8765")
    parser.add_argument("--username", default="tester1")
    parser.add_argument("--credentials-file", type=Path, default=root / "artpkg-credentials.json")
    parser.add_argument("--fixture", type=Path, default=root / "tests" / "fixtures" / "basic-windows-calculator_preartifacts.md")
    parser.add_argument("--shallow", action="store_true", help="Check HTTP services and authentication without creating a probe session")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    report = OperationalCheck()
    try:
        password = _load_password(args.credentials_file.expanduser().resolve(), args.username)
    except ValueError as exc:
        report.fail("credentials", str(exc))
        _print_report(report, args.json)
        return 1

    authorization = _authorization(args.username, password)
    intake_url = args.intake_url.rstrip("/")
    intake_ready = _check_http_services(
        report,
        args.status_url,
        args.viewer_url,
        intake_url,
        authorization,
        args.timeout,
    )
    if not args.shallow and intake_ready:
        try:
            fixture = args.fixture.expanduser().resolve()
            if not fixture.is_file():
                raise ValueError(f"smoke fixture not found: {fixture}")
            _check_workflow(report, intake_url, authorization, fixture, args.timeout)
        except (OSError, URLError, ValueError) as exc:
            report.fail("workflow-smoke", str(exc))

    _print_report(report, args.json)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
