"""Synthetic-only UX upload/auth/custody/orchestration regressions.

No real approvals, live credentials, Pipeline-A, SDLC or DSH calls. Only temporary
sources/custody are used. The one real end-to-end test runs the pinned local renderer.
"""
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

UXROOT = Path("/home/rootux/UXPkg")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(UXROOT / "src"))
sys.path.insert(0, str(UXROOT / "tests"))
import artpkg_intake_server as server
import artpkg_ux_preparation as adapter
from preparation_fixtures import (fill_template, markdown, review_evidence,
                                  seal_synthetic, synthetic_session)
from ux_harness.errors import Blocked
from ux_harness.paths import inventory
from ux_harness.preparation_handoff import verify_receipt


class UXPreparationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = Path(temp.name)
        self.session, self.reqs = synthetic_session(self.workspace)
        self.raw, self.tables = markdown(self.session, self.reqs)
        self.coordinator = adapter.Preparation(self.session, "alice")

    def request(self, operation, payload=None, method="POST", user="alice", headers=None, directory=None):
        class Handler(server.IntakeHandler):
            def _get_authenticated_user(self):
                return user  # auth unit boundary only; HTTP credentials tested below
            def _json(self, status, body):
                self.response = status, body
            def _send_forbidden(self):
                self._json(403, {"error": "forbidden"})
            def _send_auth_required(self):
                self._json(401, {"error": "unauthorized"})
            def _send_payload_too_large(self):
                self._json(413, {"error": "too large"})
        handler = Handler.__new__(Handler)
        handler.workspace = self.workspace
        directory = self.session["session_dir"] if directory is None else directory
        body = json.dumps({"session_dir": directory, **(payload or {})}).encode()
        handler.headers = Message()
        for key, value in {"Content-Length": str(len(body)), "Content-Type": "application/json",
                           "X-ArtPkg-UX": "1", "Host": "localhost:8765", "Origin": "http://localhost:8765", **(headers or {})}.items():
            handler.headers[key] = value
        handler.rfile = io.BytesIO(body)
        if method == "GET":
            handler.path = "/api/session/ux?" + urlencode({"dir": directory, "op": operation, **(payload or {})})
            handler.do_GET()
        else:
            handler.path = "/api/session/ux-" + operation
            handler.do_POST()
        return handler.response

    def uploaded(self):
        return self.coordinator.upload(self.raw, "synthetic-calculator.md")["upload_id"]

    def reviewed(self):
        seal_synthetic(self.session)
        upload_id = self.uploaded()
        preview = self.coordinator.preview(upload_id)
        self.coordinator.review(upload_id, preview["basis_sha256"], adapter.ATTESTATION, review_evidence(preview), {})
        return upload_id

    def test_real_handler_upload_review_emit_render_receipt(self):
        status, upload = self.request("upload", {"filename": "new-calculator.md", "markdown": self.raw.decode()})
        self.assertEqual(200, status, upload)
        self.assertEqual("NONE", upload["authority"])
        sealed = seal_synthetic(self.session)
        before = inventory(sealed.sealed_dir)
        status, preview = self.request("preview", {"upload_id": upload["upload_id"]}, method="GET")
        self.assertEqual(200, status, preview)
        status, result = self.request("review", {"upload_id": upload["upload_id"], "basis_sha256": preview["basis_sha256"],
            "attestation": adapter.ATTESTATION, "exclusions": review_evidence(preview), "type_mappings": {}})
        self.assertEqual(200, status, result)
        status, receipt = self.request("run", {"upload_id": upload["upload_id"]})
        self.assertEqual(200, status, receipt)
        self.assertEqual("READY_FOR_HUMAN_UX_REVIEW", receipt["status"])
        self.assertEqual("NONE", receipt["implementation_authority"])
        self.assertEqual(before, inventory(sealed.sealed_dir))
        status, verified = self.request("verify", {"upload_id": upload["upload_id"]}, method="GET")
        self.assertEqual((200, receipt), (status, verified))
        contract = json.loads((Path(receipt["output_path"]) / "02-ux-contract.json").read_text())
        self.assertEqual(19, len(contract["screens"][0]["components"]))
        self.assertFalse((Path(receipt["output_path"]) / "05-authorization.json").exists())
        # Separate reusable consumer verification, original local private stores.
        self.assertEqual(receipt, verify_receipt(Path(receipt["output_path"]).parent / "receipt.json",
            self.coordinator.custody, self.coordinator.ux_custody,
            lambda: adapter.verified_source(self.session, "alice")[0], "alice", self.session["session_dir"]))

    def test_get_exports_and_template_prompt_are_owner_bound(self):
        for operation in ("export", "template", "prompt"):
            status, body = self.request(operation, method="GET")
            self.assertEqual(200, status, body)
            self.assertEqual(403, self.request(operation, method="GET", user="bob")[0])
            if operation == "prompt":
                self.assertIn("implemented preparation parser", body["content"])
                self.assertIn("source_snapshot_sha256", body["content"])
                self.assertIn("behavior IDs only", body["content"])
        exported = self.request("export", method="GET")[1]
        self.assertEqual(len(adapter.source_items(self.session["document"])), len(exported["items"]))
        self.assertEqual(adapter.snapshot(self.session["document"]), exported["source_snapshot_sha256"])

    def test_resolution_questionnaire_versions_source_and_invalidates_draft(self):
        upload_id = self.uploaded()
        before = adapter.snapshot(self.session["document"])
        questionnaire = self.coordinator.resolution_questionnaire(upload_id)
        self.assertEqual(6, len(questionnaire["questions"]))
        self.assertEqual("NONE", questionnaire["authority"])
        decisions = {question["id"]: {"choice": next(iter(question["choices"])), "other": ""}
                     for question in questionnaire["questions"]}
        result = self.coordinator.resolve(upload_id, decisions)
        self.assertTrue(result["status"]["complete"])
        self.assertTrue(result["proposal_stale"])
        self.assertEqual("NONE", result["implementation_authority"])
        self.assertNotEqual(before, result["source_snapshot_sha256"])
        self.assertIn("from=ux-resolution", result["return_url"])
        for identifier in adapter.RESOLUTION_BY_ID:
            answer = self.session["document"]["answers"][identifier]
            self.assertEqual("PROVIDED", answer["state"])
            self.assertEqual("HUMAN_DECLARATION", answer["source_type"])
            self.assertEqual("HUMAN_CONFIRMED", answer["review_disposition"])
        with self.assertRaisesRegex(ValueError, "stale requirements"):
            self.coordinator.preview(upload_id)

    def test_resolution_rejects_partial_invalid_and_preserves_undecided(self):
        upload_id = self.uploaded()
        questions = self.coordinator.resolution_questionnaire(upload_id)["questions"]
        decisions = {question["id"]: {"choice": "UNDECIDED", "other": ""} for question in questions}
        for invalid in ({}, {**decisions, "UXR-001": {"choice": "INVENTED", "other": ""}},
                        {**decisions, "UXR-001": {"choice": "OTHER", "other": ""}}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.coordinator.resolve(upload_id, invalid)
        result = self.coordinator.resolve(upload_id, decisions)
        self.assertFalse(result["status"]["complete"])
        self.assertEqual(set(adapter.RESOLUTION_BY_ID), set(result["status"]["undecided"]))
        self.assertTrue(all(self.session["document"]["answers"][identifier]["state"] == "UNKNOWN"
                            for identifier in adapter.RESOLUTION_BY_ID))

    def test_resolution_handler_is_owner_bound_and_closed(self):
        upload_id = self.uploaded()
        status, questionnaire = self.request("resolution", {"upload_id": upload_id}, method="GET")
        self.assertEqual(200, status, questionnaire)
        decisions = {question["id"]: {"choice": "UNDECIDED", "other": ""}
                     for question in questionnaire["questions"]}
        self.assertEqual(403, self.request("resolve", {"upload_id": upload_id, "decisions": decisions}, user="bob")[0])
        self.assertEqual(400, self.request("resolve", {"upload_id": upload_id, "decisions": decisions, "authority": "APPROVED"})[0])
        status, result = self.request("resolve", {"upload_id": upload_id, "decisions": decisions})
        self.assertEqual(200, status, result)
        self.assertEqual("NONE", result["implementation_authority"])

    def test_auth_csrf_wrong_owner_and_client_paths_rejected(self):
        payload = {"filename": "new.md", "markdown": self.raw.decode()}
        self.assertEqual(401, self.request("upload", payload, user=None)[0])
        self.assertEqual(403, self.request("upload", payload, user="bob")[0])
        for headers in ({"X-ArtPkg-UX": ""}, {"Origin": "https://evil.example"},
                        {"Content-Type": "text/plain"}, {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(403, self.request("upload", payload, headers=headers)[0])
        self.assertEqual(400, self.request("upload", {**payload, "executable": "/bin/sh"})[0])
        self.assertEqual(400, self.request("run", {"upload_id": "a" * 32, "output": "/tmp/untrusted"})[0])
        self.assertFalse(self.coordinator.store.exists())

    def test_basic_auth_with_only_synthetic_credentials(self):
        import base64
        handler = server.IntakeHandler.__new__(server.IntakeHandler)
        handler.headers = Message()
        handler.headers["Authorization"] = "Basic " + base64.b64encode(b"synthetic:fixture-only").decode()
        with patch.dict(os.environ, {"ARTPKG_INTAKE_CREDENTIALS": "synthetic:fixture-only"}, clear=True):
            self.assertEqual("synthetic", handler._get_authenticated_user())
            handler.headers.replace_header("Authorization", "Basic invalid")
            self.assertIsNone(handler._get_authenticated_user())

    def test_upload_bounds_utf8_filename_links_and_nonmutation(self):
        before = inventory(Path(self.session["session_dir"]))
        for name in ("../escape.md", "/tmp/x.md", "a\\b.md", "a..b.md", "template_ux_ui_package.md", "x.html"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.coordinator.upload(self.raw, name)
        for raw in (b"\xff", b"x" * (512 * 1024 + 1)):
            with self.assertRaises(Blocked):
                self.coordinator.upload(raw, "new.md")
        self.assertEqual(before, inventory(Path(self.session["session_dir"])))
        outside = self.workspace / "outside"
        outside.mkdir()
        self.coordinator.store.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(Blocked):
            self.coordinator.upload(self.raw, "new.md")
        self.assertEqual([], list(outside.iterdir()))

    def test_review_never_accepts_claimed_hash_or_missing_human_attestation(self):
        seal_synthetic(self.session)
        upload_id = self.uploaded()
        preview = self.coordinator.preview(upload_id)
        for digest, attestation in (("0" * 64, adapter.ATTESTATION), (preview["basis_sha256"], "approved by upload")):
            with self.assertRaises(ValueError):
                self.coordinator.review(upload_id, digest, attestation, review_evidence(preview), {})
        with self.assertRaises((OSError, ValueError, Blocked)):
            self.coordinator.run(upload_id)
        self.assertFalse((self.coordinator._path(upload_id) / "output").exists())

    def test_stale_answers_and_records_invalidate_review(self):
        upload_id = self.reviewed()
        for mutate in (lambda d: d["answers"]["PKG-001"].update(value="Changed project"),
                       lambda d: d["records"]["functional_requirements"][0]["fields"].update(requirement="Changed behavior")):
            old = copy.deepcopy(self.session["document"])
            mutate(self.session["document"])
            with self.assertRaisesRegex(ValueError, "stale"):
                self.coordinator.run(upload_id)
            self.session["document"] = old
        self.assertFalse((self.coordinator._path(upload_id) / "output").exists())

    def test_upload_review_tamper_and_wrong_user(self):
        upload_id = self.reviewed()
        path = self.coordinator._path(upload_id)
        for name in ("proposal.md", "normalized.json", "review.json"):
            original = (path / name).read_bytes()
            if name.endswith(".json"):
                obj = json.loads(original)
                if name == "review.json":
                    obj["user"] = "mallory"
                else:
                    obj["blockers"] = ["tampered"]
                (path / name).write_text(json.dumps(obj))
            else:
                (path / name).write_bytes(original + b"\nchanged bytes\n")
            with self.assertRaises((ValueError, Blocked)):
                self.coordinator.run(upload_id)
            (path / name).write_bytes(original)
        with self.assertRaisesRegex(ValueError, "owner"):
            adapter.Preparation(self.session, "bob").preview(upload_id)

    def test_source_tamper_blocks_before_subprocess(self):
        upload_id = self.reviewed()
        source = adapter.verified_source(self.session, "alice")[0]
        file = Path(source["path"]) / "artifacts_package.md"
        file.chmod(0o600)
        file.write_bytes(file.read_bytes() + b"\ntampered synthetic file\n")
        with patch.object(adapter.subprocess, "run") as run:
            with self.assertRaises((ValueError, Blocked)):
                self.coordinator.run(upload_id)
            run.assert_not_called()

    def test_subprocess_mock_exit_timeout_and_stdout_never_authority(self):
        # Unit test only: unlike the real integration test, these do not render.
        for result in (subprocess.CompletedProcess([], 17, b"", b""),
                       subprocess.TimeoutExpired("ux-harness", 90),
                       subprocess.CompletedProcess([], 0, b'{"status":"READY_FOR_IMPLEMENTATION"}', b"")):
            with self.subTest(result=type(result).__name__):
                upload_id = self.reviewed()
                kwargs = {"side_effect": result} if isinstance(result, Exception) else {"return_value": result}
                with patch.object(adapter.subprocess, "run", **kwargs) as run:
                    with self.assertRaises((ValueError, Blocked, OSError, subprocess.TimeoutExpired)):
                        self.coordinator.run(upload_id)
                    self.assertTrue(run.called)
                    self.assertIs(run.call_args.kwargs["shell"], False)
                    self.assertEqual(90, run.call_args.kwargs["timeout"])
                    self.assertEqual(str(UXROOT / ".venv/bin/python"), run.call_args.args[0][0])
                self.assertFalse((self.coordinator._path(upload_id) / "receipt.json").exists())

    def test_no_ui_receipt_tamper_and_read_only_verification(self):
        temp = self.workspace / "no-ui"
        session, reqs = synthetic_session(temp, "no-ui")
        coordinator = adapter.Preparation(session, "alice")
        seal_synthetic(session)
        upload_id = coordinator.upload(markdown(session, reqs, "no-ui")[0], "batch.md")["upload_id"]
        preview = coordinator.preview(upload_id)
        coordinator.review(upload_id, preview["basis_sha256"], adapter.ATTESTATION, review_evidence(preview), {})
        receipt = coordinator.run(upload_id)
        before = inventory(Path(session["session_dir"]))
        self.assertEqual(receipt, coordinator.verify(upload_id))
        self.assertEqual(before, inventory(Path(session["session_dir"])))
        for name in ("receipt.json", "input/requirements.json", "output/status.json"):
            path = coordinator._path(upload_id) / name
            original = path.read_bytes()
            data = json.loads(original)
            if name == "receipt.json":
                data["uxpkg_package_sha256"] = "0" * 64
            elif name.startswith("input"):
                data["requirements"][0]["text"] = "Tampered source"
            else:
                data["status"] = "READY_FOR_IMPLEMENTATION"
            path.write_text(json.dumps(data))
            with self.assertRaises((ValueError, Blocked)):
                coordinator.verify(upload_id)
            path.write_bytes(original)
        with self.assertRaises((ValueError, Blocked)):
            coordinator.run(upload_id)  # Fresh output required; no retries into old trees.


if __name__ == "__main__":
    unittest.main()