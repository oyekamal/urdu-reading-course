import sys, json, unicodedata
sys.path.insert(0,'../verify_r1')
import h
from playwright.sync_api import sync_playwright
import os
h.URL=f'http://localhost:{os.environ.get("PORT","5460")}/?skiponb'
R={}
with sync_playwright() as p:
    b,pg=h.fresh2(p,'Asp9'); h.tamper(pg,5,{})
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1000)
    pg.evaluate("[...document.querySelectorAll('button,a')].find(b=>/All units/i.test(b.textContent))?.click()"); pg.wait_for_timeout(1000)
    R['tabs_visible']=pg.evaluate("[...document.querySelectorAll('.bottom button')].map(b=>b.textContent)")
    pg.evaluate("[...document.querySelectorAll('#app button')].find(b=>/^Unit 6/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(1500)
    R['h1']=pg.inner_text('h1')[:60]
    btns=pg.query_selector_all('td[id^=asp-] button')
    R['n']=len(btns); asp=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/letters.json',encoding='utf8'))['aspirates']; out=[]
    for i,bt in enumerate(btns):
        pg.evaluate("window.__plays=[]"); pg.evaluate('e=>e.click()',bt); pg.wait_for_timeout(250)
        pl=pg.evaluate("(window.__plays||[])"); toast=pg.evaluate("document.getElementById('toast')?.className||''")
        out.append((asp[i][1],[unicodedata.normalize('NFC',x.split('/audio/')[-1]) for x in pl], toast))
    R['clicks']=out
    R['mp3']=pg.evaluate("async()=>{const o=[];for(const a of "+json.dumps([a[1] for a in asp],ensure_ascii=False)+"){const r=await fetch('audio/aspirates/'+a+'.mp3');o.push([a,r.status,r.headers.get('content-type'),(await r.arrayBuffer()).byteLength])}return o}")
    R['errors']=h.real_errors(pg); b.close()
print(json.dumps(R,ensure_ascii=False,indent=1))
