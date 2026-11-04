# 第四批选词 / Batch 4 selection

这一批在已有 600 个词之外，再加入 **200** 个考纲词头。产品名仍是高考词图。全库现在是 **800** 个词。

## 频率来源

与前两批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第三批终点 `fight`（Zipf 5.23）之后继续往下取。

本批 Zipf 从 **5.23（fine）** 到 **5.05（base）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在 `data/word-atlas.json` 里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。先把表里的英式音标和 espeak-ng 的 en-gb 结果做粗略比对：

- 像同一个词（191 个）时，采用表里的英式音标；若表里写了 `(US)`，美式也用表里的。`center` 用了表中的 `centre`。
- 明显串行、不用表里音标的 6 个：`perfect`（对到 questionnaire）、`press`（president）、`reading`（shirt）、`size`（sixteenth）、`title`（tissue）、`forget`（forever）。
- 表里没有、改用 espeak-ng 的还有 `hear`、`lead`、`okay`。
- 中文释义仍按图鉴格式另写，不把串行的中文直接抄进词条。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 4。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。

本批没有图、也没有录音的 9 个词：

center, federal, itself, mom, o-k, okay, page, themselves, tv

没有免密钥的绘图或配音流程，这些词先只保留文字。
