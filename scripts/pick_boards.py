#!/usr/bin/env python3
"""Candidate boards for picking the best of 4: python3 scripts/pick_boards.py <cand_dir> <jobs.json> [rows=6]
Writes <cand_dir>/_pick/board_<k>.png (a row per prompt, columns A-D) and board_<k>.txt (row -> name + prompt).
Apply picks: python3 scripts/pick_boards.py apply <cand_dir> <final_dir> <picks.json>   ({"p01": "B", ...})"""
import json, os, sys, shutil
from PIL import Image, ImageDraw
if sys.argv[1] == "apply":
    _, _, cand, fin, picks = sys.argv; os.makedirs(fin, exist_ok=True); n = 0
    for name, L in json.load(open(picks)).items():
        src = f"{cand}/{name}__{'ABCD'.index(L.strip().upper()[0]) + 1}.jpg"
        if os.path.exists(src): shutil.copy(src, f"{fin}/{name}.jpg"); n += 1
    print("applied", n); sys.exit()
cand, jobs = sys.argv[1], json.load(open(sys.argv[2])); rows = int(sys.argv[3]) if len(sys.argv) > 3 else 6
names = [n for n in jobs if all(os.path.exists(f"{cand}/{n}__{k}.jpg") for k in range(1, 5))]; out = f"{cand}/_pick"; os.makedirs(out, exist_ok=True)
for s in range(0, len(names), rows):
    ch = names[s:s + rows]; B = Image.new("RGB", (4 * 270 + 30, len(ch) * 290), "white"); d = ImageDraw.Draw(B); txt = []
    for r, n in enumerate(ch):
        for k in range(4):
            B.paste(Image.open(f"{cand}/{n}__{k + 1}.jpg").resize((260, 260)), (30 + k * 270, r * 290 + 4)); d.text((36 + k * 270, r * 290 + 266), "ABCD"[k], fill="black")
        d.text((2, r * 290 + 120), str(r + 1), fill="red"); txt.append(f"row {r + 1} = {n}: {jobs[n]}")
    B.save(f"{out}/board_{s // rows:03d}.png"); open(f"{out}/board_{s // rows:03d}.txt", "w").write("\n".join(txt))
print(len(names), "complete prompts ->", (len(names) + rows - 1) // rows, "boards")
