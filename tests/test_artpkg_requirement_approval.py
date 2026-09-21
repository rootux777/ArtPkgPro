import json
import unittest
from copy import deepcopy
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_requirement_approval as approval
import artpkg_sealed_handoff as sealed

CANDIDATE = Path("/home/rootux/artpkg-sdlc-contract-review/v0.1/artpkg-fixture-revision-candidate-r2")


def _minimal_document(**overrides):
    document = {
        "schema_version": "0.2",
        "answers": {
            "PKG-003": {"state": "PROVIDED", "source_type": "HUMAN_DECLARATION", "review_disposition": "HUMAN_CONFIRMED"},
            "PKG-005": {"state": "PROVIDED", "source_type": "DERIVED_BY_SCRIPT", "review_disposition": "HUMAN_CONFIRMED"},
            "AUT-002": {"state": "NOT_APPLICABLE", "source_type": "DERIVED_BY_SCRIPT", "review_disposition": "HUMAN_CONFIRMED"},
            "BND-006": {"state": "DEFERRED", "source_type": "HUMAN_DECLARATION", "review_disposition": "HUMAN_CONFIRMED"},
            "OVR-006": {"state": "UNKNOWN", "source_type": "HUMAN_DECLARATION", "review_disposition": "HUMAN_CONFIRMED"},
        },
        "records": {
            "functional_requirements": [
                {"id": "FR-001", "source_type": "HUMAN_DECLARATION", "review_disposition": "HUMAN_CONFIRMED", "fields": {"status": "ACCEPTED"}},
                {"id": "FR-002", "source_type": "DERIVED_BY_SCRIPT", "review_disposition": "HUMAN_CONFIRMED", "fields": {"status": "PROPOSED"}},
            ],
            "risks": [
                {"id": "RSK-001", "source_type": "DERIVED_BY_SCRIPT", "review_disposition": "HUMAN_CONFIRMED", "fields": {"residual_status": "OPEN"}},
                {"id": "RSK-002", "source_type": "HUMAN_DECLARATION", "review_disposition": "HUMAN_CONFIRMED", "fields": {"residual_status": "MITIGATED"}},
            ],
            "artifacts": [
                {"id": "ART-001", "source_type": "TOOL_EXTRACTED", "review_disposition": "HUMAN_CONFIRMED", "fields": {"status": "CURRENT"}},
            ],
        },
    }
    document.update(overrides)
    return document


class DeriveTests(unittest.TestCase):
    def test_distinguishes_human_confirmed_from_seeded_answers(self):
        by_id = {record["id"]: record for record in approval.derive(_minimal_document())}
        self.assertTrue(by_id["PKG-003"]["human_confirmed"])
        self.assertFalse(by_id["PKG-005"]["human_confirmed"])
        self.assertFalse(by_id["AUT-002"]["human_confirmed"])

    def test_record_status_uses_category_specific_field(self):
        by_id = {record["id"]: record for record in approval.derive(_minimal_document())}
        self.assertTrue(by_id["FR-001"]["human_confirmed"])
        self.assertFalse(by_id["FR-002"]["human_confirmed"])
        self.assertFalse(by_id["RSK-001"]["human_confirmed"])
        self.assertEqual("residual_status", by_id["RSK-001"]["status_field"])
        self.assertTrue(by_id["RSK-002"]["human_confirmed"])

    def test_not_applicable_answer_reports_null_not_false(self):
        by_id = {record["id"]: record for record in approval.derive(_minimal_document())}
        self.assertIsNone(by_id["AUT-002"]["human_confirmed"])
        self.assertEqual("not_applicable", by_id["AUT-002"]["basis"])

    def test_deferred_answer_is_never_conflated_with_not_applicable(self):
        by_id = {record["id"]: record for record in approval.derive(_minimal_document())}
        self.assertIsNone(by_id["BND-006"]["human_confirmed"])
        self.assertEqual("deferred", by_id["BND-006"]["basis"])
        self.assertNotEqual(by_id["BND-006"]["basis"], by_id["AUT-002"]["basis"])

    def test_ambiguous_answer_is_flagged_distinctly_from_ordinary_unconfirmed(self):
        by_id = {record["id"]: record for record in approval.derive(_minimal_document())}
        self.assertFalse(by_id["OVR-006"]["human_confirmed"])
        self.assertEqual("unknown_or_ambiguous", by_id["OVR-006"]["basis"])
        self.assertNotEqual(by_id["OVR-006"]["basis"], by_id["PKG-005"]["basis"])

    def test_unmodeled_category_reports_null_not_a_guess(self):
        by_id = {record["id"]: record for record in approval.derive(_minimal_document())}
        self.assertIsNone(by_id["ART-001"]["human_confirmed"])
        self.assertEqual("record_status_unmodeled", by_id["ART-001"]["basis"])

    def test_review_disposition_is_ignored_even_when_present_and_confirmed(self):
        document = _minimal_document()
        document["answers"]["PKG-005"]["review_disposition"] = "HUMAN_CONFIRMED"
        by_id = {record["id"]: record for record in approval.derive(document)}
        self.assertFalse(by_id["PKG-005"]["human_confirmed"])

    def test_rejects_unwired_schema_variant(self):
        with self.assertRaises(approval.ApprovalDerivationError) as raised:
            approval.derive(_minimal_document(schema_version="0.3"))
        self.assertEqual("UNSUPPORTED_SCHEMA_VARIANT", raised.exception.code)

    def test_output_is_deterministic(self):
        document = _minimal_document()
        first = approval.derive(document)
        second = approval.derive(deepcopy(document))
        self.assertEqual(
            sealed.canonical_json(first),
            sealed.canonical_json(second),
        )


@unittest.skipUnless(CANDIDATE.exists(), "durable fixture repository is not present on this host")
class RunAgainstRealFixtureTests(unittest.TestCase):
    def setUp(self):
        root = CANDIDATE / "root"
        self.package_dir = root
        self.handoff = json.loads((root / "ARTPKG_HANDOFF.json").read_text())
        self.expected_sha256 = self.handoff["package"]["package_sha256"]

    def test_fully_approved_fixture_confirms_every_modeled_item(self):
        result = approval.run(self.package_dir, self.expected_sha256)
        self.assertEqual("artpkg.requirement_approval_derivation", result["contract_domain"])
        self.assertEqual(self.handoff["package"]["package_id"], result["derived_from"]["package_id"])
        modeled = [r for r in result["records"] if r["human_confirmed"] is not None]
        self.assertTrue(modeled, "fixture produced no modeled records to check")
        for record in modeled:
            with self.subTest(record=record["id"]):
                self.assertTrue(record["human_confirmed"])

    def test_output_is_reproducible(self):
        first = approval.run(self.package_dir, self.expected_sha256)
        second = approval.run(self.package_dir, self.expected_sha256)
        self.assertEqual(first["records_sha256"], second["records_sha256"])

    def test_rejects_wrong_expected_digest(self):
        with self.assertRaises(approval.ApprovalDerivationError) as raised:
            approval.run(self.package_dir, "0" * 64)
        self.assertEqual("IDENTITY_MISMATCH", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
