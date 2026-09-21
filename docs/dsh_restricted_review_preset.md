# Restricted DSH advisory review preset

This is a trusted DSH composition policy, not an OS sandbox. Package artifacts
are untrusted model input. The DSH host, loaded plugins, preset files, and bridge
configuration must remain trusted.

## Deploy both files

- Copy [the preset](../tools/dsh_review_agent.cordis.yml) into a dedicated preset
  directory under a configured DSH preset root, naming the deployed composition
  **agent.cordis.yml** (DSH's discovery filename).
- Copy [the guard](../tools/dsh_review_guard.mjs) into that **same directory**,
  preserving the guard's basename. The YAML row's `name: ./dsh_review_guard.mjs`
  resolves relative to the preset directory, **not** the DSH process working
  directory. Bare package names such as `@deepseek-ai/dsh-persona` resolve from
  the harness installation instead. No guard imports or npm install are needed.
- Select this dedicated preset explicitly when creating review sessions. Do not
  silently fall back to a general-purpose preset if discovery/mounting fails.
- Verify **both** deployed files against trusted, release-pinned SHA-256 values
  before starting or connecting review work. Validating only the YAML leaves
  executable guard replacement undetected. Pin the guard basename and reject
  unexpected composition rows, disabled guard rows, and writable/untrusted
  deployment paths. A hash obtained from the same mutable deployment directory
  is not an integrity authority.
- Keep the pair immutable while sessions run. DSH uses standing preset mounts;
  changing bytes on disk does not prove already-loaded code changed. Restart the
  deployment and create fresh review sessions after upgrading either artifact.
  Do not unload/reload the guard independently of the review composition.
- The trusted host must supply `tools` and `systemPrompt`, and support the APIs
  below. Missing services, unresolved modules, or a throwing plugin must be
  treated as a deployment failure. No model credentials are needed for the tests.

Current source artifact hashes (update trusted release pins when changing files):

| Artifact | SHA-256 |
| --- | --- |
| [tools/dsh_review_guard.mjs](../tools/dsh_review_guard.mjs) | `619004594dd133f035b4b6470a1868d5714610240dcac01427061b60380309b0` |
| [tools/dsh_review_agent.cordis.yml](../tools/dsh_review_agent.cordis.yml) | `6f102eaef7e486d32e92d8a38014f63107857333b4167a2714f928797fe20f4b` |

Bridge-side deployment/config validation and setup are intentionally outside
this change. These pins are documentation, not an implemented bridge check.

## Verified source contracts and guarantees

Verified against DSH commit `cd5ef8148158c3a752a658978873241fdf8e2bbc`
(`0.1.2-alpha.1` in that checkout), not inferred from a persona instruction:

| DSH package / symbol | Verified behavior |
| --- | --- |
| `@deepseek-ai/dsh-tools`, `restrict(filter: ToolRestriction): () => void` | `{ allow: [] }` is valid and masks all inherited global/ancestor tools, including future registrations. Unscoped calls throw. Restrictions intersect throughout the scope chain. The agent's **own** registrations are exempt. |
| `@deepseek-ai/dsh-tools`, `presentAs(mode: ToolPresentationMode): () => void` | `'native'` overrides the host presentation at the preset scope. Capability restrictions alone do not hide reserved `run_code`; native mode removes it from this scope's lookup and schemas. A nearer descendant presentation can override it, which the assertion detects. |
| `@deepseek-ai/dsh-tools`, `guard(guard: ToolGuard): () => void` | A synchronous returned string denies. `guardReason()` checks global guards, then every ancestor-to-agent guard layer, after the extensible pre-execute waterfall. Force-allow middleware cannot overrule a guard denial. No `global` argument exists. |
| `@deepseek-ai/dsh-tools`, `schemas(scope?: ScopeKey): ToolSchema[]` | Pass the actual scope explicitly. Omitting it returns the **global** view, even when calling through a scoped context. |
| `@deepseek-ai/dsh-system-prompt`, `system-prompt/assemble(assembly, context, next): Promise<PromptAssembly>` | The scoped waterfall runs after provider collection, before the assembled prompt is returned to the agent. `context.scope` is the concrete agent key. The guard checks registry schemas before/after `await next()` and the returned `assembly.tools`. |
| `@deepseek-ai/dsh-scope`, `scopeTarget()` | An ancestor-scoped listener receives descendant events. `{ global: true }` would bypass event filtering; the guard intentionally does **not** use it. |
| `@deepseek-ai/dsh-agent-presets`, `mountPreset()`, `PresetTree.import()`, `classifyRowSpecifier()` | Relative row modules load from the composition directory; bare packages resolve from the harness base. The mount rejects unusable rows. The import-free module exports standard Cordis `name`, `inject`, and `apply`. |

The preset has no concrete `ctx.agent` at plugin application time. Its standing
scope becomes an ancestor of review agents. Therefore the assertion is a
**per-assembly gate**, not a startup notification assertion or an invented
agent-schema method. `agent/session-start` is a veto-less notification, not the
correct validation hook. A local-tool misconfiguration may allow session
creation but prevents normal prompt assembly/model submission.

Within the trusted DSH dispatch path:

- Inherited global tools are neither visible nor invokable by review agents.
- Native presentation hides the code transport, even with host `ptc`/`both`.
- Agent-local tools cannot execute either: the inherited deny guard covers
  them. Their accidental visibility causes prompt assembly to fail closed.
- Additional schema providers/cooperative inner assembly middleware also cause
  an assembly error if they expose a tool.
- Sibling agents and subject-less host operations remain unaffected. This is
  deliberately not a process-global tool ban.

Do not interpret this as protection from hostile same-process plugins: those
can perform their own I/O, directly invoke tool bodies, dispatch without the
review agent identity, replace/dispose policies, or bypass the cooperative
assembly waterfall (including outer middleware returning altered results).
Review data must only enter the intended agent loop; no separate automatic host
execution path is secured by this preset. File permissions, pinned artifacts,
trusted host composition, and correct bridge identity routing remain required.

## Offline regression tests

[tests/test_dsh_review_guard.ts](../tests/test_dsh_review_guard.ts) uses real
Cordis contexts, DSH `Tools`, scoped parent chains, `SystemPrompt`, and the
actual preset loader. The agent keys are minimal constructed identities; this
is not a live-model/full agent-loop or production deployment test.

Run with an existing DSH checkout and its installed dependencies. Set
`DSH_SOURCE_ROOT` to its absolute path and `TSX_DISABLE_CACHE=1`. Invoke Node
with the checkout's `node_modules/tsx/dist/cli.mjs`, `--tsconfig` pointing at
that checkout's root TypeScript configuration, and `--test` pointing at the
absolute ArtPkg test path. DSH TypeScript path aliases resolve source packages;
ArtPkg does not need its own npm dependencies. No dependency installation,
network requests, credentials, Python, or modifications to DSH/home are needed.

Verified on Node `v24.20.0`: **5 tests passed, 0 failed**:

1. Real file-relative preset loading; current/future global and ancestor tools
   hidden and denied; persona preserved; unrelated/global dispatch unaffected.
2. Host PTC and both modes overridden without a code runtime; `run_code` absent
   and denied.
3. Own-agent/descendant tools rejected during assembly; force-allow pre-execute
   middleware cannot bypass the inherited denial; tool bodies never run.
4. Extra schema providers and cooperative inner waterfall schema injection
   rejected; assembly recovers after the offending registration is removed.
5. Unscoped application throws before installing any global denial.

The first test run exposed an incorrect test cleanup call (`ctx.dispose()`);
the suite uses the verified Cordis `ctx.fiber.dispose()` API instead. All policy
assertions passed again with successful teardown. Editor diagnostics report no
errors in the preset, guard, or test file.