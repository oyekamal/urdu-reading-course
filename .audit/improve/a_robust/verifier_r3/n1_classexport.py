import sys; sys.path.insert(0,'.')
from common import *
import json
BASE='http://localhost:5371/'
# a school roster that has progressed: NP profiles, each with cards for every item of the course (what ensureCards makes at the end)
NP=int(sys.argv[1]) if len(sys.argv)>1 else 60
SEED="""async([np,items])=>{ const now=Date.now();
 await __put('settings',{key:'mode',value:'family'});
 for(let i=0;i<np;i++){ const pid='p'+i; await __put('profiles',{id:pid,kind:'learner',name:'Kid '+i,track:'child',grade:'2',createdAt:now});
   const d=await new Promise(r=>{const q=indexedDB.open('urdu-reader');q.onsuccess=()=>r(q.result)});
   await new Promise(r=>{const t=d.transaction('cards','readwrite');const s=t.objectStore('cards'); items.forEach((it,j)=>s.put({id:pid+':'+it,profileId:pid,item:it,kind:'word',v:it,rom:'r',en:'e',unit:1,idx:j,box:1,due:now,seen:0,updatedAt:now})); t.oncomplete=r}); d.close(); }
}"""
U=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/units.json'))['units']
L=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/letters.json'))
items=[]
for u in U:
    items+=u['letters']; items+=[w[0] for w in u['words']]
items+=L['sight_words']; items=list(dict.fromkeys(items)); print('items per learner',len(items))
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b); pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500)
    pg.evaluate(SEED,[NP,items]); pg.reload(); pg.wait_for_timeout(1500)
    print('cards in db',counts(pg)[0])
    # export through the app (More tab of a learner is gated; use db via UI)
    click(pg,'text=Just me') if pg.query_selector('text=Just me') else None
    pg.wait_for_timeout(500); print(pg.inner_text('#app')[:120].replace('\n',' | '))
    ctx.close()
