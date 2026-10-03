from common import *
from d1_helpers import *
with sync_playwright() as p:
    b = p.chromium.launch()
    for gap in [100,200,300]:
        ctx, pg = newpage(b); quick_profile(pg, 'Zed')
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
        for _ in range(3): pg.wait_for_timeout(450); pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()")
        pg.wait_for_selector('.celebrate', timeout=8000); pg.wait_for_timeout(1500)
        xy=center(pg,'.cel-go'); taps(pg,xy,3,gap); pg.wait_for_timeout(2500)
        c,d=counts(pg); lessons=[ {u:list(v.get('lessons',{}).keys()) for u,v in x['units'].items()} for x in d['progress']]
        print(f'celebration Next x3 gap={gap}:', pg.inner_text('#app')[:60].replace('\n',' | '), 'celebrations', pg.evaluate("document.querySelectorAll('.celebrate').length"), lessons, [ (u,v.get('passed')) for x in d['progress'] for u,v in x['units'].items()])
        ctx.close()
    b.close()
