import assert from "node:assert/strict";
import { test } from "node:test";
import { exampleAudioUrl, exampleClipAccent, normalizeSentence, sentenceRecordingMatches } from "./sentenceAudio";
import type { Atlas, Entry } from "../atlas/types";

const concentrate = "It is hard to concentrate in a noisy room.";
const concentrateLong =
  "Governments should concentrate resources on preventive healthcare to reduce pressure on hospitals in the long term.";
const upstreamConcentrate = "I cannot concentrate with the television playing so loudly.";

test("a recording is withheld when the sentence is not the stored script", () => {
  assert.equal(sentenceRecordingMatches("concentrate", 0, upstreamConcentrate), false);
  assert.equal(sentenceRecordingMatches("concentrate", 0, "It is hard to concentrate."), false);
  assert.equal(normalizeSentence("It’s Fine."), "it's fine.");
});

test("Heart recordings use the current sentence and are marked US, while the retained high clip stays British", () => {
  assert.equal(sentenceRecordingMatches("concentrate", 0, concentrate), true);
  assert.equal(sentenceRecordingMatches("concentrate", 1, concentrateLong), true);
  assert.equal(exampleClipAccent("concentrate", 0), "us");
  assert.equal(exampleClipAccent("concentrate", 1), "us");
  assert.equal(exampleClipAccent("high", 0), "uk");
  assert.equal(exampleClipAccent("no-such-word", 0), null);
  assert.equal(sentenceRecordingMatches("high", 0, "The shelf is too high for me to reach."), true);
  assert.equal(sentenceRecordingMatches("high", 0, "The shelf is too high."), false);
});

test("example audio url stays null unless the current sentence is verified", () => {
  const entry = {
    id: "concentrate",
    ex: [
      { en: concentrate, zh: "在嘈杂的房间里很难集中注意力。" },
      { en: concentrateLong, zh: "" },
    ],
  } as Entry;
  const atlas = {
    audio: (ref: { id: string }, kind: string) => `/atlas/audio/${kind}/${ref.id}.mp3`,
  } as unknown as Atlas;
  assert.equal(exampleAudioUrl(atlas, entry, 0), "/atlas/audio/ex/concentrate.mp3");
  assert.equal(exampleAudioUrl(atlas, entry, 1), "/atlas/audio/ex2/concentrate.mp3");
  const edited = {
    ...entry,
    ex: [{ en: "It is hard to concentrate.", zh: "" }],
  } as Entry;
  assert.equal(exampleAudioUrl(atlas, edited, 0), null);
  const high = {
    id: "high",
    ex: [{ en: "The shelf is too high for me to reach.", zh: "" }],
  } as Entry;
  assert.equal(exampleAudioUrl(atlas, high, 0), "/atlas/audio/ex/high.mp3");
  assert.equal(exampleAudioUrl(atlas, high, 1), null);
});
