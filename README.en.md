<div align="center">

# 高考词图 · Gaokao Word Map

**One picture per word. Learn Gaokao words from the picture.**<br>
About 3197 core words · examples · reused illustrations and UK/US audio · FSRS spaced repetition

[**Open the app →**](https://penny0531.github.io/word-atlas-gaokao/) &nbsp;·&nbsp; [Download the dataset](data/) &nbsp;·&nbsp; [中文](README.md)

Based on [Word Atlas](https://github.com/designfuchen/word-atlas) contributors（词光）. Code MIT. Content CC BY 4.0.

</div>

---

Gaokao Word Map is a fork of Word Atlas（词光）. The interface, four recall question types, FSRS scheduler, word galaxy and sound design stay. The playable list is 3197 Gaokao English words so far (a later pass can grow toward ~3,500). The order is public Zipf frequency, not an official exam ranking. Later batches add the next highest-frequency outline headwords that are not already included. O.K. and okay are one entry, and so are p.m. and pm, and PC and p.c. Spelling pairs such as favour and favor, realise and realize, judgment and judgement, and harbor and harbour stay as separate headwords.

It is free, needs no account, and keeps progress on the device. The UI is in Chinese. This is not an official curriculum list and it does not promise a higher score.

| | |
|---:|---|
| **3197** | Gaokao core entries, CEFR A1–C1, the same 19 topic arms |
| **2927** | field-guide illustrations. Reused from Word Atlas where the catalog id matches, including the British-spelling plates copied earlier for meter, fiber, harbor, humor and neighbor. 54 further plates were drawn locally with a free tool in that same style. Batch 14 leaves 32 new headwords without a plate, Batch 15 leaves 39, and Batch 16 leaves 44 |
| **6387** | example sentences |
| **3035** | headwords with UK and US clips. Words with no upstream file use local Kokoro (`bf_emma` for UK, `af_heart` for US). Older cards that already had no headword clip stay on device TTS |
| **6368** | example recordings, local Kokoro af_heart, US English, speed 1.0. 19 upstream example clips whose text still matched were kept |
| **0** | accounts, ads or trackers |

Illustrations keep the upstream retro field-guide style. Where the everyday example was rewritten, the picture may still show the original Word Atlas scene. Example clips are new US recordings of the current sentence (Kokoro voice af_heart, speed 1.0), except upstream clips whose text still matches and were kept. They are not British. Headword UK/US clips that came from Word Atlas are unchanged. Fifty-four headwords that had no upstream file are new local Kokoro recordings of the isolated word: UK `bf_emma` (en-gb), US `af_heart` (en-us), speed 1.0. Those 54 also have new plates drawn locally with a free tool in the field-guide style. meter, fiber, harbor, humor and neighbor reuse the unused British-spelling files metre, fibre, harbour, humour and neighbour. The accent control still picks the headword clip only. Please credit **Word Atlas contributors（词光）**. absorb, aware, calculate, conclude, daily, entire, and likely were not in the upstream set: they now have new plates in that style, and they still have no headword audio. The splash line, on screen and spoken, is 「欢迎打开高考词图」. The product name remains 高考词图. Batch 14 adds 200 headwords after bean: 168 reuse an unused upstream plate and headword clip with the same catalog id, and 32 have new Kokoro headword clips and no plate. Details: [data/media-fill-notes.md](data/media-fill-notes.md), [data/batch-14-notes.md](data/batch-14-notes.md), [data/batch-15-notes.md](data/batch-15-notes.md) and [data/batch-16-notes.md](data/batch-16-notes.md). Batch 15 adds 200 outline headwords after referee, from relay (Zipf 3.86) through appoint (Zipf 3.70). 161 reuse an unused upstream plate and UK/US clip under the same catalog id. 39 have no plate; their headword clips are local Kokoro. Batch 16 adds 200 outline headwords from capsule (Zipf 3.70) through annoy (Zipf 3.46). 156 reuse an unused upstream plate and UK/US clip under the same catalog id. 44 have no plate; their headword clips are local Kokoro. No new images were generated.

## What every entry has

- Senses in Chinese, with a short English gloss, ordered for Gaokao use.
- A short everyday or school sentence, and usually a longer Gaokao-register sentence.
- Collocations, word family, synonyms, antonyms and one tip when the source entry has them.
- CEFR level and one of the original 19 topics. All 19 galaxy arms now have words.

## The dataset (CC BY 4.0)

- [`data/word-atlas.json`](data/word-atlas.json) and [`data/word-atlas.csv`](data/word-atlas.csv)
- Runtime index and chunks in `public/atlas/`. Unused upstream media files are left in place.

Field reference: [docs/dataset.md](docs/dataset.md).

## Run it

```bash
npm ci
npm run dev        # http://localhost:5188
npm test
npm run check:atlas
ATLAS_BASE=/word-atlas-gaokao/ npm run build
```

The Pages workflow already sets `ATLAS_BASE=/word-atlas-gaokao/`. Preview: <https://penny0531.github.io/word-atlas-gaokao/>.

## License

Code: [MIT](LICENSE). Word content, illustrations and recordings: [CC BY 4.0](CONTENT_LICENSE.md), attribution “Word Atlas contributors（词光）”.
