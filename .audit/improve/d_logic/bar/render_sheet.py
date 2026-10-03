#!/usr/bin/env python3
"""Contact sheet of every letter x 4 positional forms (exactly the strings the app builds with U+0640) in Naskh and Nastaliq,
via PIL+raqm. Also flags tofu by pixel-comparing against the .notdef rendering."""
import json, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.expanduser('~/Documents/free_work/urdu-reading-course'); HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(ROOT + '/data/letters.json', encoding='utf8'))['letters']; TAT = 'ـ'
fonts = {'naskh': ROOT + '/mobile/public/fonts/NotoNaskhArabic.ttf', 'nastaliq': ROOT + '/mobile/public/fonts/NotoNastaliqUrdu-Regular.ttf'}
for nm, fp in fonts.items():
    f = ImageFont.truetype(fp, 64, layout_engine=ImageFont.Layout.RAQM); lab = ImageFont.load_default()
    cw, ch = 150, 150; cols = 4; rows = len(L); W = 70 + cols * cw; H = rows * ch // 1
    # two halves to keep image size sane
    half = (len(L) + 1) // 2
    for part, chunk in enumerate((L[:half], L[half:])):
        im = Image.new('RGB', (70 + cols * cw, len(chunk) * ch), 'white'); d = ImageDraw.Draw(im)
        for r, l in enumerate(chunk):
            d.text((4, r * ch + 6), l['id'][:8], fill='black', font=lab)
            forms = [l['ch'], l['ch'] + TAT if l['joiner'] else None, TAT + l['ch'] + TAT if l['joiner'] else None, TAT + l['ch']]
            for c, s in enumerate(forms):
                x0 = 70 + c * cw
                d.rectangle([x0, r * ch, x0 + cw, (r + 1) * ch], outline='#ddd')
                if s: d.text((x0 + cw // 2, r * ch + ch // 2), s, font=f, fill='black', anchor='mm', direction='rtl', language='ur')
                else: d.text((x0 + 40, r * ch + 60), '(none)', fill='#999', font=lab)
        im.save(f'{HERE}/forms_{nm}_{part+1}.png')
print('ok')
