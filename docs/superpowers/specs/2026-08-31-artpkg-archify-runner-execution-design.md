# `artpkg_archify_runner.py` Bounded Execution Design

Date: 2026-08-31

Status: Draft for human review. **Not authorized for implementation.** This document defines the bounded execution contract for the runner only. It does not authorize changing `tools/artpkg_archify_runner.py`, wiring it into `artpkg serve`, or building it into a container image.

## Relationship To The Integration Contract

This document narrows [2026-08-31-artpkg-archify-integration-contract.md](2026-08-31-artpkg-archify-integration-contract.md) to the single component that is allowed to write across the ArtPkg/Archify boundary: the runner. Every rule in that contract still applies. This document exists so the runner's inputs, outputs, mounts, receipt schema, and failure states are explicit before any code is written or modified.

## What The Runner Is

The runner is the **only writable integration actor**. It is a bounded, single-purpose execution: given an already-materialized, immutable projection attempt and an explicit authorization decision, it invokes the Archify CLI once, records what happened, and stops. It is not a service, not a daemon, not a poller, and not a scheduler.

```text
ArtPkg authority/state
        │
        │ emits immutable projection bundle
        ▼
shared projection custody area  (/integration/RUN-<id>/projection-NNN/)
        │
        │ explicit ArtPkg-owned invocation decision
        ▼
artpkg_archify_runner.py
        │
        ├─ verify input hashes
        ├─ invoke Archify CLI
        ├─ capture exit/result
        ├─ hash outputs
        └─ write receipt
        ▼
Archify output directory (projection-NNN/output/)
        │
        └─ mounted RO
             ▼
        viewer :8666
```

## Inputs

The runner accepts exactly these inputs per invocation, all pointing into one immutable attempt directory (`/integration/RUN-<id>/projection-NNN/`):

```text
input/<view>.architecture.json        # ArtPkg-emitted Archify IR
mapping/<view>.mapping.json           # ArtPkg mapping sidecar (runner does not need to parse it, only knows it exists)
validation/<view>.projection-validation.md
authorization_decision                # explicit, ArtPkg-owned, passed by the caller — see "Authorized Invocation" below
```

The runner also takes execution configuration, not treated as "input data" but as its own operating parameters:

```text
node_executable       # path to Node runtime
archify_root           # path to local Archify checkout the runner may execute
quality                # Archify quality profile (e.g. "showcase")
timeout_seconds        # hard ceiling on CLI execution
```

Rules:

- The runner reads `input/`, `mapping/`, and `validation/` as **read-only**. It never writes into these directories.
- The runner must recompute the SHA-256 of `input/<view>.architecture.json` and compare it against the digest already recorded by ArtPkg for this attempt (recorded at emission time, outside the runner). A mismatch is a hard failure (`INPUT_DIGEST_MISMATCH`) — the runner does not proceed to invoke Archify.
- The runner does not scan `/integration/` for work. It is always told exactly which attempt directory to operate on. Discovery-by-directory-listing is explicitly disallowed (see Authorized Invocation).

## Outputs

The runner writes only into two subdirectories of the same attempt directory:

```text
output/<view>.html
output/<view>.archify-delivery.json
output/<view>.visual-check.json      (when visual-check is run)
receipt/<view>.receipt.json
```

- `output/` is writable by the runner and read-only to everything else, including the viewer container, which mounts `output/` read-only to serve `<view>.html`.
- `receipt/` is writable by the runner only. Nothing else writes here.
- The runner never writes anywhere outside its assigned attempt directory. It does not write into other `projection-NNN/` siblings, other `RUN-<id>/` directories, or back into ArtPkg's own output tree.

## Mount Permissions

Restating and binding the integration contract's mount rules to this specific component:

```text
input/, mapping/, validation/   : read-only  (runner's own mount)
Archify working/input area      : writable only if a transformation step requires it (e.g. a temp copy Archify needs) — never the attempt's input/
output/                          : writable   (runner's own mount)
receipt/                         : writable   (runner's own mount)
viewer's mount of output/        : read-only  (separate mount, held by the viewer, not the runner)
```

No other process shares the runner's writable mounts. If Archify needs scratch space to operate (e.g. a working copy of the IR), that scratch space is ephemeral, local to the runner's execution context, and never the system of record — the attempt directory's `input/` remains the only authoritative copy.

## Authorized Invocation

```text
Projection materialization is not execution authorization.
Runner execution requires an explicit ArtPkg-owned invocation decision.
```

Concretely, for this runner:

- The runner's entry point takes an explicit `authorization_decision` argument (or equivalent structured input) supplied by the ArtPkg-owned caller. This is not a boolean flag scraped from a file's existence — it is a value the caller constructs deliberately (e.g. an ArtPkg operator command, or the intake UI backend acting on an explicit human action), and it references the specific attempt directory it authorizes.
- The runner must reject invocation if the authorization decision does not name the exact attempt directory being operated on. An authorization for `projection-001` does not authorize running `projection-002`.
- The runner must not infer authorization from: the attempt directory existing, `input/` being non-empty, a file's timestamp, or a prior successful run of a sibling attempt.
- Re-running the same attempt directory (e.g. after a transient failure) requires a fresh authorization decision, even though the attempt directory itself stays immutable. Authorization and immutability are independent: the directory doesn't change, but permission to act on it is re-checked every invocation.
- The runner performs exactly one CLI invocation sequence (`validate`, then optionally `deliver`, then optionally `visual-check`) per authorized call. It does not retry on its own initiative and does not chain into a second attempt.

## Receipt Schema

One receipt per attempt, written to `receipt/<view>.receipt.json`, with at minimum:

```text
artpkg_ir_sha256                # SHA-256 of input/<view>.architecture.json
mapping_sidecar_sha256          # SHA-256 of mapping/<view>.mapping.json
projection_validation_sha256    # SHA-256 of validation/<view>.projection-validation.md
archify_version                 # Archify's own reported version string
archify_identity                # image digest / checkout commit hash, when available
output_artifact_sha256          # SHA-256 of output/<view>.html
invocation_timestamp            # UTC ISO-8601
exit_code                       # Archify CLI process exit code
runner_version                  # version/hash of artpkg_archify_runner.py itself
command                         # exact argv invoked
cwd                             # working directory the command ran in
stdout_json                     # parsed Archify JSON receipt, if any
stderr                          # captured stderr, if any
authorization_decision_ref      # identifier/reference of the authorization decision that permitted this run
```

This is additive to the fields `artpkg_archify_runner.py` already captures (`command`, `cwd`, `exit_code`, digests, stderr); the new fields are `archify_version`, `archify_identity`, `runner_version`, and `authorization_decision_ref`, which turn the receipt into self-contained provenance evidence rather than a debug log.

## Failure States

The runner must classify and record every non-success outcome as one of these, never a bare stack trace:

```text
MISSING_AUTHORIZATION           # no authorization decision supplied, or it names a different attempt
INPUT_DIGEST_MISMATCH           # input/<view>.architecture.json hash does not match ArtPkg's recorded digest
UNSUPPORTED_ATTEMPT_STATE       # attempt directory missing required input/mapping/validation files
ARCHIFY_INVOCATION_FAILED       # Archify CLI returned non-zero or malformed output
ARCHIFY_TIMEOUT                 # CLI exceeded timeout_seconds
OUTPUT_WRITE_FAILED             # runner could not write to output/ or receipt/
RECEIPT_WRITE_FAILED            # output written but receipt could not be persisted (must still surface as a failure, not a silent success)
```

Every failure still produces a receipt (or a minimal failure record in `receipt/`) stating which of the above occurred, so a failed attempt is auditable in the same way a successful one is. A failure never deletes or mutates `input/`, `mapping/`, or `validation/`.

## Non-Goals

- This design does not make the runner a long-running service, an HTTP endpoint, or a queue consumer.
- This design does not grant the runner write access to ArtPkg's own output tree, the Archify checkout's source, or the viewer container.
- This design does not define who/what constructs the `authorization_decision` value or how a human approval maps to it — that belongs to ArtPkg's own operator/UI design and is out of scope here.
- This design does not authorize implementation. It is a contract for review.

## Status

```text
ARTPKG_ARCHIFY_RUNNER EXECUTION DESIGN
→ INPUTS DEFINED (read-only attempt directory + explicit authorization decision)
→ OUTPUTS DEFINED (output/ + receipt/ only, scoped to one attempt directory)
→ MOUNT PERMISSIONS BOUND TO INTEGRATION CONTRACT
→ AUTHORIZED INVOCATION DEFINED (per-attempt, non-inferred, re-checked on retry)
→ RECEIPT SCHEMA DEFINED
→ FAILURE STATES ENUMERATED
→ IMPLEMENTATION NOT YET AUTHORIZED
```

Next step for a human reviewer: approve or amend this design. Only after both this document and the integration contract are approved should a task-by-task implementation plan be written for `artpkg_archify_runner.py`.
