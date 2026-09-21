"""Same-host UX preparation coordinator. No Pipeline/SDLC or UX-approval calls.

Trusted caller: the authenticated owner-checked IntakeHandler under its session
lock (or an equivalent trusted in-process application). This is NOT a public
Python approval API for agents. OS control of application code/private stores is
the trust boundary. Upload contents and browser-supplied hashes are never trusted.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import uuid
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlencode

import artpkg_sealed_handoff as sealed
import artpkg_requirement_approval as derivation
import artifacts_package_questionnaire as questionnaire

ATTESTATION = "I reviewed this exact source, selection, exclusions and capability catalog. This is not UX approval."
UXPKG_ROOT = Path(os.environ.get("ARTPKG_UXPKG_ROOT", "/home/rootux/UXPkg"))
ACTIVE = {
    "functional_requirements": {"ACCEPTED", "IMPLEMENTED", "VERIFIED"},
    "non_functional_requirements": {"ACCEPTED", "IMPLEMENTED", "VERIFIED"},
    "acceptance_criteria": {"ACCEPTED", "PASSED"}, "decisions": {"ACCEPTED"},
    "assumptions": {"VALIDATED"}, "conflicts": {"RESOLVED"},
    "risks": {"ACCEPTED", "MITIGATED"}, "phases": {"ACCEPTED", "IN_PROGRESS", "REVIEW"},
}
TYPES = {"functional_requirements": "FUNCTIONAL", "non_functional_requirements": "NON_FUNCTIONAL", "decisions": "CONSTRAINT"}
TEXT_FIELDS = {"functional_requirements": "requirement", "non_functional_requirements": "requirement",
               "acceptance_criteria": "pass_condition", "decisions": "decision", "assumptions": "assumption",
               "conflicts": "conflict", "risks": "risk", "phases": "title_and_outcome", "constraints": "constraint"}

RESOLUTION_QUESTIONS = (
    {"id": "UXR-001", "title": "Interface", "scope": "SOURCE_AFFECTING",
     "prompt": "Which interface is required for this product?",
     "choices": {"DESKTOP_GUI": "Desktop graphical application", "COMMAND_LINE": "Command-line application"}},
    {"id": "UXR-002", "title": "Controls", "scope": "SOURCE_AFFECTING",
     "prompt": "Which first-version calculator controls are required?",
     "choices": {"BASIC_DECIMAL": "Digits 0-9, decimal, four operators, equals, clear and backspace",
                 "BASIC_INTEGER": "Digits 0-9, four operators, equals, clear and backspace"}},
    {"id": "UXR-003", "title": "Numeric and display behavior", "scope": "SOURCE_AFFECTING",
     "prompt": "Which numeric/display rule should the requirements adopt?",
     "choices": {"DECIMAL_12_HALF_EVEN": "Decimal arithmetic; 12 significant display digits; half-even rounding",
                 "PLATFORM_FLOAT": "Platform floating-point behavior with explicit display-length tests"}},
    {"id": "UXR-004", "title": "Errors and recovery", "scope": "SOURCE_AFFECTING",
     "prompt": "How should invalid operations recover?",
     "choices": {"VISIBLE_RECOVERABLE": "Show a visible error; clear or the next numeric entry returns to a usable state",
                 "CLEAR_REQUIRED": "Show a visible error and require Clear before further input"}},
    {"id": "UXR-005", "title": "Viewport and layout", "scope": "PREPARATION_ONLY",
     "prompt": "Which initial wireframe layout should be proposed?",
     "choices": {"COMPACT_360X520": "360 x 520 fixed desktop window; display above a four-column keypad",
                 "RESPONSIVE_480X640": "480 x 640 initial window; display above a responsive four-column keypad"}},
    {"id": "UXR-006", "title": "Accessibility and keyboard", "scope": "SOURCE_AFFECTING",
     "prompt": "Which accessibility baseline is required?",
     "choices": {"KEYBOARD_BASELINE": "Keyboard digits/operators/Enter/Escape/Backspace, visible focus, labels and WCAG AA contrast",
                 "POINTER_ONLY": "Pointer operation with labels and WCAG AA contrast; keyboard behavior deferred"}},
)
RESOLUTION_BY_ID = {item["id"]: item for item in RESOLUTION_QUESTIONS}


def resolution_status(document):
    answers = document.get("answers", {})
    values, undecided = {}, []
    for question in RESOLUTION_QUESTIONS:
        answer = answers.get(question["id"], {})
        value = answer.get("value") if answer.get("state") == "PROVIDED" else None
        values[question["id"]] = value
        if not value:
            undecided.append(question["id"])
    return {"version": "0.1", "complete": not undecided, "undecided": undecided, "answers": values,
            "authority": "HUMAN_DECLARATION_NOT_UX_APPROVAL"}


def _resolution_value(question, decision):
    if not isinstance(decision, dict) or set(decision) != {"choice", "other"}:
        raise ValueError("each UX resolution needs exactly choice and other")
    choice, other = decision["choice"], decision["other"]
    if not isinstance(choice, str) or not isinstance(other, str):
        raise ValueError("UX resolution values must be strings")
    other = other.strip()
    if choice == "UNDECIDED":
        if other:
            raise ValueError("undecided UX resolution cannot include other text")
        return "UNDECIDED", "UNKNOWN"
    if choice == "OTHER":
        if not other or len(other) > 500:
            raise ValueError("Other UX resolution requires 1-500 characters")
        return "OTHER: " + other, "PROVIDED"
    if choice not in question["choices"] or other:
        raise ValueError("unsupported UX resolution choice")
    return choice + ": " + question["choices"][choice], "PROVIDED"


def runtime(root=UXPKG_ROOT):
    # This path is administrator configuration, never a request field. Lazy import
    # keeps existing ArtPkg operations available when UXPkg is not installed.
    root = Path(root)
    if not root.is_absolute() or not (root / "src/ux_harness/preparation.py").is_file():
        raise ValueError("UXPkg preparation installation unavailable")
    module_path = str(root / "src")
    if module_path not in sys.path:
        sys.path.insert(0, module_path)
    from ux_harness import preparation
    return preparation


def digest(value):
    return sealed.sha256_bytes(sealed.canonical_json(value))


def source_items(document):
    """Enumerate ALL items; unlike raw derivation, use positive active allowlists."""
    if document.get("schema_version") not in {"0.1", "0.2"}:
        raise ValueError("unsupported ArtPkg source schema")
    result = []
    answers, records = document.get("answers"), document.get("records")
    if not isinstance(answers, dict) or not isinstance(records, dict):
        raise ValueError("source must contain answers and records")
    for identifier, item in sorted(answers.items()):
        if not isinstance(item, dict):
            raise ValueError("malformed source answer")
        state = item.get("state", "UNKNOWN")
        value = item.get("value")
        text = value if isinstance(value, str) and value else sealed.canonical_json(value).decode()
        eligible = state == "PROVIDED" and item.get("source_type") == "HUMAN_DECLARATION"
        result.append(_item("answer", "answers", identifier, item, text, state, eligible, None))
    for category, rows in sorted(records.items()):
        if category not in questionnaire.RECORD_FIELDS or not isinstance(rows, list):
            raise ValueError("unknown/malformed source category: " + category)
        seen = set()
        for record in rows:
            identifier = record.get("id")
            if identifier in seen:
                raise ValueError("duplicate source record within category: " + str(identifier))
            seen.add(identifier)
            fields = record.get("fields")
            if not isinstance(fields, dict):
                raise ValueError("malformed source fields")
            field = "residual_status" if category == "risks" else "status"
            state = fields.get(field, "UNMODELED")
            text = fields.get(TEXT_FIELDS.get(category, ""))
            if not isinstance(text, str) or not text:
                text = sealed.canonical_json(fields).decode()
            result.append(_item("record", category, identifier, record, text, state,
                                state in ACTIVE.get(category, set()), TYPES.get(category)))
    if not result:
        raise ValueError("empty source inventory")
    return sorted(result, key=lambda item: item["key"])


def _item(kind, category, identifier, raw, text, state, eligible, requirement_type):
    if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,95}", identifier):
        raise ValueError("unsupported source ID; explicit upstream ID repair required")
    if not isinstance(state, str):
        raise ValueError("invalid source status")
    rejected = raw.get("review_disposition") in {"HUMAN_REJECTED", "REJECTED", "INVALIDATED", "SUPERSEDED"}
    return {"key": f"{kind}/{category}/{identifier}", "id": identifier, "kind": kind, "category": category,
            "item_sha256": digest(raw), "text": text, "status": state, "eligible": eligible and not rejected,
            "requirement_type": requirement_type}


def snapshot(document):
    # Exclude only fields which the genuine seal stamps; all semantic source data
    # (including unknown fields, rejection, status, provenance) remains bound.
    projected = deepcopy(document)
    for item in list(projected["answers"].values()) + [r for rows in projected["records"].values() for r in rows]:
        for key in ("reviewer", "timestamp", "last_edit", "last_edit_timestamp"):
            item.pop(key, None)
        if item.get("review_disposition") in {None, "HUMAN_CONFIRMED", "SEEDED_PENDING_REVIEW"}:
            item.pop("review_disposition", None)
    return digest({"package_id": projected.get("package_id"), "schema_version": projected.get("schema_version"),
                   "answers": projected["answers"], "records": projected["records"]})


def requirements_export(session):
    document = session["document"]
    return {"export_version": "0.1", "session_id": session["session_id"], "package_id": document["package_id"],
            "source_snapshot_sha256": snapshot(document), "source_revision": snapshot(document),
            "items": source_items(document), "authority": "PROPOSAL_SOURCE_ONLY_NOT_CATALOG_APPROVAL"}


def verified_source(session, user):
    """Verify independent seal-time commitment AND the current server source."""
    import artpkg_source_commitment as commitment
    from ux_harness.paths import safe_path, inventory
    sealed_id, entry = commitment.current(session["session_dir"], user)
    handoff = entry["handoff"]
    path = safe_path(Path(session["session_dir"]) / "sealed_packages" / sealed_id)
    inventory(path)  # Reject links, hardlinks, special files and oversized inventory.
    actual = derivation._load_sealed_files(path)
    derivation._verify_identity(actual, handoff["package"]["package_sha256"])
    # Neither target binding nor authority comes from the history under test.
    payloads = sealed.render_source_payloads(sealed.approved_snapshot(session["document"], user), session["validation"])
    expected, _ = sealed.assemble_files(handoff, payloads)
    if actual != expected or commitment.file_hashes(actual) != entry["files"]:
        raise ValueError("sealed source differs from server-known expected exact snapshot")
    document = sealed.parse_strict_json(actual["artifacts_package_answers.json"])
    return {"path": str(path), **handoff["package"], "sealed_id": sealed_id,
            "files": {k: sealed.sha256_bytes(v) for k, v in sorted(actual.items())}}, document


class Preparation:
    def __init__(self, session, user, root=UXPKG_ROOT):
        self.parser = runtime(root)
        from ux_harness.paths import safe_path, disjoint
        from ux_harness.custody import Custody
        self.session, self.user = session, user
        self.root = safe_path(root)
        self.session_path = safe_path(session["session_dir"])
        self.store = safe_path(self.session_path / "ux_preparation")
        self.custody = Custody(self.session_path / ".ux-preparation-custody")
        self.ux_custody = self.session_path / ".ux-render-custody"
        disjoint(self.store, self.custody.root, self.ux_custody, self.session_path / "sealed_packages")

    def _path(self, upload_id):
        if not isinstance(upload_id, str) or not re.fullmatch(r"[a-f0-9]{32}", upload_id):
            raise ValueError("invalid server upload ID")
        from ux_harness.paths import safe_path
        return safe_path(self.store / upload_id)

    def upload(self, raw, filename):
        if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,150}\.md", filename) or ".." in filename:
            raise ValueError("upload filename must be a new plain Markdown basename")
        if filename == "template_ux_ui_package.md":
            raise ValueError("upload a newly named completed proposal, not the template")
        normalized = self.parser.parse(raw)
        from ux_harness.hashing import write
        upload_id = uuid.uuid4().hex
        path = self._path(upload_id)
        with self.custody.session(create=True):
            path.mkdir(parents=True, mode=0o700)
            write(path / "proposal.md", raw)
            write(path / "normalized.json", normalized)
            record = self.custody.sign({"upload_version": "0.1", "upload_id": upload_id, "user": self.user,
                "session": str(self.session_path), "upload_sha256": normalized["upload_sha256"],
                "normalized_sha256": digest(normalized), "snapshot_sha256": snapshot(self.session["document"])})
            write(path / "upload.json", record)
        return {"upload_id": upload_id, "normalized": normalized, "preview": raw.decode("utf-8"), "authority": "NONE"}

    def _load(self, upload_id):
        from ux_harness.hashing import load
        from ux_harness.paths import inventory
        path = self._path(upload_id)
        inventory(path)
        record = load(path / "upload.json")
        self.custody.verify_signature(record)
        raw = (path / "proposal.md").read_bytes()
        normalized = self.parser.parse(raw)
        if record != {**record, "user": self.user, "session": str(self.session_path), "upload_id": upload_id,
                      "upload_sha256": sealed.sha256_bytes(raw), "normalized_sha256": digest(normalized)}:
            raise ValueError("upload owner/path/hash binding mismatch")
        if load(path / "normalized.json") != normalized:
            raise ValueError("normalized proposal tampered")
        if snapshot(self.session["document"]) != record["snapshot_sha256"]:
            raise ValueError("stale requirements: upload a reconciled proposal and review again")
        return path, record, normalized

    def _basis(self, upload_id):
        path, upload, proposal = self._load(upload_id)
        source, document = verified_source(self.session, self.user)
        metadata = dict(proposal["tables"]["metadata"])
        expected = snapshot(document)
        if expected != upload["snapshot_sha256"] or metadata["Source snapshot digest"] != expected or metadata["Source requirements revision"] != expected:
            raise ValueError("source snapshot/revision mismatch; reconcile before admission")
        if metadata["ArtPkg session/package ID"] != document["package_id"]:
            raise ValueError("wrong source package ID")
        if metadata["Sealed ArtPkg digest"] not in {"UNKNOWN", source["package_sha256"]}:
            raise ValueError("asserted sealed digest does not match verified source")
        items = source_items(document)
        # Full source identity, original upload, normalized tables and every raw item
        # are in the exact review basis. Seal stamping is explicitly re-reviewed.
        basis = {"source": source, "upload_sha256": upload["upload_sha256"], "normalized_sha256": digest(proposal),
                 "snapshot_sha256": expected, "items": items}
        return path, proposal, basis

    def preview(self, upload_id):
        with self.custody.session():
            path, proposal, basis = self._basis(upload_id)
            return {"upload_id": upload_id, "basis_sha256": digest(basis), "basis": basis,
                    "normalized": proposal, "preview": (path / "proposal.md").read_text(encoding="utf-8"),
                    "attestation": ATTESTATION, "authority": "NONE"}

    def resolution_questionnaire(self, upload_id):
        """Describe governed choices for a current draft; this grants no authority."""
        with self.custody.session():
            _, _, proposal = self._load(upload_id)
        answers = self.session["document"].get("answers", {})
        questions = []
        for question in RESOLUTION_QUESTIONS:
            answer = answers.get(question["id"], {})
            value = answer.get("value", "") if answer.get("state") == "PROVIDED" else ""
            selected, other = "UNDECIDED", ""
            if value.startswith("OTHER: "):
                selected, other = "OTHER", value.removeprefix("OTHER: ")
            elif value.partition(": ")[0] in question["choices"]:
                selected = value.partition(": ")[0]
            questions.append({**question, "selected": selected, "other": other})
        return {"resolution_version": "0.1", "upload_id": upload_id,
                "reported_blockers": proposal["blockers"], "questions": questions,
                "status": resolution_status(self.session["document"]), "authority": "NONE"}

    def resolve(self, upload_id, decisions):
        """Persist explicit human source answers, invalidating this draft by design."""
        with self.custody.session():
            self._load(upload_id)
        if not isinstance(decisions, dict) or set(decisions) != set(RESOLUTION_BY_ID):
            raise ValueError("all UX resolution questions must be supplied exactly once")
        answers = {identifier: _resolution_value(question, decisions[identifier])
                   for identifier, question in RESOLUTION_BY_ID.items()}
        import artpkg_intake
        artpkg_intake.provide_answers(self.session, answers, self.user)
        status = resolution_status(self.session["document"])
        return {"resolution_version": "0.1", "status": status,
                "source_snapshot_sha256": snapshot(self.session["document"]),
                "proposal_stale": True, "implementation_authority": "NONE",
                "next_action": "RETURN_TO_ARTPKG_INTAKE",
                "return_url": "/?" + urlencode({"dir": str(self.session_path), "from": "ux-resolution"}) + "#sealReview"}

    def _account(self, proposal, basis, exclusions, type_mappings):
        if not isinstance(exclusions, dict) or not isinstance(type_mappings, dict):
            raise ValueError("scoped exclusions and type mappings must be objects")
        rows = proposal["tables"]["scope"]
        proposed = {r[1] + "/" + r[0]: r for r in rows}
        items = {i["key"]: i for i in basis["items"]}
        if set(proposed) != set(items) or len(proposed) != len(rows):
            raise ValueError("scope must account exactly once for ALL answers and records using kind/category")
        if set(exclusions) - set(items) or set(type_mappings) - set(items):
            raise ValueError("unknown review exclusion/type mapping key")
        dispositions, reqs = [], []
        used_exclusions, used_types = set(), set()
        for key, item in items.items():
            row = proposed[key]
            if row[2] != item["text"] or row[3] != basis["snapshot_sha256"]:
                raise ValueError("exact source text/revision mismatch: " + key)
            if row[4] != item["status"]:
                raise ValueError("source status mismatch: " + key)
            disposition, reason, rtype = row[6], row[7], None
            if disposition == "INCLUDE":
                if not item["eligible"]:
                    raise ValueError("INCLUDE requires known active approved source: " + key)
                rtype = item["requirement_type"]
                if rtype is None:
                    rtype = type_mappings.get(key)
                    used_types.add(key)
                if rtype not in {"FUNCTIONAL", "NON_FUNCTIONAL", "CONSTRAINT"}:
                    raise ValueError("explicit reviewed requirement type mapping needed: " + key)
                reqs.append({"id": item["id"], "text": item["text"], "type": rtype,
                             "authority": "HUMAN_APPROVED", "ux_relevant": self.parser.boolean(row[5]), "capabilities": []})
            elif disposition == "EXCLUDE":
                evidence = exclusions.get(key)
                if not isinstance(evidence, dict) or set(evidence) != {"item_sha256", "reason"} or evidence["item_sha256"] != item["item_sha256"]:
                    raise ValueError("explicit scoped reviewed exclusion evidence required: " + key)
                reason = evidence["reason"]
                if not isinstance(reason, str) or not reason.strip() or reason in {"UNKNOWN", "NONE", "NOT_APPLICABLE"}:
                    raise ValueError("exclusion requires a specific human applicability reason: " + key)
                if item["status"] == "NOT_APPLICABLE" and not reason.startswith("NOT_APPLICABLE: "):
                    raise ValueError("NOT_APPLICABLE needs a distinct reason prefix: " + key)
                used_exclusions.add(key)
            else:
                raise ValueError("unresolved/invalid source disposition: " + key)
            dispositions.append({"key": key, "item_sha256": item["item_sha256"], "status": item["status"],
                                 "disposition": disposition, "reason": reason, "requirement_type": rtype})
        if used_exclusions != set(exclusions) or used_types != set(type_mappings):
            raise ValueError("unused or conflicting review evidence")
        data = self.parser.strict_input(proposal, reqs, basis["source"]["package_id"])
        files = self.parser.input_bytes(data)
        lineage = {"lineage_version": "0.1", **{k: basis[k] for k in ("source", "upload_sha256", "normalized_sha256", "snapshot_sha256")},
                   "dispositions": dispositions, "input_hashes": {k: sealed.sha256_bytes(v) for k, v in files.items()}}
        from ux_harness.schema import validate
        validate("preparation-lineage", lineage)
        return lineage, files

    def review(self, upload_id, basis_sha256, attestation, exclusions, type_mappings):
        """Authenticated human UI only; no CLI or uploaded approval mechanism."""
        from ux_harness.schema import validate
        from ux_harness.hashing import write
        with self.custody.session():
            path, proposal, basis = self._basis(upload_id)
            if attestation != ATTESTATION or digest(basis) != basis_sha256:
                raise ValueError("explicit human attestation must bind the exact current review basis")
            if (path / "review.json").exists():
                raise ValueError("review already recorded; upload a fresh proposal for any change")
            lineage, _ = self._account(proposal, basis, exclusions, type_mappings)
            review = self.custody.sign({"review_version": "0.1", "user": self.user, "session": str(self.session_path),
                "upload_id": upload_id, "basis_sha256": basis_sha256, "lineage": lineage,
                "exclusions": exclusions, "type_mappings": type_mappings, "attestation": ATTESTATION})
            validate("preparation-review", review)
            write(path / "review.json", review)
            return {"review_sha256": digest(review), "status": "READY_FOR_UX_PROCESSING", "implementation_authority": "NONE"}

    def _reviewed(self, upload_id):
        from ux_harness.hashing import load
        from ux_harness.schema import validate
        path, proposal, basis = self._basis(upload_id)
        review = load(path / "review.json")
        validate("preparation-review", review)
        self.custody.verify_signature(review)
        if (review["user"], review["session"], review["upload_id"], review["basis_sha256"]) != (self.user, str(self.session_path), upload_id, digest(basis)):
            raise ValueError("review is stale or belongs to another user/session/proposal")
        lineage, files = self._account(proposal, basis, review["exclusions"], review["type_mappings"])
        if lineage != review["lineage"]:
            raise ValueError("review lineage changed")
        return path, review, files

    def run(self, upload_id):
        from ux_harness.app import Harness
        from ux_harness.hashing import write
        from ux_harness.intake import accept
        from ux_harness.mapper import propose_contract
        from ux_harness.paths import safe_path, fresh, disjoint
        from ux_harness.schema import validate
        with self.custody.session():
            path, review, files = self._reviewed(upload_id)
            input_path, output_path = safe_path(path / "input"), safe_path(path / "output")
            disjoint(input_path, output_path, Path(review["lineage"]["source"]["path"]), self.ux_custody, self.custody.root)
            fresh(input_path)
            fresh(output_path)
            input_path.mkdir(mode=0o700)
            for name, data in files.items():
                write(input_path / name, data)
            package = accept(input_path)
            if not package.no_ui_reason:
                propose_contract(package)
            executable = self.root / ".venv/bin/python"
            if not executable.is_file() or not os.access(executable, os.X_OK):
                raise ValueError("pinned UXPkg virtual environment executable unavailable")
            executable_hash = sealed.sha256_bytes(executable.read_bytes())
            argv = [str(executable), "-I", "-m", "ux_harness", "--custody", str(self.ux_custody), "--renderer-root", str(self.root)]
            # Execute the administrator-installed package, not an injected source
            # checkout. Refresh that installation when deploying source changes.
            env = {"PATH": os.defpath, "HOME": str(Path.home()), "PYTHONNOUSERSITE": "1"}
            node = os.environ.get("UXPKG_NODE", "/home/rootux/.nvm/versions/node/v24.20.0/bin/node")
            if not Path(node).is_absolute():
                raise ValueError("trusted UXPKG_NODE must be absolute")
            env["UXPKG_NODE"] = node
            for command in (["propose", str(input_path), "--output", str(output_path)],
                            *([] if package.no_ui_reason else [["render", str(output_path)]])):
                if sealed.sha256_bytes(executable.read_bytes()) != executable_hash:
                    raise ValueError("pinned executable changed")
                result = subprocess.run(argv + command, shell=False, timeout=90, cwd=self.root, env=env,
                                        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    raise ValueError("local ux-harness failed with exit " + str(result.returncode))
            # Read-only local custody verification, NOT stdout or a claimed hash.
            status = Harness(self.ux_custody, self.root).status(output_path)
            if status["status"] not in {"NO_UI_ACCEPTED", "READY_FOR_HUMAN_UX_REVIEW"}:
                raise ValueError("unexpected verified UX lifecycle")
            self._reviewed(upload_id)  # Recheck source and review after subprocesses.
            if accept(input_path).hashes != review["lineage"]["input_hashes"]:
                raise ValueError("emitted input hashes changed")
            receipt = self.custody.sign({"receipt_version": "0.1", "user": self.user, "session": str(self.session_path),
                "upload_id": upload_id, "review_sha256": digest(review), "lineage": review["lineage"],
                "input_path": str(input_path), "output_path": str(output_path), "uxpkg_package_sha256": status["package_sha256"],
                "status": status["status"], "implementation_authority": "NONE"})
            validate("preparation-receipt", receipt)
            write(path / "receipt.json", receipt)
            return receipt

    def verify(self, upload_id):
        """Reusable read-only verification, requiring original local private stores."""
        from ux_harness.app import Harness
        from ux_harness.hashing import load
        from ux_harness.intake import accept
        from ux_harness.schema import validate
        with self.custody.session():
            path, review, _ = self._reviewed(upload_id)
            receipt = load(path / "receipt.json")
            validate("preparation-receipt", receipt)
            self.custody.verify_signature(receipt)
            expected = {"user": self.user, "session": str(self.session_path), "upload_id": upload_id,
                        "review_sha256": digest(review), "lineage": review["lineage"],
                        "input_path": str(path / "input"), "output_path": str(path / "output")}
            if any(receipt[k] != v for k, v in expected.items()):
                raise ValueError("receipt binding mismatch")
            if accept(path / "input").hashes != receipt["lineage"]["input_hashes"]:
                raise ValueError("receipt input mismatch")
            status = Harness(self.ux_custody, self.root).status(path / "output")
            if status["package_sha256"] != receipt["uxpkg_package_sha256"] or status["status"] != receipt["status"]:
                raise ValueError("receipt output digest/lifecycle mismatch")
            return receipt