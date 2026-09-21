import hashlib
import json
import os
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_pipeline_admission as admission


class PipelineAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sealed = self.root / "sealed" / ("a" * 64)
        self.sealed.mkdir(parents=True)
        (self.sealed / "immutable").write_bytes(b"sealed bytes")
        self.custody = self.root / "custody"
        self.config = admission.AdmissionConfig(
            pipeline_python=Path("/python with spaces;ignored"),
            admission_cli=Path("/pipeline cli.py;ignored"),
            custody_root=self.custody,
            sdlc_python=Path("/sdlc python;ignored"),
            sdlc_cli=Path("/sdlc cli.py;ignored"),
        )
        self.identity = {
            "package_id": "PKG-0123456789AB",
            "package_version": 1,
            "submission_id": "SUB-0123456789ABCDEFGHIJ",
            "package_sha256": self.sealed.name,
        }

    def tearDown(self):
        self.temp.cleanup()

    def _receipt(self, **changes):
        handoff_id = admission._handoff_id(self.identity["submission_id"], self.identity["package_sha256"])
        custody_id = admission._custody_id(self.identity["submission_id"], self.identity["package_sha256"])
        receipt = {
            "$schema": "https://contracts.local/pipeline-a/artpkg-admission-receipt/v0.1",
            "schema_version": "0.1",
            "receipt_id": "RCP-" + "1" * 32,
            "submission_id": self.identity["submission_id"],
            "package_id": self.identity["package_id"],
            "package_version": self.identity["package_version"],
            "package_sha256": self.identity["package_sha256"],
            "artpkg_source_snapshot_sha256": "b" * 64,
            "handoff_id": handoff_id,
            "custody_id": custody_id,
            "custody_path": f"packages/{custody_id}",
            "custody_manifest_sha256": "c" * 64,
            "pipeline_baseline_revision": "d" * 40,
            "pipeline_source_state_sha256": "e" * 64,
            "sdlc_invocation_id": "INV-" + "3" * 32,
            "sdlc_assessment_id": "ASM-" + "4" * 32,
            "sdlc_status": "STRUCTURE_VALID",
            "sdlc_reason_codes": [],
            "target_binding": None,
            "sdlc_output_path": "assessments/INV-" + "3" * 32,
            "sdlc_output_manifest_sha256": "f" * 64,
            "sdlc_sha256sums_sha256": "0" * 64,
            "admission_status": "ACCEPTED",
            "sdlc_phase": "STRUCTURAL_VALIDATION",
            "progress_status": "SDLC_PHASE_1_COMPLETE",
            "next_action": "SEMANTIC_ASSESSMENT_NOT_IMPLEMENTED",
            "durability_state": "DURABLE",
            "implementation_authority": "NONE",
        }
        receipt.update(changes)
        receipt_dir = self.custody / "receipts" / handoff_id
        receipt_dir.mkdir(parents=True, exist_ok=True)
        receipt_bytes = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        (receipt_dir / "ADMISSION_RECEIPT.json").write_bytes(receipt_bytes)
        complete = {
            "receipt_id": receipt["receipt_id"],
            "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "durability_state": "DURABLE",
            "implementation_authority": "NONE",
        }
        (receipt_dir / "ADMISSION_COMPLETE.json").write_text(
            json.dumps(complete, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        return receipt

    def test_configuration_is_explicit_and_fails_closed(self):
        status = admission.configuration_status({})
        self.assertFalse(status["available"])
        self.assertEqual(list(admission.REQUIRED_ENV), [name for name in admission.REQUIRED_ENV if name in status["unmet_conditions"][0]])

    def test_success_uses_argument_array_and_verified_durable_receipt(self):
        self._receipt()
        before = hashlib.sha256((self.sealed / "immutable").read_bytes()).hexdigest()
        with patch("artpkg_pipeline_admission.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, stdout='{"admission_status":"REJECTED"}', stderr="ignored")
            result = admission.admit_sealed_package(self.sealed, config=self.config, **self.identity)
        argv = run.call_args.args[0]
        self.assertIsInstance(argv, list)
        self.assertEqual(str(self.sealed), argv[argv.index("--package") + 1])
        self.assertEqual(self.sealed.name, argv[argv.index("--expected-package-sha256") + 1])
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertNotIn("PYTHONPATH", run.call_args.kwargs["env"])
        self.assertEqual("ACCEPTED", result["admission_status"])
        self.assertEqual("STRUCTURE_VALID", result["sdlc_status"])
        self.assertEqual("NONE", result["implementation_authority"])
        self.assertEqual(before, hashlib.sha256((self.sealed / "immutable").read_bytes()).hexdigest())
        self.assertFalse(any(word in argv for word in ("semantic", "discovery", "planning", "implementation", "deploy")))

    def test_exit_zero_with_rejected_business_status_is_rejected(self):
        self._receipt(admission_status="REJECTED")
        with patch("artpkg_pipeline_admission.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
            with self.assertRaisesRegex(admission.AdmissionError, "admission_status"):
                admission.admit_sealed_package(self.sealed, config=self.config, **self.identity)

    def test_nonzero_subprocess_is_rejected_without_receipt_inference(self):
        with patch("artpkg_pipeline_admission.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 7, stdout="{}", stderr="failure")
            with self.assertRaisesRegex(admission.AdmissionError, "status 7"):
                admission.admit_sealed_package(self.sealed, config=self.config, **self.identity)

    def test_malformed_and_mismatched_receipts_are_rejected(self):
        self._receipt(package_id="PKG-FFFFFFFFFFFF")
        receipt_dir = self.custody / "receipts" / admission._handoff_id(
            self.identity["submission_id"], self.identity["package_sha256"]
        )
        with self.assertRaisesRegex(admission.AdmissionError, "package_id"):
            admission.verify_receipt(receipt_dir, **self.identity)
        (receipt_dir / "ADMISSION_RECEIPT.json").write_text("not json", encoding="utf-8")
        with self.assertRaisesRegex(admission.AdmissionError, "invalid durable receipt"):
            admission.verify_receipt(receipt_dir, **self.identity)

    def test_replay_returns_unchanged_identities(self):
        self._receipt()
        first = admission.existing_admission(config=self.config, **self.identity)
        second = admission.existing_admission(config=self.config, **self.identity)
        self.assertEqual(first, second)
        self.assertEqual(1, len(list((self.custody / "receipts").iterdir())))

    def test_concurrent_duplicate_submission_is_blocked(self):
        entered = threading.Event()
        release = threading.Event()
        errors = []

        def slow_run(*_args, **_kwargs):
            entered.set()
            release.wait(2)
            return subprocess.CompletedProcess([], 1, stdout="", stderr="")

        def first_call():
            try:
                admission.admit_sealed_package(self.sealed, config=self.config, **self.identity)
            except admission.AdmissionError as error:
                errors.append(error.code)

        with patch("artpkg_pipeline_admission.subprocess.run", side_effect=slow_run):
            worker = threading.Thread(target=first_call)
            worker.start()
            self.assertTrue(entered.wait(1))
            with self.assertRaises(admission.AdmissionError) as raised:
                admission.admit_sealed_package(self.sealed, config=self.config, **self.identity)
            self.assertEqual("ADMISSION_IN_PROGRESS", raised.exception.code)
            release.set()
            worker.join(2)
        self.assertEqual(["PIPELINE_INVOCATION_FAILED"], errors)


if __name__ == "__main__":
    unittest.main()
