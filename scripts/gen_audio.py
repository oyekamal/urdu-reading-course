#!/usr/bin/env python3
"""Generate all course audio locally with an MMS-VITS Urdu model (runs on CPU). Default = sharjeel103/mms-tts-urdu-finetune (won the bake-off on isolated letters/words); set URC_TTS_MODEL to override.

Outputs assets/audio/<kind>/<id>.wav (16 kHz mono) + .mp3, and assets/audio/manifest.json.
Kinds: names (letter names), words (letter example words), syllables (CV with long vowels: با بی بو),
       aspirates, diacritics, units (unit word lists), sentences, sight, numerals.

Known limit (ponytail): the MMS vocab has NO short-vowel diacritics, so the model guesses short
vowels from spelling. Letter names and long-vowel syllables are unambiguous; short-vowel words are not.
`--verify` runs Whisper (CPU) over every clip and writes verify.json with the round-trip transcript so
a human can spot bad clips quickly; it is a smoke test, not a judge of accent.
"""
import json, os, subprocess, sys, time
import numpy as np, soundfile as sf, torch
from transformers import VitsModel, AutoTokenizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
UNITS = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
OUT = f"{ROOT}/assets/audio"
MODEL = os.environ.get("URC_TTS_MODEL", "sharjeel103/mms-tts-urdu-finetune")  # bake-off winner, research/06_tts_bakeoff.md; baseline: facebook/mms-tts-urd-script_arabic
NUMERAL_WORDS = ["صفر", "ایک", "دو", "تین", "چار", "پانچ", "چھے", "سات", "آٹھ", "نو"]


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s)[:40]


def jobs():
    for L in DATA["letters"]:
        yield "names", L["id"], L["name_ur"]
        yield "words", L["id"], L["example"][0]
        if L["role"] == "consonant" and not L["never_initial"]:
            for v, tag in (("ا", "a"), ("ی", "i"), ("و", "u")):
                yield "syllables", f"{L['id']}_{tag}", L["ch"] + v
    for dg, rom, ur, *_ in DATA["aspirates"]:
        yield "aspirates", slug(rom), ur
    for dcr in DATA["diacritics"]:
        yield "diacritics", dcr["id"], dcr["name_ur"]
        yield "diacritics", dcr["id"] + "_ex", dcr["example"][0]
    for u in UNITS:
        for i, w in enumerate(u["words"]):
            yield "units", f"u{u['n']:02d}_{i:02d}", w[0]
        for i, s in enumerate(u["sentences"]):
            yield "sentences", f"u{u['n']:02d}_{i:02d}", s[0]
    for i, w in enumerate(DATA["sight_words"]):
        yield "sight", f"{i:02d}", w
    for i, w in enumerate(NUMERAL_WORDS):
        yield "numerals", str(i), w


def main():
    verify = "--verify" in sys.argv
    torch.manual_seed(0)
    m = VitsModel.from_pretrained(MODEL).eval()
    tok = AutoTokenizer.from_pretrained(MODEL)
    sr = m.config.sampling_rate
    manifest, t0 = [], time.time()
    for kind, id_, text in jobs():
        os.makedirs(f"{OUT}/{kind}", exist_ok=True)
        wav = f"{OUT}/{kind}/{id_}.wav"
        if not os.path.exists(wav):
            ids = tok(text, return_tensors="pt")
            with torch.no_grad():
                a = m(**ids).waveform[0].numpy()
            a = np.concatenate([np.zeros(int(0.15 * sr)), a / max(1e-6, abs(a).max()) * 0.9, np.zeros(int(0.25 * sr))])
            sf.write(wav, a.astype(np.float32), sr)
            subprocess.run(["ffmpeg", "-loglevel", "quiet", "-y", "-i", wav, "-codec:a", "libmp3lame", "-q:a", "4", wav[:-4] + ".mp3"], check=True)
        manifest.append({"kind": kind, "id": id_, "text": text, "file": os.path.relpath(wav, OUT)})
    json.dump(manifest, open(f"{OUT}/manifest.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    open(f"{OUT}/MODEL.txt", "w").write(MODEL + "\n")
    print(f"{len(manifest)} clips in {time.time()-t0:.0f}s", flush=True)
    if verify:
        import whisper
        w = whisper.load_model("medium", device="cpu")
        res = []
        for j in manifest:
            r = w.transcribe(f"{OUT}/{j['file']}", language="ur", fp16=False, temperature=0)
            res.append({**j, "heard": r["text"].strip()})
            print(j["kind"], j["id"], j["text"], "->", r["text"].strip(), flush=True)
        json.dump(res, open(f"{OUT}/verify.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
