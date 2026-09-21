'use strict';

const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const html = readFileSync(path.join(__dirname, '../tools/artpkg_intake_ui.html'), 'utf8');
const start = html.indexOf('function renderDshReview(');
const end = html.indexOf('function renderSealing(', start);
assert.ok(start >= 0 && end > start, 'renderDshReview must precede renderSealing');
const source = html.slice(start, end);

// Only the DOM surface used by renderDshReview and its text helpers is modeled.
// No HTML parser: innerHTML is forbidden, and textContent always stays text.
class Element {
  constructor(tag) {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.disabled = false;
    this.checked = false;
    this.text = '';
  }

  set textContent(value) {
    this.text = value == null ? '' : String(value);
    this.children = [];
  }

  get textContent() {
    return this.text + this.children.map((child) => child.textContent).join('');
  }

  set innerHTML(_value) {
    assert.fail('HTML insertion is not allowed in this text-only DOM stub');
  }

  appendChild(child) {
    this.children.push(child);
    return child;
  }

  append(...children) {
    children.forEach((child) => this.appendChild(child));
  }

  replaceChildren(...children) {
    this.text = '';
    this.children = [];
    this.append(...children);
  }

  // Unlike calling onclick directly, user clicks respect disabled controls.
  click() {
    if (!this.disabled) return this.onclick?.();
  }

  setChecked(checked) {
    if (this.disabled) return;
    this.checked = checked;
    this.onchange?.();
  }
}

function descendants(element) {
  return element.children.flatMap((child) => [child, ...descendants(child)]);
}

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

const confirmation = 'I confirm advisory review only; implementation authority remains NONE.';

function ready(overrides = {}) {
  return { available: true, provider: 'offline-provider', model: 'offline-model', confirmation, ...overrides };
}

function result(status = 'PROMPT_SENT') {
  return {
    status,
    dsh_session_id: 'review-session-123',
    provider: 'offline-provider',
    model: 'offline-model',
    chat_url: 'http://127.0.0.1:3080/',
  };
}

function sessionWith(dsh) {
  return { session_dir: '/offline/artpkg/session', dsh_handoff: dsh };
}

function harness(dsh, responder = () => { throw new Error('Unexpected POST'); }) {
  const area = new Element('section');
  const calls = [];
  const statuses = [];
  let renderCount = 0;
  const document = { createElement: (tag) => new Element(tag) };
  // Keep these helper stubs consistent with the UI helpers, including null and
  // empty-list fallbacks; testing HTML parsing/security requires a real browser.
  function appendText(parent, tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = text;
    return parent.appendChild(element);
  }
  function sealField(parent, label, value) {
    const field = document.createElement('div');
    field.className = 'seal-field';
    appendText(field, 'strong', '', label);
    appendText(field, 'span', 'meta', value ?? 'Not available');
    parent.appendChild(field);
  }
  function sealList(parent, label, values, emptyText) {
    const field = document.createElement('div');
    field.className = 'seal-field';
    appendText(field, 'strong', '', label);
    const list = document.createElement('ul');
    list.className = 'seal-list';
    (values?.length ? values : [emptyText]).forEach((value) => appendText(list, 'li', 'meta', value));
    field.appendChild(list);
    parent.appendChild(field);
  }
  const context = vm.createContext({
    document, appendText, sealField, sealList,
    session: sessionWith(dsh),
    postJson: async (url, payload) => {
      // Normalize VM-realm objects for strict structural assertions.
      calls.push({ url, payload: JSON.parse(JSON.stringify(payload)) });
      return responder(url, payload);
    },
    setStatus: (text) => statuses.push(text),
    render: () => {
      renderCount += 1;
      area.replaceChildren();
      context.renderDshReview(area);
    },
  });
  // Deliberately expose no fetch, browser, network, or require to the UI slice.
  vm.runInContext(source, context, { filename: 'renderDshReview-ui-slice.js', timeout: 1000 });
  context.renderDshReview(area);
  const all = (tag) => descendants(area).filter((element) => element.tagName === tag.toUpperCase());
  function button(label) {
    const matches = all('button').filter((element) => element.textContent === label);
    assert.equal(matches.length, 1, `Expected exactly one ${label} button`);
    return matches[0];
  }
  return { area, all, button, calls, statuses, context, get renderCount() { return renderCount; } };
}

function assertSend(call) {
  assert.deepEqual(call, {
    url: '/api/session/dsh-send',
    payload: { session_dir: '/offline/artpkg/session', confirmation },
  });
}

for (const [name, dsh, notice] of [
  ['missing handoff', undefined, 'DSH bridge is unavailable.'],
  ['unavailable', { available: false, unmet_conditions: ['Configure the bridge first.'] }, 'Configure the bridge first.'],
  ['empty conditions', { available: false, unmet_conditions: [] }, 'DSH is unavailable'],
]) {
  test(`${name}: sending is disabled without network activity`, async () => {
    const h = harness(dsh);
    const send = h.button('Send to DSH');
    assert.equal(send.disabled, true);
    await send.click();
    assert.ok(h.area.textContent.includes(notice));
    assert.equal(h.all('input').length, 0);
    assert.equal(h.calls.length, 0);
  });
}

test('confirmation gates sending; one click disables controls and success renders the returned session', async () => {
  const pending = deferred();
  const h = harness(ready(), () => pending.promise);
  const send = h.button('Send to DSH');
  const [check] = h.all('input');
  assert.equal(check.type, 'checkbox');
  assert.equal(check.checked, false);
  assert.equal(send.disabled, true);
  assert.ok(h.area.textContent.includes(confirmation));
  await send.click();
  assert.equal(h.calls.length, 0);
  check.setChecked(true);
  assert.equal(send.disabled, false);
  check.setChecked(false);
  assert.equal(send.disabled, true);
  check.setChecked(true);

  const sending = send.click();
  assert.equal(send.disabled, true);
  assert.equal(check.disabled, true);
  await send.click();
  check.setChecked(false);
  assert.equal(check.checked, true);
  assert.equal(h.calls.length, 1);
  assertSend(h.calls[0]);
  assert.equal(h.renderCount, 0);
  const returned = sessionWith(ready({ result: result() }));
  pending.resolve(returned);
  await sending;
  assert.equal(h.context.session, returned);
  assert.equal(h.renderCount, 1);
  assert.deepEqual(h.statuses, ['DSH handoff recorded; semantic assessment remains advisory']);
  assert.equal(h.all('input').length, 0);
  for (const text of ['PROMPT_SENT', 'review-session-123', 'offline-provider / offline-model', 'NOT_VERIFIED — advisory only']) {
    assert.ok(h.area.textContent.includes(text), `Missing result field: ${text}`);
  }
  assert.equal(h.all('button').some((button) => button.textContent === 'Send to DSH'), false);
});

test('failed send stays disabled until explicit reconfirmation', async () => {
  const h = harness(ready(), () => { throw new Error('offline failure'); });
  const original = h.context.session;
  const send = h.button('Send to DSH');
  const [check] = h.all('input');
  check.setChecked(true);
  await send.click();
  assert.equal(h.context.session, original);
  assert.equal(h.renderCount, 0);
  assert.deepEqual(h.statuses, ['DSH handoff: offline failure']);
  assert.equal(check.disabled, false);
  assert.equal(check.checked, false);
  assert.equal(send.disabled, true);
  await send.click();
  assert.equal(h.calls.length, 1);
  check.setChecked(true);
  assert.equal(send.disabled, false);
  await send.click();
  assert.equal(h.calls.length, 2);
  h.calls.forEach(assertSend);
  assert.equal(send.disabled, true);
  assert.equal(check.checked, false);
});

for (const status of ['DELIVERY_UNCERTAIN', 'PROMPT_DISPATCHING']) {
  test(`${status}: no resend or resume; transcript read remains available`, async () => {
    const pending = deferred();
    const h = harness(ready({ result: result(status) }), () => pending.promise);
    assert.match(h.area.textContent, /Automatic resend is disabled/);
    assert.deepEqual(h.all('button').map((button) => button.textContent), ['Read initial review transcript']);
    assert.equal(h.all('input').length, 0);
    assert.equal(h.calls.length, 0);
    const read = h.button('Read initial review transcript');
    const reading = read.click();
    assert.equal(read.disabled, true);
    await read.click();
    assert.deepEqual(h.calls, [{
      url: '/api/session/dsh-transcript', payload: { session_dir: '/offline/artpkg/session' },
    }]);
    pending.resolve({ notice: 'Cached advisory history', messages: [{ text: 'Review response' }] });
    await reading;
    assert.equal(read.disabled, false);
    assert.equal(h.renderCount, 0);
    assert.equal(h.all('pre')[0].textContent, 'Review response');
  });
}

for (const status of ['SESSION_PREPARING', 'SESSION_CREATED']) {
  test(`${status}: prepared handoff resumes once and renders success`, async () => {
    const pending = deferred();
    const h = harness(ready({ result: result(status) }), () => pending.promise);
    const resume = h.button('Resume prepared DSH handoff');
    assert.equal(h.all('input').length, 0);
    const resuming = resume.click();
    assert.equal(resume.disabled, true);
    await resume.click();
    assert.equal(h.calls.length, 1);
    assertSend(h.calls[0]);
    const returned = sessionWith(ready({ result: result() }));
    pending.resolve(returned);
    await resuming;
    assert.equal(h.context.session, returned);
    assert.equal(h.renderCount, 1);
    assert.equal(h.all('button').some((button) => button.textContent.includes('Resume')), false);
  });
}

test('prepared resume failure restores its button and reports the error', async () => {
  const h = harness(ready({ result: result('SESSION_CREATED') }), () => { throw new Error('resume failed'); });
  const resume = h.button('Resume prepared DSH handoff');
  await resume.click();
  assert.equal(resume.disabled, false);
  assert.equal(h.renderCount, 0);
  assertSend(h.calls[0]);
  assert.deepEqual(h.statuses, ['DSH handoff: resume failed']);
});

test('Open DSH preserves the root URL without adding session IDs or tokens and isolates the new tab', () => {
  const dsh = ready({ result: result(), token: 'must-not-leak' });
  const h = harness(dsh);
  const [link] = h.all('a');
  assert.equal(h.all('a').length, 1);
  assert.equal(link.textContent, 'Open DSH');
  assert.equal(link.target, '_blank');
  assert.deepEqual(link.rel.split(/\s+/).sort(), ['noopener', 'noreferrer']);
  // The renderer passes through chat_url; this checks the server's root-URL
  // contract, not sanitization of an arbitrary or malicious supplied URL.
  assert.equal(link.href, dsh.result.chat_url);
  const url = new URL(link.href);
  assert.equal(url.pathname, '/');
  assert.equal(url.search, '');
  assert.equal(url.hash, '');
  assert.equal(url.username, '');
  assert.equal(url.password, '');
  assert.equal(link.href.includes(dsh.token), false);
  assert.equal(link.href.includes(dsh.result.dsh_session_id), false);
  assert.equal(h.calls.length, 0);
});

test('untrusted transcript stays literal text; refresh clears previous output and handles empty history', async () => {
  const attack = '<img src=x onerror="globalThis.pwned=true"><script>globalThis.pwned=true</script>&lt;b&gt;';
  let reads = 0;
  const h = harness(ready({ result: result() }), () => ++reads === 1
    ? { notice: attack, messages: [{ text: attack }, { text: 'Second response\nwith lines' }] }
    : { notice: 'Fresh cached history' });
  const read = h.button('Read initial review transcript');
  await read.click();
  assert.deepEqual(h.all('pre').map((node) => node.textContent), [attack, 'Second response\nwith lines']);
  assert.ok(h.all('p').some((node) => node.textContent === attack));
  assert.ok(h.all('pre').every((node) => node.children.length === 0));
  assert.equal(h.all('img').length, 0);
  assert.equal(h.all('script').length, 0);
  assert.equal(h.context.pwned, undefined);
  await read.click();
  assert.equal(read.disabled, false);
  assert.equal(h.all('pre').length, 0);
  assert.equal(h.area.textContent.includes(attack), false);
  assert.match(h.area.textContent, /No bound review response is visible in this cached history yet/);
  assert.equal(h.calls.length, 2);
  assert.ok(h.calls.every((call) => call.url === '/api/session/dsh-transcript'));
});

test('transcript failure renders a text warning and allows another read', async () => {
  const message = '<img src=x onerror=alert(1)> transcript unavailable';
  const h = harness(ready({ result: result() }), () => { throw new Error(message); });
  const read = h.button('Read initial review transcript');
  await read.click();
  assert.equal(read.disabled, false);
  const warnings = h.all('p').filter((node) => node.className === 'warning');
  assert.equal(warnings.length, 1);
  assert.equal(warnings[0].textContent, message);
  assert.equal(warnings[0].children.length, 0);
  assert.equal(h.renderCount, 0);
  await read.click();
  assert.equal(h.calls.length, 2);
  assert.equal(h.all('p').filter((node) => node.className === 'warning').length, 1);
});