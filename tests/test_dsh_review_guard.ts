/** Offline integration tests against an installed DSH checkout; see deployment notes. */
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { resolve } from 'node:path'
import test from 'node:test'
import { Context } from '@deepseek-ai/cordis'
import Loader from '@deepseek-ai/cordis-plugin-loader'
import SystemPrompt from '@deepseek-ai/dsh-system-prompt'
import Tools from '@deepseek-ai/dsh-tools'
import { createScope } from '@deepseek-ai/dsh-scope'
import { mountPreset } from '@deepseek-ai/dsh-agent-presets'
import * as guard from '../tools/dsh_review_guard.mjs'

const presetPath = fileURLToPath(new URL('../tools/dsh_review_agent.cordis.yml', import.meta.url))
const dshRoot = process.env.DSH_SOURCE_ROOT
assert.ok(dshRoot, 'Set DSH_SOURCE_ROOT to the DSH checkout used for module resolution')

async function harness(t, mode = 'native') {
  const ctx = new Context()
  ctx.baseUrl = pathToFileURL(resolve(dshRoot) + '/').href
  t.after(() => ctx.fiber.dispose())
  await ctx.plugin(Loader)
  await ctx.plugin(SystemPrompt, { persona: '' })
  await ctx.plugin(Tools, { mode })
  return ctx
}

async function scope(ctx, id, parent?) {
  const key = { id }
  let value
  await ctx.plugin(Object.assign(inner => {
    value = createScope(inner, key, parent === undefined ? undefined : { parent })
  }, { inject: ['tools', 'systemPrompt', 'loader'] }))
  return { key, ctx: value.ctx }
}

function tool(name, calls) {
  return {
    name,
    description: name,
    parameters: { type: 'object', properties: {}, additionalProperties: false },
    output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
    execute: async () => { calls.push(name); return `ran:${name}` },
  }
}

async function run(ctx, name, agent?) {
  const result = await ctx.tools.execute({
    signal: new AbortController().signal,
    callId: 'artpkg-test-call', name, arguments: {},
    ...(agent === undefined ? {} : { agent }),
  })
  return result.content[0]?.text
}

async function mount(ctx, keyCtx) {
  // Actual PresetTree/Include loading, not a YAML parser or mocked plugin API.
  await mountPreset(keyCtx, { id: 'artpkg-review', trust: 'system', path: presetPath })
}

test('real preset loader resolves adjacent guard and blocks current/future inherited tools', async t => {
  const ctx = await harness(t)
  const calls = []
  ctx.tools.register(tool('host-shell', calls))
  const standing = await scope(ctx, 'standing')
  const presetBefore = await readFile(presetPath, 'utf8')
  await mount(ctx, standing.ctx)
  const review = await scope(ctx, 'review', standing.key)
  const other = await scope(ctx, 'other')
  ctx.tools.register(tool('late-host-editor', calls))
  standing.ctx.tools.register(tool('late-preset-tool', calls))
  assert.deepEqual(ctx.tools.schemas(review.key), [])
  assert.equal(await run(ctx, 'host-shell', review.key), `Error: ${guard.DENIAL}`)
  assert.equal(await run(ctx, 'late-host-editor', review.key), `Error: ${guard.DENIAL}`)
  assert.equal(await run(ctx, 'late-preset-tool', review.key), `Error: ${guard.DENIAL}`)
  assert.deepEqual(calls, [])
  const assembly = await ctx.systemPrompt.assemble({ scope: review.key })
  assert.deepEqual(assembly.tools, [])
  assert.deepEqual(assembly.contexts, [])
  assert.equal(assembly.sections.length, 1)
  assert.match(assembly.sections[0].text, /advisory requirements reviewer/)
  assert.equal(await run(ctx, 'host-shell', other.key), 'ran:host-shell')
  assert.equal(await run(ctx, 'host-shell'), 'ran:host-shell')
  assert.equal((await ctx.systemPrompt.assemble({ scope: other.key })).tools.length, 2)
  assert.equal(await readFile(presetPath, 'utf8'), presetBefore)
})

test('native preset overrides host PTC/both without requiring any code runtime', async t => {
  for (const mode of ['ptc', 'both']) {
    const ctx = await harness(t, mode)
    const standing = await scope(ctx, `standing-${mode}`)
    await mount(ctx, standing.ctx)
    const review = await scope(ctx, `review-${mode}`, standing.key)
    assert.deepEqual(ctx.tools.schemas(review.key), [])
    assert.equal(ctx.tools.get('run_code', review.key), undefined)
    assert.deepEqual((await ctx.systemPrompt.assemble({ scope: review.key })).tools, [])
    assert.equal(await run(ctx, 'run_code', review.key), `Error: ${guard.DENIAL}`)
  }
})

test('own-agent tools fail assembly and inherited deny survives force-allow middleware', async t => {
  const ctx = await harness(t)
  const standing = await scope(ctx, 'standing')
  await mount(ctx, standing.ctx)
  const review = await scope(ctx, 'review', standing.key)
  const descendant = await scope(ctx, 'descendant', review.key)
  const calls = []
  for (const agent of [review, descendant]) {
    agent.ctx.tools.register(tool('local-tool', calls))
    agent.ctx.on('tools/pre-execute', async () => ({ kind: 'allow' }), { prepend: true })
    assert.equal(await run(ctx, 'local-tool', agent.key), `Error: ${guard.DENIAL}`)
    await assert.rejects(ctx.systemPrompt.assemble({ scope: agent.key }), /empty tool schema surface/)
  }
  assert.deepEqual(calls, [])
})

test('schema assertion catches provider and cooperative waterfall injection', async t => {
  const ctx = await harness(t)
  const standing = await scope(ctx, 'standing')
  await mount(ctx, standing.ctx)
  const review = await scope(ctx, 'review', standing.key)
  const schema = { name: 'injected', description: '', parameters: { type: 'object' } }
  const liftProvider = ctx.systemPrompt.tools(() => ({ schemas: [schema] }))
  await assert.rejects(ctx.systemPrompt.assemble({ scope: review.key }), /empty tool schema surface/)
  liftProvider()
  const lift = review.ctx.on('system-prompt/assemble', async (_assembly, _context, next) => {
    const result = await next()
    return { ...result, tools: [schema] }
  })
  await assert.rejects(ctx.systemPrompt.assemble({ scope: review.key }), /empty tool schema surface/)
  lift()
  assert.deepEqual((await ctx.systemPrompt.assemble({ scope: review.key })).tools, [])
})

test('unscoped installation throws before registering any global denial', async t => {
  const ctx = await harness(t)
  const calls = []
  ctx.tools.register(tool('host', calls))
  assert.throws(() => guard.apply(ctx), /requires a scoped context/)
  assert.equal(await run(ctx, 'host'), 'ran:host')
})