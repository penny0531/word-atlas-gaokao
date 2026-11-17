# 第十二批选词 / Batch 12 selection

这一批在已有 2197 个词之外，再加入 **200** 个考纲词头。没有合并缩写，所以全库是 **2397** 个词。产品名仍是高考词图。

## 频率来源

公开语料 [wordfreq](https://github.com/rspeer/wordfreq) 3.1.1 的英语 Zipf，`zipf_frequency(word, "en")`。这不是官方考频。词表来自 MIT 许可的 [busiyiworld/maimemo-export](https://github.com/busiyiworld/maimemo-export) `exported/list/高考英语大纲词汇3500.txt`。文件有 3505 行词头、26 个字母标题；小写去重后是 **3487** 个词头。先前口头说的约 3464 是近似；本批按这份导出的 3487 个唯一词头排序，没有在窗口里跳词。

从第十一批终点 `departure`（Zipf 4.22）之后继续。同一 Zipf 上按字母排在它后面、且还不在库里的词也算，所以本批从 `dig` 开始，到 `preference`（Zipf 4.11）结束。新词都记为 B1。这只用于学习路线，不是官方分级。

## 重复词头

没有需要合并的缩写。`grandma` 与 `grandmother` 都保留，提示里互相说明。

考纲用的是美式拼写，英式写法还没有单独词条，所以本批保留美式词头，并在提示里写出英式：

- `humor`（humour）
- `harbor`（harbour）
- `jewelry`（jewellery）
- `neighbor`（neighbour）

`mathematics` 的提示说明口语 maths / math。

## 参考词表里的英式音标

对照同一份高考词汇表（单词 / 音标 / 中文意思）。最后一列是打乱用的随机数，不参与排序。

- 像同一个词（189 个）时，采用表里的英式音标。
- 明显串行、改用 espeak-ng 的 8 个：`preserve`（对到 presentation）、`tobacco`（对到 toast）、`significance`（对到 signature）、`pig`（对到 pie）、`pile`（对到 pie）、`cheers`（对到 cheer）、`sandwich`（少了词尾音）、`customs`（对到 custom）。
- 表里没有的还有 `shy`、`grandmother`、`unfortunate`。

## 例句录音

新词的两条例句都用本地 Kokoro `af_heart`、美式、语速 1.0 录了，没有调用付费接口。稿和文件写进 `data/sentence-audio-provenance.json`。旧的 Heart 录音和开屏「欢迎打开高考词图」没有重录。35 个新词没有上游插画，也没有词头英音/美音，词头仍走设备朗读：

aboard, acknowledge, ash, athletic, bare, barrier, bored, boxing, burst, cheers, corrupt, disability, distant, examine, grandma, gravity, harbor, humor, lap, leaf, lightning, marathon, missile, neighbor, ours, patience, pension, phenomenon, precise, separation, spray, theft, unemployment, widespread, zoo

## 送审前改过的例句

对照 200 张新卡和 400 条例句之后，改了 69 个例句槽，并只重录这些槽。改动包括：九条“a lesson about … not how to harm”动物模板、反复出现的末班车/海报句、几乎重复的成对例句，以及几处义项用错（`occupation` 被写成地点、`corrupt` 用来形容费用、`permit` / `scratch` / `scream` 的第二句用成了名词）。机器可读记录在 `data/batch-12-review.json`。已有 2197 张卡的句子没有改。

独立语言审读在 `2437ed8b` 给出 HOLD。同一分支又改了 90 张新卡：不自然或和中文错位的例句、重复的说明腔、37 条空的 “a/an + 词 + of” 搭配，以及和词性或音节对不上的音标。英文改动的 39 条用本地 Kokoro `af_heart`、美式、语速 1.0 重录；只改中文的不重录。逐条旧文、新文、搭配处置和音标对照在 `data/batch-12-language-fixes.json`。
