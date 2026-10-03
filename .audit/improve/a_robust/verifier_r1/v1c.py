from common import *
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b)
    pg.on('console', lambda m: print('CON', m.type, m.text[:200]))
    pg.on('pageerror', lambda e: print('PAGEERR', e))
    quick_profile(pg)
    pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(800)
    # make unit 1 current: write progress passed unit0
    pid=pg.evaluate("__dump()")['profiles'][0]['id']
    pg.evaluate("([id])=>__put('progress',{id,units:{0:{passed:true}}})",[pid])
    pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.ucard')[1].click()"); pg.wait_for_timeout(1500)
    print(pg.inner_text('#app')[:150].replace('\n',' | '))
    b.close()
