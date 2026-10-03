#!/usr/bin/env python3
"""Build the printable practice sheets (PDF) for the Urdu reading course.

Reads data/letters.json + data/units.json at run time (new words/letters flow in automatically), renders HTML
in Chromium via Playwright page.pdf() (correct Urdu shaping), writes mobile/public/pdf/*.pdf and
mobile/public/pdf/index.json (the manifest the app's Practice screen reads).

    python3 scripts/build_pdfs.py              # everything
    python3 scripts/build_pdfs.py --only u01   # ids starting with u01
    python3 scripts/build_pdfs.py --png /tmp/x # also rasterise page 1.. of every PDF at 60 dpi (for review)

Design rules: A4 portrait, white page, thin grey rules, one accent (prints dark grey), embedded fonts,
body first / dots last, answer keys not on the child's face. Everything is original; no worksheet is copied.
"""
import argparse, asyncio, base64, glob, html, json, os, random, re, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / 'scripts' / 'pdf_templates'
OUT = ROOT / 'mobile' / 'public' / 'pdf'
CACHE = TPL / '.cache'
FONTS = ROOT / 'assets' / 'fonts'
IMG = ROOT / 'mobile' / 'public' / 'img'

L = json.load(open(ROOT / 'data/letters.json'))
U = json.load(open(ROOT / 'data/units.json'))['units']
LET = L['letters']
BY = {x['ch']: x for x in LET}
TAT = 'ـ'

# ---- stroke hints and dot counts: read from the app's own source so PDF and app never disagree ------------------
_src = (ROOT / 'mobile/src/content.js').read_text(encoding='utf8')
STROKE = dict(re.findall(r"(\w+):\s*'([^']*)'", re.search(r'export const STROKE = \{(.*?)\};', _src, re.S).group(1)))
DOTS = {k: int(v) for k, v in re.findall(r"'(.)':\s*(\d)", re.search(r'export const DOTS = \{(.*?)\};', _src, re.S).group(1))}
DEFAULT_HINT = 'body first in one stroke, right to left; dots last'


TAH = set('ٹڈڑ')   # these carry a small tah (ط) sign, not dots
HINT_FIX = {'ط': 'small loop first, then the tall upright stroke', 'ظ': 'small loop first, then the tall upright stroke, then the dot last',
            'ھ': 'draw the small loop, then the second loop beside it, in one flowing stroke', 'ی': 'a bowl that swings back under itself; at the start and middle, the 2 dots below come last', 'ے': 'one long flat sweep to the left, curling up at the end',
            'ئ': 'the ye-shaped body first, then the small hamza hook on top, last',
            'ص': 'loop first, then the tail leftwards along the line', 'ض': 'loop first, then the tail leftwards; the dot last',
            'ٹ': 'body first, then the small ط sign on top, last', 'ڈ': 'top down and out to the left in one angled stroke, then the small ط sign on top, last',
            'ڑ': 'top down and sweep left below the line, then the small ط sign on top, last'}


def hint(l):
    if l['ch'] in HINT_FIX: return HINT_FIX[l['ch']]
    h = STROKE.get(l['family'], DEFAULT_HINT)
    nd = DOTS.get(l['ch'], 0)
    h = re.sub(r'\s*\((?:ے|ھ)[^)]*\)', '', h)
    if nd == 0: h = re.sub(r';?\s*dots? last', '', h)
    elif nd > 1: h = h.replace('dot last', 'dots last')
    elif 'dot' not in h: h += '; the dot last'
    if nd > 1 and 'dots last' not in h: h += '; the dots last'
    if nd == 1: h = h.replace('dots last', 'dot last')
    return h


START_MODE = {'ع': 'topmost', 'غ': 'topmost', 'ل': 'topmost', 'د': 'topmost', 'ڈ': 'topmost', 'ذ': 'topmost', 'ر': 'topmost', 'ڑ': 'topmost', 'ز': 'topmost', 'ژ': 'topmost',
              'ج': 'topmost', 'چ': 'topmost', 'ح': 'topmost', 'خ': 'topmost', 'ے': 'topmost', 'ک': 'baseRight', 'گ': 'baseRight', 'ئ': 'baseRight'}


def sdfor(l, form):
    if form in ('medial', 'final'): return {'sd': True, 'dir': 'leftb', 'mode': 'default'}
    m0 = START_MODE.get(l['ch'], 'default'); d0 = direction(l)
    d0 = 'down' if (l['ch'] == 'ل' or d0 == 'downleft') else d0
    if m0 == 'baseRight': d0 = 'leftb'
    return {'sd': True, 'dir': d0, 'mode': START_MODE.get(l['ch'], 'default'), 'above': 1 if l['ch'] in DOT_ABOVE else 0}


DOT_ABOVE = set('تثٹنشضظغفقخذزژڈڑ')


def gloss(w):
    g = re.sub(r'\s*\([^)]*\)', '', w[2]).strip()
    return g or w[2].strip('() ')


def okset(n): return set(''.join(l['ch'] for l in taught_upto(n))) | set(' ۔،؟:!"-') | (set('آؤۃ۰۱۲۳۴۵۶۷۸۹') if n >= 10 else set())


def decodable(n, text): return n >= 11 or all(c in okset(n) or MARKS.match(c) for c in text)


def upassage(u):
    ps = u.get('passage')
    return ps if ps and decodable(u['n'], ps[0]) else None


def vtext(u, ps):  # story text: vowelled through unit 10 when the data has it
    return ps[3] if (u['n'] <= 10 and len(ps) > 3 and ps[3]) else ps[0]


def _rom3(w): return unicodedata.normalize('NFKD', w[1]).encode('ascii', 'ignore').decode()[:3].lower()


def _rn(w): return unicodedata.normalize('NFKD', w[1]).encode('ascii', 'ignore').decode().lower()


def _similar(a, b):
    import difflib
    x, y = _rn(a), _rn(b)
    return difflib.SequenceMatcher(None, x, y).ratio() >= 0.66


def uniq_gloss(ws):
    """Pick words for a matching page whose meanings are clearly different: no equal gloss, no look-alike romanisation (milnā / milā)."""
    seen, r3, out, rest = set(), set(), [], []
    for w in ws:
        k = re.sub(r'\s*\(.*\)', '', w[2]).strip().lower()
        if k in seen: continue
        if _rom3(w) in r3 or any(_similar(w, o) for o in out): rest.append(w); continue
        seen.add(k); r3.add(_rom3(w)); out.append(w)
    return out + rest


def uwords(u):
    ws = [w for w in u['words'] if decodable(u['n'], w[0]) and 'preview' not in w[2]]
    ws = ws if len(ws) >= 8 else list(u['words'])
    # rank: words that use this unit's new letters come first (stable), so a growing word list never pushes the unit's own letters out of the printed pages
    new = set(u['letters'])
    return [w for _, _, w in sorted(((-len(new & set(w[0])), i, w) for i, w in enumerate(ws)), key=lambda t: (t[0], t[1]))]


def usents(u):
    ss = [x for x in u['sentences'] if decodable(u['n'], x[0])]
    return (ss or list(u['sentences']))[:5]


KEYS = {}


def addkey(n, sid, htm): KEYS[(n, sid)] = htm


def key_pages(u, sids, title='Answer key'):
    groups = [['lookalike', 'match'], ['join']] if len(sids) > 1 else [sids]
    out = []
    for g in groups:
        parts = [KEYS[(u['n'], x)] for x in g if x in sids and (u['n'], x) in KEYS]
        if parts:
            out.append(hd(f'Unit {u["n"]} · answers', f'{title}: unit {u["n"]}', '', nq=False, fields=False)
                       + '<div class="note" style="margin:-1mm 0 3mm">For the grown-up. Keep this page; the child does not need it.</div>' + ''.join(parts))
    return out


def direction(l):
    h = hint(l)
    down = bool(re.search(r'top to bottom|top down(?!.*left)', h))
    dl = (not down) and re.search(r'top down|sweep left', h) and re.search(r'down', h)
    return 'down' if down else 'downleft' if dl else 'left'


# ---- helpers ----------------------------------------------------------------------------------------------------
import unicodedata
_AR = re.compile(r'([\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+)')


def _nfc_latin(t):
    return ''.join(x if _AR.fullmatch(x) else unicodedata.normalize('NFC', x) for x in _AR.split(str(t)))


def esc(t): return html.escape(_nfc_latin(t))
MARKS = re.compile(r'[ً-ٰٟۖ-ۭ]')


def clusters(w):
    out = []
    for ch in w:
        if MARKS.match(ch) and out: out[-1] += ch
        else: out.append(ch)
    return out


def forms(l):
    return [('isolated', l['ch']), ('initial', l['ch'] + TAT if l['joiner'] else None),
            ('medial', TAT + l['ch'] + TAT if l['joiner'] else None), ('final', TAT + l['ch'])]


def ur(t, nq=False, cls=''): return f'<span lang="ur" class="{"nq" if nq else "ur"} {cls}">{esc(t)}</span>'


def first_clause(h):
    h = re.split(r';', h)[0]
    h = h if len(h) <= 95 else h[:92].rsplit(' ', 1)[0] + '…'
    if h.count('(') > h.count(')'): h = h[:h.rfind('(')].strip(' ,;…')
    return h


def unit_letters(u): return [BY[c] for c in u['letters'] if c in BY]


def taught_upto(n): return [BY[c] for x in U if x['n'] <= n for c in x['letters'] if c in BY]


def use_nastaliq(n): return n >= 11


def vword(u, w):  # vowel marks kept through unit 10 (course design decision 5), removed from unit 11
    return w[3] if (u['n'] <= 10 and len(w) > 3 and w[3]) else w[0]


def level(n):
    return 'Getting ready' if n == 0 else 'Beginner' if n <= 3 else 'Early reader' if n <= 7 else 'Developing reader' if n <= 10 else 'Fluent reader'


def static_fonts():
    """Chromium embeds variable fonts as Type 3 (big, not selectable). Make static instances once, cache them."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    d = CACHE / 'fonts'; d.mkdir(parents=True, exist_ok=True)
    jobs = [('Naskh400.ttf', FONTS / 'NotoNaskhArabic.ttf', 400), ('Fredoka400.ttf', FONTS / 'Fredoka.woff2', 400),
            ('Fredoka600.ttf', FONTS / 'Fredoka.woff2', 600), ('Fredoka700.ttf', FONTS / 'Fredoka.woff2', 700)]
    for name, src, w in jobs:
        dst = d / name
        if dst.exists() and dst.stat().st_mtime > src.stat().st_mtime: continue
        f = TTFont(src); f = instancer.instantiateVariableFont(f, {'wght': w}); f.flavor = None; f.save(dst)
    return d


_images = {}


def img(name, h_px):
    """Small cached PNG of an app image (alpha kept, palette-quantised) -> file:// url."""
    from PIL import Image
    key = (name, h_px)
    if key in _images: return _images[key]
    CACHE.mkdir(parents=True, exist_ok=True)
    dst = CACHE / f'{name}_{h_px}.png'
    if not dst.exists():
        im = Image.open(IMG / f'{name}.webp').convert('RGBA')
        w = round(im.width * h_px / im.height)
        im = im.resize((w, h_px), Image.LANCZOS)
        im = im.quantize(colors=48, method=Image.FASTOCTREE, dither=Image.NONE)
        im.save(dst, optimize=True)
    _images[key] = dst.as_uri()
    return _images[key]


# ---- SVG writing row ---------------------------------------------------------------------------------------------
W = 182.0
GUIDE = 'fill="#ededed" stroke="#4a4a4a" stroke-width="1.0" stroke-dasharray="1.6 1.9" paint-order="stroke"'


def row(cells, h=36, em=30, base=24, w=W, lines=True, nq=False, arrow_first=True):
    """cells: list of (txt, mode) right-to-left; mode in model|dot|blank. Returns an <svg>."""
    n = len(cells)
    cw = w / n
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" style="display:block;overflow:visible">']
    ytop, ymid = max(1.2, base - .74 * em), base - .27 * em
    fam = 'URC Nastaliq' if nq else 'URC Naskh'
    for i, c in enumerate(cells):
        txt, mode = c[0], c[1]
        extra = c[2] if len(c) > 2 else {}
        cx = w - cw * (i + .5)
        if mode == 'blank' or not txt: continue
        if mode == 'ghost': mode = 'ghost'
        fill = '#151515' if mode == 'model' else None
        attr = f'fill="{fill}"' if fill else (GUIDE if (em >= 28 and mode == 'dot') else 'fill="#9c9c9c"')
        s.append(f'<text x="{cx:.2f}" y="{base}" font-family="{fam}" font-size="{em}" direction="rtl" text-anchor="middle" {attr}>{esc(txt)}</text>')
        if extra.get('sd'):
            s.append(f'<g class="sd" data-txt="{esc(txt)}" data-cx="{cx:.2f}" data-by="{base}" data-em="{em}" data-dir="{extra["dir"]}" data-mode="{extra.get("mode", "default")}" data-above="{extra.get("above", 0)}" data-arrow="{1 if mode == "model" else 0}" data-r="{1.6 if mode == "model" else 1.1}"></g>')
    if lines:
        s.append(f'<g stroke-width=".28"><line x1="0" x2="{w}" y1="{ytop:.2f}" y2="{ytop:.2f}" stroke="#d2d2d2"/>'
                 f'<line x1="0" x2="{w}" y1="{ymid:.2f}" y2="{ymid:.2f}" stroke="#cfcfcf" stroke-dasharray="1.4 1.4"/>'
                 f'<line x1="0" x2="{w}" y1="{base}" y2="{base}" stroke="#6f6f6f" stroke-width=".4"/></g>')
        for i in range(1, n):
            x = w - cw * i
            s.append(f'<line x1="{x:.2f}" x2="{x:.2f}" y1="{ytop - .6:.2f}" y2="{base + 3:.2f}" stroke="#ededed" stroke-width=".25"/>')
    s.append('</svg>')
    return ''.join(s)


# ---- page scaffolding ---------------------------------------------------------------------------------------------
class Doc:
    def __init__(self, id, title, title_ur, unit, kind, desc, practises=None, order=0):
        self.id, self.title, self.title_ur, self.unit, self.kind, self.desc = id, title, title_ur, unit, kind, desc
        self.pages = []; self.order = order; self.practises = practises or desc

    def add(self, inner): self.pages.append(inner)

    def extend(self, other_pages): self.pages.extend(other_pages)


def hd(tag, title, title_ur='', nq=True, fields=True):
    u = f'<div class="u {"nq" if nq else "ur"}" style="line-height:1.6">{esc(title_ur)}</div>' if title_ur else ''
    f = '<div class="nm"><div>Name <span></span></div><div>Date <span style="min-width:28mm"></span></div></div>' if fields else ''
    return f'<div class="hd"><div><div class="tag">{esc(tag)}</div><h1>{esc(title)}</h1></div>{u}</div>{f}'


def utag(n): return 'Course' if n is None else f'Unit {n}'


def page_html(inner, foot_left, i, n):
    pn = f'Page {i} of {n}' if n > 1 else ''
    return (f'<section class="page"><div class="pg">{inner}</div>'
            f'<div class="foot"><span>Urdu Reading Course · {esc(foot_left)} · A4, black and white is fine</span><span>{pn}</span></div></section>')


def compose(doc):
    css = (TPL / 'sheet.css').read_text().replace('{{FONTS}}', FONTS.as_uri()).replace('{{STATIC}}', (CACHE / 'fonts').as_uri())
    n = len(doc.pages)
    body = ''.join(page_html(p, f'{utag(doc.unit)} · {doc.title}', i + 1, n) for i, p in enumerate(doc.pages))
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(doc.title)}</title><style>{css}</style></head><body>{body}</body></html>'


# ---- sheet builders: each returns a list of page-inner html strings ------------------------------------------------
def pages_trace(u):
    nq = False
    out = []
    for l in unit_letters(u):
        f = dict((k, v) for k, v in forms(l))
        d = direction(l)
        nd = DOTS.get(l['ch'], 0)
        ch = l['ch']
        step2 = ('the small ط sign' if ch in TAH else 'the small hamza hook' if ch == 'ئ' else '2 dots below (start and middle shapes only)' if ch == 'ی'
                 else f'{nd} dot{"s" if nd != 1 else ""}' if nd else None)
        dotline = f'<span class="pill">step 1: the body</span> <span class="pill">step 2: {step2}</span>' if step2 else '<span class="pill">the body only: no dots</span>'
        sd = sdfor(l, 'isolated'); sdm = sdfor(l, 'medial')
        big = row([(l['ch'], 'model', sd)], h=36, em=34, base=27, w=60, lines=False)
        rows = []
        R = dict(h=32, em=30, base=23)
        lab = lambda t: f'<div class="note" style="margin:1.4mm 0 -.6mm;font-weight:600">{t}</div>'
        gm = 'ghost' if l['ch'] in 'ھشسصضث' else 'dot'
        rows.append(lab('Alone') + row([(f['isolated'], 'model', sd), (f['isolated'], gm, sd), (f['isolated'], gm, sd), (f['isolated'], 'blank')], **R))
        if l['joiner']:
            rows.append(lab('Start of a word (joins to the next letter)') + row([(f['initial'], 'model', sd), (f['initial'], 'ghost', sd), (f['initial'], 'blank'), (f['initial'], 'blank')], **R))
            rows.append(lab('Middle of a word (the pen comes in along the line from the letter before)') + row([(f['medial'], 'model', sdm), (f['medial'], 'ghost', sdm), (f['medial'], 'blank'), (f['medial'], 'blank')], **R))
        else:
            rows.append(lab('Again, alone') + row([(f['isolated'], 'dot', sd), (f['isolated'], 'dot', sd), (f['isolated'], 'blank'), (f['isolated'], 'blank')], **R))
        rows.append(lab('End of a word (the pen comes in along the line from the letter before)' if l['joiner'] else 'End of a word (the letter before it joins to it, it does not join forward)') + row([(f['final'], 'model', sdm), (f['final'], 'ghost', sdm), (f['final'], 'blank'), (f['final'], 'blank')], **R))
        if not l['joiner']:
            rows.append(lab('From memory: write it alone') + row([(f['isolated'], 'blank')] * 4, **R))
        ex = l['example']
        cands = [w for w in uwords(u) if l['ch'] in w[0] and decodable(u['n'], w[0])]
        cands.sort(key=lambda w: len(w[0]))
        wv, wr, wg = (vword(u, cands[0]), cands[0][1], gloss(cands[0])) if cands else (ex[0], ex[1], ex[2])
        wordrow = lab(f'In a word: {wr} ({wg})') + row([(wv, 'ghost'), (wv, 'blank')], h=26, em=21, base=19)
        sound = first_clause(l['hint'])
        head = (f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:6mm;margin-bottom:1mm">'
                f'<div style="flex:1"><div class="d" style="font-size:17pt;font-weight:600">{esc(l["name"])} <span class="ur" style="font-size:27pt;margin-left:3mm;vertical-align:middle">{esc(l["name_ur"])}</span></div>'
                f'<div style="margin:1mm 0 1.6mm">Sound: {esc(sound)}</div>'
                f'<div style="margin-bottom:1.8mm">{dotline}</div>'
                f'<div class="note"><b>How the pen moves:</b> {esc(hint(l))}.</div>'
                f'<div class="note" style="margin-top:1.4mm"><i class="gdot"></i> Put your pencil on the green dot and follow the arrow. Say the sound as you write.</div></div>'
                f'<div>{big}</div></div>')
        out.append(hd(f'Unit {u["n"]} · trace and write', f'Trace and write: {l["name"]}', l['name_ur'], nq=False) + head + ''.join(rows) + wordrow)
    return out


def rng_for(*a): return random.Random('-'.join(str(x) for x in a))


def pick_distractors(target, pool, k, rng):
    conf = [BY[c] for c in target.get('confusable', []) if c in BY and BY[c] in pool and BY[c]['ch'] != target['ch']]
    rest = [p for p in pool if p['ch'] != target['ch'] and p not in conf]
    rng.shuffle(rest)
    cand = conf + rest
    if not cand: return []
    out = cand[:k]
    while len(out) < k: out.append(rng.choice(cand))
    return out


def pages_lookalike(u):
    ls = unit_letters(u)
    if not ls: return []
    pool = taught_upto(u['n'])
    rng = rng_for('la', u['n'])
    rows, key = [], []
    for i, t in enumerate(ls[:6]):
        same = rng.choice([2, 3])
        opts = [(t, True)] * same + [(d, False) for d in pick_distractors(t, pool, 7 - same, rng)]
        rng.shuffle(opts)
        # RTL: first option is at the right
        cells = ''.join(f'<div class="o">{ur(o["ch"])}</div>' for o, _ in opts)
        rows.append(f'<div class="la"><div class="t">{ur(t["ch"])}</div><div class="sep"></div>{cells}</div>')
        key.append(f'<tr><td class="ur" style="font-size:16pt;width:16mm;text-align:center">{t["ch"]}</td><td>' + ', '.join(str(j + 1) for j, (_, ok) in enumerate(opts) if ok) + '</td></tr>')
    # dots sort
    sortl = list(ls)
    for t in ls:
        for c in t.get('confusable', []):
            if c in BY and BY[c] in pool and BY[c] not in sortl: sortl.append(BY[c])
    rng.shuffle(sortl); sortl = sortl[:8]
    have = {DOTS.get(x['ch'], 0) for x in sortl}
    extra = [x for x in pool if x not in sortl and DOTS.get(x['ch'], 0) > 0]
    rng.shuffle(extra)
    for x in sorted(extra, key=lambda x: DOTS.get(x['ch'], 0) in have):
        if len(have) >= 3 or len(sortl) >= 8: break
        if DOTS.get(x['ch'], 0) not in have: sortl.append(x); have.add(DOTS.get(x['ch'], 0))
    while len(sortl) < 4 and extra:
        sortl.append(extra.pop())
    rng.shuffle(sortl)
    chips = ''.join(f'<span class="ur">{esc(x["ch"])}</span>' for x in sortl)
    groups = {k: ''.join(x['ch'] for x in sortl if DOTS.get(x['ch'], 0) == k) for k in range(4)}
    used = [k for k in range(4) if groups[k] or k <= 1]
    boxes = ''.join(f'<div><span>{["No dots", "1 dot", "2 dots", "3 dots"][k]}</span></div>' for k in used)
    keytxt = ''.join(f'<tr><td>{"no dots" if k == 0 else str(k) + " dot" + ("s" if k != 1 else "")}</td><td class="ur" style="font-size:16pt">{esc(" ".join(groups[k])) or "-"}</td></tr>' for k in used)
    addkey(u['n'], 'lookalike', f'<div class="task"><b>+</b>Look-alike letters, part 1: circle these (counting from the right)</div><table class="guideT" style="width:90mm"><tr><th>Letter</th><th>Circles</th></tr>{"".join(key)}</table><div class="task"><b>+</b>Look-alike letters, part 2: the dot boxes</div><table class="guideT" style="width:90mm"><tr><th>Box</th><th>Letters</th></tr>{keytxt}</table>')
    return [hd(f'Unit {u["n"]} · look-alikes', 'Look-alike letters', 'ملتے جلتے حرف', nq=False)
            + '<div class="task"><b>1</b>Circle every letter that is the same as the big one on the right.</div>' + ''.join(rows)
            + '<div class="task"><b>2</b>Count the dots on each letter. Write the letter again in the box with that many dots.</div>'
            + f'<div class="chips">{chips}</div><div class="sortbox" style="grid-template-columns:repeat({len(used)},1fr)">{boxes}</div>'
            ]


def word_tiles(v):
    return ''.join(f'<div class="l">{ur(c)}</div>' + ('' if i == len(clusters(v)) - 1 else '<i>+</i>') for i, c in enumerate(clusters(v)))


def pages_join(u):
    ws = uwords(u)[:8]
    if not ws: return []
    nq = use_nastaliq(u['n'])
    out = []; keyh = ''
    per = 3 if nq else 4
    for p in range(0, len(ws), per):
        items = []
        for j, w in enumerate(ws[p:p + per]):
            i = p + j
            v = vword(u, w)
            guide = row([(v, 'ghost' if j < 2 else 'blank'), (v, 'blank')], h=38 if nq else 32, em=18 if nq else 24, base=27 if nq else 24, nq=nq)
            items.append(f'<div class="jn"><div class="no">{i + 1}</div><div class="tiles">{word_tiles(vword(u, w))}</div><div class="note" style="margin:.4mm 0 0.6mm">Say: {esc(w[1])} <span style="color:var(--soft)">({esc(gloss(w))})</span></div>{guide}</div>')
        keyh += ''.join(f'<tr><td>{p + j + 1}</td><td class="{"nq" if nq else "ur"}" style="font-size:16pt;text-align:right">{esc(vword(u, w))}</td><td>{esc(w[1])} ({esc(gloss(w))})</td></tr>' for j, w in enumerate(ws[p:p + per]))
        out.append(hd(f'Unit {u["n"]} · join the letters', 'Join the letters into a word', 'حرف جوڑیں', nq=False)
                   + '<div class="task"><b>1</b>The letters are standing alone. Join them into a word. Read it out loud.</div>'
                   + '<div class="note" style="margin:-1mm 0 2mm">Joined letters change shape. Write the word from right to left. The first two words on each page have a grey guide to trace.</div>'
                   + ''.join(items))
    addkey(u['n'], 'join', f'<div class="task"><b>+</b>Join the letters: the words</div><table class="guideT"><tr><th style="width:8mm">#</th><th style="text-align:right;width:40mm">Word</th><th>Say / meaning</th></tr>{keyh}</table>')
    return out


def pages_match(u):
    ws = uniq_gloss(uwords(u))[:20]
    if not ws: return []
    nq = use_nastaliq(u['n'])
    out = []; keyh = ''
    for p in range(0, len(ws), 10):
        chunk = ws[p:p + 10]
        rng = rng_for('mt', u['n'], p)
        order = list(range(len(chunk))); rng.shuffle(order)
        gl = [gloss(w) for w in chunk]
        for i0, g0 in enumerate(gl):
            if gl.count(g0) > 1: gl[i0] = chunk[i0][2].strip() if chunk[i0][2].strip() != g0 else f'{g0} ({chunk[i0][1]})'
        for i0, g0 in enumerate(gl):
            if gl.count(g0) > 1: gl[i0] = f'{g0} ({chunk[i0][1]})'
        # right column: Urdu, left column: English (shuffled)
        # grid: pair row k: left gloss k, right word k -> build as interleaved cells (left first in LTR grid)
        cells = ''.join(f'<div class="g"><b>{"abcdefghij"[k]}</b><span>{esc(gl[order[k]])}</span><i class="cn"></i></div><div class="w{" nqw" if nq else ""}"><span class="no">{p + k + 1}</span>{ur(vword(u, chunk[k]), nq)}<i class="cn"></i></div>' for k in range(len(chunk)))
        keyt = ', '.join(f'{p + k + 1}-{"abcdefghij"[order.index(k)]}' for k in range(len(chunk)))
        art = f'<img class="art" src="{img("unit_%02d" % u["n"], 220)}" alt="">' if (IMG / ("unit_%02d.webp" % u["n"])).exists() else ''
        top = hd(f'Unit {u["n"]} · read and match', 'Read and match', 'لفظ ملائیں', nq=False)
        out.append(f'<div style="position:relative">{top}<div style="position:absolute;right:42mm;top:-3mm;opacity:1;display:none">{art}</div></div>'
                   + '<div class="task"><b>1</b>Read each Urdu word. Draw a line to its meaning.</div>'
                   + f'<div class="mt">{cells}</div>')
        keyh += ''.join(f'<span class="kc">{p + k + 1} &rarr; {"abcdefghij"[order.index(k)]}</span>' for k in range(len(chunk)))
    addkey(u['n'], 'match', f'<div class="task"><b>+</b>Read and match: which meaning goes with each word</div><div class="kcs">{keyh}</div>')
    return out


def sent_row(s, nq, boxes=True):
    return f'<div class="sent"><span class="{"nq" if nq else "ur"}">{esc(s)}</span>' + ('<span class="bx"><i></i><i></i></span>' if boxes else '') + '</div>'


def pages_reading(u):
    ps = upassage(u); ws = uwords(u)[:40]; ss = usents(u)[:(3 if ps else 4)]
    if not (ws or ss or ps): return []
    nq = use_nastaliq(u['n'])
    out = []
    for p in range(0, len(ws), 20):
        chunk = ws[p:p + 20]
        cells = ''.join(f'<div class="c{" nqc" if nq else ""}">{ur(vword(u, w), nq)}<div class="bx"><i></i><i></i><i></i></div></div>' for w in chunk)
        gu = ' · '.join(f'{esc(w[1])} ({esc(gloss(w))})' for w in chunk)
        out.append(hd(f'Unit {u["n"]} · reading practice', 'Read the words', 'پڑھنے کی مشق', nq=False)
                   + '<div class="task"><b>1</b>Read each word. Colour a circle each time you read it smoothly (three tries).</div>'
                   + f'<div class="wg">{cells}</div>'
                   + f'<div class="gu"><b>Grown-up corner.</b> Say a word, let the child repeat it, then point. Sounds and meanings, from the right: {gu}</div>')
    if ss or ps:
        inner = hd(f'Unit {u["n"]} · reading practice', 'Read the sentences', 'جملے پڑھیں', nq=False)
        if ss:
            def sc(s):
                t = s[3] if (u['n'] <= 10 and len(s) > 3) else s[0]
                em = max(5.5, min(7.4, 168 / (0.46 * max(len(t), 1)))) * (0.92 if nq else 1)
                return sent_row(t, nq) + row([(t, 'ghost')], h=18 if not nq else 24, em=em, base=13 if not nq else 17, nq=nq) + ('' if (ps or nq) else row([(t, 'blank')], h=20, em=em, base=14, nq=nq))
            inner += '<div class="task"><b>2</b>Read each line twice. Slide your finger under the words, right to left. Then trace it' + ('' if (ps or nq) else ', then write it on your own') + '.</div>' + ''.join(sc(s) for s in ss)
        gu = ''
        if ss: gu += ''.join(f'<p><b>{i + 1}.</b> {esc(s[1])} - {esc(s[2])}</p>' for i, s in enumerate(ss))
        story = ''
        if ps:
            nwords = len(ps[0].split()); ptxt = vtext(u, ps)
            story = (hd(f'Unit {u["n"]} · reading practice', 'Read the story', 'کہانی پڑھیں', nq=False)
                     + '<div class="task"><b>3</b>Read the story. Then ask: who? where? what happened?</div>'
                     + f'<div class="pass {"nq" if nq else "ur"}" style="font-size:{20 if nwords <= 110 else 18}pt;line-height:{2.35 if nq else 2.1}">{esc(ptxt)}</div>'
                     + f'<div class="note" style="margin-top:2mm">Time it: ____ seconds. Words in the story: {nwords}. Words per minute = {nwords} × 60 ÷ seconds.</div>')
            gu += f'<p><b>Story.</b> {esc(ps[1])}</p><p><b>Meaning.</b> {esc(ps[2])}</p>'
        if ps:
            if ss: out.append(inner)
            out.append(story)
            out.append(hd(f'Unit {u["n"]} · reading practice', 'For the grown-up: sounds and meanings', '', nq=False, fields=False)
                       + '<div class="note" style="margin:-1mm 0 2mm">Read the lines aloud first, then let the child read them. Ask the three questions after the story.</div>' + f'<div class="gu" style="font-size:9.5pt">{gu}</div>')
        else:
            out.append(inner + f'<div class="gu" style="position:absolute;left:0;right:0;bottom:2mm"><b>Grown-up corner.</b>{gu}</div>')
    return out


def wl(n, nq=False, h=21):
    return f'<div style="display:flex;align-items:flex-end;gap:2mm;direction:ltr">{row([("", "blank")], h=h, em=17, base=15, w=170)}<div class="d" style="font:700 12pt \'URC Fredoka\';color:var(--accent);width:8mm;padding-bottom:3mm;text-align:right">{n}</div></div>'


def pages_dictation(u):
    ws = uwords(u)
    if not ws: return []
    sel = ws[8:18] if len(ws) >= 18 else ws[:10]
    ss = usents(u)[:4]
    nq = use_nastaliq(u['n'])
    p1 = (hd(f'Unit {u["n"]} · dictation', 'Listen and write', 'املا', nq=False)
          + '<div class="task"><b>1</b>The grown-up says a word twice. Write it on the line, right to left. (The words are on the last page, for the grown-up.)</div>'
          + ''.join(wl(i + 1) for i in range(len(sel))))
    say = ''.join(f'<tr><td>{i + 1}</td><td>{esc(w[1])}</td><td>{esc(gloss(w))}</td><td style="text-align:right;font-size:15pt">{ur(vword(u, w), nq)}</td></tr>' for i, w in enumerate(sel))
    p2 = hd(f'Unit {u["n"]} · dictation', 'Listen and write: sentences', 'املا', nq=False)
    if ss:
        p2 += '<div class="task"><b>1</b>The grown-up reads a sentence slowly, a few words at a time. Write it on the lines. (The words and sentences are on the last pages, for the grown-up.)</div>' + ''.join('<div style="margin-bottom:5mm;border-left:.8mm solid var(--accent);padding-left:2mm">' + wl(i + 1, h=24) + wl('', h=18) + '</div>' for i in range(len(ss)))
    p3 = (hd(f'Unit {u["n"]} · dictation key', 'For the grown-up: what to say', '', nq=False, fields=False)
          + '<div class="note" style="margin:-1mm 0 2mm">Keep this page. Say each word twice, then check the child\'s page against the last column.</div>'
          + f'<table class="guideT"><tr><th style="width:8mm">#</th><th>Say</th><th>Meaning</th><th style="width:34mm;text-align:right">Check against</th></tr>{say}'
          + ''.join(f'<tr><td>S{i + 1}</td><td colspan="2">{esc(s[1])} ({esc(s[2])})</td><td style="text-align:right;font-size:15pt">{ur(s[3] if (u["n"] <= 10 and len(s) > 3) else s[0], nq)}</td></tr>' for i, s in enumerate(ss))
          + '</table><p class="note">Marking: one tick for each word spelt correctly. A missing or wrong dot makes a different letter, so it counts as wrong. Small vowel marks are a bonus until unit 11.</p>')
    return [p1, p2, p3]


def confusable_words(u, w, rng, k=2):
    base = vword(u, w)
    cand = [vword(u, x) for x in uwords(u) if x[0] != w[0]]
    same = [c for c in cand if len(clusters(c)) == len(clusters(base))]
    rng.shuffle(same); rng.shuffle(cand)
    out = (same + cand)[:k]
    return out


def build_check(u):
    """Return (questions list) for the 10-item unit check; each q = dict(kind, say, opts, ans, text)."""
    n = u['n']; rng = rng_for('ck', n)
    nq = use_nastaliq(n)
    ls = unit_letters(u); pool = taught_upto(n); ws = uwords(u)
    qs = []
    # letters (3)
    cl = ls[:]; rng.shuffle(cl); cl = cl[:3]
    if len(cl) < 3:
        extra = [x for x in pool if x not in cl]; rng.shuffle(extra); cl += extra[:3 - len(cl)]
    for t in cl:
        d = pick_distractors(t, pool, 3, rng)
        opts = [t['ch']] + [x['ch'] for x in d]
        rng.shuffle(opts)
        qs.append(dict(kind='letter', say=f'Say: “{t["name"]}”' + (f' ({first_clause(t["hint"])})' if first_clause(t["hint"]) else ''), opts=opts, ans=opts.index(t['ch']), text=t['ch']))
    # dot count (1)
    dl = [t for t in ls if DOTS.get(t['ch'], 0) > 0 and t not in cl] or [t for t in pool if DOTS.get(t['ch'], 0) > 0 and t not in cl] or [t for t in ls if t not in cl] or ls
    if dl:
        t = rng.choice(dl); qs.append(dict(kind='dots', say='How many dots does this letter have?', big=t['ch'], ans=DOTS.get(t['ch'], 0), text=t['ch']))
    # hear the word
    need = 10 - len(qs) - 3
    hw = ws[:]; rng.shuffle(hw)
    for w in hw[:max(need - 0, 0)]:
        if len(qs) >= 7 and len([q for q in qs if q['kind'] == 'word']) >= 3 and ls: break
        v = vword(u, w); opts = [v] + confusable_words(u, w, rng); rng.shuffle(opts)
        qs.append(dict(kind='word', say=f'Say: “{w[1]}” ({gloss(w)})', opts=opts, ans=opts.index(v), text=v, nq=nq))
    wn = [q for q in qs if q['kind'] == 'word']
    # write the word (2)
    rest = [w for w in ws if vword(u, w) not in [q['text'] for q in wn]]
    rng.shuffle(rest)
    for w in (rest or ws)[:2]:
        qs.append(dict(kind='write', say=f'Join the letters and write the word. Say: “{w[1]}”.', tiles=vword(u, w), text=vword(u, w), rom=w[1]))
    # read aloud (1)
    w = (rest[2:3] or ws[:1])
    for ww in w:
        qs.append(dict(kind='read', say='Read this word out loud. Tick if it was right.', text=vword(u, ww), rom=f'{ww[1]} ({gloss(ww)})'))
    return qs[:10]


def opt_fs(opts, nq, base=8.5):
    """Largest font (mm) at which all options fit one line inside a 88 mm question card; never wraps, never overhangs."""
    n = sum(len(MARKS.sub('', o)) for o in opts)
    avail = 82 - 2.5 * (len(opts) - 1) - 5 * len(opts)
    return max(4.2, min(base, avail / ((0.72 if nq else 0.56) * max(n, 1))))


def q_html(i, q, nq, key=False):
    n = i + 1
    wide = False
    inner = f'<span class="n">{n}</span> <span class="say">{esc(q["say"])}</span>'
    if q['kind'] in ('letter', 'word'):
        cls = 'o w' if q['kind'] == 'word' else 'o'
        fs = opt_fs(q['opts'], bool(q.get('nq'))) if q['kind'] == 'word' else None
        sty = f' style="font-size:{fs:.1f}mm"' if fs else ''
        inner += '<div class="opts" style="flex-wrap:nowrap">' + ''.join(f'<div class="{cls}{" nqo" if q.get("nq") else ""}{" ok" if key and j == q["ans"] else ""}"{sty}>{ur(o, q.get("nq", False))}</div>' for j, o in enumerate(q['opts'])) + '</div>'
    elif q['kind'] == 'dots':
        inner += f'<div style="text-align:center;font-size:12mm;line-height:1;height:13mm;margin-top:0"><span class="ur" style="line-height:1">{esc(q["big"])}</span></div><div class="num">' + ''.join(f'<span class="{"ok" if key and k == q["ans"] else ""}">{k}</span>' for k in range(4)) + '</div>'
    elif q['kind'] == 'write':
        t = q['text']
        inner += f'<div class="tiles sm">{word_tiles(t)}</div>'
        inner += (f'<div style="font-size:{8 if nq else 11}mm;text-align:center;line-height:1.35">{ur(t, nq)}</div>' if key else row([("", "blank")], h=15, em=12, base=11, w=80))
    elif q['kind'] == 'read':
        inner += (f'<div style="font-size:{8.5 if (nq or key) else 16}mm;text-align:center;line-height:{1.6 if nq else 1.25};margin-top:1mm">{ur(q["text"], nq)}</div>')
        inner += f'<div style="position:absolute;left:4mm;bottom:1.6mm;font-size:9pt" class="rm">{"Answer: " + esc(q["rom"]) if key else "<i class=cb></i> right &nbsp; <i class=cb></i> needs help"}</div>'
    if key:
        redo = {'letter': 'trace + look-alike sheets for this letter', 'dots': 'look-alike sheet, part 2', 'word': 'read-and-match + reading practice', 'write': 'join-the-letters sheet', 'read': 'reading practice words'}[q['kind']]
        inner = inner.replace('<span class="say">', f'<span class="redo">If wrong, redo: {redo}</span><br><span class="say">', 1)
    return f'<div class="q{" wide" if wide else ""}">{inner}</div>'


def pages_check(u):
    if not (uwords(u) or u['letters']):
        return []
    qs = build_check(u); nq = use_nastaliq(u['n'])
    # fixed layout: 10 questions; make the two wide ones sit at the end
    qs = [q for q in qs if q['kind'] not in ('write', 'read')] + [q for q in qs if q['kind'] in ('write', 'read')]
    ch = '<div class="ck">' + ''.join(q_html(i, q, nq) for i, q in enumerate(qs)) + '</div>'
    score = '<div class="score"><span>Score: ____ / 10</span><span>8 or more: ready for the next unit</span></div>'
    p1 = (hd(f'Unit {u["n"]} · unit check', f'Unit {u["n"]} check', 'جانچ', nq=False)
          + '<div class="note" style="margin:-1mm 0 1mm">A grown-up reads each prompt. No help with the letters. 10 questions, about 10 minutes.</div>' + ch + score)
    ck = '<div class="ck keyk">' + ''.join(q_html(i, q, nq, key=True) for i, q in enumerate(qs)) + '</div>'
    p2 = (hd(f'Unit {u["n"]} · answer key', f'Unit {u["n"]} check: answer key', '', nq=False, fields=False)
          + '<div class="note" style="margin:-1mm 0 1mm">Correct answers are circled. If the score is under 8: redo the look-alike sheet and the trace sheet for the letters that were missed, wait a day, try again.</div>' + ck)
    return [p1, p2]


def pages_guide(u):
    n = u['n']; ls = unit_letters(u); nq = False
    pool = taught_upto(n)
    img_ = (IMG / ('unit_%02d.webp' % n)).exists()
    art = f'<img class="art" style="height:26mm;margin-left:4mm" src="{img("unit_%02d" % n, 220)}" alt="">' if img_ else ''
    hrs = u.get('hours') or [1, 1]
    chips = ''.join(f'<span class="ur" style="font-size:15mm;line-height:1.15;border:.3mm solid var(--rule);border-radius:2.5mm;width:19mm;height:19mm;display:grid;place-items:center">{esc(c)}</span>' for c in u['letters'] if c in BY)
    tbl = ''
    if ls:
        rows = ''
        for l in ls:
            mix = ', '.join(BY[c]['name'] for c in l.get('confusable', []) if c in BY and BY[c] in pool) or 'none yet'
            rows += (f'<tr><td class="ur" style="font-size:17pt;width:13mm;text-align:center">{esc(l["ch"])}</td><td><b>{esc(l["name"])}</b> <span class="ur" style="font-size:11pt">{esc(l["name_ur"])}</span><br>'
                     f'<span class="note">{esc(first_clause(l["hint"]))}</span></td><td class="note">{esc(hint(l))}</td><td class="note">{esc(mix)}</td></tr>')
        tbl = f'<div class="task"><b>2</b>What to say and show, letter by letter</div><table class="guideT"><tr><th></th><th>Say</th><th>How the pen moves</th><th>Often mixed up with</th></tr>{rows}</table>'
    sheets = []
    if ls: sheets += ['<b>Trace and write</b>: one page per letter. Start at the dot, follow the arrow; body first, dots last.', '<b>Look-alikes</b>: circle the same letter, then sort by dots.']
    if uwords(u): sheets += ['<b>Join the letters</b>: standing letters into a joined word.', '<b>Read and match</b>: word to meaning.', '<b>Reading practice</b>: words, sentences' + (', story.' if upassage(u) else '.'), '<b>Dictation</b>: the grown-up says it, the child writes it.']
    if uwords(u) or ls: sheets += ['<b>Unit check</b>: 10 questions. The answer key is the last page of the unit-check PDF; in the unit pack the keys are on the last pages.']
    how = '<div class="task"><b>3</b>How to use the sheets</div><ol style="columns:2;column-gap:6mm">' + ''.join(f'<li>{s}</li>' for s in sheets) + '</ol>' if sheets else ''
    if n == 0:
        how = ('<div class="task"><b>2</b>Five things to say before letter one</div><ol><li><b>Right to left.</b> The first letter is on the right. Slide a finger right to left.</li>'
               '<li><b>Letters join</b> like cursive and change shape. Ten never join forward: <span lang="ur" class="ur">ا د ڈ ذ ر ڑ ز ژ و ے</span>.</li><li><b>Dots decide the letter.</b> <span lang="ur" class="ur">ب پ ت ٹ ث ن ی</span> share one body.</li>'
               '<li><b>Small marks are vowels.</b> We keep them until unit 11.</li><li><b>Two typefaces.</b> Naskh for learning, Nastaliq for print. They are the same letters.</li></ol>')
    check = ('<div class="task"><b>4</b>How to check</div><ul><li><b>Letters:</b> cover the sound, point to the letter, the child says it. 3 of 4 right is a pass.</li>'
             '<li><b>Writing:</b> look at the start dot and the direction, not at how pretty it is. Right to left, body first, dots last.</li>'
             '<li><b>Unit check:</b> 8 of 10 means go on. Under 8: redo the look-alike and trace sheets, try again tomorrow.</li>'
             '<li><b>Praise</b> effort: “you started on the right”, “good dots”. One sheet a day beats five at once.</li></ul>'
             '<div class="task"><b>5</b>A 10-minute sitting</div><p style="margin:0"><b>2 min</b> warm-up: point to last time’s letters, the child says them. <b>5 min</b> the sheet of the day: say it, trace it, write it. <b>3 min</b> read it back together and end on something done well.</p>') if (ls or uwords(u)) else ''
    if n == 12:
        how = '<div class="task"><b>2</b>The reading test</div><p>Four short checks, as in the app: letter sounds, nonsense words, familiar words per minute, and a passage with 5 questions. Benchmarks: over 90 correct words a minute exceeds, 60 to 90 meets, under 60 below the grade-2 standard. The page in this pack has the test passage and the answers.</p>'
    if n == 11:
        how += '<p class="note">From this unit the small vowel marks are removed and the sheets switch to Nastaliq, the style of printed Urdu books.</p>'
    mins = f'About {hrs[0]} hour{"s" if hrs[0] != 1 else ""} for a child, {hrs[1]} for an adult. Do 10 minutes a day, short and happy.'
    inner = ('<div class="gd"><div class="hd"><div><div class="tag">For parents and teachers</div>'
             f'<h1>Unit {n}: {esc(u["title"])}</h1></div><div class="u nq" style="line-height:1.6">{esc(u["title_ur"])}</div></div>'
             f'<div style="display:flex;gap:5mm;align-items:flex-start"><div style="flex:1"><div class="task" style="margin-top:0"><b>1</b>In this unit</div><p style="margin:0 0 1.6mm">{esc(u["focus"])}.</p>'
             f'<div class="note"><b>How long:</b> {mins}</div></div>{art}</div>'
             + (f'<div class="chips" style="justify-content:flex-start;gap:2mm">{chips}</div>' if chips else '') + tbl + how + check + '</div>')
    return [inner]


def ans_cell(x):
    m = re.match(r'^(.*?)\s*\((.*)\)\s*$', x)
    if not m: return f'<span class="nq" style="font-size:13pt">{esc(x)}</span>'
    return f'<span class="rm" style="color:var(--mid);margin-right:4mm">({esc(m.group(2))})</span><span class="nq" style="font-size:13pt">{esc(m.group(1))}</span>'


def pages_unit12_test():
    a = L['assessment']
    qs = ''.join(f'<li class="nq" style="font-size:15pt;line-height:2.1;direction:rtl;text-align:right">{esc(q)}</li>' for q in a['questions'])
    ans = '<table class="guideT">' + ''.join(f'<tr><td style="width:8mm">{i + 1}</td><td style="text-align:right">{ans_cell(x)}</td></tr>' for i, x in enumerate(a['answers'])) + '</table>'
    n = len(a['passage'].split())
    addkey(12, 'check', f'<div class="task"><b>+</b>Reading test: answers</div>{ans}')
    return [hd('Unit 12 · reading test practice', 'Reading test: the passage', 'روانی کی جانچ', nq=False)
            + '<div class="task"><b>1</b>Read the passage out loud. A grown-up times one minute and marks the words that were wrong.</div>'
            + f'<div class="pass nq">{esc(a["passage"])}</div><div class="note" style="margin-top:2mm">The passage has {n} words. Correct words in one minute: ______ . Over 90 exceeds, 60 to 90 meets, under 60 below the grade-2 standard.</div>'
            + '<div class="task"><b>2</b>Ask the five questions. The child answers out loud.</div>'
            + f'<ol style="direction:rtl;list-style-position:inside;padding:0 3mm">{qs}</ol>']


# ---- course-level sheets -------------------------------------------------------------------------------------------
DICT_ORDER = list('ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءئیے')


def short_sound(l):
    h = re.split(r'[;(]', l['hint'])[0].strip(' ,')
    return h if len(h) <= 46 else h[:44].rsplit(' ', 1)[0]


def chart_cards(ls, offset=0):
    cards = []
    for i, l in enumerate(ls):
        f = dict(forms(l))
        fm = ''.join(f'<span class="fx"><span class="ur">{esc(f[k])}</span><small>{lab}</small></span>' for k, lab in (('initial', 'start'), ('medial', 'middle'), ('final', 'end')) if f[k])
        cards.append(f'<div class="cc"><div><div class="nm2"><span class="n">{offset + i + 1}</span> {esc(l["name"])}<span class="ur">{esc(l["name_ur"])}</span></div><div class="snd">{esc(short_sound(l))}</div></div>'
                     f'<div class="big">{ur(l["ch"])}</div><div class="fm">{fm or "<span class=note style=direction:ltr>never joins forward</span>"}</div></div>')
    return cards


def pages_chart():
    out = []
    teach = [BY[c] for x in U for c in x['letters'] if c in BY]
    seen = set()
    teach = [l for l in teach if not (l['ch'] in seen or seen.add(l['ch']))]
    dic = [BY[c] for c in DICT_ORDER if c in BY] + [l for l in LET if l['ch'] not in DICT_ORDER]
    per = 21
    for title, tag, ls in (('Alphabet chart: the order we teach', 'teaching order', teach), ('Alphabet chart: dictionary order', 'dictionary order', dic)):
        for p in range(0, len(ls), per):
            out.append(hd(f'Alphabet chart · {tag}', title, 'حروفِ تہجی', nq=False, fields=False)
                       + f'<div class="note" style="margin:-1.4mm 0 2mm">{len(ls)} letters. Each card: the letter alone, then its shape at the start, middle and end of a word (read from the right).</div>'
                       + f'<div class="chart">{"".join(chart_cards(ls[p:p + per], p))}</div>')
    return out


def pages_vowels():
    dc = L['diacritics']
    base = 'ب'
    cards = ''
    for d in dc:
        ex = d['example']
        cards += (f'<div class="v"><div class="big">{ur(base + d["ch"])}</div><div class="nm3">{esc(d["name"])} <span class="ur" style="font-size:12pt;font-weight:400">{esc(d["name_ur"])}</span></div>'
                  f'<div class="sm">{esc(d["sound"])}</div><div style="font-size:8mm;line-height:1.2;margin-top:1.5mm" class="ur"><span class="ur" style="line-height:1.3">{esc(ex[0])}</span></div><div class="sm">{esc(ex[1])} · {esc(ex[2])}</div></div>')
    lv = ''.join(f'<tr><td class="ur" style="font-size:13pt;text-align:center;width:16mm">{esc(r[0])}</td><td>{esc(r[1])}</td><td class="ur" style="font-size:13pt;text-align:right">{esc(r[2].split(" ")[0])}</td><td>{esc(" ".join(r[2].split(" ")[1:]))}</td></tr>' for r in L['long_vowels'])
    nums = ''.join(f'<span style="display:inline-block;text-align:center;width:16mm"><span class="nq" lang="ur" style="font-size:17pt;display:block;line-height:1.5">{a}</span><span class="note">{b}</span></span>' for a, b in L['numerals'])
    pun = ' · '.join(f'<span class="ur" style="font-size:15pt">{esc(a)}</span> <span class="note">{esc(c)}</span>' for a, _, c in L['punctuation'])
    return [hd('Course card · vowel marks', 'Vowel marks and signs', 'حرکات', nq=False, fields=False)
            + '<div class="note" style="margin:-1.4mm 0 1mm">The small marks are written above or below a letter. They tell you the short vowel. We keep them in every word until unit 11.</div>'
            + f'<div class="vw">{cards}</div>'
            + f'<div class="task"><b>+</b>Long vowels</div><table class="guideT"><tr><th>Letter</th><th>Sound</th><th style="text-align:right">Example</th><th>Reads as</th></tr>{lv}</table>'
            + f'<div class="task"><b>+</b>Numbers</div><div style="direction:rtl;text-align:center">{nums}</div>'
            + f'<div class="task"><b>+</b>Signs</div><div>{pun}</div>']


def pages_flash_letters():
    teach = [BY[c] for x in U for c in x['letters'] if c in BY]
    out = []
    for p in range(0, len(teach), 12):
        cells = ''
        for l in teach[p:p + 12]:
            f = dict(forms(l))
            fm = ''.join(f'<span class="ur">{esc(f[k])}</span>' for k in ('final', 'medial', 'initial') if f[k])
            cells += (f'<div class="k"><span class="tag">unit {l["unit"]}</span><div class="ur" style="font-size:30mm">{esc(l["ch"])}</div><div class="nmn">{esc(l["name"])}</div><div class="fm">{fm}</div><div class="sm">{esc(first_clause(l["hint"]))}</div></div>')
        out.append(f'<div class="d" style="font:600 8.5pt \'URC Fredoka\';color:var(--soft)">Letter flashcards · cut along the dashed lines · say the name, then the sound</div><div class="fc" style="grid-template-rows:repeat(4,1fr)">{cells}</div>')
    return out


SIGHT_EXTRA = {'یہ': ('یہ', 'yeh', 'this'), 'اس': ('اس', 'us', 'that, his, her')}


def pages_flash_words():
    sw = L['sight_words']
    out = []
    for p in range(0, len(sw), 15):
        cells = ''
        for w in sw[p:p + 15]:
            hit = next((x for un in U for x in un['words'] if x[0] == w), None) or SIGHT_EXTRA.get(w)
            sub = f'<div class="sm">{esc(hit[1])} · {esc(gloss(hit))}</div>' if hit else ''
            cells += f'<div class="k"><div class="nq" style="font-size:17mm">{esc(w)}</div>{sub}</div>'
        out.append(f'<div class="d" style="font:600 8.5pt \'URC Fredoka\';color:var(--soft)">Sight-word flashcards · the {len(sw)} most common words, up to 15 on a page · shown in Nastaliq, the style of printed books · cut along the dashed lines</div><div class="fc" style="grid-template-rows:repeat(5,1fr)">{cells}</div>')
    return out


def pages_certificate():
    return [f'<div class="cert"><div class="pill">Urdu Reading Course</div><h1>My Urdu Reading Certificate</h1><div class="u nq">میرا اردو پڑھنے کا سرٹیفکیٹ</div>'
            f'<div class="stars"><i class="st"></i><i class="st"></i><i class="st"></i></div><div class="note" style="font-size:11pt">This certificate is proudly given to</div><div class="line"></div><div class="lab">name</div>'
            f'<div class="note" style="font-size:11pt;margin-top:5mm">who has learned the Urdu letters and can read Urdu words, sentences and stories.</div><div style="display:flex;flex-direction:column;gap:3mm;margin-top:5mm;font-size:10pt;align-items:flex-start"><div>Units finished (out of 12): <span class="line" style="display:inline-block;width:30mm;margin:0;height:5mm"></span></div><div>Letters I can read: <span class="line" style="display:inline-block;width:30mm;margin:0;height:5mm"></span></div></div>'
            f'<img src="{img("mascot_trophy", 420)}" alt="">'
            f'<div style="display:flex;gap:10mm;margin-top:2mm"><div><div class="line" style="width:60mm"></div><div class="lab">date</div></div><div><div class="line" style="width:60mm"></div><div class="lab">reading speed (words read right in one minute)</div></div></div>'
            f'<div class="sig"><div>Teacher or parent</div><div>Learner</div></div></div>']


def pages_welcome():
    return [hd('Starter pack', 'Welcome: start here', 'خوش آمدید', nq=False, fields=False)
            + f'<div style="display:flex;gap:6mm;align-items:center"><div style="flex:1"><p style="font-size:11pt;margin:0 0 2mm">This pack has what you need for the first week: an alphabet chart, a vowel-marks card, and Unit 1 (the first six letters).</p>'
              '<div class="task"><b>1</b>Print</div><ul><li>A4 paper, portrait, “actual size”. Black and white is fine.</li><li>Pencils (HB) and a rubber for the child. A soft pencil is easier to trace with.</li></ul>'
              '<div class="task"><b>2</b>Sit down</div><ul><li>10 minutes, once a day. Stop while the child still wants more.</li><li>Sit on the child’s left so your hand does not hide the page.</li></ul>'
              '<div class="task"><b>3</b>Remember three things</div><ul><li>Urdu goes <b>right to left</b>. Start on the right of the page.</li><li>Letters <b>join</b>, and change shape. The chart shows all the shapes.</li><li><b>Body first, dots last.</b> Write the whole word, then add the dots.</li></ul></div>'
              f'<img class="mk" style="height:70mm" src="{img("mascot_hello", 360)}" alt=""></div>'
            + '<div class="task"><b>4</b>What is inside</div><ol><li>Alphabet chart in teaching order (2 pages)</li><li>Vowel marks card</li><li>Unit 1: guide, trace sheets for the six letters, look-alikes, join the letters, reading practice, unit check, answer keys</li></ol>'
            + '<p class="note">More sheets for every unit are in the app, under Practice sheets.</p>']


# ---- registry of documents ----------------------------------------------------------------------------------------
SHEETS = [
    ('guide', 'Parent and teacher guide', 'والدین اور استاد کے لیے', 'guide', pages_guide, 'What to say, how long, how to check.'),
    ('trace', 'Trace and write', 'حرف لکھنا', 'trace', pages_trace, 'Writing each letter and its shapes, body first, dots last.'),
    ('lookalike', 'Look-alike letters', 'ملتے جلتے حرف', 'lookalike', pages_lookalike, 'Telling similar letters apart by their dots.'),
    ('join', 'Join the letters', 'حرف جوڑیں', 'join', pages_join, 'Joining separate letters into words.'),
    ('match', 'Read and match', 'لفظ ملائیں', 'match', pages_match, 'Reading words and matching them to their meaning.'),
    ('reading', 'Reading practice', 'پڑھنے کی مشق', 'reading', pages_reading, 'Words, sentences and a short story to read aloud.'),
    ('dictation', 'Listen and write', 'املا', 'dictation', pages_dictation, 'Writing words and sentences the grown-up says.'),
    ('check', 'Unit check', 'جانچ', 'check', pages_check, 'Ten questions with an answer key. 8 of 10 means go on.'),
]
PACK_ORDER = ['guide', 'trace', 'lookalike', 'join', 'match', 'reading', 'dictation', 'check']


def build_docs():
    docs = []
    for u in U:
        n = u['n']; tail = {}; pk = Doc(f'u{n:02d}_pack', f'Unit {n} pack', 'مکمل مشق', n, 'pack', f'Everything for unit {n} in one print.', order=n * 100 + 99)
        for j, (sid, title, tur, kind, fn, desc) in enumerate(SHEETS):
            pages = fn(u)
            if n == 12 and sid == 'check':
                pages = pages_unit12_test(); title, tur, desc = 'Reading test', 'روانی کی جانچ', 'The test passage with five questions and the answers, for the grown-up to time and mark.'
            if not pages: continue
            d = Doc(f'u{n:02d}_{sid}', title, tur, n, kind, desc, order=n * 100 + j)
            d.pages = pages + (key_pages(u, [sid]) if sid in ('lookalike', 'join', 'match') or (n == 12 and sid == 'check') else [])
            docs.append(d)
            if sid in PACK_ORDER: pk.extend(pages[:-1] if sid in ('dictation', 'check') and len(pages) >= 2 and n != 12 else pages)
            if sid in ('dictation', 'check') and len(pages) >= 2 and n != 12: tail[sid] = pages[-1]
        pk.extend(key_pages(u, ['lookalike', 'join', 'match']) + [tail[k] for k in ('dictation', 'check') if k in tail] + (key_pages(u, ['check']) if n == 12 else []))
        if len(pk.pages) > 1:
            docs.append(pk)
    course = [
        ('course_alphabet_chart', 'Alphabet chart', 'حروفِ تہجی کا چارٹ', 'chart', pages_chart(), 'All the letters with every shape, in teaching order and in dictionary order.'),
        ('course_vowel_marks', 'Vowel marks and signs card', 'حرکات کا کارڈ', 'card', pages_vowels(), 'Zabar, zer, pesh, the long vowels, numbers and signs.'),
        ('course_flashcards_letters', 'Letter flashcards', 'حروف کے کارڈ', 'flashcards', pages_flash_letters(), 'Cut-out cards: every letter with its name, shapes and sound.'),
        ('course_flashcards_sight_words', 'Sight-word flashcards', 'عام الفاظ کے کارڈ', 'flashcards', pages_flash_words(), 'Cut-out cards for the most common Urdu words.'),
        ('course_certificate', 'My Urdu Reading Certificate', 'میرا اردو پڑھنے کا سرٹیفکیٹ', 'certificate', pages_certificate(), 'A certificate to print when the course is finished.'),
    ]
    for j, (cid, t, tur, kind, pages, desc) in enumerate(course):
        d = Doc(cid, t, tur, None, kind, desc, order=-100 + j); d.pages = pages; docs.append(d)
    sp = Doc('course_starter_pack', 'Starter pack', 'شروعاتی پیک', None, 'starter', 'Welcome, alphabet chart, vowel card and the practice sheets for unit 1: a first week of practice.', order=-200)
    u1 = U[1]
    sp.pages = pages_welcome() + pages_chart()[:2] + pages_vowels() + pages_guide(u1) + pages_trace(u1) + pages_lookalike(u1) + pages_join(u1) + pages_reading(u1) + pages_check(u1)[:1] + key_pages(u1, ['lookalike', 'join']) + pages_check(u1)[1:]
    docs.append(sp)
    return docs


# ---- render -------------------------------------------------------------------------------------------------------
def find_chromium():
    cands = sorted(glob.glob(str(Path.home() / '.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))) + \
        sorted(glob.glob(str(Path.home() / '.cache/ms-playwright/chromium-*/chrome-linux64/chrome')))
    return cands[-1] if cands else None


OVERFLOW_JS = '''() => { const out = [], mm = 96 / 25.4;
  document.querySelectorAll('.page').forEach((pgEl, i) => { const pg = pgEl.querySelector('.pg'), r = pg.getBoundingClientRect();
    let maxB = 0; const abs = [];
    for (const c of pg.children) { const cs = getComputedStyle(c); if (cs.position === 'absolute') { abs.push(c); continue; } maxB = Math.max(maxB, c.getBoundingClientRect().bottom); }
    if (maxB > r.bottom + 1) out.push([i + 1, 'content runs past the page by ' + ((maxB - r.bottom) / mm).toFixed(1) + ' mm']);
    for (const a of abs) { const t = a.getBoundingClientRect().top; if (maxB > t - 1 && (a.classList.contains('key') || a.classList.contains('gu'))) out.push([i + 1, 'answer box overlaps content by ' + ((maxB - t) / mm).toFixed(1) + ' mm']); else if (maxB > t - 1) out.push([i + 1, 'bottom box overlaps content']); }
    pg.querySelectorAll('.q').forEach(q => { const r = q.getBoundingClientRect();
      q.querySelectorAll('*').forEach(e => { if (e.closest('svg')) return; const b = e.getBoundingClientRect(); if (b.width && (b.right > r.right + 1 || b.left < r.left - 1 || b.bottom > r.bottom + 1 || b.top < r.top - 1)) out.push([i + 1, 'question card overflow: ' + (e.textContent || e.className).slice(0, 18)]); if (e.classList.contains('w') && e.classList.contains('o') && (e.scrollWidth > e.clientWidth + 2 || e.scrollHeight > e.clientHeight + 2)) out.push([i + 1, 'option wider than its box: ' + e.textContent.slice(0, 14)]); }); });
    pg.querySelectorAll('*').forEach(e => { const b = e.getBoundingClientRect(); const pr = pgEl.getBoundingClientRect(); if (b.right > pr.right - 8 || b.left < pr.left + 8) { if (!e.closest('svg') && e.children.length === 0 && b.width > 0) out.push([i + 1, 'element outside page width: ' + (e.textContent || e.tagName).slice(0, 20)]); } });
  }); return out.slice(0, 12); }'''


async def render_all(docs, workers, png):
    from playwright.async_api import async_playwright
    tmp = CACHE / 'html'; tmp.mkdir(parents=True, exist_ok=True)
    js = (TPL / 'sheet.js').read_text()
    async with async_playwright() as p:
        try: b = await p.chromium.launch()
        except Exception:
            b = await p.chromium.launch(executable_path=find_chromium())
        q = asyncio.Queue()
        for d in docs: q.put_nowait(d)
        errs = []

        async def work():
            ctx = await b.new_context()
            pg = await ctx.new_page()
            await pg.add_init_script(js)
            while True:
                try: d = q.get_nowait()
                except asyncio.QueueEmpty: break
                try:
                    f = tmp / f'{d.id}.html'; f.write_text(compose(d), encoding='utf8')
                    await pg.goto(f.as_uri())
                    await pg.evaluate("""Promise.all(['30px "URC Naskh"','30px "URC Nastaliq"','700 20px "URC Nastaliq"','20px "URC Fredoka"'].map(f=>document.fonts.load(f,'ابجد ا')))""")
                    await pg.evaluate('document.fonts.ready')
                    await pg.evaluate('placeStarts()')
                    warn = await pg.evaluate(OVERFLOW_JS)
                    await pg.evaluate('vectorizeBorders()')
                    for w in warn: print(f'  WARN {d.id} p{w[0]}: {w[1]}', flush=True)
                    d.warn = warn
                    for w in warn:
                        if 'question card' in w[1] or 'option wider' in w[1]: errs.append((d.id, w[1]))
                    out = OUT / f'{d.id}.pdf'
                    await pg.pdf(path=str(out), prefer_css_page_size=True, print_background=True)
                    d.bytes = out.stat().st_size
                    print(f'  {d.id}: {len(d.pages)}p {d.bytes // 1024} KB', flush=True)
                except Exception as e:
                    errs.append((d.id, repr(e))); print('FAIL', d.id, e, flush=True)
            await ctx.close()
        await asyncio.gather(*[work() for _ in range(workers)])
        await b.close()
    if errs: raise SystemExit(f'failures: {errs}')


def pdf_pages(f):
    from pypdf import PdfReader
    return len(PdfReader(str(f)).pages)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=''); ap.add_argument('--workers', type=int, default=4); ap.add_argument('--png', default='')
    a = ap.parse_args()
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    static_fonts()
    docs = build_docs(); docs_all = docs
    if a.only: docs = [d for d in docs if d.id.startswith(a.only)]
    asyncio.run(render_all(docs, a.workers, a.png))
    # manifest (always rebuilt from files on disk so --only keeps the rest)
    allpdfs = {}
    for d in docs_all:
        f = OUT / f'{d.id}.pdf'
        if not f.exists(): continue
        allpdfs[d.id] = dict(id=d.id, title=d.title, title_ur=d.title_ur, unit=d.unit, kind=d.kind, pages=pdf_pages(f), size=f.stat().st_size,
                             file=f'pdf/{d.id}.pdf', level=level(d.unit) if d.unit is not None else 'All levels', desc=d.desc, order=d.order)
    items = sorted(allpdfs.values(), key=lambda x: (x['unit'] if x['unit'] is not None else -1, x['order']))
    json.dump(dict(version=1, units=[dict(n=u['n'], title=u['title'], title_ur=u['title_ur'], letters=u['letters']) for u in U], items=items),
              open(OUT / 'index.json', 'w'), ensure_ascii=False, indent=1)
    tot = sum(i['size'] for i in items)
    print(f'{len(items)} PDFs, {tot / 1e6:.2f} MB total, {time.time() - t0:.0f}s; largest {max(i["size"] for i in items) // 1024} KB')
    if a.png:
        os.makedirs(a.png, exist_ok=True)
        for d in docs:
            subprocess.run(['pdftoppm', '-r', '60', '-png', str(OUT / f'{d.id}.pdf'), f'{a.png}/{d.id}'])


if __name__ == '__main__':
    main()
