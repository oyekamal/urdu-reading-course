import sys, json, unicodedata, os
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5490/?skiponb'
from playwright.sync_api import sync_playwright
R={}
asp=[a[1] for a in json.load(open('/home/oye/Documents/free_work/urdu-reading-course/data/letters.json',encoding='utf8'))['aspirates']]
R['expected']=asp
def nfc(s): return unicodedata.normalize('NFC',s)
def check_buttons(pg,label):
    out={}
    ids=pg.evaluate("[...document.querySelectorAll('td[id^=asp-]')].map(e=>e.id)")
    btns=pg.query_selector_all('td[id^=asp-] button')
    out['n_buttons']=len(btns); out['ids_unique']=len(ids)==len(set(ids)); out['n_ids']=len(ids)
    got=[]
    for bt in btns:
        pg.evaluate("window.__plays=[];const t=document.getElementById('toast'); if(t){t.textContent='';t.classList.remove('show')}")
        pg.evaluate('e=>e.click()',bt); pg.wait_for_timeout(250)
        pl=pg.evaluate("(window.__plays||[]).map(x=>decodeURIComponent(x.split('/audio/')[1]))"); tt=pg.evaluate("document.getElementById('toast')?.textContent||''")
        got.append({'played':pl,'toast':tt})
    out['clicks']=got
    out['distinct_clips']=len({tuple(g['played']) for g in got})
    out['ok_each']=[len(g['played'])==1 and 'No audio' not in g['toast'] for g in got]
    out['matches_expected']=[len(g['played'])==1 and nfc(g['played'][0])==nfc(f'aspirates/{a}.mp3') for g,a in zip(got,asp)]
    R[label]=out
with sync_playwright() as p:
    # (1) unit 6 current, via Units tab page
    b,pg=h.fresh2(p,'AspA'); h.tamper(pg,5,{})
    pg.wait_for_selector('.bottom button',timeout=20000)
    pg.evaluate("[...document.querySelectorAll('.bottom button')].find(b=>b.textContent.includes('Learn')).click()"); pg.wait_for_timeout(1000)
    pg.evaluate("[...document.querySelectorAll('button,a,.card')].find(b=>/All units/i.test(b.textContent))?.click()"); pg.wait_for_timeout(1000)
    pg.evaluate("t=>[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim().startsWith(t)).click()", 'Unit 6'); pg.wait_for_timeout(2000)
    R['units_tab_h1']=pg.evaluate("document.querySelector('h1')?.textContent")
    check_buttons(pg,'units_tab_unit6_current'); R['err_a']=pg.errors; b.close()
    # (2) unit 6 lesson in learner flow
    b,pg=h.fresh2(p,'AspB'); 
    pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0}; for(let n=0;n<6;n++) pr.units[n]={passed:true,score:10,total:10,lessons:{}}; const {C,loadContent}=await import('/src/content.js'); await loadContent(); const u=C.units[6]; pr.units[6]={lessons:Object.fromEntries(u.letters.map(c=>['L'+C.by[c].id,Date.now()]))}; await db.put('progress',pr); }""")
    pg.reload(); pg.wait_for_selector('.bottom button',timeout=20000); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('.tc-go')?.click()"); pg.wait_for_timeout(2000)
    R['lesson_h1']=pg.evaluate("document.querySelector('#app h1,#app h2')?.textContent")
    for i in range(8):
        n=pg.evaluate("document.querySelectorAll('td[id^=asp-]').length")
        if n: break
        pg.evaluate("document.querySelector('.btn-primary.btn-wide:not(.act)')?.click()"); pg.wait_for_timeout(900)
    R['lesson_found']=n
    if n: check_buttons(pg,'lesson_flow')
    R['err_b']=pg.errors; b.close()
    # (3) unit 6 preview (units 0-2 passed) via Units tab
    b,pg=h.fresh2(p,'AspC'); h.tamper(pg,2,{})
    pg.wait_for_selector('.bottom button',timeout=20000)
    pg.evaluate("[...document.querySelectorAll('.bottom button')].find(b=>b.textContent.includes('Learn')).click()"); pg.wait_for_timeout(1000)
    pg.evaluate("[...document.querySelectorAll('button,a,.card')].find(b=>/All units/i.test(b.textContent))?.click()"); pg.wait_for_timeout(1000)
    pg.evaluate("t=>[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim().startsWith(t)).click()", 'Unit 6'); pg.wait_for_timeout(2000)
    check_buttons(pg,'units_tab_unit6_preview'); R['err_c']=pg.errors; b.close()
json.dump(R,open('t4_asp.json','w'),ensure_ascii=False,indent=1)
for k in ('units_tab_unit6_current','lesson_flow','units_tab_unit6_preview'):
    if k in R: v=R[k]; print(k,v['n_buttons'],v['n_ids'],v['ids_unique'],v['distinct_clips'],all(v['matches_expected']),[g['toast'] for g in v['clicks'] if g['toast']])
print(R['lesson_found'],R['err_a'],R['err_b'],R['err_c'])
