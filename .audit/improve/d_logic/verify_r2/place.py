import json
from lib import *
JS='''async()=>{const D=await import('/src/drills.js');const Cn=await import('/src/content.js');await Cn.loadContent();const C=Cn.C;const out={};
 const taught=k=>C.units.filter(u=>u.n<=k).flatMap(u=>u.letters).filter(c=>C.by[c]);
 for(const u of C.units){ if(!u.letters.length) {out[u.n]={noletters:true};continue}
  let pass1=0,N=3000,nOpt=new Set(),repeat=0,missingLetter=0,words=new Set(),itemCounts=new Set(),badRight=0,dupOpt=0,wordOptsBad=0;
  for(let t=0;t<N;t++){ const it=D.placementItems(u,taught(u.n),()=>false); itemCounts.add(it.length);
    const ls=it.filter(x=>x.kind==='letter'); const ws=it.filter(x=>x.kind==='word'); words.add(ws.length);
    const tg=ls.map(x=>x.target); if(new Set(tg).size!==tg.length) repeat++; if(u.letters.filter(c=>C.by[c]).some(c=>!tg.includes(c))) missingLetter++;
    for(const x of it){ nOpt.add(x.options.length); if(x.options.filter(o=>o.right).length!==1) badRight++; if(new Set(x.options.map(o=>o.text)).size!==x.options.length) dupOpt++; }
    // learner who misses exactly one random LETTER (guess) 
    const k=Math.floor(Math.random()*ls.length); let ok=true; for(let i=0;i<it.length;i++){ if(it[i]===ls[k]){ const g=it[i].options[Math.floor(Math.random()*it[i].options.length)]; if(!g.right) ok=false } }
    if(ok) pass1++; }
  out[u.n]={letters:u.letters.length,items:[...itemCounts],words:[...words],nOpt:[...nOpt],repeat,missingLetter,badRight,dupOpt,pass1:pass1/N};
 } return out}'''
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500); r=pg.evaluate(JS); b.close()
for k,v in r.items(): print(k,v)
json.dump(r,open('place.json','w'),indent=1)
