#!/usr/bin/env python3
"""design/gen/out/*.png -> mobile/public/img/*.webp (mascot 320px transparent, unit headers 800px) + img/list.json for the service worker."""
import glob, json, os
from PIL import Image
SRC = 'design/gen/out'; DST = 'mobile/public/img'; os.makedirs(DST, exist_ok=True)
out = []
for p in sorted(glob.glob(f'{SRC}/mascot_*.png')) + sorted(glob.glob(f'{SRC}/unit_*.png')):
    name = os.path.basename(p)[:-4]
    if 'test' in name: continue
    im = Image.open(p)
    if name.startswith('mascot'): im = im.convert('RGBA'); im.thumbnail((320, 320), Image.LANCZOS); im.save(f'{DST}/{name}.webp', quality=88, method=6)
    else: im = im.convert('RGB'); im.thumbnail((800, 800), Image.LANCZOS); im.save(f'{DST}/{name}.webp', quality=80, method=6)
    out.append(f'img/{name}.webp')
json.dump(out, open(f'{DST}/list.json', 'w'))
print(len(out), 'images,', sum(os.path.getsize(f'{DST}/{os.path.basename(o)}') for o in out) // 1024, 'KB')
