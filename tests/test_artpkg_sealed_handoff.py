import io
import json
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_sealed_handoff as handoff
import artifacts_package_questionnaire as questionnaire
import artpkg_intake_server as server


CANDIDATE = Path("/home/rootux/artpkg-sdlc-contract-review/v0.1/artpkg-fixture-revision-candidate-r2")


class SealedHandoffContractTests(unittest.TestCase):
    def test_provenance_and_all_accepted_canonicalization_vectors(self):
        provenance = json.loads((Path(__file__).parent / "fixtures" / "artpkg_contract_candidate_r2_provenance.json").read_text())
        self.assertEqual(CANDIDATE, Path(provenance["candidate_read_only_path"]))
        vectors_path = CANDIDATE / "canonicalization" / "cross_project_canonicalization_vectors_v0.1.json"
        self.assertEqual(provenance["canonicalization_vectors_sha256"], handoff.sha256_bytes(vectors_path.read_bytes()))
        vectors = json.loads(vectors_path.read_text())["vectors"]
        for vector in vectors:
            with self.subTest(vector=vector["id"]):
                if vector["expected_result"] == "ACCEPT":
                    actual = handoff.canonical_json(vector["input_json"], identity_bearing=vector["identity_bearing"])
                    self.assertEqual(vector["expected_canonical_utf8_hex"], actual.hex())
                    self.assertEqual(vector["expected_sha256"], handoff.sha256_bytes(actual))
                else:
                    with self.assertRaises(handoff.HandoffError) as raised:
                        handoff.parse_strict_json(bytes.fromhex(vector["input_bytes_hex"]), identity_bearing=vector["identity_bearing"])
                    self.assertEqual(vector["expected_rejection_reason_code"], raised.exception.code)

    def test_fixture_package_and_content_set_identities_recompute(self):
        root = CANDIDATE / "root"
        payloads = {name: (root / name).read_bytes() for name in handoff.PAYLOAD_INVENTORY}
        self.assertEqual(
            "f5069bb062dea1f53cbb1eb89064ca55c7b76a20b3c612333d65c1bb422ee9ec",
            handoff.package_sha256("PKG-0123456789AB", 1, payloads),
        )
        content = {"ARTPKG_HANDOFF.json": (root / "ARTPKG_HANDOFF.json").read_bytes(), **payloads}
        self.assertEqual(
            "420251d6c83e36be0e2794ac39f1e51df85400670330c0d97bfced6a01b2f20d",
            handoff.content_set_sha256(content),
        )

    def test_exact_inventory_manifest_checksums_and_transport(self):
        root = CANDIDATE / "root"
        accepted = json.loads((root / "ARTPKG_HANDOFF.json").read_text())
        payloads = {name: (root / name).read_bytes() for name in handoff.PAYLOAD_INVENTORY}
        files, _ = handoff.assemble_files(accepted, payloads)
        self.assertEqual(set(handoff.ROOT_INVENTORY), set(files))
        manifest = json.loads(files["MANIFEST.json"])
        self.assertEqual(4, len(manifest["entries"]))
        sums = dict(line.split("  ", 1)[::-1] for line in files["SHA256SUMS"].decode().splitlines())
        self.assertEqual(set(files) - {"SHA256SUMS"}, set(sums))
        for name, digest in sums.items():
            self.assertEqual(digest, handoff.sha256_bytes(files[name]))
        first = handoff.deterministic_zip(files)
        self.assertEqual(first, handoff.deterministic_zip(files))
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            self.assertEqual(set(files), set(archive.namelist()))
            self.assertEqual(files, {name: archive.read(name) for name in archive.namelist()})

    def test_closed_handoff_rejects_pipeline_fields_and_authority(self):
        accepted = json.loads((CANDIDATE / "root" / "ARTPKG_HANDOFF.json").read_text())
        for field in handoff.PROHIBITED_HANDOFF_FIELDS:
            with self.subTest(field=field):
                invalid = deepcopy(accepted)
                invalid[field] = "pipeline-owned"
                with self.assertRaisesRegex(handoff.HandoffError, "root schema is closed"):
                    handoff.validate_handoff(invalid)
        invalid = deepcopy(accepted)
        invalid["implementation_authority"] = "EXECUTE"
        with self.assertRaises(handoff.HandoffError) as raised:
            handoff.validate_handoff(invalid)
        self.assertEqual("AUTHORITY_CONTRADICTION", raised.exception.code)

    def test_target_binding_is_required_nullable_and_closed(self):
        accepted = json.loads((CANDIDATE / "root" / "ARTPKG_HANDOFF.json").read_text())
        handoff.validate_handoff(accepted)
        bound = deepcopy(accepted)
        bound["target_binding"] = {
            "branch": None,
            "evidence_manifest_sha256": "5c42010f411e5df885ec3a0e947d2cd8b7519170df64bdc09d4a58612c467987",
            "kind": "FIXTURE",
            "repository_identity": {"registry": "artpkg-fixture", "repository_id": "urn:fixture:one"},
            "revision": "fixture-v1",
            "target_id": "target:one",
            "verification_state": "EVIDENCE_BOUND",
        }
        handoff.validate_handoff(bound)
        del bound["target_binding"]
        with self.assertRaises(handoff.HandoffError):
            handoff.validate_handoff(bound)

    def test_completion_gate_handles_answers_deferrals_and_validation(self):
        document = {
            "answers": {
                "AUT-001": {"value": "NONE", "state": "PROVIDED", "review_disposition": "HUMAN_CONFIRMED"},
                "OPT-001": {"value": None, "state": "DEFERRED", "review_disposition": "HUMAN_CONFIRMED"},
            },
            "records": {},
        }
        summary = handoff.completion_summary(document, {"errors": [], "warnings": [], "blocking_ids": []})
        self.assertEqual("READY_TO_SEAL", summary["completion_result"])
        self.assertEqual(["OPT-001"], summary["explicitly_deferred_questions"])
        unanswered = deepcopy(document)
        unanswered["answers"]["REQ-001"] = {"value": None, "state": "UNKNOWN", "review_disposition": "HUMAN_CONFIRMED"}
        self.assertEqual("BLOCKED", handoff.completion_summary(unanswered, {"errors": [], "blocking_ids": []})["completion_result"])
        blocked = handoff.completion_summary(document, {"errors": ["validation failed"], "blocking_ids": ["VAL-001"]})
        self.assertEqual("BLOCKED", blocked["completion_result"])

    def test_package_confirmation_approves_pending_snapshot_without_mutating_draft(self):
        document = {
            "answers": {
                "AUT-001": {"value": "NONE", "state": "PROVIDED", "review_disposition": "SEEDED_PENDING_REVIEW"},
                "FIN-001": {"value": "YES", "state": "PROVIDED", "review_disposition": "HUMAN_CONFIRMED"},
                "FIN-002": {"value": "YES", "state": "PROVIDED", "review_disposition": "HUMAN_CONFIRMED"},
                "FIN-003": {"value": "YES", "state": "PROVIDED", "review_disposition": "HUMAN_CONFIRMED"},
            },
            "records": {"functional_requirements": [{"id": "FR-001", "review_disposition": None}]},
            "updated": "2026-09-02T00:00:00+00:00",
        }
        summary = handoff.completion_summary(document, {"errors": [], "warnings": [], "blocking_ids": []})
        self.assertEqual("READY_TO_SEAL", summary["completion_result"])
        approved = handoff.approved_snapshot(document, "reviewer")
        self.assertEqual("SEEDED_PENDING_REVIEW", document["answers"]["AUT-001"]["review_disposition"])
        self.assertEqual("HUMAN_CONFIRMED", approved["answers"]["AUT-001"]["review_disposition"])
        self.assertEqual("HUMAN_CONFIRMED", approved["records"]["functional_requirements"][0]["review_disposition"])

    def test_package_confirmation_preserves_timestamps_for_replay_identity(self):
        document = {
            "created": "2026-08-31T00:00:00Z",
            "updated": "2026-09-03T00:00:00Z",
            "answers": {
                "AUT-001": {
                    "review_disposition": "SEEDED_PENDING_REVIEW",
                    "last_edit_timestamp": "2026-09-01T00:00:00Z",
                },
            },
            "records": {
                "functional_requirements": [{
                    "id": "FR-001",
                    "review_disposition": None,
                    "last_edit": "2026-09-02T00:00:00Z",
                }],
            },
        }

        first = handoff.approved_snapshot(document, "reviewer")
        second = handoff.approved_snapshot(document, "reviewer")

        self.assertEqual(first, second)
        self.assertEqual("2026-09-01T00:00:00Z", first["answers"]["AUT-001"]["last_edit_timestamp"])
        self.assertEqual("2026-09-02T00:00:00Z", first["records"]["functional_requirements"][0]["last_edit"])
        self.assertEqual("2026-09-02T00:00:00Z", first["updated"])

    def test_package_confirmation_canonicalizes_generated_timestamps(self):
        base = {
            "created": "2026-09-01T00:00:00Z",
            "updated": "2026-09-04T00:00:00Z",
            "answers": {
                "AUT-001": {
                    "source_type": "DERIVED_BY_SCRIPT",
                    "timestamp": "2026-09-04T00:00:00Z",
                    "last_edit_timestamp": "2026-09-04T00:00:00Z",
                },
                "FIN-001": {
                    "source_type": "HUMAN_DECLARATION",
                    "timestamp": "2026-09-02T00:00:00Z",
                    "last_edit_timestamp": "2026-09-02T00:00:00Z",
                },
            },
            "records": {},
        }
        reloaded = deepcopy(base)
        reloaded["updated"] = "2026-09-05T00:00:00Z"
        reloaded["answers"]["AUT-001"]["timestamp"] = "2026-09-05T00:00:00Z"
        reloaded["answers"]["AUT-001"]["last_edit_timestamp"] = "2026-09-05T00:00:00Z"

        self.assertEqual(
            handoff.approved_snapshot(base, "reviewer"),
            handoff.approved_snapshot(reloaded, "reviewer"),
        )

    def test_sealed_history_never_overwrites(self):
        root = CANDIDATE / "root"
        accepted = json.loads((root / "ARTPKG_HANDOFF.json").read_text())
        payloads = {name: (root / name).read_bytes() for name in handoff.PAYLOAD_INVENTORY}
        files, _ = handoff.assemble_files(accepted, payloads)
        with tempfile.TemporaryDirectory() as temp_dir:
            first = handoff.seal_to_history(temp_dir, files)
            second = handoff.seal_to_history(temp_dir, files)
            self.assertEqual(first, second)
            changed = dict(files)
            changed["SHA256SUMS"] += b"changed"
            with self.assertRaises(handoff.HandoffError):
                handoff.seal_to_history(temp_dir, changed)

    def test_full_seal_lifecycle_reuses_identical_bytes_and_versions_edits(self):
        document = json.loads((CANDIDATE / "root" / "artifacts_package_answers.json").read_text())
        document["setup"]["template_path"] = str(
            Path(__file__).parents[1] / "reusable_artifacts_package_template (1).md"
        )
        validation = questionnaire.validate_answers(document)
        self.assertEqual([], validation["errors"])
        with tempfile.TemporaryDirectory() as temp_dir:
            session = {"document": document, "validation": validation, "session_dir": temp_dir}
            with self.assertRaises(handoff.HandoffError) as raised:
                handoff.seal_session(session, "reviewer", "not confirmed", True)
            self.assertEqual("CONFIRMATION_REQUIRED", raised.exception.code)

            first, first_files = handoff.seal_session(
                session, "reviewer", handoff.CONFIRMATION_TEXT, True,
            )
            repeated, repeated_files = handoff.seal_session(
                session, "reviewer", handoff.CONFIRMATION_TEXT, True,
            )
            self.assertEqual(1, first.package_version)
            self.assertEqual(first, repeated)
            self.assertEqual(first_files, repeated_files)
            self.assertTrue(first.sealed_dir.is_dir())
            self.assertEqual(1, len(list((Path(temp_dir) / "sealed_packages").iterdir())))

            edited = deepcopy(document)
            edited["answers"]["OVR-008"]["value"] = "A newly reviewed checkpoint"
            edited["answers"]["OVR-008"]["last_edit_timestamp"] = "2026-09-02T00:00:00Z"
            edited["updated"] = "2026-09-02T00:00:00Z"
            edited_session = {
                "document": edited,
                "validation": questionnaire.validate_answers(edited),
                "session_dir": temp_dir,
            }
            second, second_files = handoff.seal_session(
                edited_session, "reviewer", handoff.CONFIRMATION_TEXT, True,
            )
            self.assertEqual(2, second.package_version)
            self.assertNotEqual(first.submission_id, second.submission_id)
            self.assertNotEqual(first.package_sha256, second.package_sha256)
            second_handoff = json.loads(second_files["ARTPKG_HANDOFF.json"])
            self.assertEqual(first.package_sha256, second_handoff["lineage"]["parent_package_sha256"])
            self.assertEqual(2, len(list((Path(temp_dir) / "sealed_packages").iterdir())))

    def test_owner_scoped_download_reconstructs_exact_root(self):
        root = CANDIDATE / "root"
        accepted = json.loads((root / "ARTPKG_HANDOFF.json").read_text())
        payloads = {name: (root / name).read_bytes() for name in handoff.PAYLOAD_INVENTORY}
        files, _ = handoff.assemble_files(accepted, payloads)
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session_dir = workspace / ".artpkg" / "users" / "alice" / "sessions" / "session-1"
            session_dir.mkdir(parents=True)
            sealed_dir = handoff.seal_to_history(session_dir, files)
            headers, body = server.sealed_zip_response(str(session_dir), sealed_dir.name, "alice", workspace)
            self.assertEqual("application/zip", headers["Content-Type"])
            with zipfile.ZipFile(io.BytesIO(body)) as archive:
                reconstructed = {name: archive.read(name) for name in archive.namelist()}
            self.assertEqual(files, reconstructed)

    def test_sealed_history_rejects_links_and_ui_claims_no_submission(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = Path(temp_dir) / "sealed_packages"
            history.mkdir()
            outside = Path(temp_dir) / "outside"
            outside.mkdir()
            sealed_id = "a" * 64
            (history / sealed_id).symlink_to(outside, target_is_directory=True)
            with self.assertRaises(handoff.HandoffError) as raised:
                handoff.load_sealed_files(temp_dir, sealed_id)
            self.assertEqual("UNSAFE_PATH", raised.exception.code)
        html = (Path(__file__).parents[1] / "tools" / "artpkg_intake_ui.html").read_text()
        self.assertIn("Seal Package for Pipeline-A", html)
        self.assertIn("blockedSealButton.disabled = true", html)
        self.assertIn('sealing.implementation_authority || "Not established"', html)
        self.assertIn("Final external-assessment review", html)
        self.assertIn("Record final assessment attestations", html)
        self.assertIn("const pendingFinalAttestations = new Set()", html)
        self.assertNotIn("checkbox.disabled = !prerequisitesComplete", html)
        self.assertIn("pendingFinalAttestations.add(qid)", html)
        self.assertIn("function humanAnswerInput(item)", html)
        self.assertIn('["BOOLEAN", "ENUM"].includes(answerType)', html)
        self.assertNotIn("!prerequisitesComplete || !checks.every", html)
        self.assertIn('id="blockerReview"', html)
        self.assertIn("Resolve before sealing", html)
        self.assertIn('sealResolvableList(findings, "Unanswered questions", sealing.unanswered_questions, "None")', html)
        self.assertIn('sealResolvableList(findings, "Validation blockers", sealing.seal_blockers, "None")', html)
        self.assertIn('link.href = `#blocker-${id}`', html)
        self.assertIn('finding.includes("FIN-001..FIN-003")', html)
        self.assertIn('questionId, value] of [["AUT-001", "NONE"], ["FIN-001", "YES"], ["FIN-002", "YES"], ["FIN-003", "YES"]]', html)
        self.assertIn("Download Sealed Package", html)
        self.assertIn("Pipeline-A admission requirements", html)
        self.assertIn("Package admitted", html)
        self.assertIn('progress.className = "pipeline-progress"', html)
        self.assertIn('["ArtPkg", "Package sealed"', html)
        self.assertIn('["Pipeline-A", "Admission accepted"', html)
        self.assertIn('["SDLC Harness", "Phase 1 complete"', html)
        self.assertIn('["Next boundary", "Semantic assessment"', html)
        self.assertIn('admission?.admission_status === "ACCEPTED"', html)
        self.assertIn("Pipeline-A handoff complete", html)
        self.assertIn("The Phase 1 receipt is unchanged. DSH advisory review is a separate handoff", html)
        self.assertIn("Send to DSH", html)
        self.assertNotIn("/api/session/send", html)


if __name__ == "__main__":
    unittest.main()