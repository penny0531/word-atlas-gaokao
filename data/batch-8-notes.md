# 第八批选词 / Batch 8 selection

这一批在已有 1398 个词之外，再加入 **200** 个考纲词头。产品名仍是高考词图。全库现在是 **1598** 个词。

## 频率来源

与前几批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第七批终点 `candidate`（Zipf 4.66）之后继续往下取。同一 Zipf 上按字母排在 `candidate` 后面、且还不在库里的词也算这一批，所以本批从 `comfortable` 开始。

本批 Zipf 从 **4.66（comfortable）** 到 **4.55（ban）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在词库里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。

## 重复词头

这一批没有需要合并成一条的同一个缩写。

`favourite` 与已有的 `favorite`、`programme` 与已有的 `program` 是英美拼写。搜索只匹配词头，所以都保留，提示里互相说明。`favor` 是 favour（恩惠、帮助），不是 favourite，单独成条，并注明英式拼写 favour。

另外这些相关词也各自保留，并在提示里指向已有或本批词条：`Asia` / `Asian`，`perform` / `performance`，`worried` / `worry`，`drunk` / `drink`，`lay` / `lie`，`maximum` / `minimum`，`anybody` / `anyone`，`e-mail` / `mail`，`T-shirt` / `shirt`，`danger` / `dangerous`，`properly` / `proper`，`personnel` / `personal`。

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。词头允许括号、星号、连字符和空格的差别，以及 favourite / favorite、programme / program、favour / favor 这类英美拼写。一行里若有多个读音，取得分最接近 espeak-ng 的那一个。`mm` 按 millimetre 来比对。

- 像同一个词（194 个）时，采用表里的英式音标；若表里写了完整的 `(US)`，美式也用表里的。
- 明显串行、不用表里音标的 5 个：`unable`（音标不像这个词）、`newspaper`（对到 news）、`pleasure`（对到 pleased）、`diet`（对到 die）、`goods`（对到 good）。
- 表里没有、改用 espeak-ng 的还有 `troops`。
- 中文释义仍按图鉴格式另写，不把串行的中文直接抄进词条。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 8。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。

本批没有图、也没有录音的 9 个词：

constitution, desire, e-mail, heaven, mm, pack, personnel, troops, x-ray

没有免密钥的绘图或配音流程，这些词先只保留文字。
