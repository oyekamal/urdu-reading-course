#!/usr/bin/env python3
"""Verifier round-1 defects: D3 skipped passage, D5 flash subtask unknown count, D6 odd items to recordAttempt, D7 hint when no answer tile, D4 compText."""
import json
from common import *
R = {}
with sync_playwright() as p:
    b, pg = bare(p); pg.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=egra-root></div>')"); pg.clock.install()
    def start():
        pg.evaluate("""async () => { window.__res = null; const E = await import('/src/egra.js'); document.getElementById('egra-root').innerHTML=''; E.runEgra(document.getElementById('egra-root'), null, {id:'egra-p', name:'Syn'}, r => { window.__res = r; }); }"""); pg.clock.run_for(300)
    click = lambda t: (pg.click(f'#egra-root button:has-text("{t}")'), pg.clock.run_for(30))
    rows = lambda: {k.strip(): v.strip() for k, v in (r.split('\t') for r in pg.inner_text('#egra-root table').split('\n') if '\t' in r)}
    # D3
    start(); [click('Skip') for _ in range(3)]; click('Skip')
    for k in range(5): click('Correct')
    R['D3_rows'] = rows(); click('Save assessment'); pg.clock.run_for(100); R['D3_saved'] = pg.evaluate("window.__res && {orfDone:window.__res.orfDone, band:window.__res.band, level:window.__res.level}")
    R['D3_no_nonreader_flag'] = 'immediate small-group' not in pg.inner_text('#egra-root')
    # D5: nothing tapped, 60 s pass -> asked
    start(); pg.clock.run_for(60500); R['D5_asked'] = pg.is_visible('#egra-root input[type=number]'); pg.fill('#egra-root input[type=number]', '3'); click('Score it'); R['D5_next'] = pg.inner_text('#egra-root h2')
    [click('Skip') for _ in range(2)]; [click('Skip')]; 
    for k in range(5): click('Skip') if False else None
    # D5 touched path unchanged: tap one wrong then expire -> no prompt
    start(); pg.click('#egra-root .item[data-i="1"]'); pg.clock.run_for(60500); R['D5_touched_no_prompt'] = not pg.is_visible('#egra-root input[type=number]')
    R['page_errors'] = pg.errors
    # D6 + D7 + compText
    b2, pg2 = fresh(p, 'D6')
    R['D6'] = pg2.evaluate("""async () => { const {db}=await import('/src/db.js'); const S=await import('/src/session.js'); const {loadContent,compText}=await import('/src/content.js'); await loadContent(); const prof=(await db.all('profiles'))[0]; const out=[];
      for (const it of [undefined,null,42,{},'',['x'],'کی']) { try { await S.recordAttempt(prof.id,1,'blend',it,false,0); out.push('ok'); } catch(e) { out.push('THROW '+e.message); } }
      out.push(compText({comp:0,compDone:false}), compText({comp:3,compDone:true}), compText({comp:2})); return out; }""")
    pg2.evaluate("""() => { const h=document.createElement('div'); h.className='choices'; h.id='h7'; const a=document.createElement('button'), c=document.createElement('button'); a.className='tile ur'; c.className='tile ur'; a.textContent='بکرا'; c.textContent='بلی'; h.append(a,c); document.body.append(h); c.classList.add('no'); }""")
    pg2.wait_for_timeout(200); R['D7_text'] = pg2.evaluate("document.querySelector('.feel-say')?.textContent")
    R['D6_page_errors'] = pg2.errors; b2.close(); b.close()
print(json.dumps(R, ensure_ascii=False, indent=1)); json.dump(R, open(HERE + '/t8.json', 'w'), ensure_ascii=False, indent=1)
