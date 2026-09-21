"""Coding handoff tests: temporary files and fake DSH only; never a live build."""
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import artpkg_coding_handoff as coding
import artpkg_dsh_bridge as bridge
import artpkg_sealed_handoff as handoff
import test_artpkg_dsh_bridge as fixtures


class CodingTests(fixtures.SealedCase):
    def setUp(self):
        super().setUp()
        self.document = handoff.parse_strict_json(self.files["artifacts_package_answers.json"])
        self.template = self.root / "template.md"
        self.template.write_text("# Template")
        self.document["setup"]["template_path"] = str(self.template)
        self.document.setdefault("attestation", {})
        self.session["document"] = self.document
        self.session["validation"] = {"errors": [], "warnings": [], "status": "DRAFT"}
        self.source_path = self.session_dir / "source_pre_artifacts.md"
        self.source_path.write_text("# Source\nCMP-001 is PROPOSED, not implemented.\n")
        self.stack.enter_context(patch.object(coding.intake, "_refresh_session", side_effect=self.refresh))
        os.environ["ARTPKG_CODING_ROOT"] = str(self.root / "coding-workspaces")

    def refresh(self, session):
        session["document"]["updated"] = "2026-09-07T00:00:00Z"

    def approve(self):
        coding.approve_review(self.session, "alice", coding.review_digest(self.session), coding.REVIEW_CONFIRMATION)

    def reviewed_seal(self):
        self.approve()
        payloads = {name: self.files[name] for name in handoff.PAYLOAD_INVENTORY}
        payloads["artifacts_package_answers.json"] = handoff.canonical_json(self.document)
        contract = handoff.parse_strict_json(self.files["ARTPKG_HANDOFF.json"])
        contract["package"]["package_sha256"] = handoff.package_sha256(
            contract["package"]["package_id"], contract["package"]["package_version"], payloads)
        self.files, _ = handoff.assemble_files(contract, payloads)
        self.sealed_dir = handoff.seal_to_history(self.session_dir, self.files)
        self.sealing["sealed_id"] = self.sealed_dir.name
        self.write_receipt()

    def prepare(self):
        return coding.prepare(self.session, "alice", self.sealing["sealed_id"], coding.PREPARE_CONFIRMATION)

    def test_review_is_bound_to_source_document_and_template(self):
        self.approve()
        self.assertTrue(coding.review_is_current(self.session))
        self.assertEqual("NONE", self.document["attestation"]["final_package_review"]["authority_effect"])
        old = self.source_path.read_text()
        self.source_path.write_text(old + "changed")
        self.assertFalse(coding.review_is_current(self.session))
        self.source_path.write_text(old)
        self.assertTrue(coding.review_is_current(self.session))
        self.template.write_text("changed")
        self.assertFalse(coding.review_is_current(self.session))

    def test_answer_edits_invalidate_review(self):
        self.approve()
        self.document["answers"]["PKG-001"]["value"] = "Changed"
        self.assertFalse(coding.review_is_current(self.session))

    def test_attested_source_cannot_be_replaced_without_review(self):
        self.approve()
        self.document["attestation"]["final_package_review"]["source_evidence"]["text"] = "replaced"
        self.assertFalse(coding.review_is_current(self.session))

    def test_review_repeated_acknowledgement_is_idempotent(self):
        self.approve()
        before = deepcopy(self.document)
        self.approve()
        self.assertEqual(before, self.document)

    def test_stale_or_missing_confirmation_cannot_approve(self):
        for digest, confirmation in (("wrong", coding.REVIEW_CONFIRMATION), (coding.review_digest(self.session), "yes")):
            with self.assertRaises(ValueError):
                coding.approve_review(self.session, "alice", digest, confirmation)
        self.assertNotIn("final_package_review", self.document["attestation"])

    def test_source_symlink_is_rejected(self):
        self.source_path.unlink()
        self.source_path.symlink_to(self.template)
        with self.assertRaises(ValueError):
            self.approve()

    def test_source_size_limit_no_truncation(self):
        with patch.object(coding, "MAX_SOURCE", 3):
            with self.assertRaises(ValueError):
                self.approve()

    def test_missing_source_explicitly_recorded(self):
        self.source_path.unlink()
        self.approve()
        self.assertIsNone(self.document["attestation"]["final_package_review"]["source_evidence"])

    def test_open_human_confirmed_question_stays_open(self):
        self.document["records"]["questions"] = [{"id": "Q-B001", "review_disposition": "HUMAN_CONFIRMED",
                                                  "fields": {"current_disposition": "OPEN"}}]
        self.assertEqual(1, len(coding.project_context(self.document)["open_questions"]))

    def test_old_sealed_package_without_final_review_refused(self):
        with self.assertRaises(ValueError):
            coding.companion_files(self.files, self.binding())

    def test_companion_preserves_exact_sealed_bytes_and_source(self):
        self.reviewed_seal()
        output = coding.companion_files(self.files, self.binding())
        for name, raw in self.files.items():
            self.assertEqual(raw, output["handoff/sealed/" + name])
        self.assertEqual(self.source_path.read_bytes(), output["handoff/source_pre_artifacts.md"])
        self.assertNotIn(b"CMP-001", output["project/AGENTS.md"])
        manifest = json.loads(output["handoff/COMPANION_MANIFEST.json"])
        for name, digest in manifest["sha256"].items():
            self.assertEqual(digest, bridge.digest(output[name]))
        self.assertEqual("NONE", manifest["binding"]["implementation_authority"])

    def test_prepare_creates_blank_standard_session_and_never_prompts(self):
        self.reviewed_seal()
        fake = self.start_dsh()
        before = self.snapshot()
        result = self.prepare()
        self.assertFalse(result["prompt_sent"])
        self.assertEqual("standard", result["preset"])
        self.assertEqual("REQUIRES_DSH_HUMAN_APPROVAL", result["execution_approval"])
        project = Path(result["workspace"])
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertTrue((project.parent / "handoff" / "sealed" / "MANIFEST.json").is_file())
        self.assertEqual(before, self.snapshot())
        self.assertEqual([], fake.prompts)
        self.assertTrue(fake.sessions[result["dsh_session_id"]]["blank"])
        self.assertEqual(4, len(result["prompts"]))
        self.assertTrue(all(self.sealing["package_id"] in p["text"] for p in result["prompts"]))

    def test_retry_after_ready_does_not_reconfigure_used_session(self):
        self.reviewed_seal()
        fake = self.start_dsh()
        result = self.prepare()
        fake.sessions[result["dsh_session_id"]]["blank"] = False
        count = len(fake.calls)
        self.assertEqual(result, self.prepare())
        self.assertEqual(count, len(fake.calls))

    def test_browser_address_can_change_without_recreating_coding_workspace(self):
        self.reviewed_seal()
        fake = self.start_dsh()
        first = self.prepare()
        self.config_path.with_name("dsh-browser.json").write_text(json.dumps({"browser_url":"http://192.168.1.163:3080/"}))
        self.config_path.with_name("dsh-browser.json").chmod(0o600)
        before = len(fake.calls)
        result = self.prepare()
        self.assertEqual(first["workspace"], result["workspace"])
        self.assertEqual(first["dsh_session_id"], result["dsh_session_id"])
        self.assertEqual("http://192.168.1.163:3080/", result["chat_url"])
        self.assertEqual(before, len(fake.calls))

    def test_changed_companion_refuses_overwrite(self):
        self.reviewed_seal()
        self.start_dsh()
        result = self.prepare()
        path = Path(result["workspace"]) / "AGENTS.md"
        path.write_text("user modification")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual("user modification", path.read_text())

    def test_untracked_remote_session_cannot_be_adopted(self):
        self.reviewed_seal()
        fake = self.start_dsh()
        sid = "artpkg-code-" + bridge.digest(handoff.canonical_json(self.binding()))
        fake.sessions[sid] = {"sessionId": sid, "blank": True, "running": False}
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual([], fake.prompts)

    def test_failed_creation_can_resume_but_nonblank_cannot(self):
        self.reviewed_seal()
        fake = self.start_dsh()
        fake.overrides["session/create"] = {}
        with self.assertRaises(ValueError):
            self.prepare()
        del fake.overrides["session/create"]
        fake.roster_changes["blank"] = False
        with self.assertRaises(ValueError):
            self.prepare()
        fake.roster_changes.clear()
        self.assertEqual("READY", self.prepare()["status"])
        self.assertEqual([], fake.prompts)

    def test_changed_model_does_not_reuse_session(self):
        self.reviewed_seal()
        self.start_dsh()
        self.prepare()
        self.write_config(model="another-model")
        with self.assertRaises(ValueError):
            self.prepare()

    def test_unconfirmed_stale_seal_and_source_change_refused(self):
        self.reviewed_seal()
        fake = self.start_dsh()
        for sealed, confirmation in (("bad", coding.PREPARE_CONFIRMATION), (self.sealing["sealed_id"], "yes")):
            with self.assertRaises(ValueError):
                coding.prepare(self.session, "alice", sealed, confirmation)
        self.source_path.write_text("changed")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual([], fake.calls)

    def test_storage_overlap_and_symlink_refused(self):
        self.reviewed_seal()
        fake = self.start_dsh()
        for root in (self.custody / "nested", self.session_dir / "nested", self.state / "nested"):
            os.environ["ARTPKG_CODING_ROOT"] = str(root)
            with self.assertRaises(ValueError):
                self.prepare()
        link = self.root / "link"
        link.symlink_to(self.state, target_is_directory=True)
        os.environ["ARTPKG_CODING_ROOT"] = str(link)
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual([], fake.calls)


class ReviewLifecycleTests(unittest.TestCase):
    """Use real load/save/refresh, with clocks advanced rather than fast same-second mocks."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        template = root / "template.md"
        template.write_text("# Review template\n")
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        self.q = coding.intake.questionnaire
        with patch.object(self.q, "now", return_value="2026-09-07T10:00:00Z"):
            session = coding.intake.create_intake_session(source, root, template_path=template, respondent="Reviewer")
            self.q.set_answer(session["document"], "PKG-002", "DISCOVERY")
            self.q.set_answer(session["document"], "PKG-005", "NOT_CREATED")
            coding.intake._refresh_session(session)
        self.path = Path(session["session_dir"])

    def load(self, stamp):
        with patch.object(self.q, "now", return_value=stamp):
            return coding.intake.load_intake_session(self.path)

    def test_discovery_review_fingerprint_survives_later_loads_without_writes(self):
        before = (self.path / "answers.json").read_bytes()
        first = self.load("2026-09-07T10:01:00Z")
        later = self.load("2026-09-07T10:02:00Z")
        self.assertEqual(coding.review_digest(first), coding.review_digest(later))
        self.assertEqual(first["document"], later["document"])
        self.assertEqual(before, (self.path / "answers.json").read_bytes())

    def test_saved_review_remains_current_through_refresh_and_reload(self):
        preview = self.load("2026-09-07T10:01:00Z")
        expected = coding.review_digest(preview)
        posted = self.load("2026-09-07T10:02:00Z")
        with patch.object(self.q, "now", return_value="2026-09-07T10:03:00Z"):
            coding.approve_review(posted, "Reviewer", expected, coding.REVIEW_CONFIRMATION)
        self.assertTrue(coding.review_is_current(posted))
        later = self.load("2026-09-07T10:04:00Z")
        self.assertTrue(coding.review_is_current(later))
        self.assertEqual(expected, coding.review_digest(later))
        self.assertEqual(posted["document"], later["document"])
        before = (self.path / "answers.json").read_bytes()
        coding.approve_review(later, "Reviewer", expected, coding.REVIEW_CONFIRMATION)
        self.assertEqual(before, (self.path / "answers.json").read_bytes())

    def test_real_edit_still_rejects_previously_displayed_review(self):
        session = self.load("2026-09-07T10:01:00Z")
        expected = coding.review_digest(session)
        coding.intake.provide_answer(session, "PKG-001", "Changed project", "Reviewer")
        later = self.load("2026-09-07T10:02:00Z")
        with self.assertRaisesRegex(ValueError, "stale"):
            coding.approve_review(later, "Reviewer", expected, coding.REVIEW_CONFIRMATION)
        self.assertFalse(coding.review_is_current(later))

    def test_unchanged_discovery_answers_keep_human_review_metadata(self):
        session = self.load("2026-09-07T10:01:00Z")
        for qid in ("AUT-001", "PKG-006"):
            coding.intake.confirm_answer(session, qid, "Reviewer")
        expected = deepcopy(session["document"]["answers"])
        later = self.load("2026-09-07T10:02:00Z")
        for qid in ("AUT-001", "PKG-006"):
            self.assertEqual(expected[qid], later["document"]["answers"][qid])
            self.assertEqual("HUMAN_CONFIRMED", later["document"]["answers"][qid]["review_disposition"])

    def test_discovery_profile_corrections_are_still_applied_and_persisted(self):
        session = self.load("2026-09-07T10:01:00Z")
        session["document"]["answers"].pop("AUT-001")
        session["document"]["answers"].pop("PKG-006")
        coding.intake._refresh_session(session)
        saved = json.loads((self.path / "answers.json").read_text())
        self.assertEqual(session["document"], saved)
        self.assertEqual("NONE", saved["answers"]["AUT-001"]["value"])
        self.assertEqual("NOT_APPLICABLE", saved["answers"]["PKG-006"]["state"])


class CodingRouteTests(fixtures.DSHRouteTests):
    def test_coding_routes_auth_owner_origin_and_content_type(self):
        with patch.object(coding, "approve_review") as approve, patch.object(coding, "prepare") as prepare:
            for route in ("/api/session/final-review", "/api/session/coding-prepare"):
                self.assertEqual(401, self.request(route, user=None)[0])
                self.assertEqual(403, self.request(route, user="bob")[0])
                self.assertEqual(403, self.request(route, origin="http://evil.invalid")[0])
                self.assertEqual(403, self.request(route, content_type="text/plain")[0])
            approve.assert_not_called()
            prepare.assert_not_called()

    def test_owned_prepare_calls_only_coding_adapter(self):
        with patch.object(coding, "prepare", return_value={"prompt_sent": False}) as prepare:
            status, body = self.request("/api/session/coding-prepare", confirmation=coding.PREPARE_CONFIRMATION)
            self.assertEqual((200, {"prompt_sent": False}), (status, body))
            prepare.assert_called_once_with(self.loaded_session, "alice", "", coding.PREPARE_CONFIRMATION)
            self.send_mock.assert_not_called()

    def test_review_get_owner_scoped(self):
        route = "/api/session/final-review?dir=" + str(self.owned)
        with patch.object(coding, "review_preview", return_value={"review_current": False}) as preview:
            self.assertEqual(401, self.request(route, user=None, method="GET")[0])
            self.assertEqual(403, self.request(route, user="bob", method="GET")[0])
            preview.assert_not_called()
            self.assertEqual(200, self.request(route, method="GET")[0])
            preview.assert_called_once_with(self.loaded_session, "alice")


if __name__ == "__main__":
    unittest.main()