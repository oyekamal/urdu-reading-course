import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
def state(pg):
    return pg.evaluate("""()=>{const a=document.getElementById('app'); return {text:a.innerText.replace(/\\s+/g,' ').slice(0,70), rec:!!document.querySelector('.recovery'), btns:[...document.querySelectorAll('#app button')].map(b=>b.innerText.trim().slice(0,14)).slice(0,5)}}""")
def txfault(store, how, flag='window.__fault'):
    body = {'throw': "throw new DOMException('gone','NotFoundError')",
            'hang': "const tx=t.apply(this,a); return new Proxy(tx,{get(o,k){const v=o[k]; return typeof v==='function'?v.bind(o):v}, set(o,k,v){ if(k==='oncomplete'||k==='onerror'||k==='onabort') return true; o[k]=v; return true}})",
            'abort': "const tx=t.apply(this,a); setTimeout(()=>{try{tx.abort()}catch(e){}},0); return tx"}[how]
    return f"const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){{ const n=[].concat(a[0]); if(window.__fault!==false && n.includes('{store}')) {{ {body} }} return t.apply(this,a)}}"
cases=[(s,h) for s in ['profiles','settings'] for h in ['throw','hang','abort']]
mode=sys.argv[1] if len(sys.argv)>1 else 'learner'
with sync_playwright() as p:
    b=p.chromium.launch()
    for st,how in cases:
        ctx,pg=newpage(b); quick_profile(pg,'Zara')
        if mode=='teacher':
            pg.evaluate("__put('settings',{key:'mode',value:'school'}); __put('settings',{key:'teacherPin',value:'1234'}); __put('settings',{key:'activeProfile',value:null})"); pg.wait_for_timeout(300)
        ctx.add_init_script(txfault(st,how)); pg.reload(); pg.wait_for_timeout(2500); s1=state(pg)
        pg.wait_for_timeout(12000); s2=state(pg)
        # recover: clear fault and press Try again
        pg.evaluate("window.__fault=false")
        if s2['rec']:
            click(pg,"button:has-text('Try again')"); pg.wait_for_timeout(2500); s3=state(pg)
        else: s3=None
        print(st,how,mode,'| 2.5s',s1['text'][:40],'| 14s',s2['text'][:40],'rec' if s2['rec'] else '', s2['btns'], '| after retry', s3 and s3['text'][:40], flush=True)
        ctx.close()
