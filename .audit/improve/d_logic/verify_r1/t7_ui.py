import json, h, t1_real as T
T.ONE=True
from playwright.sync_api import sync_playwright
STUB = "const _put=IDBObjectStore.prototype.put; IDBObjectStore.prototype.put=function(v,k){ if(window.__failcards && this.name==='cards' && v && v.lastMiss) throw new DOMException('quota','QuotaExceededError'); return _put.call(this,v,k) }"
out = {}
for fail in (False, True):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=h.EXE); ctx = b.new_context(viewport={'width':390,'height':800}); pg = ctx.new_page(); pg.errors=[]; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept()); pg.add_init_script(h.INIT); pg.add_init_script(STUB)
        pg.goto(h.URL); pg.wait_for_timeout(1500); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300); pg.fill('input[placeholder=Name]','Q'); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2300)
        info = pg.evaluate("async()=>{const {C,loadContent}=await import('/src/content.js');await loadContent();return C.units[1].letters.slice(0,1).map(c=>'L'+C.by[c].id)}")
        h.tamper(pg, 0, {'1': info})
        pg.evaluate("w=>{window.__failcards=w}", fail)
        pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1200)
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>/^(Start|Continue):/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(900)
        log=[]; T.BUDGET=5
        done=False
        for k in range(200):
            try: T.step_once(pg,'ب',log)
            except StopIteration: done=True; break
            except Exception as e: pg.wait_for_timeout(300)
        cards = pg.evaluate("async()=>{const {db}=await import('/src/db.js');const prof=(await db.all('profiles'))[0];return {cards:(await db.by('cards','profileId',prof.id)).map(c=>[c.item,c.box,c.lastMiss?1:0]),att:(await db.by('attempts','profileId',prof.id)).map(a=>[a.drill,a.item,a.correct])}}")
        out['fail' if fail else 'ok'] = {'reached_celebrate': done, 'hints': len(log), 'cards': cards['cards'], 'n_attempts': len(cards['att']), 'wrong_attempts': sum(1 for a in cards['att'] if not a[2]), 'errors': h.real_errors(pg)[:4]}
        b.close()
h.save('t7_ui.json', out); print(json.dumps(out, ensure_ascii=False, indent=1))
