import json, h
from playwright.sync_api import sync_playwright
out={}
with sync_playwright() as p:
    b, pg = h.fresh2(p, 'Jn2')
    ids = pg.evaluate("async()=>{const {C,loadContent}=await import('/src/content.js');await loadContent();return C.units[2].letters.map(c=>'L'+C.by[c].id)}")
    h.tamper(pg, 1, {'2': ids})
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1200)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/^(Start|Continue):/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(900)
    out['lesson']=pg.inner_text('h1')
    pg.evaluate("[...document.querySelectorAll('.lesson button.btn-primary')].slice(-1)[0].click()"); pg.wait_for_timeout(800)
    out['card']=pg.inner_text('.lesson h2')
    # joinIt: tiles are shuffled letters of the word; click tiles until one goes 'no'
    seen=[]
    for rep in range(3):
        tiles=pg.query_selector_all('.lesson .choices .tile')
        for t in tiles:
            if t.is_disabled(): continue
            t.click(); pg.wait_for_timeout(250)
            if 'no' in (t.get_attribute('class') or '').split():
                s=pg.query_selector('.feel-say'); seen.append({'wrong':t.inner_text(),'hint':s.inner_text() if s else None,'green':pg.evaluate("[...document.querySelectorAll('.tile.feel-answer')].length")}); break
        break
    out['joinIt']=seen; out['errors']=h.real_errors(pg); b.close()
print(json.dumps(out,ensure_ascii=False,indent=1))
h.save('t1_nogreen2.json',out)
