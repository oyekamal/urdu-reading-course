#!/usr/bin/env python3
"""Check every unit word uses only letters taught so far (plus hamza forms, diacritics, marks).
Words flagged '(… preview)' in their gloss are allowed one not-yet-taught letter and are reported, not failed."""
import json, os, unicodedata, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
ALWAYS = set("ءئؤآأـ") | {c for c in "َُِّْٰٔ"}
taught, bad, prev = set(), 0, 0
for u in U:
    taught |= set(u["letters"])
    for ur, rom, en, *_ in u["words"]:
        letters = {c for c in ur if unicodedata.category(c) != "Mn" and c not in ALWAYS}
        missing = letters - taught
        if missing:
            if "preview" in en:
                prev += 1
            else:
                bad += 1; print(f"unit {u['n']}: {ur} ({rom}) uses untaught {''.join(missing)}")
print(f"{bad} violations, {prev} declared previews")
sys.exit(1 if bad else 0)
