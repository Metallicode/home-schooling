#!/usr/bin/env python3
"""Pre-record audio for first_reading.html with edge-tts.

Reads the predefinedSentences array straight out of first_reading.html and
writes one mp3 per sentence (s-<slug>.mp3, e.g. s-the-cat-sat.mp3) and one per unique word
(w-<word>.mp3, lowercase, letters only) into this folder. Existing files are
skipped, so re-run after adding sentences to fill in only what's new.

    python3 sounds/first_reading/generate.py
"""
import re
import subprocess
from pathlib import Path

VOICE = "en-US-JennyNeural"
HERE = Path(__file__).resolve().parent
PAGE = HERE.parent.parent / "first_reading.html"

src = PAGE.read_text()
block = re.search(r"predefinedSentences\s*=\s*\[(.*?)\];", src, re.S).group(1)
sentences = re.findall(r'"([^"]+)"', block)

words = sorted({re.sub(r"[^a-z]", "", w.lower()) for s in sentences for w in s.split()} - {""})

slug = lambda t: re.sub(r"[^a-z]+", "-", t.lower()).strip("-")
jobs = [(f"s-{slug(s)}.mp3", s) for s in sentences]
jobs += [(f"w-{w}.mp3", w) for w in words]

for name, text in jobs:
    out = HERE / name
    if out.exists():
        continue
    print(name, "<-", text)
    subprocess.run(["edge-tts", "--voice", VOICE, "--text", text, "--write-media", str(out)], check=True)

print(f"{len(sentences)} sentences, {len(words)} words")
