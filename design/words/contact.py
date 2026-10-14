#!/usr/bin/env python3
"""Review images: python3 contact.py <chunk 1-10> <part 1-8> -> /tmp/contact_<chunk>_<part>.png (13 words per image; candidate number + id under each picture).
Uses cand_NN.json plus any fix_NN.json already applied."""
import io, json, os, sys, cairosvg
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from find_pic import pic_path
ch, part = int(sys.argv[1]), int(sys.argv[2]); out = sys.argv[3] if len(sys.argv) > 3 else f'/tmp/contact_{ch:02d}_{part}.png'
words = json.load(open(f'{HERE}/cand_{ch:02d}.json'))
fx = f'{HERE}/fix_{ch:02d}.json'; fix = json.load(open(fx)) if os.path.exists(fx) else {}
for w in words: w.update(fix.get(str(w['id']), {}))
rows = words[(part - 1) * 13: part * 13]
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15); FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
S = 112; RH = S + 34; W = 420 + 4 * (S + 14); im = Image.new('RGB', (W, RH * max(1, len(rows))), 'white'); d = ImageDraw.Draw(im)
for r, w in enumerate(rows):
    y = r * RH; d.line((0, y + RH - 1, W, y + RH - 1), fill='#ccc')
    d.text((8, y + 8), f"#{w['id']}  {w['rom']}  =  {w['en']}", fill='black', font=FB)
    d.text((8, y + 36), f"show: {w['concept']}"[:60], fill='#333', font=F); d.text((8, y + 60), f"fit: {w['fit']}", fill='#555', font=F)
    for i, k in enumerate(w['cands'][:4]):
        try: p = Image.open(io.BytesIO(cairosvg.svg2png(url=pic_path(k), output_width=S, output_height=S))).convert('RGBA')
        except Exception: continue
        x = 420 + i * (S + 14); im.paste(p, (x, y + 4), p); d.text((x, y + S + 6), f"{i+1}:{k}"[:20], fill='#006', font=F)
im.save(out)
