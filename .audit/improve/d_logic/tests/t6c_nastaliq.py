#!/usr/bin/env python3
"""Verifier r3 D1-D3: Nastaliq + Naskh careful traces (body by axis midline, marks tapped) for ا ک ر ط ڈ ڑ ز ظ ٹ forms; reversed alif/dal/re must still be rejected."""
import json
exec(open('t6_trace.py').read().split("with sync_playwright() as p:")[0])
def tap(pg, pt): pg.mouse.move(*pt); pg.mouse.down(); pg.mouse.up()
FORM = {'isolated': 0, 'initial': 1, 'medial': 2, 'final': 3}
def open_letter(p, ch, style):
    b, pg = fresh(p, 'T')
    if style == 'nastaliq': pg.evaluate("async()=>{const {db}=await import('/src/db.js'); await db.setting('ui',{style:'nastaliq'})}"); pg.reload(); pg.wait_for_timeout(2500)
    for ui in range(1, 12):
        js(pg, pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(700); js(pg, pg.query_selector_all('.ucard')[ui]); pg.wait_for_timeout(1200)
        pg.query_selector('canvas.trace').scroll_into_view_if_needed()
        for t_ in pg.query_selector_all('.tchip:not(.pchip)'):
            if t_.inner_text().startswith(ch): js(pg, t_); pg.wait_for_timeout(500); return b, pg
        js(pg, pg.query_selector(".bottom button[data-k=today]")); pg.wait_for_timeout(600)
    raise SystemExit('no unit ' + ch)
res = {}; bad = []
with sync_playwright() as p:
    for style in ('naskh', 'nastaliq'):
        for ch, forms_ in (('ا', ['isolated']), ('ر', ['isolated']), ('ڈ', ['isolated']), ('ڑ', ['isolated']), ('ز', ['isolated']), ('د', ['isolated'])):
            b, pg = open_letter(p, ch, style)
            for f in forms_:
                pg.query_selector_all('.pchip')[FORM[f]].click(); pg.wait_for_timeout(500); P = Pad(pg); comps = P.comps(); body = comps[0]; rows = P.midline_axis(body); marks = [P.sc(*c[len(c) // 2]) for c in comps[1:]]
                reset(pg); P.stroke(thin(rows, 3)); [tap(pg, m) for m in marks]; v = verdict(pg); ok = '✓ good' in v; res[f'{style}/{ch}/{f}'] = v
                if not ok: bad.append((style, ch, f, v))
                if ch in 'ادر' and f == 'isolated':
                    reset(pg); P.stroke(thin(rows[::-1], 3)); v2 = verdict(pg)
                    if '✓ good' in v2: bad.append((style, ch, f, 'REVERSED ACCEPTED', v2))
            b.close()
json.dump({'res': res, 'bad': bad}, open(HERE + '/t6c.json', 'w'), ensure_ascii=False, indent=1)
print(len(res), 'cases; bad:', bad)
