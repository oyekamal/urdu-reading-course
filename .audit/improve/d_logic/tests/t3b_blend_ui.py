#!/usr/bin/env python3
"""Real UI: unit 9 'Blend' lesson, 30 rounds read from the page. No round may show two tiles with the same consonant sound + vowel."""
import json
from common import *
SAME = {'ث':'س','ص':'س','ذ':'ز','ض':'ز','ظ':'ز','ط':'ت','ح':'ہ','ع':'ا'}
R = {'rounds': 0, 'bad': []}
with sync_playwright() as p:
    b, pg = fresh(p, 'Bl')
    pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const {C,loadContent}=await import('/src/content.js'); await loadContent(); const prof=(await db.all('profiles'))[0]; const pr={id:prof.id,units:{},wpm:[],sessions:0};
      for (let n=0;n<9;n++) pr.units[n]={passed:true,score:10,total:10,lessons:{}}; const u=C.units[9]; const {lessonsFor}=await import('/src/path.js'); const ls=lessonsFor(u); const bi=ls.findIndex(l=>l.kind==='blend'); pr.units[9]={lessons:Object.fromEntries(ls.slice(0,bi).map(l=>[l.id,Date.now()]))}; await db.put('progress',pr); }""")
    pg.reload(); pg.wait_for_timeout(2500)
    js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1500)
    js(pg, pg.query_selector("button:has-text('Continue:'), button:has-text('Start:')")); pg.wait_for_timeout(1200)
    R['lesson'] = pg.inner_text('#app h1')[:40]
    for _ in range(6):
        tiles = pg.query_selector_all('.choices .tile')
        if len(tiles) < 2: pg.wait_for_timeout(300); continue
        txt = [t.inner_text().strip() for t in tiles]; R['rounds'] += 1
        sig = [SAME.get(x[0], x[0]) + x[1:] for x in txt]
        if len(set(sig)) != len(sig): R['bad'].append(txt)
        right = pg.query_selector('.choices .tile[data-right]'); js(pg, right); pg.wait_for_timeout(700)
    R['page_errors'] = pg.errors; b.close()
print(R)
