<div align="center">

# 词光·高考 · Word Atlas

**One word, one picture. Light up Gaokao vocabulary.**<br>
About 200 core words · examples · reused illustrations and UK/US audio · FSRS spaced repetition

[**Open the app →**](https://penny0531.github.io/word-atlas-gaokao/) &nbsp;·&nbsp; [Download the dataset](data/) &nbsp;·&nbsp; [中文](README.md)

Based on [Word Atlas](https://github.com/designfuchen/word-atlas) contributors（词光）. Code MIT. Content CC BY 4.0.

</div>

---

词光·高考 is a Gaokao fork of Word Atlas. The interface, four recall question types, FSRS scheduler, word galaxy and sound design stay. The 7,298-word IELTS list is replaced by about 200 high-frequency Gaokao English words (a later pass can grow toward ~3,500).

It is free, needs no account, and keeps progress on the device. The UI is in Chinese. This is not an official curriculum list and it does not promise a higher score.

| | |
|---:|---|
| **200** | Gaokao core entries, CEFR A1–B2, the same 19 topic arms |
| **193** | illustrations and voiced headwords reused from Word Atlas (CC BY 4.0) |
| **393** | example sentences |
| **7** | entries with text only, until art and audio exist: absorb, aware, calculate, conclude, daily, entire, likely |
| **0** | accounts, ads or trackers |

Illustrations keep the upstream retro field-guide style. Where the everyday example was rewritten, the picture and the example recording may still show the original Word Atlas scene. Headword audio still matches the word. Please credit **Word Atlas contributors（词光）**.

## What every entry has

- Senses in Chinese, with a short English gloss, ordered for Gaokao use.
- A short everyday or school sentence, and usually a longer Gaokao-register sentence.
- Collocations, word family, synonyms, antonyms and one tip when the source entry has them.
- CEFR level and one of the original 19 topics. Nature and sport have no words in this slice, so those galaxy arms stay dark.

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
