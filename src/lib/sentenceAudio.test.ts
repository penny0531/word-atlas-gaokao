import assert from "node:assert/strict";
import { test } from "node:test";
import { exampleAudioUrl, normalizeSentence, sentenceRecordingMatches } from "./sentenceAudio";
import type { Atlas, Entry } from "../atlas/types";

const concentrate = "It is hard to concentrate in a noisy room.";
const upstreamConcentrate = "I cannot concentrate with the television playing so loudly.";

test("a reused recording is withheld when the current sentence is not its script", () => {
  assert.equal(sentenceRecordingMatches("concentrate", 0, concentrate), false);
  assert.equal(sentenceRecordingMatches("concentrate", 0, upstreamConcentrate), false);
  assert.equal(normalizeSentence("It’s Fine."), "it's fine.");
});

test("the one first-example recording whose script still matches may play", () => {
  assert.equal(sentenceRecordingMatches("high", 0, "The shelf is too high for me to reach."), true);
  assert.equal(sentenceRecordingMatches("high", 0, "The shelf is too high."), false);
});

test("example audio url stays null unless the current sentence is verified", () => {
  const entry = {
    id: "concentrate",
    ex: [{ en: concentrate, zh: "在嘈杂的房间里很难集中注意力。" }],
  } as Entry;
  const atlas = {
    audio: (ref: { id: string }, kind: string) => `/atlas/audio/${kind}/${ref.id}.mp3`,
  } as unknown as Atlas;
  assert.equal(exampleAudioUrl(atlas, entry, 0), null);
  const high = {
    id: "high",
    ex: [{ en: "The shelf is too high for me to reach.", zh: "" }],
  } as Entry;
  assert.equal(exampleAudioUrl(atlas, high, 0), "/atlas/audio/ex/high.mp3");
  assert.equal(exampleAudioUrl(atlas, high, 1), null);
});
