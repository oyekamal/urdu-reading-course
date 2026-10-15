#!/usr/bin/env python3
"""design/words/picks_final.json ({word id: 'om:1F415' | 'tw:..' | 'mb:..' | 'none' | 'draw'}) -> mobile/public/img/words/<set>-<name>.webp
(256px, transparent; hand-drawn art/<id>.svg for 'draw' picks) + data/word_img.json {urdu word: file stem}. Pictures come from OpenMoji / Twemoji / Mulberry (see CREDITS in the app).
Picked by Kamal in the Qaida Picture Picker; critic-reviewed in design/words/fix_*.json. Re-run after changing picks."""
import io, json, os, sys, glob
import cairosvg
from PIL import Image
sys.path.insert(0, 'design/words')
from find_pic import pic_path
DST = 'mobile/public/img/words'; os.makedirs(DST, exist_ok=True)
picks = json.load(open('design/words/picks_final.json')); cat = {c['id']: c for c in json.load(open('data/word_catalog.json'))}
# 'draw' picks use the hand-drawn SVG design/words/art/<id>.svg when it exists and was not dropped (art/rejected.txt, one id per line)
rej = set(open('design/words/art/rejected.txt').read().split()) if os.path.exists('design/words/art/rejected.txt') else set()
# design/words/dropped.txt: ids whose picked picture was pulled after in-app QA (abstract diagrams a child cannot decode)
drop = set(open('design/words/dropped.txt').read().split()) if os.path.exists('design/words/dropped.txt') else set()
m, stems = {}, set()
for i, k in picks.items():
    if int(i) not in cat or k == 'none' or i in drop: continue
    if k == 'draw':
        if i in rej or not os.path.exists(f'design/words/art/{i}.svg'): continue
        k = f'art:{i}'
    stem = k.replace(':', '-').replace(',', '').replace('_', '-'); m[cat[int(i)]['ur']] = stem; stems.add((stem, k))
svg = lambda k: f'design/words/art/{k[4:]}.svg' if k.startswith('art:') else pic_path(k)
for stem, k in stems:
    if os.path.exists(f'{DST}/{stem}.webp') and not stem.startswith('art-'): continue  # emoji/pictogram files never change; art is always re-rendered
    im = Image.open(io.BytesIO(cairosvg.svg2png(url=svg(k), output_width=512))).convert('RGBA'); im.thumbnail((256, 256), Image.LANCZOS)
    im.save(f'{DST}/{stem}.webp', quality=88, method=6)
for f in glob.glob(f'{DST}/*.webp'):
    if os.path.basename(f)[:-5] not in {s for s, _ in stems}: os.remove(f)
for out in ('data/word_img.json', 'mobile/public/data/word_img.json'): json.dump(m, open(out, 'w'), ensure_ascii=False)  # data/ is tracked; sync_mobile_content.sh copies it into the bundle
print(len(m), 'words,', len(stems), 'files,', sum(os.path.getsize(f) for f in glob.glob(f'{DST}/*.webp')) // 1024, 'KB')
