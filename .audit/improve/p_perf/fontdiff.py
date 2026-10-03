# Before/after glyph diff for the font subsets: every letter in 4 positions (+ every diacritic), all unit words/sentences,
# Naskh + Nastaliq, regular + bold. Output images go to /tmp/claude-1000/p_perf/fd.
# python3 fontdiff.py   -> per font/weight: number of strings that differ pixel-wise (expect 0)
import json, subprocess, time, shutil, pathlib, io, sys
from h import *
from PIL import Image, ImageChops
Image.MAX_IMAGE_PIXELS = None
R = pathlib.Path('/home/oye/Documents/free_work/urdu-reading-course'); W = pathlib.Path('/tmp/claude-1000/p_perf/fd'); W.mkdir(parents=True, exist_ok=True)
shutil.copy(R/'assets/fonts/NotoNaskhArabic.ttf', W/'old_naskh.ttf'); shutil.copy(R/'assets/fonts/NotoNastaliqUrdu-Regular.ttf', W/'old_nastaliq.ttf')
shutil.copy(R/'mobile/public/fonts/NotoNaskhArabic-ur.woff2', W/'new_naskh.woff2'); shutil.copy(R/'mobile/public/fonts/NotoNastaliqUrdu-ur.woff2', W/'new_nastaliq.woff2')
L = json.load(open(R/'mobile/public/data/letters.json', encoding='utf8')); U = json.load(open(R/'mobile/public/data/units.json', encoding='utf8'))
B = 'ب'; strings = []
for l in L['letters']:
    c = l['ch']; strings += [c, c + B, B + c + B, B + c]
dia = [d['ch'] for d in L['diacritics']]
for l in L['letters']:
    for d in dia: strings += [l['ch'] + d + B, B + l['ch'] + d]
def walk(o):
    if isinstance(o, str):
        if any('؀' <= ch <= 'ۿ' for ch in o): yield o
    elif isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
for o in (U, L): strings += list(walk(o))
seen = set(); strings = [s for s in strings if not (s in seen or seen.add(s))]
print('strings', len(strings))
def page(kind, fam, weight):
    src = f"url(old_{fam}.ttf)" if kind == 'old' else f"url(new_{fam}.woff2) format('woff2')"
    rows = ''.join(f'<div class="r">{s}</div>' for s in strings)
    h = '78px' if fam == 'nastaliq' else '56px'
    return f"""<!doctype html><meta charset=utf8><style>@font-face{{font-family:T;src:{src}}}
body{{margin:0;background:#fff}}.r{{font-family:T;direction:rtl;font-size:34px;line-height:{h};height:{h};width:600px;font-weight:{weight};overflow:hidden;white-space:nowrap;box-sizing:border-box;padding-right:10px}}</style>{rows}"""
srv = subprocess.Popen(['python3', '-m', 'http.server', '5399', '--directory', str(W)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
total_bad = 0
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        for fam in ('naskh', 'nastaliq'):
            for weight in (400, 700):
                imgs = {}
                for kind in ('old', 'new'):
                    (W/f'{kind}_{fam}_{weight}.html').write_text(page(kind, fam, weight), encoding='utf8')
                    pg = b.new_page(viewport={'width': 600, 'height': 800}, device_scale_factor=2); pg.goto(f'http://localhost:5399/{kind}_{fam}_{weight}.html'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(500)
                    st = pg.evaluate("[...document.fonts].map(f=>f.status)")
                    imgs[kind] = Image.open(io.BytesIO(pg.screenshot(full_page=True))).convert('L'); pg.close()
                    if st != ['loaded']: print('  font status', kind, st)
                rh = (78 if fam == 'nastaliq' else 56) * 2; a, c = imgs['old'], imgs['new']
                bad = [i for i in range(len(strings)) if ImageChops.difference(a.crop((0, i*rh, a.width, (i+1)*rh)), c.crop((0, i*rh, c.width, (i+1)*rh))).getbbox()]
                total_bad += len(bad)
                print(f'{fam} {weight}: {len(strings)} strings, {len(bad)} differ', [strings[i] for i in bad[:6]])
                for k in range(min(3, len(bad))):
                    a.crop((0, bad[k]*rh, a.width, (bad[k]+1)*rh)).save(W/f'diff_{fam}_{weight}_{k}_old.png'); c.crop((0, bad[k]*rh, c.width, (bad[k]+1)*rh)).save(W/f'diff_{fam}_{weight}_{k}_new.png')
        b.close()
finally: srv.terminate()
print('TOTAL DIFFERING', total_bad)
