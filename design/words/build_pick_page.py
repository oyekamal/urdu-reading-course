#!/usr/bin/env python3
"""cand_*.json (+ optional fixes_*.json overrides) -> design/words/pick_page.html, ready to publish as an Artifact.
Every candidate picture is rendered once to a 128px WebP data URI and embedded (the page cannot fetch anything else)."""
import base64, glob, io, json, os, sys
import cairosvg
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from find_pic import pic_path

words = []
for f in sorted(glob.glob(f'{HERE}/cand_*.json')): words += json.load(open(f))
fix = {}
for f in sorted(glob.glob(f'{HERE}/fix_*.json')):  # critic rounds: {id: {"cands": [...], "fit": ..., "concept": ...}}
    for k, v in json.load(open(f)).items(): fix.setdefault(k, {}).update(v)
for w in words: w.update(fix.get(str(w['id']), {}))
words.sort(key=lambda w: w['id'])
unit = {c['id']: c['unit'] for c in json.load(open(f'{HERE}/../../data/word_catalog.json'))}
imgs = {}
for w in words:
    w['unit'] = unit[w['id']]; keep = []
    for k in w['cands']:
        if k in imgs: keep.append(k); continue
        try:
            png = cairosvg.svg2png(url=pic_path(k), output_width=128, output_height=128)
            b = io.BytesIO(); Image.open(io.BytesIO(png)).convert('RGBA').save(b, 'WEBP', quality=82, method=6)
            imgs[k] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(); keep.append(k)
        except Exception as e: print('skip', w['id'], k, e)
    w['cands'] = keep
tpl = open(f'{HERE}/pick_template.html').read()
page = tpl.replace('__DATA__', json.dumps([{k: w.get(k, '') for k in ('id', 'ur', 'rom', 'en', 'unit', 'concept', 'fit', 'cands', 'draw')} for w in words], ensure_ascii=False).replace('</', '<\\/')).replace('__IMGS__', json.dumps(imgs))
open(f'{HERE}/pick_page.html', 'w').write(page)
print(len(words), 'words,', len(imgs), 'pictures,', len(page) // 1024, 'KB')
