#!/usr/bin/env python3
"""Assemble batch 16 cards, assign CEFR and IPA, and publish the atlas files.

Review only:  python3 scripts/build_batch16.py
Publish:      python3 scripts/build_batch16.py --write

Selection rows live in data/batch-16-selection.json (Zipf and CEFR-J tags).
IPA is read from espeak-ng at build time, then normalized. A short override
list corrects stress or vowel mistakes. No paid API is called.
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
SELECTION = ROOT / "data" / "batch-16-selection.json"
CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"]
ZIPF_B1 = 4.18
ZIPF_B2 = 3.74
POS_TO_CEFRJ = {
    "n.": "noun",
    "v.": "verb",
    "adj.": "adjective",
    "adv.": "adverb",
    "prep.": "preposition",
    "pron.": "pronoun",
    "conj.": "conjunction",
    "det.": "determiner",
    "num.": "number",
    "int.": "interjection",
}
ALLOWED_POS = set(POS_TO_CEFRJ)
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

# Learner IPA after espeak-ng 1.51. These replace a bad stress, a missing TRAP
# vowel, or a reading that treated an abbreviation as an ordinary word.
IPA_OVERRIDE = {
    # espeak-ng 1.51 wrote TRAP as a, put stress inside a consonant cluster,
    # or read a different part of speech.
    "capsule": ("/ˈkæpsjuːl/", "/ˈkæpsəl/"),
    "advertise": ("/ˈædvətaɪz/", "/ˈædvərtaɪz/"),
    "bamboo": ("/ˌbæmˈbuː/", "/ˌbæmˈbuː/"),
    "panda": ("/ˈpændə/", "/ˈpændə/"),
    "applicant": ("/ˈæplɪkənt/", "/ˈæplɪkənt/"),
    "camel": ("/ˈkæməl/", "/ˈkæməl/"),
    "fax": ("/fæks/", "/fæks/"),
    "carrot": ("/ˈkærət/", "/ˈkærət/"),
    "damp": ("/dæmp/", "/dæmp/"),
    "granny": ("/ˈɡræni/", "/ˈɡræni/"),
    "lantern": ("/ˈlæntən/", "/ˈlæntərn/"),
    "astronaut": ("/ˈæstrənɔːt/", "/ˈæstrənɔːt/"),
    "chant": ("/tʃɑːnt/", "/tʃænt/"),
    "granddaughter": ("/ˈɡrændɔːtə/", "/ˈɡrændɔːtər/"),
    "gymnastics": ("/dʒɪmˈnæstɪks/", "/dʒɪmˈnæstɪks/"),
    "congratulate": ("/kənˈɡrætʃuleɪt/", "/kənˈɡrætʃuleɪt/"),
    "madam": ("/ˈmædəm/", "/ˈmædəm/"),
    "adolescent": ("/ˌædəˈlesənt/", "/ˌædəˈlesənt/"),
    "ambiguous": ("/æmˈbɪɡjuəs/", "/æmˈbɪɡjuəs/"),
    "handwriting": ("/ˈhændraɪtɪŋ/", "/ˈhændraɪtɪŋ/"),
    "traveler": ("/ˈtrævələ/", "/ˈtrævələr/"),
    "traveller": ("/ˈtrævələ/", "/ˈtrævələr/"),
    "Antarctic": ("/ænˈtɑːktɪk/", "/ænˈtɑːrktɪk/"),
    "catastrophe": ("/kəˈtæstrəfi/", "/kəˈtæstrəfi/"),
    "cabbage": ("/ˈkæbɪdʒ/", "/ˈkæbɪdʒ/"),
    "rag": ("/ræɡ/", "/ræɡ/"),
    "clap": ("/klæp/", "/klæp/"),
    "practise": ("/ˈpræktɪs/", "/ˈpræktɪs/"),
    "ancestor": ("/ˈænsestə/", "/ˈænsestər/"),
    "botanical": ("/bəˈtænɪkl/", "/bəˈtænɪkl/"),
    "paddle": ("/ˈpædl/", "/ˈpædl/"),
    "parrot": ("/ˈpærət/", "/ˈpærət/"),
    "sparrow": ("/ˈspærəʊ/", "/ˈspɛroʊ/"),
    "analyse": ("/ˈænəlaɪz/", "/ˈænəlaɪz/"),
    "admirable": ("/ˈædmərəbl/", "/ˈædmərəbl/"),
    "pineapple": ("/ˈpaɪnæpl/", "/ˈpaɪnæpl/"),
    "translator": ("/trænzˈleɪtə/", "/trænzˈleɪtər/"),
    "squirrel": ("/ˈskwɪrəl/", "/ˈskwɜːrəl/"),
    "oneself": ("/wʌnˈself/", "/wʌnˈself/"),
    "buffet": ("/ˈbʊfeɪ/", "/bəˈfeɪ/"),
    "interrupt": ("/ˌɪntəˈrʌpt/", "/ˌɪntəˈrʌpt/"),
    "yogurt": ("/ˈjɒɡət/", "/ˈjoʊɡərt/"),
    "haircut": ("/ˈheəkʌt/", "/ˈherkʌt/"),
    "courtyard": ("/ˈkɔːtjɑːd/", "/ˈkɔːrtjɑːrd/"),
    "starvation": ("/stɑːˈveɪʃən/", "/stɑːrˈveɪʃən/"),
    "postpone": ("/pəʊstˈpəʊn/", "/poʊstˈpoʊn/"),
    "unbearable": ("/ʌnˈbeərəbl/", "/ʌnˈberəbl/"),
    "multiply": ("/ˈmʌltɪplaɪ/", "/ˈmʌltɪplaɪ/"),
    "kangaroo": ("/ˌkæŋɡəˈruː/", "/ˌkæŋɡəˈruː/"),
    "digital versatile disk": ("/ˌdɪdʒɪtl ˈvɜːsətaɪl ˌdɪsk/", "/ˌdɪdʒɪtl ˈvɜːrsətaɪl ˌdɪsk/"),
    "pianist": ("/ˈpiːənɪst/", "/ˈpiːənɪst/"),
    "pear": ("/peə/", "/per/"),
}

VOWELS = set("aeiouæɑɒɔəɛɜɪʊʌɐʉɨøʏœᵻᵿ")


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


def shift_stress(ipa: str) -> str:
    chars = list(ipa)
    result = []
    i = 0
    while i < len(chars):
        c = chars[i]
        if c in "ˈˌ":
            nxt = chars[i + 1] if i + 1 < len(chars) else ""
            if nxt in VOWELS:
                j = len(result)
                while j > 0 and result[j - 1] not in VOWELS and result[j - 1] not in "ˈˌː":
                    j -= 1
                result.insert(j, c)
            else:
                result.append(c)
        else:
            result.append(c)
        i += 1
    return "".join(result)


def clean_espeak(raw: str) -> str:
    s = raw.strip().replace("\n", " ").strip()
    s = s.replace("ʔ", "").replace("n̩", "ən").replace("m̩", "əm").replace("l̩", "əl")
    s = s.replace("ɚ", "ər").replace("ɝ", "ɜːr").replace("ɐ", "ə").replace("ɹ", "r").replace("ɾ", "t")
    s = s.replace("ᵻ", "ɪ").replace("ᵿ", "ʊ")
    s = s.replace(" ", "")
    s = shift_stress(s)
    s = s.replace("g", "ɡ")
    s = re.sub(r"ə([ˈˌ])r(?=[^aeiouæɑɒɔəɛɜɪʊʌˈˌː])", r"ər\1", s)
    s = s.replace("rr", "r")
    return f"/{s}/"


def espeak(word: str, voice: str) -> str:
    out = subprocess.check_output(["espeak-ng", "-v", voice, "-q", "--ipa", word], text=True)
    return clean_espeak(out)


def choose_ipa(word: str) -> dict:
    if word in IPA_OVERRIDE:
        uk, us = IPA_OVERRIDE[word]
        return {"uk": uk, "us": us, "ipaSource": "espeak-ng+override", "ipaNote": "stress or vowel corrected after espeak-ng 1.51"}
    return {
        "uk": espeak(word, "en-gb"),
        "us": espeak(word, "en-us"),
        "ipaSource": "espeak-ng",
        "ipaNote": "espeak-ng 1.51, stress moved before a vowel onset, flap and syllabic consonants normalized",
    }


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
    return re.findall(r"[0-9A-Za-z'À-ÖØ-öø-ÿ]+", text.lower())


def exact_or_inflected(word: str, sentence: str) -> bool:
    w = word.lower()
    if re.search(r"\s", w):
        body = r"\s+".join(re.escape(part) for part in w.split())
        return re.search(rf"(?<![A-Za-z]){body}(?![A-Za-z])", sentence, re.I) is not None
    found = set(tokens(sentence))
    if w in found:
        return True
    extras = IRREGULAR.get(w, [])
    if any(form in found for form in extras):
        return True
    for tok in found:
        if tok.startswith(w) and tok[len(w):] in {"s", "es", "ed", "d", "ing", "er", "est", "ly"}:
            return True
    if len(w) > 3 and w.endswith("y") and w[-2] not in "aeiou":
        stem = w[:-1]
        for tok in found:
            if tok.startswith(stem) and tok[len(stem):] in {"ies", "ied", "ier", "iest"}:
                return True
    return False


def allowed_forms(word: str) -> set[str]:
    w = word.lower()
    forms = {w, *IRREGULAR.get(w, [])}
    for suf in ("s", "es", "ed", "d", "ing", "er", "est", "ly"):
        forms.add(w + suf)
    if w.endswith("e") and len(w) > 2:
        stem = w[:-1]
        for suf in ("ed", "es", "ing", "er", "est"):
            forms.add(stem + suf)
    if len(w) > 3 and w.endswith("y") and w[-2] not in "aeiou":
        stem = w[:-1]
        for suf in ("ied", "ies", "ier", "iest"):
            forms.add(stem + suf)
        forms.add(stem + "ying")
    if re.search(r"[^aeiou][aeiou][bdgmnprt]$", w):
        forms.add(w + w[-1] + "ed")
        forms.add(w + w[-1] + "ing")
        forms.add(w + w[-1] + "er")
    return forms


def choose_cefr(card: dict, row: dict) -> dict:
    band = zipf_band(row["zipf"])
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
        "published": [{"pos": t["pos"], "cefr": t["cefr"], "headword": t.get("headword", row["w"])} for t in tags],
        "publishedVia": row.get("cefrj_via"),
        "samePosLevels": same,
        "otherPos": [{"pos": p, "cefr": c} for p, c in other],
        "cefr": level,
        "decision": how,
        "differ": bool(tags) and level != band,
    }


def review(cards_by_id: dict, rows: list[dict]) -> list[str]:
    errors = []
    sentences = []
    if len(cards_by_id) != 200 or len(rows) != 200:
        errors.append(f"count cards {len(cards_by_id)} rows {len(rows)}")
    seen_en = {}
    forms_cache = {}
    for row in rows:
        card = cards_by_id.get(row["id"])
        if not card:
            errors.append(f"no card for {row['id']}")
            continue
        if card["senses"][0]["pos"] not in ALLOWED_POS:
            errors.append(f"pos {row['id']} {card['senses'][0]['pos']}")
        if len(card["ex"]) != 2:
            errors.append(f"ex count {row['id']}")
        pat = headword_pattern(row["w"])
        forms = forms_cache.setdefault(row["w"].lower(), allowed_forms(row["w"]))
        for i, ex in enumerate(card["ex"]):
            if not ex["en"] or not ex["zh"]:
                errors.append(f"empty ex {row['id']} {i}")
            match = pat.search(ex["en"])
            if not match:
                errors.append(f"gap miss {row['id']} {i}: {ex['en']}")
            elif match.group(1).lower() not in forms:
                errors.append(f"gap wrong {row['id']} {i}: {match.group(1)!r} in {ex['en']}")
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
            ra = SequenceMatcher(None, ens[a][1].lower(), ens[b][1].lower()).ratio()
            if ra >= 0.62:
                errors.append(f"cross {ra:.2f} {ens[a][0]} || {ens[b][0]} :: {ens[a][1]} || {ens[b][1]}")
    return errors


def media_flags(entry_id: str) -> dict:
    pub = ROOT / "public" / "atlas"
    img = pub / "img" / f"{entry_id}.webp"
    thumb = pub / "thumb" / f"{entry_id}.webp"
    return {
        "img": img.is_file() and thumb.is_file(),
        "uk": (pub / "audio" / "uk" / f"{entry_id}.mp3").is_file(),
        "us": (pub / "audio" / "us" / f"{entry_id}.mp3").is_file(),
        "ex": (pub / "audio" / "ex" / f"{entry_id}.mp3").is_file(),
        "ex2": (pub / "audio" / "ex2" / f"{entry_id}.mp3").is_file(),
    }


def build_entries(rows, cards_by_id):
    entries = []
    audit = []
    for row in rows:
        card = cards_by_id[row["id"]]
        cefr_info = choose_cefr(card, row)
        ipa = choose_ipa(row["w"])
        media = media_flags(row["id"])
        m = 0
        if media["img"]:
            m |= 1
        if media["uk"]:
            m |= 2
        if media["us"]:
            m |= 4
        if media["ex"]:
            m |= 8
        if media["ex2"]:
            m |= 16
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
                "batch": 16,
                "zipf": row["zipf"],
                "ipaSource": ipa["ipaSource"],
                "mediaReuseCandidate": bool(media["img"]),
            },
        }
        entry["_m"] = m
        entries.append(entry)
        audit.append({
            **cefr_info,
            "ipaSource": ipa["ipaSource"],
            "ipaNote": ipa["ipaNote"],
            "uk": ipa["uk"],
            "us": ipa["us"],
            "missingImg": not media["img"],
            "missingUk": not media["uk"],
            "missingUs": not media["us"],
        })
    return entries, audit


def publish(entries, audit):
    data_path = ROOT / "data" / "word-atlas.json"
    old = json.loads(data_path.read_text(encoding="utf-8"))
    new_ids = {e["id"] for e in entries}
    old_ids = {e["id"] for e in old}
    # A second --write may refresh these 200 cards. Any other overlap is a real collision.
    foreign = new_ids & old_ids
    if foreign and not foreign <= new_ids:
        raise SystemExit("new id collides with an existing card")
    kept = [e for e in old if e["id"] not in new_ids]
    if len(kept) + len(entries) != len(old_ids | new_ids):
        raise SystemExit("catalog id accounting failed")
    old = kept
    old_snapshot = {e["id"]: json.dumps(e, ensure_ascii=False, sort_keys=True) for e in old}
    pub = ROOT / "public" / "atlas"
    index = json.loads((pub / "index.json").read_text(encoding="utf-8"))
    old_m = {}
    for n in range((index["count"] + index["chunk"] - 1) // index["chunk"]):
        for e in json.loads((pub / "entries" / f"{n}.json").read_text(encoding="utf-8")):
            old_m[e["id"]] = e["m"]
    clean = []
    for e in entries:
        m = e.pop("_m")
        clean.append((e, m))
    combined = list(old) + [e for e, _ in clean]
    for e in combined:
        if e["id"] in old_snapshot and json.dumps(e, ensure_ascii=False, sort_keys=True) != old_snapshot[e["id"]]:
            raise SystemExit(f"existing card changed: {e['id']}")
    m_of = dict(old_m)
    for e, m in clean:
        m_of[e["id"]] = m
    topics = [t[0] for t in index["topics"]]
    combined.sort(key=lambda e: (CEFR.index(e["cefr"]), hashlib.sha1(e["id"].encode()).hexdigest()))
    data_path.write_text(json.dumps(combined, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    csv_path = ROOT / "data" / "word-atlas.csv"
    with csv_path.open(newline="", encoding="utf-8") as f:
        existing_rows = list(csv.reader(f))
    header = existing_rows[0]
    by_id = {r[0]: r for r in existing_rows[1:]}
    out_rows = [header]
    for e in combined:
        # Refresh this batch. Leave every earlier catalog row byte-for-byte.
        if e["id"] in by_id and e["id"] not in new_ids:
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
    # drop a stale extra shard if the count ever shrinks; it does not
    index["count"] = len(words)
    index["examples"] = sum(len(e["ex"]) for e in combined)
    index["illustrated"] = sum(1 for r in words if r[6] & 1)
    index["voiced"] = sum(1 for r in words if r[6] & 2)
    index["words"] = words
    (pub / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (ROOT / "data" / "batch-16-cefr.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "count": index["count"],
        "examples": index["examples"],
        "illustrated": index["illustrated"],
        "voiced": index["voiced"],
        "missingImg": sum(1 for a in audit if a["missingImg"]),
        "missingUk": sum(1 for a in audit if a["missingUk"]),
        "missingUs": sum(1 for a in audit if a["missingUs"]),
    }))


def main():
    import sys
    from collections import Counter
    a = load_py(ROOT / "scripts" / "batch16_cards_a.py", "cards_a")
    b = load_py(ROOT / "scripts" / "batch16_cards_b.py", "cards_b")
    c = load_py(ROOT / "scripts" / "batch16_cards_c.py", "cards_c")
    d = load_py(ROOT / "scripts" / "batch16_cards_d.py", "cards_d")
    cards = a.CARDS_A + b.CARDS_B + c.CARDS_C + d.CARDS_D
    cards_by_id = {}
    for card in cards:
        if card["id"] in cards_by_id:
            raise SystemExit(f"duplicate card {card['id']}")
        cards_by_id[card["id"]] = card
    rows = json.loads(SELECTION.read_text(encoding="utf-8"))
    errors = review(cards_by_id, rows)
    entries, audit = build_entries(rows, cards_by_id)
    dist = Counter(e["cefr"] for e in entries)
    decisions = Counter(item["decision"] for item in audit)
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
