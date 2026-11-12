import provenance from "../../data/sentence-audio-provenance.json";
import type { Atlas, Entry } from "../atlas/types";

/** Same character folding as scoring, then lowercase, so a recording script can be compared. */
export function normalizeSentence(text: string) {
  return text
    .normalize("NFKC")
    .replace(/[’‘]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/[‐‑–—]/g, "-")
    .replace(/\s/g, " ")
    .toLowerCase();
}

const verified = provenance.verified as Record<string, Record<string, string>>;

/** True only when this card's current sentence is the script the on-disk recording was made from. */
export function sentenceRecordingMatches(id: string, index: number, text: string) {
  const script = verified[id]?.[String(index)];
  return !!script && script === normalizeSentence(text);
}

/** Sentence files that do not match the current example are withheld. Word clips are untouched. */
export function exampleAudioUrl(atlas: Atlas, entry: Entry, index: number) {
  const text = entry.ex[index]?.en;
  if (!text || !sentenceRecordingMatches(entry.id, index, text)) return null;
  return atlas.audio(entry, index === 0 ? "ex" : "ex2");
}
