/** Normalize the typography mobile keyboards commonly substitute. */
export const clean = (text: string) =>
  text
    .normalize("NFKC")
    .replace(/[’‘]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/[‐‑–—]/g, "-")
    .replace(/\s/g, " ");
export const same = (a: string, b: string) =>
  clean(a).toLowerCase() === clean(b).toLowerCase();

/** Use normalized Unicode code points consistently for scoring and highlighting. */
export function correctCharacterCount(value: string, target: string) {
  const expected = Array.from(clean(target));
  return Array.from(clean(value)).filter((char, index) =>
    same(char, expected[index] || ""),
  ).length;
}

/**
 * Apply an input edit at the end of the previous answer.
 * A mobile tap on the hidden field moves the caret, so the browser may insert
 * the next letter in the middle. The lesson caret is always at the end, and
 * that letter would otherwise be compared with the wrong target character.
 */
export function commitAtEnd(previous: string, next: string) {
  if (next === previous) return next;
  const prev = Array.from(previous);
  const nxt = Array.from(next);
  let start = 0;
  while (start < prev.length && start < nxt.length && prev[start] === nxt[start]) start++;
  let endPrev = prev.length;
  let endNext = nxt.length;
  while (endPrev > start && endNext > start && prev[endPrev - 1] === nxt[endNext - 1]) {
    endPrev--;
    endNext--;
  }
  if (endPrev === prev.length) return next;
  const added = nxt.slice(start, endNext);
  const removed = endPrev - start;
  if (!added.length) return prev.slice(0, Math.max(0, prev.length - removed)).join("");
  return previous + added.join("");
}

export type TypingSlot = "ok" | "bad" | "empty";

/** Slot marks use the same normalization as scoring, one grapheme at a time. */
export function typingSlots(value: string, target: string): TypingSlot[] {
  const expected = Array.from(clean(target));
  const typed = Array.from(clean(value));
  return expected.map((char, index) => {
    const got = typed[index];
    if (got === undefined) return "empty";
    return same(got, char) ? "ok" : "bad";
  });
}

/** Opening the dictation answer leaves the attempt unchanged and does not finish the item. */
export function showDictationAnswer(value: string) {
  return { revealed: true as const, value, advance: false as const };
}

/** The next sentence starts hidden again, with an empty attempt. */
export function resetDictationItem() {
  return { revealed: false as const, value: "" };
}

/** Count newly inserted characters, including replacements, without rewarding deletions. */
export function typingDelta(previous: string, next: string, target: string) {
  const before = Array.from(clean(previous));
  const after = Array.from(clean(next));
  const expected = Array.from(clean(target));
  let prefix = 0;
  while (
    prefix < before.length &&
    prefix < after.length &&
    before[prefix] === after[prefix]
  ) prefix++;
  let suffix = 0;
  while (
    suffix < before.length - prefix &&
    suffix < after.length - prefix &&
    before[before.length - 1 - suffix] === after[after.length - 1 - suffix]
  ) suffix++;
  const added = after.slice(prefix, after.length - suffix);
  let correct = 0;
  for (let i = 0; i < added.length; i++) {
    if (same(added[i], expected[prefix + i] || "")) correct++;
  }
  return { total: added.length, correct };
}

/** Standard WPM uses 5 characters per word, not the number of vocabulary cards. */
export function typingMetrics(
  correctCharacters: number,
  attemptedCharacters: number,
  acceptedCharacters: number,
  elapsedMs: number,
) {
  const finiteNonnegative = (n: number) => Number.isFinite(n) ? Math.max(0, n) : 0;
  const attempted = finiteNonnegative(attemptedCharacters);
  const correct = Math.min(finiteNonnegative(correctCharacters), attempted);
  const accepted = finiteNonnegative(acceptedCharacters);
  const duration = finiteNonnegative(elapsedMs);
  return {
    accuracy: attempted ? Math.round((correct / attempted) * 100) : 100,
    wpm: duration >= 1000 ? Math.round(accepted / 5 / (duration / 60000)) : 0,
  };
}
