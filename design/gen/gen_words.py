#!/usr/bin/env python3
"""One Marko-hand picture per word-image id (data/word_img.json), via Gemini in the shared STYLE.
  python3 gen_words.py pilot            # 12 sample ids -> design/words/gen/
  python3 gen_words.py all [workers]    # every id not yet generated (resumable)
Output: design/words/gen/<id>.png (transparent, 320px). Review with design/words/gen/sheet.png."""
import json, os, sys, concurrent.futures as cf, io
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_assets as G
ROOT = os.path.abspath(f"{G.HERE}/../.."); GEN = f"{ROOT}/design/words/gen"; os.makedirs(GEN, exist_ok=True)
wi = json.load(open(f"{ROOT}/data/word_img.json")); units = json.load(open(f"{ROOT}/data/units.json"))["units"]
en = {}
for u in units:
    for k in ("words", "sight", "nonwords"):
        for w in u.get(k, []) or []:
            if isinstance(w, list) and len(w) > 2: en.setdefault(w[0], w[2])
concept = {}
for ur, i in wi.items(): concept.setdefault(i, []).append(en.get(ur, ""))
def gloss(i):
    g = [x for x in concept[i] if x]; g = g[0] if g else i
    return g.split("(")[0].split("/")[0].strip()
STYLE = G.STYLE + " Style match: the friendly markhor mascot Marko. Square image, one single clear subject, no border, no frame, no background scenery."
def one(i):
    out = f"{GEN}/{i}.png"
    if os.path.exists(out): return i, "skip"
    try:
        raw = G.call(f'Draw one simple, instantly recognisable picture meaning "{gloss(i)}" for a 5-year-old learning to read. Show the meaning, not a written word.', style=STYLE)
        im = G.transparent(Image.open(io.BytesIO(raw)).convert("RGB")); bb = im.getbbox() or (0, 0) + im.size; im = im.crop(bb)
        s = 280 / max(im.size); im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        c = Image.new("RGBA", (320, 320), (0, 0, 0, 0)); c.paste(im, ((320 - im.width) // 2, (320 - im.height) // 2), im); c.save(out); return i, "ok"
    except Exception as e: return i, f"ERR {str(e)[:80]}"
def sheet(ids, path):
    ids = [i for i in ids if os.path.exists(f"{GEN}/{i}.png")]; cols = 6; rows = (len(ids) + cols - 1) // cols
    S = Image.new("RGB", (cols * 200, rows * 220), "#EEF6F4")
    from PIL import ImageDraw; d = ImageDraw.Draw(S)
    for n, i in enumerate(ids):
        im = Image.open(f"{GEN}/{i}.png").resize((180, 180)); S.paste(im, ((n % cols) * 200 + 10, (n // cols) * 220 + 4), im); d.text(((n % cols) * 200 + 10, (n // cols) * 220 + 190), f"{i} {gloss(i)}"[:30], fill="black")
    S.save(path)
if __name__ == "__main__":
    mode = sys.argv[1]; ids = sorted(concept)
    if mode == "pilot":
        import random; random.seed(3); ids = random.sample(ids, 12)
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with cf.ThreadPoolExecutor(workers) as ex:
        for i, r in ex.map(one, ids): print(i, gloss(i), r, flush=True)
    sheet(ids, f"{GEN}/sheet_{mode}.png")
