import fs from 'node:fs';
import ts from 'typescript';
const script=JSON.parse(fs.readFileSync('explainer-script.json','utf8'));
const manifest=JSON.parse(fs.readFileSync('public/explainer-captures/capture-manifest.json','utf8'));
const clean=text=>String(text).replaceAll('|','\\|').replaceAll('\n','<br>');
const lines=['# Diode Sentinel explainer — claims trace','',
  'Source of truth: `../VIDEO-BRIEF.md` §§9–11. UI values come from the fresh recorded synthetic replay authorized in §11. This is not a performance or accuracy benchmark.','',
  '## Narration and scene copy','',
  '| Scene | On-screen label and headline | Spoken copy | Brief sections |','|---|---|---|---|'];
for(const s of script) lines.push(`| ${s.id} | ${clean(s.label)}<br>${clean(s.title)} | ${clean(s.text)} | ${s.briefSections.join(', ')}; §11 approved production copy |`);
lines.push('', '## Shared production text','',
  '| Exact text | Origin |','|---|---|',
  '| Diode Sentinel; samarags; Built by samarags | §§9–11 |',
  '| See everything. Touch nothing. | §§10–11; positioning, not perfect-coverage assurance |',
  '| Recorded software · Synthetic replay | §§9–11; required demonstration qualifier |',
  '| Illustrative diagram · Receive-side observations | §§10–11; illustrative context qualifier |','',
  '## Diagram copy and numbers','',
  'Authored diagram wording below is flagged as **added wording**: it explains behavior in §10 but is not a verbatim quote from the brief. Labels are original editorial copy, not additional product claims. Illustrative 10 + 10 = 20 pairs, ten-second windows and a sixty-second horizon are explicitly authorized in §10.','',
  '| Exact authored literal | Brief basis | Status |','|---|---|---|');
const source=ts.createSourceFile('Graphics.tsx',fs.readFileSync('src/explainer/Graphics.tsx','utf8'),ts.ScriptTarget.Latest,true,ts.ScriptKind.TSX);
const found=new Set();
function visit(node){
  if(ts.isJsxText(node)&&node.getText(source).trim())found.add(node.getText(source).trim());
  if(ts.isJsxAttribute(node)&&['title','sub'].includes(node.name.getText(source))&&node.initializer&&ts.isStringLiteral(node.initializer))found.add(node.initializer.text);
  if(ts.isCallExpression(node)&&['tag','title'].includes(node.expression.getText(source))&&node.arguments[0]&&ts.isStringLiteral(node.arguments[0]))found.add(node.arguments[0].text);
  if(ts.isArrayLiteralExpression(node)&&node.elements.length===2&&node.elements.every(ts.isStringLiteral))for(const el of node.elements)found.add(el.text);
  ts.forEachChild(node,visit);
}
visit(source);
for(const text of [...found].sort())lines.push(`| ${clean(text)} | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |`);
lines.push('', 'Dynamic characters in the domain-label diagram spell the generic illustrative label `domainlabel`. Dynamic rolling count is the illustrative integers 0–20; 10 and 20 are fixture arithmetic, not observed production throughput. Decorative packet glyphs, card layouts, timing markers and scene progress are illustrative design.','',
  '## Recorded dashboard text and numbers','',
  'Every text block below was extracted from the actual visible component at the end of its recording. Other visible dashboard chrome and values are captured in the snapshots and the full synthetic `alerts.jsonl`; per-clip actions and the selected original records are stored in `capture-manifest.json`. No dashboard value is replaced by generated text.','',
  `Fresh capture: ${manifest.scenario?.packets_total} packets, including ${manifest.scenario?.fixture_packets} focused fixture packets; ${manifest.pipeline_alerts?.count} recorded alerts with the enabled demonstration tiers. Basis: §11, capture manifest and synthetic replay. These are demonstration counts, not archived regression counts.`, '');
for(const [name,clip] of Object.entries(manifest.clips)){
  lines.push(`### ${name}`,'', `Brief: §§9–11. File: ${name}.mp4. Exact recorded UI text:`, '', '```text',clip.visibleText??'', '```','');
}
lines.push('## Exact selected records and captured interactions','',
  'These original synthetic records supply all displayed detector values, addresses, timestamps, scores and model inputs. Qualifiers are retained in the software and the surrounding Synthetic replay caption.','',
  '```json',JSON.stringify(manifest.selected_records,null,2),'```','',
  'Recorded cursor/filter actions and their timing (these are action logs, not additional detector measurements):','',
  '```json',JSON.stringify(manifest.interactions,null,2),'```','');
lines.push('## All replay record values and dynamic counters','',
  'The live Seen and Analyzed counters progress through actual replay counts up to 14,171, with 0 sampled out. Queue, severity, source, category and origin counts change as these records arrive or filters change. Their brief basis is §11: recorded synthetic replay values, with the Synthetic replay qualifier. This section preserves the entire 108-record stream, including every original score/address/time/measurement that may appear in the dashboard table. No counter state is a performance benchmark.','',
  '```jsonl',fs.readFileSync('public/explainer-captures/alerts.jsonl','utf8').trim(),'```','');
lines.push('## Export and evidence provenance','',
  'Selected alert identities, recorded model inputs and scores are the original pipeline records in the capture manifest. Downloaded bundles are listed under `downloads`, with original-record hashes, filters and explicit provenance availability. The alert-record SHA-256 is not packet provenance or legal chain of custody.','',
  '## Additions not in the brief','',
  'The diagram wording enumerated above and original visual artwork are added editorial content. Scene labels/headlines and narration are registered in §11 by their source file. There are no invented capabilities, accuracy figures, threat verdicts, calibrated probabilities, team members, event wins or product URLs.');
fs.writeFileSync('EXPLAINER-CLAIMS-TRACE.md',lines.join('\n')+'\n');
console.log(`Traced ${script.length} narrated scenes, ${found.size} diagram literals and ${Object.keys(manifest.clips).length} recorded components.`);
