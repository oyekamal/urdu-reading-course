#!/usr/bin/env python3
"""Marko via perchance.org/alebrije-pic (invisible, own profile+lock). Usage: marko_gen.py <params.json>
params: {"tag":"r2","styles":["Markhor horns","Flat Vector Illustration 2"],"prompt":"...","negative":"...","count":4,"seed":null}
Writes design/gen/marko_alebrije/<tag>__k.jpg (+ <tag>.json with the seeds). Real Playwright clicks are required: JS .click() on style chips is ignored by the page."""
import os, fcntl, sys, time, base64, json
from playwright.sync_api import sync_playwright
P=json.load(open(sys.argv[1])); OUT=os.path.dirname(os.path.abspath(__file__))+'/marko_alebrije'; os.makedirs(OUT,exist_ok=True)
lk=open(os.path.expanduser("~/.kamil-harness/perchance-alebrije.lock"),"w"); t0=time.time()
while True:
    try: fcntl.flock(lk, fcntl.LOCK_EX|fcntl.LOCK_NB); break
    except OSError:
        if time.time()-t0>1200: sys.exit("lock busy")
        time.sleep(10)
if int(open(os.path.expanduser(f"~/.kamil-harness/perchance-alebrije-count-{time.strftime('%Y-%m-%d')}.txt")).read() if os.path.exists(os.path.expanduser(f"~/.kamil-harness/perchance-alebrije-count-{time.strftime('%Y-%m-%d')}.txt")) else 0) >= 250: sys.exit("daily cap")
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(os.path.expanduser("~/.kamil-harness/perchance-profile-alebrije"), headless=False, viewport={"width":1280,"height":1300})
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.goto("https://perchance.org/alebrije-pic", wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(9000)
    fr=[f for f in pg.frames if 'alebrije-pic' in f.url and f!=pg.main_frame][0]
    fr.evaluate("()=>{const b=document.getElementById('clearStylesBtn'); b&&b.click()}"); pg.wait_for_timeout(500)
    fr.click('#openStylesBtn'); pg.wait_for_timeout(1200); got=[]
    for st in P['styles']:
        fr.fill('#styleSearchIn',st); pg.wait_for_timeout(1100)
        loc=fr.locator("button:visible", has_text=st)
        if loc.count(): loc.first.click(); got.append(st); pg.wait_for_timeout(700)
    fr.locator("button:visible", has_text="Done").first.click(); pg.wait_for_timeout(800)
    if not fr.evaluate("(()=>{const e=document.getElementById('negInput'); return !!e && e.offsetParent!==null})()"): fr.click('#negToggle'); pg.wait_for_timeout(500)
    fr.fill('#negInput',P['negative'])
    n=P.get('count',4); fr.evaluate("(n)=>{const s=document.getElementById('numInput'); s.value=String(n); s.dispatchEvent(new Event('change',{bubbles:true}))}",n)
    
    if not fr.evaluate("(()=>{const e=document.getElementById('seedInput'); const d=e&&e.closest('details'); return !!e && (!d || d.open)})()"): fr.locator("summary:has-text('Advanced options')").first.click(); pg.wait_for_timeout(600)
   
    import random; fr.fill('#seedInput',str(P['seed']) if P.get('seed') else str(random.randint(1,999999999)))   # the page remembers the last seed: always set or clear it
    fr.fill('#promptInput',P['prompt']); before=set(fr.evaluate("()=>[...document.querySelectorAll('#gridEl img')].map(i=>i.src)"))
    fr.click('#genTopBtn'); t1=time.time(); imgs=[]
    while time.time()-t1<170:
        pg.wait_for_timeout(4000)
        imgs=[s for s in dict.fromkeys(fr.evaluate("()=>[...document.querySelectorAll('#gridEl img')].filter(i=>i.naturalWidth>=500&&i.src.startsWith('data:image')).map(i=>i.src)")) if s not in before]
        if len(imgs)>=n: break
    seeds=fr.evaluate("()=>[...document.querySelectorAll('#gridEl *')].map(e=>e.children.length===0?e.innerText:'').filter(t=>/seed/.test(t)).slice(0,8)")
    for i,s in enumerate(imgs): open(f"{OUT}/{P['tag']}__{i+1}.jpg",'wb').write(base64.b64decode(s.split(',',1)[1]))
    json.dump({**P,'styles_applied':got,'seeds':seeds},open(f"{OUT}/{P['tag']}.json",'w'),indent=1,ensure_ascii=False)
    cf=os.path.expanduser(f"~/.kamil-harness/perchance-alebrije-count-{time.strftime('%Y-%m-%d')}.txt"); old=int(open(cf).read()) if os.path.exists(cf) else 0; open(cf,'w').write(str(old+1))
    print('styles applied:',got,'| images:',len(imgs),'| seeds:',seeds); ctx.close()
