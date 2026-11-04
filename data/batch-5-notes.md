# 第五批选词 / Batch 5 selection

这一批在已有 800 个词之外，再加入 **200** 个考纲词头，并把重复的 `o-k` 并进 `okay`。产品名仍是高考词图。全库现在是 **999** 个词。

## 频率来源

与前几批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第四批终点 `base`（Zipf 5.05）之后继续往下取。同一 Zipf 上按字母排在 `base` 后面的词也算下一批，所以本批从 `below` 开始，而不是从更小的 Zipf 才开始。

本批 Zipf 从 **5.05（below）** 到 **4.91（color）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在词库里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。`o.k.` / `okay` 已在库里，这一批不再另加。

## 重复词头

`o-k` 和 `okay` 是同一个词，两条都没有配图或录音。本库只保留 `okay`，`meta.mergedFrom` 记为 `["o-k"]`。提示改为：okay 与 O.K. 是同一个词，正式写作可用 all right。

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。词头允许这些写法对上：括号里的词形变化、末尾星号、连字符和空格的差别，以及 colour / color、defence / defense 这类英美拼写。先把表里的英式音标和 espeak-ng 的 en-gb 结果做粗略比对：

- 像同一个词（189 个）时，采用表里的英式音标；若表里写了 `(US)`，美式也用表里的。注解行也对上了：`colour(美color)`、`Europe*`、`hurt(hurt,hurt)`、`southwest`、`northwest`、`northeast`。`defense` 用了表中的 `defence`。
- 明显串行、不用表里音标的 5 个：`wide`（对到 wear）、`speak`（对到 sparrow）、`piece`（对到 pie）、`visit`（对到 visa）、`spend`（对到 spelling）。
- `side road` 在表里对到 `sideroad`，音标是空的，中文是人行道，不用。
- 表里没有、改用 espeak-ng 的还有 `centre`、`commercial`、`positive`、`previous`、`south-east`。`centre` 和已有的 `center` 都保留，因为考纲里两种拼写都出现。
- 中文释义仍按图鉴格式另写，不把串行的中文直接抄进词条。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 5。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。

本批没有图、也没有录音的 18 个词：

association, cancer, color, committee, dad, deep, defense, hi, justice, mine, north-east, north-west, opening, potential, search, side-road, south-east, south-west

没有免密钥的绘图或配音流程，这些词先只保留文字。
