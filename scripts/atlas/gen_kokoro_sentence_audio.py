#!/usr/bin/env python3
"""Record the current example sentences with local Kokoro, voice af_heart.

One sentence per call. No network during synthesis, no API keys, and no paid
TTS. Already-verified recordings whose stored script still matches the card
are left untouched. A new file is published only after the spoken phonemes
cover the full phonemization and the mp3 decodes.

The model weights and the virtualenv stay in gitignored ``.local/``.

Setup
-----
.. code-block:: bash

    sudo apt-get install -y espeak-ng ffmpeg
    python3 -m venv .local/kokoro-venv
    .local/kokoro-venv/bin/pip install 'kokoro-onnx==0.6.1' soundfile numpy
    mkdir -p .local/kokoro/models
    curl -L -o .local/kokoro/models/kokoro-v1.0.onnx \\
      https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
    curl -L -o .local/kokoro/models/voices-v1.0.bin \\
      https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin

The pinned SHA-256 values below are the model-files-v1.1 release assets.
Model license: Apache-2.0, hexgrad/Kokoro-82M. Runtime: MIT, kokoro-onnx.

Run
---
.. code-block:: bash

    .local/kokoro-venv/bin/python scripts/atlas/gen_kokoro_sentence_audio.py --sample
    .local/kokoro-venv/bin/python scripts/atlas/gen_kokoro_sentence_audio.py
    # optional local ASR spot check (not used by the website):
    .local/kokoro-venv/bin/pip install faster-whisper
    .local/kokoro-venv/bin/python scripts/atlas/gen_kokoro_sentence_audio.py --asr

``--sample`` records a fixed representative set, including concentrate.
The full run resumes from ``.local/kokoro/cache`` keyed by text, voice,
speed, language, engine version, and model hashes. Re-running does not
reuse an older public mp3 just because a file is already there.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

VOICE = "af_heart"
LANG = "en-us"
SPEED = 1.0
ENGINE = "kokoro-onnx"
ENGINE_VERSION = "0.6.1"
MODEL_SHA = "beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a"
VOICES_SHA = "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"
TAIL_PAD_SEC = 0.08

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "public" / "atlas"
MODEL_PATH = ROOT / ".local" / "kokoro" / "models" / "kokoro-v1.0.onnx"
VOICES_PATH = ROOT / ".local" / "kokoro" / "models" / "voices-v1.0.bin"
CACHE = ROOT / ".local" / "kokoro" / "cache"
RESULTS = ROOT / ".local" / "kokoro" / "results.jsonl"
PROVENANCE_PATH = ROOT / "data" / "sentence-audio-provenance.json"
MANIFEST_PATH = ROOT / "data" / "kokoro-sentence-audio-manifest.json"

# Short, long, punctuation, apostrophe, digits, question, exclamation, lowercase.
SAMPLE = [
    ("concentrate", 0),
    ("concentrate", 1),
    ("stable", 0),
    ("not", 0),
    ("behavior", 1),
    ("describe", 0),
    ("amazing", 0),
    ("soldier", 0),
    ("km", 0),
    ("mr", 0),
    ("discuss", 0),
    ("if", 0),
    ("electric", 0),
]

ID_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def normalize_sentence(text: str) -> str:
    """Match src/lib/sentenceAudio.ts so provenance comparisons stay exact."""
    text = unicodedata.normalize("NFKC", text)
    text = (
        text.replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‐", "-")
        .replace("‑", "-")
        .replace("–", "-")
        .replace("—", "-")
    )
    return "".join(" " if ch.isspace() else ch for ch in text).lower()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_models() -> None:
    for path, expected in ((MODEL_PATH, MODEL_SHA), (VOICES_PATH, VOICES_SHA)):
        if not path.is_file():
            raise SystemExit(
                f"Missing {path}. Download the official model-files-v1.1 asset into .local/kokoro/models/. See the module docstring."
            )
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"Refusing {path.name}: sha256 {actual} != pinned {expected}")


def cache_key(text: str) -> str:
    payload = "\n".join(
        [ENGINE, ENGINE_VERSION, MODEL_SHA, VOICES_SHA, VOICE, LANG, f"{SPEED:.1f}", text]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_entries() -> list[dict]:
    index = json.loads((PUB / "index.json").read_text(encoding="utf-8"))
    entries = []
    chunk = index["chunk"]
    for n in range((index["count"] + chunk - 1) // chunk):
        entries.extend(json.loads((PUB / "entries" / f"{n}.json").read_text(encoding="utf-8")))
    if len(entries) != index["count"]:
        raise SystemExit(f"entry count {len(entries)} != index {index['count']}")
    return entries


def destination(entry_id: str, index: int) -> Path:
    if not ID_RE.fullmatch(entry_id) or index not in (0, 1):
        raise SystemExit(f"refusing unsafe audio path {entry_id} [{index}]")
    folder = "ex" if index == 0 else "ex2"
    return PUB / "audio" / folder / f"{entry_id}.mp3"


def tasks_and_retained(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    verified = provenance.get("verified") or {}
    todo, retained = [], []
    for entry in entries:
        slots = verified.get(entry["id"]) or {}
        for index, example in enumerate(entry["ex"]):
            text = example["en"]
            script = slots.get(str(index))
            if script == normalize_sentence(text):
                path = destination(entry["id"], index)
                if not path.is_file():
                    raise SystemExit(f"retained recording missing on disk: {path}")
                retained.append(
                    {
                        "id": entry["id"],
                        "index": index,
                        "text": text,
                        "script": script,
                        "sha256": sha256_file(path),
                        "bytes": path.stat().st_size,
                    }
                )
                continue
            todo.append({"id": entry["id"], "index": index, "text": text})
    return todo, retained


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def synthesize(kokoro, text: str, trim: bool):
    audio, sample_rate, spoken = kokoro.create_timed(
        text, voice=VOICE, speed=SPEED, lang=LANG, trim=trim
    )
    phonemes = kokoro.tokenizer.phonemize(text, LANG)
    known = kokoro.tokenizer.known(phonemes)
    got = "".join(item.phoneme for item in spoken)
    return audio, sample_rate, spoken, known, got


def qc_audio(audio, sample_rate: int, spoken, known: str, got: str, text: str) -> dict:
    import numpy as np

    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim != 1 or audio.size == 0:
        return {"ok": False, "reason": "empty audio"}
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio))))
    duration = float(audio.size / sample_rate)
    words = word_count(text)
    if peak < 0.02 or rms < 0.005:
        return {"ok": False, "reason": f"silent peak={peak:.4f} rms={rms:.4f}"}
    if not spoken or got != known:
        return {
            "ok": False,
            "reason": f"phoneme coverage {len(got)}/{len(known)}",
            "duration": duration,
        }
    last_gap = duration - float(spoken[-1].end)
    if last_gap > 0.45:
        return {"ok": False, "reason": f"trailing gap {last_gap:.3f}s", "duration": duration}
    if duration < max(0.4, words * 0.12):
        return {"ok": False, "reason": f"too short {duration:.2f}s for {words} words", "duration": duration}
    return {
        "ok": True,
        "duration": round(duration, 3),
        "words": words,
        "secPerWord": round(duration / words, 3) if words else None,
        "phonemes": len(known),
        "peak": round(peak, 4),
        "rms": round(rms, 4),
        "lastGap": round(last_gap, 3),
    }


def encode_mp3(audio, sample_rate: int, dest: Path) -> None:
    import numpy as np

    padded = np.concatenate(
        [np.asarray(audio, dtype=np.float32), np.zeros(int(TAIL_PAD_SEC * sample_rate), dtype=np.float32)]
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(".partial.mp3")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-f",
                "f32le",
                "-ar",
                str(sample_rate),
                "-ac",
                "1",
                "-i",
                "pipe:0",
                "-codec:a",
                "libmp3lame",
                "-b:a",
                "64k",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(partial),
            ],
            input=padded.tobytes(),
            check=True,
        )
        decoded = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(partial), "-f", "null", "-"],
            check=False,
            capture_output=True,
        )
        if decoded.returncode != 0:
            raise RuntimeError(decoded.stderr.decode("utf-8", "replace")[:400])
        probe = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=codec_name,channels,sample_rate:format=duration",
                "-of",
                "json",
                str(partial),
            ],
            text=True,
        )
        info = json.loads(probe)
        stream = info["streams"][0]
        mp3_duration = float(info["format"]["duration"])
        wav_duration = padded.size / sample_rate
        if stream.get("codec_name") != "mp3" or stream.get("channels") != 1 or str(stream.get("sample_rate")) != "44100":
            raise RuntimeError(f"unexpected mp3 layout {stream}")
        if abs(mp3_duration - wav_duration) > 0.3:
            raise RuntimeError(f"mp3 duration {mp3_duration:.3f}s vs wav {wav_duration:.3f}s")
        partial.replace(dest)
    finally:
        if partial.exists():
            partial.unlink()


def append_result(row: dict) -> None:
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def load_kokoro():
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(str(MODEL_PATH), str(VOICES_PATH))
    if VOICE not in kokoro.voices:
        raise SystemExit(f"voice {VOICE} missing from voices file")
    if not kokoro.has_timings:
        raise SystemExit("model does not report phoneme durations; refusing to generate without a truncation check")
    return kokoro


def produce(kokoro, text: str) -> tuple[dict, bytes]:
    """Return QC plus mp3 bytes. The no-trim pass runs only if the trimmed pass fails."""
    errors = []
    for trim in (True, False):
        try:
            audio, sample_rate, spoken, known, got = synthesize(kokoro, text, trim)
            report = qc_audio(audio, sample_rate, spoken, known, got, text)
            report["trim"] = trim
            if not report["ok"]:
                errors.append(report.get("reason", "qc") + (" trim" if trim else " no-trim"))
                continue
            key = cache_key(text)
            dest = CACHE / f"{key}.mp3"
            encode_mp3(audio, sample_rate, dest)
            report["cache"] = key
            (CACHE / f"{key}.qc.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            return report, dest.read_bytes()
        except Exception as exc:
            errors.append(("trim " if trim else "no-trim ") + str(exc)[:240])
    raise RuntimeError("; ".join(errors) or "synthesis failed")


def publish(entry_id: str, index: int, payload: bytes, retained_keys: set[tuple[str, int]]) -> Path:
    if (entry_id, index) in retained_keys:
        raise SystemExit(f"refusing to overwrite retained recording {entry_id} [{index}]")
    path = destination(entry_id, index)
    partial = path.with_suffix(".partial.mp3")
    partial.write_bytes(payload)
    partial.replace(path)
    return path


def fold_results() -> dict[tuple[str, int], dict]:
    folded: dict[tuple[str, int], dict] = {}
    if not RESULTS.exists():
        return folded
    for line in RESULTS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        folded[(row["id"], int(row["index"]))] = row
    return folded


def generate(todo: list[dict], retained: list[dict], publish_files: bool) -> dict[tuple[str, int], dict]:
    require_models()
    if not shutil_which("ffmpeg") or not shutil_which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")
    retained_keys = {(row["id"], row["index"]) for row in retained}
    kokoro = None
    done = fold_results()
    total = len(todo)
    for n, job in enumerate(todo, start=1):
        key = cache_key(job["text"])
        cached_mp3 = CACHE / f"{key}.mp3"
        cached_qc = CACHE / f"{key}.qc.json"
        row = done.get((job["id"], job["index"]))
        if cached_mp3.is_file() and cached_qc.is_file():
            report = json.loads(cached_qc.read_text(encoding="utf-8"))
            if report.get("ok") and report.get("cache") == key:
                if publish_files:
                    publish(job["id"], job["index"], cached_mp3.read_bytes(), retained_keys)
                if not row or row.get("cache") != key or row.get("status") != "ok":
                    row = {
                        "id": job["id"],
                        "index": job["index"],
                        "text": job["text"],
                        "status": "ok",
                        "resumed": True,
                        **{k: report[k] for k in ("duration", "words", "secPerWord", "phonemes", "trim", "cache") if k in report},
                        "bytes": cached_mp3.stat().st_size,
                        "sha256": sha256_file(cached_mp3),
                    }
                    append_result(row)
                    done[(job["id"], job["index"])] = row
                print(f"skip {n}/{total} {job['id']}[{job['index']}] cache", flush=True)
                continue
        if kokoro is None:
            kokoro = load_kokoro()
        try:
            report, payload = produce(kokoro, job["text"])
            path = None
            if publish_files:
                path = publish(job["id"], job["index"], payload, retained_keys)
            row = {
                "id": job["id"],
                "index": job["index"],
                "text": job["text"],
                "status": "ok",
                "resumed": False,
                "duration": report["duration"],
                "words": report["words"],
                "secPerWord": report["secPerWord"],
                "phonemes": report["phonemes"],
                "trim": report["trim"],
                "cache": report["cache"],
                "bytes": len(payload) if path is None else path.stat().st_size,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        except Exception as exc:
            row = {
                "id": job["id"],
                "index": job["index"],
                "text": job["text"],
                "status": "failed",
                "reason": str(exc)[:500],
            }
            print(f"FAIL {job['id']}[{job['index']}] {row['reason']}", flush=True)
        append_result(row)
        done[(job["id"], job["index"])] = row
        if n % 50 == 0 or n == total or row["status"] != "ok":
            print(
                f"{row['status']} {n}/{total} {job['id']}[{job['index']}] {row.get('duration', '')}",
                flush=True,
            )
    return done


def shutil_which(name: str) -> str | None:
    from shutil import which

    return which(name)


def duration_outliers(rows: list[dict]) -> list[dict]:
    rates = [row["secPerWord"] for row in rows if row.get("status") == "ok" and row.get("secPerWord")]
    if not rates:
        return []
    rates_sorted = sorted(rates)
    median = rates_sorted[len(rates_sorted) // 2]
    flagged = []
    for row in rows:
        rate = row.get("secPerWord")
        if row.get("status") != "ok" or not rate:
            continue
        if rate < median * 0.65 or rate > median * 2.2:
            flagged.append(
                {
                    "id": row["id"],
                    "index": row["index"],
                    "secPerWord": rate,
                    "duration": row.get("duration"),
                    "words": row.get("words"),
                    "medianSecPerWord": round(median, 3),
                    "text": row["text"],
                }
            )
    return flagged


def write_metadata(entries: list[dict], retained: list[dict], done: dict[tuple[str, int], dict]) -> dict:
    """Point the app at new files only when that exact sentence was recorded."""
    verified: dict[str, dict[str, str]] = {}
    for row in retained:
        verified.setdefault(row["id"], {})[str(row["index"])] = row["script"]
    current = {
        (entry["id"], index): example["en"]
        for entry in entries
        for index, example in enumerate(entry["ex"])
    }
    generated = []
    failed = []
    for (entry_id, index), row in sorted(done.items()):
        if row.get("status") != "ok":
            failed.append({"id": entry_id, "index": index, "reason": row.get("reason", "")})
            continue
        path = destination(entry_id, index)
        card_text = current.get((entry_id, index))
        if card_text is None or normalize_sentence(card_text) != normalize_sentence(row["text"]):
            failed.append({"id": entry_id, "index": index, "reason": "card text changed after synthesis"})
            continue
        if not path.is_file():
            failed.append({"id": entry_id, "index": index, "reason": "qc passed but mp3 missing"})
            continue
        verified.setdefault(entry_id, {})[str(index)] = normalize_sentence(card_text)
        generated.append(row)
    for row in retained:
        if sha256_file(destination(row["id"], row["index"])) != row["sha256"]:
            raise SystemExit(f"retained file changed: {row['id']} [{row['index']}]")

    provenance = {
        "source": (
            "A sentence file may play only when the current example normalizes to verified[id][index]. "
            "Kokoro slots were synthesized locally from that exact text with kokoro-onnx "
            f"{ENGINE_VERSION}, voice {VOICE}, lang {LANG}, speed {SPEED}. "
            "Retained slots are upstream recordings whose script still matches; they were not regenerated. "
            "verified clips are US English unless clipAccent says otherwise. "
            "high/0 remains the British ElevenLabs everyday clip. Retained second examples remain US ElevenLabs. "
            "Kokoro clips are US af_heart and must not be described as British. "
            "A later text edit that does not update this script fails validation and withholds playback."
        ),
        "generator": {
            "engine": ENGINE,
            "engineVersion": ENGINE_VERSION,
            "model": "kokoro-v1.0.onnx",
            "modelSha256": MODEL_SHA,
            "voices": "voices-v1.0.bin",
            "voicesSha256": VOICES_SHA,
            "modelRelease": "https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1",
            "modelRepo": "hexgrad/Kokoro-82M",
            "modelLicense": "Apache-2.0",
            "runtimeLicense": "MIT",
            "runtimeRepo": "https://github.com/thewh1teagle/kokoro-onnx",
            "voice": VOICE,
            "lang": LANG,
            "speed": SPEED,
            "accent": "us",
            "encoding": "mp3 mono 44100 Hz 64 kbps",
        },
        "clipAccent": {"high": {"0": "uk"}},
        "retainedUpstream": [f"{row['id']}:{row['index']}" for row in retained],
        "verified": {entry_id: verified[entry_id] for entry_id in sorted(verified)},
    }
    PROVENANCE_PATH.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_media_bits(entries, provenance["verified"])

    outliers = duration_outliers(generated)
    bytes_total = sum(row["bytes"] for row in generated)
    manifest = {
        "generator": provenance["generator"],
        "counts": {
            "examplesOnCards": sum(len(entry["ex"]) for entry in entries),
            "generated": len(generated),
            "resumedFromCache": sum(1 for row in generated if row.get("resumed")),
            "retainedUpstream": len(retained),
            "failed": len(failed),
        },
        "bytes": bytes_total,
        "durationOutliers": outliers,
        "failures": failed,
        "retainedUpstream": provenance["retainedUpstream"],
        "files": [
            {
                "id": row["id"],
                "index": row["index"],
                "bytes": row["bytes"],
                "duration": row.get("duration"),
                "words": row.get("words"),
                "phonemes": row.get("phonemes"),
                "sha256": row["sha256"],
                "textSha256": hashlib.sha256(row["text"].encode("utf-8")).hexdigest(),
            }
            for row in sorted(generated, key=lambda item: (item["id"], item["index"]))
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("counts", "bytes")}, indent=2), flush=True)
    print(f"duration outliers {len(outliers)}", flush=True)
    return manifest


def update_media_bits(entries: list[dict], verified: dict) -> None:
    """Set example-audio bits where a verified file exists. Leave image and headword bits alone."""
    index_path = PUB / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in entries}
    changed_chunks = set()
    chunk = index["chunk"]
    for n, row in enumerate(index["words"]):
        entry = by_id[row[0]]
        slots = verified.get(entry["id"]) or {}
        media = entry["m"]
        if "0" in slots and destination(entry["id"], 0).is_file():
            media |= 8
        if "1" in slots and destination(entry["id"], 1).is_file():
            media |= 16
        if media != entry["m"] or row[6] != media:
            entry["m"] = media
            row[6] = media
            changed_chunks.add(n // chunk)
    for n in sorted(changed_chunks):
        block = []
        for row in index["words"][n * chunk : (n + 1) * chunk]:
            block.append(by_id[row[0]])
        path = PUB / "entries" / f"{n}.json"
        path.write_text(json.dumps(block, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    index_path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def run_asr(rows: list[dict], sample_keys: set[tuple[str, int]]) -> dict:
    """Spot-check with local faster-whisper. This does not ship to visitors."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit(
            "faster-whisper is not installed in .local/kokoro-venv. ASR was not run. Phoneme coverage still gated publication."
        ) from exc
    outliers = {(item["id"], item["index"]) for item in duration_outliers(rows)}
    import random

    ok_rows = [row for row in rows if row.get("status") == "ok"]
    random.seed(20261113)
    extra = random.sample(ok_rows, k=min(24, len(ok_rows)))
    chosen = []
    seen = set()
    for row in ok_rows:
        key = (row["id"], int(row["index"]))
        if key in sample_keys or key in outliers or row in extra:
            if key not in seen:
                chosen.append(row)
                seen.add(key)
    cache = ROOT / ".local" / "kokoro" / "hf"
    cache.mkdir(parents=True, exist_ok=True)
    model = WhisperModel("base.en", device="cpu", compute_type="int8", download_root=str(cache))
    reports = []
    failures = []
    for row in chosen:
        path = destination(row["id"], int(row["index"]))
        # Decode with ffmpeg so ASR does not depend on a PyAV build.
        pcm = subprocess.check_output(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(path),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-f",
                "f32le",
                "pipe:1",
            ]
        )
        import numpy as np

        audio = np.frombuffer(pcm, dtype=np.float32)
        segments, _info = model.transcribe(
            audio,
            language="en",
            vad_filter=False,
            beam_size=5,
            condition_on_previous_text=False,
        )
        heard = " ".join(segment.text.strip() for segment in segments).strip()
        ratio = word_ratio(row["text"], heard)
        tail_ok = tail_words_present(row["text"], heard)
        item = {
            "id": row["id"],
            "index": row["index"],
            "ratio": round(ratio, 3),
            "tailOk": tail_ok,
            "text": row["text"],
            "heard": heard,
            "sample": (row["id"], int(row["index"])) in sample_keys,
            "outlier": (row["id"], int(row["index"])) in outliers,
        }
        reports.append(item)
        if ratio < 0.45 or not tail_ok:
            failures.append(item)
            print(f"ASR FLAG {row['id']}[{row['index']}] ratio={ratio:.2f} tail={tail_ok}", flush=True)
            print(f"  text  {row['text']}", flush=True)
            print(f"  heard {heard}", flush=True)
        else:
            print(f"ASR ok {row['id']}[{row['index']}] ratio={ratio:.2f}", flush=True)
    report = {"model": "faster-whisper base.en", "checked": len(reports), "flags": failures, "items": reports}
    qc_path = ROOT / "data" / "kokoro-sentence-audio-qc.json"
    previous = {}
    if qc_path.exists():
        previous = json.loads(qc_path.read_text(encoding="utf-8"))
    previous["asr"] = report
    qc_path.write_text(json.dumps(previous, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def norm_words(text: str) -> list[str]:
    folded = normalize_sentence(text).replace("'", "")
    return re.findall(r"[a-z0-9]+", folded)


def word_ratio(reference: str, hypothesis: str) -> float:
    from difflib import SequenceMatcher

    left, right = norm_words(reference), norm_words(hypothesis)
    if not left:
        return 0.0
    return SequenceMatcher(a=left, b=right).ratio()


NUMBER_WORDS = {
    "zero": "0",
    "oh": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
}


def canon_word(word: str) -> str:
    return NUMBER_WORDS.get(word, word)


def tail_words_present(reference: str, hypothesis: str) -> bool:
    """The last two reference words should be audible. Digits may be heard as words."""
    ref = norm_words(reference)
    hyp = {canon_word(word) for word in norm_words(hypothesis)}
    if len(ref) < 2:
        return all(canon_word(word) in hyp for word in ref)
    tail = [canon_word(word) for word in ref[-2:] if not word.isdigit()]
    if not tail:
        return True
    return all(word in hyp for word in tail)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Kokoro af_heart example recordings")
    parser.add_argument("--sample", action="store_true", help="record the representative set only")
    parser.add_argument("--no-publish", action="store_true", help="write the cache but not public mp3s")
    parser.add_argument("--write-meta", action="store_true", help="rewrite provenance, media bits, and the manifest from the cache")
    parser.add_argument("--asr", action="store_true", help="local ASR spot check of the sample, outliers, and 24 other clips")
    args = parser.parse_args()

    entries = load_entries()
    todo, retained = tasks_and_retained(entries)
    sample_keys = set(SAMPLE)
    if args.asr:
        rows = list(fold_results().values())
        if not rows:
            raise SystemExit("no generator results to check")
        report = run_asr(rows, sample_keys)
        print(json.dumps({"checked": report["checked"], "flags": len(report["flags"])}, indent=2))
        if report["flags"]:
            sys.exit(2)
        return
    if args.write_meta and not args.sample:
        manifest = write_metadata(entries, retained, fold_results())
        if manifest["counts"]["failed"]:
            sys.exit(1)
        return

    selected = todo
    if args.sample:
        wanted = sample_keys
        selected = [job for job in todo if (job["id"], job["index"]) in wanted]
        missing = wanted - {(job["id"], job["index"]) for job in selected}
        retained_hit = missing & {(row["id"], row["index"]) for row in retained}
        missing -= retained_hit
        if missing:
            raise SystemExit(f"sample sentences not on cards: {sorted(missing)}")
        print(f"sample {len(selected)} retained-in-sample {len(retained_hit)}", flush=True)
    print(f"todo {len(selected)} retained {len(retained)}", flush=True)
    generate(selected, retained, publish_files=not args.no_publish)
    if not args.sample:
        manifest = write_metadata(entries, retained, fold_results())
        if manifest["counts"]["failed"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
