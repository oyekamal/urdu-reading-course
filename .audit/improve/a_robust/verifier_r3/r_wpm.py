import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
FAULT="""window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ const tx=t.apply(this,a); if(window.__fault && a[1]==='readwrite' && [].concat(a[0]).includes('progress')) setTimeout(()=>{try{tx.abort()}catch(e){}},0); return tx}"""
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,init=FAULT); quick_profile(pg,'Zara'); nav(pg,'read'); pg.wait_for_timeout(1000)
    print('headings:',pg.evaluate("[...document.querySelectorAll('h3')].map(h=>h.innerText)"), '| current unit 0')
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Start/.test(b.innerText)).click()"); pg.wait_for_timeout(1500)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Stop' && !b.disabled).click()"); pg.wait_for_timeout(1500)
    d=pg.evaluate('__dump()'); print('progress after Stop on unit-1 passage (learner at unit 0):', d['progress'])
    # failed write
    pg.evaluate("window.__fault=true")
    pg.evaluate("[...document.querySelectorAll('button')].filter(b=>/Start|Again/.test(b.innerText))[0].click()"); pg.wait_for_timeout(800)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Stop' && !b.disabled).click()"); pg.wait_for_timeout(2500)
    print('after failed write: Start/Again button disabled =', pg.evaluate("(()=>{const b=[...document.querySelectorAll('button')].filter(b=>/Start|Again/.test(b.innerText)); return b.map(x=>x.disabled)})()"), 'toast', toast(pg))
