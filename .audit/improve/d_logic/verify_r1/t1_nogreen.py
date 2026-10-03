import json, h
from playwright.sync_api import sync_playwright
out={}
with sync_playwright() as p:
    b, pg = h.fresh2(p, 'Jn')
    ids = pg.evaluate("async()=>{const {C,loadContent}=await import('/src/content.js');await loadContent();return C.units[1].letters.map(c=>'L'+C.by[c].id)}")
    h.tamper(pg, 0, {'1': ids})
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1200)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/^(Start|Continue):/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(900)
    out['lesson']=pg.inner_text('h1')
    pg.evaluate("[...document.querySelectorAll('.lesson button.btn-primary')].slice(-1)[0].click()"); pg.wait_for_timeout(800)   # to the joinIt screen
    out['card']=pg.inner_text('.lesson h2')
    tiles=pg.query_selector_all('.lesson .choices .tile')
    out['n_tiles']=len(tiles)
    # which is the right next letter? read the 'Make:' prompt; we just tap tiles until one goes 'no'
    for t in tiles:
        t.click(); pg.wait_for_timeout(250)
        cls=t.get_attribute('class'); 
        if 'no' in cls.split():
            out['wrong_tile']=t.inner_text(); out['hint']=(pg.query_selector('.feel-say').inner_text() if pg.query_selector('.feel-say') else None)
            out['green_tiles']=pg.evaluate("[...document.querySelectorAll('.tile.feel-answer, .tile.ok')].map(t=>t.textContent+':'+t.className)")
            break
    out['errors']=h.real_errors(pg); b.close()
print(json.dumps(out,ensure_ascii=False,indent=1)); h.save('t1_nogreen.json',out)
