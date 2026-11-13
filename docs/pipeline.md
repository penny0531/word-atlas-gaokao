# 内容生成流程 / Content pipeline

所有脚本在 `scripts/atlas/`，凭据只从环境变量或仓库外目录读取（见 [SECURITY.md](../SECURITY.md)）。中间产物写入被 Git 忽略的 `.local/forge/`，可断点续跑。

1. **词头**：`.local/forge/headwords.json`，每项 `{hid, word, raw}`。`raw` 是可选的义项提示，只用于判断哪些义项重要，不会被复制进输出。
2. **词条文本** `gen_text.py`：每批 10 个词，按 [`gen_text.py`](../scripts/atlas/gen_text.py) 中的编写规范（准确优先、原创、两类例句、不编造词源、安全中立）生成 JSON。
3. **插画** `gen_images.py`：每个词条自带一个场景描述 `scene`，与统一画风提示词组合后生成 1024px 图片，压缩为 768px WebP 母版。按学习路线顺序生成。
4. **发音** `gen_word_audio.py`：ElevenLabs，英音 Alice、美音 Sarah。
5. **例句朗读** `gen_sentence_audio.py`：为 `ex[0]` 合成朗读，按学习路线顺序。
6. **编译** `build_atlas.py`：清洗字段、排序、切块，生成 `public/atlas/` 与 `data/`。
7. **校验** `npm run check:atlas`：结构、顺序、引用与媒体文件存在性。

```bash
export SUB2_BASE_URL=... SUB2_API_KEY=... ELEVENLABS_API_KEY=...
python3 scripts/atlas/gen_text.py --workers 8
python3 scripts/atlas/gen_images.py --workers 8 --follow
python3 scripts/atlas/gen_word_audio.py
python3 scripts/atlas/gen_sentence_audio.py --follow
python3 scripts/atlas/build_atlas.py
npm run check:atlas
```

`SUB2_BASE_URL` 指向任意 OpenAI 兼容的接口。

## 例句录音（Kokoro af_heart）

当前词卡例句使用本地开源 Kokoro，不用付费 TTS，也不读取 API key。声音是 `af_heart`，语言 `en-us`，语速 `1.0`。模型是 [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)（Apache-2.0），运行时是 [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) `0.6.1`（MIT）。权重用官方 `model-files-v1.1` 的 `kokoro-v1.0.onnx` 与 `voices-v1.0.bin`，放在被 Git 忽略的 `.local/kokoro/models/`，不要提交。

每条例句单独合成。缓存键是例句原文、声音、语速、语言、运行时版本和模型哈希。原文仍与 `data/sentence-audio-provenance.json` 一致的上游录音会跳过，不会被覆盖。未通过音素覆盖或 mp3 解码检查的句子不会写入 provenance，播放会继续回退到设备朗读。

```bash
sudo apt-get install -y espeak-ng ffmpeg
python3 -m venv .local/kokoro-venv
.local/kokoro-venv/bin/pip install 'kokoro-onnx==0.6.1' soundfile numpy
mkdir -p .local/kokoro/models
curl -L -o .local/kokoro/models/kokoro-v1.0.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
curl -L -o .local/kokoro/models/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin
.local/kokoro-venv/bin/python scripts/atlas/gen_kokoro_sentence_audio.py --sample
.local/kokoro-venv/bin/python scripts/atlas/gen_kokoro_sentence_audio.py
```

`scripts/atlas/gen_sentence_audio.py` 是上游 ElevenLabs 流程，生成这批例句时不要运行它。

词头英音、美音和开屏口播不由这个脚本写入。Kokoro 例句是美式，不标成英式。听者设备上的「英式 / 美式」开关仍只决定词头用哪一条原录音；没有例句录音时，设备朗读才跟随这个开关。

## 质量边界

自动校验覆盖结构、字段、顺序和文件，不覆盖语义正确性。插画和例句没有逐条人工审校；发现问题请提 Issue 或 PR。例句录音另有音素覆盖、时长和 mp3 整文件解码检查，见 `data/kokoro-sentence-audio-manifest.json`。抽查 ASR 只在生成机器上运行，网站不下载语音模型。
