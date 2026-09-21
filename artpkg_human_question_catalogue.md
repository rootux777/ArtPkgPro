# ArtPkg Human Question Catalogue

## Required summary counts

| Count | Value |
|---|---:|
| total catalogue questions | 117 |
| unconditional questions | 85 |
| conditional questions | 32 |
| package administration questions | 10 |
| source seeded questions | 36 |
| questions requiring human authority | 20 |
| current phase blockers | 3 |
| later phase questions | 37 |
| final assessment or sealing attestations | 4 |
| questions presented in calculator session | 2 |
| questions answered directly by user | 2 |
| questions resolved through source seeding | 19 |
| questions resolved by package level confirmation | 0 |
| questions deferred | 0 |
| questions marked NOT APPLICABLE | 33 |
| questions suppressed | 32 |
| questions still unresolved | 0 |

Counts use the definitions in the JSON report. The canonical total is the 117 entries in `QUESTION_CATALOG`; six additional dynamic/action prompt templates are catalogued separately. Classification is advisory and non-mutating.

## Reconciliation

- Defined in code: 117 canonical IDs.
- Eligible for a package: controlled by source extraction, questionnaire traversal, and 32 direct conditional suppressions.
- Actually presented: not derivable globally from definitions; the UI/CLI renderer and persisted state determine candidates.
- Included in unanswered export: only answer-kind items in `needs_answer`.
- Counted unresolved for sealing: `completion_summary` uses UNKNOWN, TO_BE_INSPECTED, or empty non-deferred/non-NA values, independently of the UI export.

## Shared verbatim rendering

Every terminal question appends: `Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.` and `Do not enter secrets, credentials, tokens, keys, or sensitive payloads.` The JSON resolves all group meaning, example, review scaffold, downstream effects, and missing-summary text per entry.

## Complete catalogue

### AC-SET: Acceptance criteria

- Group: Acceptance criteria
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Records can block validation when accepted/passed references, evidence, authority, or conflicts violate validation rules.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Acceptance-criterion rows
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Define how a requirement will be shown to pass or fail.", "what_this_question_means": "Define how a requirement will be shown to pass or fail.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What must be true before a requirement can be treated as accepted.", "answer_scaffold": "Pass condition:\n- ...\n\nFail condition:\n- ...\n\nEvidence required:\n- ...", "downstream_effects": ["Determines what evidence can satisfy a requirement.", "Affects evidence-sensitive gaps and gate readiness."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "requirement_ids", "exact_display_label": "Linked requirement IDs", "supporting_explanation": {"what_this_question_means": "Provide the linked requirement ids for this acceptance criteria record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "pass_condition", "exact_display_label": "Pass condition", "supporting_explanation": {"what_this_question_means": "Provide the pass condition for this acceptance criteria record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "validation_method", "exact_display_label": "Validation method", "supporting_explanation": {"what_this_question_means": "Provide the validation method for this acceptance criteria record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "expected_evidence", "exact_display_label": "Expected evidence", "supporting_explanation": {"what_this_question_means": "Provide the expected evidence for this acceptance criteria record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "evidence_ids", "exact_display_label": "Evidence IDs", "supporting_explanation": {"what_this_question_means": "Provide the evidence ids for this acceptance criteria record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "approver", "exact_display_label": "Approver", "supporting_explanation": {"what_this_question_means": "Provide the approver for this acceptance criteria record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["ACCEPTED", "FAILED", "NOT_RUN", "PASSED", "PROPOSED"]}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "acceptance criteria"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ACT-SET: Actors

- Group: Actors
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured actors records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Identify people, roles, or systems affected by the package.", "what_this_question_means": "Identify people, roles, or systems affected by the package.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Actors.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "name", "exact_display_label": "Name", "supporting_explanation": {"what_this_question_means": "Provide the name for this actors record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "role_type", "exact_display_label": "Role type", "supporting_explanation": {"what_this_question_means": "Provide the role type for this actors record.", "example": "A specific, reviewable value."}, "choices": ["AFFECTED_PARTY", "APPROVER", "EXTERNAL_SYSTEM", "OPERATOR", "OWNER", "SUPPLIER", "USER"]}, {"name": "needs_or_responsibilities", "exact_display_label": "Needs or responsibilities", "supporting_explanation": {"what_this_question_means": "Provide the needs or responsibilities for this actors record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "decision_authority", "exact_display_label": "Decision authority", "supporting_explanation": {"what_this_question_means": "Provide the decision authority for this actors record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "actors"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ARC-SET: Components

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured components records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Components.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "component", "exact_display_label": "Component", "supporting_explanation": {"what_this_question_means": "Provide the component for this components record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "responsibility", "exact_display_label": "Responsibility", "supporting_explanation": {"what_this_question_means": "Provide the responsibility for this components record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "inputs", "exact_display_label": "Inputs", "supporting_explanation": {"what_this_question_means": "Provide the inputs for this components record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "outputs", "exact_display_label": "Outputs", "supporting_explanation": {"what_this_question_means": "Provide the outputs for this components record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "state_owner", "exact_display_label": "State owner", "supporting_explanation": {"what_this_question_means": "Provide the state owner for this components record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source_evidence", "exact_display_label": "Source evidence", "supporting_explanation": {"what_this_question_means": "Provide the source evidence for this components record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "confidence", "exact_display_label": "Confidence", "supporting_explanation": {"what_this_question_means": "Provide the confidence for this components record.", "example": "A specific, reviewable value."}, "choices": ["HIGH", "LOW", "MEDIUM"]}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "components"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ART-SET: Artifact index

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Artifact index.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "exact_path_or_reference", "exact_display_label": "Exact path or reference", "supporting_explanation": {"what_this_question_means": "Provide the exact path or reference for this artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "purpose", "exact_display_label": "Purpose", "supporting_explanation": {"what_this_question_means": "Provide the purpose for this artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "provenance", "exact_display_label": "Provenance", "supporting_explanation": {"what_this_question_means": "Provide the provenance for this artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "authority", "exact_display_label": "Authority", "supporting_explanation": {"what_this_question_means": "Provide the authority for this artifacts record.", "example": "A specific, reviewable value."}, "choices": ["AUTHORITATIVE", "EXPLORATORY", "SUPPORTING"]}, {"name": "authority_basis", "exact_display_label": "Authority basis", "supporting_explanation": {"what_this_question_means": "Provide the authority basis for this artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["CURRENT", "DRAFT", "RESTRICTED", "STALE", "SUPERSEDED", "UNVERIFIED"]}, {"name": "last_validated_date", "exact_display_label": "Last validated date", "supporting_explanation": {"what_this_question_means": "Provide the last validated date for this artifacts record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "artifacts"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ARTQ-001: Excluded artifacts

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PURPOSE_UNCLEAR`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Excluded artifacts.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "path_or_description", "exact_display_label": "Path or description", "supporting_explanation": {"what_this_question_means": "Provide the path or description for this exclusions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "exclusion_reason", "exact_display_label": "Exclusion reason", "supporting_explanation": {"what_this_question_means": "Provide the exclusion reason for this exclusions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "reason_code", "exact_display_label": "Reason code", "supporting_explanation": {"what_this_question_means": "Provide the reason code for this exclusions record.", "example": "A specific, reviewable value."}, "choices": ["PROHIBITED_PATH", "RESTRICTED", "UNAVAILABLE", "UNRELATED", "UNSEALED", "WEAK_RELATIONSHIP", "WRONG_PROJECT", "WRONG_SNAPSHOT"]}, {"name": "impact", "exact_display_label": "Impact", "supporting_explanation": {"what_this_question_means": "Provide the impact for this exclusions record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "exclusions"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ASM-SET: Assumptions

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured assumptions records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Assumptions.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "assumption", "exact_display_label": "Assumption", "supporting_explanation": {"what_this_question_means": "Provide the assumption for this assumptions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "impact_if_wrong", "exact_display_label": "Impact if wrong", "supporting_explanation": {"what_this_question_means": "Provide the impact if wrong for this assumptions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "validation_method", "exact_display_label": "Validation method", "supporting_explanation": {"what_this_question_means": "Provide the validation method for this assumptions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "owner", "exact_display_label": "Owner", "supporting_explanation": {"what_this_question_means": "Name the person or role responsible for this item or its follow-up.", "example": "Product owner or Security reviewer."}, "choices": []}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["INVALIDATED", "OPEN", "VALIDATED"]}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "assumptions"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### AUT-001: Current authority state

- Group: Authority
- Answer type: ENUM
- Choices: ["CLOSEOUT_ONLY", "DESIGN_ONLY", "DISCOVERY_ONLY", "IMPLEMENTATION_WITHIN_EXACT_SCOPE", "NONE", "NOT_EVALUATED", "REVIEW_ONLY"]
- Required status: required
- Blocking effect: IMPLEMENTATION_WITHIN_EXACT_SCOPE adds phase/criteria/recovery gates; sealing requires authority exactly NONE.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts authority defaults to NOT_EVALUATED
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record authority that already exists. Selecting a value records it; it does not grant any permission.", "example": "DISCOVERY_ONLY, REVIEW_ONLY, or NONE when no authority has been granted.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### AUT-002: Authorizer and role

- Group: Authority
- Answer type: SHORT_TEXT
- Choices: []
- Required status: conditional
- Blocking effect: Blocks validation when AUT-001 claims authority and this answer is absent.
- Trigger: AUT-001 claims authority other than NONE or NOT_EVALUATED
- Suppression condition: AUT-001 is NONE, NOT_EVALUATED, or absent
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Authorizer and role", "variables": {}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### AUT-003: Recorded authority source

- Group: Authority
- Answer type: PATH_OR_URI
- Choices: []
- Required status: conditional
- Blocking effect: Blocks validation when AUT-001 claims authority and this answer is absent.
- Trigger: AUT-001 claims authority other than NONE or NOT_EVALUATED
- Suppression condition: AUT-001 is NONE, NOT_EVALUATED, or absent
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A relative path, repository URL, or other durable reference.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Recorded authority source", "variables": {}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### AUT-004: Exact authorized scope

- Group: Authority
- Answer type: LONG_TEXT
- Choices: []
- Required status: conditional
- Blocking effect: Blocks validation when AUT-001 claims authority and this answer is absent.
- Trigger: AUT-001 claims authority other than NONE or NOT_EVALUATED
- Suppression condition: AUT-001 is NONE, NOT_EVALUATED, or absent
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Exact authorized scope", "variables": {}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### AUT-005: Authority exclusions

- Group: Authority
- Answer type: LONG_TEXT
- Choices: []
- Required status: conditional
- Blocking effect: Blocks validation when AUT-001 claims authority and this answer is absent.
- Trigger: AUT-001 claims authority other than NONE or NOT_EVALUATED
- Suppression condition: AUT-001 is NONE, NOT_EVALUATED, or absent
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Authority exclusions", "variables": {}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### AUT-006: Authority expiry or checkpoint

- Group: Authority
- Answer type: SHORT_TEXT
- Choices: []
- Required status: conditional
- Blocking effect: Blocks validation when AUT-001 claims authority and this answer is absent.
- Trigger: AUT-001 claims authority other than NONE or NOT_EVALUATED
- Suppression condition: AUT-001 is NONE, NOT_EVALUATED, or absent
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Authority expiry or checkpoint", "variables": {}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### AUT-007: Separately authorized special actions

- Group: Authority
- Answer type: MULTI_ENUM
- Choices: []
- Required status: advisory
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A comma-separated list of applicable values, or NOT_APPLICABLE.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### AUT-007-SCOPE: Special action exact scope, authorizer, source, recovery, and expiry

- Group: Authority
- Answer type: LONG_TEXT
- Choices: []
- Required status: conditional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: AUT-001 claims authority other than NONE or NOT_EVALUATED
- Suppression condition: AUT-001 is NONE, NOT_EVALUATED, or absent
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Special action exact scope, authorizer, source, recovery, and expiry", "variables": {}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### AUT-008: Active bounded contract ID and path

- Group: Authority
- Answer type: SHORT_TEXT
- Choices: []
- Required status: advisory
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### AUT-009: Escalation owner

- Group: Authority
- Answer type: SHORT_TEXT
- Choices: []
- Required status: advisory
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record existing human authority precisely; this questionnaire never creates it.", "what_this_question_means": "Record existing human authority precisely; this questionnaire never creates it.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Identify who granted permission, what permission exists, and where that authority is recorded.", "answer_scaffold": "Authority granted by:\n- ...\n\nAuthority permits:\n- ...\n\nAuthority does not permit:\n- ...\n\nRecorded in:\n- ...", "downstream_effects": ["Affects whether ArtPkg treats the package as discovery, review, or implementation-authorized work.", "Limits downstream claims that depend on human approval."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### BND-001: In scope

- Group: Scope boundary
- Answer type: LONG_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 5 in-scope bullets
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Make the included and excluded work explicit before it is handed off.", "what_this_question_means": "Name the behavior, components, or decisions this package is allowed to discuss or change.", "example": "Order validation and its public API contract.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What work this artifact package is allowed to cover.", "answer_scaffold": "This package is in scope for:\n- ...\n\nIt may discuss or change:\n- ...\n\nIt may make decisions about:\n- ...\n\nIt does not authorize:\n- ...\n\nSource basis:\n- ...", "downstream_effects": ["Prevents scope expansion when the package is handed to another reviewer or agent.", "Constrains authority, acceptance criteria, validation, and blast-radius visualization."], "missing_summary": "No explicit in-scope statement was found in the uploaded artifact. Provide a human clarification before relying on scope-sensitive downstream decisions."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### BND-002: Out of scope

- Group: Scope boundary
- Answer type: LONG_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 5 out-of-scope bullets
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Make the included and excluded work explicit before it is handed off.", "what_this_question_means": "Name nearby work that must not be treated as part of this package.", "example": "Payment processing, database migration, and deployment automation.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What nearby work must stay outside this package even if it is related.", "answer_scaffold": "This package is out of scope for:\n- ...\n\nDo not infer approval to change:\n- ...\n\nSource basis:\n- ...", "downstream_effects": ["Prevents scope expansion when the package is handed to another reviewer or agent.", "Constrains authority, acceptance criteria, validation, and blast-radius visualization."], "missing_summary": "ArtPkg did not find an explicit out-of-scope boundary in the uploaded artifact."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### BND-003: External dependencies

- Group: Scope boundary
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured external dependencies records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Make the included and excluded work explicit before it is handed off.", "what_this_question_means": "Make the included and excluded work explicit before it is handed off.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What boundary should keep this artifact package from expanding beyond its intended purpose.", "answer_scaffold": "Boundary:\n- ...\n\nIncluded:\n- ...\n\nExcluded:\n- ...\n\nSource basis:\n- ...", "downstream_effects": ["Prevents scope expansion when the package is handed to another reviewer or agent.", "Constrains authority, acceptance criteria, validation, and blast-radius visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "dependency", "exact_display_label": "Dependency", "supporting_explanation": {"what_this_question_means": "Provide the dependency for this external dependencies record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "owner", "exact_display_label": "Owner", "supporting_explanation": {"what_this_question_means": "Name the person or role responsible for this item or its follow-up.", "example": "Product owner or Security reviewer."}, "choices": []}, {"name": "required_behavior", "exact_display_label": "Required behavior", "supporting_explanation": {"what_this_question_means": "Provide the required behavior for this external dependencies record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "availability", "exact_display_label": "Availability", "supporting_explanation": {"what_this_question_means": "Provide the availability for this external dependencies record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "failure_impact", "exact_display_label": "Failure impact", "supporting_explanation": {"what_this_question_means": "Provide the failure impact for this external dependencies record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "external dependencies"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### BND-004: Prohibited shortcuts

- Group: Scope boundary
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured prohibited shortcuts records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Make the included and excluded work explicit before it is handed off.", "what_this_question_means": "Make the included and excluded work explicit before it is handed off.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What boundary should keep this artifact package from expanding beyond its intended purpose.", "answer_scaffold": "Boundary:\n- ...\n\nIncluded:\n- ...\n\nExcluded:\n- ...\n\nSource basis:\n- ...", "downstream_effects": ["Prevents scope expansion when the package is handed to another reviewer or agent.", "Constrains authority, acceptance criteria, validation, and blast-radius visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "prohibited_approach", "exact_display_label": "Prohibited approach", "supporting_explanation": {"what_this_question_means": "Provide the prohibited approach for this prohibited shortcuts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "reason", "exact_display_label": "Reason", "supporting_explanation": {"what_this_question_means": "Provide the reason for this prohibited shortcuts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "detection_method", "exact_display_label": "Detection method", "supporting_explanation": {"what_this_question_means": "Provide the detection method for this prohibited shortcuts record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "prohibited shortcuts"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### BND-005: Change surface

- Group: Scope boundary
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Make the included and excluded work explicit before it is handed off.", "what_this_question_means": "Make the included and excluded work explicit before it is handed off.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What boundary should keep this artifact package from expanding beyond its intended purpose.", "answer_scaffold": "Boundary:\n- ...\n\nIncluded:\n- ...\n\nExcluded:\n- ...\n\nSource basis:\n- ...", "downstream_effects": ["Prevents scope expansion when the package is handed to another reviewer or agent.", "Constrains authority, acceptance criteria, validation, and blast-radius visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "path_or_component", "exact_display_label": "Path, component, interface, or process", "supporting_explanation": {"what_this_question_means": "Provide the path, component, interface, or process for this change surface record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "reason", "exact_display_label": "Why it may change", "supporting_explanation": {"what_this_question_means": "Provide the why it may change for this change surface record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "change surface"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### BND-006: Preserve surface

- Group: Scope boundary
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Make the included and excluded work explicit before it is handed off.", "what_this_question_means": "Make the included and excluded work explicit before it is handed off.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What boundary should keep this artifact package from expanding beyond its intended purpose.", "answer_scaffold": "Boundary:\n- ...\n\nIncluded:\n- ...\n\nExcluded:\n- ...\n\nSource basis:\n- ...", "downstream_effects": ["Prevents scope expansion when the package is handed to another reviewer or agent.", "Constrains authority, acceptance criteria, validation, and blast-radius visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "surface", "exact_display_label": "Behavior, data, file, interface, or user change", "supporting_explanation": {"what_this_question_means": "Provide the behavior, data, file, interface, or user change for this preserve surface record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "reason", "exact_display_label": "Why it must remain untouched", "supporting_explanation": {"what_this_question_means": "Provide the why it must remain untouched for this preserve surface record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "preserve surface"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### CFT-SET: Source conflicts

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Records can block validation when accepted/passed references, evidence, authority, or conflicts violate validation rules.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Source conflicts.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "source_a", "exact_display_label": "Source A", "supporting_explanation": {"what_this_question_means": "Provide the source a for this conflicts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source_b", "exact_display_label": "Source B", "supporting_explanation": {"what_this_question_means": "Provide the source b for this conflicts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "conflict", "exact_display_label": "Conflict", "supporting_explanation": {"what_this_question_means": "Provide the conflict for this conflicts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "impact", "exact_display_label": "Impact", "supporting_explanation": {"what_this_question_means": "Provide the impact for this conflicts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "resolution_owner", "exact_display_label": "Resolution owner", "supporting_explanation": {"what_this_question_means": "Provide the resolution owner for this conflicts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["OPEN", "RESOLVED"]}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "conflicts"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### DAT-001: Data lineage

- Group: Data
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Describe data handling, lineage, and retention constraints.", "what_this_question_means": "Describe data handling, lineage, and retention constraints.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Data lineage.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### DAT-002: Retention and expiry

- Group: Data
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Describe data handling, lineage, and retention constraints.", "what_this_question_means": "Describe data handling, lineage, and retention constraints.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Retention and expiry.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### DAT-SET: Inputs and outputs

- Group: Data
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Describe data handling, lineage, and retention constraints.", "what_this_question_means": "Describe data handling, lineage, and retention constraints.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Inputs and outputs.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "direction", "exact_display_label": "Direction", "supporting_explanation": {"what_this_question_means": "Provide the direction for this data record.", "example": "A specific, reviewable value."}, "choices": ["INPUT", "OUTPUT"]}, {"name": "name", "exact_display_label": "Name", "supporting_explanation": {"what_this_question_means": "Provide the name for this data record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "format_or_schema", "exact_display_label": "Format or schema", "supporting_explanation": {"what_this_question_means": "Provide the format or schema for this data record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "producer", "exact_display_label": "Producer", "supporting_explanation": {"what_this_question_means": "Provide the producer for this data record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "consumer", "exact_display_label": "Consumer", "supporting_explanation": {"what_this_question_means": "Provide the consumer for this data record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "trust_classification", "exact_display_label": "Trust classification", "supporting_explanation": {"what_this_question_means": "Provide the trust classification for this data record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "sample_reference", "exact_display_label": "Sample reference", "supporting_explanation": {"what_this_question_means": "Provide the sample reference for this data record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "validation", "exact_display_label": "Validation", "supporting_explanation": {"what_this_question_means": "Provide the validation for this data record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "data"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### DEC-SET: Decisions

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured decisions records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Decisions.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "decision", "exact_display_label": "Decision", "supporting_explanation": {"what_this_question_means": "Provide the decision for this decisions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "rationale", "exact_display_label": "Rationale", "supporting_explanation": {"what_this_question_means": "Provide the rationale for this decisions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "decider", "exact_display_label": "Decider", "supporting_explanation": {"what_this_question_means": "Provide the decider for this decisions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "date", "exact_display_label": "Date", "supporting_explanation": {"what_this_question_means": "Provide the date for this decisions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "evidence", "exact_display_label": "Evidence", "supporting_explanation": {"what_this_question_means": "Reference evidence that supports this record and note its limits elsewhere when needed.", "example": "EVD-001 or a durable source reference."}, "choices": []}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["ACCEPTED", "PROPOSED", "SUPERSEDED"]}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "decisions"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ENV-001: Runtime and platforms

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Runtime and platforms.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "item", "exact_display_label": "Item", "supporting_explanation": {"what_this_question_means": "Provide the item for this environment record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "version", "exact_display_label": "Version", "supporting_explanation": {"what_this_question_means": "Provide the version for this environment record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "purpose", "exact_display_label": "Purpose", "supporting_explanation": {"what_this_question_means": "Provide the purpose for this environment record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source", "exact_display_label": "Source", "supporting_explanation": {"what_this_question_means": "Identify where this information came from; it is not automatically an approval.", "example": "A human declaration, policy reference, or evidence ID."}, "choices": []}, {"name": "required_or_observed", "exact_display_label": "Required or observed", "supporting_explanation": {"what_this_question_means": "Provide the required or observed for this environment record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "environment"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ENV-002: Tools and dependencies

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Tools and dependencies.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "dependency", "exact_display_label": "Dependency", "supporting_explanation": {"what_this_question_means": "Provide the dependency for this dependencies record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "version_or_constraint", "exact_display_label": "Version or constraint", "supporting_explanation": {"what_this_question_means": "Provide the version or constraint for this dependencies record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source", "exact_display_label": "Source", "supporting_explanation": {"what_this_question_means": "Identify where this information came from; it is not automatically an approval.", "example": "A human declaration, policy reference, or evidence ID."}, "choices": []}, {"name": "purpose", "exact_display_label": "Purpose", "supporting_explanation": {"what_this_question_means": "Provide the purpose for this dependencies record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "availability", "exact_display_label": "Availability", "supporting_explanation": {"what_this_question_means": "Provide the availability for this dependencies record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "license_or_access_concern", "exact_display_label": "License or access concern", "supporting_explanation": {"what_this_question_means": "Provide the license or access concern for this dependencies record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "dependencies"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ENV-003: Configuration locations

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Configuration locations.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "path_or_source", "exact_display_label": "Path or source", "supporting_explanation": {"what_this_question_means": "Provide the path or source for this configuration record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "purpose", "exact_display_label": "Purpose", "supporting_explanation": {"what_this_question_means": "Provide the purpose for this configuration record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "authoritative_status", "exact_display_label": "Authoritative status", "supporting_explanation": {"what_this_question_means": "Provide the authoritative status for this configuration record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "configuration"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ENV-004: Build commands

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Build commands.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "command", "exact_display_label": "Command", "supporting_explanation": {"what_this_question_means": "Provide the command for this build commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "working_directory", "exact_display_label": "Working directory", "supporting_explanation": {"what_this_question_means": "Provide the working directory for this build commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "expected_result", "exact_display_label": "Expected result", "supporting_explanation": {"what_this_question_means": "Provide the expected result for this build commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source", "exact_display_label": "Source", "supporting_explanation": {"what_this_question_means": "Identify where this information came from; it is not automatically an approval.", "example": "A human declaration, policy reference, or evidence ID."}, "choices": []}, {"name": "last_observed_date", "exact_display_label": "Last observed date", "supporting_explanation": {"what_this_question_means": "Provide the last observed date for this build commands record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "build commands"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ENV-005: Test and lint commands

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Test and lint commands.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "command", "exact_display_label": "Command", "supporting_explanation": {"what_this_question_means": "Provide the command for this test commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "working_directory", "exact_display_label": "Working directory", "supporting_explanation": {"what_this_question_means": "Provide the working directory for this test commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "expected_result", "exact_display_label": "Expected result", "supporting_explanation": {"what_this_question_means": "Provide the expected result for this test commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source", "exact_display_label": "Source", "supporting_explanation": {"what_this_question_means": "Identify where this information came from; it is not automatically an approval.", "example": "A human declaration, policy reference, or evidence ID."}, "choices": []}, {"name": "last_observed_date", "exact_display_label": "Last observed date", "supporting_explanation": {"what_this_question_means": "Provide the last observed date for this test commands record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "test commands"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### ENV-006: Runtime verification commands

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Runtime verification commands.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "command_or_step", "exact_display_label": "Command or step", "supporting_explanation": {"what_this_question_means": "Provide the command or step for this runtime commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "controlled_input", "exact_display_label": "Controlled input", "supporting_explanation": {"what_this_question_means": "Provide the controlled input for this runtime commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "expected_observation", "exact_display_label": "Expected observation", "supporting_explanation": {"what_this_question_means": "Provide the expected observation for this runtime commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "environment", "exact_display_label": "Environment", "supporting_explanation": {"what_this_question_means": "Provide the environment for this runtime commands record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "evidence_location", "exact_display_label": "Evidence location", "supporting_explanation": {"what_this_question_means": "Provide the evidence location for this runtime commands record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "runtime commands"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### EVD-SET: Evidence ledger

- Group: Evidence
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Records can block validation when accepted/passed references, evidence, authority, or conflicts violate validation rules.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured evidence records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record what was observed, where it came from, and its limitations.", "what_this_question_means": "Record what was observed, where it came from, and its limitations.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What evidence supports a claim, where it came from, and what it does not prove.", "answer_scaffold": "Evidence observed:\n- ...\n\nSource location:\n- ...\n\nSupports this claim:\n- ...\n\nLimitations:\n- ...", "downstream_effects": ["Controls whether claims are backed by inspectable source material.", "Affects confidence in acceptance and validation results."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "claim_tested", "exact_display_label": "Claim tested", "supporting_explanation": {"what_this_question_means": "Provide the claim tested for this evidence record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "evidence_type", "exact_display_label": "Evidence type", "supporting_explanation": {"what_this_question_means": "Provide the evidence type for this evidence record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "exact_source_or_command", "exact_display_label": "Exact source, path, or command", "supporting_explanation": {"what_this_question_means": "Provide the exact source, path, or command for this evidence record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "expected_result", "exact_display_label": "Expected result", "supporting_explanation": {"what_this_question_means": "Provide the expected result for this evidence record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "observed_result", "exact_display_label": "Observed result", "supporting_explanation": {"what_this_question_means": "Provide the observed result for this evidence record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "result", "exact_display_label": "Result", "supporting_explanation": {"what_this_question_means": "Provide the result for this evidence record.", "example": "A specific, reviewable value."}, "choices": ["FAIL", "NOT_RUN", "PARTIAL", "PASS"]}, {"name": "date", "exact_display_label": "Date", "supporting_explanation": {"what_this_question_means": "Provide the date for this evidence record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "limitations", "exact_display_label": "Limitations", "supporting_explanation": {"what_this_question_means": "Provide the limitations for this evidence record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "evidence"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### FC-SET: Failure, denial, and misuse cases

- Group: Failure cases
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured failure cases records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Applicability and acceptable safety handling require human judgment; extraction is not approval.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CONDITIONAL_SAFETY`
- Exact supporting explanation: {"group_description": "Record unsafe conditions and the required fail-closed or recovery behavior.", "what_this_question_means": "Record unsafe conditions and the required fail-closed or recovery behavior.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Failure, denial, and misuse cases.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "condition", "exact_display_label": "Condition", "supporting_explanation": {"what_this_question_means": "Provide the condition for this failure cases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "required_safe_behavior", "exact_display_label": "Required safe behavior", "supporting_explanation": {"what_this_question_means": "Provide the required safe behavior for this failure cases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "recovery_or_abstention", "exact_display_label": "Recovery or abstention behavior", "supporting_explanation": {"what_this_question_means": "Provide the recovery or abstention behavior for this failure cases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "evidence_needed", "exact_display_label": "Evidence needed", "supporting_explanation": {"what_this_question_means": "Provide the evidence needed for this failure cases record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "failure cases"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### FIN-001: Completeness review

- Group: Final review
- Answer type: BOOLEAN
- Choices: ["NO", "YES"]
- Required status: required
- Blocking effect: Blocks validate_answers and sealing unless YES.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Confirm completion, sensitive-content, and authority checks before generation.", "what_this_question_means": "Confirm completion, sensitive-content, and authority checks before generation.", "example": "YES or NO.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Completeness review.", "answer_scaffold": "Select the truthful value for Completeness review. Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### FIN-002: Secret and sensitive-content review

- Group: Final review
- Answer type: BOOLEAN
- Choices: ["NO", "YES"]
- Required status: required
- Blocking effect: Blocks validate_answers and sealing unless YES.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Confirm completion, sensitive-content, and authority checks before generation.", "what_this_question_means": "Confirm completion, sensitive-content, and authority checks before generation.", "example": "YES or NO.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Secret and sensitive-content review.", "answer_scaffold": "Select the truthful value for Secret and sensitive-content review. Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### FIN-003: Authority review

- Group: Final review
- Answer type: BOOLEAN
- Choices: ["NO", "YES"]
- Required status: required
- Blocking effect: Blocks validate_answers and sealing unless YES.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Confirm completion, sensitive-content, and authority checks before generation.", "what_this_question_means": "Confirm completion, sensitive-content, and authority checks before generation.", "example": "YES or NO.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Authority review.", "answer_scaffold": "Select the truthful value for Authority review. Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### FIN-004: Generate outputs

- Group: Final review
- Answer type: BOOLEAN
- Choices: ["NO", "YES"]
- Required status: advisory
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Confirm completion, sensitive-content, and authority checks before generation.", "what_this_question_means": "Confirm completion, sensitive-content, and authority checks before generation.", "example": "YES or NO.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Generate outputs.", "answer_scaffold": "Select the truthful value for Generate outputs. Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### FR-SET: Functional requirements

- Group: Functional requirements
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Functional requirement rows
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Record a human-owned behavior the project must provide.", "what_this_question_means": "Record a human-owned behavior the project must provide.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Functional requirements.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "requirement", "exact_display_label": "Requirement text", "supporting_explanation": {"what_this_question_means": "Provide the requirement text for this functional requirements record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source", "exact_display_label": "Source", "supporting_explanation": {"what_this_question_means": "Identify where this information came from; it is not automatically an approval.", "example": "A human declaration, policy reference, or evidence ID."}, "choices": []}, {"name": "priority", "exact_display_label": "Priority", "supporting_explanation": {"what_this_question_means": "Provide the priority for this functional requirements record.", "example": "A specific, reviewable value."}, "choices": ["COULD", "MUST", "SHOULD"]}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["ACCEPTED", "IMPLEMENTED", "PROPOSED", "VERIFIED"]}, {"name": "decision_owner", "exact_display_label": "Decision owner", "supporting_explanation": {"what_this_question_means": "Provide the decision owner for this functional requirements record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "functional requirements"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-000: SDLC Harness: HAR-000

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: ["NO", "YES"]
- Required status: optional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Choose whether this package will be consumed by the SDLC Harness. YES reveals its state questions; NO keeps them out of scope.", "example": "YES only when the package is actually intended for that workflow.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-000.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-000"}, "allowed_values": ["NO", "YES"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-001: SDLC Harness: HAR-001

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: ["BEC_CONSIDERATION", "CHECKPOINT_REVIEW", "CLOSEOUT", "DISCOVERY", "IMPLEMENTATION_HANDOFF", "INTAKE", "PLANNING", "RECONCILIATION"]
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-001.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-001"}, "allowed_values": ["BEC_CONSIDERATION", "CHECKPOINT_REVIEW", "CLOSEOUT", "DISCOVERY", "IMPLEMENTATION_HANDOFF", "INTAKE", "PLANNING", "RECONCILIATION"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-002: SDLC Harness: HAR-002

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: ["CHANGED_SNAPSHOT_RECONCILIATION", "CHECKPOINT_UPDATE", "NEW_PROJECT_INTAKE", "RESUMED_PROJECT"]
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-002.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-002"}, "allowed_values": ["CHANGED_SNAPSHOT_RECONCILIATION", "CHECKPOINT_UPDATE", "NEW_PROJECT_INTAKE", "RESUMED_PROJECT"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-003: SDLC Harness: HAR-003

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-003.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-003"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-004: SDLC Harness: HAR-004

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-004.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-004"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-005: SDLC Harness: HAR-005

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-005.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-005"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-006: SDLC Harness: HAR-006

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-006.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-006"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-007: SDLC Harness: HAR-007

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-007.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-007"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-008: SDLC Harness: HAR-008

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-008.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-008"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-009: SDLC Harness: HAR-009

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-009.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-009"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-010: SDLC Harness: HAR-010

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: ["CONTRADICTORY", "NOT_VERIFIED", "PARTIAL", "UNAVAILABLE", "VERIFIED"]
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-010.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-010"}, "allowed_values": ["CONTRADICTORY", "NOT_VERIFIED", "PARTIAL", "UNAVAILABLE", "VERIFIED"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-011: SDLC Harness: HAR-011

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: ["COMPLETE_WITHIN_BOUNDARY", "CONTRADICTORY", "EMPTY", "NOISY", "NOT_RUN", "PARTIAL", "STALE"]
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-011.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-011"}, "allowed_values": ["COMPLETE_WITHIN_BOUNDARY", "CONTRADICTORY", "EMPTY", "NOISY", "NOT_RUN", "PARTIAL", "STALE"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-012: SDLC Harness: HAR-012

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-012.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-012"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-013: SDLC Harness: HAR-013

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-013.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-013"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-014: SDLC Harness: HAR-014

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-014.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-014"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-015: SDLC Harness: HAR-015

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-015.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-015"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-016: SDLC Harness: HAR-016

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-016.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-016"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-017: SDLC Harness: HAR-017

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-017.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-017"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-018: SDLC Harness: HAR-018

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-018.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-018"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-019: SDLC Harness: HAR-019

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-019.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-019"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-020: SDLC Harness: HAR-020

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-020.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-020"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-021: SDLC Harness: HAR-021

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-021.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-021"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-022: SDLC Harness: HAR-022

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-022.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-022"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-023: SDLC Harness: HAR-023

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-023.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-023"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HAR-024: SDLC Harness: HAR-024

- Group: SDLC Harness
- Answer type: HARNESS
- Choices: []
- Required status: conditional
- Blocking effect: Conditional Harness validation and transition rules can block when enabled.
- Trigger: HAR-000 = YES / setup.harness_enabled is true
- Suppression condition: HAR-000 is NO / setup.harness_enabled is false
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Record pipeline state only; recording it does not authorize implementation or execution.", "what_this_question_means": "Record pipeline state only; recording it does not authorize implementation or execution.", "example": "A documented pipeline state backed by the appropriate human decision or evidence.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for SDLC Harness: HAR-024.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "SDLC Harness: {question_id}", "variables": {"question_id": "HAR-024"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HND-001: Checkpoint classification

- Group: Handoff
- Answer type: ENUM
- Choices: ["ACCEPTED", "ACCEPTED_WITH_CHANGES", "BLOCKED_AT_HUMAN_CHECKPOINT", "DEFERRED", "NEEDS_MORE_EVIDENCE", "NEEDS_REVISION", "NOT_EVALUATED", "REJECTED"]
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "Choose one listed value, or use UNKNOWN or NOT_APPLICABLE when that is truthful.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Checkpoint classification.", "answer_scaffold": "Select the truthful value for Checkpoint classification. Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### HND-002: Classification reason

- Group: Handoff
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Lifecycle progression requires a human checkpoint decision.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Classification reason.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### HND-003: Changed artifacts

- Group: Handoff
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Lifecycle progression requires a human checkpoint decision.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Changed artifacts.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "exact_path", "exact_display_label": "Exact path", "supporting_explanation": {"what_this_question_means": "Provide the exact path for this changed artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "change_summary", "exact_display_label": "Change summary", "supporting_explanation": {"what_this_question_means": "Provide the change summary for this changed artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "expected_or_unexpected", "exact_display_label": "Expected or unexpected", "supporting_explanation": {"what_this_question_means": "Provide the expected or unexpected for this changed artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "phase_ids", "exact_display_label": "Related phase IDs", "supporting_explanation": {"what_this_question_means": "Provide the related phase ids for this changed artifacts record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "requirement_ids", "exact_display_label": "Related requirement IDs", "supporting_explanation": {"what_this_question_means": "Provide the related requirement ids for this changed artifacts record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "changed artifacts"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HND-004: Deviations

- Group: Handoff
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Lifecycle progression requires a human checkpoint decision.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Deviations.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "deviation", "exact_display_label": "Deviation", "supporting_explanation": {"what_this_question_means": "Provide the deviation for this deviations record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "reason", "exact_display_label": "Reason", "supporting_explanation": {"what_this_question_means": "Provide the reason for this deviations record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "impact", "exact_display_label": "Impact", "supporting_explanation": {"what_this_question_means": "Provide the impact for this deviations record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "disposition", "exact_display_label": "Disposition", "supporting_explanation": {"what_this_question_means": "Provide the disposition for this deviations record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "approver", "exact_display_label": "Approver if accepted", "supporting_explanation": {"what_this_question_means": "Provide the approver if accepted for this deviations record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "deviations"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### HND-005: Residual risks and limitations

- Group: Handoff
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Lifecycle progression requires a human checkpoint decision.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Residual risks and limitations.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### HND-006: Working-state observations

- Group: Handoff
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Lifecycle progression requires a human checkpoint decision.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Working-state observations.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### HND-007: Next permitted action

- Group: Handoff
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Lifecycle progression requires a human checkpoint decision.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Next permitted action.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### HND-008: Required approver

- Group: Handoff
- Answer type: SHORT_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Can be named by Harness execution support and phase checkpoint blockers.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Required approver.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### HND-009: Fresh-session instruction

- Group: Handoff
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Lifecycle progression requires a human checkpoint decision.
- Applicable maturity: ["validation", "release"]
- Applicable package purpose: ["HANDOFF", "REVIEW", "CLOSEOUT"]
- Applicable lifecycle stage: ["review", "sealing"]
- Assessment label: `LATER_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Prepare a truthful checkpoint for the next human reviewer.", "what_this_question_means": "Prepare a truthful checkpoint for the next human reviewer.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Fresh-session instruction.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### INT-SET: Interfaces

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Interfaces.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "interface_type", "exact_display_label": "Interface type", "supporting_explanation": {"what_this_question_means": "Provide the interface type for this interfaces record.", "example": "A specific, reviewable value."}, "choices": ["API", "CLI", "DATABASE", "EVENT", "FILE", "HUMAN_STEP", "OTHER", "UI"]}, {"name": "producer", "exact_display_label": "Producer", "supporting_explanation": {"what_this_question_means": "Provide the producer for this interfaces record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "consumer", "exact_display_label": "Consumer", "supporting_explanation": {"what_this_question_means": "Provide the consumer for this interfaces record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "contract_or_format", "exact_display_label": "Contract or format", "supporting_explanation": {"what_this_question_means": "Provide the contract or format for this interfaces record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "failure_behavior", "exact_display_label": "Failure behavior", "supporting_explanation": {"what_this_question_means": "Provide the failure behavior for this interfaces record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source", "exact_display_label": "Source", "supporting_explanation": {"what_this_question_means": "Identify where this information came from; it is not automatically an approval.", "example": "A human declaration, policy reference, or evidence ID."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "interfaces"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### NFR-SET: Non-functional requirements

- Group: Non-functional requirements
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Non-functional requirement rows
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Record measurable quality, operational, or policy constraints.", "what_this_question_means": "Record measurable quality, operational, or policy constraints.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Non-functional requirements.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "category", "exact_display_label": "Category", "supporting_explanation": {"what_this_question_means": "Provide the category for this non functional requirements record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "requirement", "exact_display_label": "Requirement", "supporting_explanation": {"what_this_question_means": "Provide the requirement for this non functional requirements record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "measurement", "exact_display_label": "Measurement or threshold", "supporting_explanation": {"what_this_question_means": "Provide the measurement or threshold for this non functional requirements record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source", "exact_display_label": "Source", "supporting_explanation": {"what_this_question_means": "Identify where this information came from; it is not automatically an approval.", "example": "A human declaration, policy reference, or evidence ID."}, "choices": []}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["ACCEPTED", "IMPLEMENTED", "PROPOSED", "VERIFIED"]}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "non functional requirements"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### OUT-001: Good outcome

- Group: Outcomes
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "State both the desired result and the unacceptable result to avoid.", "what_this_question_means": "State both the desired result and the unacceptable result to avoid.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Good outcome.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### OUT-002: Bad outcome

- Group: Outcomes
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "State both the desired result and the unacceptable result to avoid.", "what_this_question_means": "State both the desired result and the unacceptable result to avoid.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Bad outcome.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### OUT-003: Stop conditions

- Group: Outcomes
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Applicability and acceptable safety handling require human judgment; extraction is not approval.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CONDITIONAL_SAFETY`
- Exact supporting explanation: {"group_description": "State both the desired result and the unacceptable result to avoid.", "what_this_question_means": "State both the desired result and the unacceptable result to avoid.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Stop conditions.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "condition", "exact_display_label": "Condition", "supporting_explanation": {"what_this_question_means": "Provide the condition for this stop conditions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "detection", "exact_display_label": "Detection", "supporting_explanation": {"what_this_question_means": "Provide the detection for this stop conditions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "required_response", "exact_display_label": "Required response", "supporting_explanation": {"what_this_question_means": "Provide the required response for this stop conditions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "decision_owner", "exact_display_label": "Decision owner", "supporting_explanation": {"what_this_question_means": "Provide the decision owner for this stop conditions record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "stop conditions"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### OVR-001: Problem statement

- Group: Problem and outcome
- Answer type: LONG_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 2 problem statement
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Problem statement.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### OVR-002: Intended observable outcome

- Group: Problem and outcome
- Answer type: LONG_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 3 intended outcome
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Intended observable outcome.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### OVR-003: Completed work and linked evidence

- Group: Problem and outcome
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 4 completed work or concept-stage inference
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Completed work and linked evidence.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "OVR-003"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### OVR-004: Work in progress

- Group: Problem and outcome
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 4 work in progress or concept-stage inference
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Work in progress.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "OVR-004"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### OVR-005: Current blockers

- Group: Problem and outcome
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 4 blockers / blocking questions
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Current blockers.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "OVR-005"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### OVR-006: Deferred work

- Group: Problem and outcome
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: advisory
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Deferred work.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "OVR-006"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### OVR-007: Unverified claims

- Group: Problem and outcome
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 14 unverified content
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Unverified claims.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "OVR-007"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### OVR-008: Next proposed checkpoint

- Group: Problem and outcome
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 18 next checkpoint
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Describe the problem, intended result, and current work state.", "what_this_question_means": "Describe the problem, intended result, and current work state.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Next proposed checkpoint.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PHS-SET: Phases

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Records can block validation when accepted/passed references, evidence, authority, or conflicts violate validation rules.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CURRENT_PHASE_EVIDENCE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Phases.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "title_and_outcome", "exact_display_label": "Title and single observable outcome", "supporting_explanation": {"what_this_question_means": "Provide the title and single observable outcome for this phases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "status", "exact_display_label": "Status", "supporting_explanation": {"what_this_question_means": "Record the current state, not a hoped-for future state.", "example": "PROPOSED, OPEN, or NOT_RUN as applicable."}, "choices": ["ACCEPTED", "CLOSED", "IN_PROGRESS", "PROPOSED", "REVIEW"]}, {"name": "requirement_ids", "exact_display_label": "Linked requirement IDs", "supporting_explanation": {"what_this_question_means": "Provide the linked requirement ids for this phases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "in_scope", "exact_display_label": "In scope", "supporting_explanation": {"what_this_question_means": "Provide the in scope for this phases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "out_of_scope", "exact_display_label": "Out of scope", "supporting_explanation": {"what_this_question_means": "Provide the out of scope for this phases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "validation", "exact_display_label": "Validation commands or checks", "supporting_explanation": {"what_this_question_means": "Provide the validation commands or checks for this phases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "human_review_level", "exact_display_label": "Human-review level", "supporting_explanation": {"what_this_question_means": "Provide the human-review level for this phases record.", "example": "A specific, reviewable value."}, "choices": ["APPROVAL_REQUIRED", "NONE", "REQUIRED", "SAMPLED"]}, {"name": "rollback_or_recovery", "exact_display_label": "Rollback or recovery", "supporting_explanation": {"what_this_question_means": "Provide the rollback or recovery for this phases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "authority_source", "exact_display_label": "Authority source", "supporting_explanation": {"what_this_question_means": "Provide the authority source for this phases record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "phases"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### PKG-001: Project canonical name

- Group: Package context
- Answer type: SHORT_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Document control / project name
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Project canonical name.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-002: Package purpose

- Group: Package context
- Answer type: ENUM
- Choices: ["CLOSEOUT", "CROSS_PROJECT_TRANSFER", "DESIGN", "DISCOVERY", "IMPLEMENTATION_HANDOFF", "RESUMPTION", "REVIEW"]
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts intake purpose defaults to DISCOVERY
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "Choose one listed value, or use UNKNOWN or NOT_APPLICABLE when that is truthful.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Package purpose.", "answer_scaffold": "Select the truthful value for Package purpose. Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-003: Package owner

- Group: Package context
- Answer type: SHORT_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Document control owner candidates
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Package owner.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-004: Respondent and role

- Group: Package context
- Answer type: SHORT_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Document control prepared-by/respondent candidates
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A short, specific phrase or identifier.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Respondent and role.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-005: Repository or workspace

- Group: Package context
- Answer type: PATH_OR_URI
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Document control repository/workspace
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A relative path, repository URL, or other durable reference.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Repository or workspace.", "answer_scaffold": "Reference:\n- ...\n\nWhy this reference is the correct package context:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-006: Snapshot identity

- Group: Package context
- Answer type: SHORT_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Document control snapshot or repository NOT_CREATED
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify the exact code or document state this package describes so a later reviewer can reproduce the context.", "example": "A commit such as a1b2c3d, a release such as v0.3.0, or a dated snapshot.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Snapshot identity.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-007: Authoritative source of truth

- Group: Package context
- Answer type: PATH_OR_URI
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Uploaded Pre-Artifacts source path
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A relative path, repository URL, or other durable reference.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Authoritative source of truth.", "answer_scaffold": "Reference:\n- ...\n\nWhy this reference is the correct package context:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-007-AUTH: Who designated the source of truth and where recorded?

- Group: Package context
- Answer type: LONG_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Requesting-user source designation scaffold
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Only a human can own, grant, confirm, or attest this authority/accountability judgment.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Who designated the source of truth and where recorded?.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-008: Package coverage claim

- Group: Package context
- Answer type: LONG_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 1 primary goal / short description
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Package coverage claim.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### PKG-009: Explicit limitations

- Group: Package context
- Answer type: LONG_TEXT
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 16 package limitations / boundary statement
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Identify what this package covers and the source material it describes.", "what_this_question_means": "Identify what this package covers and the source material it describes.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Explicit limitations.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### QST-SET: Open questions

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Open-question headings, tables, or question-like source text
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Open questions.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "question", "exact_display_label": "Question", "supporting_explanation": {"what_this_question_means": "Provide the question for this questions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "why_it_matters", "exact_display_label": "Why it matters", "supporting_explanation": {"what_this_question_means": "Provide the why it matters for this questions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "decision_owner", "exact_display_label": "Decision owner", "supporting_explanation": {"what_this_question_means": "Provide the decision owner for this questions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "needed_by", "exact_display_label": "Needed by checkpoint", "supporting_explanation": {"what_this_question_means": "Provide the needed by checkpoint for this questions record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "current_disposition", "exact_display_label": "Current disposition", "supporting_explanation": {"what_this_question_means": "Provide the current disposition for this questions record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "questions"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### RSK-SET: Risks

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured risks records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Risks.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "risk", "exact_display_label": "Risk", "supporting_explanation": {"what_this_question_means": "Provide the risk for this risks record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "likelihood", "exact_display_label": "Likelihood", "supporting_explanation": {"what_this_question_means": "Provide the likelihood for this risks record.", "example": "A specific, reviewable value."}, "choices": ["HIGH", "LOW", "MEDIUM"]}, {"name": "impact", "exact_display_label": "Impact", "supporting_explanation": {"what_this_question_means": "Provide the impact for this risks record.", "example": "A specific, reviewable value."}, "choices": ["HIGH", "LOW", "MEDIUM"]}, {"name": "detection", "exact_display_label": "Detection", "supporting_explanation": {"what_this_question_means": "Provide the detection for this risks record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "mitigation_or_control", "exact_display_label": "Mitigation or control", "supporting_explanation": {"what_this_question_means": "Provide the mitigation or control for this risks record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "owner", "exact_display_label": "Owner", "supporting_explanation": {"what_this_question_means": "Name the person or role responsible for this item or its follow-up.", "example": "Product owner or Security reviewer."}, "choices": []}, {"name": "residual_status", "exact_display_label": "Residual status", "supporting_explanation": {"what_this_question_means": "Provide the residual status for this risks record.", "example": "A specific, reviewable value."}, "choices": ["ACCEPTED", "MITIGATED", "OPEN"]}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "risks"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### SEC-001: Restricted content?

- Group: Safety and security
- Answer type: BOOLEAN
- Choices: ["NO", "YES"]
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Section 19 restricted-content declaration
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Applicability and acceptable safety handling require human judgment; extraction is not approval.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CONDITIONAL_SAFETY`
- Exact supporting explanation: {"group_description": "Record restricted-content handling and safe failure behavior.", "what_this_question_means": "Indicate whether restricted or sensitive content is relevant so the follow-up safety questions can be shown only when needed.", "example": "YES for customer data or credentials; NO when none is in scope.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Whether sensitive, restricted, or safety-relevant material is involved and how it must be handled.", "answer_scaffold": "Sensitive or restricted material:\n- ...\n\nRequired handling:\n- ...\n\nControls or redactions:\n- ...", "downstream_effects": ["Affects restricted-content handling and safe failure requirements.", "May add safety, redaction, or access-control questions downstream."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### SEC-001-CATEGORIES: Restricted-content categories, allowed/prohibited locations, roles, redaction, and fail-closed behavior

- Group: Safety and security
- Answer type: LONG_TEXT
- Choices: []
- Required status: conditional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: SEC-001 = YES
- Suppression condition: SEC-001 is not YES
- Source mapping: Section 19 categories/safeguards/redaction
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Applicability and acceptable safety handling require human judgment; extraction is not approval.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CONDITIONAL_SAFETY`
- Exact supporting explanation: {"group_description": "Record restricted-content handling and safe failure behavior.", "what_this_question_means": "Record restricted-content handling and safe failure behavior.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Whether sensitive, restricted, or safety-relevant material is involved and how it must be handled.", "answer_scaffold": "Sensitive or restricted material:\n- ...\n\nRequired handling:\n- ...\n\nControls or redactions:\n- ...", "downstream_effects": ["Affects restricted-content handling and safe failure requirements.", "May add safety, redaction, or access-control questions downstream."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Restricted-content categories, allowed/prohibited locations, roles, redaction, and fail-closed behavior", "variables": {}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### SEC-002: Negative-path behavior

- Group: Safety and security
- Answer type: MULTI_ENUM
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Applicability and acceptable safety handling require human judgment; extraction is not approval.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CONDITIONAL_SAFETY`
- Exact supporting explanation: {"group_description": "Record restricted-content handling and safe failure behavior.", "what_this_question_means": "Record restricted-content handling and safe failure behavior.", "example": "A comma-separated list of applicable values, or NOT_APPLICABLE.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Whether sensitive, restricted, or safety-relevant material is involved and how it must be handled.", "answer_scaffold": "Sensitive or restricted material:\n- ...\n\nRequired handling:\n- ...\n\nControls or redactions:\n- ...", "downstream_effects": ["Affects restricted-content handling and safe failure requirements.", "May add safety, redaction, or access-control questions downstream."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### SEC-003: Rollback and recovery

- Group: Safety and security
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Blocks implementation-authorized validation when absent.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Applicability and acceptable safety handling require human judgment; extraction is not approval.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CONDITIONAL_SAFETY`
- Exact supporting explanation: {"group_description": "Record restricted-content handling and safe failure behavior.", "what_this_question_means": "Record restricted-content handling and safe failure behavior.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Whether sensitive, restricted, or safety-relevant material is involved and how it must be handled.", "answer_scaffold": "Sensitive or restricted material:\n- ...\n\nRequired handling:\n- ...\n\nControls or redactions:\n- ...", "downstream_effects": ["Affects restricted-content handling and safe failure requirements.", "May add safety, redaction, or access-control questions downstream."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### SEC-SET: Security and operational constraints

- Group: Safety and security
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Applicability and acceptable safety handling require human judgment; extraction is not approval.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `CONDITIONAL_SAFETY`
- Exact supporting explanation: {"group_description": "Record restricted-content handling and safe failure behavior.", "what_this_question_means": "Record restricted-content handling and safe failure behavior.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "Whether sensitive, restricted, or safety-relevant material is involved and how it must be handled.", "answer_scaffold": "Sensitive or restricted material:\n- ...\n\nRequired handling:\n- ...\n\nControls or redactions:\n- ...", "downstream_effects": ["Affects restricted-content handling and safe failure requirements.", "May add safety, redaction, or access-control questions downstream."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "category", "exact_display_label": "Category", "supporting_explanation": {"what_this_question_means": "Provide the category for this constraints record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "constraint", "exact_display_label": "Constraint", "supporting_explanation": {"what_this_question_means": "Provide the constraint for this constraints record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "enforcement", "exact_display_label": "Enforcement", "supporting_explanation": {"what_this_question_means": "Provide the enforcement for this constraints record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "evidence_or_status", "exact_display_label": "Evidence or status", "supporting_explanation": {"what_this_question_means": "Provide the evidence or status for this constraints record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "owner", "exact_display_label": "Owner", "supporting_explanation": {"what_this_question_means": "Name the person or role responsible for this item or its follow-up.", "example": "Product owner or Security reviewer."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "constraints"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### SET-001: Exact path to reusable_artifacts_package_template.md

- Group: Setup
- Answer type: PATH_OR_URI
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Configure the template, output location, and permitted operating mode.", "what_this_question_means": "Configure the template, output location, and permitted operating mode.", "example": "A relative path, repository URL, or other durable reference.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Exact path to reusable_artifacts_package_template.md.", "answer_scaffold": "Reference:\n- ...\n\nWhy this reference is the correct package context:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### SET-002: Where should the generated package be written?

- Group: Setup
- Answer type: PATH_OR_URI
- Choices: []
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Configure the template, output location, and permitted operating mode.", "what_this_question_means": "Configure the template, output location, and permitted operating mode.", "example": "A relative path, repository URL, or other durable reference.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Where should the generated package be written?.", "answer_scaffold": "Reference:\n- ...\n\nWhy this reference is the correct package context:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### SET-003: Output shape (COMPACT_SINGLE_FILE or STANDARD_MULTI_FILE)

- Group: Setup
- Answer type: ENUM
- Choices: ["COMPACT_SINGLE_FILE", "STANDARD_MULTI_FILE"]
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Configure the template, output location, and permitted operating mode.", "what_this_question_means": "Configure the template, output location, and permitted operating mode.", "example": "Choose one listed value, or use UNKNOWN or NOT_APPLICABLE when that is truthful.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Output shape (COMPACT_SINGLE_FILE or STANDARD_MULTI_FILE).", "answer_scaffold": "Select the truthful value for Output shape (COMPACT_SINGLE_FILE or STANDARD_MULTI_FILE). Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### SET-005: Inspection permission (NO_INSPECTION or READ_ONLY_INSPECTION)

- Group: Setup
- Answer type: ENUM
- Choices: ["NO_INSPECTION", "READ_ONLY_INSPECTION"]
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Configure the template, output location, and permitted operating mode.", "what_this_question_means": "Configure the template, output location, and permitted operating mode.", "example": "Choose one listed value, or use UNKNOWN or NOT_APPLICABLE when that is truthful.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Inspection permission (NO_INSPECTION or READ_ONLY_INSPECTION).", "answer_scaffold": "Select the truthful value for Inspection permission (NO_INSPECTION or READ_ONLY_INSPECTION). Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### SET-006: Command execution permission (DO_NOT_EXECUTE or CONFIRM_EACH_COMMAND)

- Group: Setup
- Answer type: ENUM
- Choices: ["CONFIRM_EACH_COMMAND", "DO_NOT_EXECUTE"]
- Required status: required
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["all"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PACKAGE_ADMINISTRATION`
- Exact supporting explanation: {"group_description": "Configure the template, output location, and permitted operating mode.", "what_this_question_means": "Configure the template, output location, and permitted operating mode.", "example": "Choose one listed value, or use UNKNOWN or NOT_APPLICABLE when that is truthful.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Command execution permission (DO_NOT_EXECUTE or CONFIRM_EACH_COMMAND).", "answer_scaffold": "Select the truthful value for Command execution permission (DO_NOT_EXECUTE or CONFIRM_EACH_COMMAND). Add a source basis when the value came from the uploaded artifact.", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### UC-SET: Primary use cases

- Group: Use cases
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: Pre-Artifacts structured use cases records when recognized
- Seeding behavior: Can be answered, proposed, or instantiated from uploaded source material by seed_from_pre_artifacts; confidence and review disposition remain separate from human confirmation.
- Human authority reason: Source extraction can propose content, but a human must confirm truth, scope, and completeness.
- Applicable maturity: ["concept", "requirements", "existing-system change"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `SOURCE_SEEDABLE`
- Exact supporting explanation: {"group_description": "Record a concrete user or system interaction and its observable outcome.", "what_this_question_means": "Record a concrete user or system interaction and its observable outcome.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Primary use cases.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "actor_id", "exact_display_label": "Actor ID", "supporting_explanation": {"what_this_question_means": "Provide the actor id for this use cases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "trigger", "exact_display_label": "Trigger", "supporting_explanation": {"what_this_question_means": "Provide the trigger for this use cases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "behavior", "exact_display_label": "Expected behavior", "supporting_explanation": {"what_this_question_means": "Provide the expected behavior for this use cases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "outcome", "exact_display_label": "Observable outcome", "supporting_explanation": {"what_this_question_means": "Provide the observable outcome for this use cases record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "frequency_or_importance", "exact_display_label": "Frequency or importance", "supporting_explanation": {"what_this_question_means": "Provide the frequency or importance for this use cases record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "use cases"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: seed_from_pre_artifacts and extraction helpers", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### VAL-001: Generation evidence

- Group: Questionnaire
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What validation has been performed and what remains unchecked.", "answer_scaffold": "Validated by:\n- ...\n\nResult:\n- ...\n\nStill unverified:\n- ...", "downstream_effects": ["Affects whether the package can claim the behavior has been checked.", "Changes readiness and downstream handoff risk."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### VAL-002: Verification evidence

- Group: Questionnaire
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What validation has been performed and what remains unchecked.", "answer_scaffold": "Validated by:\n- ...\n\nResult:\n- ...\n\nStill unverified:\n- ...", "downstream_effects": ["Affects whether the package can claim the behavior has been checked.", "Changes readiness and downstream handoff risk."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### VAL-003: Understanding evidence

- Group: Questionnaire
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What validation has been performed and what remains unchecked.", "answer_scaffold": "Validated by:\n- ...\n\nResult:\n- ...\n\nStill unverified:\n- ...", "downstream_effects": ["Affects whether the package can claim the behavior has been checked.", "Changes readiness and downstream handoff risk."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### VAL-004: Negative evidence

- Group: Questionnaire
- Answer type: LONG_TEXT
- Choices: []
- Required status: optional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "A concise explanation with enough detail for a later reviewer.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What validation has been performed and what remains unchecked.", "answer_scaffold": "Validated by:\n- ...\n\nResult:\n- ...\n\nStill unverified:\n- ...", "downstream_effects": ["Affects whether the package can claim the behavior has been checked.", "Changes readiness and downstream handoff risk."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]

### VAL-005: Reproducibility observations

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: advisory
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: Questionnaire reaches this catalogue entry or the entry is instantiated by seeding/review state
- Suppression condition: NONE
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: No current Pre-Artifacts source mapping was found; entered by a human or later workflow.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["implementation", "validation", "release"]
- Applicable package purpose: ["DISCOVERY", "REQUIREMENTS", "CHANGE", "HANDOFF", "REVIEW", "RESUMPTION", "CLOSEOUT"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `DUPLICATE_OR_OVERLAPPING`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What validation has been performed and what remains unchecked.", "answer_scaffold": "Validated by:\n- ...\n\nResult:\n- ...\n\nStill unverified:\n- ...", "downstream_effects": ["Affects whether the package can claim the behavior has been checked.", "Changes readiness and downstream handoff risk."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: []
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "VAL-005"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

### XFR-SET: Cross-project transfer items

- Group: Questionnaire
- Answer type: REPEATED_RECORD
- Choices: []
- Required status: conditional
- Blocking effect: Does not independently block by stable ID; it may enter needs_answer or affect a composite readiness gate.
- Trigger: PKG-002 = CROSS_PROJECT_TRANSFER
- Suppression condition: PKG-002 is not CROSS_PROJECT_TRANSFER
- Source mapping: No direct Pre-Artifacts source mapping identified
- Seeding behavior: Can be set to NOT_APPLICABLE by apply_conditionals when its trigger is false.
- Human authority reason: Human input is needed when source material is absent, uncertain, conflicting, deferred, or not authoritative.
- Applicable maturity: ["all"]
- Applicable package purpose: ["CROSS_PROJECT_TRANSFER"]
- Applicable lifecycle stage: ["intake", "review"]
- Assessment label: `PURPOSE_UNCLEAR`
- Exact supporting explanation: {"group_description": "Provide the information needed to make this package reviewable.", "what_this_question_means": "Provide the information needed to make this package reviewable.", "example": "Type add to enter one record, then done when there are no more records to add.", "terminal_help": "Help: answer explicitly; state UNKNOWN, NOT_APPLICABLE, TO_BE_INSPECTED, or DEFERRED when appropriate.", "secret_warning": "Do not enter secrets, credentials, tokens, keys, or sensitive payloads.", "review_decision_prompt": "What human-owned answer should ArtPkg use for Cross-project transfer items.", "answer_scaffold": "Answer:\n- ...\n\nSource basis:\n- ...\n\nLimits or uncertainty:\n- ...", "downstream_effects": ["Controls whether later reviewers can treat the package as complete.", "Changes how unresolved gaps appear in the readiness visualization."], "missing_summary": "ArtPkg did not find a provided answer in the uploaded artifact. Mark it unknown, deferred, not applicable, or provide the human answer."}
- Repeated-record fields: [{"name": "item", "exact_display_label": "Item", "supporting_explanation": {"what_this_question_means": "Provide the item for this transfer items record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "source_project_and_snapshot", "exact_display_label": "Source project and snapshot", "supporting_explanation": {"what_this_question_means": "Provide the source project and snapshot for this transfer items record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "classification", "exact_display_label": "Classification", "supporting_explanation": {"what_this_question_means": "Provide the classification for this transfer items record.", "example": "A specific, reviewable value."}, "choices": ["ADAPT", "BORROW", "DO_NOT_CARRY_OVER"]}, {"name": "reason", "exact_display_label": "Reason", "supporting_explanation": {"what_this_question_means": "Provide the reason for this transfer items record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "target_project_difference", "exact_display_label": "Target-project difference", "supporting_explanation": {"what_this_question_means": "Provide the target-project difference for this transfer items record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "required_adaptation", "exact_display_label": "Required adaptation", "supporting_explanation": {"what_this_question_means": "Provide the required adaptation for this transfer items record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "required_reverification", "exact_display_label": "Required re-verification", "supporting_explanation": {"what_this_question_means": "Provide the required re-verification for this transfer items record.", "example": "A specific, reviewable value."}, "choices": []}, {"name": "prohibited_inherited_assumptions", "exact_display_label": "Prohibited inherited assumptions", "supporting_explanation": {"what_this_question_means": "Provide the prohibited inherited assumptions for this transfer items record.", "example": "A specific, reviewable value."}, "choices": []}]
- Implementation location: ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]
- Dynamic construction: {"exact_template": "Add {section_label} record, or type done:", "variables": {"section_label": "transfer items"}, "allowed_values": ["DEFERRED", "NOT_APPLICABLE", "PROVIDED", "TO_BE_INSPECTED", "UNKNOWN"], "rendering_code_path": ["tools/artifacts_package_questionnaire.py: QUESTION_CATALOG, question_guidance, format_terminal_question", "tools/artifacts_package_questionnaire.py: REPEATED_QID_TO_SECTION, RECORD_FIELDS, collect_repeated/collect_record", "tools/artifacts_package_questionnaire.py: apply_conditionals, conditional_skip_reason, should_ask_question", "tools/artpkg_intake.py: _question_context, build_review_queues"]}

## Additional dynamic and action prompts

### DYN-QST-SOURCE-{record_id}

- Exact displayed template: {question}
- Kind: source-generated open question record
- Variables: {"record_id": "stable Q-* record ID", "question": "verbatim source question text"}
- Allowed values: free text plus why_it_matters, decision_owner, needed_by, current_disposition
- Rendering code path: ["tools/artifacts_package_questionnaire.py: _extract_open_questions", "tools/artpkg_intake.py: record queue rendering"]
- Assessment label: `SOURCE_SEEDABLE`

### UI-FIN-001

- Exact displayed template: The package is complete enough for external assessment.
- Kind: final assessment checkbox mapped to FIN-001=YES
- Variables: {}
- Allowed values: ["checked", "unchecked"]
- Rendering code path: ["tools/artpkg_intake_ui.html: renderSealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`

### UI-FIN-002

- Exact displayed template: Secrets and sensitive-content handling have been reviewed.
- Kind: final assessment checkbox mapped to FIN-002=YES
- Variables: {}
- Allowed values: ["checked", "unchecked"]
- Rendering code path: ["tools/artpkg_intake_ui.html: renderSealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`

### UI-FIN-003

- Exact displayed template: This package grants no implementation authority; authority remains NONE.
- Kind: final assessment checkbox mapped to AUT-001=NONE and FIN-003=YES
- Variables: {}
- Allowed values: ["checked", "unchecked"]
- Rendering code path: ["tools/artpkg_intake_ui.html: renderSealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`

### SEAL-001

- Exact displayed template: This creates an immutable package for Pipeline-A custody and external<br>assessment. It does not authorize implementation or repository changes.
- Kind: exact sealing confirmation checkbox
- Variables: {}
- Allowed values: ["reviewed=true with exact confirmation text", "unchecked"]
- Rendering code path: ["tools/artpkg_sealed_handoff.py: CONFIRMATION_TEXT, seal_session", "tools/artpkg_intake_ui.html: renderSealing"]
- Assessment label: `CORE_AUTHORITY_OR_ATTESTATION`

### REJECT-REASON-{item_id}

- Exact displayed template: Why is this seeded item rejected?
- Kind: dynamic rejection reason prompt
- Variables: {"item_id": "answer or record stable ID"}
- Allowed values: free text; UI default is Rejected in UI
- Rendering code path: ["tools/artpkg_intake_ui.html: reject action"]
- Assessment label: `CORE_HUMAN_INTENT`

## Limitations

- Required status, maturity, package purpose, and advisory assessment label are review classifications because the implementation does not store those fields on QUESTION_CATALOG entries.
- HAR-003 through HAR-024 display only their IDs as prompts; semantic meaning is supplied indirectly by HARNESS_STATE_FIELDS/harness_state_value and transition APIs.
- No browser event log records every card actually viewed.
- Dynamic source questions have source-derived wording and therefore cannot be enumerated as a finite static text list.

Final status: `QUESTION_INVENTORY_READY_FOR_HUMAN_SCOPE_REVIEW`
