'use strict';
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {test} = require('node:test');
const vm = require('node:vm');
const html = readFileSync(require('node:path').join(__dirname, '../tools/artpkg_final_review.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
class Element {
  constructor() { this.children = []; this.checked = false; this.disabled = false; this.hidden = false; }
  set innerHTML(_) { assert.fail('Do not interpret package content as HTML'); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(name, value) { this[name] = value; }
  focus() { this.focused = true; }
  select() { this.selected = true; }
  click() { if (!this.disabled) return this.onclick?.(); }
  check() { if (!this.disabled) { this.checked = true; this.onchange?.(); } }
}
const preview = () => ({basis_sha256:'digest', review_current:false, confirmation:'review-confirmation',
  prepare_confirmation:'prepare-confirmation', context:{project:'<script>bad()</script>', purpose:'DISCOVERY',
  objective:'Calculator', in_scope:'Python', out_of_scope:'Cloud', record_counts:{components:0},
  records:{questions:[{id:'Q-B001',fields:{current_disposition:'OPEN'}}]}, open_questions:[{id:'Q-B001'}]},
  source:{sha256:'source-hash',text:'<img src=x onerror=bad()>'}, package_markdown:'<script>bad()</script>',
  validation_markdown:'PASS', sealing:{package_id:'PKG-123', package_version:1, sealed:false,
    completion_result:'READY_TO_SEAL', confirmation_text:'seal-confirmation', sealed_id:'seal-hash', target_binding:null}});
async function harness(initial = preview(), handler = async () => {throw Error('unexpected POST');}) {
  const nodes = new Map([...html.matchAll(/id="([^"]+)"/g)].map(match => [match[1], new Element()]));
  nodes.get('actionError').hidden = true;
  for (const [, id, text] of html.matchAll(/<button id="([^"]+)"[^>]*>([^<]*)<\/button>/g)) {
    nodes.get(id).textContent = text.replaceAll('&amp;', '&');
  }
  const calls = [], copied = [];
  const context = vm.createContext({URL, URLSearchParams, location:{search:'?dir=%2Fowned%2Fsession'},
    document:{getElementById:id => nodes.get(id),createElement:() => new Element()},
    navigator:{clipboard:{writeText:async text => copied.push(text)}},
    fetch:async (url, opts) => {
      calls.push({url, body:opts?.body ? JSON.parse(opts.body) : null});
      return {ok:true,json:async () => opts?.method === 'POST' ? handler(url, JSON.parse(opts.body))
        : url.startsWith('/api/session?') ? {pipeline_admission: initial.pipeline || {
          result:initial.sealing.sealed ? {admission_status:'ACCEPTED'} : null}} : JSON.parse(JSON.stringify(initial))};
    }});
  await vm.runInContext(script, context);
  return {nodes, calls, copied, context, node:id=>nodes.get(id)};
}
test('initial review renders literal evidence, no automatic writes or DSH calls', async () => {
  const h = await harness();
  assert.equal(h.calls.length, 2);
  assert.equal(h.node('package').textContent, '<script>bad()</script>');
  assert.match(h.node('source').textContent, /onerror/);
  assert.ok(h.node('approve').disabled);
  assert.ok(h.node('prepare').disabled);
  h.node('reviewAck').check();
  assert.equal(h.node('approve').disabled, false);
  assert.ok(h.node('seal').disabled);
});
test('old seal without saved final review explains locked steps and disables their checkboxes', async () => {
  const p = preview(); p.sealing.sealed = true;
  const h = await harness(p);
  h.node('reviewAck').check();
  assert.match(h.node('reviewNotice').textContent, /not saved yet/);
  assert.equal(h.node('approve').disabled, false);
  for (const id of ['sealAck', 'prepareAck']) {
    assert.ok(h.node(id).disabled);
    h.node(id).check();
    assert.equal(h.node(id).checked, false);
  }
  assert.match(h.node('sealHint').textContent, /clicking Save review & continue/);
  assert.match(h.node('prepareHint').textContent, /step 1/);
  assert.equal(h.calls.length, 2);
  assert.equal(h.node('reviewActions').hidden, false);
  assert.equal(h.node('sealActions').hidden, true);
  assert.equal(h.node('prepareActions').hidden, true);
});
test('saved review unlocks only sealing, sealed revision unlocks preparation', async () => {
  const p = preview(); p.review_current = true;
  const h = await harness(p);
  assert.equal(h.node('sealAck').disabled, false);
  assert.equal(h.node('prepareAck').disabled, true);
  assert.equal(h.node('approve').textContent, 'Final review recorded');
  assert.equal(h.node('reviewActions').hidden, true);
  assert.equal(h.node('sealActions').hidden, false);
  const sealed = await harness({...p,sealing:{...p.sealing,sealed:true}});
  assert.equal(sealed.node('sealAck').disabled, true);
  assert.equal(sealed.node('prepareAck').disabled, false);
  assert.match(sealed.node('sealHint').textContent, /already sealed/);
  assert.equal(sealed.node('sealActions').hidden, true);
  assert.equal(sealed.node('prepareActions').hidden, false);
});
test('sealed without admission offers admission retry, not a dead-end preparation button', async () => {
  const p = preview(); p.review_current = true; p.sealing.sealed = true; p.pipeline = {result:null};
  const h = await harness(p);
  assert.equal(h.node('sealActions').hidden, false);
  assert.equal(h.node('sealAck').disabled, false);
  assert.equal(h.node('prepareActions').hidden, true);
  assert.match(h.node('nextExplanation').textContent, /retries admission/);
});
test('review submits displayed digest and exact confirmation, then resets checks', async () => {
  const p = preview();
  const h = await harness(p, async (url, body) => {
    assert.equal(url, '/api/session/final-review');
    assert.equal(body.basis_sha256, 'digest');
    assert.equal(body.confirmation, 'review-confirmation');
    assert.equal(body.session_dir, '/owned/session');
    return {...p,review_current:true};
  });
  h.node('reviewAck').check(); await h.node('approve').click();
  assert.ok(h.node('approve').disabled);
  assert.equal(h.node('reviewAck').checked, false);
  h.node('sealAck').check(); assert.equal(h.node('seal').disabled, false);
  assert.ok(h.node('prepare').disabled);
});
test('bottom continuation stays consent-gated and saves only the review', async () => {
  const p = preview();
  const h = await harness(p, async (url, body) => {
    assert.equal(url, '/api/session/final-review');
    assert.equal(body.basis_sha256, 'digest');
    assert.equal(body.confirmation, 'review-confirmation');
    return {...p, review_current:true};
  });
  assert.equal(h.node('continueAction').textContent, 'Save review & continue →');
  assert.equal(h.node('continueAction').disabled, true);
  await h.node('continueAction').click();
  assert.equal(h.calls.filter(c=>c.body).length, 0);
  h.node('reviewAck').check();
  assert.equal(h.node('continueAction').disabled, false);
  assert.match(h.node('continueHint').textContent, /Save your review/);
  await h.node('continueAction').click();
  assert.equal(h.calls.filter(c=>c.body).length, 1);
  assert.equal(h.node('continueAction').textContent, 'Seal & continue →');
  assert.equal(h.node('continueAction').disabled, true);
  assert.equal(h.node('continueDsh').hidden, true);
});
test('bottom continuation resets when confirmation is unchecked and never bypasses blockers', async () => {
  const h = await harness();
  h.node('reviewAck').check();
  h.node('reviewAck').checked = false; h.node('reviewAck').onchange();
  assert.equal(h.node('continueAction').disabled, true);
  const p = preview(); p.review_current = true; p.sealing.completion_result = 'NOT_READY';
  const blocked = await harness(p);
  assert.equal(blocked.node('continueAction').disabled, true);
  assert.match(blocked.node('continueHint').textContent, /blocked/);
});
test('ready coding handoff exposes copyable prompts without dispatching them', async () => {
  const p = preview(); p.review_current = true; p.sealing.sealed = true;
  const h = await harness(p, async (url, body) => {
    assert.equal(url, '/api/session/coding-prepare');
    assert.equal(body.sealed_id, 'seal-hash');
    assert.equal(body.confirmation, 'prepare-confirmation');
    return {workspace:'/host/Downloads/project', dsh_session_id:'code-session', provider:'test',model:'local',
      execution_approval:'REQUIRES_DSH_HUMAN_APPROVAL',chat_url:'http://127.0.0.1:3080/',
      prompts:[{title:'Plan',text:'Read the reviewed requirements.'}]};
  });
  h.node('prepareAck').check(); await h.node('continueAction').click();
  assert.equal(h.node('result').hidden, false);
  assert.equal(h.node('continueAction').hidden, true);
  assert.equal(h.node('continueDsh').hidden, false);
  assert.equal(h.node('continueDsh').href, 'http://127.0.0.1:3080/');
  assert.equal(h.node('openDsh').href, 'http://127.0.0.1:3080/');
  const copy = h.node('prompts').children[2]; await copy.click();
  assert.deepEqual(h.copied, ['Read the reviewed requirements.']);
  assert.equal(h.calls.length, 3);
  assert.equal(h.node('prepareActions').hidden, true);
  assert.match(h.node('nextTitle').textContent, /Continue in DSH/);
  assert.match(h.node('status').textContent, /copied/);
});
test('prepare failure exposes no result and never sends a fallback prompt', async () => {
  const p = preview(); p.review_current = true; p.sealing.sealed = true;
  const h = await harness(p, async () => {throw Error('DSH unavailable');});
  h.node('prepareAck').check(); await h.node('prepare').click();
  assert.equal(h.node('status').textContent, 'DSH unavailable');
  assert.equal(h.node('result').hidden, true);
  assert.equal(h.calls.length, 3);
  assert.equal(h.node('actionError').textContent, 'DSH unavailable');
});
test('browser navigation supports LAN origin but never token-bearing links', async () => {
  const p = preview(); p.review_current = true; p.sealing.sealed = true;
  for (const url of ['http://192.168.1.163:3080/', 'http://192.168.1.163:3080/?token=SYNTHETIC', 'javascript:alert(1)']) {
    const h = await harness(p, async () => ({chat_url:url, prompts:[]}));
    h.node('prepareAck').check(); await h.node('prepare').click();
    if (url === 'http://192.168.1.163:3080/') {
      assert.equal(h.node('openDsh').href, url);
      assert.equal(h.node('continueDsh').href, url);
      assert.equal(h.node('result').hidden, false);
    } else {
      assert.equal(h.node('result').hidden, true);
      assert.equal(h.node('actionError').textContent, 'Invalid DSH origin');
    }
  }
});
test('seal carries review digest and does not silently prepare a coding session', async () => {
  const p = preview(); p.review_current = true;
  const h = await harness(p, async (url, body) => {
    assert.equal(url, '/api/session/seal');
    assert.equal(body.review_basis_sha256, 'digest');
    assert.equal(body.reviewed, true); return {};
  });
  h.node('sealAck').check(); await h.node('continueAction').click();
  assert.equal(h.calls.filter(c=>c.body).length, 1);
});
test('intake makes coding review primary and nests legacy actions under advanced details', () => {
  const intake = readFileSync(require('node:path').join(__dirname, '../tools/artpkg_intake_ui.html'), 'utf8');
  const source = intake.slice(intake.indexOf('    function renderSealing()'), intake.indexOf('    function render()'));
  class Node {
    constructor(tag) { this.tag = tag; this.children = []; this.textContent = ''; }
    set innerHTML(_) { this.children = []; }
    appendChild(child) { this.children.push(child); return child; }
    append(...children) { children.forEach(child => this.appendChild(child)); }
  }
  for (const admitted of [false, true]) {
    const area = new Node('div');
    const context = vm.createContext({document:{getElementById:()=>area,createElement:tag=>new Node(tag)},
      session:{session_dir:'/owned/session',sealing:{completion_result:'READY_TO_SEAL',sealed:admitted,sealed_id:'abc'},
        pipeline_admission:{available:true,eligible:true,result:admitted ? {admission_status:'ACCEPTED'} : null}},
      appendText(parent, tag, cls, text) { const node = new Node(tag); node.textContent = text; parent.appendChild(node); return node; },
      sealField(){},sealList(){},sealResolvableList(){},
      renderDshReview(parent) { const node = new Node('button'); node.textContent='Send to DSH'; parent.appendChild(node); }
    });
    vm.runInContext(source, context); context.renderSealing();
    assert.ok(area.children.some(n=>n.tag==='a' && n.textContent.includes('Continue to final review')));
    assert.equal(area.children.some(n=>n.tag==='button'), false);
    const advanced = area.children.find(n=>n.tag==='details');
    assert.ok(advanced.children[0].textContent.startsWith('Advanced:'));
    if (admitted) assert.ok(advanced.children.some(n=>n.textContent==='Send to DSH'));
    else assert.ok(advanced.children.some(n=>n.tag==='details' && n.children[0].textContent.startsWith('Legacy:')));
  }
});