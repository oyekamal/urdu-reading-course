#!/usr/bin/env python3
"""Tracing with REAL Playwright mouse drags on the real canvas. Alif (letter lesson), د and ر (single-stroke, hinted direction), ب (body then dot),
plus weird strokes: slow, shaky, reversed, tiny dot, scribble, dashes, left-handed start/lift."""
import json, math, random
from common import *
R = {}
random.seed(3)
def lerp(a, b_, n=40): return [(a[0] + (b_[0] - a[0]) * i / n, a[1] + (b_[1] - a[1]) * i / n) for i in range(n + 1)]
def open_units_trace(p, ch, unit_idx):
    b, pg = fresh(p, 'T')
    js(pg, pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(900); js(pg, pg.query_selector_all('.ucard')[unit_idx]); pg.wait_for_timeout(1500)
    pg.query_selector('canvas.trace').scroll_into_view_if_needed()
    for t in pg.query_selector_all('.tchip'):
        if ch in t.inner_text() and 'ur' in (t.inner_html()): js(pg, t); break
    pg.wait_for_timeout(600); return b, pg
def open_lesson_trace(p):   # alif: the letter lesson's trace screen
    b, pg = fresh(p, 'T')
    js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1200)
    pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0}; pr.units[0]={passed:true,lessons:{rules:1,done:1}}; await db.put('progress',pr); }""")
    pg.reload(); pg.wait_for_timeout(2500); js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1200)
    js(pg, pg.query_selector("button:has-text('Start:'), button:has-text('Continue:')")); pg.wait_for_timeout(900)
    for _ in range(8):
        if pg.query_selector('canvas.trace'): break
        c = pg.query_selector('.btn-primary.btn-wide:not(.act)')
        if not c: pg.wait_for_timeout(500); continue
        js(pg, c); pg.wait_for_timeout(900)
    pg.wait_for_timeout(700); return b, pg
MASK = """() => { const cv=document.querySelector('canvas.trace'); const r=cv.getBoundingClientRect(); const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; const W=cv.width,H=cv.height;
  // filled glyph only: alpha>20 in the faint fill
  const rows=[]; let x0=1e9,x1=-1,y0=1e9,y1=-1; const ink=new Uint8Array(W*H); for(let i=0;i<W*H;i++){ if(d[i*4+3]>20){ink[i]=1; const x=i%W,y=(i/W)|0; x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);} }
  const dot=document.querySelector('.trace-start').getBoundingClientRect();
  return {l:r.left,t:r.top,sx:r.width/W,sy:r.height/H,W,H,x0,x1,y0,y1,ink:Array.from(ink),dot:[dot.left+dot.width/2,dot.top+dot.height/2]}; }"""
class Pad:
    def __init__(s, pg): s.pg = pg; s.m = pg.evaluate(MASK)
    def sc(s, x, y): return (s.m['l'] + x * s.m['sx'], s.m['t'] + y * s.m['sy'])
    def stroke(s, pts, step=2):
        pg = s.pg; pg.mouse.move(*pts[0]); pg.mouse.down()
        for q in pts[1:]: pg.mouse.move(*q, steps=step)
        pg.mouse.up()
    def bb(s): m = s.m; return (m['l'] + m['x0'] * m['sx'], m['l'] + m['x1'] * m['sx'], m['t'] + m['y0'] * m['sy'], m['t'] + m['y1'] * m['sy'])
    def comps(s):   # connected components of the faint fill (8-neigh), biggest first, as lists of (x,y) canvas px
        m = s.m; W, H = m['W'], m['H']; ink = m['ink']; lab = [0] * (W * H); out = []
        for i in range(W * H):
            if not ink[i] or lab[i]: continue
            comp = []; st = [i]; lab[i] = 1
            while st:
                q = st.pop(); comp.append((q % W, q // W)); x, y = q % W, q // W
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H and ink[ny * W + nx] and not lab[ny * W + nx]: lab[ny * W + nx] = 1; st.append(ny * W + nx)
            out.append(comp)
        return sorted(out, key=len, reverse=True)
    def midline_cols(s, comp):  # right -> left, vertical middle of the component in each column
        cols = {}
        for x, y in comp: cols.setdefault(x, []).append(y)
        return [s.sc(x, (min(v) + max(v)) / 2) for x, v in sorted(cols.items(), reverse=True)]
    def midline_rows(s, comp):  # top -> bottom, horizontal middle in each row
        rows = {}
        for x, y in comp: rows.setdefault(y, []).append(x)
        return [s.sc((min(v) + max(v)) / 2, y) for y, v in sorted(rows.items())]
    def midline_axis(s, comp, n=40):  # follow the body from the green dot to its far end: bins along that axis, centroid of each bin
        m = s.m; sd = ((m['dot'][0] - m['l']) / m['sx'], (m['dot'][1] - m['t']) / m['sy']); far = max(comp, key=lambda q: (q[0] - sd[0]) ** 2 + (q[1] - sd[1]) ** 2)
        vx, vy = far[0] - sd[0], far[1] - sd[1]; vv = vx * vx + vy * vy; bins = {}
        for x, y in comp: bins.setdefault(min(n - 1, max(0, int(((x - sd[0]) * vx + (y - sd[1]) * vy) / vv * n))), []).append((x, y))
        return [s.sc(sum(q[0] for q in v) / len(v), sum(q[1] for q in v) / len(v)) for k, v in sorted(bins.items())]
def wiggle(pts, amp=7, per=6, vertical=True):
    out = []
    for i, (x, y) in enumerate(pts):
        o = amp * math.sin(i * 2 * math.pi / per); out.append((x, y + o) if vertical else (x + o, y))
    return out
def verdict(pg):
    pg.click('.btn-check'); pg.wait_for_timeout(250); return pg.inner_text('.trace-out')
def reset(pg): pg.click('.trace-clear'); pg.wait_for_timeout(350)
def shaky(pts, amp=5): return [(x + random.uniform(-amp, amp), y + random.uniform(-amp, amp)) for x, y in pts]
def thin(pts, k): return pts[::k] + ([pts[-1]] if (len(pts) - 1) % k else [])
OK = lambda s: '✓ good' in s
def check(res, name, got, want_ok, want_words=()):
    ok = OK(got) == want_ok and all(w in got for w in want_words); res[name] = {'verdict': got, 'expected': 'pass' if want_ok else 'kind-reject', 'as_expected': ok}
    return ok
with sync_playwright() as p:
    # ---------- alif
    b, pg = open_lesson_trace(p); pg.query_selector('canvas.trace').scroll_into_view_if_needed(); pg.wait_for_timeout(300); P = Pad(pg); l, r_, t, bt = P.bb(); cx = (l + r_) / 2; A = {}
    def run(name, fn, want, words=()):
        reset(pg); fn(); check(A, name, verdict(pg), want, words)
    run('top->bottom right of centre', lambda: P.stroke(lerp((cx + 3, t), (cx + 3, bt))), True)
    run('top->bottom exactly on the centre line (was falsely rejected)', lambda: P.stroke(lerp((cx, t), (cx, bt))), True)
    run('top->bottom 3px left of centre (was falsely rejected)', lambda: P.stroke(lerp((cx - 3, t), (cx - 3, bt))), True)
    run('BOTTOM->top (reversed)', lambda: P.stroke(lerp((cx + 3, bt), (cx + 3, t))), False, ('Start at the green dot',))
    run('ten random short dashes', lambda: [P.stroke(lerp((cx + 3, y), (cx + 3, y + (bt - t) / 9))) for y in random.sample([t + (bt - t) * k / 10 for k in range(10)], 10)], False, ('one smooth line',))
    run('wide zigzag scribble over the glyph box', lambda: P.stroke([pt for i in range(14) for pt in lerp(*(((cx + 90, t + (bt - t) * i / 13), (cx - 90, t + (bt - t) * i / 13)) if i % 2 == 0 else ((cx - 90, t + (bt - t) * i / 13), (cx + 90, t + (bt - t) * i / 13))), 12)]), False)
    run('slow shaky top->bottom (4px steps, +-4px jitter)', lambda: P.stroke(shaky(lerp((cx, t), (cx, bt), 60), 4), 3), True)
    run('very slow smooth top->bottom (200 points)', lambda: P.stroke(lerp((cx + 2, t), (cx + 2, bt), 200), 1), True)
    run('shaky BOTTOM->top', lambda: P.stroke(shaky(lerp((cx, bt), (cx, t), 60), 4), 3), False)
    run('tiny dot in the middle', lambda: P.stroke([(cx, (t + bt) / 2), (cx + 1, (t + bt) / 2 + 1)]), False, ('keep tracing',))
    run('left-handed: starts 5px left, lifts once in the middle (2 strokes)', lambda: (P.stroke(lerp((cx - 5, t + 4), (cx - 4, (t + bt) / 2), 25)), P.stroke(lerp((cx - 4, (t + bt) / 2 - 2), (cx - 5, bt), 25))), True)
    run('two strokes top half then bottom half (a 6-year-old lifting)', lambda: (P.stroke(lerp((cx + 2, t), (cx + 2, (t + bt) / 2), 25)), P.stroke(lerp((cx + 2, (t + bt) / 2), (cx + 2, bt), 25))), True)
    run('only the bottom half', lambda: P.stroke(lerp((cx, (t + bt) / 2), (cx, bt), 25)), False, ('keep tracing',))
    run('do nothing', lambda: None, False, ('keep tracing',))
    R['alif'] = A; b.close()
    # ---------- د (dal) and ر (re): unit with those letters; direction from the glyph's own body
    for ch, uidx in (('د', 4), ('ر', 3)):
        b, pg = open_units_trace(p, ch, uidx)
        # find the unit containing ch: scan units 1..12 until the chip exists
        if not any(ch in t.inner_text() for t in pg.query_selector_all('.tchip')):
            b.close(); b, pg = fresh(p, 'T'); found = False
            for ui in range(1, 12):
                js(pg, pg.query_selector(".bottom button:has-text('Units'), button:has-text('All units')")); pg.wait_for_timeout(700); js(pg, pg.query_selector_all('.ucard')[ui]); pg.wait_for_timeout(1200)
                pg.query_selector('canvas.trace').scroll_into_view_if_needed()
                for t_ in pg.query_selector_all('.tchip'):
                    if t_.inner_text().startswith(ch): js(pg, t_); found = True; break
                if found: break
                js(pg, pg.query_selector(".bottom button[data-k=today]")); pg.wait_for_timeout(600)
            pg.wait_for_timeout(600)
        P = Pad(pg); D = {}; comps = P.comps(); body = comps[0]; rows = P.midline_axis(body)
        def run2(name, fn, want, words=()):
            reset(pg); fn(); check(D, name, verdict(pg), want, words)
        run2('body top->bottom along the glyph (hinted direction)', lambda: P.stroke(thin(rows, 3)), True)
        run2('body BOTTOM->top (reversed)', lambda: P.stroke(thin(rows[::-1], 3)), False)
        run2('body top->bottom, shaky', lambda: P.stroke(shaky(thin(rows, 2), 3), 3), True)
        run2('body top->bottom then marks (if any) last', lambda: (P.stroke(thin(rows, 3)), [P.stroke([P.sc(*c[len(c) // 2]), P.sc(*c[len(c) // 2])]) for c in comps[1:]]), True)
        if len(comps) > 1: run2('marks FIRST, then body', lambda: ([P.stroke([P.sc(*c[len(c) // 2]), P.sc(c[len(c) // 2][0] + 1, c[len(c) // 2][1])]) for c in comps[1:]], P.stroke(thin(rows, 3))), False, ('Body first',))
        run2('ten random dashes', lambda: [P.stroke(lerp(rows[i], rows[min(len(rows) - 1, i + 3)], 4)) for i in random.sample(range(0, len(rows) - 3), min(10, len(rows) - 3))], False)
        R[ch] = D; b.close()
    # ---------- ب : body right->left then dot
    b, pg = open_units_trace(p, 'ب', 1); pg.wait_for_timeout(400); P = Pad(pg); B = {}; comps = P.comps(); body = comps[0]; cols = wiggle(P.midline_cols(body), 3, 6); dots = [P.sc(*c[len(c) // 2]) for c in comps[1:]]
    def run3(name, fn, want, words=()):
        reset(pg); fn(); check(B, name, verdict(pg), want, words)
    run3('body right->left, then the dot (taught order)', lambda: (P.stroke(thin(cols, 3)), [P.stroke([d, (d[0] + 1, d[1])]) for d in dots]), True)
    run3('dot FIRST then body', lambda: ([P.stroke([d, (d[0] + 1, d[1])]) for d in dots], P.stroke(thin(cols, 3))), False, ('Body first',))
    run3('body drawn LEFT->right (reversed)', lambda: (P.stroke(thin(cols[::-1], 3)), [P.stroke([d, (d[0] + 1, d[1])]) for d in dots]), False, ('Start at the green dot',))
    run3('shaky body right->left + dot', lambda: (P.stroke(shaky(thin(cols, 2), 3), 3), [P.stroke([d, (d[0] + 1, d[1])]) for d in dots]), True)
    run3('scribble over whole glyph box', lambda: (lambda l_, r2, t2, b2: P.stroke([pt for i in range(16) for pt in lerp(*(((r2 + 6, t2 + (b2 - t2) * i / 15), (l_ - 6, t2 + (b2 - t2) * i / 15)) if i % 2 == 0 else ((l_ - 6, t2 + (b2 - t2) * i / 15), (r2 + 6, t2 + (b2 - t2) * i / 15))), 12)]))(*P.bb()), False)
    R['be'] = B; b.close()
bad = [(k, n, v['verdict']) for k, d in R.items() for n, v in d.items() if not v['as_expected']]
R['unexpected'] = bad; json.dump(R, open(HERE + '/t6_trace.json', 'w'), ensure_ascii=False, indent=1)
for k, d in R.items():
    if k == 'unexpected': continue
    print('==', k)
    for n, v in d.items(): print(('  OK  ' if v['as_expected'] else '  BAD ') + n + ' -> ' + v['verdict'])
print('UNEXPECTED:', bad)
