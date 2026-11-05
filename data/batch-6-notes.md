# 第六批选词 / Batch 6 selection

这一批在已有 999 个词之外，再加入 **200** 个考纲词头。产品名仍是高考词图。全库现在是 **1199** 个词。

## 频率来源

与前几批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第五批终点 `color`（Zipf 4.91）之后继续往下取。同一 Zipf 上按字母排在 `color` 后面、且还不在库里的词也算这一批，所以本批从 `dream` 开始。

本批 Zipf 从 **4.91（dream）** 到 **4.78（proud）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在词库里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。

## 重复词头

这一批没有需要合并的同一个词。`realize` 用考纲里的拼写，库里没有另一条 `realise`。

下面这些是相关词，但考纲里各自成条，所以都保留，并在提示里互相说明：

- `television` 与已有的 `TV`
- `till` 与已有的 `until`
- `hearing` 与已有的 `hear`
- `physical education` 与已有的 `physical`
- `Mrs.` 与已有的 `Mr.`
- `everybody` 与已有的 `everyone`
- `somebody` 与已有的 `someone`

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。词头允许括号里的词形、末尾星号、连字符和空格的差别，以及 realise / realize 这类英美拼写。先把表里的英式音标和 espeak-ng 的 en-gb 结果做粗略比对：

- 像同一个词（193 个）时，采用表里的英式音标；若表里写了完整的 `(US)`，美式也用表里的。`produce` 的美式只写了 `-ˈduːs`，不完整，美式仍用 espeak-ng。
- 明显串行、不用表里音标的 5 个：`theory`（对到 theoretical）、`weather`（对到 wear）、`slow`（对到 sleep）、`traditional`（对到 tradition）、`television`（对到 telegraph）。
- 表里没有、改用 espeak-ng 的还有 `everybody`、`physical education`。
- 中文释义仍按图鉴格式另写，不把串行的中文直接抄进词条。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 6。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。

本批没有图、也没有录音的 12 个词：

award, herself, hot-dog, institute, luck, mrs, physical-education, religious, sad, trial, waiting-room, whom

没有免密钥的绘图或配音流程，这些词先只保留文字。
