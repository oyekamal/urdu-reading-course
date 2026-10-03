import json, unicodedata, h
from playwright.sync_api import sync_playwright
R={}
def check_table(pg, label):
    pg.wait_for_timeout(500)
    ids = pg.evaluate("[...document.querySelectorAll('td[id^=asp-]')].map(e=>e.id)")
    allids = pg.evaluate("[...document.querySelectorAll('[id]')].map(e=>e.id)")
    dup = sorted({i for i in allids if allids.count(i) > 1})
    btns = pg.query_selector_all('td[id^=asp-] button.btn-play')
    asp = [a[1] for a in json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/letters.json', encoding='utf8'))['aspirates']]
    out=[]
    for i, bt in enumerate(btns):
        pg.evaluate("window.__plays=[];const t=document.getElementById('toast');if(t){t.textContent='';t.classList.remove('show')}")
        pg.evaluate('e=>e.click()', bt); pg.wait_for_timeout(200)
        pl = pg.evaluate("(window.__plays||[]).map(x=>decodeURIComponent(x.split('/audio/')[1]))"); toast = pg.evaluate("document.getElementById('toast')?.textContent||''")
        # is that URL really an mp3 (not the SPA fallback)?
        url = pg.evaluate("(window.__plays||[]).slice(-1)[0]||''")
        ct = pg.evaluate("async u=>u?(await fetch(u).then(async r=>[r.status,r.headers.get('content-type'),(await r.arrayBuffer()).byteLength])):null", url)
        out.append({'i': i, 'want': asp[i], 'played': pl, 'toast': toast, 'fetch': ct})
    okc = [len(o['played'])==1 and unicodedata.normalize('NFC',o['played'][0])==unicodedata.normalize('NFC',f"aspirates/{o['want']}.mp3") and 'No audio' not in o['toast'] and o['fetch'] and o['fetch'][1].startswith('audio') and o['fetch'][2]>1000 for o in out]
    # distinct clips
    uniq = len({o['played'][0] for o in out if o['played']})
    R[label] = {'n_buttons': len(btns), 'ids_n': len(ids), 'dup_dom_ids': dup, 'all_ok': all(okc) and len(okc)==11, 'distinct_clips': uniq, 'bad': [o for o,k in zip(out,okc) if not k]}
with sync_playwright() as p:
    b, pg = h.fresh2(p, 'Asp')
    ids = pg.evaluate("async()=>{const {C,loadContent}=await import('/src/content.js');await loadContent();return C.units[6].letters.map(c=>'L'+C.by[c].id)}")
    h.tamper(pg, 5, {'6': ids})
    R['track'] = pg.evaluate("async()=>{const {db}=await import('/src/db.js');return (await db.all('profiles'))[0].track}")
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1500)
    R['dock'] = pg.evaluate("[...document.querySelectorAll('button')].map(b=>b.textContent.trim()).filter(t=>/Start|Continue/.test(t))")
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/^(Start|Continue):/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(1200)
    R['lesson_h1'] = pg.inner_text('h1')
    check_table(pg, 'lesson')
    R['lesson_errors'] = h.real_errors(pg)
    # Units tab: need non-child profile or 'All units'
    pg.reload(); pg.wait_for_timeout(2000)
    tabs = pg.evaluate("[...document.querySelectorAll('.bottom button')].map(b=>b.textContent.trim())"); R['tabs']=tabs
    if 'Units' in tabs: pg.click(".bottom button:has-text('Units')")
    else:
        pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(800)
        pg.evaluate("[...document.querySelectorAll('button,a')].find(b=>/All units/i.test(b.textContent))?.click()")
    pg.wait_for_timeout(1200); R['units_screen'] = pg.inner_text('#app')[:200]
    # find unit 6 card
    R['units_buttons'] = pg.evaluate("[...document.querySelectorAll('#app button')].map(b=>b.textContent.trim().slice(0,30))")[:40]
    b.close()
h.save('t2_asp.json', R); print(json.dumps(R, ensure_ascii=False, indent=1))
