#!/usr/bin/env python3
"""Fill UK/US headword audio for the 59 batch-12/13 cards that only have examples.

US clips use local Kokoro, voice af_heart, language en-us, speed 1.0.
UK clips use local Kokoro, voice bf_emma, language en-gb, speed 1.0.
Each clip speaks the isolated headword. No paid API and no API key.

Five American spellings reuse unused upstream Word Atlas files of the
same word's British spelling (illustration, thumbnail, UK audio, US audio).
Those bytes are copied. The upstream files stay where they are.

This script does not read or write example audio, splash audio, or any
card that already has a headword clip or an illustration bit.

Run
---
.. code-block:: bash

    .local/kokoro-venv/bin/python scripts/atlas/gen_kokoro_headword_audio.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
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

# Chosen among the four female British voices in voices-v1.0.bin
# (bf_alice, bf_emma, bf_isabella, bf_lily). A local faster-whisper
# base.en pass on 30 isolated headwords scored emma 25, isabella 24,
# alice 21, lily 19. Emma had no multi-syllable miss in that set.
UK_VOICE_REASON = (
    "bf_emma scored highest among bf_alice, bf_emma, bf_isabella and bf_lily "
    "on a local faster-whisper base.en check of 30 isolated headwords "
    "(25, 24, 21 and 19). Emma had no multi-syllable miss in that set."
)

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "public" / "atlas"
MODEL_PATH = ROOT / ".local" / "kokoro" / "models" / "kokoro-v1.0.onnx"
VOICES_PATH = ROOT / ".local" / "kokoro" / "models" / "voices-v1.0.bin"
STAGING = ROOT / ".local" / "kokoro" / "headword-staging"
PROVENANCE_PATH = ROOT / "data" / "headword-audio-provenance.json"
DATA_PATH = ROOT / "data" / "word-atlas.json"
SENTENCE_PROVENANCE = ROOT / "data" / "sentence-audio-provenance.json"
SPLASH = ROOT / "public" / "sfx" / "splash-voice.mp3"

# Catalog ids. All 59 are a single token; none are hyphenated.
TARGETS = [
    "belly", "booth", "facial", "import", "meter", "coke", "merchant", "adjust",
    "flame", "inn", "nationwide", "scan", "fiber", "pulse", "beg", "graph",
    "strengthen", "transform", "passive", "deliberately", "sympathy", "theoretical",
    "dash", "bent", "aboard", "acknowledge", "ash", "athletic", "bare", "barrier",
    "bored", "boxing", "burst", "cheers", "corrupt", "disability", "distant",
    "examine", "grandma", "gravity", "harbor", "humor", "lap", "leaf", "lightning",
    "marathon", "missile", "neighbor", "ours", "patience", "pension", "phenomenon",
    "precise", "separation", "spray", "theft", "unemployment", "widespread", "zoo",
]

# Same word, British spelling, not used by any catalog id.
REUSE = {
    "meter": "metre",
    "fiber": "fibre",
    "harbor": "harbour",
    "humor": "humour",
    "neighbor": "neighbour",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_models() -> None:
    for path, expected in ((MODEL_PATH, MODEL_SHA), (VOICES_PATH, VOICES_SHA)):
        if not path.is_file():
            raise SystemExit(f"Missing {path}. See scripts/atlas/gen_kokoro_sentence_audio.py.")
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"Refusing {path.name}: sha256 {actual} != pinned {expected}")


def webp_size(path: Path) -> tuple[int, int, str]:
    data = path.read_bytes()
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise SystemExit(f"{path} is not a WebP")
    chunk = data[12:16]
    if chunk != b"VP8 ":
        raise SystemExit(f"{path} is {chunk!r}, expected lossy VP8")
    payload = data[20:]
    marker = payload.find(b"\x9d\x01\x2a")
    if marker < 0:
        raise SystemExit(f"{path} has no VP8 start code")
    width = int.from_bytes(payload[marker + 3 : marker + 5], "little") & 0x3FFF
    height = int.from_bytes(payload[marker + 5 : marker + 7], "little") & 0x3FFF
    return width, height, "VP8"


def load_index() -> dict:
    return json.loads((PUB / "index.json").read_text(encoding="utf-8"))


def load_entries(index: dict) -> list[dict]:
    entries = []
    chunk = index["chunk"]
    for n in range((index["count"] + chunk - 1) // chunk):
        block = json.loads((PUB / "entries" / f"{n}.json").read_text(encoding="utf-8"))
        entries.extend(block)
    if len(entries) != index["count"]:
        raise SystemExit(f"entry count {len(entries)} != index {index['count']}")
    for row, entry in zip(index["words"], entries):
        if row[0] != entry["id"] or row[6] != entry["m"]:
            raise SystemExit(f"index/entry drift at {entry['id']}")
    return entries


def protected_hashes(entries_by_id: dict[str, dict]) -> dict[str, str]:
    paths = [
        SENTENCE_PROVENANCE,
        SPLASH,
        PUB / "audio" / "uk" / "abandon.mp3",
        PUB / "audio" / "us" / "abandon.mp3",
        PUB / "img" / "abandon.webp",
        PUB / "audio" / "ex" / "abandon.mp3",
    ]
    for entry_id in TARGETS:
        paths.append(PUB / "audio" / "ex" / f"{entry_id}.mp3")
        paths.append(PUB / "audio" / "ex2" / f"{entry_id}.mp3")
    for source in REUSE.values():
        paths.append(PUB / "img" / f"{source}.webp")
        paths.append(PUB / "thumb" / f"{source}.webp")
        paths.append(PUB / "audio" / "uk" / f"{source}.mp3")
        paths.append(PUB / "audio" / "us" / f"{source}.mp3")
    hashes = {}
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"protected file missing before the run: {path}")
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    # Example clips must already be flagged. Headword and image bits must be off.
    for entry_id in TARGETS:
        entry = entries_by_id[entry_id]
        if entry["m"] != 24:
            raise SystemExit(f"{entry_id} media bit is {entry['m']}, expected 24 (examples only)")
        if any((PUB / folder / f"{entry_id}.mp3").exists() for folder in ("audio/uk", "audio/us")):
            raise SystemExit(f"{entry_id} already has a headword mp3")
        if (PUB / "img" / f"{entry_id}.webp").exists() or (PUB / "thumb" / f"{entry_id}.webp").exists():
            raise SystemExit(f"{entry_id} already has an illustration")
    return hashes


def assert_unchanged(before: dict[str, str]) -> None:
    for rel, digest in before.items():
        path = ROOT / rel
        if sha256_file(path) != digest:
            raise SystemExit(f"protected file changed: {rel}")


def copy_exact(src: Path, dst: Path) -> None:
    if dst.exists():
        raise SystemExit(f"refusing to overwrite {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    partial = dst.with_name(dst.name + ".partial")
    partial.write_bytes(src.read_bytes())
    partial.replace(dst)
    if sha256_file(dst) != sha256_file(src):
        raise SystemExit(f"copy mismatch {src} -> {dst}")


def reuse_upstream() -> list[dict]:
    index_ids = {row[0] for row in load_index()["words"]}
    records = []
    for entry_id, source in REUSE.items():
        if source in index_ids:
            raise SystemExit(f"refusing to reuse {source}: it is an in-catalog id")
        img = PUB / "img" / f"{source}.webp"
        thumb = PUB / "thumb" / f"{source}.webp"
        uk = PUB / "audio" / "uk" / f"{source}.mp3"
        us = PUB / "audio" / "us" / f"{source}.mp3"
        for path in (img, thumb, uk, us):
            if not path.is_file():
                raise SystemExit(f"upstream source missing: {path}")
        iw, ih, _ = webp_size(img)
        tw, th, _ = webp_size(thumb)
        if (iw, ih) != (512, 512) or (tw, th) != (256, 256):
            raise SystemExit(f"{source} plate is {iw}x{ih} / {tw}x{th}, expected 512 and 256")
        copy_exact(img, PUB / "img" / f"{entry_id}.webp")
        copy_exact(thumb, PUB / "thumb" / f"{entry_id}.webp")
        copy_exact(uk, PUB / "audio" / "uk" / f"{entry_id}.mp3")
        copy_exact(us, PUB / "audio" / "us" / f"{entry_id}.mp3")
        records.append(
            {
                "id": entry_id,
                "upstreamId": source,
                "reason": "Same headword, British spelling. Unused by every catalog id. Bytes copied; originals kept.",
                "img": file_record(PUB / "img" / f"{entry_id}.webp"),
                "thumb": file_record(PUB / "thumb" / f"{entry_id}.webp"),
                "uk": file_record(PUB / "audio" / "uk" / f"{entry_id}.mp3"),
                "us": file_record(PUB / "audio" / "us" / f"{entry_id}.mp3"),
            }
        )
        print(f"reused {source} -> {entry_id}", flush=True)
    return records


def file_record(path: Path) -> dict:
    return {
        "file": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


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
    if not (0.30 <= duration <= 3.5):
        raise RuntimeError(f"duration {duration:.3f}s outside 0.30–3.5s")


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
        wav_duration = padded.size / sample_rate
        if abs(duration - wav_duration) > 0.3:
            raise RuntimeError(f"mp3 duration {duration:.3f}s vs wav {wav_duration:.3f}s")
        partial.replace(dest)
        return duration
    finally:
        if partial.exists():
            partial.unlink()


def synthesize_headwords(entries_by_id: dict[str, dict]) -> list[dict]:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(str(MODEL_PATH), str(VOICES_PATH))
    for voice in (UK_VOICE, US_VOICE):
        if voice not in kokoro.voices:
            raise SystemExit(f"voice {voice} missing from voices file")
    if not kokoro.has_timings:
        raise SystemExit("model does not report phoneme durations")

    jobs = []
    for entry_id in TARGETS:
        if entry_id in REUSE:
            continue
        word = entries_by_id[entry_id]["w"]
        if word.lower() != entry_id or " " in word:
            raise SystemExit(f"refusing unexpected headword {entry_id!r} / {word!r}")
        jobs.append((entry_id, word))

    records = []
    total = len(jobs) * 2
    done = 0
    for entry_id, word in jobs:
        for accent, voice, lang, folder in (
            ("uk", UK_VOICE, UK_LANG, "uk"),
            ("us", US_VOICE, US_LANG, "us"),
        ):
            errors = []
            audio = spoken = known = None
            sample_rate = 0
            for trim in (True, False):
                try:
                    audio, sample_rate, spoken = kokoro.create_timed(
                        word, voice=voice, speed=SPEED, lang=lang, trim=trim
                    )
                    phonemes = kokoro.tokenizer.phonemize(word, lang)
                    known = kokoro.tokenizer.known(phonemes)
                    qc_audio(audio, sample_rate, spoken, known)
                    break
                except Exception as exc:
                    errors.append(f"{'trim' if trim else 'no-trim'}: {exc}")
                    audio = None
            if audio is None:
                raise SystemExit(f"FAIL {entry_id} {accent}: {'; '.join(errors)}")
            dest = STAGING / folder / f"{entry_id}.mp3"
            duration = encode_mp3(audio, sample_rate, dest)
            records.append(
                {
                    "id": entry_id,
                    "accent": accent,
                    "voice": voice,
                    "lang": lang,
                    "speed": SPEED,
                    "script": word,
                    "phonemes": known,
                    "duration": round(duration, 3),
                    "trim": True if not any(item.startswith("trim:") for item in errors) else False,
                    "origin": "kokoro",
                    **file_record(dest),
                }
            )
            done += 1
            if done % 20 == 0 or done == total:
                print(f"synthesized {done}/{total}", flush=True)
    return records


def publish_kokoro(records: list[dict]) -> list[dict]:
    published = []
    for record in records:
        src = ROOT / record["file"]
        dest = PUB / "audio" / record["accent"] / f"{record['id']}.mp3"
        copy_exact(src, dest)
        item = dict(record)
        item.update(file_record(dest))
        item["file"] = str(dest.relative_to(ROOT))
        published.append(item)
    return published


def update_catalog(entries: list[dict], index: dict) -> None:
    by_id = {entry["id"]: entry for entry in entries}
    bits_before = {row[0]: row[6] for row in index["words"]}
    changed_chunks = set()
    chunk = index["chunk"]
    for entry_id in TARGETS:
        entry = by_id[entry_id]
        media = entry["m"]
        if entry_id in REUSE:
            if not (PUB / "img" / f"{entry_id}.webp").is_file() or not (PUB / "thumb" / f"{entry_id}.webp").is_file():
                raise SystemExit(f"illustration missing for reused {entry_id}")
            media |= 1
        else:
            if (PUB / "img" / f"{entry_id}.webp").exists() or (PUB / "thumb" / f"{entry_id}.webp").exists():
                raise SystemExit(f"unexpected illustration appeared for {entry_id}")
        for bit, folder in ((2, "uk"), (4, "us")):
            if not (PUB / "audio" / folder / f"{entry_id}.mp3").is_file():
                raise SystemExit(f"missing published {folder} audio for {entry_id}")
            media |= bit
        if entry_id in REUSE and media != 31:
            raise SystemExit(f"{entry_id} media {media}, expected 31")
        if entry_id not in REUSE and media != 30:
            raise SystemExit(f"{entry_id} media {media}, expected 30")
        entry["m"] = media
        changed_chunks.add(index["words"].index(next(row for row in index["words"] if row[0] == entry_id)) // chunk)

    for n, row in enumerate(index["words"]):
        row[6] = by_id[row[0]]["m"]
        if row[0] not in TARGETS and row[6] != bits_before[row[0]]:
            raise SystemExit(f"media bit changed on an out-of-scope card: {row[0]}")
    for n in sorted(changed_chunks):
        block = entries[n * chunk : (n + 1) * chunk]
        path = PUB / "entries" / f"{n}.json"
        path.write_bytes(json.dumps(block, ensure_ascii=False, separators=(",", ":")).encode())
    index["illustrated"] = sum(1 for row in index["words"] if row[6] & 1)
    index["voiced"] = sum(1 for row in index["words"] if row[6] & 2)
    (PUB / "index.json").write_bytes(json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode())

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    seen = set()
    for entry in data:
        if entry["id"] in REUSE:
            entry.setdefault("meta", {})["mediaReuseCandidate"] = True
            seen.add(entry["id"])
    if seen != set(REUSE):
        raise SystemExit(f"mediaReuseCandidate update missed {set(REUSE) - seen}")
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(
        json.dumps({"illustrated": index["illustrated"], "voiced": index["voiced"], "count": index["count"]}),
        flush=True,
    )


def write_provenance(reused: list[dict], clips: list[dict]) -> None:
    kokoro_uk = [row for row in clips if row["accent"] == "uk"]
    kokoro_us = [row for row in clips if row["accent"] == "us"]
    if len(kokoro_uk) != 54 or len(kokoro_us) != 54 or len(reused) != 5:
        raise SystemExit(f"unexpected counts reuse={len(reused)} uk={len(kokoro_uk)} us={len(kokoro_us)}")
    payload = {
        "source": (
            "Headword clips for 59 batch-12 and batch-13 cards that previously had only example audio. "
            "Kokoro clips speak the isolated headword (not a sentence) at speed 1.0. "
            f"US voice {US_VOICE}, language {US_LANG}. UK voice {UK_VOICE}, language {UK_LANG}. "
            "Five American spellings reuse unused upstream Word Atlas media of the British spelling; "
            "those files were copied and the originals were left in place. "
            "Example clips, splash audio, and already-complete cards were not rewritten. "
            + UK_VOICE_REASON
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
            "encoding": "mp3 mono 44100 Hz 64 kbps",
            "tailPadSec": TAIL_PAD_SEC,
            "uk": {"voice": UK_VOICE, "lang": UK_LANG, "speed": SPEED, "script": "isolated headword"},
            "us": {"voice": US_VOICE, "lang": US_LANG, "speed": SPEED, "script": "isolated headword"},
            "ukVoiceReason": UK_VOICE_REASON,
        },
        "counts": {
            "targets": len(TARGETS),
            "kokoroUk": len(kokoro_uk),
            "kokoroUs": len(kokoro_us),
            "reusedUpstreamWords": len(reused),
            "illustrationsAdded": len(reused),
            "illustrationsStillMissing": len(TARGETS) - len(reused),
        },
        "reusedUpstream": reused,
        "clips": sorted(clips, key=lambda row: (row["id"], row["accent"])),
    }
    PROVENANCE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    require_models()
    if set(REUSE) - set(TARGETS):
        raise SystemExit("reuse ids are not all in the target list")
    index = load_index()
    if index["count"] != 2597 or index["illustrated"] != 2383 or index["voiced"] != 2376:
        raise SystemExit(
            f"refusing to start from illustrated={index.get('illustrated')} voiced={index.get('voiced')} count={index.get('count')}"
        )
    entries = load_entries(index)
    by_id = {entry["id"]: entry for entry in entries}
    missing = [entry_id for entry_id in TARGETS if entry_id not in by_id]
    if missing:
        raise SystemExit(f"ids not in the catalog: {missing}")
    before = protected_hashes(by_id)
    if STAGING.exists():
        shutil.rmtree(STAGING)
    clips = synthesize_headwords(by_id)
    published = publish_kokoro(clips)
    reused = reuse_upstream()
    assert_unchanged(before)
    update_catalog(entries, index)
    assert_unchanged(before)
    write_provenance(reused, published)
    # A second load proves the bits just written still match the files.
    index = load_index()
    entries = load_entries(index)
    by_id = {entry["id"]: entry for entry in entries}
    for entry_id in TARGETS:
        expect = 31 if entry_id in REUSE else 30
        if by_id[entry_id]["m"] != expect:
            raise SystemExit(f"post-check {entry_id} media {by_id[entry_id]['m']} != {expect}")
    if index["illustrated"] != 2388 or index["voiced"] != 2435:
        raise SystemExit(f"unexpected counts illustrated={index['illustrated']} voiced={index['voiced']}")
    print("headword fill ok", flush=True)


if __name__ == "__main__":
    main()
