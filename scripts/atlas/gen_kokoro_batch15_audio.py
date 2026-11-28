#!/usr/bin/env python3
"""Local Kokoro audio for batch 15 only.

Headwords that have no upstream UK/US file:
  US af_heart / en-us / 1.0, UK bf_emma / en-gb / 1.0, isolated headword.
Every new example:
  af_heart / en-us / 1.0.
Unused upstream files at a new id's ex/ex2 path are replaced.
Existing cards, their example bytes, splash audio, and upstream headword
clips are not rewritten. No paid API.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

UK_VOICE = "bf_emma"
UK_LANG = "en-gb"
US_VOICE = "af_heart"
US_LANG = "en-us"
SPEED = 1.0
ENGINE = "kokoro-onnx"
ENGINE_VERSION = "0.6.1"
MODEL_SHA = "beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a"
VOICES_SHA = "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"
TAIL_PAD_SEC = 0.08
SPLASH_SHA = "641e1f3d138c4a4b69027a24efac36e40440f4edfeb7615fbb42be5470cc45c9"

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "public" / "atlas"
MODEL_PATH = ROOT / ".local" / "kokoro" / "models" / "kokoro-v1.0.onnx"
VOICES_PATH = ROOT / ".local" / "kokoro" / "models" / "voices-v1.0.bin"
SELECTION = ROOT / "data" / "batch-15-selection.json"
CEFR_PATH = ROOT / "data" / "batch-15-cefr.json"
PROVENANCE_PATH = ROOT / "data" / "sentence-audio-provenance.json"
HEADWORD_PATH = ROOT / "data" / "batch-15-headword-audio.json"
SENTENCE_PATH = ROOT / "data" / "batch-15-sentence-audio.json"
SPLASH = ROOT / "public" / "sfx" / "splash-voice.mp3"
OLD_HEADWORD_PROVENANCE = ROOT / "data" / "headword-audio-provenance.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_sentence(text: str) -> str:
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


def require_models() -> None:
    for path, expected in ((MODEL_PATH, MODEL_SHA), (VOICES_PATH, VOICES_SHA)):
        if not path.is_file():
            raise SystemExit(f"Missing {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"Refusing {path.name}: sha256 {actual} != pinned {expected}")
    if sha256_file(SPLASH) != SPLASH_SHA:
        raise SystemExit("splash-voice.mp3 hash changed before synthesis")


def load_index() -> dict:
    return json.loads((PUB / "index.json").read_text(encoding="utf-8"))


def load_entries(index: dict) -> list[dict]:
    entries = []
    chunk = index["chunk"]
    for n in range((index["count"] + chunk - 1) // chunk):
        entries.extend(json.loads((PUB / "entries" / f"{n}.json").read_text(encoding="utf-8")))
    if len(entries) != index["count"]:
        raise SystemExit(f"entry count {len(entries)} != index {index['count']}")
    return entries


def encode_mp3(audio, sample_rate: int, dest: Path) -> float:
    import numpy as np

    padded = np.concatenate(
        [np.asarray(audio, dtype=np.float32), np.zeros(int(TAIL_PAD_SEC * sample_rate), dtype=np.float32)]
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(".partial.mp3")
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-f", "f32le", "-ar", str(sample_rate), "-ac", "1", "-i", "pipe:0",
                "-codec:a", "libmp3lame", "-b:a", "64k", "-ar", "44100", "-ac", "1",
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
        probe = json.loads(
            subprocess.check_output(
                [
                    "ffprobe", "-v", "error", "-select_streams", "a:0",
                    "-show_entries", "stream=codec_name,channels,sample_rate,bit_rate:format=duration",
                    "-of", "json", str(partial),
                ],
                text=True,
            )
        )
        stream = probe["streams"][0]
        duration = float(probe["format"]["duration"])
        if stream.get("codec_name") != "mp3" or stream.get("channels") != 1 or str(stream.get("sample_rate")) != "44100":
            raise RuntimeError(f"unexpected mp3 layout {stream}")
        if str(stream.get("bit_rate")) != "64000":
            raise RuntimeError(f"unexpected bitrate {stream.get('bit_rate')}")
        partial.replace(dest)
        return duration
    finally:
        if partial.exists():
            partial.unlink()


def qc_headword(audio, sample_rate: int, spoken, known: str) -> None:
    import numpy as np

    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim != 1 or audio.size == 0:
        raise RuntimeError("empty audio")
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio))))
    duration = audio.size / sample_rate
    got = "".join(item.phoneme for item in spoken)
    if got != known:
        raise RuntimeError(f"phoneme coverage {got!r} != {known!r}")
    if peak < 0.02 or rms < 0.005:
        raise RuntimeError(f"silent peak={peak:.4f} rms={rms:.4f}")
    if not (0.18 <= duration <= 3.5):
        raise RuntimeError(f"duration {duration:.3f}s outside 0.18–3.5s")


def word_count(text: str) -> int:
    import re

    return len(re.findall(r"[0-9A-Za-z'À-ÖØ-öø-ÿ]+", text))


def qc_sentence(audio, sample_rate: int, spoken, known: str, text: str) -> None:
    import numpy as np

    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim != 1 or audio.size == 0:
        raise RuntimeError("empty audio")
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio))))
    duration = audio.size / sample_rate
    got = "".join(item.phoneme for item in spoken)
    words = word_count(text)
    if got != known:
        raise RuntimeError(f"phoneme coverage {len(got)}/{len(known)}")
    if peak < 0.02 or rms < 0.005:
        raise RuntimeError(f"silent peak={peak:.4f} rms={rms:.4f}")
    last_gap = duration - float(spoken[-1].end)
    if last_gap > 0.45:
        raise RuntimeError(f"trailing gap {last_gap:.3f}s")
    if duration < max(0.4, words * 0.12):
        raise RuntimeError(f"too short {duration:.2f}s for {words} words")


def synthesize_text(kokoro, text: str, voice: str, lang: str, kind: str):
    errors = []
    for trim in (True, False):
        try:
            audio, sample_rate, spoken = kokoro.create_timed(text, voice=voice, speed=SPEED, lang=lang, trim=trim)
            phonemes = kokoro.tokenizer.phonemize(text, lang)
            known = kokoro.tokenizer.known(phonemes)
            if kind == "headword":
                qc_headword(audio, sample_rate, spoken, known)
            else:
                qc_sentence(audio, sample_rate, spoken, known, text)
            return audio, sample_rate, known, trim
        except Exception as exc:
            errors.append(f"{'trim' if trim else 'no-trim'}: {exc}")
    raise RuntimeError("; ".join(errors))


def allowed_dest(batch_ids: set[str], path: Path) -> None:
    if path.parent.parent != PUB / "audio" and path.parent != PUB / "audio":
        raise SystemExit(f"refusing path {path}")
    folder = path.parent.name
    if folder not in {"uk", "us", "ex", "ex2"}:
        raise SystemExit(f"refusing folder {folder}")
    if path.stem not in batch_ids:
        raise SystemExit(f"refusing to write audio outside batch 15: {path.name}")


def update_bits(index: dict, entries: list[dict], batch_ids: set[str]) -> None:
    by_id = {entry["id"]: entry for entry in entries}
    before = {row[0]: row[6] for row in index["words"]}
    changed = set()
    chunk = index["chunk"]
    for row in index["words"]:
        entry_id = row[0]
        entry = by_id[entry_id]
        if entry_id not in batch_ids:
            if entry["m"] != before[entry_id] or row[6] != before[entry_id]:
                raise SystemExit(f"media bit drifted on an old card: {entry_id}")
            continue
        media = entry["m"]
        if (PUB / "audio" / "uk" / f"{entry_id}.mp3").is_file():
            media |= 2
        if (PUB / "audio" / "us" / f"{entry_id}.mp3").is_file():
            media |= 4
        if (PUB / "audio" / "ex" / f"{entry_id}.mp3").is_file():
            media |= 8
        if (PUB / "audio" / "ex2" / f"{entry_id}.mp3").is_file():
            media |= 16
        entry["m"] = media
        row[6] = media
        pos = next(i for i, item in enumerate(index["words"]) if item[0] == entry_id)
        changed.add(pos // chunk)
    for row in index["words"]:
        if row[0] not in batch_ids and row[6] != before[row[0]]:
            raise SystemExit(f"old media bit changed: {row[0]}")
    for n in sorted(changed):
        block = entries[n * chunk : (n + 1) * chunk]
        (PUB / "entries" / f"{n}.json").write_text(
            json.dumps(block, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    index["illustrated"] = sum(1 for row in index["words"] if row[6] & 1)
    index["voiced"] = sum(1 for row in index["words"] if row[6] & 2)
    (PUB / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    smoke = "--smoke" in sys.argv
    require_models()
    from kokoro_onnx import Kokoro

    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    batch_ids = [row["id"] for row in selection]
    batch_set = set(batch_ids)
    if len(batch_ids) != 200 or len(batch_set) != 200:
        raise SystemExit("selection is not 200 unique ids")
    index = load_index()
    entries = load_entries(index)
    by_id = {entry["id"]: entry for entry in entries}
    missing = [entry_id for entry_id in batch_ids if entry_id not in by_id]
    if missing:
        raise SystemExit(f"cards missing: {missing[:5]}")
    old_verified = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))["verified"]
    old_headword_sha = sha256_file(OLD_HEADWORD_PROVENANCE)

    kokoro = Kokoro(str(MODEL_PATH), str(VOICES_PATH))
    for voice in (UK_VOICE, US_VOICE):
        if voice not in kokoro.voices:
            raise SystemExit(f"voice {voice} missing")

    headword_targets = []
    for entry_id in batch_ids:
        if smoke and entry_id not in {"yourselves", "pe", "cafe"}:
            continue
        for folder in ("uk", "us"):
            path = PUB / "audio" / folder / f"{entry_id}.mp3"
            if not path.exists():
                headword_targets.append((entry_id, folder))
    if not smoke and len(headword_targets) != 78:
        raise SystemExit(f"expected 78 missing headword clips, found {len(headword_targets)}")

    headword_records = []
    for n, (entry_id, folder) in enumerate(headword_targets, 1):
        voice, lang = (UK_VOICE, UK_LANG) if folder == "uk" else (US_VOICE, US_LANG)
        word = by_id[entry_id]["w"]
        dest = PUB / "audio" / folder / f"{entry_id}.mp3"
        allowed_dest(batch_set, dest)
        audio, sample_rate, known, trim = synthesize_text(kokoro, word, voice, lang, "headword")
        duration = encode_mp3(audio, sample_rate, dest)
        headword_records.append({
            "id": entry_id,
            "accent": folder,
            "voice": voice,
            "lang": lang,
            "speed": SPEED,
            "script": word,
            "phonemes": known,
            "duration": round(duration, 3),
            "trim": trim,
            "file": str(dest.relative_to(ROOT)),
            "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest),
        })
        if n % 10 == 0 or n == len(headword_targets):
            print(f"headword {n}/{len(headword_targets)}", flush=True)

    sentence_jobs = []
    for entry_id in batch_ids:
        if smoke and entry_id not in {"relay", "cafe", "compact-disk", "pe"}:
            continue
        for index_no, example in enumerate(by_id[entry_id]["ex"]):
            sentence_jobs.append((entry_id, index_no, example["en"]))
    sentence_records = []
    replaced = []
    for n, (entry_id, index_no, text) in enumerate(sentence_jobs, 1):
        folder = "ex" if index_no == 0 else "ex2"
        dest = PUB / "audio" / folder / f"{entry_id}.mp3"
        allowed_dest(batch_set, dest)
        if dest.exists():
            replaced.append(str(dest.relative_to(ROOT)))
        audio, sample_rate, known, trim = synthesize_text(kokoro, text, US_VOICE, US_LANG, "sentence")
        duration = encode_mp3(audio, sample_rate, dest)
        words = word_count(text)
        sentence_records.append({
            "id": entry_id,
            "index": index_no,
            "text": text,
            "script": normalize_sentence(text),
            "voice": US_VOICE,
            "lang": US_LANG,
            "speed": SPEED,
            "phonemes": known,
            "duration": round(duration, 3),
            "words": words,
            "secPerWord": round(duration / words, 3) if words else None,
            "trim": trim,
            "replacedUnusedUpstream": dest.name in {Path(item).name for item in replaced} and str(dest.relative_to(ROOT)) in replaced,
            "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest),
        })
        if n % 25 == 0 or n == len(sentence_jobs):
            print(f"sentence {n}/{len(sentence_jobs)}", flush=True)

    if smoke:
        print(json.dumps({"headwords": len(headword_records), "sentences": len(sentence_records)}, indent=2))
        return

    update_bits(index, entries, batch_set)
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    if provenance["verified"] != old_verified:
        raise SystemExit("provenance changed during synthesis")
    for record in sentence_records:
        provenance["verified"].setdefault(record["id"], {})[str(record["index"])] = record["script"]
    provenance["source"] = (
        provenance["source"]
        + " Batch 15 added 400 new-card examples with the same Kokoro voice, language, and speed. "
        + "Older verified scripts were not regenerated."
    )
    PROVENANCE_PATH.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rates = sorted(record["secPerWord"] for record in sentence_records if record["secPerWord"])
    median = rates[len(rates) // 2]
    outliers = [
        record for record in sentence_records
        if record["secPerWord"] and (record["secPerWord"] < median * 0.65 or record["secPerWord"] > median * 2.2)
    ]
    audit = json.loads(CEFR_PATH.read_text(encoding="utf-8"))
    generated_ids = {record["id"] for record in headword_records}
    for row in audit:
        row["headwordAudio"] = "kokoro" if row["id"] in generated_ids else "upstream"
        if row["id"] in generated_ids:
            row["missingUk"] = False
            row["missingUs"] = False
    CEFR_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    HEADWORD_PATH.write_text(json.dumps({
        "source": (
            "Batch 15 headword clips for new cards that had no upstream Word Atlas uk/us file. "
            "Kokoro speaks the isolated headword at speed 1.0. US voice af_heart, language en-us. "
            "UK voice bf_emma, language en-gb. Example clips, splash audio, and earlier headword "
            "provenance files were not the target of these clips. Illustrations were not generated."
        ),
        "generator": {
            "engine": ENGINE,
            "engineVersion": ENGINE_VERSION,
            "model": "kokoro-v1.0.onnx",
            "modelSha256": MODEL_SHA,
            "voices": "voices-v1.0.bin",
            "voicesSha256": VOICES_SHA,
            "encoding": "mp3 mono 44100 Hz 64 kbps",
            "tailPadSec": TAIL_PAD_SEC,
            "uk": {"voice": UK_VOICE, "lang": UK_LANG, "speed": SPEED},
            "us": {"voice": US_VOICE, "lang": US_LANG, "speed": SPEED},
        },
        "counts": {"words": len(generated_ids), "clips": len(headword_records)},
        "ids": sorted(generated_ids),
        "clips": headword_records,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    SENTENCE_PATH.write_text(json.dumps({
        "generator": {
            "engine": ENGINE,
            "engineVersion": ENGINE_VERSION,
            "voice": US_VOICE,
            "lang": US_LANG,
            "speed": SPEED,
            "encoding": "mp3 mono 44100 Hz 64 kbps",
            "modelSha256": MODEL_SHA,
            "voicesSha256": VOICES_SHA,
        },
        "counts": {
            "clips": len(sentence_records),
            "replacedUnusedUpstreamPaths": len(replaced),
            "durationOutliers": len(outliers),
        },
        "medianSecPerWord": median,
        "durationOutliers": [
            {"id": item["id"], "index": item["index"], "secPerWord": item["secPerWord"], "text": item["text"]}
            for item in outliers
        ],
        "replacedUnusedUpstream": replaced,
        "clips": sentence_records,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if sha256_file(SPLASH) != SPLASH_SHA:
        raise SystemExit("splash hash changed")
    if sha256_file(OLD_HEADWORD_PROVENANCE) != old_headword_sha:
        raise SystemExit("old headword provenance changed")
    index = load_index()
    print(json.dumps({
        "headwordClips": len(headword_records),
        "sentenceClips": len(sentence_records),
        "replacedUnused": len(replaced),
        "outliers": len(outliers),
        "voiced": index["voiced"],
        "illustrated": index["illustrated"],
        "count": index["count"],
    }, indent=2))


if __name__ == "__main__":
    main()
