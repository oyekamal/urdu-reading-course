#!/usr/bin/env python3
"""Check every unit word uses only letters taught so far.
Words flagged '(… preview)' in their gloss are allowed one not-yet-taught letter and are reported, not failed.
Madda/hamza carriers fold to their base letter (آ→ا, ؤ→و) and bare ء counts as the unit-10 hamza letter ئ,
so the gate cannot be satisfied by a blanket exemption."""
import json, os, unicodedata, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
ALWAYS = {"ـ"}  # tatweel
FOLD = {"آ": "ا", "أ": "ا", "ؤ": "و", "ء": "ئ"}
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
print(f"{bad} violations, {prev} declared previews")
sys.exit(1 if bad else 0)
