import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
# last-lesson-step Continue followed by a tab tap / leave tap at various delays: what ends up on screen?
delays=[int(x) for x in sys.argv[1:]] or [0,60,150,300,450,700]
with sync_playwright() as p:
    b=p.chromium.launch()
    for d in delays:
        ctx,pg=newpage(b); quick_profile(pg,'Zara')
        click(pg,"button:has-text('Start:')"); pg.wait_for_timeout(700)
        # advance to the final screen of lesson 1 (Continue clicks, spaced)
        for _ in range(2): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
        pg.evaluate("""d=>new Promise(res=>{document.querySelector('.lesson .btn-primary').click(); setTimeout(()=>{document.querySelector(".bottom button[data-k='review']").click(); res()}, d)})""", d)
        pg.wait_for_timeout(3500)
        r=pg.evaluate("""()=>({h1:[...document.querySelectorAll('#app h1')].map(h=>h.innerText), cel:document.querySelectorAll('.celebrate').length, lessonCls:document.querySelector('#app > div')?.className, app:document.getElementById('app').innerText.replace(/\\s+/g,' ').slice(0,80)})""")
        print(d,r, 'prog',{k:len(v) for k,v in pg.evaluate('__dump()').items()}['progress'], flush=True); ctx.close()
