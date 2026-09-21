"""Deterministic ArtPkg to Pipeline-A sealed handoff assembly."""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import re
import tempfile
import unicodedata
import zipfile
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT_INVENTORY = (
    "ARTPKG_HANDOFF.json",
    "MANIFEST.json",
    "SHA256SUMS",
    "artifacts_package.md",
    "artifacts_package_answers.json",
    "artifacts_package_validation.md",
)
PAYLOAD_INVENTORY = (
    "artifacts_package.md",
    "artifacts_package_answers.json",
    "artifacts_package_validation.md",
)
PROHIBITED_HANDOFF_FIELDS = {
    "admitted_at", "content_set_sha256", "custody_receipt_id", "handoff_id", "idempotency_key",
}
SOURCE_CLASSIFICATIONS = {
    "EXTERNAL_REFERENCE", "HUMAN_APPROVED_ARTPKG", "HUMAN_SUPPLIED_UNCONFIRMED",
    "MODEL_PROPOSAL", "REPOSITORY_EVIDENCE", "TOOL_EXTRACTED",
}
MAX_FILES = 64
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_PARSED_BYTES = 4 * 1024 * 1024
MAX_PATH_BYTES = 240
MAX_DEPTH = 8
MAX_RECORDS = 10_000
MAX_SAFE_INTEGER = 9_007_199_254_740_991
CONFIRMATION_TEXT = (
    "This creates an immutable package for Pipeline-A custody and external\n"
    "assessment. It does not authorize implementation or repository changes."
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class HandoffError(ValueError):
    """A deterministic sealed-handoff validation failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class SealResult:
    sealed_dir: Path
    package_id: str
    package_version: int
    submission_id: str
    package_sha256: str
    content_set_sha256: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _utf16_key(value: str) -> bytes:
    return value.encode("utf-16-be", errors="strict")


def _validate_string(value: str) -> None:
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise HandoffError("LONE_SURROGATE", "JSON contains a lone surrogate") from exc


def _number(value: int | float, identity_bearing: bool) -> str:
    if isinstance(value, int):
        return str(value)
    if not math.isfinite(value):
        raise HandoffError("NON_FINITE_NUMBER", "JSON numbers must be finite")
    if value == 0:
        return "0"
    absolute = abs(value)
    if value.is_integer() and absolute < 1e21:
        return str(int(value))
    rendered = json.dumps(value, allow_nan=False, separators=(",", ":"))
    if "e" in rendered.lower() and 1e-6 <= absolute < 1e21:
        rendered = format(Decimal(repr(value)), "f").rstrip("0").rstrip(".")
    rendered = re.sub(r"e([+-])0+(\d+)$", r"e\1\2", rendered)
    return rendered


def _canonical_text(value: Any, identity_bearing: bool) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        _validate_string(value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, (int, float)):
        return _number(value, identity_bearing)
    if isinstance(value, list):
        return "[" + ",".join(_canonical_text(item, identity_bearing) for item in value) + "]"
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise HandoffError("SCHEMA_INVALID", "JSON object keys must be strings")
        keys = sorted(value, key=_utf16_key)
        return "{" + ",".join(
            f"{_canonical_text(key, identity_bearing)}:{_canonical_text(value[key], identity_bearing)}"
            for key in keys
        ) + "}"
    raise HandoffError("SCHEMA_INVALID", f"unsupported JSON value: {type(value).__name__}")


def canonical_json(value: Any, *, identity_bearing: bool = True) -> bytes:
    return _canonical_text(value, identity_bearing).encode("utf-8")


def parse_strict_json(data: bytes, *, identity_bearing: bool = True) -> Any:
    if data.startswith(b"\xef\xbb\xbf"):
        raise HandoffError("BOM_NOT_ALLOWED", "UTF-8 BOM is not allowed")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise HandoffError("NON_UTF8_INPUT", "JSON must be strict UTF-8") from exc

    def reject_duplicate(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise HandoffError("DUPLICATE_KEY", f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(_: str) -> Any:
        raise HandoffError("NON_FINITE_NUMBER", "JSON numbers must be finite")

    try:
        value = json.loads(text, object_pairs_hook=reject_duplicate, parse_constant=reject_constant)
    except HandoffError:
        raise
    except json.JSONDecodeError as exc:
        code = "LONE_SURROGATE" if "surrogate" in text.lower() else "SCHEMA_INVALID"
        raise HandoffError(code, "invalid JSON") from exc
    if identity_bearing:
        _validate_identity_values(value)
    canonical_json(value, identity_bearing=identity_bearing)
    return value


def _validate_identity_values(value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            _validate_identity_values(item)
        return
    if not isinstance(value, dict):
        return
    for key, item in value.items():
        if key == "package_version":
            if isinstance(item, float) and not item.is_integer():
                raise HandoffError("NON_INTEGRAL_IDENTITY_NUMBER", "package_version must be integral")
            if not isinstance(item, int) or isinstance(item, bool) or not 1 <= item <= MAX_SAFE_INTEGER:
                raise HandoffError("PACKAGE_VERSION_OUT_OF_RANGE", "package_version is outside the positive safe range")
        if key == "sha256" or key.endswith("_sha256"):
            _check_sha256(item)
        _validate_identity_values(item)


def _check_sha256(value: str) -> None:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise HandoffError("SHA256_FORMAT_INVALID", "SHA-256 values must be 64 lowercase hex characters")


def _validate_target_binding(value: Any) -> None:
    if value is None:
        return
    required = {
        "branch", "evidence_manifest_sha256", "kind", "repository_identity", "revision", "target_id",
        "verification_state",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise HandoffError("SCHEMA_INVALID", "target_binding does not match the closed contract")
    repository = value.get("repository_identity")
    if not isinstance(repository, dict) or set(repository) != {"registry", "repository_id"}:
        raise HandoffError("SCHEMA_INVALID", "target_binding.repository_identity is invalid")
    for key in ("target_id", "kind", "revision", "verification_state"):
        if not isinstance(value[key], str) or not value[key]:
            raise HandoffError("SCHEMA_INVALID", f"target_binding.{key} is required")
    if value["kind"] not in {"FIXTURE", "GIT"} or value["verification_state"] not in {"DECLARED_UNVERIFIED", "EVIDENCE_BOUND"}:
        raise HandoffError("SCHEMA_INVALID", "target_binding uses an unsupported closed-vocabulary value")
    if value["kind"] == "GIT" and not re.fullmatch(r"[0-9a-f]{40}", value["revision"]):
        raise HandoffError("SCHEMA_INVALID", "GIT target revisions must be 40 lowercase hexadecimal characters")
    if value["branch"] is not None and (not isinstance(value["branch"], str) or not value["branch"]):
        raise HandoffError("SCHEMA_INVALID", "target_binding.branch must be null or a nonempty string")
    if value["evidence_manifest_sha256"] is not None:
        _check_sha256(value["evidence_manifest_sha256"])
    if value["verification_state"] == "EVIDENCE_BOUND" and value["evidence_manifest_sha256"] is None:
        raise HandoffError("SCHEMA_INVALID", "EVIDENCE_BOUND targets require an evidence manifest digest")


def source_snapshot(package_id: str, package_version: int, payloads: dict[str, bytes]) -> dict[str, Any]:
    if not package_id or not isinstance(package_version, int) or not 1 <= package_version <= MAX_SAFE_INTEGER:
        raise HandoffError("PACKAGE_VERSION_OUT_OF_RANGE", "package_version must be a positive safe integer")
    if set(payloads) != set(PAYLOAD_INVENTORY):
        raise HandoffError("MANIFEST_MISMATCH", "source snapshot requires exactly three payloads")
    return {
        "contract_domain": "sdlc.artpkg_source_snapshot",
        "contract_version": "0.1",
        "files": [
            {"file_sha256": sha256_bytes(payloads[path]), "path": path}
            for path in sorted(payloads, key=lambda item: item.encode("utf-8"))
        ],
        "package_id": package_id,
        "package_version": package_version,
    }


def package_sha256(package_id: str, package_version: int, payloads: dict[str, bytes]) -> str:
    return sha256_bytes(canonical_json(source_snapshot(package_id, package_version, payloads)))


def content_set_sha256(files: dict[str, bytes]) -> str:
    expected = {"ARTPKG_HANDOFF.json", *PAYLOAD_INVENTORY}
    if set(files) != expected:
        raise HandoffError("MANIFEST_MISMATCH", "content set requires the handoff and three payloads")
    digest_input = {
        "contract_domain": "pipeline_a.artpkg_content_set",
        "contract_version": "0.1",
        "files": [
            {"file_sha256": sha256_bytes(files[path]), "path": path}
            for path in sorted(files, key=lambda item: item.encode("utf-8"))
        ],
    }
    return sha256_bytes(canonical_json(digest_input))


def completion_summary(document: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    answers = document.get("answers", {})
    unanswered = sorted(
        qid for qid, item in answers.items()
        if item.get("state") in {"UNKNOWN", "TO_BE_INSPECTED"}
        or (item.get("state") not in {"DEFERRED", "NOT_APPLICABLE"} and item.get("value") in {None, ""})
    )
    deferred = sorted(qid for qid, item in answers.items() if item.get("state") == "DEFERRED")
    unreviewed = sorted(
        qid for qid, item in answers.items()
        if item.get("review_disposition") not in {"HUMAN_CONFIRMED", "HUMAN_REJECTED"}
    )
    unreviewed_records = sorted(
        record.get("id", "UNKNOWN")
        for records in document.get("records", {}).values()
        for record in records
        if record.get("review_disposition") != "HUMAN_CONFIRMED"
    )
    blockers = sorted(set(validation.get("blocking_ids", [])))
    errors = list(validation.get("errors", []))
    authority = answers.get("AUT-001", {}).get("value")
    seal_blockers = list(errors)
    if blockers:
        seal_blockers.append("validation has blocking IDs: " + ", ".join(blockers))
    if unanswered:
        seal_blockers.append("required questions remain unanswered: " + ", ".join(unanswered))
    if authority != "NONE":
        seal_blockers.append("implementation_authority must be NONE")
    return {
        "completion_result": "READY_TO_SEAL" if not seal_blockers else "BLOCKED",
        "unanswered_questions": unanswered,
        "explicitly_deferred_questions": deferred,
        "unreviewed_questions": unreviewed,
        "unreviewed_records": unreviewed_records,
        "validation_blockers": blockers,
        "validation_errors": errors,
        "validation_warnings": list(validation.get("warnings", [])),
        "seal_blockers": seal_blockers,
        "implementation_authority": authority,
        "final_attestations": {
            qid: answers.get(qid, {}).get("value") for qid in ("FIN-001", "FIN-002", "FIN-003")
        },
    }


def approved_snapshot(document: dict[str, Any], reviewer: str) -> dict[str, Any]:
    approved = deepcopy(document)
    stable_time = _stable_approval_time(approved)
    approved["updated"] = stable_time
    for item in approved.get("answers", {}).values():
        if item.get("review_disposition") != "HUMAN_REJECTED":
            item["review_disposition"] = "HUMAN_CONFIRMED"
            item["reviewer"] = reviewer
        if item.get("source_type") == "DERIVED_BY_SCRIPT":
            item["timestamp"] = stable_time
            item["last_edit_timestamp"] = stable_time
    for records in approved.get("records", {}).values():
        for record in records:
            if record.get("review_disposition") != "HUMAN_REJECTED":
                record["review_disposition"] = "HUMAN_CONFIRMED"
                record["reviewer"] = reviewer
    return approved


def _stable_approval_time(document: dict[str, Any]) -> str:
    candidates = [document.get("created")]
    candidates.extend(
        value
        for item in document.get("answers", {}).values()
        if item.get("source_type") != "DERIVED_BY_SCRIPT"
        for value in (item.get("timestamp"), item.get("last_edit_timestamp"))
    )
    candidates.extend(
        value
        for records in document.get("records", {}).values()
        for item in records
        for value in (item.get("created"), item.get("last_edit"))
    )
    return max((value for value in candidates if isinstance(value, str) and value), default="")


def render_source_payloads(document: dict[str, Any], validation: dict[str, Any]) -> dict[str, bytes]:
    import artifacts_package_questionnaire as questionnaire

    questionnaire.validate_document_shape(document)
    rendered_document = deepcopy(document)
    template_path = Path(rendered_document["setup"]["template_path"]).expanduser().resolve()
    rendered_document["template_version"] = questionnaire.template_digest(str(template_path))
    answers = canonical_json(rendered_document)
    package = questionnaire.render_package(rendered_document, str(template_path), validation).encode("utf-8")
    lines = [
        "# Artifacts Package Validation", "", f"- Status: `{validation.get('status', 'BLOCKED')}`",
        "- Sealing compatibility: `PASS`", "", "## Errors",
        *([f"- {error}" for error in validation.get("errors", [])] or ["- None"]), "", "## Warnings",
        *([f"- {warning}" for warning in validation.get("warnings", [])] or ["- None"]), "",
        "## Blocking IDs", "", f"`{', '.join(validation.get('blocking_ids', [])) or 'NONE'}`", "",
        "## Authority", "", "`implementation_authority: NONE`", "",
        "## Next permitted action", "", "`SUBMIT_FOR_SDLC_ASSESSMENT`", "",
    ]
    payloads = {
        "artifacts_package.md": package,
        "artifacts_package_answers.json": answers,
        "artifacts_package_validation.md": "\n".join(lines).encode("utf-8"),
    }
    _validate_inventory({
        "ARTPKG_HANDOFF.json": b"{}", "MANIFEST.json": b"{}", "SHA256SUMS": b"", **payloads,
    })
    return payloads


def _payload_signature(payloads: dict[str, bytes]) -> list[dict[str, str]]:
    return [
        {"file_sha256": sha256_bytes(payloads[path]), "path": path}
        for path in sorted(payloads, key=lambda item: item.encode("utf-8"))
    ]


def _existing_handoffs(session_dir: Path) -> list[dict[str, Any]]:
    history = session_dir / "sealed_packages"
    if not history.exists():
        return []
    handoffs = []
    for sealed_dir in sorted(history.iterdir()):
        if sealed_dir.is_symlink() or not sealed_dir.is_dir() or not _SHA256_RE.fullmatch(sealed_dir.name):
            continue
        files = load_sealed_files(session_dir, sealed_dir.name)
        handoff = parse_strict_json(files["ARTPKG_HANDOFF.json"])
        validate_handoff(handoff)
        handoffs.append(handoff)
    return handoffs


def select_identity(
    session_dir: str | Path,
    package_id: str,
    payloads: dict[str, bytes],
    target_binding: Any,
    *, trusted_history: list[dict[str, Any]] | None = None,
) -> tuple[int, str, str, dict[str, Any] | None]:
    _validate_target_binding(target_binding)
    existing = _existing_handoffs(Path(session_dir).resolve()) if trusted_history is None else trusted_history
    signature = _payload_signature(payloads)
    for handoff in existing:
        if (
            handoff["package"]["package_id"] == package_id
            and handoff["source_snapshot_digest_input"]["files"] == signature
            and handoff["target_binding"] == target_binding
        ):
            package = handoff["package"]
            return package["package_version"], handoff["submission_id"], package["package_sha256"], handoff
    versions = [
        item["package"]["package_version"] for item in existing
        if item["package"]["package_id"] == package_id
    ]
    version = max(versions, default=0) + 1
    digest = package_sha256(package_id, version, payloads)
    submission_input = {"package_sha256": digest, "target_binding": target_binding}
    submission_id = "SUB-" + sha256_bytes(canonical_json(submission_input))[:20].upper()
    return version, submission_id, digest, None


def build_handoff(
    session: dict[str, Any],
    reviewer: str,
    target_binding: Any = None,
    *, trusted_history: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, bytes], dict[str, Any]]:
    document = session["document"]
    validation = session["validation"]
    summary = completion_summary(document, validation)
    if summary["seal_blockers"]:
        raise HandoffError("SEALING_BLOCKED", "; ".join(summary["seal_blockers"]))
    if _count_records(document) > MAX_RECORDS:
        raise HandoffError("LIMIT_EXCEEDED", "structured record limit exceeded")
    sealed_document = approved_snapshot(document, reviewer)
    payloads = render_source_payloads(sealed_document, validation)
    package_id = str(document.get("package_id") or "").strip()
    if not package_id:
        raise HandoffError("SCHEMA_INVALID", "the answer document does not contain package_id")
    version, submission_id, digest, existing = select_identity(
        session["session_dir"], package_id, payloads, target_binding, trusted_history=trusted_history,
    )
    if existing is not None:
        files, content_digest = assemble_files(existing, payloads)
        return existing, files, {**summary, "content_set_sha256": content_digest}
    authority_answer = document["answers"]["AUT-001"]
    approver_answer = document["answers"].get("AUT-009", {})
    completed_at = _completion_time(document)
    if not completed_at:
        raise HandoffError("SCHEMA_INVALID", "a deterministic completion timestamp is required")
    snapshot = source_snapshot(package_id, version, payloads)
    handoff = {
        "authority_state": {
            "approval_reference": authority_answer.get("source_reference") or "ArtPkg intake UI confirmation",
            "approver_role": approver_answer.get("value") or "ARTPKG_REVIEWER",
            "approver_subject_id": reviewer,
            "decided_at": completed_at,
            "decision_scope": "Submit this exact snapshot for plan-only SDLC assessment",
            "implementation_authority": "NONE",
            "state": "HUMAN_APPROVED_FOR_SDLC_ASSESSMENT",
        },
        "compatibility_validation": {
            "generator_semantic_validation": "PASS", "generator_shape_validation": "PASS",
            "legacy_registered_schema": "PASS", "plan_only_compatibility_schema": "PASS",
            "submission_readiness": "PASS",
        },
        "completed_at": completed_at,
        "completion_state": "PACKAGE_COMPLETE",
        "contract_domain": "sdlc.artpkg_handoff",
        "contract_version": "0.1",
        "implementation_authority": "NONE",
        "lineage": None,
        "package": {"package_id": package_id, "package_sha256": digest, "package_version": version},
        "payloads": [
            {"path": "artifacts_package_answers.json", "required": True, "source_classification": "HUMAN_APPROVED_ARTPKG"},
            {"path": "artifacts_package.md", "required": True, "source_classification": "TOOL_EXTRACTED"},
            {"path": "artifacts_package_validation.md", "required": True, "source_classification": "TOOL_EXTRACTED"},
        ],
        "producer": {"repository": "ArtPkgPro", "revision": "648bcf3f3dc40b138a08b9388808e5fb89a72ae2", "system": "ArtPkg"},
        "profile": "ARTPKG_V0_2_PLAN_ONLY",
        "requested_mode": "PLAN_ONLY",
        "source_contract": {
            "compatibility_schema_id": "sdlc.artpkg_answers_v0_2_plan_only_compat.v0.1",
            "legacy_schema_id": "artifacts_package_answers_v0.2.schema.json",
            "questionnaire_version": str(document.get("questionnaire_version", "0.1")),
            "schema_version": str(document.get("schema_version", "0.2")),
        },
        "source_snapshot_digest_input": snapshot,
        "submission_id": submission_id,
        "target_binding": target_binding,
        "unresolved_question_dispositions": [],
    }
    if version > 1:
        history = _existing_handoffs(Path(session["session_dir"])) if trusted_history is None else trusted_history
        parent = next(
            (item for item in history if item["package"]["package_id"] == package_id and item["package"]["package_version"] == version - 1),
            None,
        )
        if parent is None:
            raise HandoffError("IDENTITY_MISMATCH", "the prior sealed package version is missing")
        handoff["lineage"] = {
            "kind": "PACKAGE_REVISION",
            "parent_package_id": parent["package"]["package_id"],
            "parent_package_sha256": parent["package"]["package_sha256"],
            "parent_package_version": parent["package"]["package_version"],
        }
    for qid in summary["explicitly_deferred_questions"]:
        answer = document["answers"][qid]
        handoff["unresolved_question_dispositions"].append({
            "disposition": "DEFER_TO_CHECKPOINT",
            "human_confirmation_state": "HUMAN_CONFIRMED",
            "materiality": "ADVISORY",
            "next_review_checkpoint": "HUMAN_REVIEW_REQUIRED",
            "provenance": {
                "source_classification": "HUMAN_APPROVED_ARTPKG",
                "source_reference": answer.get("source_reference") or "ArtPkg intake UI",
            },
            "question_id": qid,
            "reason_code": "OPTIONAL_DETAIL_PENDING",
        })
    files, content_digest = assemble_files(handoff, payloads)
    return handoff, files, {**summary, "content_set_sha256": content_digest}


def review_package(session: dict[str, Any], reviewer: str, target_binding: Any = None) -> dict[str, Any]:
    summary = completion_summary(session["document"], session["validation"])
    result = {**summary, "target_binding": target_binding, "source_classification": "HUMAN_APPROVED_ARTPKG"}
    if summary["seal_blockers"]:
        return result
    handoff, files, enriched = build_handoff(session, reviewer, target_binding)
    sealed_id = sha256_bytes(files["MANIFEST.json"])
    sealed = (Path(session["session_dir"]) / "sealed_packages" / sealed_id).is_dir()
    return {
        **result, **enriched,
        "package_id": handoff["package"]["package_id"],
        "package_version": handoff["package"]["package_version"],
        "submission_id": handoff["submission_id"],
        "package_sha256": handoff["package"]["package_sha256"],
        "inventory": list(ROOT_INVENTORY),
        "confirmation_text": CONFIRMATION_TEXT,
        "pipeline_submission_configured": False,
        "sealed": sealed,
        "sealed_id": sealed_id,
    }


def seal_session(
    session: dict[str, Any], reviewer: str, confirmation: str, reviewed: bool, target_binding: Any = None,
) -> tuple[SealResult, dict[str, bytes]]:
    if not reviewed or confirmation != CONFIRMATION_TEXT:
        raise HandoffError("CONFIRMATION_REQUIRED", "the exact sealing summary and confirmation must be reviewed")
    import artpkg_source_commitment as commitment
    store = commitment.Store(session["session_dir"])
    with store.locked(create=True) as ledger:
        # Never promote existing package envelopes into independent trust. Identity
        # replay and lineage use only prior successful authenticated sealing calls.
        history = [entry["handoff"] for entry in ledger["seals"].values()]
        handoff, files, summary = build_handoff(session, reviewer, target_binding, trusted_history=history)
        package = handoff["package"]
        preliminary = SealResult(
            sealed_dir=Path(), package_id=package["package_id"], package_version=package["package_version"],
            submission_id=handoff["submission_id"], package_sha256=package["package_sha256"],
            content_set_sha256=summary["content_set_sha256"],
        )
        commitment.safe(Path(session["session_dir"]) / "sealed_packages")
        sealed_dir = seal_to_history(session["session_dir"], files, preliminary)
        store.commit(ledger, handoff, files, reviewer)
    return SealResult(**{**preliminary.__dict__, "sealed_dir": sealed_dir}), files


def _count_records(document: dict[str, Any]) -> int:
    return sum(len(records) for records in document.get("records", {}).values() if isinstance(records, list))


def _completion_time(document: dict[str, Any]) -> str:
    candidates = [document.get("created"), document.get("updated")]
    candidates.extend(
        value
        for item in document.get("answers", {}).values()
        for value in (item.get("timestamp"), item.get("last_edit_timestamp"))
    )
    candidates.extend(
        value
        for records in document.get("records", {}).values()
        for item in records
        for value in (item.get("created"), item.get("last_edit"))
    )
    return max((value for value in candidates if isinstance(value, str) and value), default="")


def validate_handoff(handoff: dict[str, Any]) -> None:
    required = {
        "authority_state", "compatibility_validation", "completed_at", "completion_state",
        "contract_domain", "contract_version", "implementation_authority", "lineage", "package",
        "payloads", "producer", "profile", "requested_mode", "source_contract",
        "source_snapshot_digest_input", "submission_id", "target_binding", "unresolved_question_dispositions",
    }
    if set(handoff) != required or PROHIBITED_HANDOFF_FIELDS.intersection(handoff):
        raise HandoffError("SCHEMA_INVALID", "ARTPKG_HANDOFF.json root schema is closed")
    if not isinstance(handoff["submission_id"], str) or not 1 <= len(handoff["submission_id"]) <= 200:
        raise HandoffError("SCHEMA_INVALID", "submission_id is required and must contain 1-200 characters")
    if handoff["implementation_authority"] != "NONE" or handoff["authority_state"].get("implementation_authority") != "NONE":
        raise HandoffError("AUTHORITY_CONTRADICTION", "implementation_authority must be NONE")
    if handoff["completion_state"] != "PACKAGE_COMPLETE":
        raise HandoffError("IDENTITY_MISMATCH", "only complete packages may be sealed")
    _validate_target_binding(handoff["target_binding"])
    package = handoff["package"]
    if not isinstance(package, dict) or set(package) != {"package_id", "package_sha256", "package_version"}:
        raise HandoffError("SCHEMA_INVALID", "package identity is invalid")
    if not re.fullmatch(r"PKG-[A-F0-9]{12}", package["package_id"]):
        raise HandoffError("SCHEMA_INVALID", "package_id does not match the ArtPkg contract")
    _check_sha256(package["package_sha256"])
    lineage = handoff["lineage"]
    if package["package_version"] == 1 and lineage is not None:
        raise HandoffError("IDENTITY_MISMATCH", "package version 1 must not have lineage")
    if package["package_version"] > 1:
        expected_lineage = {"kind", "parent_package_id", "parent_package_sha256", "parent_package_version"}
        if not isinstance(lineage, dict) or set(lineage) != expected_lineage or lineage.get("kind") != "PACKAGE_REVISION":
            raise HandoffError("SCHEMA_INVALID", "package revisions require closed parent lineage")
        _check_sha256(lineage["parent_package_sha256"])
    for disposition in handoff["unresolved_question_dispositions"]:
        required_disposition = {
            "disposition", "human_confirmation_state", "materiality", "next_review_checkpoint", "provenance",
            "question_id", "reason_code",
        }
        if not isinstance(disposition, dict) or set(disposition) != required_disposition:
            raise HandoffError("SCHEMA_INVALID", "unresolved question disposition is not closed")
        if disposition["materiality"] != "ADVISORY" or disposition["human_confirmation_state"] != "HUMAN_CONFIRMED":
            raise HandoffError("IDENTITY_MISMATCH", "blocking or unconfirmed deferrals cannot be sealed")


def _manifest_entry(path: str, data: bytes, classification: str) -> dict[str, Any]:
    if classification not in SOURCE_CLASSIFICATIONS:
        raise HandoffError("SCHEMA_INVALID", "invalid source classification")
    entry: dict[str, Any] = {
        "exact_byte_sha256": sha256_bytes(data),
        "media_type": "application/json" if path.endswith(".json") else "text/markdown; charset=utf-8",
        "path": path,
        "required": True,
        "size_bytes": len(data),
        "source_classification": classification,
    }
    if path.endswith(".json"):
        parsed = parse_strict_json(data)
        entry["semantic_digest"] = {"algorithm": "SHA256", "value": sha256_bytes(canonical_json(parsed))}
    return entry


def assemble_files(handoff: dict[str, Any], payloads: dict[str, bytes]) -> tuple[dict[str, bytes], str]:
    validate_handoff(handoff)
    if _count_records(parse_strict_json(payloads["artifacts_package_answers.json"])) > MAX_RECORDS:
        raise HandoffError("LIMIT_EXCEEDED", "structured record limit exceeded")
    handoff_bytes = canonical_json(handoff)
    content_files = {"ARTPKG_HANDOFF.json": handoff_bytes, **payloads}
    classifications = {
        "ARTPKG_HANDOFF.json": "TOOL_EXTRACTED",
        "artifacts_package.md": "TOOL_EXTRACTED",
        "artifacts_package_answers.json": "HUMAN_APPROVED_ARTPKG",
        "artifacts_package_validation.md": "TOOL_EXTRACTED",
    }
    manifest = {
        "contract_domain": "sdlc.artpkg_manifest",
        "contract_version": "0.1",
        "entries": [
            _manifest_entry(path, content_files[path], classifications[path])
            for path in sorted(content_files, key=lambda item: item.encode("utf-8"))
        ],
        "package": handoff["package"],
        "profile": handoff["profile"],
    }
    manifest_bytes = canonical_json(manifest)
    checksummed = {**content_files, "MANIFEST.json": manifest_bytes}
    sums = "".join(
        f"{sha256_bytes(checksummed[path])}  {path}\n"
        for path in sorted(checksummed, key=lambda item: item.encode("utf-8"))
    ).encode("ascii")
    files = {**checksummed, "SHA256SUMS": sums}
    _validate_inventory(files)
    return files, content_set_sha256(content_files)


def _validate_inventory(files: dict[str, bytes]) -> None:
    if tuple(sorted(files, key=lambda item: item.encode("utf-8"))) != tuple(sorted(ROOT_INVENTORY, key=lambda item: item.encode("utf-8"))):
        raise HandoffError("UNDECLARED_FILE", "sealed root must contain exactly the six contract files")
    if len(files) > MAX_FILES or sum(map(len, files.values())) > MAX_TOTAL_BYTES:
        raise HandoffError("LIMIT_EXCEEDED", "sealed package exceeds aggregate limits")
    normalized: set[str] = set()
    for path, data in files.items():
        if len(path.encode("utf-8")) > MAX_PATH_BYTES or len(Path(path).parts) > MAX_DEPTH:
            raise HandoffError("UNSAFE_PATH", "sealed path exceeds contract limits")
        if Path(path).name != path or path in {".", ".."}:
            raise HandoffError("UNSAFE_PATH", "sealed root paths must be plain filenames")
        nfc = unicodedata.normalize("NFC", path)
        if nfc in normalized:
            raise HandoffError("UNSAFE_PATH", "sealed paths are not NFC-unique")
        normalized.add(nfc)
        if len(data) > MAX_FILE_BYTES or (path.endswith((".json", ".md")) and len(data) > MAX_PARSED_BYTES):
            raise HandoffError("LIMIT_EXCEEDED", f"{path} exceeds the file limit")
        if path.endswith((".json", ".md")):
            try:
                data.decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                raise HandoffError("NON_UTF8_INPUT", f"{path} is not UTF-8") from exc


def seal_to_history(session_dir: str | Path, files: dict[str, bytes], result: SealResult | None = None) -> Path:
    _validate_inventory(files)
    root = Path(session_dir).resolve() / "sealed_packages"
    identity = sha256_bytes(files["MANIFEST.json"])
    destination = root / identity
    if destination.exists():
        existing = load_sealed_files(Path(session_dir).resolve(), identity)
        for name, data in files.items():
            if existing[name] != data:
                raise HandoffError("IDENTITY_MISMATCH", "existing sealed package bytes differ")
        return destination
    root.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".sealing-", dir=root))
    try:
        for name, data in files.items():
            path = temporary / name
            with path.open("xb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
                path.chmod(0o444)
        os.replace(temporary, destination)
        destination.chmod(0o555)
    finally:
        if temporary.exists():
            for child in temporary.iterdir():
                child.unlink()
            temporary.rmdir()
    return destination


def load_sealed_files(session_dir: str | Path, sealed_id: str) -> dict[str, bytes]:
    if not _SHA256_RE.fullmatch(sealed_id):
        raise HandoffError("UNSAFE_PATH", "invalid sealed package identity")
    history = Path(session_dir).resolve() / "sealed_packages"
    sealed_dir = history / sealed_id
    if sealed_dir.is_symlink() or not sealed_dir.is_dir():
        raise HandoffError("UNSAFE_PATH", "sealed package is missing or is not a regular directory")
    children = list(sealed_dir.iterdir())
    if {path.name for path in children} != set(ROOT_INVENTORY):
        raise HandoffError("UNDECLARED_FILE", "sealed package inventory has changed")
    files: dict[str, bytes] = {}
    for path in children:
        if path.is_symlink() or not path.is_file():
            raise HandoffError("UNSAFE_PATH", "sealed package contains a link or non-regular file")
        files[path.name] = path.read_bytes()
    _validate_inventory(files)
    return files


def deterministic_zip(files: dict[str, bytes]) -> bytes:
    _validate_inventory(files)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
        for name in sorted(files, key=lambda item: item.encode("utf-8")):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    output.seek(0)
    return output.read()