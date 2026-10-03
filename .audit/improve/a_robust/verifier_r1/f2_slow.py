from common import *
from d1_helpers import *
BLOCK = """async(ms)=>{ const d=await new Promise(r=>{const q=indexedDB.open('urdu-reader'); q.onsuccess=()=>r(q.result)}); const t=d.transaction(['progress','cards','attempts','sessions','profiles'],'readwrite'); const t0=Date.now(); const s=t.objectStore('progress'); const spin=()=>{ if(Date.now()-t0>ms) return; const r=s.get('x'); r.onsuccess=()=>spin()}; spin(); window.__blk=t; return 1}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b); quick_profile(pg,'Slow'); pg2=ctx.new_page(); pg2.goto(BASE+'manifest.webmanifest')
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
    pg.bring_to_front()
    pg2.evaluate(BLOCK, 20000)
    for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
    for t in [3,9,12]:
        pg.wait_for_timeout(3000 if t==3 else 6000 if t==9 else 3000); print(f't~{t}s:', repr(pg.inner_text('#app')[:300])); pg.screenshot(path=f'f2_{t}.png')
    pg.wait_for_timeout(9000)  # block released
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Try again')?.click()")
    try: pg.wait_for_selector('.celebrate', timeout=15000); print('retry -> celebration OK')
    except Exception as e: print('retry FAILED', pg.inner_text('#app')[:80])
    pg.wait_for_timeout(1000)
    c,d=counts(pg); print('pearls', [list(v.get('lessons',{}).keys()) for x in d['progress'] for u,v in x['units'].items()], 'errs', pg._errs)
    b.close()
