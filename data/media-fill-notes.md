# 词头录音与插画补缺 / Headword audio and illustration fill

起点是 `141d9380`（2597 词，5187 条例句，第十二、十三批已在 main）。这一次只补下面 59 个词的缺媒体。没有开第十四批，没有改例句录音、开屏口播、已经配齐的卡，也没有改 UI。

## 这次加了什么

| 项目 | 结果 |
|---|---|
| 目标词 | 59。目录 id 与词头相同，没有带连字符的 id |
| 原先的 media | 全部是 24，也就是只有 ex + ex2 |
| 词头英音 / 美音 | 59 个都补上了 |
| 插画 | 5 个复用上游原文件。另外 54 个插画位仍空着 |
| media 位 | 54 个从 24 变成 30（2+4+8+16）。5 个从 24 变成 31（1+2+4+8+16） |
| illustrated | 2383 → 2388 |
| voiced（英音位） | 2376 → 2435 |
| 例句录音 | 未改。`data/sentence-audio-provenance.json` 未改 |

第十二批 35 个：aboard, acknowledge, ash, athletic, bare, barrier, bored, boxing, burst, cheers, corrupt, disability, distant, examine, grandma, gravity, harbor, humor, lap, leaf, lightning, marathon, missile, neighbor, ours, patience, pension, phenomenon, precise, separation, spray, theft, unemployment, widespread, zoo。

第十三批 24 个：belly, booth, facial, import, meter, coke, merchant, adjust, flame, inn, nationwide, scan, fiber, pulse, beg, graph, strengthen, transform, passive, deliberately, sympathy, theoretical, dash, bent。

## 上游原文件：核对过，能复用的只有这 5 个

`public/atlas/` 里留着词光全套未选用的文件（约 7305 张图、7298 条英音、7298 条美音）。按目录 id 逐个对过这 59 个词：没有一个 id 自己就有图或词头文件。

同一词的英式拼写、而且该拼写不在本目录里、文件也没被别的卡占用的，有 5 个。图、缩略图、英音、美音都是按字节复制，原路径上的文件还在。

| 本库 id | 上游 id | 卡上的意思 |
|---|---|---|
| meter | metre | 米；公尺 |
| fiber | fibre | 纤维 |
| harbor | harbour | 港口 |
| humor | humour | 幽默 |
| neighbor | neighbour | 邻居 |

复制后的文件与上游文件 SHA-256 相同。`data/word-atlas.json` 里这 5 条的 `meta.mediaReuseCandidate` 改为 true。其余词条的正文没有改。

看过、但没有拿来用的邻近文件：

- `cola` 有未占用的图和词头录音，画的是一杯可乐。本卡 `coke` 的意思也是可乐，但它是另一个词头，不借用别的词的画，也不把 `cola` 的录音标成 `coke`。
- `leaves` 有未占用的图和录音。它是另一个词头，不用来填 `leaf`。
- `grandmother` 的图和录音已经挂在目录里的 grandmother 卡上（media 31）。不用来填 `grandma`。
- `bend` 的图和录音已经挂在 bend 卡上（media 31）。不用来填 `bent`。
- `neighbourhood` 有未占用的图和英音、美音，对应的是更早缺口里的 `neighborhood`。那不在这 59 个词里，这次不复制。

## 词头录音

54 个没有上游文件的词，用本地 Kokoro ONNX 只读词头，不读句子。没有调用付费接口，也没有 API key。

| | 英音 | 美音 |
|---|---|---|
| 声音 | `bf_emma` | `af_heart` |
| 语言 | `en-gb` | `en-us` |
| 语速 | 1.0 | 1.0 |
| 稿 | 孤立词头 | 孤立词头 |

`voices-v1.0.bin` 里的英国女声是 `bf_alice`、`bf_emma`、`bf_isabella`、`bf_lily`。用本地 faster-whisper `base.en` 对 30 个孤立词头打分：emma 25，isabella 24，alice 21，lily 19。emma 在这组里没有把多音节词听成另一个词。四条都完整覆盖了音素。全库英音只用 `bf_emma`。

技术格式对齐现有词头 mp3：MPEG layer III，单声道，44100 Hz，64 kbps。尾部按例句脚本同样垫了 0.08 秒，避免编码器截掉词尾。模型是 `kokoro-v1.0.onnx` 与 `voices-v1.0.bin`（model-files-v1.1），SHA-256 与 `scripts/atlas/gen_kokoro_sentence_audio.py` 里的锁定值相同。运行时 kokoro-onnx 0.6.1。权重在被 Git 忽略的 `.local/kokoro/models/`，没有提交。

每条都通过音素覆盖检查：合成出的音素串等于该语言的 phonemize 结果，峰值和时长也在单次词头的范围内。稿、声音、语言、语速、路径和 SHA-256 在 `data/headword-audio-provenance.json`。脚本是 `scripts/atlas/gen_kokoro_headword_audio.py`。它拒绝覆盖已有词头文件，也不写 `audio/ex`、`audio/ex2` 和开屏口播。

本地 faster-whisper `base.en` 又听了全部 108 条 Kokoro 词头。89 条听成了词头本身或极近的同音。下面 19 条对不上。孤立的半秒片段上，`base.en` 经常听错短词和 th 开头的词；这 19 条的音素覆盖是齐的，重读音节也有能量。把它们记在这里，方便人耳复查，不把听写结果当成删除条件。

| 口音 | 词 | 听写 |
|---|---|---|
| uk | aboard | Abort |
| uk | adjust | But just... |
| uk | ash | Last |
| us | bare | There. |
| uk | beg | big |
| us | booth | Boosbytes |
| uk | bored | Booty. |
| uk | graph | Grass |
| uk | inn | Send. |
| uk | lightning | lighting |
| uk | marathon | Merrithind |
| us | merchant | Marchant |
| uk | ours | I was. |
| uk | pulse | Pulsy |
| us | separation | Rebellation. |
| us | strengthen | strength in |
| uk | theft | Safetyulent. |
| us | theft | Zephth. |
| us | theoretical | See you reticle. |

## 仍缺的插画（54）

这 54 个词的 media 是 30。插画位（bit 1）没有置上。仓库里没有可用的本地图像模型。`scripts/atlas/gen_images.py` 走的是付费图像接口，这次不能用。没有提交剪贴画、库存照片或只有文字的占位图。

现有图的规格（量过 `public/atlas/img` 和 `thumb` 全部 7305 对）：

- 插画 `public/atlas/img/{id}.webp`：512×512，WebP 有损 VP8，yuv420p，无 alpha。7305 张里 7304 张是这个规格。唯一的例外是 `volume.webp`（VP8X，带 alpha），不要照那一张。
- 缩略图 `public/atlas/thumb/{id}.webp`：256×256，同样是 VP8、无 alpha。例外同样只有 `volume.webp`。
- `scripts/atlas/build_atlas.py` 从 768 母版压图：插画 `cwebp -q 74 -m 6 -resize 512 512`，缩略图 `cwebp -q 70 -m 6 -resize 256 256`。
- `scripts/atlas/gen_images.py` 的母版是 `cwebp -q 78 -m 6 -resize 768 768`，源图 1024×1024。
- 文件名就是目录 id。这 54 个 id 等于词头。

画风，沿用 `gen_images.py` 的 STYLE：

> Mid-century modern editorial illustration, like a plate from a vintage illustrated field guide. Strict limited palette: deep ink navy, warm terracotta, mustard ochre, muted sage green and soft sky blue on warm cream paper. Flat geometric shapes, confident clean silhouettes, subtle risograph grain and paper texture, gentle shading, one clear focal subject with generous negative space, centered square composition, calm and charming mood. Absolutely no text, letters, words, numbers, captions, signs, logos, watermarks or frames.

两张图都放到上面的路径之后，把该词的 index 行和 entries 里的 `m` 加上 bit 1，并把 `index.illustrated` 加 1。文件不齐时不要先把 bit 置上。

| id | 批次 | 义项 | 第一条例句 |
|---|---:|---|---|
| belly | 13 | n. 肚子 | My belly hurts after two bowls of noodles. |
| booth | 13 | n. 小隔间；亭 | Wait in the phone booth; I'll be one minute. |
| facial | 13 | adj. 面部的 | The facial cream stung the cut on his cheek. |
| import | 13 | v. 进口；输入 | The shop imports tea from Fujian every spring. |
| coke | 13 | n. 可乐 | He bought a bottle of coke after practice. |
| merchant | 13 | n. 商人；adj. 商业的 | The merchant counted the crates before the ship left. |
| adjust | 13 | v. 调整；适应 | Adjust the chair before you start writing. |
| flame | 13 | n. 火焰 | Keep your sleeve away from the flame. |
| inn | 13 | n. 小旅店 | We stayed at a small inn near the station. |
| nationwide | 13 | adj. 全国性的 | The speech contest is nationwide, so our school can enter. |
| scan | 13 | n. 浏览；扫描；v. 浏览；扫描 | Scan the page for dates before you read every line. |
| pulse | 13 | n. 脉搏 | The nurse checked my pulse after the race. |
| beg | 13 | v. 请求；乞求 | I won't beg the teacher for the answer. |
| graph | 13 | n. 图表；曲线图 | The graph shows how the plant grew each week. |
| strengthen | 13 | v. 加强；增强 | These exercises strengthen the muscles you use for jumping. |
| transform | 13 | v. 使改观；使改变形态 | They transform the hall into an exam room every June. |
| passive | 13 | adj. 被动的 | Rewrite the sentence in the passive if the doer is unknown. |
| deliberately | 13 | adv. 故意地 | He deliberately left the last question blank. |
| sympathy | 13 | n. 同情 | We sent a card to show our sympathy. |
| theoretical | 13 | adj. 理论的 | The theoretical result did not match the lab reading. |
| dash | 13 | v. 猛冲；n. 短跑；冲刺 | We dash to the canteen if the break is short. |
| bent | 13 | adj. 弯的 | The bent nail would not go into the wood. |
| aboard | 12 | adv. 在船上；上车 | The students are aboard the bus. |
| acknowledge | 12 | v. 承认 | She acknowledged the mistake. |
| ash | 12 | n. 灰 | Ash covered the path after the fire. |
| athletic | 12 | adj. 运动的；健壮的 | The athletic field is behind the hall. |
| bare | 12 | adj. 赤裸的；空的；v. 露出 | The shelf is bare. |
| barrier | 12 | n. 障碍；栏杆 | The barrier at the gate is down. |
| bored | 12 | adj. 厌倦的 | He was bored with the same worksheet. |
| boxing | 12 | n. 拳击 | Boxing practice is in the gym. |
| burst | 12 | v. 爆裂；突然发生 | The pipe may burst in the frost. |
| cheers | 12 | int. 干杯；谢谢 | She said cheers and put the cup down. |
| corrupt | 12 | adj. 腐败的；v. 使腐化 | The report calls the contract corrupt. |
| disability | 12 | n. 残疾 | The form asks about disability in private. |
| distant | 12 | adj. 遥远的 | The farm is distant, but the school is open. |
| examine | 12 | v. 检查 | The nurse will examine the cut. |
| grandma | 12 | n. 奶奶；外婆 | Her grandma makes soup every Sunday. |
| gravity | 12 | n. 重力 | Gravity keeps the book on the desk. |
| lap | 12 | n. 一圈；膝部 | She ran one more lap. |
| leaf | 12 | n. 叶子 | A yellow leaf fell on the path. |
| lightning | 12 | n. 闪电 | Lightning lit the playground. |
| marathon | 12 | n. 马拉松 | The marathon passes the school. |
| missile | 12 | n. 导弹 | The news mentions a missile and then gives the date. |
| ours | 12 | pron. 我们的 | The books on the desk are ours. |
| patience | 12 | n. 耐心 | The queue tested her patience. |
| pension | 12 | n. 养老金 | The pension arrives on the first day. |
| phenomenon | 12 | n. 现象 | The phenomenon is written on the chart. |
| precise | 12 | adj. 精确的 | The time must be precise. |
| separation | 12 | n. 分离 | The separation lasted one term. |
| spray | 12 | v. 喷洒；n. 喷雾 | Spray the plants, not the books. |
| theft | 12 | n. 盗窃 | The novel mentions a theft and then stops. |
| unemployment | 12 | n. 失业 | Unemployment rose after the factory closed. |
| widespread | 12 | adj. 普遍的；分布广的 | The practice is widespread in this town. |
| zoo | 12 | n. 动物园 | The zoo is closed on Monday. |

## 更早的缺口（只清点，这次不补）

这 59 个词之外，目录里还有 **162** 个词缺图和/或词头录音。其中 155 个缺插画和英音、美音，7 个已有插画、缺英音和美音（absorb, aware, calculate, conclude, daily, entire, likely）。这次没有给它们加文件，也没有改它们的 media 位。

`neighborhood` 在词光里有未占用的英式文件 `neighbourhood`（图、缩略图、英音、美音都在）。它属于下面这份更早的缺口，这次不复制。

| batch | id | word | 缺 | media |
|---:|---|---|---|---:|
| 3 | check | check | img+thumb,uk,us | 24 |
| 3 | dr | Dr. | img+thumb,uk,us | 24 |
| 3 | happy | happy | img+thumb,uk,us | 24 |
| 3 | himself | himself | img+thumb,uk,us | 24 |
| 3 | human-being | human being | img+thumb,uk,us | 24 |
| 3 | means | means | img+thumb,uk,us | 24 |
| 3 | oh | oh | img+thumb,uk,us | 24 |
| 3 | past | past | img+thumb,uk,us | 24 |
| 3 | saying | saying | img+thumb,uk,us | 24 |
| 3 | song | song | img+thumb,uk,us | 24 |
| 3 | thank | thank | img+thumb,uk,us | 24 |
| 3 | thinking | thinking | img+thumb,uk,us | 24 |
| 3 | whether | whether | img+thumb,uk,us | 24 |
| 3 | yes | yes | img+thumb,uk,us | 24 |
| 4 | center | center | img+thumb,uk,us | 24 |
| 4 | federal | federal | img+thumb,uk,us | 24 |
| 4 | itself | itself | img+thumb,uk,us | 24 |
| 4 | mom | mom | img+thumb,uk,us | 24 |
| 4 | okay | okay | img+thumb,uk,us | 24 |
| 4 | page | page | img+thumb,uk,us | 24 |
| 4 | themselves | themselves | img+thumb,uk,us | 24 |
| 4 | tv | TV | img+thumb,uk,us | 24 |
| 5 | association | association | img+thumb,uk,us | 24 |
| 5 | cancer | cancer | img+thumb,uk,us | 24 |
| 5 | color | color | img+thumb,uk,us | 24 |
| 5 | committee | committee | img+thumb,uk,us | 24 |
| 5 | dad | dad | img+thumb,uk,us | 24 |
| 5 | deep | deep | img+thumb,uk,us | 24 |
| 5 | defense | defense | img+thumb,uk,us | 24 |
| 5 | hi | hi | img+thumb,uk,us | 24 |
| 5 | justice | justice | img+thumb,uk,us | 24 |
| 5 | mine | mine | img+thumb,uk,us | 24 |
| 5 | north-east | north-east | img+thumb,uk,us | 24 |
| 5 | north-west | north-west | img+thumb,uk,us | 24 |
| 5 | opening | opening | img+thumb,uk,us | 24 |
| 5 | potential | potential | img+thumb,uk,us | 24 |
| 5 | search | search | img+thumb,uk,us | 24 |
| 5 | side-road | side road | img+thumb,uk,us | 24 |
| 5 | south-east | south-east | img+thumb,uk,us | 24 |
| 5 | south-west | south-west | img+thumb,uk,us | 24 |
| 6 | award | award | img+thumb,uk,us | 24 |
| 6 | herself | herself | img+thumb,uk,us | 24 |
| 6 | hot-dog | hot dog | img+thumb,uk,us | 24 |
| 6 | institute | institute | img+thumb,uk,us | 24 |
| 6 | luck | luck | img+thumb,uk,us | 24 |
| 6 | mrs | Mrs. | img+thumb,uk,us | 24 |
| 6 | physical-education | physical education | img+thumb,uk,us | 24 |
| 6 | religious | religious | img+thumb,uk,us | 24 |
| 6 | sad | sad | img+thumb,uk,us | 24 |
| 6 | trial | trial | img+thumb,uk,us | 24 |
| 6 | waiting-room | waiting room | img+thumb,uk,us | 24 |
| 6 | whom | whom | img+thumb,uk,us | 24 |
| 7 | abuse | abuse | img+thumb,uk,us | 24 |
| 7 | appeal | appeal | img+thumb,uk,us | 24 |
| 7 | beer | beer | img+thumb,uk,us | 24 |
| 7 | command | command | img+thumb,uk,us | 24 |
| 7 | labour | labour | img+thumb,uk,us | 24 |
| 7 | ms | Ms. | img+thumb,uk,us | 24 |
| 7 | muslim | Muslim | img+thumb,uk,us | 24 |
| 7 | personal-computer | personal computer | img+thumb,uk,us | 24 |
| 7 | victory | victory | img+thumb,uk,us | 24 |
| 7 | violence | violence | img+thumb,uk,us | 24 |
| 7 | yours | yours | img+thumb,uk,us | 24 |
| 8 | constitution | constitution | img+thumb,uk,us | 24 |
| 8 | desire | desire | img+thumb,uk,us | 24 |
| 8 | e-mail | e-mail | img+thumb,uk,us | 24 |
| 8 | heaven | heaven | img+thumb,uk,us | 24 |
| 8 | mm | mm | img+thumb,uk,us | 24 |
| 8 | pack | pack | img+thumb,uk,us | 24 |
| 8 | personnel | personnel | img+thumb,uk,us | 24 |
| 8 | troops | troops | img+thumb,uk,us | 24 |
| 8 | x-ray | X-ray | img+thumb,uk,us | 24 |
| 9 | bc | BC | img+thumb,uk,us | 24 |
| 9 | bonus | bonus | img+thumb,uk,us | 24 |
| 9 | broad | broad | img+thumb,uk,us | 24 |
| 9 | consistent | consistent | img+thumb,uk,us | 24 |
| 9 | everyday | everyday | img+thumb,uk,us | 24 |
| 9 | extension | extension | img+thumb,uk,us | 24 |
| 9 | flash | flash | img+thumb,uk,us | 24 |
| 9 | ice-cream | ice cream | img+thumb,uk,us | 24 |
| 9 | math | math | img+thumb,uk,us | 24 |
| 9 | neighborhood | neighborhood | img+thumb,uk,us | 24 |
| 9 | olympic | Olympic | img+thumb,uk,us | 24 |
| 9 | origin | origin | img+thumb,uk,us | 24 |
| 9 | quit | quit | img+thumb,uk,us | 24 |
| 9 | somehow | somehow | img+thumb,uk,us | 24 |
| 9 | surrounding | surrounding | img+thumb,uk,us | 24 |
| 9 | witness | witness | img+thumb,uk,us | 24 |
| 10 | aspect | aspect | img+thumb,uk,us | 24 |
| 10 | bishop | bishop | img+thumb,uk,us | 24 |
| 10 | breast | breast | img+thumb,uk,us | 24 |
| 10 | bye | bye | img+thumb,uk,us | 24 |
| 10 | cd | CD | img+thumb,uk,us | 24 |
| 10 | daddy | daddy | img+thumb,uk,us | 24 |
| 10 | enterprise | enterprise | img+thumb,uk,us | 24 |
| 10 | glory | glory | img+thumb,uk,us | 24 |
| 10 | hunter | hunter | img+thumb,uk,us | 24 |
| 10 | km | km | img+thumb,uk,us | 24 |
| 10 | liberty | liberty | img+thumb,uk,us | 24 |
| 10 | memorial | memorial | img+thumb,uk,us | 24 |
| 10 | minority | minority | img+thumb,uk,us | 24 |
| 10 | mum | mum | img+thumb,uk,us | 24 |
| 10 | output | output | img+thumb,uk,us | 24 |
| 10 | participate | participate | img+thumb,uk,us | 24 |
| 10 | possession | possession | img+thumb,uk,us | 24 |
| 10 | punishment | punishment | img+thumb,uk,us | 24 |
| 10 | reflect | reflect | img+thumb,uk,us | 24 |
| 10 | settle | settle | img+thumb,uk,us | 24 |
| 10 | spoken | spoken | img+thumb,uk,us | 24 |
| 10 | theater | theater | img+thumb,uk,us | 24 |
| 11 | abortion | abortion | img+thumb,uk,us | 24 |
| 11 | agenda | agenda | img+thumb,uk,us | 24 |
| 11 | aids | AIDS | img+thumb,uk,us | 24 |
| 11 | beast | beast | img+thumb,uk,us | 24 |
| 11 | communist | communist | img+thumb,uk,us | 24 |
| 11 | dvd | DVD | img+thumb,uk,us | 24 |
| 11 | equality | equality | img+thumb,uk,us | 24 |
| 11 | judgment | judgment | img+thumb,uk,us | 24 |
| 11 | outer | outer | img+thumb,uk,us | 24 |
| 11 | overcome | overcome | img+thumb,uk,us | 24 |
| 11 | parallel | parallel | img+thumb,uk,us | 24 |
| 11 | passage | passage | img+thumb,uk,us | 24 |
| 11 | photographer | photographer | img+thumb,uk,us | 24 |
| 11 | racial | racial | img+thumb,uk,us | 24 |
| 11 | sacrifice | sacrifice | img+thumb,uk,us | 24 |
| 11 | table-tennis | table tennis | img+thumb,uk,us | 24 |
| 11 | ton | ton | img+thumb,uk,us | 24 |
| 11 | worn | worn | img+thumb,uk,us | 24 |
| — | absorb | absorb | uk,us | 9 |
| — | at | at | img+thumb,uk,us | 24 |
| — | aware | aware | uk,us | 9 |
| — | calculate | calculate | uk,us | 9 |
| — | conclude | conclude | uk,us | 9 |
| — | could | could | img+thumb,uk,us | 24 |
| — | daily | daily | uk,us | 9 |
| — | do | do | img+thumb,uk,us | 24 |
| — | entire | entire | uk,us | 9 |
| — | for | for | img+thumb,uk,us | 24 |
| — | go | go | img+thumb,uk,us | 24 |
| — | have | have | img+thumb,uk,us | 24 |
| — | here | here | img+thumb,uk,us | 24 |
| — | how | how | img+thumb,uk,us | 24 |
| — | likely | likely | uk,us | 9 |
| — | may | may | img+thumb,uk,us | 24 |
| — | might | might | img+thumb,uk,us | 24 |
| — | mr | Mr. | img+thumb,uk,us | 24 |
| — | no | no | img+thumb,uk,us | 24 |
| — | not | not | img+thumb,uk,us | 24 |
| — | only | only | img+thumb,uk,us | 24 |
| — | part | part | img+thumb,uk,us | 24 |
| — | then | then | img+thumb,uk,us | 24 |
| — | this | this | img+thumb,uk,us | 24 |
| — | those | those | img+thumb,uk,us | 24 |
| — | used | used | img+thumb,uk,us | 24 |
| — | well | well | img+thumb,uk,us | 24 |
| — | what | what | img+thumb,uk,us | 24 |
| — | where | where | img+thumb,uk,us | 24 |
| — | while | while | img+thumb,uk,us | 24 |
| — | who | who | img+thumb,uk,us | 24 |
| — | will | will | img+thumb,uk,us | 24 |
| — | work | work | img+thumb,uk,us | 24 |
| — | would | would | img+thumb,uk,us | 24 |

## 校验

- `npm test`：28 项通过。
- `npm run check:atlas`：2597 词，5187 条例句，illustrated 2388，英音 2435，美音 2435，例句录音 2597，第二条例句录音 2590，errors 0。`oneExample` 警告仍是 7，是原先只有一条例句的卡。
- `ATLAS_BASE=/word-atlas-gaokao/ npm run build`：`tsc -b` 和 vite build 通过。
- 仓库的 GitHub workflow 只有 Pages 部署（push 到 main 才跑），没有单独的测试 CI。这次 PR 不合并，所以不会触发部署。
