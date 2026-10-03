import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
def FAULT(store):
    return f"window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){{ if(window.__fault && [].concat(a[0]).includes('{store}')) throw new DOMException('x','NotFoundError'); return t.apply(this,a)}}"
with sync_playwright() as p:
    b=p.chromium.launch()
    for st in ['profiles','progress','assessments']:
        ctx,pg=newpage(b,init=FAULT(st)); pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500)
        pg.evaluate("__put('settings',{key:'mode',value:'school'}); __put('settings',{key:'teacherPin',value:'1234'}); __put('settings',{key:'activeProfile',value:null}); __put('profiles',{id:'k1',kind:'learner',name:'Amna',track:'child',grade:2,createdAt:1})"); pg.wait_for_timeout(300); pg.reload(); pg.wait_for_timeout(1500)
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText)).click()"); pg.wait_for_timeout(500)
        pg.fill('input[type=password]','1234'); pg.evaluate("window.__fault=true"); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(3000)
        print(st,'teacher open with fault -> app text:',repr(pg.inner_text('#app')[:90]),'| recovery:',bool(pg.query_selector('.recovery')),'| buttons',pg.evaluate("[...document.querySelectorAll('#app button, #app .tab')].map(b=>b.innerText.trim()).slice(0,8)"),'| toast',toast(pg),'| errs',pg._errs[:1],flush=True)
        ctx.close()
