#!/usr/bin/env python3
"""Build CET-4 / CET-6 / IELTS full word decks from ECDICT (open dictionary).

Filters: exam tag match, single lowercase token, has phonetic and Chinese
translation. Sorted by ECDICT frequency rank (frq, then bnc).
Appends 3 decks to src/data/words.json and merges src/data/word-audio.json.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/tmp/ecdict.csv")

EXAMS = [
    ("cet4", "cet4-full", "CET-4 必背全词库", "CET-4 必背", "四级考试大纲标签全量高频词，数据来自开源词库 ECDICT，按词频排序。"),
    ("cet6", "cet6-full", "CET-6 必背全词库", "CET-6 必背", "六级考试大纲标签全量高频词，数据来自开源词库 ECDICT，按词频排序。"),
    ("ielts", "ielts-full", "IELTS 必背全词库", "IELTS 必背", "雅思考试标签全量高频词，数据来自开源词库 ECDICT，按词频排序。"),
]

WORD_RE = re.compile(r"^[a-z][a-z'-]*[a-z]$|^[a-z]$")


def audio_name(word):
    return re.sub(r"[^a-z0-9'-]+", "-", word.lower().strip()).strip("-") + ".mp3"


def clean_cn(translation):
    parts = [p.strip() for p in translation.replace("\\n", "\n").split("\n")]
    parts = [re.sub(r"^[a-z]+\.\s*", "", p) for p in parts]
    parts = [p for p in parts if p and not p.startswith("[网络]") and not p.startswith("[") ]
    cn = "；".join(parts)
    return cn[:90]


def parse_pos(pos_field, translation):
    if pos_field:
        first = pos_field.split("/")[0].split(":")[0].strip()
        if first:
            return first + "."
    m = re.match(r"^([a-z]+\.)", translation.strip())
    return m.group(1) if m else ""


def main():
    rows = {tag: [] for tag, *_ in EXAMS}
    with open(SRC, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            word = (r["word"] or "").strip()
            if not WORD_RE.match(word):
                continue
            phonetic = (r["phonetic"] or "").strip()
            translation = (r["translation"] or "").strip()
            if not phonetic or not translation or not re.search(r"[一-鿿]", translation):
                continue
            tags = (r["tag"] or "").split()
            try:
                frq = int(r["frq"] or 0)
            except ValueError:
                frq = 0
            try:
                bnc = int(r["bnc"] or 0)
            except ValueError:
                bnc = 0
            for tag, *_ in EXAMS:
                if tag in tags:
                    rows[tag].append((frq or 10**9, bnc or 10**9, word, phonetic, translation, r["pos"] or ""))

    words_path = ROOT / "src" / "data" / "words.json"
    decks = json.loads(words_path.read_text(encoding="utf-8"))
    decks = [d for d in decks if d["id"] not in {e[1] for e in EXAMS}]

    mapping_path = ROOT / "src" / "data" / "word-audio.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    stats = {}
    for tag, deck_id, name, level, desc in EXAMS:
        seen = set()
        entries = []
        for _, _, word, phonetic, translation, pos in sorted(rows[tag]):
            if word in seen:
                continue
            seen.add(word)
            entries.append({
                "word": word,
                "phonetic": f"/{phonetic.strip('/')}/",
                "pos": parse_pos(pos, translation),
                "cn": clean_cn(translation),
                "example": "",
                "exampleCn": "",
                "level": level,
            })
            mapping[word] = audio_name(word)
        decks.append({"id": deck_id, "name": name, "description": desc, "words": entries})
        stats[name] = len(entries)

    words_path.write_text(json.dumps(decks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    unique = sorted(mapping.keys())
    (ROOT / "scripts" / "all_words.txt").write_text("\n".join(unique) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    print("unique words needing audio mapping:", len(unique))


if __name__ == "__main__":
    main()
