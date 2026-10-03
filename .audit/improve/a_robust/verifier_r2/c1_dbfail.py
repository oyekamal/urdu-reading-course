from common import *
import sys
def state(pg):
    return pg.evaluate("""()=>{const a=document.getElementById('app'); const t=a.innerText.replace(/\\s+/g,' ').slice(0,110);
      return {text:t, recovery: !!document.querySelector('.recovery'), buttons:[...document.querySelectorAll('#app button')].map(b=>b.innerText.trim()).slice(0,6)}}""")
S = {}
S['no_indexedDB'] = "Object.defineProperty(window,'indexedDB',{value:undefined,configurable:true})"
S['open_throws'] = "const o=IDBFactory.prototype.open; IDBFactory.prototype.open=function(){throw new DOMException('denied','SecurityError')}"
S['open_hang'] = "IDBFactory.prototype.open=function(){return {}}"
S['open_error'] = "IDBFactory.prototype.open=function(){const r={}; setTimeout(()=>r.onerror&&r.onerror(new Event('error')),10); return r}"
S['open_blocked'] = "IDBFactory.prototype.open=function(){const r={}; setTimeout(()=>r.onblocked&&r.onblocked(new Event('blocked')),10); return r}"
S['tx_throws'] = "const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(){throw new DOMException('closing','InvalidStateError')}"
S['tx_hang'] = """const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){const tx=t.apply(this,a); const d={oncomplete:null}; return new Proxy(tx,{get(o,k){ if(k==='oncomplete'||k==='onerror'||k==='onabort') return null; const v=o[k]; return typeof v==='function'?v.bind(o):v}, set(o,k,v){ if(k==='oncomplete'||k==='onerror'||k==='onabort') return true; o[k]=v; return true}}) }"""
S['put_quota'] = "const p=IDBObjectStore.prototype.put; IDBObjectStore.prototype.put=function(){throw new DOMException('quota','QuotaExceededError')}"
S['getAll_throws_cards'] = "const g=IDBObjectStore.prototype.getAll; IDBObjectStore.prototype.getAll=function(...a){ if(this.name==='cards') throw new DOMException('x','UnknownError'); return g.apply(this,a)}"
S['index_throws'] = "const g=IDBObjectStore.prototype.index; IDBObjectStore.prototype.index=function(...a){ throw new DOMException('x','NotFoundError')}"
with sync_playwright() as p:
    b = p.chromium.launch()
    names = sys.argv[1:] or list(S)
    for name in names:
        # fresh profile first (no fault), then reload with fault injected
        ctx, pg = newpage(b); quick_profile(pg, 'Zara')
        ctx.add_init_script(S[name]); pg.reload()
        res = []
        for t in [2000, 5000, 10000, 15000]:
            pg.wait_for_timeout(t - (res[-1][0] if res else 0)); res.append((t, state(pg)))
        print(name, '\n   2s', res[0][1]['text'][:70], '| rec', res[0][1]['recovery'], '\n  15s', res[3][1]['text'][:70], '| rec', res[3][1]['recovery'], res[3][1]['buttons'])
        ctx.close()
    b.close()
