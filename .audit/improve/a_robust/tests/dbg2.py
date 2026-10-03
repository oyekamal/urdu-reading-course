from common import *
with sync_playwright() as p:
    b = p.chromium.launch(); ctx, pg = newpage(b)
    pg.goto(BASE); pg.wait_for_timeout(2200)
    s = lambda sel, w=420: (click(pg, sel), pg.wait_for_timeout(w))
    s("text=Let's begin", 500); s('.ob-sleeper', 2800); s('.ob-sw >> nth=0'); s('.ob-cta')
    s(".ob-opt:has-text('My child')", 1600); pg.fill('#ob-name', 'Z'); pg.wait_for_timeout(200)
    s('.ob-cta'); s('.ob-opt >> nth=1', 1600); s('.ob-opt >> nth=0', 1600); s('.ob-opt >> nth=0', 1600)
    click(pg, '.ob-opt >> nth=0'); click(pg, '.ob-opt >> nth=3'); 
    print('pains:', pg.inner_text('#app')[:60].replace('\n',' | '))
    print(pg._errs); s('.ob-cta', 1800); print(pg._errs); print('after cta1:', pg.inner_text('#app')[:60].replace('\n',' | '), pg.evaluate("[...document.querySelectorAll('.ob-cta')].map(b=>b.textContent+b.disabled)"))
    s('.ob-cta', 1800); print('after cta2:', pg.inner_text('#app')[:60].replace('\n',' | '))
