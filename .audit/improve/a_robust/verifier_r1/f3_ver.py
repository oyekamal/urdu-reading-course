from common import *
from d1_helpers import *
def txt(pg): return pg.inner_text('#app')[:150].replace('\n',' | ')
with sync_playwright() as p:
    b=p.chromium.launch()
    # (1) DB at v99 missing stores, other tab holds it open (no versionchange handler) -> repair blocked
    ctx,pg=newpage(b); quick_profile(pg,'Ver'); pg.close()
    pg2=ctx.new_page(); pg2.goto(BASE+'manifest.webmanifest')
    pg2.evaluate("""()=>new Promise(r=>{const q=indexedDB.open('urdu-reader',99);q.onupgradeneeded=()=>{q.result.deleteObjectStore('progress');q.result.deleteObjectStore('cards')};q.onsuccess=()=>{window.__hold=q.result; r()};q.onerror=()=>r()})""")
    pg3=ctx.new_page(); pg3.on('pageerror', lambda e: print('PE',e)); pg3.add_init_script(IDB); pg3.goto(BASE); 
    pg3.wait_for_timeout(6000); print('(1) blocked repair after 6s:', txt(pg3))
    pg3.wait_for_timeout(8000); print('(1) after 14s:', txt(pg3))
    pg2.evaluate("window.__hold.close()"); 
    pg3.evaluate("()=>[...document.querySelectorAll('.recovery button')][0]?.click()"); pg3.wait_for_timeout(3000); print('(1) after releasing + Try again:', txt(pg3))
    ctx.close()
    # (2) records with keyPath of wrong type / garbage in every store
    ctx,pg=newpage(b); quick_profile(pg,'Gar')
    pg.evaluate("""async()=>{ const bad=[1,2,[3],{a:1},true,null]; let i=0;
      for(const s of ['profiles','attempts','cards','sessions','progress','assessments']){ for(const b of [5,[1],{x:1},true]) { try{ await __put(s,{id:b,profileId:b,name:b,track:b,ts:b,units:b,wpm:b,orf:b,band:b,by:b,item:b,kind:b,due:b,box:b,seen:b}) }catch(e){} } }
      await __put('settings',{key:'ui',value:'garbage'}); await __put('settings',{key:'mode',value:{x:1}}); await __put('settings',{key:'activeProfile',value:{x:1}});
      await __put('settings',{key:'teacherPin',value:1234}); }""")
    pg.reload(); pg.wait_for_timeout(2500); print('(2) garbage everywhere ->', txt(pg), pg._errs[-2:])
    ctx.close()
    # (3) activeProfile points to profile that does not exist; mode school without pin
    ctx,pg=newpage(b); quick_profile(pg,'Orph'); pg.evaluate("__put('settings',{key:'activeProfile',value:'nope'})"); pg.reload(); pg.wait_for_timeout(2000); print('(3) orphan active:', txt(pg))
    ctx.close()
    b.close()
