#!/usr/bin/env python3
"""Verifier D1/D2: dots/tah drawn as pure TAPS (mouse down/up, no move), squiggled marks, body lifted twice, for ڈ ژ پ ث ذ ز."""
import json
exec(open('t6_trace.py').read().split("with sync_playwright() as p:")[0])
def open_letter(p, ch):
    b, pg = fresh(p, 'T')
    for ui in range(1, 12):
        js(pg, pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(700); js(pg, pg.query_selector_all('.ucard')[ui]); pg.wait_for_timeout(1200)
        pg.query_selector('canvas.trace').scroll_into_view_if_needed()
        for t_ in pg.query_selector_all('.tchip'):
            if t_.inner_text().startswith(ch): js(pg, t_); pg.wait_for_timeout(600); return b, pg
        js(pg, pg.query_selector(".bottom button[data-k=today]")); pg.wait_for_timeout(600)
    raise SystemExit('no unit for ' + ch)
def tap(pg, pt): pg.mouse.move(*pt); pg.mouse.down(); pg.mouse.up()
out = {}
with sync_playwright() as p:
    for ch in 'ڈژپثذز':
        b, pg = open_letter(p, ch); P = Pad(pg); comps = P.comps(); body = comps[0]; rows = P.midline_axis(body); marks = [P.sc(*c[len(c) // 2]) for c in comps[1:]]; r = {}
        def go(name, fn, want):
            reset(pg); fn(); check(r, name, verdict(pg), want)
        go('body then marks TAPPED', lambda: (P.stroke(thin(rows, 3)), [tap(pg, m) for m in marks]), True)
        go('body then marks SQUIGGLED 28px', lambda: (P.stroke(thin(rows, 3)), [P.stroke([(m[0] + 14 * math.sin(i), m[1] + 9 * math.cos(i * 1.7)) for i in range(7)]) for m in marks]), True)
        n = len(rows); third = n // 3
        go('body lifted twice then marks tapped', lambda: ([P.stroke(thin(rows[a:b_ + 1], 2)) for a, b_ in ((0, third), (third, 2 * third), (2 * third, n - 1))], [tap(pg, m) for m in marks]), True)
        go('body 2 pieces then marks as 30px LINES', lambda: ([P.stroke(thin(rows[:n // 2 + 1], 2)), P.stroke(thin(rows[n // 2:], 2))], [P.stroke(lerp((m[0] - 15, m[1]), (m[0] + 15, m[1]), 8)) for m in marks]), True)
        go('1-piece body then marks as 45px LINES', lambda: (P.stroke(thin(rows, 3)), [P.stroke(lerp((m[0] - 22, m[1]), (m[0] + 22, m[1]), 10)) for m in marks]), True)
        out[ch] = r; b.close()
bad = [(c, n, v['verdict']) for c, d in out.items() for n, v in d.items() if not v['as_expected']]
json.dump({'r': out, 'bad': bad}, open(HERE + '/t6b_marks.json', 'w'), ensure_ascii=False, indent=1)
for c, d in out.items():
    for n, v in d.items(): print(c, 'OK ' if v['as_expected'] else 'BAD', n, '->', v['verdict'])
print('BAD:', bad)
