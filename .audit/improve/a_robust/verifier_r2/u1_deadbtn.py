from common import *
FAULT = """window.__f={}; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ const n=[].concat(a[0]); for(const s of n){ const m=window.__f[s]; if(m==='throw') throw new DOMException('The database connection is closing.','InvalidStateError'); if(m==='hang'){ const tx=t.apply(this,a); return new Proxy(tx,{get(o,k){const v=o[k]; return typeof v==='function'?v.bind(o):v}, set(o,k,v){ if(k==='oncomplete'||k==='onerror'||k==='onabort') return true; o[k]=v; return true}}) } } return t.apply(this,a)}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for store in ['progress', 'cards', 'attempts']:
        for mode in ['throw', 'hang']:
            ctx, pg = newpage(b, init=FAULT); quick_profile(pg, 'Dead')
            pg.evaluate("([s,m])=>{window.__f[s]=m}", [store, mode])
            pg.evaluate("()=>document.querySelector('.tc-go, .dock')?.click()")
            seen = []
            for t in [1500, 5000, 11000]:
                pg.wait_for_timeout(t - (seen[-1][0] if seen else 0)); seen.append((t, pg.inner_text('#app')[:40].replace('\n', ' | '), toast(pg), bool(pg.query_selector('.recovery'))))
            print(store, mode, 'after Start tap ->', seen[0][1:], '|', seen[-1][1:], pg._errs[:1], flush=True)
            ctx.close()
    b.close()
