from common import *
import sys
sys.path.insert(0, '../verifier_r1')
from d1_helpers import *
# Burst methods on lesson Continue (unit 0 rules lesson), the finish, and the celebration buttons.
def width(pg): return pg.evaluate("document.querySelector('.lesson .progress i')?.style.width")
def method(pg, sel, how, gap=100):
    if how == 'prog3': pg.evaluate("s=>{const b=document.querySelector(s); b.click(); b.click(); b.click()}", sel)
    elif how == 'dbl': pg.dblclick(sel)
    elif how == 'cc3': pg.click(sel, click_count=3)
    elif how.startswith('mouse'):
        xy = center(pg, sel); n = 3
        taps(pg, xy, n, gap)
def lesson_state(pg):
    c, d = counts(pg)
    les = [sorted(v.get('lessons', {}).keys()) for x in d['progress'] for u, v in x['units'].items()]
    return {'w': width(pg), 'cel': pg.evaluate("document.querySelectorAll('.celebrate').length"), 'lessons': les, 'att': c.get('attempts'), 'sess': c.get('sessions'),
            'text': pg.inner_text('#app')[:40].replace('\n', ' | ')}
rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for how, gap in [('prog3', 0), ('dbl', 0), ('cc3', 0), ('mouse', 0), ('mouse', 100), ('mouse', 200), ('mouse', 300)]:
        ctx, pg = newpage(b); quick_profile(pg, 'Zed')
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(1000)
        w0 = width(pg)
        method(pg, '.lesson .btn-primary', how, gap); pg.wait_for_timeout(1500)
        w1 = width(pg)
        # then continue (slow) to the last screen, burst on the last Continue -> finish
        for _ in range(8):
            pg.wait_for_timeout(500)
            if pg.query_selector('.celebrate'): break
            if pg.evaluate("(()=>{const bs=[...document.querySelectorAll('.lesson .btn-primary')]; return bs.length})()") and width(pg) not in ('66%', '67%', '66.6667%'):
                pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()")
            else: break
        pg.wait_for_timeout(600)
        pre = width(pg)
        method(pg, '.lesson .btn-primary', how, gap); pg.wait_for_timeout(2500)
        st = lesson_state(pg)
        print(f'{how}/{gap}: first burst {w0}->{w1}; before last {pre}; after finish burst', st)
        # celebration button burst
        if pg.query_selector('.cel-go'):
            method(pg, '.cel-go', how, gap); pg.wait_for_timeout(2000)
            st2 = lesson_state(pg)
            print('    cel-go burst ->', st2, 'tab bar active:', pg.evaluate("document.querySelector('.bottom .active')?.dataset.k"), 'errs', pg._errs)
        ctx.close()
    b.close()
