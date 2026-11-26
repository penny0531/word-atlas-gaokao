# 第十三批选词 / Batch 13 selection

这一批在已有 2397 个词之外，再加入 **200** 个考纲词头。没有合并缩写，所以全库是 **2597** 个词。产品名仍是高考词图。已有 2397 张卡的正文、`cefr` 和旧录音都没有改。

## 频率来源

公开语料 [wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf，`zipf_frequency(word, "en")`。这不是官方考频。词表来自 MIT 许可的 [busiyiworld/maimemo-export](https://github.com/busiyiworld/maimemo-export) `exported/list/高考英语大纲词汇3500.txt`。文件有 3505 行词头、26 个字母标题；小写去重后是 **3487** 个词头。本批按这 3487 个唯一词头排序，没有把条数改成 3500，也没有在窗口里跳词。

多词或带连字符的形式会再试空格写法，取较高的 Zipf。本批只有 `o'clock` 一种带符号的词头，采用 `o'clock` 的分数。

从第十二批终点 `preference`（Zipf 4.11）之后继续。同一 Zipf 上按 id 字母排在它后面、且还不在库里的词也算，所以本批从 `selfish` 开始，到 `bean`（Zipf 3.98）结束。`pm` 的 Zipf 是 4.69，但早已并进 `p.m.`，不在本窗口里，也不另开一条。

`meta.gaokaoFreq` 仍为 `high`，`meta.batch` 为 13。库里没有把 high / mid / low 再分成 Zipf 门槛的成文规则，最近几批新词都标 `high`，本批照旧。

## 难度（学习路线，不是官方等级）

`cefr` 是学习路线用的等级，不是考试院分数。第二批写下的旧分段仍然有效：

- Zipf ≥ 6.4 → A1
- Zipf ≥ 5.9 → A2

旧规则在这以下一律 B1。第十三批全部低于 4.11，若停在「其余 B1」，200 个词会再次全部变成 B1。本批把这条学习路线往下写明，门槛来自 CEFR-J 词表自身的词频中位数，不是凭感觉取整：

用《CEFR-J Wordlist Version 1.6》ALL_sep 表里每个等级的词头（小写唯一；连字符形式再试空格写法，取较高 Zipf），对 wordfreq 3.1.1 的英语 Zipf 取中位数，保留两位小数：

- B1 词头中位数 **4.18** → Zipf ≥ 4.18 → B1
- B2 词头中位数 **3.74** → Zipf ≥ 3.74 → B2
- 低于 3.74 → C1

允许的值仍是 A1、A2、B1、B2、C1、C2。

交叉来源是可以注明出处后用于研究和商用的《CEFR-J Wordlist Version 1.6》（东京外国语大学投野由纪夫研究室，2020-03-24）。本批于 2026-11-26 从 <https://www.cefr-j.org/data/CEFRJ_wordlist_ver1.6.zip> 下载。词头与本卡第一义项的词性一致时，采用表里的等级。词性对不上、或词头不在表里时，不用别的词性的等级，改用上面的 Zipf 分段。公布等级和 Zipf 分段不同时，采用公布等级，两套都记在 `data/batch-13-cefr.json`。

本窗口的 Zipf 分段本身全是 B2。183 个词有对得上的 CEFR-J 等级，其中 140 个和 B2 分段不同，按公布等级写入。没有同词性标签、因而留在 Zipf 分段 B2 的 17 个是：

facial, hurricane, shark, receiver, warehouse, inn, nest, elder, grocery, bowling, disturbing, authentic, subscribe, adaptation, insert, theoretical, voluntary

新词的 `cefr` 分布：

| 等级 | 词数 |
| --- | ---: |
| A1 | 19 |
| A2 | 41 |
| B1 | 80 |
| B2 | 60 |
| C1 | 0 |
| C2 | 0 |

没有改已有 2397 张卡的 `cefr`。

## 重复词头与拼写

没有把两个还能分开搜索的拼写并成一条。

- `meter` 按参考表对应英式 `metre`（米）。`metre` 仍在考纲里，不在本窗口。
- `fiber` 按参考表对应英式 `fibre`（纤维）。`fibre` 仍在考纲里。
- `tire` 按参考表是动词「使疲劳」。考纲另有 `tyre`，本批不合并。
- `backwards` 与考纲里的 `backward` 都保留为不同词头。参考表写成 `backward(s)`。
- `disk` 在参考表里写作 disk＝disc。`disc` 不是这份考纲词头。
- `o'clock` 的 id 是 `o-clock`。`Arctic` 保留考纲里的大写。

## 参考词表

对照同一份高考词汇表（单词 / 音标 / 中文意思，3931 条）。最后一列是打乱用的随机数，不参与排序。

参考表里没有单独一行、释义不从那一格抄来的词：`widow`、`grocery`、`tablet`、`airline`、`donate`、`warn`。

同一词头但写法带括号、等号或英美拼写的，不算缺失：`backward(s)`、`fridge＝refrigerator`、`disk＝disc`、`metre`（美式 meter）、`fibre`（美式 fiber）。

音标明显串行或对不上、英式改用 espeak-ng en-gb 的：

- `shout`（音标是 shoulder）
- `slice`（音标是 sleeve）
- `possess`（音标是 position）
- `uncertain`（音标是 certain，少了 un-）
- `booth`（写成 /ð/，不是 /θ/）
- `fridge`（音标是 refrigerator）
- 加上表里没有的 `widow`、`grocery`、`tablet`、`airline`、`donate`、`warn`

`statue` 的音标 /ˈstætjuː/ 留用，中文格写成了法令（那是 statute），本卡改为雕像。`civilization` 不收参考表里多出来的「开花」。`bounce` 不收「被束缚的」（那是 bound）。`nephew` 表里有 /ˈnefjuː/ 和 /ˈnevjuː/，字段里用前一个。`backwards` 用表内 /ˈbækwəd/ 补上实际听到的词尾 /z/。`insert` 的美式不用 espeak 的名词重音，改成和表内动词一致的 /ɪnˈsɜːrt/。`o'clock` 的美式重音按表内英式对齐为 /əˈklɑːk/。`uncertain` 的美式把 espeak 的成节鼻音整理成 /ʌnˈsɜːrtən/。

## 例句录音

新词的两条例句都用本地 Kokoro `af_heart`、美式、语速 1.0 录了，400 条全部通过音素覆盖检查，没有调用付费接口。稿和文件写进 `data/sentence-audio-provenance.json`。原文还对得上的旧例句录音没有重录，开屏「欢迎打开高考词图」也没有重录。本批新生成 400 条。全库例句录音现在是 5168 条 Kokoro，另有 19 条原文仍匹配的上游录音。

24 个新词没有上游插画，也没有词头英音/美音，词头仍走设备朗读：

belly, booth, facial, import, meter, coke, merchant, adjust, flame, inn, nationwide, scan, fiber, pulse, beg, graph, strengthen, transform, passive, deliberately, sympathy, theoretical, dash, bent

没有为补第十二批缺的图或词头录音另开工作。
