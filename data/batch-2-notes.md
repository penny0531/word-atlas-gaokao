# 第二批选词 / Batch 2 selection

这一批在已有 200 个词之外，再加入 **200** 个考纲词头。产品名仍是高考词图，不是另一套词表品牌。

## 频率来源

[wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf 频率：`zipf_frequency(word, "en")`。这是公开的词频库，数值越高越常见。多词或带连字符的形式会再试空格写法，取较高的一个分数。

本批 Zipf 大约从 7.27（in）到 5.52（power）。

## 怎么筛

1. 读 `gaokao-outline-3500` 词表，忽略 `#` 分段标记，按小写去重。
2. 去掉已经在 `data/word-atlas.json` 里的词头。
3. 去掉过于虚的功能词：a / an / the，be 及其变位，人称和物主代词，and / or / but，of / to。
4. 去掉 `No.`，因为它和 `no` 会变成同一个 id。
5. 按 Zipf 从高到低取前 200。

## 难度

只用于学习路线排序，不是官方分级：

- Zipf ≥ 6.4 → A1
- Zipf ≥ 5.9 → A2
- 其余 → B1

## 例句

沿用现在图鉴的写法：`ex[0]` 是完整的日常或校园句，不挖空；练习时再挖空。`ex[1]` 是更长的阅读句。音标来自 espeak-ng 的 en-gb / en-us。

## 媒体

词头如果在 `public/atlas/img|thumb|audio` 里已有文件，就复用，并在 `meta.mediaReuseCandidate` 标出有图的词。这些图和例句录音来自上游词库，新写的例句不一定和旧录音逐字相同。

本批没有图、也没有录音的 27 个词：

at, could, do, for, go, have, here, how, may, might, mr, no, not, only, part, then, this, those, used, well, what, where, while, who, will, work, would

没有现成的免密钥绘图或配音流程，所以这些词先只保留文字。
