import sys
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5490/?skiponb'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b,pg=h.fresh2(p,'Probe')
    pg.wait_for_timeout(1500)
    print(pg.evaluate("[...document.querySelectorAll('button')].map(b=>b.className+':'+b.textContent.trim().slice(0,30))"))
    print(pg.evaluate("document.querySelector('.bottom')?.outerHTML.slice(0,600)"))
    print(pg.inner_text('#app')[:300]); print(pg.errors)
    b.close()
