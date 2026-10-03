from common import *
import sys
def state(pg):
    return pg.evaluate("""()=>{const a=document.getElementById('app'); const t=a.innerText.replace(/\\s+/g,' ').slice(0,110);
      return {text:t, recovery: !!document.querySelector('.recovery'), buttons:[...document.querySelectorAll('#app button')].map(b=>b.innerText.trim()).slice(0,6)}}""")
def txfault(store, how):
    body = {'throw': "throw new DOMException('gone','NotFoundError')",
            'hang': "const tx=t.apply(this,a); return new Proxy(tx,{get(o,k){const v=o[k]; return typeof v==='function'?v.bind(o):v}, set(o,k,v){ if(k==='oncomplete'||k==='onerror'||k==='onabort') return true; o[k]=v; return true}})"}[how]
    return f"const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){{ const n=[].concat(a[0]); if(n.includes('{store}')) {{ {body} }} return t.apply(this,a)}}"
S = {}
for st in ['cards', 'progress', 'sessions', 'attempts', 'assessments']:
    for how in ['throw', 'hang']:
        S[f'{st}_{how}'] = txfault(st, how)
with sync_playwright() as p:
    b = p.chromium.launch()
    names = sys.argv[1:] or list(S)
    for name in names:
        ctx, pg = newpage(b); quick_profile(pg, 'Zara')
        ctx.add_init_script(S[name]); pg.reload()
        pg.wait_for_timeout(3000); s2 = state(pg)
        pg.wait_for_timeout(14000); s15 = state(pg)
        # try the tab bar
        tabs = {}
        for k in ['review', 'read', 'me', 'today']:
            try:
                pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`)?.click()", k); pg.wait_for_timeout(1500 if 'hang' not in name else 9500)
                s = state(pg); tabs[k] = ('REC' if s['recovery'] else s['text'][:30])
            except Exception as e: tabs[k] = 'EXC'
        print(name, '| 3s:', s2['text'][:40], '| 17s:', s15['text'][:50], 'rec' if s15['recovery'] else '', '| tabs:', tabs, flush=True)
        ctx.close()
    b.close()
