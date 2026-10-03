#!/usr/bin/env python3
"""Check every unit word, sentence token and passage token uses only letters taught so far.
Words flagged '(… preview)' in their gloss are allowed one not-yet-taught letter and are reported, not failed (none remain since v0.11).
Madda آ and the hamza carriers ؤ أ ء are taught in unit 10 (the letter ئ), so they count as ئ: a word with آ cannot appear before unit 10."""
import json, os, unicodedata, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
ALWAYS = {"ـ"}  # tatweel
FOLD = {"آ": "ئ", "أ": "ئ", "ؤ": "ئ", "ء": "ئ"}
taught, bad, prev = set(), 0, 0
for u in U:
    taught |= set(u["letters"])
    for ur, rom, en, *_ in u["words"]:
        letters = {FOLD.get(c, c) for c in ur if unicodedata.category(c) != "Mn" and c not in ALWAYS}
        missing = letters - taught
        if missing:
            if "preview" in en:
                prev += 1
            else:
                bad += 1; print(f"unit {u['n']}: {ur} ({rom}) uses untaught {''.join(missing)}")
TEXT_OK = set("۔،؟:!۰۱۲۳۴۵۶۷۸۹ ")
taught = set()
for u in U:
    taught |= set(u["letters"])
    texts = [x[0] for x in u.get("sentences", [])] + ([u["passage"][0]] if u.get("passage") else [])
    for t in texts:
        letters = {FOLD.get(c, c) for c in t if unicodedata.category(c) != "Mn" and c not in ALWAYS and c not in TEXT_OK}
        missing = letters - taught
        if missing:
            bad += 1; print(f"unit {u['n']}: text '{t[:30]}' uses untaught {''.join(missing)}")
print(f"{bad} violations, {prev} declared previews")
sys.exit(1 if bad else 0)
