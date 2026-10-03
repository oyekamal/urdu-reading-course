import json, h
from playwright.sync_api import sync_playwright
JS = r'''async () => {
 const {db} = await import('/src/db.js'); const S = await import('/src/session.js'); const Cn = await import('/src/content.js'); await Cn.loadContent(); const C = Cn.C;
 const prog=async pid=>db.put('progress',{id:pid,units:Object.fromEntries([...Array(12).keys()].map(n=>[n,{passed:true,score:10,total:10}])),wpm:[],sessions:0}); for(const q of ['pA','pB','pC','pD','pE']) await prog(q);
 const DAY=86400000, BOX=[0,1,2,4,8,16]; const R={}; const fails=[];
 const chk=(c,m)=>{ if(!c) fails.push(m); return c; };
 // ---- A. gradeCard sequences
 let pid='pA'; await S.ensureCards(pid, 4); let all=await db.by('cards','profileId',pid); const b0=all.find(c=>c.kind==='letter');
 let card=await db.get('cards',b0.id); const seq=[true,true,true,true,true,true,false,true,false,false,true]; const trace=[]; let expBox=card.box;
 for(const ok of seq){ const t0=Date.now(); await S.gradeCard(card, ok); card=await db.get('cards',b0.id); expBox = ok?Math.min(expBox+1,5):1;
   const days=(card.due-t0)/DAY; trace.push([ok,card.box,+days.toFixed(3)]); chk(card.box===expBox,'gradeCard box '+ok+' got '+card.box+' want '+expBox); chk(Math.abs(days-BOX[expBox])<0.01,'gradeCard due '+days+' for box '+expBox); chk(card.lastOk===ok,'lastOk'); }
 chk(card.seen===seq.length,'seen '+card.seen); R.gradeTrace=trace;
 // ---- B. dueCards ordering vs brute force
 pid='pB'; await S.ensureCards(pid, 10); all=await db.by('cards','profileId',pid); const now=Date.now();
 let i=0; for(const c of all){ i++; await db.put('cards',{...c, box:1+(i*7)%5, due: now + ((i*13)%9-4)*DAY*0.37}); }
 all=await db.by('cards','profileId',pid); const want=all.filter(c=>c.due<=Date.now()).sort((a,b)=>a.box-b.box||a.due-b.due);
 for(const lim of [1,5,12,30,1000]){ const got=await S.dueCards(pid,lim); chk(JSON.stringify(got.map(c=>c.id))===JSON.stringify(want.slice(0,lim).map(c=>c.id)),'dueCards order lim '+lim); }
 R.due={n:want.length,total:all.length};
 // ---- C. ensureCards idempotent, no clobber, unique ids
 pid='pC'; await S.ensureCards(pid,12); const n1=(await db.by('cards','profileId',pid)); await S.ensureCards(pid,12); const n2=(await db.by('cards','profileId',pid));
 chk(n1.length===n2.length,'ensureCards not idempotent '+n1.length+' '+n2.length); chk(new Set(n2.map(c=>c.id)).size===n2.length,'dup ids');
 const sw=new Set(C.letters.sight_words); const unitWords=new Map(); C.units.forEach(u=>u.words.forEach(w=>{ if(!unitWords.has(w[0])) unitWords.set(w[0],u.n); }));
 const overlap=[...sw].filter(w=>unitWords.has(w)); R.sight_unitword_overlap=overlap;
 R.overlap_kinds=overlap.map(w=>{ const c=n2.find(x=>x.item===w); return c&&[w,c.kind,c.unit,c.idx]; });
 // dup items among cards with different ids?
 const items=n2.map(c=>c.item); chk(new Set(items).size===items.length,'duplicate item cards');
 const c5=n2.find(c=>c.kind==='word'); await db.put('cards',{...c5,box:4,seen:9}); await S.ensureCards(pid,12); chk((await db.get('cards',c5.id)).box===4,'ensureCards clobbered a card');
 R.counts={cards:n2.length};
 // ---- D. missCard semantics
 pid='pD'; await S.ensureCards(pid,5); const L=(await db.by('cards','profileId',pid)).filter(c=>c.kind==='letter'); const W=(await db.by('cards','profileId',pid)).filter(c=>c.kind==='word');
 const lc=L[0], wc=W[0]; const T=Date.now();
 // far-future box 5 card -> miss
 await db.put('cards',{...lc,box:5,due:T+16*DAY,seen:4}); await S.recordAttempt(pid,2,'tell',lc.item,false,10); let x=await db.get('cards',lc.id);
 chk(x.box===1,'miss box'); chk(x.due-T<=DAY+2000,'miss due within a day '+(x.due-T)/DAY); chk(x.seen===4,'miss changed seen');
 // already overdue -> must not be postponed
 await db.put('cards',{...lc,box:3,due:T-3*DAY,seen:4}); await S.recordAttempt(pid,2,'tell',lc.item,false,10); x=await db.get('cards',lc.id); chk(x.due===T-3*DAY,'postponed overdue card'); chk(x.box===1,'overdue box');
 // due in 3 hours -> keeps 3 hours
 await db.put('cards',{...lc,box:2,due:T+3*3600e3,seen:1}); await S.recordAttempt(pid,2,'check',lc.item,false,10); x=await db.get('cards',lc.id); chk(x.due===T+3*3600e3,'postponed earlier due');
 // correct answer: untouched
 await db.put('cards',{...lc,box:4,due:T+8*DAY,seen:2,last:5}); const before=JSON.stringify(await db.get('cards',lc.id)); await S.recordAttempt(pid,2,'tell',lc.item,true,10); chk(JSON.stringify(await db.get('cards',lc.id))===before,'correct answer changed card');
 // card missing -> created
 await db.del('cards',lc.id); await S.recordAttempt(pid,2,'tell',lc.item,false,10); x=await db.get('cards',lc.id); chk(x&&x.kind==='letter'&&x.box===1&&x.seen===0,'letter card not created'); 
 await db.del('cards',wc.id); for (const d of ['read','quiz','dictation','join','marks']) { await db.del('cards',wc.id); await S.recordAttempt(pid,3,d,wc.item,false,1); x=await db.get('cards',wc.id); chk(x&&x.kind==='word'&&x.box===1&&x.unit!=null&&x.idx!=null&&x.v&&x.rom,'word card create via '+d+' '+JSON.stringify(x)); }
 // audio keys valid for created cards
 chk(!!Cn.C.audio[S.audioKeyFor(x)],'audio key for created word card '+S.audioKeyFor(x));
 // blend miss sends the letter back
 const bl=C.units[2].letters[0]; await db.del('cards',pid+':'+bl); await S.recordAttempt(pid,2,'blend',bl+'ا',false,0); x=await db.get('cards',pid+':'+bl); chk(x&&x.kind==='letter','blend miss');
 // sight
 const sgt=C.letters.sight_words[3]; await db.del('cards',pid+':'+sgt); await S.recordAttempt(pid,11,'sight',sgt,false,0); x=await db.get('cards',pid+':'+sgt); R.sight_card=x&&[x.kind,x.unit,x.idx]; chk(x && !!Cn.C.audio[S.audioKeyFor(x)],'sight card audio '+(x&&S.audioKeyFor(x)));
 // attempts recorded
 const atts=await db.by('attempts','profileId',pid); R.attempts=atts.length; chk(atts.filter(a=>a.correct===false).length>=10,'attempts lost');
 // ---- E. odd items
 const odd=['', undefined, null, 'ببب', 'تَپْتا', 'اَبّا', 'ا', 'کیا', 'x'.repeat(5000), 42, {a:1}, [], '🙂', ' ', 'ب ا', '__proto__', 'constructor', 'toString'];
 const drills=['tell','join','quiz','dictation','read','blend','check','marks','sight','trace','self-letters','constructor','toString','__proto__',undefined,null,''];
 const thrown=[]; pid='pE';
 for(const d of drills) for(const it of odd){ try{ await S.recordAttempt(pid,1,d,it,false,0); await S.recordAttempt(pid,1,d,it,true,0);}catch(e){ thrown.push([String(d),typeof it==='string'?it.slice(0,8):String(it),String(e).slice(0,60)]); } }
 R.thrown=thrown; R.thrown_n=thrown.length;
 const cards=await db.by('cards','profileId',pid); R.odd_cards=cards.length; const bad=cards.filter(c=>!c.item||c.id!==pid+':'+c.item||!(c.box>=1&&c.box<=5)||!(c.due>0)||c.profileId!==pid); R.bad_cards=bad.slice(0,5);
 // ---- F. sight==unit word identity
 R.fails=fails; return R; }'''
with sync_playwright() as p:
    b, pg = h.bare(p); r = pg.evaluate(JS); print(json.dumps(r, ensure_ascii=False, indent=1)[:5000]); h.save('t7_sr_live.json', r); print('page errors', h.real_errors(pg)); b.close()
