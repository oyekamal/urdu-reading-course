#!/usr/bin/env python3
"""Regenerate only the clips a listener flagged (keys like `units/u01_17`, one per line, from app/audio_check.html
"Export flags"), using a better method than a bare isolated word:

  --method carrier   (default) synthesize "یہ لفظ <word>" with the main voice and cut the word out exactly,
                     using the VITS duration predictor's own per-letter frame counts (captured by hooking
                     torch.ceil inside the forward pass; hop = 256 samples). Sentence context gives the model
                     better short vowels than an isolated word, and nothing follows the word so nothing bleeds in.
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
        m, tok = VitsModel.from_pretrained(MAIN).eval(), AutoTokenizer.from_pretrained(MAIN)
        hop = int(np.prod(m.config.upsample_rates)); cap = {}
        _ceil = torch.ceil
        def rec(x):
            y = _ceil(x); cap["dur"] = y.detach(); return y
        torch.ceil = rec
    else:
        m, tok = VitsModel.from_pretrained(LATIN).eval(), AutoTokenizer.from_pretrained(LATIN)
    for k in keys:
        j = M.get(k)
        if not j:
            print("unknown key", k); continue
        text = j["text"]
        if method == "carrier":
            enc = tok(f"یہ لفظ {text}", return_tensors="pt")
            with torch.no_grad():
                a = norm(m(**enc).waveform[0].numpy())
            dur = cap["dur"][0, 0] if cap["dur"].dim() == 3 else cap["dur"][0]
            chars = tok.convert_ids_to_tokens(enc.input_ids[0].tolist())
            sp = [i for i, c in enumerate(chars) if c == " "]
            t0 = int(dur[: sp[-1] + 1].sum().item()) * hop if sp else 0
            clip = pad(a[max(0, t0 - 480):])
            heard = f"cut at {t0/16000:.2f}s of {len(a)/16000:.2f}s"
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
