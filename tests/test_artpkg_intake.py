import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_intake as intake


class IntakeSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.template = self.root / "reusable_artifacts_package_template.md"
        self.template.write_text("# Package\n", encoding="utf-8")
        self.pre = self.root / "pre.md"
        self.pre.write_text(
            "# Pre-Artifacts Package\n\n"
            "## 1. Project Summary\n"
            "- Project name: Example Intake\n"
            "- Primary goal: Produce a reviewable package.\n\n"
            "## 16. Authority and Decision Boundaries\n"
            "- This file is discovery context; it is not an approved implementation contract.\n"
            "## 14. Evidence and Validation\n"
            "- What is still unverified? Runtime behavior has not been validated.\n\n"
            "## 7. Requirements\n"
            "### Functional Requirements\n"
            "- FR-01: The intake UI shall let reviewers resolve seeded questionnaire gaps.\n\n"
            "## 19. Sensitive or Restricted Content\n"
            "- Does this project involve sensitive data, credentials, regulated information, or restricted content? Yes\n"
            "- If yes, what safeguards are required? Local-only handling and redaction.\n"
            "- Are any redaction or access controls needed? Yes, redact customer payloads.\n\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_create_intake_session_persists_seed_and_answers(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        session_dir = Path(session["session_dir"])
        self.assertTrue((session_dir / "source_pre_artifacts.md").exists())
        self.assertTrue((session_dir / "seed.json").exists())
        self.assertTrue((session_dir / "answers.json").exists())
        self.assertEqual(intake.sha256_file(self.pre), session["source"]["sha256"])
        self.assertEqual("Example Intake", session["document"]["answers"]["PKG-001"]["value"])
        self.assertEqual("SOURCE_ARTIFACT", session["document"]["answers"]["PKG-001"]["source_type"])

    def test_calculator_pre_artifacts_reaches_questionnaire_with_structure_and_authority_intact(self):
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        session = intake.create_intake_session(
            source,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        seed = json.loads(Path(session["seed_path"]).read_text(encoding="utf-8"))
        records = session["document"]["records"]
        scope = session["document"]["answers"]["BND-001"]["value"]

        self.assertEqual(source.read_text(encoding="utf-8"), Path(session["source"]["stored_path"]).read_text(encoding="utf-8"))
        self.assertEqual(3, len(records["functional_requirements"]))
        self.assertEqual(2, len(records["non_functional_requirements"]))
        self.assertEqual(2, len(records["acceptance_criteria"]))
        self.assertEqual(
            ["CONFIRMED_BY_USER", "OBSERVED", "PROPOSED", "INFERRED", "UNKNOWN", "DEFERRED", "REJECTED"],
            seed["source_statuses"],
        )
        self.assertEqual(
            ["CONFIRMED_BY_USER", "INFERRED", "PROPOSED"],
            [record["fields"]["source_status"] for record in records["functional_requirements"]],
        )
        self.assertLess(scope.index("written in Python"), scope.index("four arithmetic operations"))
        self.assertLess(scope.index("four arithmetic operations"), scope.index("local single-user workflow"))
        self.assertEqual("THRESHOLD_REQUIRED", records["non_functional_requirements"][1]["fields"]["measurement"].strip(" `"))
        self.assertEqual("NONE", session["document"]["answers"]["AUT-001"]["value"])
        self.assertEqual("HUMAN_REVIEW_ONLY", session["validation"]["next_permitted_action"])

    def test_gitignore_excludes_local_artpkg_sessions(self):
        gitignore = (Path(__file__).parents[1] / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".artpkg/", gitignore)

    def test_rejected_seeded_answer_persists_and_needs_replacement(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        rejected = intake.reject_seeded_answer(session, "PKG-001", "Project name needs correction", "Reviewer")
        reloaded = intake.load_intake_session(session["session_dir"])
        queued_ids = {item["id"] for item in reloaded["review_queues"]["needs_answer"]}

        self.assertEqual("Example Intake", rejected["value"])
        self.assertEqual("HUMAN_REJECTED", reloaded["document"]["answers"]["PKG-001"]["review_disposition"])
        self.assertEqual("Example Intake", reloaded["document"]["answers"]["PKG-001"]["value"])
        self.assertIn("PKG-001", queued_ids)
        self.assertEqual("seeded answer was rejected and needs replacement", next(
            item["reason"] for item in reloaded["review_queues"]["needs_answer"] if item["id"] == "PKG-001"
        ))

    def test_review_queues_separate_unknown_authority_and_evidence_items(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        queues = session["review_queues"]

        need_ids = {item["id"] for item in queues["needs_answer"]}
        authority_ids = {item["id"] for item in queues["authority_sensitive"]}
        evidence_ids = {item["id"] for item in queues["evidence_sensitive"]}

        self.assertIn("PKG-003", need_ids)
        self.assertIn("AUT-001", authority_ids)
        self.assertIn("SEC-001", authority_ids)
        self.assertIn("OVR-007", evidence_ids)

    def test_answer_queue_items_include_question_context_for_human_review(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        bnd_item = next(item for item in session["review_queues"]["needs_answer"] if item["id"] == "BND-001")

        self.assertEqual("Scope boundary", bnd_item["question"]["group"])
        self.assertEqual("Make the included and excluded work explicit before it is handed off.", bnd_item["question"]["group_description"])
        self.assertEqual("In scope", bnd_item["question"]["prompt"])
        self.assertEqual("LONG_TEXT", bnd_item["question"]["answer_type"])
        self.assertEqual(
            "Name the behavior, components, or decisions this package is allowed to discuss or change.",
            bnd_item["question"]["meaning"],
        )
        self.assertEqual("Order validation and its public API contract.", bnd_item["question"]["example"])
        self.assertEqual([], bnd_item["question"]["choices"])

    def test_answer_queue_items_include_project_agnostic_review_guidance(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        bnd_item = next(item for item in session["review_queues"]["needs_answer"] if item["id"] == "BND-001")

        self.assertEqual(
            "What work this artifact package is allowed to cover.",
            bnd_item["question"]["decision_prompt"],
        )
        self.assertIn("This package is in scope for:", bnd_item["question"]["answer_scaffold"])
        self.assertIn("It may make decisions about:", bnd_item["question"]["answer_scaffold"])
        self.assertIn("It does not authorize:", bnd_item["question"]["answer_scaffold"])
        self.assertIn("scope expansion", " ".join(bnd_item["question"]["downstream_effects"]))

    def test_question_guidance_scales_by_question_family(self):
        aut_context = intake._question_context("AUT-001")
        ac_context = intake._question_context("AC-SET")
        generic_context = intake._question_context("FUT-001")

        self.assertIn("who granted permission", aut_context["decision_prompt"])
        self.assertIn("Authority granted by:", aut_context["answer_scaffold"])
        self.assertIn("What must be true", ac_context["decision_prompt"])
        self.assertIn("Pass condition:", ac_context["answer_scaffold"])
        self.assertIn("What human-owned answer", generic_context["decision_prompt"])
        self.assertIn("Source basis:", generic_context["answer_scaffold"])

    def test_answer_queue_items_explain_unknown_source_attribution_and_confidence(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        bnd_item = next(item for item in session["review_queues"]["needs_answer"] if item["id"] == "BND-001")

        self.assertEqual("UNKNOWN", bnd_item["source_context"]["answer_status"])
        self.assertEqual("ABSENT", bnd_item["source_context"]["source_status"])
        self.assertIn("No explicit in-scope statement", bnd_item["source_context"]["summary"])
        self.assertEqual("Classification confidence", bnd_item["confidence_context"]["label"])
        self.assertIn("missing or seeded", bnd_item["confidence_context"]["meaning"])

    def test_calculator_generates_only_materially_absent_human_questions(self):
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        session = intake.create_intake_session(source, self.root, template_path=self.template, respondent="Reviewer")

        unanswered = {item["id"]: item for item in session["review_queues"]["needs_answer"] if item["kind"] == "answer"}
        confirmations = {item["id"]: item for item in session["review_queues"]["needs_confirmation"] if item["kind"] == "answer"}
        self.assertEqual({"PKG-003", "PKG-004", "SEC-001"}, set(unanswered))
        for qid, item in unanswered.items():
            self.assertEqual("ABSENT", item["source_status"], qid)
            self.assertEqual("required non-blocking answer is absent", item["reason"], qid)
        for qid in ("OVR-001", "OVR-002", "OVR-008", "PKG-001", "PKG-005"):
            self.assertNotIn(qid, confirmations, qid)
            self.assertIn(qid, session["question_plan"]["review_summary_ids"], qid)
            self.assertEqual("SOURCE_ARTIFACT", session["document"]["answers"][qid]["source_type"], qid)

    def test_concept_discovery_uses_phase_aware_question_plan(self):
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        session = intake.create_intake_session(source, self.root, template_path=self.template, respondent="Reviewer")

        plan = session["question_plan"]
        active_ids = set(plan["active_question_ids"])
        self.assertEqual("DISCOVERY_CONCEPT_NOT_CREATED", plan["profile"])
        self.assertNotIn("PKG-006", active_ids)
        self.assertFalse(any(qid.startswith(("ART-", "ENV-", "EVD-", "HAR-", "HND-", "VAL-")) for qid in active_ids))
        self.assertEqual("NONE", session["document"]["answers"]["AUT-001"]["value"])
        self.assertEqual("NOT_APPLICABLE", session["document"]["answers"]["PKG-006"]["state"])
        self.assertIn("intent_summary", session["review_summary"])

    def test_accept_intent_summary_is_visible_after_refresh(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        review = intake.review_intent_summary(session, "ACCEPT SUMMARY", "Reviewer")

        self.assertEqual(review, session["review_summary"]["intent_summary"]["review"])
        self.assertEqual("ACCEPT SUMMARY", session["review_summary"]["intent_summary"]["review"]["action"])
        reloaded = intake.load_intake_session(session["session_dir"])
        self.assertEqual(review, reloaded["review_summary"]["intent_summary"]["review"])

    def test_seeded_records_are_grouped_for_section_review(self):
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        session = intake.create_intake_session(source, self.root, template_path=self.template, respondent="Reviewer")

        record_tasks = [item for item in session["review_queues"]["needs_confirmation"] if item["kind"] == "record"]
        section_tasks = session["review_queues"]["repeated_records_pending_review"]
        self.assertEqual([], record_tasks)
        self.assertTrue(any(item["section"] == "functional_requirements" for item in section_tasks))
        self.assertEqual(3, next(item["count"] for item in section_tasks if item["section"] == "functional_requirements"))

        original = [(record["id"], record["fields"].get("source_status"), record["source_type"]) for record in session["document"]["records"]["functional_requirements"]]
        intake.confirm_record_section(session, "functional_requirements", "Reviewer")
        confirmed = session["document"]["records"]["functional_requirements"]
        self.assertEqual(original, [(record["id"], record["fields"].get("source_status"), record["source_type"]) for record in confirmed])
        self.assertTrue(all(record["review_disposition"] == "HUMAN_CONFIRMED" for record in confirmed))
        self.assertTrue(all(record["section_confirmation"]["scope"] == "functional_requirements" for record in confirmed))

    def test_existing_system_change_keeps_repository_snapshot_active(self):
        document = intake.questionnaire.new_answers(str(self.template), str(self.root), "Reviewer")
        intake.questionnaire.set_answer(document, "PKG-002", "CROSS_PROJECT_TRANSFER")
        intake.questionnaire.set_answer(document, "PKG-005", str(self.root))
        intake.questionnaire.set_answer(document, "PKG-006", "abc123")

        plan = intake.build_question_plan(document)

        self.assertEqual("LIFECYCLE_DEFAULT", plan["profile"])
        self.assertIn("PKG-006", plan["active_question_ids"])
        self.assertEqual("abc123", document["answers"]["PKG-006"]["value"])

    def test_active_work_counts_do_not_treat_zero_answers_as_complete(self):
        source = Path(__file__).parent / "fixtures" / "basic-windows-calculator_preartifacts.md"
        session = intake.create_intake_session(source, self.root, template_path=self.template, respondent="Reviewer")

        counts = session["human_work_counts"]
        self.assertIn("needs_human_answer", counts)
        self.assertIn("needs_human_confirmation", counts)
        self.assertIn("repeated_records_pending_review", counts)
        self.assertEqual(3, counts["final_attestations_remaining"])
        self.assertFalse(counts["ready_to_seal"])

    def test_q_b_rows_are_extracted_as_open_questions(self):
        self.pre.write_text(
            "# Pre-Artifacts Package\n\n## 12. Open and Blocking Questions\n\n"
            "| ID | Question | Why it matters | Status |\n"
            "|---|---|---|---|\n"
            "| Q-B001 | GUI or command line? | Changes the interaction architecture. | OPEN |\n",
            encoding="utf-8",
        )
        session = intake.create_intake_session(self.pre, self.root, template_path=self.template, respondent="Reviewer")
        questions = session["document"]["records"]["questions"]

        self.assertEqual("Q-B001", questions[0]["id"])
        self.assertEqual("GUI or command line?", questions[0]["fields"]["question"])
        self.assertIn("Q-B001", session["question_plan"]["material_decision_ids"])

    def test_sec_001_rejects_invalid_text_before_conditionals(self):
        session = intake.create_intake_session(self.pre, self.root, template_path=self.template, respondent="Reviewer")
        intake.provide_answer(session, "SEC-001", "YES", reviewer="Reviewer")
        self.assertNotEqual("NOT_APPLICABLE", session["document"]["answers"]["SEC-001-CATEGORIES"]["state"])

        with self.assertRaisesRegex(ValueError, "SEC-001 must be one of: (NO, YES|YES, NO)"):
            intake.provide_answer(session, "SEC-001", "not sure", reviewer="Reviewer")
        self.assertNotEqual("NOT_APPLICABLE", session["document"]["answers"]["SEC-001-CATEGORIES"]["state"])

    def test_explicit_unknown_deferred_rejected_and_conflict_have_distinct_queue_reasons(self):
        document = intake.questionnaire.new_answers(str(self.template), str(self.root), "Reviewer")
        cases = {
            "OVR-001": ("UNKNOWN", "UNKNOWN", "EXPLICIT_UNKNOWN"),
            "OVR-002": ("DEFERRED", "DEFERRED", "DEFERRED"),
            "OVR-005": ("UNKNOWN", "UNKNOWN", "REJECTED"),
            "OVR-007": ("UNKNOWN", "UNKNOWN", "CONFLICTED"),
        }
        for qid, (value, state, source_status) in cases.items():
            intake.questionnaire.set_answer(document, qid, value, state, "SOURCE_ARTIFACT", "source.md")
            document["answers"][qid].update({"source_status": source_status, "review_priority": "MEDIUM", "review_disposition": "SEEDED_PENDING_REVIEW"})
        queues = intake.build_review_queues(document, {}, {"blocking_ids": []})
        reasons = {item["id"]: item["reason"] for item in queues["needs_answer"]}

        self.assertEqual("source explicitly records UNKNOWN", reasons["OVR-001"])
        self.assertEqual("source answer was explicitly rejected and needs replacement", reasons["OVR-005"])
        self.assertEqual("conflicting source answers require human resolution", reasons["OVR-007"])
        deferred = next(item for item in queues["needs_confirmation"] if item["id"] == "OVR-002")
        self.assertEqual("answer is deferred until a later phase or gate", deferred["reason"])

    def test_missing_answer_queue_items_recommend_human_provided_state(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        bnd_item = next(item for item in session["review_queues"]["needs_answer"] if item["id"] == "BND-001")

        recommendation = bnd_item["state_recommendation"]
        self.assertEqual("PROVIDED", recommendation["suggested_state"])
        self.assertEqual("write_human_answer", recommendation["action"])
        self.assertIn("scope-sensitive downstream decisions", recommendation["reason"])
        self.assertIn("Use TO_BE_INSPECTED", recommendation["fallback"])
        self.assertFalse(recommendation["can_auto_apply"])

    def test_seeded_authority_answers_recommend_human_confirmation(self):
        item = {
            "state": "PROVIDED",
            "value": "ArtPkg intake UI",
            "source_type": "SOURCE_ARTIFACT",
            "source_reference": "ArtPkg intake UI",
        }

        recommendation = intake._state_recommendation("AUT-002", item)

        self.assertEqual("PROVIDED", recommendation["suggested_state"])
        self.assertEqual("confirm_seeded_answer", recommendation["action"])
        self.assertIn("authority-sensitive", recommendation["reason"])
        self.assertIn("does not broaden authority", recommendation["checklist"])
        self.assertFalse(recommendation["can_auto_apply"])

    def test_record_queue_items_include_schema_context_for_human_review(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        record_id = next(iter(session["created_records"].values()))[0]
        record_item = next(item for item in session["review_queues"]["repeated_records_pending_review"] if record_id in item["record_ids"])

        self.assertEqual("Functional Requirements", record_item["record_context"]["label"])
        self.assertEqual("Functional requirements", record_item["record_context"]["group"])
        self.assertEqual(
            "Record a human-owned behavior the project must provide.",
            record_item["record_context"]["group_description"],
        )
        fields = {field["name"]: field for field in record_item["record_schema"]}
        self.assertEqual("Requirement text", fields["requirement"]["label"])
        self.assertEqual("Provide the requirement text for this functional requirements record.", fields["requirement"]["meaning"])
        self.assertEqual(["ACCEPTED", "IMPLEMENTED", "PROPOSED", "VERIFIED"], fields["status"]["choices"])

    def test_confirm_and_reject_seeded_answers_are_durable(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        intake.confirm_answer(session, "PKG-001", reviewer="Reviewer")
        intake.reject_seeded_answer(session, "PKG-003", reason="Owner must be named by human", reviewer="Reviewer")

        reloaded = intake.load_intake_session(session["session_dir"])
        self.assertEqual("HUMAN_CONFIRMED", reloaded["document"]["answers"]["PKG-001"]["review_disposition"])
        self.assertEqual("HUMAN_REJECTED", reloaded["document"]["answers"]["PKG-003"]["review_disposition"])
        self.assertEqual("Owner must be named by human", reloaded["document"]["answers"]["PKG-003"]["rejection_reason"])

    def test_provide_answer_replaces_rejected_seed_with_human_declaration(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        intake.reject_seeded_answer(session, "PKG-003", reason="Owner must be named by human", reviewer="Reviewer")
        updated = intake.provide_answer(session, "PKG-003", "Vin", reviewer="Reviewer")
        reloaded = intake.load_intake_session(session["session_dir"])
        needs_answer_ids = {item["id"] for item in reloaded["review_queues"]["needs_answer"]}

        self.assertEqual("Vin", updated["value"])
        self.assertEqual("PROVIDED", updated["state"])
        self.assertEqual("HUMAN_DECLARATION", updated["source_type"])
        self.assertEqual("HUMAN_CONFIRMED", updated["review_disposition"])
        self.assertNotIn("PKG-003", needs_answer_ids)

    def test_restricted_content_human_answer_is_durable(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        intake.provide_answer(session, "SEC-001", "no", reviewer="Reviewer")
        reloaded = intake.load_intake_session(session["session_dir"])
        restricted = reloaded["document"]["answers"]["SEC-001"]

        self.assertEqual("NO", restricted["value"])
        self.assertEqual("PROVIDED", restricted["state"])
        self.assertEqual("HUMAN_DECLARATION", restricted["source_type"])
        self.assertEqual("ArtPkg intake UI", restricted["source_reference"])
        self.assertEqual("HUMAN_CONFIRMED", restricted["review_disposition"])
        self.assertNotIn("SEC-001", {item["id"] for item in reloaded["review_queues"]["needs_answer"]})

    def test_confirm_and_reject_seeded_records_are_durable(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        record_id = next(iter(session["created_records"].values()))[0]

        confirmed = intake.confirm_record(session, record_id, reviewer="Reviewer")
        self.assertEqual("HUMAN_CONFIRMED", confirmed["review_disposition"])

        rejected = intake.reject_seeded_record(session, record_id, "Record needs replacement", reviewer="Reviewer")
        reloaded = intake.load_intake_session(session["session_dir"])
        needs_answer_ids = {item["id"] for item in reloaded["review_queues"]["needs_answer"]}

        self.assertEqual("HUMAN_REJECTED", rejected["review_disposition"])
        self.assertEqual("Record needs replacement", rejected["rejection_reason"])
        self.assertEqual("HUMAN_REJECTED", intake.questionnaire.find_record(reloaded["document"], record_id)["review_disposition"])
        self.assertIn(record_id, needs_answer_ids)

    def test_advance_record_status_sets_field_and_history_without_touching_review_disposition(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        record_id = session["created_records"]["functional_requirements"][0]
        before = intake.questionnaire.find_record(session["document"], record_id)
        self.assertEqual("PROPOSED", before["fields"]["status"])
        self.assertNotIn("review_disposition", before)

        updated = intake.advance_record_status(session, record_id, "ACCEPTED", reviewer="Reviewer")

        self.assertEqual("ACCEPTED", updated["fields"]["status"])
        self.assertNotIn("review_disposition", updated, "advance_record_status must not fabricate review_disposition")
        self.assertEqual(1, len(updated["status_history"]))
        entry = updated["status_history"][0]
        self.assertEqual({"field": "status", "from": "PROPOSED", "to": "ACCEPTED", "reviewer": "Reviewer"},
                         {k: v for k, v in entry.items() if k != "timestamp"})

        reloaded = intake.load_intake_session(session["session_dir"])
        persisted = intake.questionnaire.find_record(reloaded["document"], record_id)
        self.assertEqual("ACCEPTED", persisted["fields"]["status"])
        self.assertEqual(1, len(persisted["status_history"]))

    def test_advance_record_status_rejects_value_outside_category_enum(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        record_id = session["created_records"]["functional_requirements"][0]

        with self.assertRaises(ValueError):
            intake.advance_record_status(session, record_id, "NOT_A_REAL_STATUS", reviewer="Reviewer")

        unchanged = intake.questionnaire.find_record(session["document"], record_id)
        self.assertEqual("PROPOSED", unchanged["fields"]["status"])

    def test_advance_record_status_rejects_category_with_no_status_field(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        session["document"]["records"].setdefault("actors", []).append({
            "id": "ACT-TEST", "fields": {"name": "Test actor", "role_type": "USER"},
            "source_type": "HUMAN_DECLARATION",
        })

        with self.assertRaises(ValueError):
            intake.advance_record_status(session, "ACT-TEST", "ACCEPTED", reviewer="Reviewer")

    def test_advance_record_status_rejects_unknown_record_id(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        with self.assertRaises(KeyError):
            intake.advance_record_status(session, "FR-999", "ACCEPTED", reviewer="Reviewer")

    def test_advance_record_status_uses_residual_status_field_for_risks(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )
        risk_ids = session["created_records"].get("risks")
        if not risk_ids:
            self.skipTest("fixture seeded no risks records")
        record_id = risk_ids[0]

        updated = intake.advance_record_status(session, record_id, "MITIGATED", reviewer="Reviewer")

        self.assertEqual("MITIGATED", updated["fields"]["residual_status"])
        self.assertEqual("residual_status", updated["status_history"][0]["field"])

    def test_rejected_sensitive_answers_remain_in_specialist_queues(self):
        session = intake.create_intake_session(
            self.pre,
            self.root,
            template_path=self.template,
            respondent="Reviewer",
        )

        intake.reject_seeded_answer(session, "SEC-001", "Restricted-content answer needs review", "Reviewer")
        intake.reject_seeded_answer(session, "OVR-007", "Unverified claim needs review", "Reviewer")

        reloaded = intake.load_intake_session(session["session_dir"])
        authority_ids = {item["id"] for item in reloaded["review_queues"]["authority_sensitive"]}
        evidence_ids = {item["id"] for item in reloaded["review_queues"]["evidence_sensitive"]}

        self.assertIn("SEC-001", authority_ids)
        self.assertIn("OVR-007", evidence_ids)
