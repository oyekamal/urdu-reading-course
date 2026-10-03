from common import *
import sys
A = {'who': 'child', 'name': 'Zara', 'colour': '#1E9C8F', 'goal': 'family', 'speak': 'fluent', 'reads': 'none', 'pains': ['dots'], 'minutes': 10, 'days': 7, 'firstWord': True}
with sync_playwright() as p:
    b = p.chromium.launch()
    for times in [(0,), (0, 0, 0), (0, 100), (0, 100, 200), (0, 200), (0, 300), (0, 360), (0, 100, 200, 300), (0, 50, 120, 250)]:
        res = []
        for rep in range(2):
            ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
            pg.evaluate("a=>__put('settings',{key:'onb',value:{i:16,a}})", A); pg.goto(BASE); pg.wait_for_timeout(1800)
            sel = '.ob-cta'
            log = burst_sel(pg, sel, times); pg.wait_for_timeout(2500)
            c, d = counts(pg); res.append((c.get('profiles'), c.get('attempts'), [x[0] for x in log]))
            ctx.close()
        print(times, 'profiles/attempts per run:', res, flush=True)
    b.close()
