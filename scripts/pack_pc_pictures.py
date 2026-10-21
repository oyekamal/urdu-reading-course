#!/usr/bin/env python3
"""Pack Perchance pictures (design/words/pc + perchance_test) into the app: transparent webp in mobile/public/img/words/pc-<slug>.webp
and word -> id entries in data/word_img.json (rebuilt entries override the old clip-art id). Then run scripts/sync_mobile_content.sh.
  python3 scripts/pack_pc_pictures.py            # all   |   --check  report only"""
import json, os, re, sys, unicodedata
from PIL import Image
ROOT = os.path.abspath(f"{os.path.dirname(__file__)}/..")
sys.path.insert(0, f"{ROOT}/design/gen"); sys.path.insert(0, f"{ROOT}/scripts")
import gen_assets as G
from pc_prompts import P, TEST
slug = lambda r: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", r).encode("ascii", "ignore").decode().lower()) or "x"
units = json.load(open(f"{ROOT}/data/units.json"))["units"]; wi = json.load(open(f"{ROOT}/data/word_img.json"))
words = {}
for u in units:
    for k in ("words", "sight", "nonwords"):
        for w in u.get(k, []) or []:
            if isinstance(w, list) and w[0] not in words: words[w[0]] = w
byrom = {slug(w[1]): w[0] for w in words.values()}
todo = []  # (jpg path, new id, [urdu words])
for r in P:
    f = f"{ROOT}/design/words/pc/{slug(r)}.jpg"
    if os.path.exists(f) and slug(r) in byrom: todo.append((f, "pc-" + slug(r), [byrom[slug(r)]]))
for gl, name in TEST.items():
    f = f"{ROOT}/design/words/perchance_test/{name}.jpg"; urs = [ur for ur, w in words.items() if re.match(rf"^{gl}\b", w[2].lower())]
    if os.path.exists(f) and urs: todo.append((f, "pc-" + slug(name), urs))
print(len(todo), "pictures;", sum(len(t[2]) for t in todo), "words")
if "--check" in sys.argv: sys.exit()
out = f"{ROOT}/mobile/public/img/words"
for f, i, urs in todo:
    im = G.transparent(Image.open(f).convert("RGB")); bb = im.getbbox() or (0, 0) + im.size; im = im.crop(bb)
    s = 232 / max(im.size); im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    c = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); c.paste(im, ((256 - im.width) // 2, (256 - im.height) // 2), im); c.save(f"{out}/{i}.webp", quality=88)
    for ur in urs: wi[ur] = i
json.dump(wi, open(f"{ROOT}/data/word_img.json", "w"), ensure_ascii=False)
print("packed", len(todo), "-> word_img.json now", len(wi))
