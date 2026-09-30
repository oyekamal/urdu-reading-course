#!/usr/bin/env python3
"""design/gen/out/*.png -> mobile/public/img/*.webp (mascot 320px transparent, unit headers 800px) + img/list.json for the service worker."""
import glob, json, os
from PIL import Image, ImageDraw
SRC = 'design/gen/out'; DST = 'mobile/public/img'; os.makedirs(DST, exist_ok=True)
out = []
for p in sorted(glob.glob(f'{SRC}/mascot_*.png')) + sorted(glob.glob(f'{SRC}/unit_*.png')) + sorted(glob.glob(f'{SRC}/scene_*.png')):
    name = os.path.basename(p)[:-4]
    if 'test' in name: continue
    im = Image.open(p)
    if name.startswith('mascot'): im = im.convert('RGBA'); im.thumbnail((320, 320), Image.LANCZOS); im.save(f'{DST}/{name}.webp', quality=88, method=6)
    elif name.startswith('scene'): im = im.convert('RGB'); im.thumbnail((1000, 1000), Image.LANCZOS); im.save(f'{DST}/{name}.webp', quality=80, method=6)
    else:  # unit art: white paper -> transparent (flood from the edges, so white inside the drawing stays), trimmed to the drawing
        im = im.convert('RGBA'); w, h = im.size
        for xy in [(x, y) for x in range(0, w, 16) for y in (0, h - 1)] + [(x, y) for y in range(0, h, 16) for x in (0, w - 1)]:
            if im.getpixel(xy)[3] and min(im.getpixel(xy)[:3]) > 235: ImageDraw.floodfill(im, xy, (255, 255, 255, 0), thresh=40)
        box = im.getbbox(); pad = 12; im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(w, box[2] + pad), min(h, box[3] + pad)))
        im.thumbnail((600, 600), Image.LANCZOS); im.save(f'{DST}/{name}.webp', quality=86, method=6)
    out.append(f'img/{name}.webp')
json.dump(out, open(f'{DST}/list.json', 'w'))
print(len(out), 'images,', sum(os.path.getsize(f'{DST}/{os.path.basename(o)}') for o in out) // 1024, 'KB')
