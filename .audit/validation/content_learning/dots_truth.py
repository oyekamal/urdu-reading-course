#!/usr/bin/env python3
"""Verify the DOTS table in content.js (used for wrong-answer hints 'Count the dots: X has two') against the font's own glyph decomposition
(Noto Naskh Arabic and Noto Nastaliq Urdu via HarfBuzz), for all letters and all 4 positional forms."""
import json, os, re, uharfbuzz as hb
ROOT = os.path.expanduser('~/Documents/free_work/urdu-reading-course')
L = json.load(open(ROOT + '/data/letters.json', encoding='utf8'))['letters']
src = open(ROOT + '/mobile/src/content.js', encoding='utf8').read()
DOTS = {k: int(v) for k, v in re.findall(r"'(.)': (\d)", re.search(r"export const DOTS = \{(.*?)\}", src, re.S).group(1))}
def font(fn): return hb.Font(hb.Face(hb.Blob.from_file_path(f'{ROOT}/mobile/public/fonts/{fn}')))
def shape(f, t):
    b = hb.Buffer(); b.add_str(t); b.guess_segment_properties(); hb.shape(f, b, {}); return [f.glyph_to_string(i.codepoint) for i in b.glyph_infos]
def count(names):
    n = 0; tah = False
    for g in names:
        gl = g.lower()
        if 'threedots' in gl: n += 3
        elif 'twodots' in gl: n += 2
        elif 'dotbelow' in gl or 'dotabove' in gl or re.search(r'onedot', gl): n += 1
        if 'tah' in gl and 'above' in gl: tah = True
    return n, tah
TAT = 'ـ'; out = {}; bad = []
for nm, fn in (('naskh', 'NotoNaskhArabic.ttf'), ('nastaliq', 'NotoNastaliqUrdu-Regular.ttf')):
    f = font(fn)
    for l in L:
        c = l['ch']; forms = {'isolated': c, 'final': TAT + c}
        if l['joiner']: forms.update({'initial': c + TAT, 'medial': TAT + c + TAT})
        counts = {}
        for pos, s in forms.items():
            n, tah = count(shape(f, s)); counts[pos] = (n, 'tah' if tah else '')
        out.setdefault(c, {})[nm] = counts
for c, d in out.items():
    truth = {pos: v[0] for pos, v in d['naskh'].items()}
    allsame = len(set(truth.values())) == 1
    app = DOTS.get(c, 0)
    if app not in truth.values() or not allsame:
        bad.append((c, 'app DOTS=%d' % app, {k: v for k, v in d['naskh'].items()}))
    elif app != list(truth.values())[0]:
        bad.append((c, 'app DOTS=%d' % app, d['naskh']))
tah = [c for c, d in out.items() if any(v[1] for v in d['naskh'].values())]
print('letters checked', len(out)); print('letters whose glyph carries a small TAH (not a dot):', tah)
print('DOTS table vs font:'); [print('  ', b) for b in bad]
json.dump({'dots_vs_font': bad, 'tah_letters': tah, 'DOTS': DOTS}, open('dots_truth.json', 'w'), ensure_ascii=False, indent=1)
