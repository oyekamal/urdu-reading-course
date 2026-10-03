from common import *
from d1_helpers import *
def onbi(pg): return pg.evaluate("__dump().then(d=>(d.settings.find(s=>s.key==='onb')||{}).value?.i)")
with sync_playwright() as p:
    b = p.chromium.launch()
    # onboarding: welcome -> wake -> colour. taps on 'Let's begin', sleeper, colour CTA, option, name CTA at various gaps
    for gap in [0,150,300]:
        ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2200)
        xy=centerText(pg,"Let's begin"); taps(pg,xy,3,gap); pg.wait_for_timeout(1500)
        print(f'gap={gap} welcome x3 ->', pg.inner_text('.ob')[:50].replace('\n',' | '), 'i=',onbi(pg))
        ctx.close()
    for gap in [0,150,300]:
        ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2200)
        click(pg, "text=Let's begin"); pg.wait_for_timeout(500); click(pg,'.ob-sleeper'); pg.wait_for_timeout(2800)
        # colour screen: pick swatch, cta x3
        click(pg,'.ob-sw >> nth=0'); pg.wait_for_timeout(300)
        xy=center(pg,'.ob-cta'); taps(pg,xy,3,gap); pg.wait_for_timeout(1500)
        print(f'gap={gap} colour CTA x3 -> i=',onbi(pg), pg.inner_text('.ob')[:50].replace('\n',' | '))
        # who-is-learning option: tap 'My child' x3 at same coords
        xy=centerText(pg,'My child','.ob-opt, button'); taps(pg,xy,3,gap); pg.wait_for_timeout(2500)
        print(f'gap={gap} Who option x3 -> i=',onbi(pg), pg.inner_text('.ob')[:60].replace('\n',' | '))
        ctx.close()
    # add learner Start dup at gap 0/150/400/800
    for gap in [0,150,400,800]:
        ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1500)
        click(pg, 'text=Just me'); pg.wait_for_timeout(400); click(pg, 'text=+ Add a learner'); pg.wait_for_timeout(400)
        pg.fill('input[placeholder=Name]', 'Dup')
        xy=centerText(pg,'^Start$'); taps(pg,xy,3,gap); pg.wait_for_timeout(2500)
        c,d=counts(pg); print(f'gap={gap} Add learner Start x3: profiles={c["profiles"]} screen=', pg.inner_text('#app')[:40].replace('\n',' | '))
        ctx.close()
    # dblclick / click_count=3 on Playwright for lesson Continue and review
    ctx, pg = newpage(b); quick_profile(pg, 'Zed')
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
    pg.dblclick('.lesson .btn-primary'); pg.wait_for_timeout(800); print('dblclick Continue:', pg.evaluate("document.querySelector('.progress i')?.style.width"))
    pg.wait_for_timeout(500); pg.click('.lesson .btn-primary', click_count=3); pg.wait_for_timeout(800); print('click_count=3 Continue:', pg.evaluate("document.querySelector('.progress i')?.style.width"), pg.evaluate("document.querySelectorAll('.celebrate').length"))
    ctx.close()
    b.close()
