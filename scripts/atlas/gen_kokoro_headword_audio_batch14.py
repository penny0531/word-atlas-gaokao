#!/usr/bin/env python3
"""UK/US headword audio for batch 14 cards that have no upstream clip.

US: Kokoro af_heart, en-us, speed 1.0.
UK: Kokoro bf_emma, en-gb, speed 1.0.
Each clip is the isolated headword. No paid API.

The script refuses to overwrite an existing headword file, and it never
writes example audio, splash audio, or illustrations.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
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

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "public" / "atlas"
MODEL_PATH = ROOT / ".local" / "kokoro" / "models" / "kokoro-v1.0.onnx"
VOICES_PATH = ROOT / ".local" / "kokoro" / "models" / "voices-v1.0.bin"
PROVENANCE_PATH = ROOT / "data" / "batch-14-headword-audio.json"
AUDIT_PATH = ROOT / "data" / "batch-14-cefr.json"
SENTENCE_PROVENANCE = ROOT / "data" / "sentence-audio-provenance.json"
OLD_HEADWORD_PROVENANCE = ROOT / "data" / "headword-audio-provenance.json"
SPLASH = ROOT / "public" / "sfx" / "splash-voice.mp3"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_models() -> None:
    for path, expected in ((MODEL_PATH, MODEL_SHA), (VOICES_PATH, VOICES_SHA)):
        if not path.is_file():
            raise SystemExit(f"Missing {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"Refusing {path.name}: sha256 {actual} != pinned {expected}")


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


def targets(entries_by_id: dict) -> list[str]:
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    ids = [row["id"] for row in audit if row["missingUk"] or row["missingUs"]]
    if len(ids) != 32:
        raise SystemExit(f"expected 32 headword gaps, found {len(ids)}")
    for entry_id in ids:
        entry = entries_by_id[entry_id]
        if entry["w"].lower() != entry_id:
            raise SystemExit(f"unexpected headword {entry_id} / {entry['w']}")
        if entry["m"] & 6:
            raise SystemExit(f"{entry_id} already has a headword bit {entry['m']}")
        for folder in ("uk", "us"):
            path = PUB / "audio" / folder / f"{entry_id}.mp3"
            if path.exists():
                raise SystemExit(f"refusing to overwrite {path}")
    return ids


def qc_audio(audio, sample_rate: int, spoken, known: str) -> None:
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
    # Isolated short words such as ant and zip can be under 0.30s.
    if not (0.18 <= duration <= 3.5):
        raise RuntimeError(f"duration {duration:.3f}s outside 0.18–3.5s")


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


def synthesize(ids: list[str], entries_by_id: dict) -> list[dict]:
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(str(MODEL_PATH), str(VOICES_PATH))
    for voice in (UK_VOICE, US_VOICE):
        if voice not in kokoro.voices:
            raise SystemExit(f"voice {voice} missing")
    records = []
    done = 0
    total = len(ids) * 2
    for entry_id in ids:
        word = entries_by_id[entry_id]["w"]
        for accent, voice, lang, folder in (
            ("uk", UK_VOICE, UK_LANG, "uk"),
            ("us", US_VOICE, US_LANG, "us"),
        ):
            errors = []
            audio = spoken = known = None
            sample_rate = 0
            trim_used = None
            for trim in (True, False):
                try:
                    audio, sample_rate, spoken = kokoro.create_timed(
                        word, voice=voice, speed=SPEED, lang=lang, trim=trim
                    )
                    phonemes = kokoro.tokenizer.phonemize(word, lang)
                    known = kokoro.tokenizer.known(phonemes)
                    qc_audio(audio, sample_rate, spoken, known)
                    trim_used = trim
                    break
                except Exception as exc:
                    errors.append(f"{'trim' if trim else 'no-trim'}: {exc}")
                    audio = None
            if audio is None:
                raise SystemExit(f"FAIL {entry_id} {accent}: {'; '.join(errors)}")
            dest = PUB / "audio" / folder / f"{entry_id}.mp3"
            duration = encode_mp3(audio, sample_rate, dest)
            records.append({
                "id": entry_id,
                "accent": accent,
                "voice": voice,
                "lang": lang,
                "speed": SPEED,
                "script": word,
                "phonemes": known,
                "duration": round(duration, 3),
                "trim": trim_used,
                "file": str(dest.relative_to(ROOT)),
                "bytes": dest.stat().st_size,
                "sha256": sha256_file(dest),
            })
            done += 1
            if done % 16 == 0 or done == total:
                print(f"synthesized {done}/{total}", flush=True)
    return records


def update_catalog(ids: list[str], entries: list[dict], index: dict) -> None:
    by_id = {entry["id"]: entry for entry in entries}
    chunk = index["chunk"]
    changed = set()
    idset = set(ids)
    before = {row[0]: row[6] for row in index["words"]}
    for entry_id in ids:
        entry = by_id[entry_id]
        media = entry["m"]
        for bit, folder in ((2, "uk"), (4, "us")):
            path = PUB / "audio" / folder / f"{entry_id}.mp3"
            if not path.is_file():
                raise SystemExit(f"missing {path}")
            media |= bit
        if media & 1:
            raise SystemExit(f"{entry_id} gained an illustration bit unexpectedly")
        entry["m"] = media
        pos = next(i for i, row in enumerate(index["words"]) if row[0] == entry_id)
        changed.add(pos // chunk)
    for row in index["words"]:
        row[6] = by_id[row[0]]["m"]
        if row[0] not in idset and row[6] != before[row[0]]:
            raise SystemExit(f"media bit changed outside batch 14 gaps: {row[0]}")
    for n in sorted(changed):
        block = entries[n * chunk:(n + 1) * chunk]
        (PUB / "entries" / f"{n}.json").write_bytes(
            json.dumps(block, ensure_ascii=False, separators=(",", ":")).encode()
        )
    index["illustrated"] = sum(1 for row in index["words"] if row[6] & 1)
    index["voiced"] = sum(1 for row in index["words"] if row[6] & 2)
    (PUB / "index.json").write_bytes(json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode())


def main() -> None:
    require_models()
    protected = {
        str(path.relative_to(ROOT)): sha256_file(path)
        for path in (SENTENCE_PROVENANCE, OLD_HEADWORD_PROVENANCE, SPLASH)
    }
    index = load_index()
    entries = load_entries(index)
    entries_by_id = {entry["id"]: entry for entry in entries}
    ids = targets(entries_by_id)
    records = synthesize(ids, entries_by_id)
    update_catalog(ids, entries, index)
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    for row in audit:
        if row["id"] in ids:
            row["missingUk"] = False
            row["missingUs"] = False
            row["headwordAudio"] = "kokoro"
        else:
            row["headwordAudio"] = "upstream"
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    provenance = {
        "source": (
            "Batch 14 headword clips for the 32 new cards that had no upstream "
            "Word Atlas uk/us file. Kokoro speaks the isolated headword at speed 1.0. "
            "US voice af_heart, language en-us. UK voice bf_emma, language en-gb. "
            "Example clips, splash audio, the earlier 59-word headword provenance, "
            "and already-complete cards were not rewritten. Illustrations were not generated."
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
        "counts": {"words": len(ids), "clips": len(records), "illustrationsStillMissing": len(ids)},
        "ids": ids,
        "clips": records,
    }
    PROVENANCE_PATH.write_text(json.dumps(provenance, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for rel, digest in protected.items():
        if sha256_file(ROOT / rel) != digest:
            raise SystemExit(f"protected file changed: {rel}")
    index = load_index()
    print(json.dumps({
        "clips": len(records),
        "voiced": index["voiced"],
        "illustrated": index["illustrated"],
        "count": index["count"],
    }))


if __name__ == "__main__":
    sys.exit(main())
