from common import *
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); quick_profile(pg, 'Zara')
    print('start:', pg.inner_text('#app')[:60].replace('\n', ' | '))
    # rapid tab changes: 3 different tabs within 60ms
    for gap in [0, 30, 100, 200]:
        pg.evaluate("""(g)=>{const bt=k=>document.querySelector(`.bottom button[data-k='${k}']`);
          bt('review').click(); setTimeout(()=>bt('read').click(), g); setTimeout(()=>bt('today').click(), g*2);}""", gap)
        pg.wait_for_timeout(1800)
        h1s = pg.evaluate("[...document.querySelectorAll('#app h1, main h1, .t-kids h1')].map(h=>h.innerText.trim())")
        print('gap', gap, 'h1s', h1s, 'cards', pg.evaluate("document.querySelectorAll('.t-kids > *').length"))
    # real mouse taps on the bar
    box = pg.evaluate("(()=>{const r=document.querySelector(\".bottom button[data-k='review']\").getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
    box2 = pg.evaluate("(()=>{const r=document.querySelector(\".bottom button[data-k='read']\").getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
    pg.mouse.click(*box); pg.mouse.click(*box2); pg.wait_for_timeout(1800)
    print('mouse h1s', pg.evaluate("[...document.querySelectorAll('.t-kids h1')].map(h=>h.innerText.trim())"))
    b.close()
