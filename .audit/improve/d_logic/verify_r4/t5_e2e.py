import sys, json
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5530/?skiponb'
from playwright.sync_api import sync_playwright
which=sys.argv[1]  # 'letter' or 'words'
unit=int(sys.argv[2]) if len(sys.argv)>2 else 1
SET='''async ([unit,which]) => { const {db}=await import('/src/db.js'); const {C,loadContent}=await import('/src/content.js'); await loadContent(); const P=await import('/src/path.js');
 const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0};
 for(let n=0;n<unit;n++) pr.units[n]={passed:true,score:10,total:10,lessons:{}};
 const u=C.units[unit]; const ls=P.lessonsFor(u); const done={};
 for (const l of ls) { if (which==='letter' ? l.kind==='letter' : l.kind==='words') break; done[l.id]=Date.now(); }
 pr.units[unit]={lessons:done}; await db.put('progress',pr); return ls.map(l=>l.id).join(','); }'''
log=[]
with sync_playwright() as p:
    b,pg=h.fresh2(p,'E2E'+which)
    ids=pg.evaluate(SET,[unit,which]); print('lessons',ids)
    pg.reload(); pg.wait_for_selector('.bottom button',timeout=30000); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('.tc-go')?.click()"); pg.wait_for_timeout(1500)
    for it in range(110):
        st=pg.evaluate("""()=>{ const app=document.querySelector('#app'); const h=(app.querySelector('h2')||app.querySelector('h1')||{}).textContent||''; const tiles=[...app.querySelectorAll('.choices .tile')]; const right=tiles.filter(t=>t.dataset.right); const btns=[...app.querySelectorAll('button')].filter(b=>!b.closest('.bottom')&&!b.disabled&&b.offsetParent).map(b=>b.textContent.trim().slice(0,22)); return {h:h.slice(0,50),nt:tiles.length,nr:right.length,btns,path:!!app.querySelector('.pearl'),trace:!!app.querySelector('.trace-wrap'),keys:app.querySelectorAll('.keys .tile').length}; }""")
        log.append(st)
        if st['path'] and it>2: break
        act=None
        if 'Build the word' in st['h'] and 'Continue' not in st['btns']:
            ok=pg.evaluate('''async (unit)=>{ const {C}=await import('/src/content.js'); const info=document.querySelector('#app .row b'); if(!info) return 'noinfo'; const rom=info.textContent; const w=C.units[unit].words.find(x=>x[1]===rom); if(!w) return 'nomatch:'+rom; const bare=t=>t.replace(/[\\u064B-\\u0652\\u0670\\u0640]/g,''); const L=[...bare(w[0])]; for(const c of L){ const t=[...document.querySelectorAll('#app .choices .tile')].find(t=>!t.disabled&&t.textContent===c); if(!t) return 'notile:'+c; t.click(); } return 'built:'+(document.querySelector('#app .answer')||{}).textContent; }''',unit)
            built=ok
            log[-1]['build']=ok
            if not str(ok).startswith('built'): print('BUILD',ok)
            # after 3 words, move on
            nb=sum(1 for l in log if l.get('build','').startswith('built'))
            pg.evaluate("[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim()==='Next word')?.click()")
            pg.wait_for_timeout(600); continue
        if st['nr']>0:
            act="document.querySelector('#app .choices .tile[data-right]').click()"
        elif st['trace']:
            # draw a stroke on the pad then continue
            pass
        if act: pg.evaluate(act)
        else:
            order=['Traced it','Continue','Skip','Next','Done','Finish','Read them','Got it','Built them','Show','Check','Start','Go','Practise','Finish unit','Submit']
            clicked=False
            for name in order:
                if any(name.lower() in x.lower() for x in st['btns']):
                    pg.evaluate("n=>{const b=[...document.querySelectorAll('#app button')].filter(b=>!b.closest('.bottom')&&!b.disabled&&b.offsetParent).find(b=>b.textContent.toLowerCase().includes(n.toLowerCase())); b&&b.click()}",name); clicked=True; break
            if not clicked and st['btns']:
                pg.evaluate("[...document.querySelectorAll('#app .btn-primary')].find(b=>b.offsetParent&&!b.disabled)?.click()")
        pg.wait_for_timeout(500)
    print('iterations',len(log),'errors',pg.errors)
    seen=[]; 
    for s in log:
        t=(s['h'],s['nt'],s['nr'],tuple(s['btns'][:6]))
        if not seen or seen[-1]!=t: seen.append(t)
    for t in seen: print(t)
    prog=pg.evaluate("async()=>{const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; const pr=await db.get('progress',prof.id); return pr.units}")
    print(json.dumps(prog)[:300])
    b.close()
