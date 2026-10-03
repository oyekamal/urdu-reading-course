import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
def snap(pg): return pg.evaluate("({navs:document.querySelectorAll('.bottom').length, h1:[...document.querySelectorAll('#app h1')].map(h=>h.innerText), heroes:document.querySelectorAll('.home-hero').length, cards:document.querySelectorAll('.today-card').length, paths:document.querySelectorAll('.home-path').length, mains:document.querySelectorAll('#app > div').length})")
with sync_playwright() as p:
    b=p.chromium.launch()
    for how in ['dbl','click3','mouse3','js3']:
        ctx,pg=newpage(b); quick_profile(pg,'Zara')
        # back to picker
        pg.evaluate("document.querySelector('.hh-who').click()"); pg.wait_for_timeout(1200)
        sel='.list .card.btn >> nth=0'
        if how=='dbl': pg.dblclick(sel)
        elif how=='click3': pg.click(sel,click_count=3)
        elif how=='mouse3':
            xy=xy_of(pg,sel)
            for _ in range(3): pg.mouse.click(xy[0],xy[1]); pg.wait_for_timeout(60)
        else: print(bursts(pg,xy_of(pg,sel),(0,100,200)))
        pg.wait_for_timeout(2500); print('picker->learner',how,snap(pg),pg._errs[:1])
        # Switch back via Me tab 'Switch profile / mode' then dbl
        ctx.close()
