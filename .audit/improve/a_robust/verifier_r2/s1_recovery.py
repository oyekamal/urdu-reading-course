from common import *
import json
FAULT = """if (localStorage.__fault==='1') { const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ if ([].concat(a[0]).includes('cards')||[].concat(a[0]).includes('attempts')) throw new DOMException('x','InvalidStateError'); return t.apply(this,a) };
  const dd=IDBFactory.prototype.deleteDatabase; IDBFactory.prototype.deleteDatabase=function(...a){ localStorage.__fault='0'; return dd.apply(this,a) } }"""
FAULT_ALL = FAULT.replace("if ([].concat(a[0]).includes('cards')||[].concat(a[0]).includes('attempts')) throw", "throw")
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, F in [('cards+attempts store failing', FAULT), ('all stores failing', FAULT_ALL)]:
        ctx, pg = newpage(b, init=F); quick_profile(pg, 'Keep')
        pg.evaluate("async()=>{const d=await __dump(); const pid=d.profiles[0].id; await __put('assessments',{id:'z1',profileId:pid,ts:Date.now(),letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:'words',by:'T'})}")
        pg.evaluate("localStorage.__fault='1'"); pg.reload(); pg.wait_for_timeout(2500)
        print(name, '->', pg.inner_text('#app')[:60].replace('\n', ' | '), '| recovery', bool(pg.query_selector('.recovery')))
        if not pg.query_selector('.recovery'): print('   (no recovery screen; screen above)'); 
        else:
            try:
                with pg.expect_download(timeout=8000) as dl:
                    pg.evaluate("()=>[...document.querySelectorAll('.recovery button')].find(b=>/Export/.test(b.innerText)).click()"); gate_pass(pg)
                j = json.load(open(dl.value.path())); print('   salvage export:', {k: (len(v) if isinstance(v, list) else v) for k, v in j.items() if k not in ('exportedAt',)}, '| toast', toast(pg))
            except Exception as e: print('   export FAIL', str(e)[:80])
            pg.evaluate("()=>[...document.querySelectorAll('.recovery button')].find(b=>/Start fresh/.test(b.innerText)).click()"); gate_pass(pg); pg.wait_for_timeout(3500)
            print('   after Start fresh:', pg.inner_text('#app')[:50].replace('\n', ' | '), '| profiles', counts(pg)[0].get('profiles'))
        ctx.close()
    b.close()
