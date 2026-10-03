#!/usr/bin/env python3
"""All 11 aspirate play buttons in the real unit-6 'Breath letters' lesson: each must request its OWN clip, none may toast 'No audio'; ids unique."""
import json
from common import *
R = {}
with sync_playwright() as p:
    b, pg = fresh(p, 'Asp')
    pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const {C,loadContent}=await import('/src/content.js'); await loadContent(); const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0};
      for (let n=0;n<6;n++) pr.units[n]={passed:true,score:10,total:10,lessons:{}}; const u=C.units[6]; pr.units[6]={lessons:{...Object.fromEntries(u.letters.map(c=>['L'+C.by[c].id,Date.now()]))}}; await db.put('progress',pr); }""")
    pg.reload(); pg.wait_for_timeout(2500)
    js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1500)
    js(pg, pg.query_selector("button:has-text('Continue:'), button:has-text('Start:')")); pg.wait_for_timeout(1200)
    R['screen'] = pg.inner_text('#app h1')[:50]
    rows = pg.query_selector_all('#app table tr'); R['rows'] = [{'row': r.inner_text().replace('\n', ' ')[:30], 'play_buttons': len(r.query_selector_all('button.btn-play'))} for r in rows]
    ids = pg.evaluate("[...document.querySelectorAll('#app table td[id^=asp-]')].map(e=>e.id)"); R['cell_ids_unique'] = len(ids) == len(set(ids)) == 11
    got = []
    for bt in pg.query_selector_all('#app table button.btn-play'):
        pg.evaluate("window.__plays=[];document.getElementById('toast')?.classList.remove('show');const t=document.getElementById('toast'); if(t) t.textContent=''"); js(pg, bt); pg.wait_for_timeout(250)
        pl = pg.evaluate("(window.__plays||[]).map(x=>decodeURIComponent(x.split('/audio/')[1]))"); toast = pg.evaluate("document.getElementById('toast')?.textContent||''")
        got.append({'played': pl, 'toast': toast})
    R['clicks'] = got; asp = [a[1] for a in json.load(open(os.path.expanduser('~/Documents/free_work/urdu-reading-course/data/letters.json'), encoding='utf8'))['aspirates']]
    import unicodedata
    ok = [len(g['played']) == 1 and unicodedata.normalize('NFC', g['played'][0]) == unicodedata.normalize('NFC', f'aspirates/{a}.mp3') and 'No audio' not in g['toast'] for g, a in zip(got, asp)]
    R['each_button_plays_its_own_clip'] = ok; R['all_pass'] = all(ok) and len(ok) == 11 and R['cell_ids_unique']; R['page_errors'] = pg.errors; b.close()
json.dump(R, open(HERE + '/t2_aspirates.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1)[:2500])
