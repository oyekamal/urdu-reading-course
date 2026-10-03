from common import *
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b)
    quick_profile(pg)
    nav(pg,'me') if False else None
    # kid track? default child via add learner. Units reachable via All units
    pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(800)
    print(pg.inner_text('#app')[:200])
    # click unit 0 (current)
    pg.evaluate("document.querySelectorAll('.ucard')[0].click()"); pg.wait_for_timeout(1200)
    print('AFTER cur unit click:', pg.inner_text('#app')[:300].replace('\n',' | '))
    print(pg._errs, csp(pg))
    pg.evaluate("document.querySelector('.bottom button[data-k=today]').click()"); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelectorAll('.ucard')[5].click()"); pg.wait_for_timeout(1200)
    print('AFTER locked unit click:', pg.inner_text('#app')[:300].replace('\n',' | '))
    print(pg._errs)
    b.close()
