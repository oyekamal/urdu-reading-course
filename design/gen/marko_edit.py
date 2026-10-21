#!/usr/bin/env python3
"""Seed-locked edit of a Marko base on perchance.org/alebrije-pic. Usage: marko_edit.py <params.json>
params: {"tag":"e1","base":{styles,prompt,negative,seed}, "instruction":"...", "count":4}
Generates the base (count 1, fixed seed), opens its Edit panel, applies the instruction (it keeps the seed and changes only what you ask),
saves <tag>__k.jpg."""
import os, fcntl, sys, time, base64, json
from playwright.sync_api import sync_playwright
P=json.load(open(sys.argv[1])); B=P['base']; OUT=os.path.dirname(os.path.abspath(__file__))+'/marko_alebrije'; os.makedirs(OUT,exist_ok=True)
lk=open(os.path.expanduser("~/.kamil-harness/perchance-alebrije.lock"),"w"); t0=time.time()
while True:
    try: fcntl.flock(lk, fcntl.LOCK_EX|fcntl.LOCK_NB); break
    except OSError:
        if time.time()-t0>1200: sys.exit("lock busy")
        time.sleep(10)
def imgs_in(fr, sel): return list(dict.fromkeys(fr.evaluate("(s)=>[...document.querySelectorAll(s+' img')].filter(i=>i.naturalWidth>=500&&i.src.startsWith('data:image')).map(i=>i.src)", sel)))
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(os.path.expanduser("~/.kamil-harness/perchance-profile-alebrije"), headless=False, viewport={"width":1280,"height":1700})
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.goto("https://perchance.org/alebrije-pic", wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(9000)
    fr=[f for f in pg.frames if 'alebrije-pic' in f.url and f!=pg.main_frame][0]
    fr.evaluate("()=>{const b=document.getElementById('clearStylesBtn'); b&&b.click()}"); pg.wait_for_timeout(500)
    fr.click('#openStylesBtn'); pg.wait_for_timeout(1200)
    for st in B['styles']:
        fr.fill('#styleSearchIn',st); pg.wait_for_timeout(1100); loc=fr.locator("button:visible", has_text=st)
        if loc.count(): loc.first.click(); pg.wait_for_timeout(700)
    fr.locator("button:visible", has_text="Done").first.click(); pg.wait_for_timeout(800)
    if not fr.evaluate("(()=>{const e=document.getElementById('negInput'); return !!e && e.offsetParent!==null})()"): fr.click('#negToggle'); pg.wait_for_timeout(500)
    fr.fill('#negInput',B['negative'])
    fr.evaluate("()=>{const s=document.getElementById('numInput'); s.value='1'; s.dispatchEvent(new Event('change',{bubbles:true}))}")
    
    if not fr.evaluate("(()=>{const e=document.getElementById('seedInput'); const d=e&&e.closest('details'); return !!e && (!d || d.open)})()"): fr.locator("summary:has-text('Advanced options')").first.click(); pg.wait_for_timeout(600)
    fr.fill('#seedInput',str(B['seed']))
    fr.fill('#promptInput',B['prompt']); before=set(fr.evaluate("()=>[...document.querySelectorAll('#gridEl img')].map(i=>i.src)"))
    fr.click('#genTopBtn'); t1=time.time(); base=[]
    while time.time()-t1<120:
        pg.wait_for_timeout(4000); base=[s for s in imgs_in(fr,'#gridEl') if s not in before]
        if base: break
    if not base: ctx.close(); sys.exit("base failed")
    open(f"{OUT}/{P['tag']}_base.jpg",'wb').write(base[0].split(',',1)[1] and base64.b64decode(base[0].split(',',1)[1]))
    fr.locator("#gridEl button[title^='✏️']").first.click(); pg.wait_for_timeout(2500)
    fr.evaluate("(n)=>{const s=document.getElementById('editNumInput'); s.value=String(n); s.dispatchEvent(new Event('change',{bubbles:true}))}",P.get('count',4))
    fr.fill('#editInput',P['instruction']); eb=set(imgs_in(fr,'#editResultWrap')); fr.click('#editGoBtn'); t2=time.time(); res=[]
    while time.time()-t2<170:
        pg.wait_for_timeout(4000); res=[s for s in imgs_in(fr,'#editResultWrap') if s not in eb]
        if len(res)>=P.get('count',4): break
    for i,s in enumerate(res): open(f"{OUT}/{P['tag']}__{i+1}.jpg",'wb').write(base64.b64decode(s.split(',',1)[1]))
    print('base ok; edit images:',len(res)); pg.screenshot(path=f"/tmp/ur/pc/{P['tag']}.png"); ctx.close()
