#!/usr/bin/env node
/** Batch 12 only: count, outline membership, Zipf order, and example shape. */
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
const batch = data.filter((e) => e.meta && e.meta.batch === 12);
if (batch.length !== 200) fail(`batch 12 count ${batch.length} != 200`);
if (data.length !== 2197 + batch.length) fail(`total ${data.length} != 2197 + ${batch.length}`);

const skip = new Set(["a","an","the","be","am","is","are","was","were","been","being","i","you","he","she","it","we","they","me","him","her","us","them","my","your","his","its","our","their","and","or","but","of","to","no."]);
for (const e of batch) {
  const key = e.w.toLowerCase();
  if (!outline.has(key) && !outline.has(e.id)) fail(`not in outline: ${e.id}`);
  if (skip.has(key)) fail(`function word: ${e.id}`);
  if (e.cefr !== "B1" || e.meta.gaokaoFreq !== "high" || e.meta.zipf > 4.22) fail(`meta ${e.id}`);
  if (!Array.isArray(e.ex) || e.ex.length !== 2 || e.ex.some((x) => !x.en || !x.zh)) fail(`examples ${e.id}`);
  const stem = e.w.toLowerCase().split(" ")[0].replace(/(e|y)$/, "").slice(0, 5);
  if (!e.ex[0].en.toLowerCase().includes(stem)) fail(`stem ${e.id}`);
  if (!e.uk || !e.us) fail(`ipa ${e.id}`);
}

const ordered = [...batch].sort((a, b) => b.meta.zipf - a.meta.zipf || a.id.localeCompare(b.id));
if (ordered[0].id !== "dig" || ordered[0].meta.zipf !== 4.22) fail(`start ${ordered[0] && ordered[0].id}`);
if (ordered[ordered.length - 1].id !== "preference") fail(`end ${ordered[ordered.length - 1] && ordered[ordered.length - 1].id}`);
const old = data.filter((e) => !(e.meta && e.meta.batch === 12));
if (old.some((e) => e.id === "departure" && e.meta.zipf !== 4.22)) fail("departure moved");

console.log(JSON.stringify({
  total: data.length,
  batch: batch.length,
  outline: outline.size,
  start: ordered[0] && [ordered[0].meta.zipf, ordered[0].id],
  end: ordered.at(-1) && [ordered.at(-1).meta.zipf, ordered.at(-1).id],
  errors: errors.length,
}, null, 2));
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
