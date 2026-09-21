"""Fail-closed ArtPkg to Pipeline-A Phase 1 admission boundary."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import artpkg_sealed_handoff


AUTHORITY = "NONE"
REQUIRED_ENV = (
    "PIPELINE_A_PYTHON",
    "PIPELINE_A_ADMISSION_CLI",
    "PIPELINE_A_CUSTODY_ROOT",
    "SDLC_PHASE1_PYTHON",
    "SDLC_PHASE1_CLI",
)
RECEIPT_FIELDS = {
    "$schema", "schema_version", "receipt_id", "submission_id", "package_id",
    "package_version", "package_sha256", "artpkg_source_snapshot_sha256", "handoff_id",
    "custody_id", "custody_path", "custody_manifest_sha256", "pipeline_baseline_revision",
    "pipeline_source_state_sha256", "sdlc_invocation_id", "sdlc_assessment_id", "sdlc_status",
    "sdlc_reason_codes", "target_binding", "sdlc_output_path", "sdlc_output_manifest_sha256",
    "sdlc_sha256sums_sha256", "admission_status", "sdlc_phase", "progress_status",
    "next_action", "durability_state", "implementation_authority",
}
COMPLETE_FIELDS = {"receipt_id", "receipt_sha256", "durability_state", "implementation_authority"}
_locks_guard = threading.Lock()
_locks: dict[str, threading.Lock] = {}


class AdmissionError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class AdmissionConfig:
    pipeline_python: Path
    admission_cli: Path
    custody_root: Path
    sdlc_python: Path
    sdlc_cli: Path


def _regular_file(path: Path, *, executable: bool, label: str) -> Path:
    configured = path.expanduser().absolute()
    resolved = configured.resolve(strict=True)
    mode = resolved.stat().st_mode
    if not stat.S_ISREG(mode) or not os.access(resolved, os.R_OK):
        raise AdmissionError("CONFIGURATION_UNAVAILABLE", f"{label} must be a readable regular file")
    if executable and not os.access(resolved, os.X_OK):
        raise AdmissionError("CONFIGURATION_UNAVAILABLE", f"{label} must be executable")
    return configured


def load_config(environment: Mapping[str, str] | None = None) -> AdmissionConfig:
    values = os.environ if environment is None else environment
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise AdmissionError(
            "CONFIGURATION_UNAVAILABLE",
            "Pipeline-A admission unavailable; missing configuration: " + ", ".join(missing),
        )
    try:
        custody_root = Path(values["PIPELINE_A_CUSTODY_ROOT"]).expanduser().resolve()
        parent = next((path for path in (custody_root, *custody_root.parents) if path.exists()), None)
        if parent is None or not parent.is_dir() or not os.access(parent, os.W_OK | os.X_OK):
            raise AdmissionError(
                "CONFIGURATION_UNAVAILABLE", "PIPELINE_A_CUSTODY_ROOT has no writable parent directory",
            )
        return AdmissionConfig(
            pipeline_python=_regular_file(Path(values["PIPELINE_A_PYTHON"]), executable=True, label="PIPELINE_A_PYTHON"),
            admission_cli=_regular_file(Path(values["PIPELINE_A_ADMISSION_CLI"]), executable=False, label="PIPELINE_A_ADMISSION_CLI"),
            custody_root=custody_root,
            sdlc_python=_regular_file(Path(values["SDLC_PHASE1_PYTHON"]), executable=True, label="SDLC_PHASE1_PYTHON"),
            sdlc_cli=_regular_file(Path(values["SDLC_PHASE1_CLI"]), executable=False, label="SDLC_PHASE1_CLI"),
        )
    except (OSError, RuntimeError) as exc:
        raise AdmissionError("CONFIGURATION_UNAVAILABLE", f"Pipeline-A admission unavailable: {exc}") from exc


def configuration_status(environment: Mapping[str, str] | None = None) -> dict[str, Any]:
    try:
        load_config(environment)
        return {"available": True, "unmet_conditions": []}
    except AdmissionError as exc:
        return {"available": False, "unmet_conditions": [str(exc)]}


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _strict_object(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        content = path.read_bytes()
        value = json.loads(content.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AdmissionError("RECEIPT_INVALID", f"invalid durable receipt file: {path.name}") from exc
    if not isinstance(value, dict):
        raise AdmissionError("RECEIPT_INVALID", f"durable receipt file is not an object: {path.name}")
    return value, content


def _handoff_id(submission_id: str, package_sha256: str) -> str:
    value = {"submission_id": submission_id, "sealed_package_sha256": package_sha256}
    digest = _sha256(artpkg_sealed_handoff.canonical_json(value))[:32].upper()
    return f"HND-{digest}"


def _custody_id(submission_id: str, package_sha256: str) -> str:
    return "CUS-" + _handoff_id(submission_id, package_sha256).removeprefix("HND-")


def verify_receipt(
    receipt_dir: Path,
    *,
    package_id: str,
    package_version: int,
    submission_id: str,
    package_sha256: str,
) -> dict[str, Any]:
    if receipt_dir.is_symlink() or not receipt_dir.is_dir():
        raise AdmissionError("RECEIPT_INVALID", "durable admission receipt directory is missing")
    if {path.name for path in receipt_dir.iterdir()} != {"ADMISSION_RECEIPT.json", "ADMISSION_COMPLETE.json"}:
        raise AdmissionError("RECEIPT_INVALID", "durable admission receipt inventory is invalid")
    receipt, receipt_bytes = _strict_object(receipt_dir / "ADMISSION_RECEIPT.json")
    complete, _ = _strict_object(receipt_dir / "ADMISSION_COMPLETE.json")
    if set(receipt) != RECEIPT_FIELDS or set(complete) != COMPLETE_FIELDS:
        raise AdmissionError("RECEIPT_INVALID", "durable admission receipt schema is invalid")
    expected_handoff = _handoff_id(submission_id, package_sha256)
    expected_custody = _custody_id(submission_id, package_sha256)
    expected = {
        "package_id": package_id,
        "package_version": package_version,
        "submission_id": submission_id,
        "package_sha256": package_sha256,
        "handoff_id": expected_handoff,
        "custody_id": expected_custody,
        "custody_path": f"packages/{expected_custody}",
        "admission_status": "ACCEPTED",
        "sdlc_phase": "STRUCTURAL_VALIDATION",
        "sdlc_status": "STRUCTURE_VALID",
        "progress_status": "SDLC_PHASE_1_COMPLETE",
        "implementation_authority": AUTHORITY,
        "next_action": "SEMANTIC_ASSESSMENT_NOT_IMPLEMENTED",
        "durability_state": "DURABLE",
    }
    mismatched = [key for key, value in expected.items() if receipt.get(key) != value]
    if mismatched:
        raise AdmissionError("RECEIPT_BINDING_MISMATCH", "durable receipt mismatch: " + ", ".join(mismatched))
    if (
        receipt.get("$schema") != "https://contracts.local/pipeline-a/artpkg-admission-receipt/v0.1"
        or receipt.get("schema_version") != "0.1"
        or receipt.get("sdlc_output_path") != f"assessments/{receipt.get('sdlc_invocation_id')}"
    ):
        raise AdmissionError("RECEIPT_BINDING_MISMATCH", "durable receipt contract or output path is not bound")
    if (
        complete.get("receipt_id") != receipt.get("receipt_id")
        or complete.get("receipt_sha256") != _sha256(receipt_bytes)
        or complete.get("durability_state") != "DURABLE"
        or complete.get("implementation_authority") != AUTHORITY
    ):
        raise AdmissionError("RECEIPT_INVALID", "admission completion marker does not bind the durable receipt")
    for field in ("custody_id", "handoff_id", "sdlc_invocation_id", "sdlc_assessment_id", "receipt_id"):
        if not isinstance(receipt.get(field), str) or not receipt[field]:
            raise AdmissionError("RECEIPT_INVALID", f"durable receipt is missing {field}")
    return {
        "admission_status": receipt["admission_status"],
        "sdlc_status": receipt["sdlc_status"],
        "progress_status": receipt["progress_status"],
        "sdlc_phase": receipt["sdlc_phase"],
        "package_id": receipt["package_id"],
        "package_version": receipt["package_version"],
        "submission_id": receipt["submission_id"],
        "custody_id": receipt["custody_id"],
        "handoff_id": receipt["handoff_id"],
        "invocation_id": receipt["sdlc_invocation_id"],
        "assessment_id": receipt["sdlc_assessment_id"],
        "receipt_id": receipt["receipt_id"],
        "implementation_authority": receipt["implementation_authority"],
        "next_action": receipt["next_action"],
    }


def existing_admission(
    *,
    package_id: str,
    package_version: int,
    submission_id: str,
    package_sha256: str,
    config: AdmissionConfig | None = None,
) -> dict[str, Any] | None:
    config = config or load_config()
    receipt_dir = config.custody_root / "receipts" / _handoff_id(submission_id, package_sha256)
    if not receipt_dir.exists():
        return None
    return verify_receipt(
        receipt_dir,
        package_id=package_id,
        package_version=package_version,
        submission_id=submission_id,
        package_sha256=package_sha256,
    )


def admit_sealed_package(
    sealed_dir: Path,
    *,
    package_id: str,
    package_version: int,
    submission_id: str,
    package_sha256: str,
    config: AdmissionConfig | None = None,
) -> dict[str, Any]:
    config = config or load_config()
    sealed_dir = sealed_dir.resolve(strict=True)
    if config.custody_root == sealed_dir or sealed_dir in config.custody_root.parents or config.custody_root in sealed_dir.parents:
        raise AdmissionError("CONFIGURATION_UNAVAILABLE", "custody root must be separate from the sealed package directory")
    lock_key = os.fspath(sealed_dir)
    with _locks_guard:
        lock = _locks.setdefault(lock_key, threading.Lock())
    if not lock.acquire(blocking=False):
        raise AdmissionError("ADMISSION_IN_PROGRESS", "Pipeline-A admission is already in progress for this package")
    try:
        argv = [
            os.fspath(config.pipeline_python), os.fspath(config.admission_cli), "admit",
            "--package", os.fspath(sealed_dir),
            "--expected-package-sha256", package_sha256,
            "--custody-root", os.fspath(config.custody_root),
            "--sdlc-python", os.fspath(config.sdlc_python),
            "--sdlc-cli", os.fspath(config.sdlc_cli),
        ]
        try:
            child_environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
            completed = subprocess.run(
                argv, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                shell=False, check=False, timeout=60, env=child_environment,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AdmissionError("PIPELINE_INVOCATION_FAILED", "Pipeline-A admission process failed to run") from exc
        if completed.returncode != 0:
            raise AdmissionError("PIPELINE_INVOCATION_FAILED", f"Pipeline-A admission exited with status {completed.returncode}")
        receipt_dir = config.custody_root / "receipts" / _handoff_id(submission_id, package_sha256)
        return verify_receipt(
            receipt_dir,
            package_id=package_id,
            package_version=package_version,
            submission_id=submission_id,
            package_sha256=package_sha256,
        )
    finally:
        lock.release()