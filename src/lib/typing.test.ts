import assert from "node:assert/strict";
import { test } from "node:test";
import { applyDictationAdvance, clean, commitAtEnd, dictationAdvanceLabel, dictationCanAdvance, resetDictationItem, same, showDictationAnswer, typingDelta, typingMetrics, typingSlots } from "./typing";

test("typing counts inserted characters and does not reward deletions", () => {
  assert.deepEqual(typingDelta("", "c", "cat"), { total: 1, correct: 1 });
  assert.deepEqual(typingDelta("c", "cx", "cat"), { total: 1, correct: 0 });
  assert.deepEqual(typingDelta("cx", "c", "cat"), { total: 0, correct: 0 });
  assert.deepEqual(typingDelta("cat", "cat", "cat"), { total: 0, correct: 0 });
});

test("a corrected mistake remains in the cumulative accuracy denominator", () => {
  let total = 0,
    correct = 0,
    previous = "";
  for (const value of ["c", "cx", "c", "ca", "cat"]) {
    const delta = typingDelta(previous, value, "cat");
    total += delta.total;
    correct += delta.correct;
    previous = value;
  }
  assert.deepEqual(typingMetrics(correct, total, 3, 6000), {
    accuracy: 75,
    wpm: 6,
  });
});

test("replacement and middle insertion assess only new characters at their new positions", () => {
  assert.deepEqual(typingDelta("cxt", "cat", "cat"), { total: 1, correct: 1 });
  assert.deepEqual(typingDelta("cat", "cart", "cart"), {
    total: 1,
    correct: 1,
  });
  assert.deepEqual(typingDelta("cart", "cat", "cat"), { total: 0, correct: 0 });
  assert.deepEqual(typingDelta("cat", "cats", "cat"), { total: 1, correct: 0 });
});

test("case and equivalent smart punctuation are accepted, punctuation is still required", () => {
  assert.ok(same("Cat", "cat"));
  assert.ok(same("It’s fine.", "It's fine."));
  assert.ok(!same("Its fine", "It's fine."));
  assert.ok(!same("cat ", "cat"));
  assert.deepEqual(typingDelta("", "Cat", "cat"), { total: 3, correct: 3 });
  assert.equal(clean("Ａ—Ｂ"), "A-B");
});

test("IME commits or multi-character replacements are assessed as one insertion", () => {
  assert.deepEqual(typingDelta("", "hello", "hello"), { total: 5, correct: 5 });
  assert.deepEqual(typingDelta("hel", "hello", "hello"), {
    total: 2,
    correct: 2,
  });
  assert.deepEqual(typingDelta("hello", "hello", "hello"), {
    total: 0,
    correct: 0,
  });
  assert.deepEqual(typingDelta("", "你好", "hello"), { total: 2, correct: 0 });
});

test("WPM uses five characters per word and excludes discarded error characters", () => {
  assert.deepEqual(typingMetrics(200, 250, 200, 60000), {
    accuracy: 80,
    wpm: 40,
  });
  assert.deepEqual(typingMetrics(150, 150, 150, 30000), {
    accuracy: 100,
    wpm: 60,
  });
});

test("an untouched or subsecond round never reports infinite or misleading WPM", () => {
  assert.deepEqual(typingMetrics(0, 0, 0, 0), { accuracy: 100, wpm: 0 });
  assert.equal(typingMetrics(1, 1, 1, 20).wpm, 0);
  assert.equal(typingMetrics(50, 50, 50, 999).wpm, 0);
});

test("normalized ligatures count as the same displayed characters", () => {
  assert.deepEqual(typingDelta("", "oﬃce", "office"), { total: 6, correct: 6 });
  assert.deepEqual(typingDelta("oﬃce", "office", "office"), { total: 0, correct: 0 });
});

test("decomposed accents normalize before positions and accuracy are assessed", () => {
  assert.deepEqual(typingDelta("", "cafe\u0301", "café"), { total: 4, correct: 4 });
  assert.deepEqual(typingDelta("café", "cafe\u0301", "café"), { total: 0, correct: 0 });
});

test("supplementary Unicode characters do not shift the following letter positions", () => {
  assert.deepEqual(typingDelta("", "𝔸B", "AB"), { total: 2, correct: 2 });
  assert.deepEqual(typingDelta("", "🙂a", "🙂a"), { total: 2, correct: 2 });
});

test("source nonbreaking spaces match keyboard spaces but omitted punctuation does not", () => {
  assert.ok(same("a b", "a\u00a0b"));
  assert.deepEqual(typingDelta("", "a b", "a\u00a0b"), { total: 3, correct: 3 });
  assert.ok(!same("well being", "well-being"));
});

test("a mobile caret insert is committed at the end and still matches the target", () => {
  assert.equal(commitAtEnd("he", "lhe"), "hel");
  assert.equal(commitAtEnd("he", "hle"), "hel");
  assert.equal(commitAtEnd("he", "hel"), "hel");
  assert.equal(commitAtEnd("hel", "he"), "he");
  assert.equal(commitAtEnd("abcd", "ad"), "ab");
  assert.equal(commitAtEnd("", "h"), "h");
  assert.equal(commitAtEnd("hello", "hello"), "hello");
  assert.deepEqual(typingSlots(commitAtEnd("he", "lhe"), "hello"), ["ok", "ok", "ok", "empty", "empty"]);
  assert.deepEqual(typingSlots("Cafe\u0301", "café"), ["ok", "ok", "ok", "ok"]);
  assert.deepEqual(typingSlots("It’s", "It's"), ["ok", "ok", "ok", "ok"]);
});

test("revealing a dictation answer keeps the typed attempt and does not advance", () => {
  const target = "Hello there.";
  const attempt = "Hel";
  const shown = showDictationAnswer(attempt);
  assert.equal(shown.revealed, true);
  assert.equal(shown.value, attempt);
  assert.notEqual(shown.value, target);
  assert.equal(shown.advance, false);
  assert.equal(same(shown.value, target), false);
  assert.equal(same(target, target), true);
});

test("dictation next stays blocked until the sentence matches, then advances once", () => {
  const target = "Exercise can benefit both body and mind.";
  const wrong = "excerise can benefit both body and mind.";
  assert.equal(dictationCanAdvance("", target), false);
  assert.equal(dictationCanAdvance("   ", target), false);
  assert.equal(dictationCanAdvance(wrong, target), false);
  assert.equal(dictationCanAdvance("Exercise", target), false);
  assert.equal(dictationCanAdvance(target + " extra", target), false);
  assert.equal(dictationCanAdvance(target.slice(0, -1), target), false);
  assert.equal(dictationCanAdvance(target, target), true);
  assert.equal(dictationCanAdvance(target.toLowerCase(), target), true);
  assert.equal(dictationCanAdvance(target + "  ", target), true);
  assert.equal(dictationCanAdvance("  " + target, target), false);
  assert.equal(showDictationAnswer(wrong).advance, false);
  assert.equal(showDictationAnswer(wrong).value, wrong);

  const start = { claimed: false, index: 1, count: 10 };
  const blocked = applyDictationAdvance(start, wrong, target);
  assert.deepEqual(blocked, { claimed: false, index: 1, done: false, advanced: false });
  const empty = applyDictationAdvance(start, "", target);
  assert.equal(empty.advanced, false);
  assert.equal(empty.index, 1);

  const corrected = applyDictationAdvance(start, target, target);
  assert.deepEqual(corrected, { claimed: true, index: 2, done: false, advanced: true });
  const again = applyDictationAdvance({ claimed: true, index: 1, count: 10 }, target, target);
  assert.deepEqual(again, { claimed: true, index: 1, done: false, advanced: false });

  const firstTry = applyDictationAdvance({ claimed: false, index: 0, count: 3 }, target.toLowerCase(), target);
  assert.equal(firstTry.advanced, true);
  assert.equal(firstTry.index, 1);
  assert.equal(firstTry.done, false);
  const entered = applyDictationAdvance({ claimed: false, index: 0, count: 3 }, target, target);
  assert.deepEqual(entered, firstTry);

  const finale = applyDictationAdvance({ claimed: false, index: 9, count: 10 }, target, target);
  assert.deepEqual(finale, { claimed: true, index: 9, done: true, advanced: true });
  assert.equal(dictationAdvanceLabel(0, 10), "下一页");
  assert.equal(dictationAdvanceLabel(9, 10), "完成练习");
  const finaleBlocked = applyDictationAdvance({ claimed: false, index: 9, count: 10 }, wrong, target);
  assert.equal(finaleBlocked.done, false);
  assert.equal(finaleBlocked.advanced, false);
});

test("a new dictation sentence hides the answer and clears the attempt", () => {
  assert.deepEqual(resetDictationItem(), { revealed: false, value: "" });
  const shown = showDictationAnswer("Hel");
  const fresh = resetDictationItem();
  assert.equal(fresh.revealed, false);
  assert.equal(fresh.value, "");
  assert.notEqual(fresh.value, shown.value);
});

test("metrics never emit NaN, Infinity, negatives or accuracy above 100", () => {
  assert.deepEqual(typingMetrics(20, 10, 10, 60000), { accuracy: 100, wpm: 2 });
  assert.deepEqual(typingMetrics(-1, 10, -10, 60000), { accuracy: 0, wpm: 0 });
  assert.deepEqual(typingMetrics(NaN, Infinity, 2, Infinity), { accuracy: 100, wpm: 0 });
});
