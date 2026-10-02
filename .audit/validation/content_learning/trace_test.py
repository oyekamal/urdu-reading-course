#!/usr/bin/env python3
"""Does tracing validation (drills.js writeIt) check stroke order / direction / stroke shape, or only pixel coverage + start side?
Drives the real trace canvas in the letter lesson with synthetic mouse paths and reads the verdict text."""
import json, os, re, math, random
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); PORT = os.environ.get('PORT', '5188'); R = {}
EXE = '/home/oye/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
js = lambda pg, h: pg.evaluate('e=>e.click()', h)
def open_trace(p, letter_id_done):
    b = p.chromium.launch(executable_path=EXE); pg = b.new_context(viewport={'width': 390, 'height': 800}).new_page(); pg.on('dialog', lambda d: d.accept())
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2200); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.fill('input[placeholder=Name]', 'T'); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2500)
    if letter_id_done is not None:
        pg.evaluate("""async (ids) => { const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0}; pr.units[0]={passed:true,lessons:{rules:1,done:1}}; pr.units[1]={lessons:Object.fromEntries(ids.map(i=>['L'+i,Date.now()]))}; await db.put('progress',pr); }""", letter_id_done)
        pg.reload(); pg.wait_for_timeout(2500)
    js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1200)
    js(pg, pg.query_selector("button:has-text('Start:'), button:has-text('Continue:')")); pg.wait_for_timeout(900)
    for _ in range(8):
        if pg.query_selector('canvas.trace'): break
        c = pg.query_selector('.btn-primary.btn-wide:not(.act)')
        if not c: pg.wait_for_timeout(500); continue
        js(pg, c); pg.wait_for_timeout(900)
    pg.wait_for_timeout(700); return b, pg
def open_units_trace(p, ch):
    b = p.chromium.launch(executable_path=EXE); pg = b.new_context(viewport={'width': 390, 'height': 800}).new_page(); pg.on('dialog', lambda d: d.accept())
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2200); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.fill('input[placeholder=Name]', 'T'); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2500)
    js(pg, pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(900); js(pg, pg.query_selector_all('.ucard')[1]); pg.wait_for_timeout(1500)
    pg.query_selector('canvas.trace').scroll_into_view_if_needed()
    for t in pg.query_selector_all('.tchip'):
        if ch in t.inner_text(): js(pg, t); break
    pg.wait_for_timeout(600); return b, pg
def bbox(pg):
    return pg.evaluate("""() => { const cv=document.querySelector('canvas.trace'); const r=cv.getBoundingClientRect(); const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; let x0=1e9,x1=-1,y0=1e9,y1=-1; for(let i=3;i<d.length;i+=4) if(d[i]>20){const p=i>>2,x=p%cv.width,y=(p/cv.width)|0; x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);} const sx=r.width/cv.width, sy=r.height/cv.height; return {l:r.left+x0*sx,r:r.left+x1*sx,t:r.top+y0*sy,b:r.top+y1*sy}; }""")
def stroke(pg, pts):
    pg.mouse.move(*pts[0]); pg.mouse.down()
    for q in pts[1:]: pg.mouse.move(*q, steps=2)
    pg.mouse.up()
def verdict(pg):
    pg.click('.btn-check'); pg.wait_for_timeout(250); return pg.inner_text('.trace-out')
def reset(pg): pg.click('.trace-clear'); pg.wait_for_timeout(300)
def run(p, ids, name, tests):
    b, pg = (open_units_trace(p, ids) if isinstance(ids, str) else open_trace(p, ids)); pg.query_selector('canvas.trace').scroll_into_view_if_needed(); pg.wait_for_timeout(300); bb = bbox(pg); R[name] = {'bbox': {k: round(v) for k, v in bb.items()}}; cx = (bb['l'] + bb['r']) / 2; cy = (bb['t'] + bb['b']) / 2
    for tname, fn in tests.items():
        reset(pg); fn(pg, bb, cx, cy); R[name][tname] = verdict(pg)
    b.close()
MASK = """() => { const cv=document.querySelector('canvas.trace'); const r=cv.getBoundingClientRect(); const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; const sx=r.width/cv.width, sy=r.height/cv.height; const rows=[]; for(let y=0;y<cv.height;y+=6){ let a=-1,b=-1; for(let x=0;x<cv.width;x++){ if(d[((y*cv.width+x)<<2)+3]>20){ if(a<0)a=x; b=x; } } if(a>=0) rows.push([r.top+y*sy, r.left+a*sx, r.left+b*sx]); } return rows; }"""
with sync_playwright() as p:
    def lerp(a, b_, n=40): return [(a[0] + (b_[0] - a[0]) * i / n, a[1] + (b_[1] - a[1]) * i / n) for i in range(n + 1)]
    def raster(pg, order='top_down', direction='rtl', one_stroke=True):
        rows = pg.evaluate(MASK); rows = rows if order == 'top_down' else rows[::-1]; pts = []
        for k, (y, a, b_) in enumerate(rows):
            seg = lerp((b_, y), (a, y), 8) if direction == 'rtl' else lerp((a, y), (b_, y), 8)
            if one_stroke: pts += seg
            else: stroke(pg, seg)
        if one_stroke: stroke(pg, pts)
    alif = {
      'top_to_bottom, starts right of centre (correct)': lambda pg, bb, cx, cy: stroke(pg, lerp((cx + 3, bb['t']), (cx + 3, bb['b']))),
      'bottom_to_top, starts right of centre (WRONG direction)': lambda pg, bb, cx, cy: stroke(pg, lerp((cx + 3, bb['b']), (cx + 3, bb['t']))),
      'top_to_bottom exactly at centre line (child draws a perfect straight alif)': lambda pg, bb, cx, cy: stroke(pg, lerp((cx, bb['t']), (cx, bb['b']))),
      'top_to_bottom 3px LEFT of centre': lambda pg, bb, cx, cy: stroke(pg, lerp((cx - 3, bb['t']), (cx - 3, bb['b']))),
      'ten_short_dashes_random_order': lambda pg, bb, cx, cy: [stroke(pg, lerp((cx + 3, y), (cx + 3, y + (bb['b'] - bb['t']) / 9))) for y in random.sample([bb['t'] + (bb['b'] - bb['t']) * k / 10 for k in range(10)], 10)],
      'zigzag scribble over glyph box': lambda pg, bb, cx, cy: stroke(pg, [pt for i in range(14) for pt in lerp(*(((bb['r'], bb['t'] + (bb['b'] - bb['t']) * i / 13), (bb['l'], bb['t'] + (bb['b'] - bb['t']) * i / 13)) if i % 2 == 0 else ((bb['l'], bb['t'] + (bb['b'] - bb['t']) * i / 13), (bb['r'], bb['t'] + (bb['b'] - bb['t']) * i / 13))), 12)]),
      'do nothing': lambda pg, bb, cx, cy: None,
    }
    run(p, [], 'alif', alif)
    be = {
      'raster-fill glyph mask, top->bottom, right->left (body first, dot last)': lambda pg, bb, cx, cy: raster(pg, 'top_down', 'rtl'),
      'raster-fill glyph mask, BOTTOM->top (dot first, then body)': lambda pg, bb, cx, cy: raster(pg, 'bottom_up', 'rtl'),
      'raster-fill glyph mask LEFT->right rows, top->bottom (wrong direction), 1 stroke': lambda pg, bb, cx, cy: raster(pg, 'top_down', 'ltr'),
      'raster-fill as 14 separate strokes': lambda pg, bb, cx, cy: raster(pg, 'top_down', 'rtl', one_stroke=False),
    }
    run(p, 'ب', 'be', be)
json.dump(R, open(HERE + '/trace_test.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1))
