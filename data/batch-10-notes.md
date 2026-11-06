# 第十批选词 / Batch 10 selection

这一批在已有 1797 个词之外，再加入 **200** 个考纲词头。产品名仍是高考词图。全库现在是 **1997** 个词。

## 频率来源

与前几批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第九批终点 `palace`（Zipf 4.45）之后继续往下取。同一 Zipf 上按字母排在 `palace` 后面、且还不在库里的词也算这一批，所以本批从 `pet` 开始。

本批 Zipf 从 **4.45（pet）** 到 **4.33（boom）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在词库里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。

## 重复词头

这一批没有需要合并成一条的同一个缩写。

下面这些英美拼写都保留，提示里互相说明，因为搜索只匹配词头：

- `honour` 与已有的 `honor`
- `behaviour` 与已有的 `behavior`
- `theater` 与已有的 `theatre`
- `organisation` 与已有的 `organization`
- `mum` 与已有的 `mom`，`daddy` 与已有的 `dad`

`license`、`recognize` 的另一种拼写、`neighborhood` 的英式 neighbourhood、`km` 作为 kilometre 的缩写，都在提示里说明。本批没有成对的另一条需要合并。

相关词也各自保留并互相指向，例如 `arrival` / `arrive`，`suffer` / `suffering`，`silent` / `silence`，`spoken` / `speak`，`agriculture` / `agricultural`，`prayer` / `pray`。

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。词头允许括号、星号、连字符和英美拼写。一行里若有多个读音，取得分最接近 espeak-ng 的那一个。`avenue` 格里两个读音粘在一起，采用更接近的前一个。

- 像同一个词（184 个）时，采用表里的英式音标；若表里写了完整的 `(US)`，美式也用表里的。
- 明显串行、不用表里音标的 9 个：`lab`（对到 knowledge）、`skill`（对到 ski）、`telephone`（对到 telegraph）、`desert`（名词沙漠用了动词遗弃的读音）、`smooth`（对到 smoking）、`honey`（对到 honest）、`spell`（对到 speed）、`dozen`（对到 downward）、`twin`（对到 twist）。
- 表里没有、改用 espeak-ng 的还有 `silent`、`gym`、`afterwards`、`disappointed`、`mum`、`km`、`daddy`。
- 中文释义仍按图鉴格式另写，不把串行的中文直接抄进词条。`tear` 的表内音标是动词“撕”的读音 /teə/；名词“眼泪”读 /tɪə/，写在提示里。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 10。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。

本批没有图、也没有录音的 22 个词：

aspect, bishop, breast, bye, cd, daddy, enterprise, glory, hunter, km, liberty, memorial, minority, mum, output, participate, possession, punishment, reflect, settle, spoken, theater

没有免密钥的绘图或配音流程，这些词先只保留文字。
