# 第七批选词 / Batch 7 selection

这一批在已有 1199 个词之外，按频率再取 **200** 个考纲词头，并把 `pm` 并进 `p.m.`。产品名仍是高考词图。全库现在是 **1398** 个词。

## 频率来源

与前几批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第六批终点 `proud`（Zipf 4.78）之后继续往下取。同一 Zipf 上按字母排在 `proud` 后面、且还不在库里的词也算这一批，所以本批从 `require` 开始。

本批 Zipf 从 **4.78（require）** 到 **4.66（candidate）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在词库里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。

## 重复词头

`p.m.` 和 `pm` 是同一个缩写，读音也相同。本库只保留 `p.m.`，以便和已有的 `a.m.` 一致。`meta.mergedFrom` 为 `["pm"]`。

`labor` 和 `labour` 是同一个词的美式和英式拼写，考纲里都有。搜索只匹配词头本身，所以两条都保留，提示里互相说明。`toward` 指向已有的 `towards`，`honor` 在提示里注明英式 `honour`。

另外这些相关词也各自保留，并在提示里指向已有词条：`lucky` / `luck`，`birthday` / `birth`，`religion` / `religious`，`shopping` / `shop`，`teach` / `teacher`，`chair` / `chairman`，`ill` / `sick`，`raise` / `rise`，`driver` / `drive`，`criminal` / `crime`，`Ms.` / `Mr.` 与 `Mrs.`。

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。词头允许括号、星号、连字符和空格的差别，以及 honour / honor、labour / labor 这类英美拼写。一行里若有逗号或分号隔开的几个读音，取得分最接近 espeak-ng 的那一个。先和 en-gb 做粗略比对：

- 像同一个词（185 个）时，采用表里的英式音标；若表里写了完整的 `(US)`，美式也用表里的。`reduce` 的美式只写了 `-ˈduːs`，不完整，美式仍用 espeak-ng。`Ms.` 的表内读音是 /mɪz/，采用。
- 明显串行、不用表里音标的 8 个：`wood`（对到 wonderful）、`software`（对到 soft）、`tough`（对到 totally）、`somewhere`（对到 sometimes）、`plenty`（对到 pleased）、`zone`（对到 zoo）、`smoke`（对到 smile）、`teach`（对到 tea）。
- 表里没有、改用 espeak-ng 的还有 `personal computer`、`fantastic`、`turning`、`update`、`soft`、`Muslim`。
- 中文释义仍按图鉴格式另写，不把串行的中文直接抄进词条。`tired` 那一行的中文混进了轮胎，释义按“疲倦”来写。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 7。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。`labor` 能对上原图，`labour` 没有原文件。

本批没有图、也没有录音的 11 个词：

abuse, appeal, beer, command, labour, ms, muslim, personal-computer, victory, violence, yours

没有免密钥的绘图或配音流程，这些词先只保留文字。
