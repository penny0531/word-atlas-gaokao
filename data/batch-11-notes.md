# 第十一批选词 / Batch 11 selection

这一批在已有 1997 个词之外，再加入 **200** 个考纲词头。产品名仍是高考词图。全库现在是 **2197** 个词。

## 频率来源

与前几批相同：[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率，`zipf_frequency(word, "en")`。从第十批终点 `boom`（Zipf 4.33）之后继续往下取。同一 Zipf 上按字母排在 `boom` 后面、且还不在库里的词也算这一批，所以本批从 `brave` 开始。

本批 Zipf 从 **4.33（brave）** 到 **4.22（departure）**。按既定分段，这些词都记为 B1（低于 5.9）。这只用于学习路线排序，不是官方分级。

## 怎么筛

1. 读考纲词表，忽略 `#` 分段，按小写去重。
2. 去掉已经在词库里的词头。
3. 继续去掉先前排除的虚词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to，以及 `No.`。
4. 按 Zipf 从高到低取接下来的 200 个。

## 重复词头

这一批没有需要合并成一条的同一个缩写。`exam` 和 `examination`、`laboratory` 和已有的 `lab` 都分开保留，提示里互相说明。

下面这些英美拼写都保留，提示里互相说明，因为搜索只匹配词头：

- `favour` 与已有的 `favor`
- `realise` 与已有的 `realize`
- `judgment` 与英式 `judgement`（表里词头是 judgement，读音相同；本库词头用考纲里的 judgment）
- `dialogue` 注明美式常拼 `dialog`

相关词也各自保留并互相指向，例如 `relation` / `relate`，`reliable` / `rely`，`photograph` / `photographer`，`worn` / `wear`。

## 参考词表里的英式音标

对照同一份高考词汇表（3931 条：单词 / 音标 / 中文意思）。词头允许括号、星号、连字符和英美拼写。一行里若有多个读音，取得分最接近 espeak-ng 的那一个。`table tennis` 格里两个重音属于同一个读音，保留整条，不拆成 table。`garage` 逗号后的残段 `-rɪdʒ` 丢掉，采用完整的 /ˈɡærɑːʒ/。

- 像同一个词（187 个）时，采用表里的英式音标；若表里写了完整的 `(US)`，美式也用表里的。
- 明显串行、不用表里音标的 9 个：`pretend`（对到 pressure）、`pound`（对到 potential）、`terminal`（对到 term）、`ton`（对到 tomorrow）、`worthy`（对到 worthwhile）、`exam`（对到整个 examination）、`menu`（对到 mention）、`worn`（混进了 worm）、`snake`（少了词尾的 k）。
- 表里没有、改用 espeak-ng 的还有 `foster`、`laboratory`、`examination`、`grandfather`。
- 中文释义仍按图鉴格式另写。`sacred` 的音标是对的，中文格写成了 scared，本库按“神圣的”写。`diverse` 的音标是形容词，不按表里的“动词”标记。`export` 表里是动词重音，名词重音写在提示里。`bow` 的鞠躬读 /bəʊ/，武器“弓”读 /baʊ/，写在提示里。`wound` 的伤口读 /wuːnd/。

## 例句

`ex[0]` 是完整的日常或校园句，不在数据里挖空，练习时再挖。`ex[1]` 是更长的阅读句。`meta.gaokaoFreq` 为 `high`，`meta.batch` 为 11。

## 媒体

已有 `public/atlas` 图或音的词头直接复用，不把复用说成新画。新例句和旧的例句录音不一定逐字相同。

本批没有图、也没有录音的 18 个词：

abortion, agenda, aids, beast, communist, dvd, equality, judgment, outer, overcome, parallel, passage, photographer, racial, sacrifice, table-tennis, ton, worn

没有免密钥的绘图或配音流程，这些词先只保留文字。
