from common import *
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b)
    pg.on('pageerror', lambda e: print('PAGEERR', e))
    quick_profile(pg)
    pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.ucard')[0].click()"); pg.wait_for_timeout(1500)
    print(pg.inner_text('#app')[:150].replace('\n',' | '))
    print(pg.evaluate("document.querySelectorAll('#app .card').length"))
    pg.screenshot(path='u0.png')
    b.close()
