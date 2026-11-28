#!/usr/bin/env python3
"""Select Batch 15 outline headwords after referee.

Frequency is wordfreq 3.1.1 zipf_frequency(word, "en"). Hyphenated or
multi-word headwords also try the spaced or hyphenated twin, and the higher
Zipf wins. Sort key is Zipf rounded to two decimals, then id alphabetical.
CEFR-J Wordlist 1.6 ALL_sep tags are stored for the later same-POS decision.
The script does not invent headwords and does not write catalog cards.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import openpyxl
from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parents[1]
OUTLINE = Path(
    "/home/ubuntu/.cursor/projects/agent-repos-word-atlas-gaokao/uploads/gaokao-outline-3500_398a.txt"
)
CEFRJ_XLSX = Path("/tmp/cefrj/wordlist.xlsx")
BATCH14 = ROOT / "data" / "batch-14-selection.json"
INDEX = ROOT / "public" / "atlas" / "index.json"
OUT = ROOT / "data" / "batch-15-selection.json"
WINDOW = ROOT / "data" / "batch-15-window.json"
TARGET = 200
HEADER_RE = re.compile(r"#[A-Z]")


def make_id(word: str) -> str:
    text = word.strip().lower().replace("é", "e").replace("'", "-").replace(".", "-").replace(" ", "-")
    text = re.sub(r"-+", "-", text).strip("-")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", text):
        raise SystemExit(f"unsafe id for {word!r}: {text!r}")
    return text


def zipf_lookup(word: str) -> tuple[float, float, str]:
    forms = [word.lower()]
    if "-" in word:
        forms.append(word.lower().replace("-", " "))
    if " " in word:
        forms.append(word.lower().replace(" ", "-"))
    best_z = None
    best_via = None
    raw_self = zipf_frequency(word.lower(), "en")
    for form in forms:
        score = zipf_frequency(form, "en")
        if best_z is None or score > best_z:
            best_z = score
            best_via = form
    assert best_z is not None and best_via is not None
    # wordfreq 3.1.1 already emits hundredths. Snap only a binary-float wobble.
    return round(best_z + 1e-9, 2), raw_self, best_via


def load_outline() -> list[dict]:
    lines = OUTLINE.read_text(encoding="utf-8").splitlines()
    headers = 0
    seen: set[str] = set()
    rows = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if HEADER_RE.fullmatch(text):
            headers += 1
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append({"w": text, "id": make_id(text)})
    if headers != 26:
        raise SystemExit(f"expected 26 letter headers, found {headers}")
    if len(rows) != 3487:
        raise SystemExit(f"expected 3487 unique headwords, found {len(rows)}")
    # "No." and "no" both tidy to id no. No. is a high-Zipf abbreviation, far above
    # this window, and the catalog already has the determiner no. Leave both rows
    # in the outline so the sort stays complete, and refuse the collision only if
    # a later batch actually tries to publish the abbreviation.
    return rows


def load_catalog() -> tuple[set[str], set[str]]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    words = {row[1].lower() for row in index["words"]}
    ids = {row[0] for row in index["words"]}
    if len(index["words"]) != 2797:
        raise SystemExit(f"catalog is {len(index['words'])}, expected 2797 at the Batch 14 merge")
    return words, ids


def load_cefrj() -> dict[str, list[dict]]:
    book = openpyxl.load_workbook(CEFRJ_XLSX, read_only=True, data_only=True)
    sheet = book["ALL_sep"]
    tags: dict[str, list[dict]] = {}
    seen = set()
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        if i == 0:
            if row[:3] != ("headword", "pos", "CEFR"):
                raise SystemExit(f"unexpected ALL_sep header {row}")
            continue
        head, pos, level = row[0], row[1], row[2]
        if not head or not pos or not level:
            continue
        key = str(head).strip().lower()
        item = {"pos": str(pos).strip(), "cefr": str(level).strip(), "headword": str(head).strip()}
        marker = (key, item["pos"], item["cefr"])
        if marker in seen:
            continue
        seen.add(marker)
        tags.setdefault(key, []).append(item)
    book.close()
    return tags


def attach(rows: list[dict], cefrj: dict[str, list[dict]]) -> None:
    for row in rows:
        z, raw, via = zipf_lookup(row["w"])
        row["zipf"] = z
        row["zipfRaw"] = raw
        row["zipfVia"] = via
        keys = [row["w"].lower()]
        via_note = None
        if "-" in row["w"] or " " in row["w"]:
            twin = row["w"].lower().replace("-", " ") if "-" in row["w"] else row["w"].lower().replace(" ", "-")
            if twin not in keys:
                keys.append(twin)
        found = []
        for key in keys:
            hit = cefrj.get(key) or []
            if hit and key != row["w"].lower():
                via_note = key
            found.extend(hit)
        # De-dupe after a spacing twin adds the same tag twice.
        uniq = []
        seen = set()
        for item in found:
            marker = (item["pos"], item["cefr"], item["headword"].lower())
            if marker in seen:
                continue
            seen.add(marker)
            uniq.append(item)
        row["cefrj"] = uniq
        row["cefrj_via"] = via_note


def in_catalog(row: dict, words: set[str], ids: set[str]) -> bool:
    # Match the headword, not a tidy id that a different headword already uses.
    del ids
    return row["w"].lower() in words


def main() -> None:
    outline = load_outline()
    words, ids = load_catalog()
    attach(outline, load_cefrj())
    outline.sort(key=lambda row: (-row["zipf"], row["id"]))

    batch14 = json.loads(BATCH14.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in outline}
    referee = by_id["referee"]
    if referee["zipf"] != 3.86:
        raise SystemExit(f"referee Zipf {referee['zipf']} != 3.86")
    ref_i = outline.index(referee)
    start14 = outline.index(by_id["bicycle"])
    slice14 = outline[start14 : ref_i + 1]
    expected = [item["id"] for item in batch14]
    batch14_ids = set(expected)
    window14_ids = [row["id"] for row in slice14 if row["id"] in batch14_ids]
    skips14 = [row["id"] for row in slice14 if row["id"] not in batch14_ids]
    if window14_ids != expected:
        raise SystemExit(
            "Batch 14 order was not reproduced: "
            f"missing {[i for i in expected if i not in window14_ids][:8]} "
            f"extra {[i for i in window14_ids if i not in expected][:8]}"
        )
    if skips14 != ["admire", "conclude", "calculate", "distinguish"]:
        raise SystemExit(f"Batch 14 skips changed: {skips14}")
    # Zipf stored on the Batch 14 rows must match this pass, or the sort drifted.
    for old in batch14:
        if by_id[old["id"]]["zipf"] != old["zipf"]:
            raise SystemExit(f"Zipf drift {old['id']}: {by_id[old['id']]['zipf']} != {old['zipf']}")

    after = outline[ref_i + 1 :]
    chosen = []
    skipped = []
    last_index = None
    for offset, row in enumerate(after):
        if in_catalog(row, words, ids):
            if len(chosen) < TARGET:
                skipped.append(row)
            continue
        if len(chosen) >= TARGET:
            continue
        chosen.append(row)
        last_index = ref_i + 1 + offset
    if len(chosen) != TARGET or last_index is None:
        raise SystemExit(f"only found {len(chosen)} new headwords")
    chosen_ids = [row["id"] for row in chosen]
    if len(chosen_ids) != len(set(chosen_ids)):
        raise SystemExit(f"selected id collision: {chosen_ids}")
    overlap = sorted(set(chosen_ids) & ids)
    if overlap:
        raise SystemExit(f"selected id already catalogued under another headword: {overlap}")

    # In-window skips are catalog hits from the first chosen word through the last.
    first = chosen[0]
    last = chosen[-1]
    first_i = outline.index(first)
    in_window_skips = []
    for row in outline[first_i : last_index + 1]:
        if in_catalog(row, words, ids):
            in_window_skips.append({"id": row["id"], "w": row["w"], "zipf": row["zipf"]})

    leftovers = []
    for row in outline[last_index + 1 :]:
        if row["zipf"] != last["zipf"]:
            break
        if not in_catalog(row, words, ids):
            leftovers.append({"id": row["id"], "w": row["w"], "zipf": row["zipf"]})
    next_new = None
    for row in outline[last_index + 1 :]:
        if not in_catalog(row, words, ids):
            next_new = {"id": row["id"], "w": row["w"], "zipf": row["zipf"]}
            break

    pub = ROOT / "public" / "atlas"
    media = []
    for row in chosen:
        entry_id = row["id"]
        flags = {
            "id": entry_id,
            "img": (pub / "img" / f"{entry_id}.webp").is_file() and (pub / "thumb" / f"{entry_id}.webp").is_file(),
            "imgOnly": (pub / "img" / f"{entry_id}.webp").is_file(),
            "thumbOnly": (pub / "thumb" / f"{entry_id}.webp").is_file(),
            "uk": (pub / "audio" / "uk" / f"{entry_id}.mp3").is_file(),
            "us": (pub / "audio" / "us" / f"{entry_id}.mp3").is_file(),
            "ex": (pub / "audio" / "ex" / f"{entry_id}.mp3").is_file(),
            "ex2": (pub / "audio" / "ex2" / f"{entry_id}.mp3").is_file(),
        }
        media.append(flags)

    selection = []
    for row in chosen:
        selection.append(
            {
                "id": row["id"],
                "w": row["w"],
                "zipf": row["zipf"],
                "zipfRaw": row["zipfRaw"],
                "zipfVia": row["zipfVia"],
                "cefrj": row["cefrj"],
                "cefrj_via": row["cefrj_via"],
            }
        )
    OUT.write_text(json.dumps(selection, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    report = {
        "outlineLinesWc": 3530,
        "uniqueHeadwords": 3487,
        "catalogBefore": 2797,
        "target": TARGET,
        "first": {"id": first["id"], "w": first["w"], "zipf": first["zipf"]},
        "last": {"id": last["id"], "w": last["w"], "zipf": last["zipf"]},
        "zipfCounts": dict(sorted(Counter(row["zipf"] for row in chosen).items(), reverse=True)),
        "inWindowSkips": in_window_skips,
        "leftoversSameZipf": leftovers,
        "nextNewHeadword": next_new,
        "startsWithExpectedTies": [row["id"] for row in chosen[:4]],
        "media": {
            "plate": sum(1 for item in media if item["img"]),
            "missingPlate": [item["id"] for item in media if not item["img"]],
            "uk": sum(1 for item in media if item["uk"]),
            "us": sum(1 for item in media if item["us"]),
            "missingUk": [item["id"] for item in media if not item["uk"]],
            "missingUs": [item["id"] for item in media if not item["us"]],
            "unusedEx": sum(1 for item in media if item["ex"]),
            "unusedEx2": sum(1 for item in media if item["ex2"]),
            "partialPlate": [item["id"] for item in media if item["imgOnly"] != item["thumbOnly"]],
        },
        "zipfViaNotSelf": [
            {"id": row["id"], "zipf": row["zipf"], "zipfRaw": row["zipfRaw"], "zipfVia": row["zipfVia"]}
            for row in chosen
            if row["zipfVia"] != row["w"].lower()
        ],
        "cefrjVia": [row["id"] for row in chosen if row["cefrj_via"]],
        "batch14Check": "bicycle→referee reproduced; skips admire, calculate, conclude, distinguish",
    }
    WINDOW.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("first", "last", "startsWithExpectedTies", "inWindowSkips", "leftoversSameZipf", "nextNewHeadword", "media", "zipfViaNotSelf")}, ensure_ascii=False, indent=1))
    print("---WORDS---")
    for row in chosen:
        print(f"{row['zipf']:.2f}\t{row['id']}\t{row['w']}")


if __name__ == "__main__":
    main()
