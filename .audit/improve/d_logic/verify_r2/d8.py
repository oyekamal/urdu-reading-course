import sys, os, json
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5460/?skiponb'
from playwright.sync_api import sync_playwright
R={}
with sync_playwright() as p:
    for label,upto in (('fresh_unit0_current',-1),('unit6_current',5),('unit6_preview',2)):
        b,pg=h.fresh2(p,'D8x')
        if upto>=0: h.tamper(pg,upto,{})
        pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(800)
        pg.evaluate("[...document.querySelectorAll('button,a')].find(b=>/All units/i.test(b.textContent))?.click()"); pg.wait_for_timeout(800)
        target = 'Unit 0' if upto<0 else 'Unit 6'
        pg.evaluate("t=>[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim().startsWith(t)).click()", target); pg.wait_for_timeout(1500)
        R[label]={'errors':pg.errors,'h1':pg.evaluate("document.querySelector('h1')?.textContent||null"),'asp_btns':pg.evaluate("document.querySelectorAll('td[id^=asp-] button').length")}
        b.close()
print(json.dumps(R,indent=1))
