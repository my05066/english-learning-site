#!/usr/bin/env python3
"""Fast word-audio generation: persistent Piper voice per worker process.

Reads scripts/all_words.txt, skips existing MP3s, writes public/audio/words/.
Run with the tts venv python: ~/workspace/tools/tts-venv/bin/python scripts/gen_word_audio_fast.py
"""
import subprocess
import sys
import wave
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "audio" / "words"
MODEL = str(ROOT.parent / "tools" / "piper-voices" / "en_US-lessac-medium.onnx")

_voice = None


def init():
    global _voice
    from piper import PiperVoice
    _voice = PiperVoice.load(MODEL)


def audio_name(word):
    import re
    return re.sub(r"[^a-z0-9'-]+", "-", word.lower().strip()).strip("-") + ".mp3"


def gen(word):
    target = OUT / audio_name(word)
    if target.exists() and target.stat().st_size > 1000:
        return (word, True, "skip")
    wav = target.with_suffix(".wav")
    try:
        with wave.open(str(wav), "wb") as wf:
            _voice.synthesize_wav(word, wf)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav),
                        "-codec:a", "libmp3lame", "-q:a", "4", str(target)], check=True)
        wav.unlink()
        return (word, target.stat().st_size > 1000, "")
    except Exception as e:  # noqa: BLE001
        try:
            wav.unlink(missing_ok=True)
        except Exception:
            pass
        return (word, False, str(e)[:100])


def main():
    words = [w.strip() for w in (ROOT / "scripts" / "all_words.txt").read_text(encoding="utf-8").splitlines() if w.strip()]
    OUT.mkdir(parents=True, exist_ok=True)
    done = fail = 0
    failures = []
    with Pool(2, initializer=init) as pool:
        for i, (word, ok, err) in enumerate(pool.imap_unordered(gen, words, chunksize=50)):
            if ok:
                done += 1
            else:
                fail += 1
                failures.append(f"{word}: {err}")
            if (i + 1) % 1000 == 0:
                print(f"progress {i + 1}/{len(words)} ok={done} fail={fail}", flush=True)
    print(f"DONE total={len(words)} ok={done} fail={fail}", flush=True)
    for f in failures[:50]:
        print("FAIL", f, flush=True)


if __name__ == "__main__":
    sys.exit(main())
