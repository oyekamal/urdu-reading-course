import sys; sys.path.insert(0,'.')
import common
from common import *
import inspect
BASE='http://localhost:5371/'
src=inspect.getsource(common.onboard_child)
# stop before the very last CTA tap (the plan CTA)
idx=src.rstrip().rfind("s('.ob-cta', 2000)")
src2=src[:idx].rstrip().rstrip(';')
src2=src2.replace('def onboard_child','def onboard_to_plan')
exec(src2, common.__dict__)
FAULT="""window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ const tx=t.apply(this,a); if(window.__fault && a[1]==='readwrite' && [].concat(a[0]).some(n=>['profiles'].includes(n))) setTimeout(()=>{try{tx.abort()}catch(e){}},0); return tx}"""
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,init=FAULT)
    common.onboard_to_plan(pg,'Zara',BASE)
    print('on:',pg.inner_text('#app')[:80].replace('\n',' | '))
    pg.evaluate("window.__fault=true"); click(pg,'.ob-cta'); pg.wait_for_timeout(2500)
    print('after failed finish: toast',toast(pg),'| profiles',len(pg.evaluate('__dump()')['profiles']),'| screen',pg.inner_text('#app')[:60].replace('\n',' | '))
    pg.evaluate("window.__fault=false"); pg.wait_for_timeout(500)
    for i in range(3):
        try: click(pg,'.ob-cta',1500)
        except Exception as e: print('no CTA',str(e)[:60]); break
        pg.wait_for_timeout(2500)
        d=pg.evaluate('__dump()'); print('retry',i+1,'profiles',len(d['profiles']),'screen',pg.inner_text('#app')[:50].replace('\n',' | '))
        if d['profiles']: break
