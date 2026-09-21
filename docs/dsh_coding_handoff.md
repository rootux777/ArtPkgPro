# Final review and DSH coding handoff

This is a separate path from the restricted semantic reviewer. DSH already supplies
the `standard` coding preset, filesystem/shell tools, project instructions, plan
approval and execution permissions. ArtPkg supplies reviewed project context, not
a replacement coding harness.

## User flow

The primary intake action is **Continue to final review & coding handoff**.
On the final-review page, a persistent bottom action bar remains visible while
reading the package. After checking the current confirmation, click **Save review
& continue**, then confirm **Seal & continue**, then **Prepare DSH workspace**.
The bar becomes **Open DSH** only when preparation succeeds. It uses the same
consent checks as the buttons beside each confirmation; ticking a checkbox alone
does not save, seal, send a prompt or start a build.
The final-review page shows one current action at the top, not three competing
checkbox panels. After its confirmation is checked, click its button to save or
execute that step. Later actions appear only after the prerequisite succeeds.
Sealing and admission are separate states: a sealed revision without an accepted
receipt offers an admission retry rather than prematurely enabling preparation.

The intake page's collapsed **Advanced** section retains archive downloads and the
optional no-tools advisory review. Neither is the coding handoff. The legacy
assessment-only sealing controls are further collapsed and explicitly labelled.

1. In intake, choose **Final package review & coding handoff**. This opens `/review`
   for the authenticated owner's session.
2. Inspect the generated Markdown, normalized records, OPEN questions, validation
   and original source. Correct requirements in the questionnaire if needed.
   Confirmed records are not automatically promoted from PROPOSED to accepted, and
   confirming a question is not interpreted as answering it.
3. **Record final review**. A final-review attestation binds the document, template
   digest and original source bytes. Those source bytes and their SHA-256 become
   part of the answers payload, not an unbound external attachment. Source text is
   evidence, never approved requirements or trusted harness instructions.
4. **Seal reviewed package for Pipeline-A**. The existing six-file contract is
   unchanged. A prior seal/receipt remains untouched; a reviewed revision receives
   its own seal and admission. The new page checks review freshness during sealing.
   The legacy sealing path remains available for backward compatibility, but old
   packages without this final review cannot enter the new coding adapter.
5. **Prepare DSH coding handoff**. An explicit confirmation creates a project folder
   and a blank `standard` DSH session using the configured provider/model. This
   operation does not submit a model prompt or build code. Repeat preparation
   reuses the same companion and session without overwriting modified files.
6. Open DSH and select the displayed coding session. Set **plan mode** and
   **workspace-write with human approvals**, review the generated prompts, and paste
   a chosen task. No verified session deep-link or DSH prompt-palette integration
   exists; prompts are copyable on the ArtPkg page and stored in the companion.
7. Approve a bounded plan and execution permissions in DSH before building. The
   plan-only package and original receipt retain implementation authority `NONE`.
   A later DSH approval is separate; ArtPkg does not attest or enforce that approval.

## Location and contents

By default workspaces are created below the **ArtPkg service user's**
`~/Downloads/ArtPkg-Workspaces/`, named by package ID, version and owner/receipt-bound
identity. `ARTPKG_CODING_ROOT` can select a dedicated absolute owner-only directory.
The root must not overlap ArtPkg source/repository, custody or DSH review state.
This variable is a service configuration value, not a browser-supplied path.

Each workspace contains:

- `project/AGENTS.md`: fixed trusted working instructions; DSH's existing instruction
  loader reads it. Implementation files belong in this project directory.
- `handoff/sealed/`: all six exact sealed files, unchanged.
- `handoff/source_pre_artifacts.md`: when available, source bytes extracted from the
  sealed final-review attestation, checked against their digest.
- `handoff/START_HERE.md`: reading order and approval boundaries.
- `handoff/PROJECT_CONTEXT.json`: project scope and all normalized record collections
  with status/provenance intact, including empty collections and OPEN questions.
- `handoff/PROMPTS.md` and `PROMPTS.json`: plan, build, verification and architecture
  task starters contextualized with package identity and requirement IDs. These are
  deterministic templates, not an LLM-generated architecture or accepted build plan.
- `handoff/COMPANION_MANIFEST.json`: companion hashes and seal/receipt binding.

The companion is not added retroactively to the old sealed contract. It is separately
manifested. The sibling handoff files are read-only by mode; this is **not** an OS
sandbox against a malicious same-user process. DSH permission configuration is the
runtime enforcement boundary. The backend does not set those permissions via an
unverified API, so it never auto-submits a prompt to the tool-enabled session.

## Deployment and limitations

- Restart the ArtPkg intake service after deploying the Python changes. The existing
  DSH authentication configuration remains usable; no new token is required.
- Both services must see the same host paths. Container/remote deployments need a
  deliberate shared mount; a browser's Downloads folder is not necessarily the
  service user's Downloads folder. No arbitrary destination picker is supported.
- The configured DSH deployment must expose `standard`. Creation response, blank/idle
  status, cwd and selected model are checked; partial preparation may resume only
  while blank and idle. A READY session is never reconfigured by repeat preparation.
- Config access currently reuses the existing bridge's allowlist and private config
  validation, including the installed restricted review preset. That preset is not
  selected for coding and is never weakened.
- Source evidence has a 1 MiB review cap. Oversized/invalid UTF-8/symlink sources fail
  explicitly; no silent truncation. Human approval and source inclusion are explicit
  on the review page. Model sharing happens when the human submits a task in DSH.
- No automatic prompt dispatch, Archify execution, dependency installation, commit,
  deployment or change to the Pipeline-A/SDLC authority contracts is introduced.
- Review is a human comparison, not automated source-loss remediation. Missing
  normalized components are visible, and full original source is retained for the
  next agent; this feature does not repair parser mappings or settle OPEN questions.

## Verification

Offline Python tests cover digest freshness, source evidence, stale confirmation,
sealed byte preservation, owner/origin enforcement, workspace checks, retry behavior
and blank-session creation without `session/prompt`. Node tests exercise final-review
controls, literal rendering, confirmation payloads and copying prompts without send.