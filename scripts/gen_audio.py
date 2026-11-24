#!/usr/bin/env python3
"""Generate local MP3s with Piper. Existing nonempty files are kept."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT.parent / "tools"


def load(name):
    return json.loads((ROOT / "src" / "data" / f"{name}.json").read_text(encoding="utf-8"))


def filename(value):
    return re.sub(r"[^a-z0-9'-]+", "-", value.lower().strip()).strip("-") + ".mp3"


def entries(category):
    data = load(category)
    if category == "words":
        return [(word["word"], word["word"]) for deck in data for word in deck["words"]]
    if category == "listening":
        return [(item["id"], item["transcript"]) for item in data]
    return [(item["id"], item["phrase"]) for item in data]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("categories", nargs="*", metavar="CATEGORY")
    parser.add_argument("--piper", default=os.environ.get("PIPER_BIN", TOOLS / "tts-venv/bin/piper"))
    parser.add_argument("--model", default=os.environ.get("PIPER_MODEL", TOOLS / "piper-voices/en_US-lessac-medium.onnx"))
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    categories = args.categories or ["words", "listening", "phrases"]
    if set(categories) - {"words", "listening", "phrases"} or args.jobs < 1:
        parser.error("Use words, listening or phrases and a positive job count.")

    tasks = {}
    for category in categories:
        mapping = {}
        directory = ROOT / "public" / "audio" / category
        directory.mkdir(parents=True, exist_ok=True)
        for item, text in entries(category):
            name = filename(item)
            if directory / name in tasks:
                raise ValueError(f"Duplicate audio filename: {category}/{name}")
            mapping[item] = name
            tasks[directory / name] = text
        if category == "words":
            (ROOT / "src" / "data" / "word-audio.json").write_text(
                json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

    def generate(path, text):
        if path.is_file() and path.stat().st_size:
            return "existing"
        with tempfile.TemporaryDirectory(dir=path.parent) as directory:
            wav = Path(directory) / "voice.wav"
            mp3 = Path(directory) / "voice.mp3"
            subprocess.run(
                [str(args.piper), "-m", str(args.model), "-f", str(wav)],
                input=" ".join(text.split()) + "\n", text=True, check=True, capture_output=True
            )
            subprocess.run(
                ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(wav),
                 "-codec:a", "libmp3lame", "-q:a", "4", str(mp3)],
                check=True, capture_output=True
            )
            mp3.replace(path)
        return "created"

    counts = {"existing": 0, "created": 0}
    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(generate, path, text): path for path, text in tasks.items()}
        for future in as_completed(futures):
            try:
                counts[future.result()] += 1
            except Exception as error:
                details = getattr(error, "stderr", "")
                if isinstance(details, bytes):
                    details = details.decode(errors="replace")
                failures.append(f"{futures[future].relative_to(ROOT)}: {details or error}")
    print(f"生成 {counts['created']}，跳过 {counts['existing']}，失败 {len(failures)}")
    for failure in sorted(failures):
        print(failure)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
