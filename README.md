<div align="center">

# 高考词图 · Gaokao Word Map

**一词一画，看图记高考词。**

约 2197 个高考英语核心词。一词一画，例句、英美发音，和一套刚刚好的复习节奏。<br>
免费，开源，无需注册。不是官方考纲。

[**打开高考词图 →**](https://penny0531.github.io/word-atlas-gaokao/) &nbsp;·&nbsp; [下载词库](data/) &nbsp;·&nbsp; [English](README.en.md)

![MIT](https://img.shields.io/badge/code-MIT-1E2640) ![CC BY 4.0](https://img.shields.io/badge/content-CC%20BY%204.0-C4573A) ![words](https://img.shields.io/badge/words-2197-7F9B77) ![FSRS](https://img.shields.io/badge/scheduler-FSRS%206-D9A03A) ![no login](https://img.shields.io/badge/login-not%20required-6F93AE)

基于 [词光 Word Atlas](https://github.com/designfuchen/word-atlas) contributors（词光）。代码 MIT，词库与媒体 CC BY 4.0。

</div>

---

高考词图 fork 自 Word Atlas（词光）：交互、四种主动回忆题型、FSRS、词汇星图和声音设计都留着，词表换成高考英语核心词。现在有 2197 个词：先是约 200 个精选词，再按 wordfreq 的 Zipf 频率分十批补进考纲里还没有的高频词；O.K. 与 okay、p.m. 与 pm、PC 与 p.c. 各合并成一条。后面再扩到约 3,500。

背单词最难的不是“看过”，而是“想得起来”。每个词一幅画，让你先看见它；主动回忆让你想起它；FSRS 在你快要忘记的时候让你和它重逢。学会一个，星图上就多一颗星。

## 一眼看懂

| 数量 | 内容 |
|---:|---|
| **2197** | 高考英语核心词，CEFR A1–B2，沿用 19 个话题旋臂 |
| **2042** | 幅复古图鉴插画。能对上的词复用词光原作（CC BY 4.0）；没有原文件的词先不配图 |
| **4387** | 条例句：一条日常或校园短句，一条高考语境长句 |
| **2035** | 个词有英音和美音词头录音。没有上游词头文件的词，词头仍用设备朗读 |
| **4368** | 条新例句录音，本地 Kokoro `af_heart`，美式，语速 1.0。另有 19 条原文仍匹配的上游例句录音保留 |
| **0** | 账号、广告、追踪。进度只在你自己的设备上 |

## 看一看

插画是词光的复古图鉴，依法署名后复用。重合词的第一条例句已按高考语境改写，所以有的画面对的是上游那句场景，不完全等于现在的例句。上游没有原画的七个词用了新绘的同风格图，不借用别的词的画。

<table>
<tr>
<td align="center" width="25%"><img src="public/atlas/img/abandon.webp" alt="abandon" width="100%"><br><b>abandon</b><br>放弃；遗弃</td>
<td align="center" width="25%"><img src="public/atlas/img/ancient.webp" alt="ancient" width="100%"><br><b>ancient</b><br>古代的；古老的</td>
<td align="center" width="25%"><img src="public/atlas/img/anxiety.webp" alt="anxiety" width="100%"><br><b>anxiety</b><br>焦虑</td>
<td align="center" width="25%"><img src="public/atlas/img/achieve.webp" alt="achieve" width="100%"><br><b>achieve</b><br>达到；完成</td>
</tr>
<tr>
<td align="center" width="25%"><img src="public/atlas/img/accident.webp" alt="accident" width="100%"><br><b>accident</b><br>事故；意外</td>
<td align="center" width="25%"><img src="public/atlas/img/approach.webp" alt="approach" width="100%"><br><b>approach</b><br>方法；靠近</td>
<td align="center" width="25%"><img src="public/atlas/img/admire.webp" alt="admire" width="100%"><br><b>admire</b><br>钦佩；羡慕</td>
<td align="center" width="25%"><img src="public/atlas/img/announce.webp" alt="announce" width="100%"><br><b>announce</b><br>宣布</td>
</tr>
</table>

拿 *abandon* 听词头发音（仓库里的原录音，词头仍然对得上）：

| | |
|---|---|
| 英音 | [abandon /əˈbændən/](public/atlas/audio/uk/abandon.mp3) |
| 美音 | [abandon /əˈbændən/](public/atlas/audio/us/abandon.mp3) |

界面音效、星空音乐和环境声沿用词光的 `public/sfx/`。开屏口播和屏幕文案都是「欢迎打开高考词图」。`public/sfx/splash-voice.mp3` 已换成这句，不再播放上游的「欢迎打开雅思大门」。

## 每个词都有什么

| | |
|---|---|
| 🖼 **一幅插画** | 2042 个词有图，优先复用词光原画。没有原文件的词先以文字学习，不借用别的词的图。 |
| 🔊 **英美发音** | 词头英音、美音仍是词光原录音。「英式 / 美式」只切换词头。例句是当前英文的美式 Kokoro `af_heart` 录音；原文仍匹配的上游例句录音保留。 |
| ✍️ **例句** | `ex[0]` 日常或校园短句；多数词还有 `ex[1]` 高考语境长句，配中文翻译。 |
| 📚 **中英释义** | 最多 3 个义项，按高考里更常见的意思排在前面。 |
| 💡 **提示** | 易混词和用法陷阱，例如 affect / effect。 |

## 词汇星图

2197 个词就是 2197 颗星。19 个话题仍各占一条旋臂。简单的词靠近中心，难的在外缘。拖动旋转、滚动缩放，点一颗星打开词卡。

## 怎么帮你记住

- **主动回忆**：看义选词、看图补句、听音辨词、拼写。
- **FSRS 间隔复习**：和新版 Anki 同款的开源算法，目标记忆率可调。
- **诚实计分**：只算第一次作答。答错会换个题型再练，不抬高正确率。
- **从你的水平开始**：基础、进阶、中高、冲刺，对应 A2 到 C1，跳过已经熟悉的词。
- **打字工作室、声音、离线、分享卡、备份**：都还在。进度存在浏览器里，没有账号。

## 词库

`data/` 里是这 2197 个词，内容 **CC BY 4.0**。请署名 Word Atlas contributors（词光），并说明做过修改。选词说明见 [data/batch-2-notes.md](data/batch-2-notes.md)、[data/batch-3-notes.md](data/batch-3-notes.md)、[data/batch-4-notes.md](data/batch-4-notes.md)、[data/batch-5-notes.md](data/batch-5-notes.md)、[data/batch-6-notes.md](data/batch-6-notes.md)、[data/batch-7-notes.md](data/batch-7-notes.md)、[data/batch-8-notes.md](data/batch-8-notes.md)、[data/batch-9-notes.md](data/batch-9-notes.md)、[data/batch-10-notes.md](data/batch-10-notes.md) 和 [data/batch-11-notes.md](data/batch-11-notes.md)。

| 文件 | 内容 |
|---|---|
| [`data/word-atlas.json`](data/word-atlas.json) | 结构化数据，可选 `meta.gaokaoFreq` |
| [`data/word-atlas.csv`](data/word-atlas.csv) | 表格版 |
| `public/atlas/` | 网页用的索引、分块词条；插画和音频仍在原目录，没用到的上游文件先留着 |

```json
{
  "id": "abandon",
  "w": "abandon",
  "uk": "/əˈbændən/",
  "us": "/əˈbændən/",
  "senses": [{ "pos": "v.", "zh": "放弃；遗弃", "en": "to leave or give up" }],
  "ex": [
    { "en": "We had to abandon the plan after the storm.", "zh": "暴风雨过后我们不得不放弃那个计划。" },
    { "en": "Cities should not abandon ambitious recycling programmes simply because initial participation rates are lower than expected.", "zh": "城市不应仅因初期参与率低于预期，就放弃雄心勃勃的回收计划。" }
  ],
  "cefr": "B2",
  "topic": "society"
}
```

字段说明见 [docs/dataset.md](docs/dataset.md)。

## 本地运行

需要 Node.js 20+。完整插画和音频体积很大，请用线上预览，或只在内存够的机器上克隆。

```bash
git clone https://github.com/penny0531/word-atlas-gaokao.git
cd word-atlas-gaokao
npm ci
npm run dev
```

打开 `http://localhost:5188`。

```bash
npm test
npm run check:atlas
ATLAS_BASE=/word-atlas-gaokao/ npm run build
```

GitHub Pages workflow 已把 `ATLAS_BASE` 设为 `/word-atlas-gaokao/`。部署说明见 [docs/deployment.md](docs/deployment.md)。

## 内容从哪来

- 产品壳、题型、星图、音效来自 [词光 Word Atlas](https://github.com/designfuchen/word-atlas)。
- 有原文件的词复用词光的插画和词头录音，署名 Word Atlas contributors（词光）。例句按当前英文用本地 Kokoro `af_heart`（美式，语速 1.0）合成；原文未改、仍能对上的上游例句录音保留，不会被当成英音。
- 第二批里的 27 个高频词没有原图原音。`absorb`、`aware`、`calculate`、`conclude`、`daily`、`entire`、`likely` 有同风格新图，仍没有词头英音或美音。

> **诚实说明**：这不是教育部、考试院或任何官方考纲词表，也不承诺提分。内容经过结构校验，没有逐条人工审校。发现问题请提 Issue，或直接改 `data/` 提 PR。

## 授权

- 代码：[MIT](LICENSE)
- 词库文本、插画、录音：[CC BY 4.0](CONTENT_LICENSE.md)，署名 “Word Atlas contributors（词光）”
- 字体 Fraunces：SIL Open Font License；记忆算法 [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs)：MIT

<div align="center">

如果高考词图帮到了你，点一颗 ⭐️，也算帮它点亮一颗星。

</div>
