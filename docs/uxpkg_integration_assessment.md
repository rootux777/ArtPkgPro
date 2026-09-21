# UXPkg integration assessment

Compares UXPkg's actual handoff doc and schemas against ArtPkg's actual
schemas, sealed-package contract, approval model, and existing custody
precedents. No UXPkg wiring exists in this tree yet. This is analysis only.

Everything below was originally written against a prose paraphrase of
UXPkg's interface. The authoritative source has since been read directly:
`/home/rootux/UXPkg/docs/ARTPKG-HANDOFF.md`, its schemas under
`/home/rootux/UXPkg/src/ux_harness/schemas/`, and its fixtures under
`/home/rootux/UXPkg/tests/fixtures/`. The paraphrase held up field-for-field;
the additions below are what the real schema adds beyond the prose.

## What the real schema adds beyond the prose brief

`input-package.schema.json` is `additionalProperties: false` at every level —
genuinely closed, matching ArtPkg's own closed-schema philosophy
(`validate_handoff`'s `set(handoff) != required` check is the same style of
gate). One concrete difference in strictness: a requirement's `authority`
field is `{"const": "HUMAN_APPROVED"}` — schema-enforced, only one literal
value accepted, with no `MODEL_PROPOSED`/`PENDING` grade available. UXPkg
cannot be handed a partially-approved requirement at all; there is no field
to honestly mark it as such. That means the filtering has to happen before a
requirement is written into `requirements.json`, not inside it — which is
exactly what [tools/artpkg_requirement_approval.py](../tools/artpkg_requirement_approval.py)'s
`human_confirmed` boolean is for: `true` records are candidates for
inclusion, `false`/`null` records must be dropped from the adapter's output
entirely, not included with a lesser label, because the schema has no lesser
label to give them.

ID format is confirmed compatible: `common.schema.json`'s `id` def is
`^[A-Za-z][A-Za-z0-9_.-]{0,95}$`. ArtPkg's requirement IDs (`FR-001`, `NFR-003`,
...) and package IDs (`PKG-[A-F0-9]{12}`) both satisfy it without adaptation.

`requirements.json`'s `capabilities` field and `structured-v1`'s
`ux-input.schema.json` (screens/regions/components/interactions/
capability_coverage) confirm the capability-catalog gap is structural, not
just underspecified in the prose: ArtPkg's schema has no analog anywhere,
and building one is real domain modeling, not a field addition.

## Sealed package vs UXPkg's dedicated input directory

ArtPkg's sealed contract ([tools/artpkg_sealed_handoff.py](../tools/artpkg_sealed_handoff.py))
is a fixed six-file bundle:

```text
ARTPKG_HANDOFF.json
MANIFEST.json
SHA256SUMS
artifacts_package.md
artifacts_package_answers.json
artifacts_package_validation.md
```

UXPkg's brief is explicit that intake is strict and this whole bundle must
**not** land in its dedicated input directory. That rules out pointing UXPkg
at a sealed ArtPkg package directly under any framing — an extraction step is
required regardless of who owns it. `artifacts_package_answers.json` is the
only file with candidate UX content; the other five are envelope, evidence,
and validation metadata UXPkg's brief says must stay out.

## Schema fit: requirements

ArtPkg's newest answers schema ([schemas/artifacts_package_answers_v0.3.schema.json](../schemas/artifacts_package_answers_v0.3.schema.json))
is requirement-centric (`intake.requirements[]`, each with `requirement_id`,
`intended_behavior`, `requirement_confidence`, `business_or_domain_reason`,
`exclusions_non_goals`, `compatibility_constraints`), plus package-level
`human_owner`, `human_approver`, and `approval.status`
(`DRAFT` / `APPROVED_FOR_DISCOVERY` / `SCOPE_APPROVED`).

Gaps against UXPkg's requirements-input shape:

- No `type` field distinguishing requirement kinds.
- No `ux_relevant` flag anywhere in the schema.
- No semantic-capability vocabulary at all — nothing maps a requirement to
  an approved catalog of UI capabilities.
- `requirement_id` is stable within a `requirement_revision` but the schema
  has no immutability guarantee across revisions beyond `revision_lineage`,
  which UXPkg's brief would need to inspect explicitly.

None of this is a small gap to patch in the schema. Capability mapping is new
domain modeling, not a field rename.

## Schema-version fragmentation

Three schema versions coexist (`v0.1`, `v0.2`, `v0.3`). **Correction:** an
earlier revision of this document called the calculator package "the one
real sealed fixture inspected in this tree" — that was wrong. Its own trace
document says explicitly: "No package-level confirmation, FIN answer,
sealing event, or sealed package directory exists" for the calculator
package. It is an in-progress intake session, never sealed. The actual sealed
fixture this repository's tests use is a different, unrelated package —
`PKG-0123456789AB` at `/home/rootux/artpkg-sdlc-contract-review/v0.1/artpkg-fixture-revision-candidate-r2/root`
(referenced by [tests/test_artpkg_sealed_handoff.py](../tests/test_artpkg_sealed_handoff.py)
and the new [tests/test_artpkg_requirement_approval.py](../tests/test_artpkg_requirement_approval.py)).
That fixture uses `schema_version: "0.2"` — the older per-question catalogue
states (`state`/`source_type` per answer, `fields.status` per record) from
[tools/artifacts_package_questionnaire.py](../tools/artifacts_package_questionnaire.py),
not `intake.requirements[]`. An adapter that only reads the v0.3 shape will
silently see nothing for packages sealed under v0.1/v0.2. It needs to handle
both, or ArtPkg needs to migrate existing fixtures forward first.

This matters for the calculator as a first integration test (see the
corrected step 4 below): before it can exercise anything end-to-end, it has
to actually be sealed, which today it is not, and per `completion_summary()`
in `artpkg_sealed_handoff.py` it is currently blocked from sealing (`FIN-001`
through `FIN-003` are unanswered).

## Approval granularity

ArtPkg's `source_classification` enum (`HUMAN_APPROVED_ARTPKG`,
`MODEL_PROPOSAL`, `HUMAN_SUPPLIED_UNCONFIRMED`, `TOOL_EXTRACTED`,
`REPOSITORY_EVIDENCE`, `EXTERNAL_REFERENCE`) is exactly the distinction
UXPkg's brief is protecting — "machine-generated proposals must not be
labeled human-approved." ArtPkg already has the vocabulary to keep that
honest.

The catch: today that classification is applied **per file**, not per
requirement or per UI element. `artifacts_package_answers.json` as a whole is
stamped `HUMAN_APPROVED_ARTPKG` in [`ARTPKG_HANDOFF.json`](../tools/artpkg_sealed_handoff.py#L464)
regardless of which individual answers inside it are still `PROPOSED`,
`SEEDED_PENDING_REVIEW`, or actually `CONFIRMED_BY_USER`. The calculator trace
shows this concretely: of 53 instantiated answers, only 2 were direct human
answers — the rest were seeded and pending confirmation — yet the sealed file
would carry one file-level `HUMAN_APPROVED_ARTPKG` stamp. An adapter cannot
treat "this file is HUMAN_APPROVED_ARTPKG" as "every requirement in it is
human-approved for UXPkg's purposes." It must re-derive per-requirement
approval from the per-answer status inside the payload, not from the
envelope classification.

## Approval granularity, part two: `review_disposition` is blanket-stamped at seal time

The per-file `source_classification` issue above turned out not to be the
whole story. `artifacts_package_answers.json` also carries a per-item
`review_disposition` field that looks like exactly the granular signal an
adapter would want — but `approved_snapshot()` in
[tools/artpkg_sealed_handoff.py](../tools/artpkg_sealed_handoff.py#L297-L313),
which runs during sealing, sets `review_disposition = "HUMAN_CONFIRMED"` on
every answer and record that isn't already `HUMAN_REJECTED`, regardless of
that item's original provenance. A `DERIVED_BY_SCRIPT`-seeded answer that was
never individually reviewed ends up with the same `HUMAN_CONFIRMED` stamp as
one a human actually typed. `review_disposition` inside a sealed package is
therefore not usable as a confirmation signal at all — the only fields that
still carry real provenance after sealing are each answer's `state` +
`source_type`, and each record's own `fields.status` (`fields.residual_status`
for `risks`).

## Shared adapter: built

Per coordination with Pipeline-A's ACC-integration agent (same conclusion
independently, from its own change-request population problem), this is now
a standalone CLI, not a field added to the sealed contract — the sealed
six-file bundle's inventory and closed-schema checks
(`content_set_sha256`, `validate_handoff`) reject a 7th file outright, and
mutating those checks would mean changing ArtPkg's existing sealed contract
rather than adding something alongside it:

[tools/artpkg_requirement_approval.py](../tools/artpkg_requirement_approval.py)
(tests: [tests/test_artpkg_requirement_approval.py](../tests/test_artpkg_requirement_approval.py))

- Invoked `--package SEALED_DIR --expected-package-sha256 HASH`, `shell=False`
  argv style, matching the Pipeline-A admission CLI shape.
- Reads the sealed package in place; never copies, repackages, or extends it.
- Independently recomputes `package_sha256` and verifies `SHA256SUMS` before
  trusting anything in the payload.
- Derives `human_confirmed` per answer/record from `state`/`source_type` or
  `fields.status`/`fields.residual_status` — never from `review_disposition`
  or the file-level `source_classification`.
- Returns `human_confirmed: null` (not a guessed `false`) for record
  categories with no approval-shaped status field (e.g. `artifacts`) and for
  `NOT_APPLICABLE` answers specifically — kept on its own `basis`, distinct
  from `DEFERRED`, per the correction below; conflating the two was an error
  in an earlier revision of this tool and this document.
- Output is bound to the sealed package's identity (`package_id`,
  `package_version`, `package_sha256`) and includes a `records_sha256` over
  its own output, so a consumer can prove which sealed package a given
  derivation came from.
- Rejects `schema_version` outside `{0.1, 0.2}` explicitly rather than
  silently misreading v0.3's `requirement_intake` shape — v0.3 is defined in
  `schemas/artifacts_package_answers_v0.3.schema.json` and implemented in
  `tools/artpkg_v03.py`, but nothing in this repository's sealing path
  produces it yet.

## Custody and trust: ArtPkg already has this pattern twice

UXPkg's stated constraint — trust is tied to the package's absolute
filesystem path and a private external custody store; reference it in place,
don't copy or repackage — is the same shape as ArtPkg's two existing external
handoffs:

- **Pipeline-A** ([docs/pipeline_a_phase1_integration.md](pipeline_a_phase1_integration.md)):
  dedicated `PIPELINE_A_CUSTODY_ROOT` outside the ArtPkg tree and outside the
  sealed directory; ArtPkg invokes an admission CLI by absolute path and
  independently re-validates the durable receipt (schema, hash, and status
  bindings) rather than trusting a zero exit code.
- **DSH bridge** ([docs/dsh_semantic_review_bridge.md](dsh_semantic_review_bridge.md),
  [docs/dsh_coding_handoff.md](dsh_coding_handoff.md)): exact sealed bytes are
  staged read-only in a separate workspace; a deterministic ID binds owner,
  session, sealed identity, and receipt hash; the companion workspace is
  manifested separately and never merged back into the six-file contract.

A UXPkg custody root should follow the same template: a dedicated
`UXPKG_CUSTODY_ROOT`-style path, an admission/extraction CLI invoked with
`shell=False` and an argument array (package dir + expected digest), and
independent verification of whatever UXPkg's return manifest says rather than
trusting process exit status. UXPkg's own output (contract, WireDSL, SVG,
validation, sealed evidence) should be tracked the same way ArtPkg tracks
Pipeline-A's admission receipt and DSH's companion manifest — a separate
ledger referenced by path, never copied into the sealed bundle after the
fact.

## Correction: filtering to `human_confirmed: true` is not by itself safe

An earlier revision of this document said `requirements.json` entries "come
only from records where the derivation tool reports `human_confirmed:
true`... `false`/`null` records must be dropped." That is unsafe as a
complete rule: a naive filter can silently turn an incomplete selection into
an apparently-complete, approvable UX contract. Dropping an unapproved
requirement that the intended scope actually needs, or a `deferred` item that
affects required UX, is not the same operation as dropping a record that is
genuinely not applicable — and a downstream consumer can't tell the
difference from a bare `requirements.json` alone.

The preparation stage (still to build) needs a full disposition, not a
boolean filter:

| Source disposition | Expected handling |
| --- | --- |
| Approved and active requirement | Include with preserved provenance |
| Unapproved requirement needed for the intended scope | Block preparation |
| Deferred decision affecting required UX | Block preparation |
| Demonstrably not applicable | Exclude with recorded justification |
| Non-requirement record or unrelated material | Exclude with explicit classification |
| Unknown or ambiguous disposition | Block pending resolution |

`tools/artpkg_requirement_approval.py` now reports enough distinct `basis`
values to build this on top of (see the fix below), but it does not decide
"needed for the intended scope" by itself — that requires reading ArtPkg's
scope-boundary answers (`BND-001`/`BND-002`) too, which the tool doesn't
touch. The preparation stage should also emit a durable selection/exclusion
report — every source item's disposition and why it was included, excluded,
or blocked — kept **outside** UXPkg's strict input directory and digest-bound
to both the source sealed package and the generated inputs, so a completeness
check has something authoritative to verify against.

**Fixed in the tool** to make this possible: `NOT_APPLICABLE` and `DEFERRED`
answers no longer share one basis. `NOT_APPLICABLE` (conditionally suppressed
by ArtPkg's own logic, e.g. a follow-up question whose trigger was `NO`) is
`basis: not_applicable` — safe to exclude with justification. `DEFERRED` is
now its own `basis: deferred` — an unresolved human decision, never safe to
treat the same as not-applicable, and the preparation stage must block on it
when it affects required scope. `UNKNOWN`/`TO_BE_INSPECTED` answers get their
own `basis: unknown_or_ambiguous` (still `human_confirmed: false`, but
distinguishable from an ordinary unconfirmed/seeded answer) so a caller can
choose to block pending resolution instead of routing it through ordinary
"not yet approved" handling. `human_confirmed: true` remains only a candidate
signal, not a decision — it still needs the scope-completeness layer above it
before anything is written to UXPkg's input directory.

## Correction: business authority and UX arrangement approval are separate

An earlier revision of this document said a machine-generated structured UX
proposal "requires an explicit human step to promote [it] ... before it's
written into UXPkg's dedicated input directory." That over-scopes what needs
approval before UXPkg sees it. Two different things were being conflated:

- **Authority over capabilities and allowed behaviors** — the approved
  catalog of what components/behaviors exist at all — genuinely needs human
  approval *before* the preparation stage can write valid UXPkg inputs. This
  is business authority; UXPkg has no way to originate it.
- **The proposed arrangement of those already-authorized components into
  screens/regions/layout** — does **not** need human approval before
  reaching UXPkg. UXPkg's own job, per its own doc, already covers this
  step: validate the proposed arrangement against the authorized
  capabilities, render the wireframe, and obtain human approval of the
  *resulting product shape*. Requiring the arrangement to be pre-approved
  upstream would duplicate that review rather than support it.

A machine-generated structured UX proposal should keep an explicit proposal
status in the preparation stage's own evidence (ArtPkg's `MODEL_PROPOSAL`
classification is the right vocabulary to reuse for that record) — but it
must never be relabeled as having created new business authority just to
satisfy UXPkg's `ux_input` shape, and it does not need a human sign-off
*before* UXPkg's own render-and-review cycle runs.

## Recommended ownership

- **ArtPkg**: source requirements, stable IDs, source approval evidence
  (via the derivation tool), and package identity.
- **A separate UX preparation stage** (not built yet, not part of ArtPkg's
  existing schema): capability mapping against an approved catalog, the
  proposed structured UX arrangement, and the complete inclusion/exclusion
  accounting from the correction above.
- **UXPkg**: deterministic validation, rendering, UX review, sealing, and
  conformance — unchanged from its own doc.
- **Orchestrator**: invocation, durable handoff references, and combined
  engineering/UX authorization.

The preparation stage can start out human-authored or template-driven; it
does not need a new LLM dependency. ArtPkg can expose the action (mirroring
how it exposes "Prepare DSH coding handoff") without owning the
domain-modeling logic inside it.

## Recommended smallest adapter

1. ~~A new preparation action~~ — **built**: `tools/artpkg_requirement_approval.py`
   verifies the sealed package and derives a raw per-item confirmation
   signal (four distinct `basis` values for answers, two for records — see
   the correction above). It handles the live `0.1`/`0.2` questionnaire shape
   only; `0.3`'s `requirement_intake.requirements[]` is explicitly rejected
   as unwired rather than silently misread (confirmed by grep: nothing
   imports `artpkg_v03.py`). This is a building block, not the preparation
   stage itself — it does not decide scope-completeness or produce the
   inclusion/exclusion report.
2. Still to build (the preparation stage proper): the disposition
   classification and blocking rules from the correction above, reading
   `BND-001`/`BND-002` for scope; the durable selection/exclusion report;
   capability mapping against an approved catalog; and strict emission of
   UXPkg's four inputs into a dedicated directory (never the full sealed
   bundle) with source-lineage binding.
3. Reference the sealed package and the UXPkg output by absolute path in a
   custody root outside both trees; verify UXPkg's returned status/seal
   independently (its own doc: "a status string or plain SHA256SUMS alone is
   insufficient verification"), same as the Pipeline-A pattern. This needs a
   verified handoff-reference contract, not yet defined (see review answer 6
   below).
4. Use the calculator as the first end-to-end test, once actually sealed —
   UXPkg's own doc proposes exactly this ("the ArtPkg-produced calculator
   export passes UXPkg intake, preserves requirement IDs, renders all 19
   components"). Per the correction above, the calculator package in this
   repo is not currently sealed and is blocked from sealing (`FIN-001`
   through `FIN-003` unanswered); it needs to reach an actual sealed state,
   with a known package digest, before this test can run.

## Current integration status

- Done: the approval-derivation building block
  (`tools/artpkg_requirement_approval.py`), verified against a real sealed
  fixture and unit-tested for the disposition distinctions above.
- Not done: safe eligibility/scope-completeness rules; capability-catalog
  preparation ownership; strict input emission with source-lineage binding;
  a verified handoff-reference contract; end-to-end integration tests.
- Blocked pending an actual sealed calculator package (or another concrete
  fixture) with a known digest, per the correction above — no end-to-end
  test can run against an unsealed source.

## Direct answers to UXPkg's "Requested review from the ArtPkg agent"

`/home/rootux/UXPkg/docs/ARTPKG-HANDOFF.md` asks six numbered questions.
Answers grounded in what's actually in this repository:

1. **Can ArtPkg emit the dedicated strict subdirectory, or is a translation
   adapter needed?** A translation adapter is needed, and can't be avoided by
   policy alone — ArtPkg's sealed six-file bundle structurally cannot be
   pointed at UXPkg's intake (UXPkg's doc: "provide a dedicated directory,
   not the entire general-purpose artifacts bundle"; ArtPkg's own
   `_validate_inventory` independently enforces that the sealed root contains
   *exactly* those six files, nothing more, nothing less). Half the adapter
   exists now (`artpkg_requirement_approval.py`); the manifest/requirements
   emission and the capability-mapping stage do not.
2. **Who owns stable requirement/capability IDs and approval of semantic
   catalogs?** ArtPkg already owns stable requirement IDs (`FR-001` etc.,
   confirmed compatible with UXPkg's `^[A-Za-z][A-Za-z0-9_.-]{0,95}$` ID
   pattern) and their approval state (via the derivation tool). It owns
   neither capability IDs nor an approved capability catalog — nothing in
   ArtPkg's schema or pipeline models UI capabilities at all. This still
   needs an owner: Pre-Artifacts, a new standalone proposal agent, or a new
   ArtPkg preparation stage, per both sides' docs.
3. **Where will Pre-Artifacts collect proposed structured UX, mockups and
   explicit viewports?** Outside this repository's current scope — nothing
   in ArtPkgPro's questionnaire/schema captures screens, viewports, or
   mockup references today. This is a question for whoever owns Pre-Artifacts,
   not something answerable from ArtPkg's source.
4. **Who invokes UXPkg, presents UX review, and combines UX and engineering
   authorization?** Not ArtPkg today. ArtPkg's existing precedent for "who
   invokes an external system" is the intake service itself (`artpkg-intake.service`)
   for Pipeline-A and the DSH bridge — an analogous orchestrator role could
   extend to UXPkg, but ArtPkg has no combined-authorization concept; its
   sealed packages carry `implementation_authority: NONE` unconditionally and
   explicitly defer that decision.
5. **What are the final filesystem/custody locations and same-host/cross-host
   constraints?** Same-host only today on the ArtPkg side, same as Pipeline-A
   and DSH (`PIPELINE_A_CUSTODY_ROOT` and the DSH bridge's shared-host-path
   requirement are both explicit about this). A UXPkg custody root would need
   its own dedicated env-configured path outside the ArtPkg tree, following
   that same template. Cross-host is unimplemented on both sides.
6. **What reference fields can ArtPkg retain for the final UXPkg path/digest
   and lifecycle?** Not yet defined. The precedent to reuse: ArtPkg tracks
   Pipeline-A's admission via a durable, independently re-validated receipt
   (`ADMISSION_RECEIPT.json`/`ADMISSION_COMPLETE.json`) rather than trusting
   exit codes or a bare path. A UXPkg reference record should follow the same
   shape — package identity, digest, lifecycle status — verified against
   UXPkg's own status/seal schemas rather than assumed from a path string,
   consistent with UXPkg's own warning that "a status string or plain
   SHA256SUMS alone is insufficient verification."
