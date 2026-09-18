#!/usr/bin/env python3
"""Round-1 fact-check fixes (see .audit/factcheck_round1.md). Idempotent. Removes stale audio for changed items."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = f"{ROOT}/data/units.json"; d = json.load(open(p, encoding="utf8"))
rep = {"ابے": ["تالاب", "tālāb", "pond", "تالاب"], "انا": ["نانا", "nānā", "maternal grandfather", "نانا"],
       "بلا": ["مالا", "mālā", "garland", "مالا"], "ٹال": ["ٹکٹ", "ṭikaṭ", "ticket", "ٹِکَٹ"], "کہّ": ["اچّھا", "achchhā", "good", "اَچّھا"]}
stale = []
for u in d["units"]:
    for i, w in enumerate(u["words"]):
        if w[0] in rep:
            u["words"][i] = rep[w[0]]; stale.append(f"assets/audio/units/u{u['n']:02d}_{i:02d}")
json.dump(d, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
p = f"{ROOT}/data/letters.json"; L = json.load(open(p, encoding="utf8"))
for l in L["letters"]:
    if l["id"] == "hamza" and l["ch"] != "ئ":
        l.update({"ch": "ئ", "cp": "U+0626", "name_ur": "ہمزہ", "name": "hamza", "joiner": True,
                  "hint": "a tiny break between two vowels (کوئی ko-ī). It rides on ی as ئ, on و as ؤ, or stands alone as ء; آ is alif with a madd, long ā at the start of a word (آم ām)"})
        stale += ["assets/audio/words/hamza", "assets/audio/names/hamza"]
    if l["id"] == "mim" and l["example"][0] != "مکان":
        l["example"] = ["مکان", "makān", "house"]; stale.append("assets/audio/words/mim")
    if l["id"] == "he": l["name_ur"] = "ہے / گول ہے"
for x in L["diacritics"]:
    if x["id"] == "jazm" and x["example"][0] != "سَبْزی":
        x["example"] = ["سَبْزی", "sabzī", "vegetable"]; stale.append("assets/audio/diacritics/jazm_ex")
L["long_vowels"] = [["ا", "ā", "کام kām"], ["آ", "ā (word start)", "آم ām"], ["ی", "ī", "تین tīn"], ["و", "ū", "جوتا jūtā"], ["و", "o", "روٹی roṭī"], ["ے", "e", "لے le"], ["ے", "ai", "ہے hai"], ["و", "au", "اور aur"], ["ی", "ai (mid-word)", "میں maiṉ"]]
L["_meta"]["aspirates_note"] = "11 of the 15 possible digraphs; رھ لھ مھ نھ are rare and left to unit 11 reading practice"
json.dump(L, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
for s in stale:
    for ext in (".wav", ".mp3"):
        try: os.remove(f"{ROOT}/{s}{ext}")
        except FileNotFoundError: pass
print("stale removed:", stale)
