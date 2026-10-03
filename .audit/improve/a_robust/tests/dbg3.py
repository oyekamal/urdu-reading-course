import os
os.environ['BASE']='http://localhost:5188/'
from common import *
with sync_playwright() as p:
    b = p.chromium.launch(); ctx, pg = newpage(b); quick_profile(pg, 'J')
    pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    pg.evaluate("""async pid=>{const S=await import('/src/session.js');const P=await import('/src/path.js');const {db}=await import('/src/db.js');const {C,loadContent}=await import('/src/content.js'); await loadContent();
      await __put('progress',{id:pid,units:{'0':{passed:true,score:10,total:10}},wpm:[],sessions:0});
      const u=C.units[1];const ls=P.lessonsFor(u);const done={};for(const l of ls){if(l.id==='join')break;done[l.id]=Date.now()} const p=await S.getProgress(pid);p.units[1]={...(p.units[1]||{}),lessons:done};await db.put('progress',p)}""", pid)
    pg.reload(); pg.wait_for_timeout(2000)
    click(pg, "button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(800)
    print(pg.inner_text('#app')[:80].replace('\n',' | '))
    for _ in range(2):
        click(pg, '.lesson .btn-primary'); pg.wait_for_timeout(500)
    print(pg.inner_text('#app')[:120].replace('\n',' | '))
    for k in range(40):
        if pg.query_selector('.lesson .btn-primary.btn-wide'): print('continue at', k); break
        ts = pg.query_selector_all('.choices .tile:not([disabled]):not(.no):not(.ok)')
        if not ts:
            n = pg.query_selector("button:has-text('Next word')")
            if n: pg.evaluate('e=>e.click()', n)
            pg.wait_for_timeout(300); continue
        pg.evaluate('e=>e.click()', ts[k % len(ts)]); pg.wait_for_timeout(260)
    print(pg.inner_text('#app')[:200].replace('\n',' | ')); print(pg._errs)
    print(pg.evaluate("[...document.querySelectorAll('.tile')].map(t=>t.className+':'+t.disabled)"))
