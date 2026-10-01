#!/usr/bin/env python3
"""raw Gemini parts (white bg) -> transparent, cropped, downscaled parts/<part>.png used by make_marko.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gen"))
from gen_assets import transparent
from PIL import Image
HERE = Path(__file__).parent / "parts"
SIZE = {"head": 330, "body": 250, "arm": 112}   # target height in 512-canvas px (x2 for crispness)
for n, h in SIZE.items():
    im = transparent(Image.open(HERE / f"raw_{n}.png").convert("RGB"))
    im = im.crop(im.getchannel("A").getbbox())
    R = 1.5; w = round(im.width * R * h / im.height); im = im.resize((w, round(R * h)), Image.LANCZOS)
    im.save(HERE / f"{n}_full.png"); print(n, im.size, (HERE / f"{n}_full.png").stat().st_size // 1024, "KB")

# --- head: paint the raster eyes and mouth out with the mask cream so vector eyes/mouth (blink, look, talk) replace them
import numpy as np
from PIL import ImageDraw
head = Image.open(HERE / "head_full.png").convert("RGBA"); a = np.array(head)
cream = tuple(int(v) for v in np.median(a[250:270, 230:270, :3].reshape(-1, 3), axis=0)) + (255,)
d = ImageDraw.Draw(head)
EYES = [(174, 291), (325, 291)]; ER = 31
for x, y in EYES: d.ellipse((x - ER, y - ER, x + ER, y + ER), fill=cream)
d.rectangle((203, 356, 299, 390), fill=cream)          # philtrum + smile (nose V stays)
head.save(HERE / "head_clean.png")
print("cream", cream)
for n in ("head_clean", "body_full", "arm_full"):
    im = Image.open(HERE / f"{n}.png").convert("RGBA")
    q = im.quantize(48, method=Image.Quantize.FASTOCTREE)
    out = HERE / (n.split("_")[0] + ".png"); q.save(out, optimize=True); print(out.name, out.stat().st_size // 1024, "KB")

# --- body: Gemini drew a blank head silhouette on top of the torso; keep only the torso (below that blob's lower outline,
# outline included) so the real head sits on real shoulders
body = Image.open(HERE / "body_full.png").convert("RGBA"); b = np.array(body); Hh, Ww = b.shape[:2]
dark = (b[..., 0] < 80) & (b[..., 2] < 130) & (b[..., 3] > 150)
for x in range(Ww):
    cut = 200
    y = 120
    while y < 200:                       # last dark run in the band that has torso turquoise right below it
        if dark[y, x]:
            y1 = y
            while y1 < Hh - 1 and dark[y1, x]: y1 += 1
            px = b[y1, x]
            if px[3] > 150 and ((px[1] > 110 and px[0] < 90) or px[0] > 200): cut = y
            y = y1
        y += 1
    b[:cut, x, 3] = 0
from scipy import ndimage
lab, n = ndimage.label(b[..., 3] > 0); keep = np.argmax(np.bincount(lab.ravel())[1:]) + 1
b[lab != keep, 3] = 0
torso = Image.fromarray(b); torso = torso.crop(torso.getchannel("A").getbbox())
torso.save(HERE / "torso_full.png")
q = torso.quantize(48, method=Image.Quantize.FASTOCTREE); q.save(HERE / "body.png", optimize=True)
print("torso", torso.size, (HERE / "body.png").stat().st_size // 1024, "KB")
