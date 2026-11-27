# 第十四批选词 / Batch 14 selection

这一批从第十三批终点 `bean`（wordfreq 3.1.1 英语 Zipf **3.98**）之后继续，加入 **200** 个考纲词头。全库从 2597 增到 **2797** 个词，例句从 5187 增到 **5587**。产品名仍是高考词图。已有 2597 张卡的正文、`cefr`、例句录音、开屏口播和已经配齐的媒体都没有改。没有合并，没有部署。

起点提交是已经合进 main 的媒体补缺 `056063d127b2518c20aed1023e061ea8ef8f5a79`。

## 频率来源

公开语料 [wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf，`zipf_frequency(word, "en")`。这不是官方考频。词表来自 MIT 许可的 [busiyiworld/maimemo-export](https://github.com/busiyiworld/maimemo-export) `exported/list/高考英语大纲词汇3500.txt`。文件有 3505 行词头、26 个字母标题；小写去重后是 **3487** 个词头。本批只从这 3487 个词头里选，没有发明词，也没有从任何打乱用的 XLS 里另取词。

多词或带连字符的形式会再试空格写法，取较高的 Zipf。本窗口里的词头都是单个词，Zipf 用的就是词头本身。排序键是两位小数 Zipf 从高到低，同一 Zipf 按 id 字母序。`bean` 之后、同一 3.98 上还排在它后面的词都算进窗口，所以本批从 **bicycle**（Zipf 3.98）开始，到 **referee**（Zipf 3.86）结束。

3.86 上排在 referee 之后、留给下一批的还有 4 个：relay、sunlight、taxpayer、yourselves。窗口里已经在库中、因而没有重复加入的是 admire、conclude、calculate、distinguish。

`bean` 之前还有 32 个考纲词头不在库里，本批不回头补：31 个是封闭类（the、to、and、of、a、i、is、you、it、be、are、he、but、my、or、we、an、your、his、they、me、their、her、she、them、its、our、him、us、being、am），外加早已并进 `p.m.` 的 `pm`。这和「从 bean 之后接着选」一致。

`meta.gaokaoFreq` 仍为 `high`，`meta.batch` 为 14。

## 难度

`cefr` 沿用第十三批写明的学习路线，不是考试院分数。门槛仍是 CEFR-J Wordlist 1.6 ALL_sep 词头的 wordfreq 中位数：

- Zipf ≥ 6.4 → A1
- Zipf ≥ 5.9 → A2
- Zipf ≥ 4.18 → B1
- Zipf ≥ 3.74 → B2
- 低于 3.74 → C1

交叉来源仍是《CEFR-J Wordlist Version 1.6》ALL_sep（东京外国语大学投野由纪夫研究室）。词头与本卡第一义项的词性一致时，采用表里的等级。词性对不上、或词头不在表里时，不用别的词性的等级，改用 Zipf 分段。本窗口的 Zipf 分段本身全是 B2。两套都记在 `data/batch-14-cefr.json`。没有改已有卡的 `cefr`。

171 个词采用同词性的 CEFR-J 等级。29 个没有同词性标签，留在 Zipf 分段 B2：

hydrogen, mistaken, porter, bachelor, grasp, portable, explicit, preview, collision, homeland, mainland, swap, acre, directory, overhead, lounge, pioneer, chorus, confidential, shuttle, fist, sincerely, geometry, socialism, alley, surplus, fragile, maid, mistress

其中 `grasp` 在 CEFR-J 里只有名词。本卡第一义项是动词「抓住；理解」，所以不用名词那一档，改用 Zipf 分段。

新词的 `cefr` 分布：

| 等级 | 词数 |
| --- | ---: |
| A1 | 14 |
| A2 | 39 |
| B1 | 82 |
| B2 | 65 |
| C1 | 0 |
| C2 | 0 |

## 拼写

没有把两个还能分开搜索的拼写并成一条。已有卡的提示也没有改写。

- `harbour` 是英式。美式 `harbor` 已在库里，本卡用目录 id `harbour` 自己的上游文件。
- `neighbourhood` 是英式。美式 `neighborhood` 已在库里。
- `catalogue` 与 `catalog` 都在本窗口里，各用各的 id 和上游文件。
- `offence` 是英式。美式 offense 不在本库。
- `recognise` 是英式。美式 `recognize` 已在库里。
- `judgement` 是英式。美式 `judgment` 已在库里；那张旧卡仍写着自己的提示，本批没有改它。
- `organize`、`airplane` 用考纲里的美式拼写。英式 organise、aeroplane 不在本窗口。
- `mommy` 是口语。`mom` 与 `mum` 已在库里。

音标来自本机 espeak-ng 1.51，英式 `en-gb`、美式 `en-us`。重音移到元音前的音节头，闪音 `ɾ` 写成 `t`，`ɹ` 写成 `r`，成节辅音展开。少数重音或 TRAP 元音明显不对的，在 `scripts/build_batch14.py` 的 `IPA_OVERRIDE` 里改过，审计文件标成 `espeak-ng+override`。没有用打乱表里的音标。

## 媒体

168 个新词的目录 id 在 `public/atlas/` 里已经有未挂到任何卡上的上游插画、缩略图、英音和美音。id 与词头相同，文件按原路径使用，没有复制，也没有覆盖。`illustrated` 从 2442 增到 **2610**。

32 个新词没有同 id 的上游图，也没有同 id 的上游词头录音。本机没有免费的本地图像模型，也没有跑 `scripts/atlas/gen_images.py`（那个脚本调用付费图像接口）。这 32 张图留空，不借用别的词的画，也不把缺图说成有图：

needle, frontier, handy, hers, thorough, preview, tendency, collision, homeland, lame, squeeze, swap, arise, thankful, fierce, liberation, offshore, pioneer, gesture, fist, fry, gifted, mommy, voyage, alley, consult, dynasty, forehead, surplus, zip, maple, referee

这 32 个词的词头用本地 Kokoro 补了。美音 `af_heart`、`en-us`、语速 1.0；英音 `bf_emma`、`en-gb`、语速 1.0。只读孤立词头，单声道 44.1 kHz、64 kbps，尾部垫 0.08 秒。稿和 SHA-256 在 `data/batch-14-headword-audio.json`。先前那份 `data/headword-audio-provenance.json` 没有改。`voiced`（英音位）从 2435 增到 **2635**。更早那些本来就没有词头录音的卡，本批没有补。

新词的两条例句都用本地 Kokoro `af_heart`、美式、语速 1.0 录，400 条全部通过音素覆盖检查，没有时长离群，也没有调用付费接口。已经挂在旧卡上、原文还对得上的例句录音没有重录。全库例句录音现在是 5568 条 Kokoro，另有 19 条原文仍匹配的上游录音。开屏「欢迎打开高考词图」没有重录。

播放路径只有 `audio/ex/{id}.mp3` 和 `audio/ex2/{id}.mp3`。168 条第一条例句、17 条第二条例句的路径上原先有未挂到任何卡的上游录音，内容不是本批的新句子。这些文件换成了新句子的 Kokoro 录音，否则新卡会播错句子。原先 2597 张卡的例句文件一个都没改。被换掉的上游字节仍在起点提交 `056063d1` 里。

## 校验

- `npm test`：28 项通过。
- `npm run check:atlas`：2797 词，5587 条例句，illustrated 2610，英音 2635，美音 2635，例句录音 2797，第二条例句录音 2790，errors 0。`oneExample` 警告仍是 7，是原先只有一条例句的卡。
- `ATLAS_BASE=/word-atlas-gaokao/ npm run build`：通过。
- 没有合并，没有部署，没有推到 `main`。`backup/dark-before-light-2026-11-13` 仍是 `3ab32bbe6ee7df121bfdbcbc3000a815b3bb2269`。
