import json
import io
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlencode

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_intake_server as server


class IntakeConcurrencyTests(unittest.TestCase):
    """Exercise real handler dispatch and temporary session persistence, not sockets/auth."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        self.session = server.create_intake_session_for_user(source, "alice", self.workspace)
        self.session_dir = self.session["session_dir"]
        # Keep the real summary logic, but omit external sealing/DSH integrations.
        summary = server.session_summary
        self.summary = self.enterContext(patch.object(
            server, "session_summary", side_effect=lambda session, reviewer: summary(session),
        ))

    def request(self, method="POST", route="/api/session/answer", session_dir=None, user="alice", **payload):
        class Handler(server.IntakeHandler):
            def _get_authenticated_user(self):
                return user

            def _json(self, status, body):
                self.response = status, json.loads(json.dumps(body))

            def _send_forbidden(self):
                self._json(403, {"error": "forbidden"})

            def _send_auth_required(self):
                self._json(401, {"error": "unauthorized"})

        handler = Handler.__new__(Handler)
        handler.workspace = self.workspace
        directory = self.session_dir if session_dir is None else str(session_dir)
        body = json.dumps({"session_dir": directory, **payload}).encode()
        handler.headers = Message()
        handler.headers["Content-Length"] = str(len(body))
        handler.headers["Content-Type"] = "application/json"
        handler.rfile = io.BytesIO(body)
        handler.path = route + ("?" + urlencode({"dir": directory}) if method == "GET" else "")
        if method == "GET":
            handler.do_GET()
        else:
            handler.do_POST()
        return handler.response

    def wait(self, event):
        self.assertTrue(event.wait(5), "concurrent request did not reach the expected boundary")

    def observe_lock_attempt(self, boundary):
        """Wake the writer at contention; before the fix the reader's load wakes it.

        This observation hook never supplies synchronization to the handler: it
        delegates to the production lock, and is unused by the unfixed handler.
        """
        get_lock = getattr(server, "_session_lock", None)

        class ObservedLock:
            def __init__(self, lock):
                self.lock = lock

            def acquire(self):
                boundary.set()
                return self.lock.acquire()

            def release(self):
                self.lock.release()

            def __enter__(self):
                self.acquire()
                return self

            def __exit__(self, *args):
                self.release()

        return patch.object(
            server, "_session_lock", create=True,
            side_effect=lambda path: ObservedLock(get_lock(path)),
        )

    def test_concurrent_answers_preserve_both_acknowledged_edits(self):
        first_loaded = threading.Event()
        second_boundary = threading.Event()
        first_saved = threading.Event()
        load = server.artpkg_intake.load_intake_session
        provide = server.artpkg_intake.provide_answer

        def observed_load(path):
            session = load(path)
            if first_loaded.is_set():
                # Pre-fix: both documents are now loaded, with the first unsaved.
                second_boundary.set()
            return session

        def ordered_provide(session, question_id, *args):
            if question_id == "PKG-003":
                first_loaded.set()
                try:
                    self.wait(second_boundary)
                    return provide(session, question_id, *args)
                finally:
                    first_saved.set()
            self.wait(first_saved)
            return provide(session, question_id, *args)

        with patch.object(server.artpkg_intake, "load_intake_session", side_effect=observed_load), \
                patch.object(server.artpkg_intake, "provide_answer", side_effect=ordered_provide), \
                ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.request, question_id="PKG-003", value="Concurrent owner")
            self.wait(first_loaded)
            with self.observe_lock_attempt(second_boundary):
                # An alternate spelling must select the same canonical lock.
                alias = self.session_dir + "/../" + Path(self.session_dir).name + "/."
                second = pool.submit(self.request, session_dir=alias,
                                     question_id="PKG-004", value="Concurrent reviewer")
                first_response = first.result(timeout=10)
                second_response = second.result(timeout=10)

        self.assertEqual(200, first_response[0], first_response)
        self.assertEqual(200, second_response[0], second_response)
        reloaded = server.load_workspace_session_with_owner(self.session_dir, "alice", self.workspace)
        for question_id, value in (("PKG-003", "Concurrent owner"), ("PKG-004", "Concurrent reviewer")):
            answer = reloaded["document"]["answers"][question_id]
            self.assertEqual(value, answer["value"], "an acknowledged concurrent edit was lost")
            self.assertEqual("PROVIDED", answer["state"])
            self.assertEqual("HUMAN_DECLARATION", answer["source_type"])
            self.assertEqual("HUMAN_CONFIRMED", answer["review_disposition"])
            self.assertEqual("alice", answer["reviewer"])
        status, summary = self.request(method="GET", route="/api/session")
        self.assertEqual(200, status)
        self.assertEqual(reloaded["human_work_counts"], summary["human_work_counts"])
        self.assertEqual(reloaded["review_queues"], summary["review_queues"])

    def test_get_waits_for_post_persistence_and_summary(self):
        for phase in ("persistence", "summary"):
            with self.subTest(phase=phase):
                writer_paused = threading.Event()
                reader_boundary = threading.Event()
                summary_complete = threading.Event()
                premature_loads = []
                load = server.artpkg_intake.load_intake_session
                save = server.artpkg_intake.save_intake_session
                summarize = self.summary.side_effect

                def pause_writer():
                    writer_paused.set()
                    self.wait(reader_boundary)

                def observed_save(session):
                    if phase == "persistence":
                        # answers.json has been saved, but session.json has not.
                        pause_writer()
                    return save(session)

                def observed_summary(session, reviewer):
                    if not summary_complete.is_set():
                        if phase == "summary":
                            pause_writer()
                        result = summarize(session, reviewer)
                        summary_complete.set()
                        return result
                    return summarize(session, reviewer)

                def observed_load(path):
                    if writer_paused.is_set() and not summary_complete.is_set():
                        premature_loads.append(str(path))
                        reader_boundary.set()
                    return load(path)

                with patch.object(server.artpkg_intake, "load_intake_session", side_effect=observed_load), \
                        patch.object(server.artpkg_intake, "save_intake_session", side_effect=observed_save), \
                        patch.object(server, "session_summary", side_effect=observed_summary), \
                        ThreadPoolExecutor(max_workers=2) as pool:
                    writer = pool.submit(self.request, question_id="PKG-003", value=phase)
                    self.wait(writer_paused)
                    with self.observe_lock_attempt(reader_boundary):
                        reader = pool.submit(self.request, method="GET", route="/api/session")
                        write_response = writer.result(timeout=10)
                        read_response = reader.result(timeout=10)

                self.assertEqual(200, write_response[0], write_response)
                self.assertEqual(200, read_response[0], read_response)
                self.assertEqual([], premature_loads, "GET loaded an unfinished POST transaction")
                self.assertEqual(write_response[1], read_response[1])

    def test_unrelated_session_can_save_while_dsh_send_is_waiting(self):
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        other = server.create_intake_session_for_user(source, "bob", self.workspace)
        dsh_started = threading.Event()
        release_dsh = threading.Event()

        def waiting_send(*args):
            dsh_started.set()
            self.wait(release_dsh)

        with patch.object(server.artpkg_dsh_bridge, "send", side_effect=waiting_send), \
                ThreadPoolExecutor(max_workers=2) as pool:
            dsh = pool.submit(self.request, route="/api/session/dsh-send")
            try:
                self.wait(dsh_started)
                answer = pool.submit(self.request, user="bob", session_dir=other["session_dir"],
                                     question_id="PKG-003", value="Independent owner")
                response = answer.result(timeout=3)
                self.assertEqual(200, response[0], response)
                self.assertFalse(dsh.done(), "DSH should still be waiting while the other session completes")
            finally:
                release_dsh.set()
            self.assertEqual(200, dsh.result(timeout=10)[0])
        reloaded = server.load_workspace_session_with_owner(other["session_dir"], "bob", self.workspace)
        self.assertEqual("Independent owner", reloaded["document"]["answers"]["PKG-003"]["value"])

    def test_lock_released_after_dispatch_errors_and_early_returns(self):
        resolved = server.resolve_session_dir_with_owner(self.session_dir, "alice", self.workspace)
        # Keep a strong reference so a leaked lock cannot vanish from the registry.
        lock = server._session_lock(resolved)
        cases = (
            ("/api/session/answer", {"question_id": "PKG-003", "value": ""}, 400),
            ("/api/session/confirm", {}, 400),
            ("/api/session/unknown", {}, 404),
        )

        def acquired_from_another_thread():
            acquired = lock.acquire(timeout=1)
            if acquired:
                lock.release()
            return acquired

        with ThreadPoolExecutor(max_workers=1) as pool:
            for route, payload, expected in cases:
                with self.subTest(route=route):
                    self.assertEqual(expected, self.request(route=route, **payload)[0])
                    self.assertTrue(pool.submit(acquired_from_another_thread).result(timeout=3))
            with patch.object(server.artpkg_intake, "load_intake_session", side_effect=ValueError("invalid session")):
                self.assertEqual(403, self.request(question_id="PKG-003", value="Owner")[0])
            self.assertTrue(pool.submit(acquired_from_another_thread).result(timeout=3))
            with patch.object(server, "session_summary", side_effect=RuntimeError("summary failure")):
                self.assertEqual(400, self.request(question_id="PKG-003", value="Saved owner")[0])
                self.assertEqual(400, self.request(method="GET", route="/api/session")[0])
            self.assertTrue(pool.submit(acquired_from_another_thread).result(timeout=3))
            response = pool.submit(self.request, question_id="PKG-004", value="Saved reviewer").result(timeout=3)
            self.assertEqual(200, response[0], response)

    def test_ownership_and_authentication_checked_before_lock_or_load(self):
        with patch.object(server, "_session_lock") as lock, \
                patch.object(server.artpkg_intake, "load_intake_session") as load:
            for method in ("GET", "POST"):
                route = "/api/session" if method == "GET" else "/api/session/answer"
                for user, directory, expected in (
                    (None, self.session_dir, 401),
                    ("bob", self.session_dir, 403),
                    ("alice", self.workspace, 403),
                    ("alice", self.session_dir + "/../../../bob/sessions/other", 403),
                ):
                    with self.subTest(method=method, user=user, directory=directory):
                        self.assertEqual(expected, self.request(method, route, directory, user)[0])
            lock.assert_not_called()
            load.assert_not_called()

    def test_lock_registry_reuses_canonical_paths_and_reclaims_idle_locks(self):
        import weakref

        resolved = server.resolve_session_dir_with_owner(self.session_dir, "alice", self.workspace)
        alias = server.resolve_session_dir_with_owner(self.session_dir + "/.", "alice", self.workspace)
        lock = server._session_lock(resolved)
        self.assertIs(lock, server._session_lock(alias))
        self.assertIsNot(lock, server._session_lock(resolved.parent / "other"))
        with lock:
            with server._session_lock(alias):
                pass  # Re-entrant access must not deadlock.
        reference = weakref.ref(lock)
        del lock
        self.assertIsNone(reference())


class IntakeServerTests(unittest.TestCase):
    def test_pipeline_admission_status_preserves_exact_sealing_and_configuration_blockers(self):
        sealing = {"completion_result": "BLOCKED", "seal_blockers": ["FIN-001 incomplete", "authority must be NONE"]}
        with patch("artpkg_intake_server.artpkg_pipeline_admission.configuration_status") as status:
            status.return_value = {"available": False, "unmet_conditions": ["PIPELINE_A_CUSTODY_ROOT missing"]}
            result = server.pipeline_admission_status(sealing)

        self.assertFalse(result["eligible"])
        self.assertEqual(
            ["FIN-001 incomplete", "authority must be NONE", "PIPELINE_A_CUSTODY_ROOT missing"],
            result["unmet_conditions"],
        )

    def test_pipeline_admission_status_enables_only_ready_configured_package(self):
        sealing = {"completion_result": "READY_TO_SEAL", "seal_blockers": []}
        with patch("artpkg_intake_server.artpkg_pipeline_admission.configuration_status") as status:
            status.return_value = {"available": True, "unmet_conditions": []}
            self.assertTrue(server.pipeline_admission_status(sealing)["eligible"])

    def test_pipeline_admission_status_never_enables_blocked_package_with_configuration(self):
        sealing = {"completion_result": "BLOCKED", "seal_blockers": ["final attestation incomplete"]}
        with patch("artpkg_intake_server.artpkg_pipeline_admission.configuration_status") as status:
            status.return_value = {"available": True, "unmet_conditions": []}
            result = server.pipeline_admission_status(sealing)

        self.assertFalse(result["eligible"])
        self.assertEqual(["final attestation incomplete"], result["unmet_conditions"])

    def test_parse_multipart_markdown_upload(self):
        boundary = "----artpkg"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="pre.md"\r\n'
            "Content-Type: text/markdown\r\n\r\n"
            "# Pre-Artifacts Package\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        upload = server.parse_multipart_upload(f"multipart/form-data; boundary={boundary}", body)
        self.assertEqual("pre.md", upload.filename)
        self.assertIn(b"Pre-Artifacts", upload.content)

    def test_session_summary_excludes_full_document_payload(self):
        session = {
            "session_id": "S",
            "session_dir": "D:/tmp/S",
            "source": {"sha256": "abc"},
            "validation": {"status": "DRAFT"},
            "review_queues": {"needs_answer": [{"id": "PKG-003"}]},
            "document": {"answers": {"PKG-001": {"value": "Example"}}},
        }
        summary = server.session_summary(session)
        self.assertNotIn("document", summary)
        self.assertEqual("S", summary["session_id"])
        self.assertEqual(1, summary["queue_counts"]["needs_answer"])

    def test_start_questionnaire_backend_accepts_calculator_pre_artifacts(self):
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            session = server.create_intake_session_for_user(source, "tester1", temp_dir)

        self.assertIn("/.artpkg/users/tester1/sessions/", session["session_dir"])
        self.assertEqual(3, len(session["document"]["records"]["functional_requirements"]))
        self.assertEqual("NONE", session["document"]["answers"]["AUT-001"]["value"])
        self.assertEqual("HUMAN_REVIEW_ONLY", session["validation"]["next_permitted_action"])

    def test_resolve_session_dir_accepts_workspace_intake_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            session_dir = workspace / ".artpkg" / "intake_sessions" / "session-1"
            session_dir.mkdir(parents=True)

            resolved = server.resolve_session_dir(str(session_dir), workspace)

            self.assertEqual(session_dir.resolve(), resolved)

    def test_resolve_session_dir_rejects_path_outside_workspace_intake_sessions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            outside_session = Path(temp_dir) / "outside" / "session-1"
            outside_session.mkdir(parents=True)

            with self.assertRaisesRegex(ValueError, "outside the configured intake sessions directory"):
                server.resolve_session_dir(str(outside_session), workspace)

    def test_load_workspace_session_normalizes_malicious_session_dir_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            session_dir = workspace / ".artpkg" / "intake_sessions" / "session-1"
            malicious_session_dir = Path(temp_dir) / "outside" / "session-1"
            session_dir.mkdir(parents=True)
            questionnaire = server.artpkg_intake.questionnaire
            answers = {
                "schema_version": questionnaire.SCHEMA_VERSION,
                "answers": {},
                "records": {section: [] for section in questionnaire.ID_PREFIXES},
            }
            (session_dir / "answers.json").write_text(json.dumps(answers), encoding="utf-8")
            (session_dir / "seed.json").write_text(json.dumps({"answers": {}}), encoding="utf-8")
            (session_dir / "session.json").write_text(
                json.dumps({"session_id": "S", "session_dir": str(malicious_session_dir)}),
                encoding="utf-8",
            )

            session = server.load_workspace_session(str(session_dir), workspace)

            self.assertEqual(str(session_dir.resolve()), session["session_dir"])

    def test_build_projection_summary_runs_archify_receipts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            ir_path = Path(temp_dir) / "artpkg-readiness.architecture.json"
            ir_path.write_text("{}", encoding="utf-8")
            mapping_path = Path(temp_dir) / "artpkg-readiness.mapping.json"
            mapping_path.write_text(json.dumps({
                "session_dir": temp_dir,
                "nodes": [{
                    "archify_id": "authorityState",
                    "artpkg_review_action": {
                        "label": "Answer AUT-001 in ArtPkg",
                        "queue": "authority_sensitive",
                        "focus": "AUT-001",
                    },
                }],
            }), encoding="utf-8")
            projection = SimpleNamespace(
                ir_path=str(ir_path),
                mapping_path=str(mapping_path),
                validation_path=str(Path(temp_dir) / "artpkg-readiness.projection-validation.json"),
            )
            def deliver_receipt(_config, _kind, _ir, html):
                Path(html).write_text("<html></html>", encoding="utf-8")
                return {"ok": True, "receipt_path": "deliver.json"}

            with patch("artpkg_intake_server.artpkg_archify_projection.build_readiness_projection", return_value=projection), \
                    patch("artpkg_intake_server.artpkg_archify_runner.run_archify_validate", return_value={"ok": True, "receipt_path": "validate.json"}) as validate, \
                    patch("artpkg_intake_server.artpkg_archify_runner.run_archify_deliver", side_effect=deliver_receipt) as deliver, \
                    patch("artpkg_intake_server.artpkg_archify_runner.run_archify_visual_check", return_value={"ok": True, "receipt_path": "visual.json"}) as visual:
                summary = server.build_projection_summary({"session_dir": temp_dir})
            decorated_html = Path(summary["html_path"]).read_text(encoding="utf-8")

            self.assertTrue(summary["ready"])
            self.assertIsNone(summary["error"])
            self.assertEqual(str(ir_path), summary["ir_path"])
            self.assertEqual(str(ir_path.with_suffix(".html")), summary["html_path"])
            self.assertEqual("validate.json", summary["archify"]["validate"]["receipt_path"])
            self.assertEqual("deliver.json", summary["archify"]["deliver"]["receipt_path"])
            self.assertEqual("visual.json", summary["archify"]["visual_check"]["receipt_path"])
            validate.assert_called_once()
            deliver.assert_called_once()
            visual.assert_called_once()
            self.assertIn("artpkg-review-actions-data", decorated_html)

    def test_decorate_projection_html_injects_node_review_actions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = Path(temp_dir) / "artpkg-readiness.architecture.html"
            html_path.write_text("<html><body><svg><g data-node-id=\"authorityState\"></g></svg></body></html>", encoding="utf-8")
            mapping_path = Path(temp_dir) / "artpkg-readiness.mapping.json"
            mapping_path.write_text(json.dumps({
                "nodes": [{
                    "archify_id": "authorityState",
                    "artpkg_review_action": {
                        "label": "Answer AUT-001 in ArtPkg",
                        "queue": "authority_sensitive",
                        "focus": "AUT-001",
                        "summary": "Primary question: AUT-001",
                        "impact": "This constrains Gate Readiness.",
                    },
                }]
            }), encoding="utf-8")

            server.decorate_projection_html(html_path, mapping_path)
            html = html_path.read_text(encoding="utf-8")

            self.assertIn("artpkg-review-actions-data", html)
            self.assertIn("Answer AUT-001 in ArtPkg", html)
            self.assertIn("data-artpkg-review-panel", html)
            self.assertIn("authority_sensitive", html)
            self.assertIn("window.open(href, '_blank'", html)

    def test_build_projection_summary_does_not_visual_check_stale_html_after_failed_deliver(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            ir_path = Path(temp_dir) / "artpkg-readiness.architecture.json"
            ir_path.write_text("{}", encoding="utf-8")
            stale_html = ir_path.with_suffix(".html")
            stale_html.write_text("<html>stale</html>", encoding="utf-8")
            projection = SimpleNamespace(
                ir_path=str(ir_path),
                mapping_path=str(Path(temp_dir) / "artpkg-readiness.mapping.json"),
                validation_path=str(Path(temp_dir) / "artpkg-readiness.projection-validation.json"),
            )
            with patch("artpkg_intake_server.artpkg_archify_projection.build_readiness_projection", return_value=projection), \
                    patch("artpkg_intake_server.artpkg_archify_runner.run_archify_validate", return_value={"ok": True}), \
                    patch("artpkg_intake_server.artpkg_archify_runner.run_archify_deliver", return_value={"ok": False, "receipt": {"error": "failed"}}), \
                    patch("artpkg_intake_server.artpkg_archify_runner.run_archify_visual_check") as visual:
                summary = server.build_projection_summary({"session_dir": temp_dir})

            self.assertFalse(summary["ready"])
            self.assertEqual("failed", summary["error"])
        self.assertFalse(Path(summary["html_path"]).exists())
        self.assertFalse(summary["archify"]["visual_check"]["ok"])
        self.assertEqual("Archify deliver did not create fresh HTML", summary["archify"]["visual_check"]["receipt"]["error"])
        visual.assert_not_called()

    def test_projection_html_response_serves_session_visualization_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            session_dir = workspace / ".artpkg" / "intake_sessions" / "session-1"
            session_dir.mkdir(parents=True)
            html_path = session_dir / "artpkg-readiness.architecture.html"
            html_path.write_text("<html><body>readiness</body></html>", encoding="utf-8")

            status, headers, body = server.projection_html_response(str(session_dir), workspace)

            self.assertEqual(200, status)
            self.assertEqual("text/html; charset=utf-8", headers["Content-Type"])
            self.assertIn(b"readiness", body)

    def test_projection_html_response_rejects_missing_visualization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            session_dir = workspace / ".artpkg" / "intake_sessions" / "session-1"
            session_dir.mkdir(parents=True)

            with self.assertRaisesRegex(FileNotFoundError, "projection HTML has not been generated"):
                server.projection_html_response(str(session_dir), workspace)

    def test_ui_contains_upload_review_and_projection_controls(self):
        html_path = Path(__file__).parents[1] / "tools" / "artpkg_intake_ui.html"
        html = html_path.read_text(encoding="utf-8")
        self.assertIn('id="preArtifactsFile"', html)
        self.assertIn('id="restrictedAck"', html)
        self.assertIn('id="exportActions" hidden', html)
        self.assertIn('[hidden] { display:none !important; }', html)
        self.assertIn('id="exportJson"', html)
        self.assertIn('id="exportMarkdown"', html)
        self.assertIn('function activeHumanWork()', html)
        self.assertIn('"repeated_records_pending_review"', html)
        self.assertIn("human_work_counts", html)
        self.assertIn('source.source_status === "ABSENT"', html)
        self.assertIn('source.source_status === "CONFLICTED"', html)
        self.assertIn('source.source_excerpt', html)
        self.assertIn('`- Answer state: ${item.state || "UNKNOWN"}`', html)
        self.assertIn('`- Source status: ${item.source_status || item.source_context?.source_status || "ABSENT"}`', html)
        self.assertIn('`- Source reference: ${item.source_reference || "Not found"}`', html)
        self.assertIn('`- Applicability: ${item.applicability || "CURRENT"}`', html)
        self.assertIn('`- Review priority: ${item.review_priority || "UNSPECIFIED"}`', html)
        self.assertIn('`- Human response reason: ${item.human_response_reason || item.reason || "Review required"}`', html)
        self.assertIn('id="reviewQueues"', html)
        self.assertIn('if (item.kind === "record")', html)
        self.assertIn('confirmButton.dataset.action = "confirm"', html)
        self.assertNotIn('syncAfterReview(item.id, "Answer confirmed")', html)
        self.assertIn('dataset.action = "reject"', html)
        self.assertIn('dataset.action = "answer"', html)
        self.assertIn('id="visualizeGaps"', html)
        self.assertIn("renderQuestionContext", html)
        self.assertIn("renderRecordContext", html)
        self.assertIn("humanQuestion(question.decision_prompt || question.prompt)", html)
        self.assertIn("Answer in your own words", html)
        self.assertIn("ArtPkg could not find a clear answer in the uploaded artifact", html)
        self.assertIn("Why ArtPkg is asking and technical details", html)
        self.assertIn("Backend recommendation", html)
        self.assertIn("Suggested state", html)
        self.assertIn("Optional answer structure", html)
        self.assertIn("a natural-language answer is accepted", html)
        self.assertIn("What ArtPkg found", html)
        self.assertIn("Downstream impact", html)
        self.assertIn("Classification confidence", html)
        self.assertIn("Machine record", html)
        self.assertIn('PROVIDED:"Answered"', html)
        self.assertIn('TO_BE_INSPECTED:"I need to check first"', html)
        self.assertIn('option.value = state', html)
        self.assertNotIn('appendText(card, "strong", "", `${item.id}', html)
        self.assertNotIn("confidence ${item.confidence_score", html)
        self.assertIn("Open visualization", html)
        self.assertIn("/api/session/projection-html", html)
        self.assertIn("if (!session.projection.ready)", html)
        self.assertIn("session.projection.error", html)
        self.assertIn('sealButton.disabled = !checkbox.checked || !pipeline.eligible || pipelineSubmissionInProgress', html)
        self.assertIn('"Pipeline-A admission requirements", pipeline.unmet_conditions', html)
        self.assertIn("Package admitted", html)
        self.assertIn("Structural validation complete", html)
        self.assertIn("Semantic assessment is not implemented", html)
        self.assertNotIn("Send to Pipeline-A — integration not configured", html)

    def test_ui_places_intake_actions_in_top_toolbar_without_sidebar(self):
        html_path = Path(__file__).parents[1] / "tools" / "artpkg_intake_ui.html"
        html = html_path.read_text(encoding="utf-8")

        file_index = html.index('id="preArtifactsFile"')
        start_index = html.index('id="upload"')
        export_index = html.index('id="exportActions"')
        visualization_index = html.index('id="visualizeGaps"')
        acknowledgement_index = html.index('id="restrictedAck"')
        queue_index = html.index('id="queueTabs"')
        self.assertIn('class="intake-toolbar"', html)
        self.assertNotIn("<aside", html)
        self.assertNotIn("grid-template-columns:320px 1fr", html)
        self.assertLess(acknowledgement_index, file_index)
        self.assertLess(file_index, start_index)
        self.assertLess(start_index, export_index)
        self.assertLess(export_index, visualization_index)
        self.assertLess(visualization_index, queue_index)
        self.assertIn('document.getElementById("exportActions").hidden = false', html)

    def test_ui_places_compact_visualization_action_above_review_queues(self):
        html_path = Path(__file__).parents[1] / "tools" / "artpkg_intake_ui.html"
        html = html_path.read_text(encoding="utf-8")

        self.assertIn('class="intake-toolbar"', html)
        self.assertIn('id="visualizeGaps"', html)
        self.assertIn("Visualize gaps", html)
        self.assertIn("visualize unresolved areas first", html)
        self.assertIn("function buildProjection", html)
        self.assertLess(html.index('id="visualizeGaps"'), html.index('id="queueTabs"'))
        self.assertNotIn("Build readiness projection", html)

    def test_ui_projection_result_links_to_html_without_dumping_receipt_json(self):
        html_path = Path(__file__).parents[1] / "tools" / "artpkg_intake_ui.html"
        html = html_path.read_text(encoding="utf-8")

        self.assertIn("Open visualization", html)
        self.assertIn('target = "_blank"', html)
        self.assertIn("session.projection.html_path", html)
        self.assertNotIn("JSON.stringify(session.projection", html)
        self.assertNotIn("Projection built", html)

    def test_ui_loads_session_and_focus_from_query_parameters(self):
        html_path = Path(__file__).parents[1] / "tools" / "artpkg_intake_ui.html"
        html = html_path.read_text(encoding="utf-8")

        self.assertIn("loadSessionFromQuery", html)
        self.assertIn("URLSearchParams(window.location.search)", html)
        self.assertIn("/api/session?dir=", html)
        self.assertIn("focusItemId", html)
        self.assertIn("focusQueueName", html)
        self.assertIn("data-focus-match", html)
        self.assertIn("function queueContaining", html)
        self.assertIn("function syncAfterReview", html)
        self.assertIn("Visualization needs refresh", html)
        self.assertIn("The linked review item is no longer in a queue", html)
        self.assertNotIn("if (focusQueueName && session.review_queues[focusQueueName]) activeQueue = focusQueueName;\n      document.getElementById", html)
        self.assertIn("scrollIntoView", html)

    def test_ui_supports_answer_and_record_actions(self):
        html_path = Path(__file__).parents[1] / "tools" / "artpkg_intake_ui.html"
        html = html_path.read_text(encoding="utf-8")
        self.assertIn("/api/session/answer", html)
        self.assertIn('/api/session/record/${action}', html)
        self.assertNotIn("Record review is not yet answer-actionable in this slice.", html)
