import json, h
from playwright.sync_api import sync_playwright
SS={'ث':'س','ص':'س','ذ':'ز','ض':'ز','ظ':'ز','ط':'ت','ح':'ہ','ع':'ا'}
rounds=[]
with sync_playwright() as p:
    for run in range(5):
        for unit in (9, 8, 5):
            b, pg = h.fresh2(p, f'B{run}{unit}')
            ids = pg.evaluate("async(n)=>{const {C,loadContent}=await import('/src/content.js');await loadContent();const u=C.units[n];return {l:u.letters.map(c=>'L'+C.by[c].id)}}", unit)
            h.tamper(pg, unit-1, {str(unit): ids['l']+['join']})
            pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1000)
            pg.evaluate("[...document.querySelectorAll('button')].find(b=>/^(Start|Continue):/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(800)
            title = pg.inner_text('h1')
            for k in range(14):
                r = pg.evaluate("""()=>{const t=[...document.querySelectorAll('.lesson .choices .tile')]; if(t.length<2) return null; const right=t.find(x=>x.dataset.right); if(!right) return null; if(t.some(x=>x.classList.contains('ok'))) return {busy:1}; const txt=t.map(x=>x.textContent.trim()); right.click(); return {txt, right:right.textContent.trim(), key:right.dataset.right}}""")
                if r and not r.get('busy'): rounds.append({'unit':unit,'title':title,**r}); pg.wait_for_timeout(700)
                else: pg.wait_for_timeout(250)
            b.close()
bad=[]
for r in rounds:
    sn=[SS.get(t[0],t[0])+t[1:] for t in r['txt']]
    if len(set(sn))!=len(sn) or r['txt'].count(r['right'])!=1: bad.append(r)
print(len(rounds),'rounds', {u:sum(1 for r in rounds if r['unit']==u) for u in (9,8,5)}, 'titles', {r['title'] for r in rounds}); print('bad',bad[:5]); print(rounds[:3])
h.save('t3_ui.json',{'rounds':rounds,'bad':bad})
