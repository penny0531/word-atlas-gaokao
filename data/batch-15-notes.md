# 第十五批选词 / Batch 15 selection

这一批从第十四批终点 `referee`（wordfreq 3.1.1 英语 Zipf **3.86**）之后继续，加入 **200** 个考纲词头。全库从 2797 增到 **2997** 个词，例句从 5587 增到 **5987**。产品名仍是高考词图。已有 2797 张卡的正文、`cefr`、例句录音、开屏口播和已经配齐的媒体都没有改。没有合并，没有部署。

起点提交是已经合进 main 的第十四批 `2fb93d13be5fcdc7dc3e1c6875df4800920415b4`。

## 频率来源

公开语料 [wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf，`zipf_frequency(word, "en")`。这不是官方考频。词表来自 MIT 许可的 [busiyiworld/maimemo-export](https://github.com/busiyiworld/maimemo-export) `exported/list/高考英语大纲词汇3500.txt`。`wc -l` 是 **3530**（最后一行没有换行符）。内容是 3505 行词头加 26 个 `#A`–`#Z` 标题；小写去重后是 **3487** 个词头。本批只从这 3487 个词头里选，没有发明词，也没有从任何打乱用的 XLS 里另取词。

多词或带连字符的形式会再试空格或连字符写法，取较高的 Zipf。本窗口里只有 `compact disk` 是两个词，两种写法的 Zipf 相同，排序用词头本身。排序键是两位小数 Zipf 从高到低，同一 Zipf 按 id 字母序。`referee` 之后、同一 3.86 上还排在它后面的 4 个词都算进窗口，所以本批从 **relay**（Zipf 3.86）开始，到 **appoint**（Zipf 3.70）结束。

3.70 上排在 appoint 之后、留给下一批的还有 10 个：capsule、compulsory、grape、haircut、rot、spear、stain、trousers、unwilling、whichever。下一批从 **capsule**（Zipf 3.70）开始。

窗口里已经在库中、因而没有重复加入的是 absorb（3.81）、distribute（3.79）、attach（3.75）。

`bean` 之前还有 32 个考纲词头不在库里，本批不回头补：31 个是封闭类（the、to、and、of、a、i、is、you、it、be、are、he、but、my、or、we、an、your、his、they、me、their、her、she、them、its、our、him、us、being、am），外加早已并进 `p.m.` 的 `pm`。`No.` 与 `no` 会整理成同一个目录 id，而且 Zipf 远高于本窗口，本批不收。`P.E.` 的 Zipf 是 2.79，`madam` 是 3.59，都在窗口之后。

`meta.gaokaoFreq` 仍为 `high`，`meta.batch` 为 15。选词行在 `data/batch-15-selection.json`，窗口摘要在 `data/batch-15-window.json`。

## 难度

`cefr` 沿用第十三、十四批写明的学习路线，不是考试院分数。门槛仍是 CEFR-J Wordlist 1.6 ALL_sep 词头的 wordfreq 中位数：

- Zipf ≥ 6.4 → A1
- Zipf ≥ 5.9 → A2
- Zipf ≥ 4.18 → B1
- Zipf ≥ 3.74 → B2
- 低于 3.74 → C1

交叉来源仍是《CEFR-J Wordlist Version 1.6》ALL_sep（东京外国语大学投野由纪夫研究室）。词头与本卡第一义项的词性一致时，采用表里的等级。词性对不上、或词头不在表里时，不用别的词性的等级，改用 Zipf 分段。两套都记在 `data/batch-15-cefr.json`。没有改已有卡的 `cefr`。

165 个词采用同词性的 CEFR-J 等级。35 个没有同词性标签，改用 Zipf 分段：

taxpayer, yourselves, arbitrary, autonomous, spit, goose, mat, zoom, hatch, boycott, carpenter, cuisine, communism, glue, kindergarten, subjective, tractor, algebra, stainless, pyramid, rigid, splendid, upwards, compass, compact-disk, vest, jeep, pe, radioactive, bingo, cubic, digest, friction, recorder, salute

其中三词在 CEFR-J 里有别的词性，本卡没有借用：

- `zoom` 第一义是动词「急速移动；拉近镜头」。表里只有名词 B2。Zipf 分段也是 B2。
- `hatch` 第一义是动词「孵出」。表里只有名词 B1。不用名词那一档，Zipf 3.82 落在 B2。
- `digest` 第一义是动词「消化；领会」。表里只有名词 B2。不用名词那一档，Zipf 3.71 低于 3.74，记为 C1。

其余 32 个词头不在 ALL_sep 里。Zipf ≥ 3.74 的留在 B2；`compact disk`、vest、jeep、PE、radioactive、bingo、cubic、friction、recorder、salute 低于 3.74，记为 C1。

新词的 `cefr` 分布：

| 等级 | 词数 |
| --- | ---: |
| A1 | 16 |
| A2 | 34 |
| B1 | 68 |
| B2 | 71 |
| C1 | 11 |
| C2 | 0 |

## 拼写

没有把两个还能分开搜索的拼写并成一条。已有卡的提示也没有改写。

- `café` 保留考纲里的音符。目录 id 是 `cafe`，因为文件名只允许小写字母、数字和连字符。插画和录音用这个 id 上未占用的上游文件。
- `PE` 按考纲的无点写法。带点的 `P.E.` 仍在考纲里，Zipf 2.79，不在本窗口。
- `humour` 是英式。美式 `humor` 已在库里。
- `jewellery` 是英式。美式 `jewelry` 已在库里。
- `metre` 是英式。美式 `meter` 已在库里。
- `maths` 是英式。美式 `math` 已在库里。
- `afterward` 是美式。英式 `afterwards` 已在库里。
- `forwards` 是英式副词。没有 s 的 `forward` 已在库里。
- `backward` 与已在库里的 `backwards` 分开。
- `upwards` 与 `upward` 都在本窗口，各用各的 id。`upward` 的第一义是形容词。
- `aluminium` 是英式。美式 aluminum 不是本库词头，只在提示里点明，不另开一条。
- `analyze` 用考纲里的美式拼写。英式 analyse 不在本库。
- `compact disk` 是两个词，目录 id 是 `compact-disk`。缩写 `cd` 与单词 `disk` 已在库里。

音标来自本机 espeak-ng 1.51，英式 `en-gb`、美式 `en-us`。重音移到元音前的音节头，闪音 `ɾ` 写成 `t`，`ɹ` 写成 `r`，成节辅音展开。TRAP 元音、`PE`、`café`、`compact disk`、`herb` 的英式无 h 等明显不对的，在 `scripts/build_batch15.py` 的 `IPA_OVERRIDE` 里改过，审计文件标成 `espeak-ng+override`。没有用打乱表里的音标。

## 扩展词

每张新卡都写了产品里已有的词族、近义、反义字段，并在需要时用提示点明相关形式。词族尽量写到考试用得上的派生词或明确相关形式，格式是「词 (词性 简短中文)」，这样词族按钮仍能对上库里的词头。近义和反义写成「词（中文）」。反义词只放在 `ant`，不放进 `syn`。扩展词可以是考纲以外的真实英语词，但不会变成新的目录词头，也不发明词。

没有干净反义词的词，`ant` 留空，不硬凑一对。

## 语言

例句仍是上面英文、下面中文。每张卡两句：第一句短，第二句更长。敏感词只收校园里站得住的义项：`spit` 只讲吐痰，`addicted` 只讲学习和生活习惯，`explode` 只讲安全和「激增」，`choke` 只讲噎住和忍住情绪，`bleed` 只讲止血并找老师，`razor` 只讲剃须工具，`radioactive` 和 `atom` 只讲课本结构和安全标志，`violate` 只讲违反规则，`butcher` 只讲肉铺和职业，`madame` 只讲尊称，`overweight` 谈人时要求尊重，`communism` 按历史课本的定义来写。

## 媒体

161 个新词的目录 id 在 `public/atlas/` 里已经有未挂到任何卡上的上游插画、缩略图、英音和美音。id 与目录 id 相同，文件按原路径使用，没有复制，也没有覆盖。`illustrated` 从 2610 增到 **2771**。

39 个新词没有同 id 的上游图，也没有同 id 的上游词头录音。本机没有免费的本地图像模型，也没有跑 `scripts/atlas/gen_images.py`（那个脚本调用付费图像接口）。这 39 张图留空，不借用别的词的画，也不把缺图说成有图：

yourselves, autonomous, enthusiastic, paperwork, convey, zoom, addicted, cube, rainfall, carpenter, dioxide, forwards, communism, grandpa, madame, seize, vacant, encouragement, hesitate, algebra, scar, stainless, rigid, upwards, amusement, compass, worthwhile, compact-disk, devotion, dilemma, millionaire, atom, choke, jeep, pe, radioactive, accuse, bingo, upward

这 39 个词的词头用本地 Kokoro 补了。美音 `af_heart`、`en-us`、语速 1.0；英音 `bf_emma`、`en-gb`、语速 1.0。只读孤立词头，单声道 44.1 kHz、64 kbps，尾部垫 0.08 秒。稿和 SHA-256 在 `data/batch-15-headword-audio.json`。先前的 `data/headword-audio-provenance.json` 和 `data/batch-14-headword-audio.json` 没有改。`voiced`（英音位）从 2635 增到 **2835**。更早那些本来就没有词头录音的卡，本批没有补。

新词的两条例句都用本地 Kokoro `af_heart`、美式、语速 1.0 录，400 条全部通过音素覆盖检查，没有时长离群，也没有调用付费接口。已经挂在旧卡上、原文还对得上的例句录音没有重录。全库例句录音现在是 5968 条 Kokoro，另有 19 条原文仍匹配的上游录音。开屏「欢迎打开高考词图」没有重录，SHA-256 仍是 `641e1f3d138c4a4b69027a24efac36e40440f4edfeb7615fbb42be5470cc45c9`。

播放路径只有 `audio/ex/{id}.mp3` 和 `audio/ex2/{id}.mp3`。161 条第一条例句、27 条第二条例句的路径上原先有未挂到任何卡的上游录音，内容不是本批的新句子。这些文件换成了新句子的 Kokoro 录音，否则新卡会播错句子。原先 2797 张卡的例句文件一个都没改。被换掉的上游字节仍在起点提交 `2fb93d13` 里。稿和 SHA-256 在 `data/batch-15-sentence-audio.json`。`data/sentence-audio-provenance.json` 只为这 200 张新卡追加了核对脚本。

## 复核修订

独立复核标出 6 处必须改的语言问题，都改在这 200 张新卡上。`pardon` 的第二句中文改成「请原谅」，英文没动，录音没重录。`shave` 的第二句改成刮胡子，`conductor` 补上「导体」并换了第二句，`cubic` 的第二句改成体积。这三句英文变了，只重录了对应的 Kokoro（`af_heart`，en-us，语速 1.0）。`envy` 的近义改为 be jealous of，`ample` 的近义改为 plentiful。顺手改了 drawer、diploma、kindergarten、vest 的词族或提示，没有重录。

## 校验

- `npm test`：28 项通过。
- `npm run check:atlas`：2997 词，5987 条例句，illustrated 2771，英音 2835，美音 2835，例句录音 2997，第二条例句录音 2990，errors 0。`oneExample` 警告仍是 7，是原先只有一条例句的卡。
- `ATLAS_BASE=/word-atlas-gaokao/ npm run build`：通过。
- 没有合并，没有部署，没有推到 `main`。`backup/dark-before-light-2026-11-13` 仍是 `3ab32bbe6ee7df121bfdbcbc3000a815b3bb2269`。开屏口播 SHA-256 仍是 `641e1f3d138c4a4b69027a24efac36e40440f4edfeb7615fbb42be5470cc45c9`。
