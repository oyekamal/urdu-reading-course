#!/usr/bin/env python3
"""Smoke-test the generated audio with Whisper (CPU). Whisper hallucinates on <1 s clips, so clips of one
kind are concatenated into ~15 s chunks with 0.7 s gaps and the chunk transcript is compared with the
expected text (character-level match after stripping vowel marks). Writes assets/audio/verify.json:
per kind -> chunks -> {ids, expected, heard, char_match}. Human blind listening (app/audio_check.html) is the real judge."""
import json, os, difflib, re, numpy as np, soundfile as sf, whisper
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = f"{ROOT}/assets/audio"
M = json.load(open(f"{OUT}/manifest.json", encoding="utf8"))
w = whisper.load_model("medium", device="cpu"); SR = 16000; GAP = np.zeros(int(0.7 * SR), dtype=np.float32)
norm = lambda s: re.sub(r"[ً-ْٰٔ٘\s۔،؟!.]", "", s)
res = {}
for kind in sorted({j["kind"] for j in M}):
    items = [j for j in M if j["kind"] == kind]; chunks = []
    for i in range(0, len(items), 12):
        grp = items[i:i + 12]
        audio = np.concatenate([np.concatenate([sf.read(f"{OUT}/{j['file']}")[0].astype(np.float32), GAP]) for j in grp])
        sf.write("/tmp/urc_chunk.wav", audio, SR)
        heard = w.transcribe("/tmp/urc_chunk.wav", language="ur", fp16=False, temperature=0)["text"].strip()
        exp = " ".join(j["text"] for j in grp)
        ratio = difflib.SequenceMatcher(None, norm(exp), norm(heard)).ratio()
        chunks.append({"ids": [j["id"] for j in grp], "expected": exp, "heard": heard, "char_match": round(ratio, 2)})
        print(kind, i, round(ratio, 2), "|", exp[:60], "->", heard[:60], flush=True)
    res[kind] = chunks
json.dump(res, open(f"{OUT}/verify.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
allr = [c["char_match"] for k in res.values() for c in k]; print("mean char match", round(sum(allr) / len(allr), 2))
