from common import *
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); quick_profile(pg, 'R')
    nav(pg, 'read'); pg.wait_for_timeout(800)
    print('read tab h3:', pg.evaluate("[...document.querySelectorAll('h3')].map(h=>h.innerText)"))
    pg.evaluate("document.querySelector('.btn-gold').click()"); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{const s=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Stop'); s.click(); s.click(); s.click()}"); pg.wait_for_timeout(1500)
    c, d = counts(pg); print('progress', [(x['units'], x.get('wpm')) for x in d['progress']])
    ctx.close(); b.close()
