from common import *
from d1_helpers import *
from r2_import import run_import, base
import json
THROW="(()=>{const p=IDBObjectStore.prototype.put; let n=0; IDBObjectStore.prototype.put=function(v,k){ if(window.__thr){ if(++n>=window.__thr) throw new DOMException('quota','QuotaExceededError') } return p.call(this,v,k)} })()"
with sync_playwright() as p:
    b=p.chromium.launch()
    # atomic: throw at the 3rd put inside the import transaction
    ctx,pg=newpage(b,init=THROW); base(pg); before=counts(pg)[0]
    pg.evaluate("window.__thr=3")
    f={'format':'urdu-qaida-backup','version':1,'profiles':[{'id':'n%d'%i,'name':'N%d'%i} for i in range(5)],'cards':[{'id':'c%d'%i,'profileId':'n1','item':'x'} for i in range(5)]}
    t=run_import(pg,json.dumps(f)); after=counts(pg)[0]
    print('atomic (throw at 3rd put):', repr(t), 'unchanged' if before==after else ('CHANGED',before,after), pg._errs[-1:])
    ctx.close()
    # mode picker & welcome & presence
    ctx,pg=newpage(b); pg.goto(BASE); pg.wait_for_timeout(2200)
    print('welcome restore btn:', pg.evaluate("[...document.querySelectorAll('button')].some(b=>/Restore from a backup/.test(b.innerText))"))
    ctx.close()
    ctx,pg=newpage(b); pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500)
    print('mode picker restore btn:', pg.evaluate("[...document.querySelectorAll('button')].some(b=>/Restore from a backup/.test(b.innerText))"))
    ctx.close()
    # mode picker with existing data -> gate
    ctx,pg=newpage(b); base(pg); pg.evaluate("__put('settings',{key:'mode',value:null})"); pg.goto(BASE); pg.wait_for_timeout(1800)
    print('mode picker w/ data:', pg.inner_text('#app')[:40].replace('\n',' | '))
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()"); pg.wait_for_timeout(500)
    print('gate opened for restore on populated mode picker:', pg.query_selector('.gate-sheet') is not None)
    ctx.close()
    # adult More has import; kid Me has import
    for track,tab in [('adult','more'),('child','me')]:
        ctx,pg=newpage(b); base(pg); pg.evaluate(f"__put('profiles',{{id:'p1',kind:'learner',name:'Amal',track:'{track}',createdAt:1}})"); pg.reload(); pg.wait_for_timeout(1500); nav(pg,tab)
        print(track,tab,'import btn:', pg.evaluate("[...document.querySelectorAll('button')].some(b=>/Import a backup/.test(b.innerText))"))
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Import a backup/.test(b.innerText)).click()"); pg.wait_for_timeout(500); print('  gate:', pg.query_selector('.gate-sheet') is not None)
        ctx.close()
    # cancelled chooser: no error, app still usable
    ctx,pg=newpage(b); base(pg)
    with pg.expect_file_chooser(timeout=8000) as fc:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Import a backup/.test(b.innerText)).click()"); gate_pass(pg)
    fc.value.set_files([]); pg.wait_for_timeout(1200); print('cancel/empty chooser toast:', repr(toast(pg)), pg._errs)
    # Teacher import path (Reports)
    ctx.close()
    b.close()
