'use strict';

const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const html = readFileSync(path.join(__dirname, '../tools/artpkg_intake_ui.html'), 'utf8');
const source = html.slice(html.indexOf('let session = null;'), html.indexOf('function humanQuestion('));

function deferred() {
  let resolve;
  const promise = new Promise((done) => { resolve = done; });
  return { promise, resolve };
}

function harness(storage = new Map(), responder = async () => ({ session_dir:'/test/session' })) {
  const status = {};
  const listeners = {};
  const calls = [];
  const context = vm.createContext({
    document: {
      getElementById: () => status,
      createElement: () => ({}),
    },
    sessionStorage: {
      getItem: (key) => storage.get(key) || null,
      setItem: (key, value) => storage.set(key, value),
      removeItem: (key) => storage.delete(key),
    },
    window: { addEventListener: (name, fn) => { listeners[name] = fn; } },
    fetch: async (url, options) => {
      const payload = JSON.parse(options.body);
      calls.push({ url, payload });
      return { ok:true, json:async () => responder(payload) };
    },
    syncAfterReview: () => {},
  });
  vm.runInContext(source + '\nsession = {session_dir:"/test/session"};', context);
  function editor(id, value = '', state = 'PROVIDED') {
    const answer = { value };
    const availability = { value:state };
    const button = { disabled:false, textContent:'Save answer' };
    const controls = { appendChild: (element) => element };
    context.bindAnswerDraft({ id }, answer, availability, controls);
    return {
      answer, availability, button,
      type: (text) => { answer.value = text; answer.oninput(); },
      state: (next) => { availability.value = next; availability.onchange(); },
      save: () => context.saveHumanAnswer({ id }, answer, availability, button),
    };
  }
  return { context, editor, storage, calls, listeners, status,
    redraw: () => vm.runInContext('answerEditors.clear()', context),
    switchSession: (dir) => { context.dir = dir; vm.runInContext('session = {session_dir:dir}; answerEditors.clear()', context); },
  };
}

test('saving one answer preserves another draft through redraw and page reload', async () => {
  const h = harness();
  const first = h.editor('PKG-003');
  const other = h.editor('PKG-004');
  first.type('Owner');
  other.type('Respondent still editing');
  other.state('TO_BE_INSPECTED');
  await first.save();
  assert.equal(h.storage.size, 1);
  h.redraw();
  assert.equal(h.editor('PKG-004').answer.value, 'Respondent still editing');
  const reloaded = harness(h.storage);
  const restored = reloaded.editor('PKG-004');
  assert.equal(restored.answer.value, 'Respondent still editing');
  assert.equal(restored.availability.value, 'TO_BE_INSPECTED');
  await restored.save();
  assert.equal(h.storage.size, 0);
});

test('duplicate blocker and queue editors share value and availability', async () => {
  const h = harness();
  const blocker = h.editor('SEC-001');
  const queue = h.editor('SEC-001');
  blocker.type('NO');
  assert.equal(queue.answer.value, 'NO');
  queue.state('DEFERRED');
  assert.equal(blocker.availability.value, 'DEFERRED');
  await queue.save();
  assert.equal(h.calls[0].payload.value, 'NO');
  assert.equal(h.calls[0].payload.state, 'DEFERRED');
});

test('failed save retains draft and enables explicit retry', async () => {
  let fail = true;
  const h = harness(new Map(), async () => {
    if (fail) throw new Error('offline');
    return { session_dir:'/test/session' };
  });
  const editor = h.editor('PKG-003');
  editor.type('Kept value');
  await editor.save();
  assert.match(h.status.textContent, /draft has been kept/);
  assert.equal(editor.button.disabled, false);
  assert.equal(h.storage.size, 1);
  fail = false;
  await editor.save();
  assert.equal(h.storage.size, 0);
});

test('double click cannot dispatch twice; edits made during save remain drafts', async () => {
  const pending = deferred();
  const h = harness(new Map(), () => pending.promise);
  const editor = h.editor('PKG-003');
  editor.type('Sent value');
  const saving = editor.save();
  await editor.save();
  assert.equal(h.calls.length, 1);
  editor.type('Newer draft');
  pending.resolve({ session_dir:'/test/session' });
  await saving;
  assert.equal(h.storage.size, 1);
  h.redraw();
  assert.equal(h.editor('PKG-003').answer.value, 'Newer draft');
});

test('answer saves are serialized and all edits dispatch in order', async () => {
  const pending = deferred();
  let index = 0;
  const h = harness(new Map(), async () => {
    if (++index === 1) await pending.promise;
    return { session_dir:'/test/session' };
  });
  const one = h.editor('PKG-003');
  const two = h.editor('PKG-004');
  one.type('Owner'); two.type('Respondent');
  const first = one.save();
  const second = two.save();
  await Promise.resolve();
  assert.equal(h.calls.length, 1);
  pending.resolve();
  await Promise.all([first, second]);
  assert.deepEqual(h.calls.map((call) => call.payload.value), ['Owner', 'Respondent']);
  assert.equal(h.storage.size, 0);
});

test('drafts are isolated by session and old save responses cannot switch sessions', async () => {
  const pending = deferred();
  const h = harness(new Map(), () => pending.promise);
  const editor = h.editor('PKG-003');
  editor.type('Session one owner');
  const saving = editor.save();
  h.switchSession('/test/other');
  assert.equal(h.editor('PKG-003').answer.value, '');
  pending.resolve({ session_dir:'/test/session' });
  await saving;
  assert.equal(vm.runInContext('session.session_dir', h.context), '/test/other');
});

test('unavailable browser storage keeps in-memory drafts and warns before leaving', () => {
  const h = harness();
  h.context.sessionStorage.setItem = () => { throw new Error('disabled'); };
  h.editor('PKG-003').type('Keep in memory');
  h.redraw();
  assert.equal(h.editor('PKG-003').answer.value, 'Keep in memory');
  let prevented = false;
  h.listeners.beforeunload({ preventDefault: () => { prevented = true; } });
  assert.equal(prevented, true);
});

test('both answer surfaces bind drafts and upload records the resumable session URL', () => {
  assert.equal((html.match(/bindAnswerDraft\(item, answerBox, stateSelect, controls\);/g) || []).length, 2);
  assert.equal((html.match(/=> saveHumanAnswer\(item, answerBox, stateSelect,/g) || []).length, 2);
  assert.ok(html.includes('url.searchParams.set("dir", session.session_dir)'));
  assert.ok(html.includes('window.history.replaceState(null, "", url)'));
});

test('UX resolution return restores the session and exposes final review handoff', () => {
  assert.ok(html.includes('params.get("from") === "ux-resolution"'));
  assert.ok(html.includes('UX/UI decisions saved. Review the updated ArtPkg source'));
  assert.ok(html.includes('Continue to final review & coding handoff'));
  assert.ok(html.includes('id="uxResolutionStatus"'));
  assert.ok(html.includes('fresh UX/UI snapshot and proposal are required'));
});