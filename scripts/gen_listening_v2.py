#!/usr/bin/env python3
"""Regenerate listening MP3s with per-lesson distinct Piper voices.

- Each lesson gets a different narrator voice (rotating pool of US/GB male/female).
- Quoted dialogue (“...”) alternates between two character voices (female/male).
- Slower pace: --length-scale 1.12, --sentence-silence 0.5.
Writes a `voice` label back into src/data/listening.json and a manifest to
scripts/listening_voices.md.
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPER = ROOT.parent / "tools" / "tts-venv" / "bin" / "piper"
VOICES_DIR = ROOT.parent / "tools" / "piper-voices"

# (model file, label, gender)
POOL = [
    ("en_US-lessac-medium", "美音女声 · Lessac", "F"),
    ("en_US-ryan-medium", "美音男声 · Ryan", "M"),
    ("en_GB-alba-medium", "英音女声 · Alba", "F"),
    ("en_GB-alan-medium", "英音男声 · Alan", "M"),
    ("en_US-amy-medium", "美音女声 · Amy", "F"),
    ("en_US-joe-medium", "美音男声 · Joe", "M"),
    ("en_GB-cori-medium", "英音女声 · Cori", "F"),
    ("en_GB-northern_english_male-medium", "英音男声 · Northern", "M"),
    ("en_US-hfc_female-medium", "美音女声 · HFC", "F"),
    ("en_US-hfc_male-medium", "美音男声 · HFC", "M"),
    ("en_GB-jenny_dioco-medium", "英音女声 · Jenny", "F"),
]
FEMALE = [v for v in POOL if v[2] == "F"]
MALE = [v for v in POOL if v[2] == "M"]


def synth(text, model, out_wav):
    subprocess.run(
        [str(PIPER), "-m", str(VOICES_DIR / f"{model}.onnx"), "-f", str(out_wav),
         "--length-scale", "1.12", "--sentence-silence", "0.5"],
        input=text.encode(), check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def segments(transcript):
    """Split into (is_quote, text) segments preserving order."""
    parts = re.split(r"(“[^”]*”)", transcript)
    return [(p.startswith("“"), p.strip()) for p in parts if p.strip()]


def main():
    data = json.loads((ROOT / "src" / "data" / "listening.json").read_text(encoding="utf-8"))
    out_dir = ROOT / "public" / "audio" / "listening"
    manifest = ["# 听力配音分配（v2 多音色）", ""]
    for i, item in enumerate(data):
        narrator = POOL[i % len(POOL)]
        segs = segments(item["transcript"])
        has_dialogue = any(q for q, _ in segs)
        label = narrator[1]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            wavs = []
            quote_idx = 0
            fi = mi = 0
            for is_quote, text in segs:
                if is_quote:
                    # alternate female / male character voices, skipping narrator duplicates
                    if quote_idx % 2 == 0:
                        voice = FEMALE[fi % len(FEMALE)]; fi += 1
                    else:
                        voice = MALE[mi % len(MALE)]; mi += 1
                    quote_idx += 1
                else:
                    voice = narrator
                wav = td / f"seg{len(wavs):03d}.wav"
                synth(text, voice[0], wav)
                wavs.append(wav)
            if has_dialogue:
                label += "（含双角色对话配音）"
            list_file = td / "list.txt"
            list_file.write_text("".join(f"file '{w}'\n" for w in wavs))
            out_mp3 = out_dir / f"{item['id']}.mp3"
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                 "-i", str(list_file), "-codec:a", "libmp3lame", "-q:a", "4", str(out_mp3)],
                check=True,
            )
        item["voice"] = label
        manifest.append(f"- {item['id']}（{item['level']}）{item['title']}：{label}")
        print(f"done {item['id']}: {label}", flush=True)
    (ROOT / "src" / "data" / "listening.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "scripts" / "listening_voices.md").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print("ALL_DONE")


if __name__ == "__main__":
    main()
