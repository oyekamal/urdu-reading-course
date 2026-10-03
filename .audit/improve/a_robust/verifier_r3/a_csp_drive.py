import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
from urllib.parse import urlparse
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,sw='block'); reqs=[]; fails=[]
    pg.on('request',lambda r: reqs.append(r.url)); pg.on('requestfailed',lambda r: fails.append((r.url,r.failure)))
    onboard_child(pg,'Zara')
    print('after onboarding:',pg.inner_text('#app')[:50].replace('\n',' | '))
    do_rules(pg); print('celebrate shown; csp',csp(pg))
    pg.evaluate("document.querySelector('.cel-go')?.click()"); pg.wait_for_timeout(700)
    for _ in range(4):  # finish unit 0 lesson 2
        pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
    pg.wait_for_timeout(1500); print('state',pg.inner_text('#app')[:60].replace('\n',' | '))
    pg.evaluate("document.querySelector('.cel-go, .cel-back')?.click()"); pg.wait_for_timeout(1500)
    for k in ['review','read','me','today']:
        nav(pg,k); pg.wait_for_timeout(800)
    # stickers / practice / report / units
    for rx in ['Sticker','practice','Parent report']:
        pg.evaluate("rx=>[...document.querySelectorAll('button')].find(b=>new RegExp(rx,'i').test(b.innerText))?.click()",rx); pg.wait_for_timeout(1200)
        pg.evaluate("()=>document.querySelector('.stk-back, .pr-back, .gate-cancel')?.click()"); pg.wait_for_timeout(300)
    nav(pg,'today'); pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.ucard')?.click()"); pg.wait_for_timeout(1200)
    # audio: tap every speaker button once
    pg.evaluate("document.querySelectorAll('.btn-play, .btn-say').forEach(b=>b.click())"); pg.wait_for_timeout(1500)
    off=[u for u in reqs if urlparse(u).scheme in ('http','https') and urlparse(u).netloc!='localhost:5371']
    print('requests',len(reqs),'off-origin',off[:5],'failed',[f for f in fails if 'localhost' not in f[0]][:3])
    print('CSP violations:',csp(pg),'| page errors',pg._errs[:3])
