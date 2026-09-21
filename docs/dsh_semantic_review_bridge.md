# ArtPkg → DSH advisory semantic review

The **Send to DSH** action appears after verified Pipeline-A admission. It sends
the sealed package text to an explicitly selected DSH model, using a dedicated
restricted preset. It does not implement the package or advance an SDLC phase.
The Phase 1 admission receipt remains immutable, including its original
`SEMANTIC_ASSESSMENT_NOT_IMPLEMENTED` next action. DSH handoff state is separate.

## Host setup

Use [tools/artpkg_dsh_setup.py](../tools/artpkg_dsh_setup.py) with the ArtPkg service
Python interpreter and `--user` set to the authenticated ArtPkg owner. The default
DSH origin is `http://localhost:3080`; `--base-url` must match the authority of the
current DSH launch URL exactly. Only loopback HTTP origins are accepted.

If editing/pasting the full URL is error-prone, add `--token-only`. The hidden
prompt then accepts only the value after `token=`; the utility builds the URL at
the validated `--base-url` origin. Do not put the token in command arguments.
This uses the same DSH authentication exchange, not a different auth mechanism.

The utility prompts for the launch URL using hidden terminal input. Enter it
directly into the terminal, never into chat, command arguments, repository files,
or a browser-visible ArtPkg link. The utility performs DSH's supported token-to-cookie
exchange. It neither reads DSH's signing secret nor fabricates authentication.
It then lists the DSH model catalog and asks which provider/model is authorized
to receive package text. A local DSH host does **not** mean the model is local:
verify the provider's configured destination before selecting it.

The utility installs the pinned composition and executable denial guard together
under the configured DSH home's custom preset root. See the
[restricted preset contract](dsh_restricted_review_preset.md). Existing different
artifacts are never overwritten automatically. DSH discovers new presets on
demand; upgrades to already-loaded presets require a DSH restart and fresh review
sessions, not a silent in-place edit.

Defaults are an owner-only configuration at `$HOME/.config/artpkg/dsh.json` and
separate owner-only state at `$HOME/.local/share/artpkg/dsh-review`. Set the host
ArtPkg service environment variable `ARTPKG_DSH_CONFIG_FILE` to the chosen absolute
configuration path, then restart ArtPkg. Preserve all five existing Pipeline-A /
SDLC environment settings. The service user must own and be able to read the config,
preset, guard and state root. Container deployment is not supported by this
loopback/shared-host-path bridge without a separate reviewed transport design.

Setup accepts `--replace-credentials` for renewal after the DSH cookie expires.
It stores only the issued cookie, never the process launch token. The config is
trusted administrator input, not an API payload. Changing model/origin for an
existing handoff fails closed instead of silently sending the same package elsewhere.

### Diagnosing setup exit code 1

The terminal now prints each setup stage and a fixed, secret-safe failure code.
`INVALID_LAUNCH_URL` means the pasted input failed local validation;
`AUTH_REJECTED` means DSH returned HTTP 401; `AUTH_FORBIDDEN` means HTTP 403.
A failure at `model catalog` occurs after the launch-token exchange succeeded,
and must not be confused with a bad pasted URL. Model selection, preset installation,
preset verification and configuration saving each have separate stage messages.

An owner-only status report named **dsh-setup-status.json** is saved beside the
configured credential file. It contains only stage, state, fixed diagnostic code
and guidance—no URL, token, cookie, model content or raw exception. It is diagnostic
only, never an authentication credential or proof that the bridge is connected.
If a task terminal disappears, this report preserves its last setup stage.
Share only the failure stage/code when troubleshooting, not the launch URL.

## Review flow and states

1. ArtPkg rechecks current sealing eligibility, all six sealed files, regenerated
   manifest/checksums, package identity, and accepted admission receipt/completion
   marker. Symlinked source/receipt paths are refused.
2. User confirms sending the package to the displayed provider/model. The prompt
   includes rendered package, approved answers, validation text and handoff JSON.
   Oversized prompts are rejected, never truncated (setup budget: 262,144 UTF-8 bytes).
3. A deterministic ID binds owner, ArtPkg session, sealed identity and receipt byte
   hash. An advisory DSH record is written durably outside ArtPkg and Pipeline-A
   custody. Exact sealed bytes are staged read-only in a separate workspace.
4. `SESSION_PREPARING` records creation intent before DSH session creation. An
   existing DSH session with no local creation record is refused. Safe preparation
   failures can be resumed only while the session remains blank and idle.
5. `SESSION_CREATED` means the intended preset/session/model were acknowledged.
   `PROMPT_DISPATCHING` is fsynced **before** the prompt HTTP call.
6. `PROMPT_ACCEPTED` means DSH acknowledged enqueueing. `DELIVERY_UNCERTAIN` means
   the request may have been accepted despite a transport/protocol failure.
   Neither state allows an automatic resend. Process crashes during dispatch
   deliberately leave the same conservative no-resend boundary.

Cross-process nonblocking file locks serialize sends. Repeated sends reuse the
durable record and cannot queue another initial prompt. The native DSH chat can
still be used by its authenticated account, so this is not a multi-tenant DSH
security boundary. The initial setup enables exactly one ArtPkg user. Do not
share the DSH account between mutually untrusted ArtPkg owners.

## Reading the result

**Open DSH** opens the authenticated application's root in another tab. This DSH
version has no verified session deep links; select the displayed session ID or
the `ArtPkg <package> v<version> semantic review` title. The link contains no cookie
or launch token and does not authenticate the browser on the user's behalf.

For browsers on another device, create a service-user-owned, non-group/world-writable
`dsh-browser.json` beside the private file named by `ARTPKG_DSH_CONFIG_FILE`.
Its `browser_url` field specifies the browser-only HTTP(S) origin, for example
`http://192.168.1.163:3080/`. Without this file, links use the local API origin.
Both advisory and coding links use this setting; authenticated RPC remains
loopback-only. Changing the browser address does not recreate or alter a handoff.
Never include launch tokens, credentials, query strings or fragments in this file.
Authenticate the browser directly through DSH's supported login/launch process;
cookies for localhost do not automatically authenticate a LAN-IP origin. Prefer
HTTPS for remote access. The navigation link still does not select a DSH session.

**Read initial review transcript** reads a bounded cached history prefix. It
requires the exact receipt-bound prompt request ID **and** text hash, verifies
assistant provider/model provenance, and excludes later native-chat user turns.
Model text is rendered as text, not HTML. Cached DSH cursors may be stale; missing
history is never evidence that retrying a prompt is safe.

New initial-review prompts explicitly require English findings, explanations and
questions, preserving exact IDs and JSON keys, and request an assessment rather
than a conversational introduction. This is a model instruction, not a guarantee
of compliance or a language-validation gate.

Saved transcripts remain verbatim, including older non-English responses.
Refreshing does not translate or regenerate them. For an English rendering of an
older response, ask for a translation in the existing DSH chat; that later turn
is not substituted for the receipt-bound initial transcript. Do not delete the
handoff ledger to force another initial review. Prompt updates require an ArtPkg
service restart but do not change the pinned preset or invalidate dispatched
handoffs. A prepared but undispatched old prompt still fails closed on a hash
change rather than silently sending different text.

All output remains `assessment_status: NOT_VERIFIED` and
`implementation_authority: NONE`. Suggested outcomes in the prompt are draft
advisory vocabulary, not an implemented accepted-assessment schema. Structured
semantic-result validation, human acceptance, Pipeline-A phase advancement, and
automatic recovery of ambiguous sends are **not implemented**. Inspect uncertain
delivery in DSH; do not delete the ledger or manually resubmit to work around it.

## Security and validation

- The local DSH process, model routing, host plugins, installation and ArtPkg
  service account are trusted. File modes alone are not a sandbox.
- The scoped guard hides inherited tools, disables code-tool transport, denies
  all tool execution, and rejects any nonempty assembled tool schema surface.
- HTTP proxies/redirects are disabled for credential-bearing API calls; response
  sizes/timeouts and RPC correlation/business acknowledgements are checked.
- DSH APIs are not generally proxied to the browser. Both narrow ArtPkg routes
  authenticate and enforce session ownership; JSON/origin checks reject cross-site
  browser submissions. DSH errors do not echo remote error messages or credentials.
- There is no claim that review has completed merely because a prompt was accepted.

Regression suites: [tests/test_artpkg_dsh_bridge.py](../tests/test_artpkg_dsh_bridge.py)
uses a strict fake local DSH HTTP server and temporary sealed custody;
[tests/test_dsh_review_guard.ts](../tests/test_dsh_review_guard.ts) tests the real DSH
tool registry and preset loader offline, without model calls.