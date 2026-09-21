#!/usr/bin/env python3
"""Derive per-item human-approval status from a sealed ArtPkg package.

A peer of the Pipeline-A admission and DSH bridge handoffs, not a mutation
of the sealed six-file contract: this reads an already-sealed package in
place by absolute path, verifies its identity against a caller-supplied
digest, and emits its own output bound to that identity. It never copies,
repackages, or extends the sealed bundle.

Exists because ArtPkg's own approval signals are coarser than they look:

- `source_classification` in ARTPKG_HANDOFF.json / MANIFEST.json is applied
  per FILE ("this whole answers.json is HUMAN_APPROVED_ARTPKG"), not per
  requirement.
- `review_disposition` inside artifacts_package_answers.json looks per-item,
  but ArtPkg's own approved_snapshot() (tools/artpkg_sealed_handoff.py)
  stamps it to HUMAN_CONFIRMED on every answer and record that is not
  already HUMAN_REJECTED at the moment of sealing, regardless of whether
  that specific item was individually reviewed. It is not usable as a
  confirmation signal from outside ArtPkg.

The only fields approved_snapshot() does not overwrite are each answer's
pre-seal `state`/`source_type` and each record's own `fields.status` (or
`fields.residual_status` for risks) -- this module derives human confirmation
from those instead.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
import artpkg_sealed_handoff as sealed  # noqa: E402

CONTRACT_DOMAIN = "artpkg.requirement_approval_derivation"
CONTRACT_VERSION = "0.1"
SUPPORTED_SCHEMA_VERSIONS = {"0.1", "0.2"}

# category -> (field name inside record["fields"], values meaning "still at
# its initial/unconfirmed state"). Sourced directly from RECORD_TYPES in
# artifacts_package_questionnaire.py -- not guessed. Categories whose status
# field does not represent approval progress (e.g. "artifacts", which
# describes reference freshness) are deliberately absent, not mapped.
RECORD_STATUS_FIELDS: dict[str, tuple[str, frozenset[str]]] = {
    "functional_requirements": ("status", frozenset({"PROPOSED"})),
    "non_functional_requirements": ("status", frozenset({"PROPOSED"})),
    "acceptance_criteria": ("status", frozenset({"PROPOSED"})),
    "decisions": ("status", frozenset({"PROPOSED"})),
    "assumptions": ("status", frozenset({"OPEN"})),
    "conflicts": ("status", frozenset({"OPEN"})),
    "risks": ("residual_status", frozenset({"OPEN"})),
    "phases": ("status", frozenset({"PROPOSED"})),
}

ANSWER_CONFIRMED_STATE = "PROVIDED"
ANSWER_CONFIRMED_SOURCE_TYPE = "HUMAN_DECLARATION"
ANSWER_AMBIGUOUS_STATES = frozenset({"UNKNOWN", "TO_BE_INSPECTED"})

CAVEATS = (
    "review_disposition is not used as the confirmation signal: ArtPkg's "
    "approved_snapshot() stamps review_disposition=HUMAN_CONFIRMED onto every "
    "answer and record that is not already HUMAN_REJECTED at seal time, "
    "regardless of whether that item was individually reviewed beforehand. "
    "Confirmation here is derived from the pre-seal provenance fields "
    "(answer state/source_type, record status) that approved_snapshot() "
    "does not overwrite.",
    "Record categories with no known approval-shaped status field report "
    "human_confirmed=null with basis=record_status_unmodeled, rather than a "
    "guessed value.",
    "Answers in state NOT_APPLICABLE report human_confirmed=null with "
    "basis=not_applicable: conditional-suppression logic (e.g. a follow-up "
    "question suppressed because its trigger answer was NO) legitimately "
    "produces these, and it is not an approval gap.",
    "Answers in state DEFERRED report human_confirmed=null with "
    "basis=deferred -- deliberately NOT the same basis as not_applicable. "
    "A deferred decision is unresolved, not inapplicable; a consumer that "
    "silently excludes deferred items the same way it excludes "
    "not-applicable ones can produce an apparently-complete package that "
    "is missing a decision it actually needs. Callers must treat "
    "basis=deferred as a blocking condition when the item affects required "
    "scope, never as safe-to-drop.",
    "Answers in state UNKNOWN or TO_BE_INSPECTED report human_confirmed=false "
    "with basis=unknown_or_ambiguous, distinct from an ordinary unconfirmed "
    "answer, so a caller can choose to block pending resolution rather than "
    "treat it as routinely unapproved.",
    "This module derives a raw per-item signal only. It does not decide "
    "whether an unconfirmed/deferred/ambiguous item is actually needed for "
    "the intended scope; that judgment (and any resulting block on package "
    "preparation) belongs to a higher-level preparation stage that also "
    "reads scope-boundary answers (e.g. BND-001/BND-002) and produces a "
    "durable inclusion/exclusion accounting -- this module is a building "
    "block for that, not a replacement for it.",
    "schema_version 0.3 (tools/artpkg_v03.py's requirement_intake shape) is "
    "not wired into any producer in this repository today and is not "
    "supported by this derivation.",
)


class ApprovalDerivationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _load_sealed_files(package_dir: Path) -> dict[str, bytes]:
    if package_dir.is_symlink() or not package_dir.is_dir():
        raise ApprovalDerivationError("UNSAFE_PATH", "package directory is missing or not a regular directory")
    children = list(package_dir.iterdir())
    if {child.name for child in children} != set(sealed.ROOT_INVENTORY):
        raise ApprovalDerivationError("UNDECLARED_FILE", "sealed package inventory has changed")
    files: dict[str, bytes] = {}
    for child in children:
        if child.is_symlink() or not child.is_file():
            raise ApprovalDerivationError("UNSAFE_PATH", "sealed package contains a link or non-regular file")
        files[child.name] = child.read_bytes()
    try:
        sealed._validate_inventory(files)  # reuse ArtPkg's own hardening rather than re-derive it
    except sealed.HandoffError as exc:
        raise ApprovalDerivationError(exc.code, str(exc)) from exc
    return files


def _verify_checksums(files: dict[str, bytes]) -> None:
    lines = files["SHA256SUMS"].decode("utf-8", errors="strict").splitlines()
    recorded = dict(line.split("  ", 1)[::-1] for line in lines if line)
    if set(recorded) != set(files) - {"SHA256SUMS"}:
        raise ApprovalDerivationError("MANIFEST_MISMATCH", "SHA256SUMS does not list exactly the other sealed files")
    for name, digest in recorded.items():
        if sealed.sha256_bytes(files[name]) != digest:
            raise ApprovalDerivationError("MANIFEST_MISMATCH", f"{name} does not match its recorded SHA-256")


def _verify_identity(files: dict[str, bytes], expected_package_sha256: str) -> dict[str, Any]:
    try:
        handoff = sealed.parse_strict_json(files["ARTPKG_HANDOFF.json"])
        sealed.validate_handoff(handoff)
    except sealed.HandoffError as exc:
        raise ApprovalDerivationError(exc.code, str(exc)) from exc
    _verify_checksums(files)
    payloads = {name: files[name] for name in sealed.PAYLOAD_INVENTORY}
    package = handoff["package"]
    recomputed = sealed.package_sha256(package["package_id"], package["package_version"], payloads)
    if recomputed != package["package_sha256"]:
        raise ApprovalDerivationError("IDENTITY_MISMATCH", "sealed payloads do not match the handoff's recorded package_sha256")
    if package["package_sha256"] != expected_package_sha256:
        raise ApprovalDerivationError("IDENTITY_MISMATCH", "sealed package does not match --expected-package-sha256")
    return handoff


def _derive_answer(question_id: str, item: dict[str, Any]) -> dict[str, Any]:
    state = item.get("state")
    source_type = item.get("source_type")
    base = {"id": question_id, "kind": "answer", "state": state, "source_type": source_type}
    if state == "NOT_APPLICABLE":
        # Conditionally suppressed by ArtPkg's own logic (e.g. a follow-up
        # question whose trigger answer was NO). Safe to exclude outright --
        # not a gap, and must not be conflated with DEFERRED below.
        return {**base, "basis": "not_applicable", "human_confirmed": None}
    if state == "DEFERRED":
        # A human explicitly deferred this decision. Unlike NOT_APPLICABLE,
        # this is NOT safe to silently exclude: if the deferred item affects
        # required scope, a downstream consumer must block on it, not drop
        # it. Never merge this basis with "not_applicable".
        return {**base, "basis": "deferred", "human_confirmed": None}
    if state in ANSWER_AMBIGUOUS_STATES:
        # UNKNOWN / TO_BE_INSPECTED: genuinely unresolved, not a considered
        # non-applicability. Reported as unconfirmed, but tagged separately
        # so a consumer can block pending resolution rather than treat it
        # the same as an ordinary unconfirmed/seeded answer.
        return {**base, "basis": "unknown_or_ambiguous", "human_confirmed": False}
    confirmed = state == ANSWER_CONFIRMED_STATE and source_type == ANSWER_CONFIRMED_SOURCE_TYPE
    return {**base, "basis": "questionnaire_state_source_type", "human_confirmed": confirmed}


def _derive_record(category: str, record: dict[str, Any]) -> dict[str, Any]:
    record_id = record.get("id", "UNKNOWN")
    source_type = record.get("source_type")
    field_spec = RECORD_STATUS_FIELDS.get(category)
    if field_spec is None:
        return {
            "id": record_id, "kind": "record", "category": category,
            "basis": "record_status_unmodeled", "human_confirmed": None,
            "source_type": source_type,
        }
    field_name, unconfirmed_values = field_spec
    status = record.get("fields", {}).get(field_name)
    confirmed = status is not None and status not in unconfirmed_values
    return {
        "id": record_id, "kind": "record", "category": category,
        "basis": "record_status", "human_confirmed": confirmed,
        "status_field": field_name, "status": status, "source_type": source_type,
    }


def derive(document: dict[str, Any]) -> list[dict[str, Any]]:
    schema_version = str(document.get("schema_version", ""))
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ApprovalDerivationError(
            "UNSUPPORTED_SCHEMA_VARIANT",
            f"schema_version {schema_version!r} is not a wired production shape",
        )
    records = [_derive_answer(qid, item) for qid, item in sorted(document.get("answers", {}).items())]
    for category, items in sorted(document.get("records", {}).items()):
        for record in items:
            records.append(_derive_record(category, record))
    return records


def run(package_dir: Path, expected_package_sha256: str) -> dict[str, Any]:
    files = _load_sealed_files(package_dir)
    handoff = _verify_identity(files, expected_package_sha256)
    document = sealed.parse_strict_json(files["artifacts_package_answers.json"])
    records = derive(document)
    return {
        "contract_domain": CONTRACT_DOMAIN,
        "contract_version": CONTRACT_VERSION,
        "derived_from": {
            "package_id": handoff["package"]["package_id"],
            "package_version": handoff["package"]["package_version"],
            "package_sha256": handoff["package"]["package_sha256"],
            "sealed_package_path": str(package_dir.resolve()),
        },
        "schema_variant": f"questionnaire_v{document.get('schema_version')}",
        "caveats": list(CAVEATS),
        "records": records,
        "records_sha256": sealed.sha256_bytes(sealed.canonical_json(records)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Derive per-item human-approval status from a sealed ArtPkg package.")
    parser.add_argument("--package", required=True, type=Path, help="path to the sealed six-file package directory")
    parser.add_argument("--expected-package-sha256", required=True, help="package_sha256 the caller expects this package to have")
    parser.add_argument("--output", type=Path, default=None, help="write JSON here instead of stdout")
    args = parser.parse_args(argv)
    try:
        result = run(args.package, args.expected_package_sha256)
    except ApprovalDerivationError as exc:
        print(json.dumps({"error_code": exc.code, "error": str(exc)}), file=sys.stderr)
        return 1
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
