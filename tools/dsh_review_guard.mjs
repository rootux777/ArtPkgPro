/** Import-free Cordis preset plugin. See docs/dsh_restricted_review_preset.md. */
export const name = 'artpkg-review-guard'
export const inject = ['tools', 'systemPrompt']

export const DENIAL = 'ArtPkg advisory review forbids all tool execution'

function assertEmpty(schemas) {
  if (!Array.isArray(schemas) || schemas.length !== 0) {
    throw new Error('ArtPkg advisory review requires an empty tool schema surface')
  }
}

export function apply(ctx) {
  // These APIs register Cordis-owned effects themselves. restrict() rejects
  // an unscoped mount; do it first so a bad host mount cannot install a global
  // denial. An empty allow-list also covers tools registered later.
  ctx.tools.restrict({ allow: [] })
  // Capability restrictions do not hide the reserved PTC transport run_code.
  ctx.tools.presentAs('native')
  // A string is a terminal denial AFTER the extensible pre-execute waterfall.
  // No global option: this guard covers the standing preset and descendants,
  // not unrelated agents or subject-less host calls.
  ctx.tools.guard(() => DENIAL)

  // A standing preset has no concrete agent at apply time. The scoped assembly
  // waterfall supplies the actual agent key in context.scope, before the LLM
  // request. Own-agent registrations bypass restrict(), so fail closed rather
  // than silently presenting them. Check both the registry and wire assembly,
  // including changes made by cooperative inner middleware during await.
  ctx.on('system-prompt/assemble', async (_assembly, context, next) => {
    if (context.scope === undefined) {
      throw new Error('ArtPkg advisory review requires scoped prompt assembly')
    }
    assertEmpty(ctx.tools.schemas(context.scope))
    const assembled = await next()
    assertEmpty(ctx.tools.schemas(context.scope))
    assertEmpty(assembled.tools)
    return assembled
  }, { prepend: true })
}