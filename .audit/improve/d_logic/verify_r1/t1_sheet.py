import h
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b, pg = h.bare(p, 900, 700)
    pg.evaluate('''async()=>{const Cn=await import('/src/content.js');await Cn.loadContent();await document.fonts.load('60px "Noto Nastaliq Urdu"');await document.fonts.load('60px "Noto Naskh Arabic"');
    document.body.innerHTML='';document.body.style.background='#fff';const sel='یںئٹڈڑہھکگنبتثجخذزعحط'; 
    for(const fam of ['"Noto Naskh Arabic"','"Noto Nastaliq Urdu"']){ for(const ch of sel){ const l=Cn.C.by[ch]; const d=document.createElement('div'); d.style.cssText='display:inline-block;width:215px;font:46px '+fam+';direction:rtl;border:1px solid #ccc;margin:2px;line-height:1.8'; d.textContent=Cn.forms(l).filter(f=>f[1]).map(f=>f[1]).join(' '); document.body.append(d);} document.body.append(document.createElement('hr')); } }''')
    pg.wait_for_timeout(500); pg.screenshot(path='sheet.png', full_page=True); b.close()
