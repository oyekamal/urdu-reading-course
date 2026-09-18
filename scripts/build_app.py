#!/usr/bin/env python3
"""Assemble app/index.html from app/template.html + data, and app/audio.json (base64 mp3 map).
Audio is shipped as one JSON file so the page can be published with a single supporting file."""
import base64, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))
M = json.load(open(f"{ROOT}/assets/audio/manifest.json", encoding="utf8"))
V = {}
try:
    V = {f"{v['kind']}/{v['id']}": v["heard"] for v in json.load(open(f"{ROOT}/assets/audio/verify.json", encoding="utf8"))}
except FileNotFoundError:
    pass
audio = {}
for j in M:
    p = f"{ROOT}/assets/audio/{j['file'][:-4]}.mp3"
    audio[f"{j['kind']}/{j['id']}"] = "data:audio/mpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()
json.dump(audio, open(f"{ROOT}/app/audio.json", "w"))
D.pop("_meta", None); U.pop("_meta", None)
data = json.dumps({"letters": D, "units": U["units"], "verify": V}, ensure_ascii=False)
tpl = open(f"{ROOT}/app/template.html", encoding="utf8").read()
open(f"{ROOT}/app/index.html", "w", encoding="utf8").write(tpl.replace("/*__DATA__*/null", data))
print("index.html", os.path.getsize(f"{ROOT}/app/index.html") // 1024, "KB; audio.json", os.path.getsize(f"{ROOT}/app/audio.json") // 1024, "KB;", len(audio), "clips")
