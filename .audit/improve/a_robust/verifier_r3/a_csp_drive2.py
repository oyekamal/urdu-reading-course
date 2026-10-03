import sys; sys.path.insert(0,'.')
from common import *
from urllib.parse import urlparse
BASE='http://localhost:5371/'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,sw='block'); reqs=[]
    pg.on('request',lambda r: reqs.append(r.url))
    quick_profile(pg,'Zara'); do_rules(pg); pg.evaluate("document.querySelector('.cel-go')?.click()"); pg.wait_for_timeout(900)
    for i in range(14):
        r=pg.evaluate("()=>{const c=document.querySelector('.celebrate'); if(c){c.querySelector('.cel-go')?.click(); return 'cel'} const b=document.querySelector('.lesson .btn-primary, .lesson .btn-wide'); if(b){b.click(); return 'btn:'+b.innerText.slice(0,15)} return 'none'}"); pg.wait_for_timeout(900)
    print('state',pg.inner_text('#app')[:80].replace('\n',' | '), '| progress', {k:v for k,v in (pg.evaluate('__dump()')['progress'][0] if pg.evaluate('__dump()')['progress'] else {}).items() if k=='units'})
    nav(pg,'today'); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(900)
    for rx in ['Sticker']: 
        nav(pg,'me'); pg.evaluate("rx=>[...document.querySelectorAll('button')].find(b=>new RegExp(rx,'i').test(b.innerText))?.click()",rx); pg.wait_for_timeout(1500)
    off=[u for u in reqs if urlparse(u).scheme in ('http','https') and urlparse(u).netloc!='localhost:5371']
    print('requests',len(reqs),'off-origin',off,'| CSP',csp(pg),'| errs',pg._errs[:3])
