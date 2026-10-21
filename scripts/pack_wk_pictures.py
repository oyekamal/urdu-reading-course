#!/usr/bin/env python3
"""design/words/wk_final/w<N>_<slug>.jpg (N = row in design/words/weak_words.json) -> mobile/public/img/words/pc-w<N>.webp (transparent, 256px)
and data/word_img.json[urdu word] = 'pc-w<N>'. Old pictures no longer referenced by any word are deleted. Run AFTER pack_pc_pictures.py."""
import json, os, re, sys, glob
from PIL import Image
ROOT = os.path.abspath(f"{os.path.dirname(__file__)}/..")
sys.path.insert(0, f"{ROOT}/design/gen"); import gen_assets as G
weak = {w["n"]: w for w in json.load(open(f"{ROOT}/design/words/weak_words.json"))}
wi = json.load(open(f"{ROOT}/data/word_img.json")); out = f"{ROOT}/mobile/public/img/words"; n = 0
for f in sorted(glob.glob(f"{ROOT}/design/words/wk_final/w*.jpg")):
    num = int(re.match(r"w(\d+)_", os.path.basename(f)).group(1))
    if num not in weak: continue
    im = G.transparent(Image.open(f).convert("RGB")); bb = im.getbbox() or (0, 0) + im.size; im = im.crop(bb)
    s = 232 / max(im.size); im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    c = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); c.paste(im, ((256 - im.width) // 2, (256 - im.height) // 2), im); c.save(f"{out}/pc-w{num}.webp", quality=88)
    wi[weak[num]["ur"]] = f"pc-w{num}"; n += 1
json.dump(wi, open(f"{ROOT}/data/word_img.json", "w"), ensure_ascii=False)
used = set(wi.values()); gone = 0
for f in glob.glob(f"{out}/*.webp"):
    if os.path.basename(f)[:-5] not in used: os.remove(f); gone += 1
print("packed", n, "| words with picture", len(wi), "| removed unreferenced old files", gone)
