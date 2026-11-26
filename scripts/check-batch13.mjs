#!/usr/bin/env node
/** Batch 13: count, outline membership, Zipf window, and CEFR rule. */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const data = JSON.parse(fs.readFileSync(path.join(root, "data/word-atlas.json"), "utf8"));
const outlinePath = process.env.OUTLINE || "/tmp/gaokao-outline.txt";
const errors = [];
const fail = (msg) => errors.push(msg);

const outline = new Set();
for (const line of fs.readFileSync(outlinePath, "utf8").split("\n")) {
  const raw = line.trim();
  if (!raw || raw.startsWith("#")) continue;
  outline.add(raw.split("\t")[0].trim().toLowerCase());
}

const ids = new Set();
for (const e of data) {
  if (ids.has(e.id)) fail(`duplicate id ${e.id}`);
  ids.add(e.id);
}
const batch = data.filter((e) => e.meta && e.meta.batch === 13);
if (batch.length !== 200) fail(`batch 13 count ${batch.length} != 200`);
if (data.length !== 2397 + batch.length) fail(`total ${data.length} != 2397 + ${batch.length}`);

const allowed = new Set(["A1", "A2", "B1", "B2", "C1", "C2"]);
function zipfBand(z) {
  if (z >= 6.4) return "A1";
  if (z >= 5.9) return "A2";
  if (z >= 4.18) return "B1";
  if (z >= 3.74) return "B2";
  return "C1";
}
const cefr = JSON.parse(fs.readFileSync(path.join(root, "data/batch-13-cefr.json"), "utf8"));
const byId = new Map(cefr.map((row) => [row.id, row]));
const dist = {};
for (const e of batch) {
  const key = e.w.toLowerCase();
  if (!outline.has(key) && !outline.has(e.id)) fail(`not in outline: ${e.id}`);
  if (!allowed.has(e.cefr)) fail(`bad cefr ${e.id}`);
  if (e.meta.gaokaoFreq !== "high" || e.meta.batch !== 13) fail(`meta ${e.id}`);
  if (e.meta.zipf > 4.11) fail(`zipf before window ${e.id} ${e.meta.zipf}`);
  if (!Array.isArray(e.ex) || e.ex.length !== 2 || e.ex.some((x) => !x.en || !x.zh)) fail(`examples ${e.id}`);
  const stem = e.w.toLowerCase().split(" ")[0].replace(/(e|y)$/, "").slice(0, 5);
  if (!e.ex[0].en.toLowerCase().includes(stem) && !e.ex[1].en.toLowerCase().includes(stem)) fail(`stem ${e.id}`);
  if (!e.uk || !e.us || !e.uk.startsWith("/") || !e.us.startsWith("/")) fail(`ipa ${e.id}`);
  const row = byId.get(e.id);
  if (!row) fail(`no cefr audit ${e.id}`);
  else if (row.cefr !== e.cefr || row.zipfBand !== zipfBand(e.meta.zipf)) fail(`cefr rule ${e.id}`);
  dist[e.cefr] = (dist[e.cefr] || 0) + 1;
}

const ordered = [...batch].sort((a, b) => b.meta.zipf - a.meta.zipf || a.id.localeCompare(b.id));
if (ordered[0].id !== "selfish" || ordered[0].meta.zipf !== 4.11) fail(`start ${ordered[0] && ordered[0].id}`);
if (ordered.at(-1).id !== "bean") fail(`end ${ordered.at(-1) && ordered.at(-1).id}`);
const old = data.filter((e) => !(e.meta && e.meta.batch === 13));
if (old.length !== 2397) fail(`old count ${old.length}`);
if (old.some((e) => e.id === "preference" && e.meta.zipf !== 4.11)) fail("preference moved");

console.log(JSON.stringify({
  total: data.length,
  batch: batch.length,
  outline: outline.size,
  start: ordered[0] && [ordered[0].meta.zipf, ordered[0].id],
  end: ordered.at(-1) && [ordered.at(-1).meta.zipf, ordered.at(-1).id],
  cefr: dist,
  errors: errors.length,
}, null, 2));
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
