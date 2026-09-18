#!/usr/bin/env python3
"""Apply listener picks (JSON {key: "A".."F" | "none"}) from the repair page: copy the chosen candidate wav/mp3 from
assets/audio/_repair/<kind>__<id>/ into place, record it in data/audio_overrides.json, and list the 'none' clips
(those need a human recording). Usage: python3 scripts/apply_picks.py picks.json"""
import json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/assets/audio"; OVR = f"{ROOT}/data/audio_overrides.json"
picks = json.load(open(sys.argv[1], encoding="utf8"))
if "picks" in picks: picks = picks["picks"]
M = {f"{j['kind']}/{j['id']}": j for j in json.load(open(f"{OUT}/manifest.json", encoding="utf8"))}
ovr = json.load(open(OVR, encoding="utf8")) if os.path.exists(OVR) else {}
labels = {"A": "main-alone", "B": "main-carrier", "C": "meta-alone", "D": "meta-carrier", "E": "roman-model", "F": "main-retake"}
applied, none = 0, []
for k, v in picks.items():
    if k not in M: print("unknown", k); continue
    if v == "none": none.append(k); ovr[k] = {"method": "needs-human", "text": M[k]["text"]}; continue
    src = f"{OUT}/_repair/{k.replace('/', '__')}/{v}"
    if not os.path.exists(src + ".wav"): print("missing candidate", k, v); continue
    dst = f"{OUT}/{M[k]['file'][:-4]}"
    shutil.copy(src + ".wav", dst + ".wav"); shutil.copy(src + ".mp3", dst + ".mp3")
    ovr[k] = {"method": labels[v], "text": M[k]["text"], "pick": v}; applied += 1
json.dump(ovr, open(OVR, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(f"applied {applied}; {len(none)} marked needs-human:", " ".join(none))
print("now: python3 scripts/build_app.py")
