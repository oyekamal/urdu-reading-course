#!/usr/bin/env python3
"""Blind listening judge (Gemini hears the audio; Whisper can't judge <1 s clips).

  identify <clip> [...]            -> which letter name / syllable is spoken, chosen from the full option list; no answer key sent
  ab <target_text> <clipA> <clipB> -> order shuffled, labels stripped; returns winner + single biggest gap

Prints JSON lines. Key: GEMINI_API_KEY (env or repo .env). Model: URC_JUDGE_MODEL.
"""
import base64, json, os, random, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eleven

MODEL = os.environ.get("URC_JUDGE_MODEL", "gemini-3.1-pro-preview")
L = json.load(open(f"{eleven.ROOT}/data/letters.json", encoding="utf8"))["letters"]


def gkey():
    for line in open(f"{eleven.ROOT}/.env"):
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    return os.environ["GEMINI_API_KEY"]


def ask(parts, model=None):
    body = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model or MODEL}:generateContent?key={gkey()}",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for i in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=60))
            break
        except (TimeoutError, OSError) as e:  # 5xx / read timeouts are common on audio calls
            if i == 3:
                raise
            time.sleep(5 * (i + 1))
    txt = "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])
    return json.loads(re.search(r"\{.*\}", txt, re.S).group(0))


def audio(path):
    mime = "audio/mpeg" if path.endswith(".mp3") else "audio/wav"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(open(path, "rb").read()).decode()}}


def identify(clip):
    names = [f"{x['name_ur']} ({x['name']})" for x in L]
    prompt = ("You are a strict native Urdu-speaking primary teacher. A child will hear this clip to learn one Urdu letter name. "
              "Listen and say which ONE item is spoken, choosing from this list: " + "، ".join(names) +
              ". If it is none of them, unclear, cut off, or has extra words, say so. Reply JSON: "
              '{"heard": "<item from list or NONE>", "clear": true|false, "native": 1-5, "problem": "<short or empty>"}')
    return ask([{"text": prompt}, audio(clip)])


def check(clip, target, model=None):
    """Not blind: does the clip say exactly `target`? Used inside the generate loop to reject bad takes."""
    prompt = (f"You are a strict native Urdu-speaking teacher of 6-year-olds. This clip should say exactly «{target}» "
              "(Urdu; for a letter name, the name as a Pakistani teacher says it). Retroflex vs dental (ٹ/ت، ڈ/د، ڑ/ر), aspiration, "
              "a missing first sound, a clipped ending, or any extra word = no match. "
              "Urdu (not Arabic) rules: ص/س/ث, ط/ت, ح/ہ, ظ/ز/ذ/ض are pronounced alike and an initial ع is a light glottal onset or silent, so do not fail a clip for those. "
              'Reply JSON: {"match": true|false, "native": 1-5, "problem": "<short or empty>"}')
    return ask([{"text": prompt}, audio(clip)], model)


def ab(target, a, b):
    pair = [("x", a), ("y", b)]
    random.shuffle(pair)
    prompt = (f"You are a harsh native Urdu-speaking teacher of 6-year-olds. Both clips try to say «{target}» for a child learning to read. "
              "Pick the one a child should learn from: correct native Pakistani Urdu pronunciation first, then clarity, then a warm unhurried teacher tone, then clean start/end. "
              'Reply JSON: {"better": "1"|"2", "gap": "<the single biggest weakness of the losing clip>", "loser_ok_for_kids": true|false}')
    r = ask([{"text": prompt}, {"text": "Clip 1:"}, audio(pair[0][1]), {"text": "Clip 2:"}, audio(pair[1][1])])
    r["winner"] = pair[int(r["better"]) - 1][1]
    return r


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:] or ["-"]
    if cmd == "identify":
        with ThreadPoolExecutor(6) as ex:
            for c, r in zip(rest, ex.map(identify, rest)):
                print(json.dumps({"clip": c, **r}, ensure_ascii=False), flush=True)
    elif cmd == "ab":
        print(json.dumps(ab(*rest), ensure_ascii=False))
    else:
        sys.exit(__doc__)
