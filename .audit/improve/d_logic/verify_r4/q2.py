import sys,json,unicodedata
sys.path.insert(0,'../tests')
from common import *
R={}
with sync_playwright() as p:
    b, pg = fresh(p, 'Asp')
    pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const {C,loadContent}=await import('/src/content.js'); await loadContent(); const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0};
      for (let n=0;n<6;n++) pr.units[n]={passed:true,score:10,total:10,lessons:{}}; const u=C.units[6]; pr.units[6]={lessons:{...Object.fromEntries(u.letters.map(c=>['L'+C.by[c].id,Date.now()]))}}; await db.put('progress',pr); }""")
    pg.reload(); pg.wait_for_timeout(2500)
    print([x.inner_text() for x in pg.query_selector_all('.bottom button')])
    js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1000); js(pg, pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(900)
    print(pg.inner_text('#app')[:600])
    cards=pg.query_selector_all('.ucard'); print(len(cards)); js(pg,cards[6]); pg.wait_for_timeout(1200)
    print(pg.inner_text('#app')[:800])
    el=pg.query_selector("text=Breath letters"); print('breath', bool(el))
    if el:
        js(pg, el); pg.wait_for_timeout(1000)
    print(pg.inner_text('#app h1')[:60] if pg.query_selector('#app h1') else '', len(pg.query_selector_all('#app table button.btn-play')))
    got=[]
    for bt in pg.query_selector_all('#app table button.btn-play'):
        pg.evaluate("window.__plays=[];const t=document.getElementById('toast'); if(t) t.textContent=''"); js(pg, bt); pg.wait_for_timeout(250)
        pl = pg.evaluate("(window.__plays||[]).map(x=>decodeURIComponent(x.split('/audio/')[1]))"); toast = pg.evaluate("document.getElementById('toast')?.textContent||''"); got.append((pl,toast))
    asp = [a[1] for a in json.load(open(os.path.expanduser('~/Documents/free_work/urdu-reading-course/data/letters.json'), encoding='utf8'))['aspirates']]
    ok=[len(g[0])==1 and unicodedata.normalize('NFC',g[0][0])==unicodedata.normalize('NFC',f'aspirates/{a}.mp3') and 'No audio' not in g[1] for g,a in zip(got,asp)]
    print(len(got), ok, pg.errors)
    b.close()
