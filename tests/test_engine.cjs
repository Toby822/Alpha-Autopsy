'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const E=require('../web/engine.js'),R=JSON.parse(fs.readFileSync(path.join(__dirname,'../research/results.json'),'utf8'));
assert.equal(R.dataset.observations,731);assert.equal(R.candidates.length,10);assert.equal(R.chosen,'momentum-2');
assert.equal(R.daily.close[0],44230.2);assert.equal(R.daily.close.at(-1),87608.2);
const out=E.candidate(R,R.chosen,10);
for(const phase of ['train','validate','test']){
const actual=out.segments[phase],saved=R.candidates.find(x=>x.id===R.chosen)[phase];
for(const k of ['return','sharpe','mean_bps','annualised_vol','max_drawdown','trades']){
 assert.ok(Math.abs(actual[k]-saved[k])<1e-7,phase+' '+k+' '+actual[k]+' '+saved[k]);
}
}
const diag=E.diagnostics(R,out,10);assert.ok(Math.abs(diag.placebo.p-R.holdout_shift_placebo.one_sided_p)<1e-12);
assert.ok(Math.abs(diag.placebo.actual-R.holdout_shift_placebo.observed_bps)<1e-7);
const cost0=E.candidate(R,R.chosen,0),cost20=E.candidate(R,R.chosen,20);
assert.ok(cost0.segments.test.return>=out.segments.test.return);
assert.ok(out.segments.test.return>=cost20.segments.test.return);
assert.throws(()=>E.compute(R.daily.close,'momentum',5,-3));
const mutated=R.daily.close.slice();mutated[680]*=1.5;
const before=E.compute(R.daily.close,'momentum',5,10),after=E.compute(mutated,'momentum',5,10);
assert.deepEqual(before.position.slice(0,680),after.position.slice(0,680));
assert.ok(E.diagnostics(R,out,10).ci.every(Number.isFinite));
const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const frontend=fs.readFileSync(path.join(__dirname,'../web/app.js'),'utf8');
for(const match of frontend.matchAll(/\$\('([a-zA-Z0-9_-]+)'\)/g)){
 assert.ok(html.includes('id="'+match[1]+'"'),'Missing HTML id '+match[1]);
}
console.log('ALPHA AUTOPSY PASS: Python/JS parity, selection, fee identity, lookahead, statistics, DOM and provenance.');