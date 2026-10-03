from common import *
from d1_helpers import *
INIT="(()=>{const p=IDBObjectStore.prototype.put; window.__n=0; IDBObjectStore.prototype.put=function(v,k){ if(window.__arm && this.name==='progress'){ window.__n++; if(window.__n===2){ const r=p.call(this,v,k); try{this.transaction.abort()}catch(e){} return r } } return p.call(this,v,k)} })()"
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b,init=INIT); quick_profile(pg,'Part')
    pid=pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    # unit 0: rules done already; next is 'done' lesson. markLesson(progress put#1) ok, markUnit(progress put#2) aborted
    pg.evaluate("p=>__put('progress',{id:p,units:{0:{lessons:{rules:1}}}})",pid); pg.reload(); pg.wait_for_timeout(2000)
    pg.evaluate("window.__arm=1")
    click(pg,"button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(900)
    pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(2500)
    print('after finish w/ 2nd write failing:', pg.inner_text('#app')[:140].replace('\n',' | '))
    pg.evaluate("window.__arm=0")
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Back to path').click()"); pg.wait_for_timeout(1500)
    c,d=counts(pg); print('progress:', [(k,{'passed':v.get('passed'),'lessons':list(v.get('lessons',{}))}) for x in d['progress'] for k,v in x['units'].items()])
    print('Today:', pg.inner_text('.home-hero')[:200].replace('\n',' | '))
    print('primary CTA present:', pg.query_selector('.tc-go') is not None, '| Start btn:', pg.evaluate("[...document.querySelectorAll('button')].some(b=>/Start:|Continue:/.test(b.innerText))"))
    b.close()
