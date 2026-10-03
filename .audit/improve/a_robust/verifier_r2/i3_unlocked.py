from common import *
from i1_gate import open_unit, snap, CLICKALL
from h1_flows import mk, L1
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); quick_profile(pg, 'U'); mk(pg, [])
    for n, expect_preview in [(0, False), (1, False), (2, True)]:
        open_unit(pg, n); 
        print(f'unit {n}: preview={bool(pg.query_selector(".preview-note"))} (expect {expect_preview}) quiz={bool(pg.evaluate("[...document.querySelectorAll(\'h3\')].some(h=>/Check/.test(h.innerText))"))} head={pg.inner_text("#app")[:40]!r}')
    open_unit(pg, 1)
    # answer quiz correctly + submit
    pg.evaluate("""()=>{const lis=[...document.querySelectorAll('ol > li')]; lis.forEach(li=>{const rom=li.querySelector('b')?.innerText; const t=[...li.querySelectorAll('.tile')].find(t=>t.getAttribute('aria-label')===rom); t&&t.click()})}""")
    pg.evaluate("()=>[...document.querySelectorAll('button.act')].find(b=>b.innerText==='Submit').click()"); pg.wait_for_timeout(2500)
    c, d = counts(pg); print('after quiz in Units tab: attempts', c['attempts'], 'cards', c['cards'], 'progress', [(u, v.get('passed')) for x in d['progress'] for u, v in x['units'].items()])
    open_unit(pg, 2); print('unit 2 now preview?', bool(pg.query_selector('.preview-note')))
    print('errs', pg._errs)
    ctx.close(); b.close()
