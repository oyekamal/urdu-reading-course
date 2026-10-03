import sys, json, os
sys.path.insert(0,'../verify_r1')
import h
h.URL=f'http://localhost:5460/?skiponb'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b,pg=h.fresh2(p,'Asp9'); h.tamper(pg,5,{})
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1000)
    print(pg.evaluate("[...document.querySelectorAll('button,a')].filter(b=>/All units/i.test(b.textContent)).length"))
    pg.evaluate("[...document.querySelectorAll('button,a')].find(b=>/All units/i.test(b.textContent))?.click()"); pg.wait_for_timeout(1000)
    print(pg.evaluate("[...document.querySelectorAll('#app button')].map(b=>b.textContent.trim().slice(0,30))"))
    pg.screenshot(path='dbg.png'); print(h.real_errors(pg)); print(pg.inner_text('#app')[:500])
    pg.evaluate("[...document.querySelectorAll('#app button')].find(b=>/^Unit 6/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(2000)
    print('--- after click'); print(pg.errors); print(pg.inner_text('#app')[:600]); pg.screenshot(path='dbg2.png')
