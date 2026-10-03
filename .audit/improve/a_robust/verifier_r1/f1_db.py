from common import *
from d1_helpers import *
HANG = """(()=>{const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ if(window.__hang==='read' ){ const fake={objectStore:()=>new Proxy({},{get:()=>()=>({})})}; return fake } if(window.__hang==='abort'){ const tx=t.apply(this,a); setTimeout(()=>{try{tx.abort()}catch(e){}},0); return tx } return t.apply(this,a)} })()"""
def snap(pg): return {'main': pg.evaluate("document.querySelector('#app > div')?.innerHTML.length"), 'text': pg.inner_text('#app')[:70].replace('\n',' | '), 'toast': toast(pg)}
with sync_playwright() as p:
    b=p.chromium.launch()
    for mode in ['read','abort']:
        ctx,pg=newpage(b, init=HANG); quick_profile(pg,'Hang')
        pg.evaluate(f"window.__hang='{mode}'")
        for k in ['review','me','read']:
            nav(pg,k); pg.wait_for_timeout(9500)
            print(f'[{mode}] tab {k} after 9.5s:', snap(pg), 'errs', pg._errs[-1:])
        # recover: stop hanging, click today
        pg.evaluate("window.__hang=''"); nav(pg,'today'); pg.wait_for_timeout(1500); print(f'[{mode}] recovered?', snap(pg))
        ctx.close()
    # versionchange from another tab then a normal action
    ctx,pg=newpage(b); quick_profile(pg,'VC'); pg2=ctx.new_page(); pg2.goto(BASE+'manifest.webmanifest')
    pg2.evaluate("""()=>new Promise(r=>{const q=indexedDB.open('urdu-reader',3);q.onupgradeneeded=()=>{};q.onsuccess=()=>{q.result.close();r()};q.onerror=()=>r()})""")
    pg.bring_to_front(); nav(pg,'review'); pg.wait_for_timeout(1500); print('after versionchange, review tab:', snap(pg), pg._errs[-1:])
    click(pg,"button:has-text('Start:')") if pg.query_selector("button:has-text('Start:')") else None
    nav(pg,'today'); pg.wait_for_timeout(1000); print('today:', snap(pg))
    ctx.close()
    # card kind letter with unknown item (importable via backup validator)
    ctx,pg=newpage(b); quick_profile(pg,'Cd'); pid=pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    pg.evaluate("p=>__put('cards',{id:p+':zzz',profileId:p,item:'zzz',kind:'letter',box:1,due:1,seen:0})",pid)
    pg.reload(); pg.wait_for_timeout(1800); nav(pg,'review'); pg.wait_for_timeout(600)
    print('review with bad letter card:', pg.inner_text('#app')[:80].replace('\n',' | '))
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Not yet').click()"); pg.wait_for_timeout(1800)
    print('after Not yet:', snap(pg), pg._errs[-1:])
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Not yet')?.click()"); pg.wait_for_timeout(800)
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Got it')?.click()"); pg.wait_for_timeout(800); print('Got it afterwards:', snap(pg))
    ctx.close()
    b.close()
