'use strict';
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {test} = require('node:test');
const vm = require('node:vm');
const html = readFileSync(require('node:path').join(__dirname, '../tools/artpkg_ux_preparation.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
class Element {
  constructor(){this.children=[];this.disabled=false;this.checked=false;this.value='';this.files=[];this.listeners={};}
  set innerHTML(_){assert.fail('Untrusted proposal must never be interpreted as HTML');}
  addEventListener(name,fn){this.listeners[name]=fn;}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  click(){if(!this.disabled)return this.listeners.click?.();}
}
function harness(responder, dir='/owned/session'){
  const nodes=new Map([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],new Element()]));
  for(const [,id] of html.matchAll(/<button id="([^"]+)" disabled/g)) nodes.get(id).disabled=true;
  const calls=[], downloads=[];
  const context=vm.createContext({URLSearchParams,TextDecoder,Blob,
    URL:{createObjectURL:()=> 'blob:synthetic',revokeObjectURL:()=>{}},
    location:{search:dir?'?dir='+encodeURIComponent(dir):'',assign:url=>{context.assigned=url;}},
    document:{getElementById:id=>nodes.get(id),querySelectorAll:()=>[...nodes.values()],createElement:()=>{const e=new Element();downloads.push(e);return e;}},
    fetch:async(url,options)=>{const call={url,options,body:options?.body?JSON.parse(options.body):null};calls.push(call);return {ok:true,json:async()=>responder(call)};}});
  vm.runInContext(script,context);
  return {nodes,calls,context,node:id=>nodes.get(id),downloads};
}
const uploaded={upload_id:'a'.repeat(32),preview:'<img src=x onerror=attack()>',normalized:{blockers:[]}};
const resolution={questions:[],status:{complete:false,undecided:[]},reported_blockers:[],authority:'NONE'};
const preview={...uploaded,basis_sha256:'b'.repeat(64),attestation:'EXACT SYNTHETIC CATALOG ATTESTATION',
  basis:{items:[{key:'answer/answers/PKG-001',text:'<script>not executable</script>',status:'PROVIDED',item_sha256:'c'.repeat(64),requirement_type:null}]},
  normalized:{blockers:[],tables:{scope:[['PKG-001','answer/answers','Exact text','revision','PROVIDED','NO','EXCLUDE','uploaded exclusion NOT authority']]}}};
async function upload(h){h.node('file').files=[{name:'new.md',size:10,arrayBuffer:async()=>new TextEncoder().encode('Synthetic Markdown').buffer}];await h.node('upload').click();}

test('UX page initializes without network or automatic approval',()=>{
  const h=harness(()=>{throw Error('unexpected request');});
  assert.equal(h.calls.length,0);assert.equal(h.node('attest').checked,false);
  assert.equal(h.node('run').disabled,true);assert.equal(h.node('review').disabled,true);
});
test('upload stores literal preview and enables only preparation review',async()=>{
  const h=harness(call=>call.url.includes('op=resolution')?resolution:uploaded);await upload(h);
  assert.equal(h.node('preview').textContent,uploaded.preview);
  assert.equal(h.node('loadReview').disabled,false);assert.equal(h.node('run').disabled,true);
  assert.equal(h.calls.length,2);assert.equal(h.calls[0].options.headers['X-ArtPkg-UX'],'1');
  assert.equal(h.calls[0].body.filename,'new.md');
});
test('catalog approval requires explicit checkbox and exact displayed basis, exclusions are not prefilled',async()=>{
  const h=harness(call=>call.url.endsWith('ux-upload')?uploaded:call.url.includes('op=resolution')?resolution:call.body?{status:'READY_FOR_UX_PROCESSING'}:preview);
  await upload(h);await h.node('loadReview').click();
  assert.equal(h.node('decisions').children[0].children[1].textContent,preview.basis.items[0].text);
  const textarea=h.node('decisions').children[0].children[2].children[0];
  assert.equal(textarea.value,'');
  await h.node('review').click();assert.equal(h.calls.length,3);
  h.node('attest').checked=true;textarea.value='Human: administrative metadata outside product scope';
  await h.node('review').click();
  const body=h.calls.at(-1).body;
  assert.equal(body.basis_sha256,preview.basis_sha256);assert.equal(body.attestation,preview.attestation);
  assert.equal(body.exclusions['answer/answers/PKG-001'].item_sha256,'c'.repeat(64));
  assert.equal(body.exclusions['answer/answers/PKG-001'].reason,textarea.value);
  assert.equal(h.node('run').disabled,false);
  assert.ok(h.calls.every(c=>!c.url.includes('/approve')&&!c.url.includes('dsh')&&!c.url.includes('pipeline')));
});
test('no project session disables all actions',()=>{
  const h=harness(()=>{throw Error('unexpected request');},'');
  assert.equal(h.node('upload').disabled,true);assert.match(h.node('status').textContent,/owned questionnaire/);
});
test('UI has no executable raw HTML or remote render sink',()=>{
  assert.doesNotMatch(script,/innerHTML|insertAdjacentHTML|eval\(|new Function/);
  assert.match(html,/No UX approval or implementation authorization/);
});