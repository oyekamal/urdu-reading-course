import json
from lib import *
JS='''async()=>{const S=await import('/src/session.js'); const {db}=await import('/src/db.js'); const Cn=await import('/src/content.js'); await Cn.loadContent();
 await db.put('profiles',{id:'p6',kind:'learner',name:'K',track:'child'}); await db.put('progress',{id:'p6',units:{0:{passed:true},1:{passed:true}},wpm:[],sessions:0});
 const out=[]; const odd=[null,undefined,5,{},[],['ب'],'', 'ب', 'بی', 'zzz', 'کتاب', NaN, true, Symbol?'x':'', '\\u0000'];
 for(const d of ['tell','blend','join','quiz','dictation','read','check','marks','sight','other']) for(const it of odd){ try{ await S.recordAttempt('p6',1,d,it,false,10); out.push(0)}catch(e){ out.push(String(e).slice(0,80)) } }
 for(const it of odd){ try{ const r=await S.missCard('p6','tell',it); }catch(e){out.push('miss:'+String(e).slice(0,80))} }
 const cards=await db.by('cards','profileId','p6'); return {thrown:out.filter(x=>x!==0), nthrown:out.filter(x=>x!==0).length, cards:cards.map(c=>[c.item,c.box,c.kind])};}'''
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500); r=pg.evaluate(JS); print(json.dumps(r,ensure_ascii=False)); print(pg.errors); b.close()
