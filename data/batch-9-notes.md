# 第九批选词 / Batch 9 selection

这一批在已有 1598 个词之外，按频率再取 **200** 个考纲词头，并把 `p.c.` 并进 `PC`。产品名仍是高考词图。全库现在是 **1797** 个词。

## 频率来源

与前几批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第八批终点 `ban`（Zipf 4.55）之后继续往下取。同一 Zipf 上按字母排在 `ban` 后面、且还不在库里的词也算这一批，所以本批从 `carbon` 开始。`brilliant` 已经在库里，这一批不重复。

本批 Zipf 从 **4.55（carbon）** 到 **4.45（palace）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在词库里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。

## 重复词头

`p.c.` 和 `pc` 是同一个缩写，都指 personal computer。本库只保留 `PC`（id 为 `pc`，能对上已有插画），`meta.mergedFrom` 为 `["p-c"]`。personal computer 已在本库。

`grey` 和 `gray`、`colour` 和已有的 `color`、`defence` 和已有的 `defense` 是英美拼写。搜索只匹配词头，所以都保留，提示里互相说明。`license`、`recognize`、`neighborhood`、`theatre`、`math` 在提示里注明另一种拼写，考纲这一批里没有成对的另一条。

另外这些相关词也各自保留，并在提示里指向已有或本批词条：`Olympic` / `Olympics`，`existence` / `exist`，`expression` / `express`，`depth` / `deep`，`tradition` / `traditional`，`clothing` / `clothes`，`ice cream` / `cream`，`actress` / `actor`，`pride` / `proud`，`everyday`（一个词）和 every day（两个词）。

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。词头允许括号、星号、连字符、空格和句点的差别，以及 colour / color、defence / defense、grey / gray 这类英美拼写。一行里若有多个读音，取得分最接近 espeak-ng 的那一个。

- 像同一个词（184 个）时，采用表里的英式音标；若表里写了完整的 `(US)`，美式也用表里的。`PC` 用了表里 `p.c.` 的读音。
- 明显串行、不用表里音标的 6 个：`sight`（对到 sigh）、`respond`（对到 respect）、`everyday`（对到 everybody）、`technique`（对到 technical）、`cloud`（对到 clothing）、`wash`（对到 warning）。
- 表里没有、改用 espeak-ng 的还有 `factory`、`bike`、`somehow`、`pink`、`approval`、`grey`、`gray`、`math`、`Olympics`。
- 中文释义仍按图鉴格式另写，不把串行的中文直接抄进词条。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 9。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。`PC` 复用了 `pc` 的原文件。

本批没有图、也没有录音的 16 个词：

bc, bonus, broad, consistent, everyday, extension, flash, ice-cream, math, neighborhood, olympic, origin, quit, somehow, surrounding, witness

没有免密钥的绘图或配音流程，这些词先只保留文字。
