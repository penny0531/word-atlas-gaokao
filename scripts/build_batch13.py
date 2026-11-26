#!/usr/bin/env python3
"""Assemble batch 13 cards, assign CEFR and IPA, and publish the atlas files.

Review only:  python3 scripts/build_batch13.py
Publish:      python3 scripts/build_batch13.py --write
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNOT = Path("/tmp/batch13-annot.json")
CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"]
# Medians of wordfreq Zipf for CEFR-J Wordlist v1.6 headwords (sheet ALL_sep),
# rounded to 2 decimals. See data/batch-13-notes.md.
ZIPF_B1 = 4.18
ZIPF_B2 = 3.74
POS_TO_CEFRJ = {"n.": "noun", "v.": "verb", "adj.": "adjective", "adv.": "adverb", "prep.": "preposition"}
FORCE_ESPEAK_UK = {
    "shout", "slice", "possess", "uncertain", "booth", "fridge",
    "widow", "grocery", "tablet", "airline", "donate", "warn",
}
IRREGULAR_ROWS = (
    "arise arose arisen|awake awoke awoken|bear bore borne born|beat beat beaten|become became|begin began begun beginn|"
    "bend bent|bet bet|bind bound|bite bit bitten|bleed bled|blow blew blown|break broke broken|breed bred|bring brought|"
    "broadcast broadcast|build built|burn burnt burned|burst burst|buy bought|catch caught|choose chose chosen|"
    "cling clung|come came|cost cost|creep crept|cut cut cutt|deal dealt|dig dug|do did done does|draw drew drawn|"
    "dream dreamt dreamed|drink drank drunk|drive drove driven|eat ate eaten|fall fell fallen|feed fed|feel felt|"
    "fight fought|find found|flee fled|fling flung|fly flew flown flies|forbid forbade forbidden|forget forgot forgotten|"
    "forgive forgave forgiven|freeze froze frozen|get got gotten gett|give gave given|go went gone goes|grind ground|"
    "grow grew grown|hang hung|have had has|hear heard|hide hid hidden|hit hit hitt|hold held|hurt hurt|keep kept|"
    "kneel knelt|know knew known|lay laid|lead led|lean leant leaned|leap leapt leaped|learn learnt learned|"
    "leave left|lend lent|let let|lie lay lain|light lit|lose lost|make made|mean meant|meet met|pay paid|"
    "prove proved proven|put put putt|quit quit|read read|ride rode ridden|ring rang rung|rise rose risen|"
    "run ran runn|say said|see saw seen|seek sought|sell sold|send sent|set set|sew sewed sewn|shake shook shaken|"
    "shed shed|shine shone|shoot shot|show showed shown|shrink shrank shrunk|shut shut|sing sang sung|sink sank sunk|"
    "sit sat sitt|sleep slept|slide slid|sling slung|speak spoke spoken|speed sped|spend spent|spill spilt spilled|"
    "spin spun spinn|spy spied spies|mislead misled|spit spat|split split|spread spread|spring sprang sprung|"
    "stand stood|steal stole stolen|stick stuck|sting stung|stink stank stunk|stride strode|strike struck|"
    "string strung|strive strove striven|swear swore sworn|sweep swept|swell swelled swollen|swim swam swum swimm|"
    "swing swung|take took taken|teach taught|tear tore torn|tell told|think thought|throw threw thrown|"
    "tread trod trodden|understand understood|undertake undertook undertaken|upset upset|wake woke woken|"
    "wear wore worn|weave wove woven|weep wept|win won winn|wind wound|withdraw withdrew withdrawn|write wrote written|"
    "be was were been is are am|child children|man men|woman women|foot feet|tooth teeth|mouse mice|"
    "person people|good better best|bad worse worst|far further farther furthest"
)
IRREGULAR = {}
for row in IRREGULAR_ROWS.split("|"):
    parts = row.split(" ")
    IRREGULAR[parts[0]] = parts[1:]


def load_py(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def zipf_band(z: float) -> str:
    if z >= 6.4:
        return "A1"
    if z >= 5.9:
        return "A2"
    if z >= ZIPF_B1:
        return "B1"
    if z >= ZIPF_B2:
        return "B2"
    return "C1"


def phon_key(ipa: str) -> str:
    ipa = ipa.lower()
    ipa = re.sub(r"\(us\).*", "", ipa, flags=re.I)
    ipa = ipa.replace("ɹ", "r").replace("ɾ", "t").replace("ɐ", "ə").replace("ᵻ", "ɪ")
    ipa = ipa.replace("g", "ɡ")
    ipa = re.sub(r"[ˈˌ'\/\s\.\,\(\)\[\]\-ː:]", "", ipa)
    return ipa


def lev(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a or not b:
        return max(len(a), len(b))
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def sim(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 1 - lev(a, b) / max(len(a), len(b))


def clean_ipa(raw: str) -> str:
    s = raw.strip()
    s = s.replace("’", "'").replace("'", "ˈ")
    s = s.strip().strip("/")
    s = s.replace(" ", "")
    s = s.replace("ɡ", "ɡ").replace("g", "ɡ")
    return f"/{s}/"


def slash_espeak(ipa: str) -> str:
    s = ipa.replace("ʔ", "").replace("n̩", "ən").replace("m̩", "əm").replace("l̩", "əl")
    s = s.replace("ɚ", "ər").replace("ɝ", "ɜːr")
    return clean_ipa(s)


def headword_pattern(word: str) -> re.Pattern:
    w = word.strip().lower()

    def esc(s: str) -> str:
        return re.escape(s)

    if re.search(r"\s", w):
        body = r"\s+".join(esc(p) for p in w.split())
        return re.compile(rf"(?<![A-Za-z])({body})(?![A-Za-z])", re.I)
    irregular = IRREGULAR.get(w)
    if irregular:
        alt = "|".join(esc(x) for x in [w, *irregular])
        return re.compile(rf"(?<![A-Za-z])((?:{alt})[a-z]{{0,3}})(?![A-Za-z])", re.I)
    stem = w
    if len(w) > 3 and re.search(r"[^aeiou]y$|e$", w):
        stem = w[:-1]
    double = esc(w[-1]) + "?" if re.search(r"[^aeiou][aeiou][bdgmnprt]$", w) else ""
    return re.compile(rf"(?<![A-Za-z])({esc(stem)}{double}[a-z]{{0,4}})(?![A-Za-z])", re.I)


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def exact_or_inflected(word: str, sentence: str) -> bool:
    w = word.lower()
    found = set(tokens(sentence))
    if w in found:
        return True
    extras = IRREGULAR.get(w, [])
    if any(form in found for form in extras):
        return True
    # light inflection of the written headword, still the same word
    for tok in found:
        if tok.startswith(w) and tok[len(w):] in {"s", "es", "ed", "d", "ing", "er", "est", "ly"}:
            return True
    return False


def choose_cefr(card: dict, row: dict) -> dict:
    band = zipf_band(row["zipf_raw"])
    tags = row.get("cefrj") or []
    primary = card["senses"][0]["pos"]
    want = POS_TO_CEFRJ.get(primary)
    same = sorted({t["cefr"] for t in tags if t["pos"] == want}) if want else []
    other = sorted({(t["pos"], t["cefr"]) for t in tags if t["pos"] != want})
    if len(same) == 1:
        level = same[0]
        how = "cefr-j-same-pos"
    elif len(same) > 1:
        level = same[0]
        how = "cefr-j-same-pos-first"
    else:
        level = band
        how = "zipf-band"
    return {
        "id": row["id"],
        "w": row["w"],
        "zipf": row["zipf"],
        "pos": primary,
        "zipfBand": band,
        "published": [{"pos": t["pos"], "cefr": t["cefr"], "headword": t["hw"]} for t in tags],
        "publishedVia": row.get("cefrj_via"),
        "samePosLevels": same,
        "otherPos": [{"pos": p, "cefr": c} for p, c in other],
        "cefr": level,
        "decision": how,
        "differ": bool(tags) and level != band,
    }


def choose_ipa(row: dict) -> dict:
    wid = row["id"]
    gb = slash_espeak(row["espeak_gb"])
    us = slash_espeak(row["espeak_us"])
    note = ""
    source = "espeak-ng"
    if wid == "backwards":
        gb = "/ˈbækwədz/"
        source = "user-ref-uk"
        note = "sheet backward(s) /ˈbækwəd/ plus the pronounced final /z/"
    elif wid == "disk":
        gb = "/dɪsk/"
        source = "user-ref-uk"
        note = "sheet row disk＝disc /dɪsk/"
    elif wid not in FORCE_ESPEAK_UK and row.get("xls"):
        raw_uk = row["xls"]["ipa"]
        # nephew is stored as two pronunciations in one cell; keep the first in the field.
        if "," in raw_uk:
            raw_uk = raw_uk.split(",")[0]
            note = "sheet also lists a second UK pronunciation"
        gb = clean_ipa(raw_uk)
        source = "user-ref-uk"
        us_sheet = row["xls"].get("us")
        if us_sheet:
            cleaned = clean_ipa(us_sheet)
            if sim(phon_key(cleaned), phon_key(us)) >= 0.55 and not us_sheet.strip().startswith("-"):
                us = cleaned
                note = "US from sheet"
    if wid in FORCE_ESPEAK_UK:
        source = "espeak-ng"
        why = {
            "shout": "sheet IPA is shoulder",
            "slice": "sheet IPA is sleeve",
            "possess": "sheet IPA is position",
            "uncertain": "sheet IPA is certain, missing un-",
            "booth": "sheet uses /ð/ instead of /θ/",
            "fridge": "sheet IPA is refrigerator",
            "widow": "no sheet row",
            "grocery": "no sheet row",
            "tablet": "no sheet row",
            "airline": "no sheet row",
            "donate": "no sheet row",
            "warn": "no sheet row",
        }[wid]
        note = why
    if wid == "uncertain":
        us = "/ʌnˈsɜːrtən/"
    if wid == "insert":
        us = "/ɪnˈsɜːrt/"
        note = (note + "; " if note else "") + "US espeak stress was the noun; verb stress kept"
    if wid == "o-clock":
        us = "/əˈklɑːk/"
        note = (note + "; " if note else "") + "US stress aligned with the sheet"
    return {"uk": gb, "us": us, "ipaSource": source, "ipaNote": note}


def review(cards_by_w: dict, rows: list[dict]) -> list[str]:
    errors = []
    sentences = []
    if len(cards_by_w) != 200 or len(rows) != 200:
        errors.append(f"count cards {len(cards_by_w)} rows {len(rows)}")
    seen_en = {}
    for row in rows:
        card = cards_by_w.get(row["w"].lower())
        if not card:
            errors.append(f"no card for {row['w']}")
            continue
        if card["senses"][0]["pos"] not in POS_TO_CEFRJ:
            errors.append(f"pos {row['id']} {card['senses'][0]['pos']}")
        if len(card["ex"]) != 2:
            errors.append(f"ex count {row['id']}")
        pat = headword_pattern(row["w"])
        for i, ex in enumerate(card["ex"]):
            if not ex["en"] or not ex["zh"]:
                errors.append(f"empty ex {row['id']} {i}")
            if not pat.search(ex["en"]):
                errors.append(f"gap miss {row['id']} {i}: {ex['en']}")
            if not exact_or_inflected(row["w"], ex["en"]):
                errors.append(f"exact miss {row['id']} {i}: {ex['en']}")
            key = ex["en"].strip().lower()
            if key in seen_en:
                errors.append(f"dup sentence {row['id']} == {seen_en[key]}")
            seen_en[key] = row["id"]
            sentences.append((row["id"], i, ex["en"]))
            low = ex["en"].lower()
            for bad in ("a lesson about", "last bus", "not how to harm", "poster"):
                if bad in low:
                    errors.append(f"template {row['id']} {bad}")
        if len(card["ex"][1]["en"].split()) < len(card["ex"][0]["en"].split()):
            errors.append(f"ex1 shorter {row['id']}")
        for col in card["col"]:
            if "｜" not in col:
                errors.append(f"col bar {row['id']} {col}")
            en = col.split("｜")[0].lower()
            if re.fullmatch(r"an? [a-z']+ of", en):
                errors.append(f"dummy col {row['id']} {col}")
            w = row["w"].lower()
            stems = {w, w[:4], *IRREGULAR.get(w, [])}
            if not any(stem and stem in en for stem in stems):
                errors.append(f"col stem {row['id']} {col}")
        # near-duplicate pair inside the card
        from difflib import SequenceMatcher
        ratio = SequenceMatcher(None, card["ex"][0]["en"].lower(), card["ex"][1]["en"].lower()).ratio()
        if ratio >= 0.72:
            errors.append(f"pair similar {ratio:.2f} {row['id']}")
    from difflib import SequenceMatcher
    ens = [(i, s) for i, _, s in sentences]
    for a in range(len(ens)):
        for b in range(a + 1, len(ens)):
            if ens[a][0] == ens[b][0]:
                continue
            # only compare across cards; skip if first 12 chars differ a lot to save time
            ra = SequenceMatcher(None, ens[a][1].lower(), ens[b][1].lower()).ratio()
            if ra >= 0.62:
                errors.append(f"cross {ra:.2f} {ens[a][0]} || {ens[b][0]} :: {ens[a][1]} || {ens[b][1]}")
    return errors


def build_entries(rows, cards_by_w):
    entries = []
    audit = []
    for row in rows:
        card = cards_by_w[row["w"].lower()]
        cefr_info = choose_cefr(card, row)
        ipa = choose_ipa(row)
        media = row["media"]
        has_img = bool(media["img"] and media["thumb"])
        m = 0
        if has_img:
            m |= 1
        if media["uk"]:
            m |= 2
        if media["us"]:
            m |= 4
        entry = {
            "id": row["id"],
            "w": row["w"],
            "uk": ipa["uk"],
            "us": ipa["us"],
            "senses": card["senses"],
            "ex": card["ex"],
            "col": card["col"],
            "fam": card["fam"],
            "syn": card["syn"],
            "ant": card["ant"],
            "tip": card["tip"],
            "cefr": cefr_info["cefr"],
            "topic": card["topic"],
            "note": card.get("note") or "",
            "meta": {
                "gaokaoFreq": "high",
                "source": "gaokao-outline-3500+wordfreq-zipf",
                "batch": 13,
                "zipf": row["zipf"],
                "ipaSource": ipa["ipaSource"],
                "mediaReuseCandidate": has_img,
            },
        }
        entry["_m"] = m
        entry["_ipaNote"] = ipa["ipaNote"]
        entries.append(entry)
        audit.append({**cefr_info, "ipaSource": ipa["ipaSource"], "ipaNote": ipa["ipaNote"], "uk": ipa["uk"], "us": ipa["us"],
                       "missingImg": not has_img, "missingUk": not media["uk"], "missingUs": not media["us"],
                       "xls": bool(row.get("in_xls_exact") or (row.get("xls") and row["xls"].get("variant"))),
                       "xlsVariant": (row.get("xls") or {}).get("variant"),
                       "inXlsExact": row.get("in_xls_exact")})
    return entries, audit


def publish(entries, audit):
    data_path = ROOT / "data" / "word-atlas.json"
    old = json.loads(data_path.read_text(encoding="utf-8"))
    old_ids = {e["id"] for e in old}
    if any(e["id"] in old_ids for e in entries):
        raise SystemExit("new id collides with an existing card")
    # preserve old media bits
    old_m = {}
    pub = ROOT / "public" / "atlas"
    index = json.loads((pub / "index.json").read_text(encoding="utf-8"))
    for n in range((index["count"] + index["chunk"] - 1) // index["chunk"]):
        for e in json.loads((pub / "entries" / f"{n}.json").read_text(encoding="utf-8")):
            old_m[e["id"]] = e["m"]
    clean = []
    for e in entries:
        m = e.pop("_m")
        e.pop("_ipaNote", None)
        e_pub_m = m
        clean.append((e, e_pub_m))
    combined = list(old) + [e for e, _ in clean]
    m_of = dict(old_m)
    for e, m in clean:
        m_of[e["id"]] = m
    topics = [t[0] for t in index["topics"]]
    combined.sort(key=lambda e: (CEFR.index(e["cefr"]), hashlib.sha1(e["id"].encode()).hexdigest()))
    # old objects unchanged
    data_path.write_text(json.dumps(combined, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # csv
    csv_path = ROOT / "data" / "word-atlas.csv"
    with csv_path.open(newline="", encoding="utf-8") as f:
        existing_rows = list(csv.reader(f))
    header = existing_rows[0]
    by_id = {r[0]: r for r in existing_rows[1:]}
    out_rows = [header]
    for e in combined:
        if e["id"] in by_id:
            out_rows.append(by_id[e["id"]])
            continue
        ex = e["ex"] + [{"en": "", "zh": ""}] * (2 - len(e["ex"]))
        out_rows.append([
            e["id"], e["w"], e["uk"], e["us"], e["cefr"], e["topic"],
            " | ".join(f'{s["pos"]} {s["zh"]}' for s in e["senses"]),
            " | ".join(s["en"] for s in e["senses"]),
            ex[0]["en"], ex[0]["zh"], ex[1]["en"], ex[1]["zh"],
            " ; ".join(e["col"]), " ; ".join(e["fam"]), ", ".join(e["syn"]), ", ".join(e["ant"]), e["tip"],
        ])
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows(out_rows)
    csv_path.write_bytes(buf.getvalue().encode("utf-8"))

    # shards and index; sentence-audio bits stay off until Kokoro
    words = []
    public_entries = []
    for e in combined:
        m = m_of[e["id"]]
        s0 = e["senses"][0]
        zh = f'{s0["pos"]} {s0["zh"]}'.strip()
        words.append([e["id"], e["w"], zh, e["uk"] or e["us"], CEFR.index(e["cefr"]), topics.index(e["topic"]), m])
        pub_e = {k: v for k, v in e.items() if k != "meta"}
        pub_e["m"] = m
        public_entries.append(pub_e)
    chunk = index["chunk"]
    nfiles = (len(public_entries) + chunk - 1) // chunk
    for n in range(nfiles):
        block = public_entries[n * chunk:(n + 1) * chunk]
        (pub / "entries" / f"{n}.json").write_text(json.dumps(block, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    index["count"] = len(words)
    index["examples"] = sum(len(e["ex"]) for e in combined)
    index["illustrated"] = sum(1 for r in words if r[6] & 1)
    index["voiced"] = sum(1 for r in words if r[6] & 2)
    index["words"] = words
    (pub / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (ROOT / "data" / "batch-13-cefr.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "count": index["count"],
        "examples": index["examples"],
        "illustrated": index["illustrated"],
        "voiced": index["voiced"],
    }))


def main():
    import sys
    sys.path.insert(0, str(ROOT))
    a = load_py(ROOT / "scripts" / "batch13_cards_a.py", "cards_a")
    b = load_py(ROOT / "scripts" / "batch13_cards_b.py", "cards_b")
    c = load_py(ROOT / "scripts" / "batch13_cards_c.py", "cards_c")
    cards = a.CARDS_A + b.CARDS_B + c.CARDS_C
    cards_by_w = {card["id"].lower(): card for card in cards}
    rows = json.loads(ANNOT.read_text(encoding="utf-8"))
    errors = review(cards_by_w, rows)
    entries, audit = build_entries(rows, cards_by_w)
    from collections import Counter
    dist = Counter(e["cefr"] for e in entries)
    decisions = Counter(a["decision"] for a in audit)
    print("cefr", dict(dist))
    print("decisions", dict(decisions))
    print("errors", len(errors))
    for err in errors:
        print(err)
    if errors:
        raise SystemExit(1)
    if "--write" in sys.argv:
        publish(entries, audit)


if __name__ == "__main__":
    main()
