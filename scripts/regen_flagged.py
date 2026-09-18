#!/usr/bin/env python3
"""Regenerate only the clips a listener flagged (keys like `units/u01_17`, one per line, from app/audio_check.html
"Export flags"), using a better method than a bare isolated word:

  --method carrier   (default) synthesize "یہ <word> ہے۔" with the main voice, then cut the middle word out
                     using Whisper word timestamps. Sentence context gives the model the right short vowels
                     far more often than an isolated word does.
  --method latin     synthesize from romanised spelling with facebook/mms-tts-urd-script_latin; the roman
                     spelling carries the vowels explicitly. Needs a roman form: taken from units.json / letters.json.

Usage: python3 scripts/regen_flagged.py flags.txt [--method carrier|latin]
Every regenerated clip is recorded in data/audio_overrides.json so gen_audio.py will not overwrite it and a
future full regeneration reproduces the same choice. Then run scripts/build_app.py.
"""
import json, os, subprocess, sys, numpy as np, soundfile as sf, torch
from transformers import VitsModel, AutoTokenizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/assets/audio"
MAIN = open(f"{OUT}/MODEL.txt").read().strip() if os.path.exists(f"{OUT}/MODEL.txt") else "sharjeel103/mms-tts-urdu-finetune"
LATIN = "facebook/mms-tts-urd-script_latin"
OVR = f"{ROOT}/data/audio_overrides.json"
M = {f"{j['kind']}/{j['id']}": j for j in json.load(open(f"{OUT}/manifest.json", encoding="utf8"))}
L = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
ROMAN = {}
for u in U:
    for w in u["words"] + u["sentences"]:
        ROMAN[w[0]] = w[1]
for l in L["letters"]:
    ROMAN[l["example"][0]] = l["example"][1]
    ROMAN[l["name_ur"]] = l["name"]
ROMAN.update({a[2]: a[3] for a in L["aspirates"]})


def norm(a):
    return (a / max(1e-6, abs(a).max()) * 0.9).astype(np.float32)


def pad(a, sr=16000):
    return np.concatenate([np.zeros(int(0.15 * sr)), a, np.zeros(int(0.25 * sr))]).astype(np.float32)


def main():
    keys = [k.strip() for k in open(sys.argv[1], encoding="utf8") if k.strip()]
    method = sys.argv[sys.argv.index("--method") + 1] if "--method" in sys.argv else "carrier"
    ovr = json.load(open(OVR, encoding="utf8")) if os.path.exists(OVR) else {}
    torch.manual_seed(0)
    if method == "carrier":
        import whisper
        m, tok = VitsModel.from_pretrained(MAIN).eval(), AutoTokenizer.from_pretrained(MAIN)
        w = whisper.load_model("medium", device="cpu")
    else:
        m, tok = VitsModel.from_pretrained(LATIN).eval(), AutoTokenizer.from_pretrained(LATIN)
    for k in keys:
        j = M.get(k)
        if not j:
            print("unknown key", k); continue
        text = j["text"]
        if method == "carrier":
            ids = tok(f"یہ {text} ہے۔", return_tensors="pt")
            with torch.no_grad():
                a = norm(m(**ids).waveform[0].numpy())
            tmp = "/tmp/urc_carrier.wav"; sf.write(tmp, a, 16000)
            r = w.transcribe(tmp, language="ur", fp16=False, temperature=0, word_timestamps=True)
            ws = [x for s in r["segments"] for x in s["words"]]
            if len(ws) < 3:
                print("could not align", k, r["text"]); continue
            # middle chunk = everything between the first word's end and the last word's start
            t0, t1 = int(ws[0]["end"] * 16000), int(ws[-1]["start"] * 16000)
            clip = pad(a[max(0, t0 - 400):t1 + 400])
            heard = r["text"].strip()
        else:
            rom = ROMAN.get(text)
            if not rom:
                print("no roman form for", k, text); continue
            rom = rom.replace("ā", "aa").replace("ī", "ee").replace("ū", "oo").replace("ṭ", "t").replace("ḍ", "d").replace("ṛ", "r").replace("ṉ", "n").replace("ḥ", "h").replace("ṣ", "s").replace("ẕ", "z").replace("z̤", "z").replace("t̤", "t").replace("k͟h", "kh").replace("g͟h", "gh").replace("s̱", "s").replace("ʻ", "").replace("ʾ", "")
            ids = tok(rom, return_tensors="pt")
            with torch.no_grad():
                clip = pad(norm(m(**ids).waveform[0].numpy()))
            heard = rom
        wav = f"{OUT}/{j['file']}"
        sf.write(wav, clip, 16000)
        subprocess.run(["ffmpeg", "-loglevel", "quiet", "-y", "-i", wav, "-codec:a", "libmp3lame", "-q:a", "4", wav[:-4] + ".mp3"], check=True)
        ovr[k] = {"method": method, "text": text, "heard": heard}
        print(k, text, "->", method, "|", heard)
    json.dump(ovr, open(OVR, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{len(keys)} clips regenerated; overrides saved to data/audio_overrides.json. Now run scripts/build_app.py")


if __name__ == "__main__":
    main()
