# 第十六批选词 / Batch 16 selection

这一批从第十五批终点 `appoint`（wordfreq 3.1.1 英语 Zipf **3.70**）之后继续，加入 **200** 个考纲词头。全库从 2997 增到 **3197** 个词，例句从 5987 增到 **6387**。产品名仍是高考词图。已有 2997 张卡的正文、`cefr`、例句录音、开屏口播和已经配齐的媒体都没有改。没有合并，没有部署。

起点提交是已经合进 main 的第十五批 `69c164ab1fd7c32dc93a11e2ca7e6b37a9c8fb35`。本说明所在提交就是本批 PR head；合并前只核对该提交，不要合并别的提交。PR 说明里会再写一次这个 head SHA。

## 频率来源

公开语料 [wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf，`zipf_frequency(word, "en")`。这不是官方考频。词表来自 MIT 许可的 [busiyiworld/maimemo-export](https://github.com/busiyiworld/maimemo-export) `exported/list/高考英语大纲词汇3500.txt`。这次用的就是随任务附上的那一份：`wc -l` 是 **3530**（最后一行没有换行符）。内容是 3531 行，其中 26 个 `#A`–`#Z` 标题，小写去重后是 **3487** 个词头。本批只从这 3487 个词头里选，没有发明词，也没有从任何打乱用的 XLS 里另取词。

多词或带连字符的形式会再试空格或连字符写法，取较高的 Zipf。本窗口里没有词因为这种双写而改分。排序键是两位小数 Zipf 从高到低，同一 Zipf 按 id 字母序。`appoint` 之后、同一 3.70 上还排在它后面的 10 个词都算进窗口，所以本批从 **capsule**（Zipf 3.70）开始，到 **annoy**（Zipf 3.46）结束。

3.46 上排在 annoy 之后、留给下一批的还有 10 个：applaud、brunch、criterion、dialog、flashlight、liter、simplify、snowy、statesman、tram。下一批从 **applaud**（Zipf 3.46）开始。

窗口里已经在库中、因而没有重复加入的是 confuse（3.67）、gradual（3.67）、circumstance（3.66）、devote（3.53）。

`bean` 之前还有 32 个考纲词头不在库里，本批不回头补：31 个是封闭类（the、to、and、of、a、i、is、you、it、be、are、he、but、my、or、we、an、your、his、they、me、their、her、she、them、its、our、him、us、being、am），外加早已并进 `p.m.` 的 `pm`。`No.` 与 `no` 会整理成同一个目录 id，而且 Zipf 远高于本窗口，本批不收。

`meta.gaokaoFreq` 仍为 `high`，`meta.batch` 为 16。选词行在 `data/batch-16-selection.json`，窗口摘要在 `data/batch-16-window.json`。

## 难度

`cefr` 沿用第十三批以来写明的学习路线，不是考试院分数。门槛仍是 CEFR-J Wordlist 1.6 ALL_sep 词头的 wordfreq 中位数：

- Zipf ≥ 6.4 → A1
- Zipf ≥ 5.9 → A2
- Zipf ≥ 4.18 → B1
- Zipf ≥ 3.74 → B2
- 低于 3.74 → C1

交叉来源仍是《CEFR-J Wordlist Version 1.6》ALL_sep（东京外国语大学投野由纪夫研究室）。词头与本卡第一义项的词性一致时，采用表里的等级。词性对不上、或词头不在表里时，不用别的词性的等级，改用 Zipf 分段。两套都记在 `data/batch-16-cefr.json`。没有改已有卡的 `cefr`。

156 个词采用同词性的 CEFR-J 等级。44 个没有同词性标签，改用 Zipf 分段。本窗口全部低于 3.74，所以这 44 个都是 C1。

其中三词在 CEFR-J 里有别的词性，本卡没有借用：

- `clone` 第一义是名词「克隆体」。表里只有动词 A2。不用动词那一档，Zipf 3.68 低于 3.74，记为 C1。
- `refresh` 第一义是动词「使恢复精力；刷新」。表里只有名词 B2。不用名词那一档，Zipf 3.65 记为 C1。
- `rhyme` 第一义是名词「韵」。表里只有动词 B2。不用动词那一档，Zipf 3.56 记为 C1。

其余 41 个词头不在 ALL_sep 里，同样记为 C1：

rot, spear, chalk, irrigation, squirrel, skeptical, accelerate, bamboo, courtyard, furnished, panda, accustomed, pest, Buddhism, freeway, lantern, tailor, chant, claw, outgoing, typhoon, adolescent, cigar, mummy, Antarctic, hen, mister, cater, buffet, sideways, numb, socket, appendix, postage, tyre, botanical, stocking, unconditional, digital versatile disk, pianist, wrestle

新词的 `cefr` 分布：

| 等级 | 词数 |
| --- | ---: |
| A1 | 12 |
| A2 | 35 |
| B1 | 54 |
| B2 | 55 |
| C1 | 44 |
| C2 | 0 |

## 拼写

没有把两个还能分开搜索的拼写并成一条。已有卡的提示也没有改写。

- `neighbour` 是英式。美式 `neighbor` 已在库里。
- `fibre` 是英式。美式 `fiber` 已在库里。
- `practise` 是英式动词。库里的 `practice` 是名词。
- `organise` 是英式动词。美式 `organize` 已在库里。
- `analyse` 是英式动词。美式 `analyze` 已在库里。
- `litre` 是英式「升」。美式 `liter` 仍在考纲里，Zipf 与本批终点相同，留给下一批，不在这里另开词头。不要和已在库里的 `metre` 米弄混。
- `tyre` 是英式「轮胎」。库里的 `tire` 是动词「使疲劳」，不是这条的美式拼写。
- `cheque` 是英式「支票」。库里的 `check` 同时有「检查」和美式「支票」。
- `traveller` 是英式，`traveler` 是美式。两个都在本批，各用各的 id 和例句。
- `sidewalk` 是美式人行道。英式 `pavement` 也在本批，并在提示里说明美式 pavement 有时指路面。
- `skeptical` 用考纲里的美式拼写。英式 sceptical 不另开词头。
- `cozy` 是美式。英式常写 cosy。
- `yogurt` 是美式。英式常写 yoghurt。
- `madam` 是英语尊称。库里已有 `madame`，多用于法语姓名前。
- `digital versatile disk` 是两个以上的词，目录 id 是 `digital-versatile-disk`。口语说 DVD。`disk` 已在库里。不要把它写成 compact disk。
- `Buddhism`、`Antarctic` 保留考纲里的大写。

音标来自本机 espeak-ng 1.51，英式 `en-gb`、美式 `en-us`。重音移到元音前的音节头，闪音 `ɾ` 写成 `t`，`ɹ` 写成 `r`，成节辅音展开。TRAP 元音、`squirrel` 的美音、`oneself`、`buffet` 的自助餐读音、`interrupt` 和 `multiply` 的重音、`digital versatile disk` 被连读坏的音标等，在 `scripts/build_batch16.py` 的 `IPA_OVERRIDE` 里改过，审计文件标成 `espeak-ng+override`。`buffet` 的词条音标按第一义「自助餐」；动词「冲击」的读音写在提示里。没有用打乱表里的音标。

## 扩展词

每张新卡都处理了词族、近义、反义，并在相关形式需要提醒时写了提示。词族尽量写到考试用得上的派生词，格式是「词 (词性 简短中文)」，这样词族按钮仍能对上库里的词头。近义和反义写成「词（中文）」。反义词只放在 `ant`，不放进 `syn`。扩展词可以是考纲以外的真实英语词，但不会变成新的目录词头，也不发明词。

没有干净派生词的具体名词，`fam` 留空。没有干净近义词的，`syn` 留空。没有干净反义词的，`ant` 留空，不硬凑一对。例如 grape、panda、typhoon、kettle 没有可靠的反义。compulsory / optional、unwilling / willing、noisy / quiet、forbid / allow 这种成对的才写入 `ant`。sidewalk 与 pavement、traveler 与 traveller、cheque 与美式 check 写成近义，并在提示里说明它们不是可以随便合并的词头。

## 语言

例句仍是上面英文、下面中文。每张卡两句：第一句短，第二句更长。一个词如果有两个高考里都常见的义项，两个义项都列出，两句分别对着它们。例如 stain 的污渍和沾污，whichever 的限定词和代词，mummy 的妈妈和木乃伊，appendix 的附录和阑尾，overlook 的忽略和俯瞰，correspond 的通信和对应。

敏感或容易写偏的词只收校园里站得住的用法：`cigar` 只讲烟草有害，`brewery` 只当产业来讲，`unrest` 按历史阅读来写，`starve` 和 `starvation` 不鼓励节食，`poisonous` 只讲识别和不要品尝，`wrestle` 只讲垫上的摔跤和跟题目较劲，`pest` 用来骂同学时明确说这样不礼貌，`Buddhism` 按历史课本、保持尊重。

## 媒体

156 个新词的目录 id 在 `public/atlas/` 里已经有未挂到任何卡上的上游插画、缩略图、英音和美音。id 与目录 id 相同，文件按原路径使用，没有复制，也没有覆盖。`illustrated` 从 2771 增到 **2927**。

44 个新词没有同 id 的上游图，也没有同 id 的上游词头录音。没有跑 `scripts/atlas/gen_images.py`。这 44 张图留空，不借用别的词的画：

whichever, chalk, mustard, clone, skeptical, govern, translator, remark, furnished, accustomed, camel, cocoa, cozy, buddhism, fax, freeway, granny, unrest, humorous, muddy, outgoing, competence, mummy, hen, rhyme, educator, oneself, yummy, socket, postage, outing, botanical, cheque, loaf, paddle, stocking, traveller, unconditional, accumulate, admirable, contradictory, crossroads, digital-versatile-disk, wrestle

这 44 个词的词头用本地 Kokoro 补了。美音 `af_heart`、`en-us`、语速 1.0；英音 `bf_emma`、`en-gb`、语速 1.0。只读孤立词头，单声道 44.1 kHz、64 kbps，尾部垫 0.08 秒。稿和 SHA-256 在 `data/batch-16-headword-audio.json`。先前的词头 provenance 文件没有改。`voiced`（英音位）从 2835 增到 **3035**。更早那些本来就没有词头录音的卡，本批没有补。

新词的两条例句都用本地 Kokoro `af_heart`、美式、语速 1.0 录。已经挂在旧卡上的例句录音没有重录。同 id 上未挂到旧卡的上游例句文件换成了新句子，否则新卡会播错句子。稿和 SHA-256 在 `data/batch-16-sentence-audio.json`。`data/sentence-audio-provenance.json` 只为这 200 张新卡追加了核对脚本。开屏「欢迎打开高考词图」没有重录。

## 校验

- `npm test`：28 项通过。
- `npm run check:atlas`：3197 词，6387 条例句，illustrated 2927，英音 3035，美音 3035，例句录音 3197，第二条例句录音 3190，verified 与例句一致，withheld 0，errors 0。`oneExample` 警告仍是 7，是原先只有一条例句的卡。`headwordNotInExample` 和 `missingIpa` 都是 0。
- `ATLAS_BASE=/word-atlas-gaokao/ npm run build`：通过。
- 没有合并，没有部署，没有推到 `main`。`backup/dark-before-light-2026-11-13` 仍是 `3ab32bbe6ee7df121bfdbcbc3000a815b3bb2269`。开屏口播 SHA-256 仍是 `641e1f3d138c4a4b69027a24efac36e40440f4edfeb7615fbb42be5470cc45c9`。旧卡例句文件的 SHA-256 在补录前后一致。
