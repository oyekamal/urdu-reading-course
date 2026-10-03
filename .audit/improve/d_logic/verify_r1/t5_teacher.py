import json, h
from playwright.sync_api import sync_playwright
SEED = '''async () => { const {db}=await import('/src/db.js'); await db.setting('mode','school'); await db.setting('teacherPin','1234'); await db.setting('teacherName','T');
 const P=[['pA','OldBand'],['pB','OldNoBand'],['pC','NewLowComp'],['pD','NewCompSkipped'],['pE','NewHigh']];
 for(const [id,name] of P) await db.put('profiles',{id,kind:'learner',name,track:'child',grade:'2',createdAt:1});
 const t=Date.now();
 await db.put('assessments',{id:'a1',profileId:'pA',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:65,acc:90},comp:1,band:'fluent',by:'teacher'});
 await db.put('assessments',{id:'a2',profileId:'pB',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:45,acc:90},comp:5,by:'teacher'});
 await db.put('assessments',{id:'a3',profileId:'pC',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:70,acc:95,seconds:60,errors:2,attempted:52,capped:false},comp:2,compDone:true,band:'sentences',level:'below standard: reads fast, understands too little',by:'teacher'});
 await db.put('assessments',{id:'a4',profileId:'pD',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:70,acc:95},comp:0,compDone:false,band:'sentences',level:'fluent, comprehension not tested: not yet a standard result',by:'teacher'});
 await db.put('assessments',{id:'a5',profileId:'pE',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:95,acc:99},comp:5,compDone:true,band:'fluent',level:'exceeds grade-2 standard',by:'teacher'}); }'''
R={}
with sync_playwright() as p:
    b,pg=h.bare(p); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent.includes('Teacher')).click()"); pg.wait_for_timeout(500)
    pg.fill('input[type=password]','1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Unlock').click()"); pg.wait_for_timeout(1500)
    R['tabs']=pg.evaluate("[...document.querySelectorAll('.tabs .tab')].map(t=>t.textContent)")
    R['class']=pg.evaluate("[...document.querySelectorAll('#app table tr')].map(r=>[...r.children].slice(0,3).map(c=>c.textContent).join(' | '))")
    def tab(n): pg.evaluate("n=>[...document.querySelectorAll('.tabs .tab')].find(t=>t.textContent===n).click()", n); pg.wait_for_timeout(800)
    tab('Groups'); R['groups']=pg.evaluate("[...document.querySelectorAll('#app .card')].map(c=>c.innerText.replace(/\\n+/g,' / ').slice(0,160))")
    for t in R['tabs']:
        if t in ('Reports','Report'): tab(t); R['report']=pg.evaluate("[...document.querySelectorAll('#app table tr')].map(r=>[...r.children].map(c=>c.textContent).join(' | '))"); R['report_text']=pg.inner_text('#app')[-400:]
    # parent slip: find Share slip buttons; capture text via navigator.share stub
    pg.evaluate("()=>{window.__shared=[]; navigator.share=async d=>{window.__shared.push(d.text)}; return 1}")
    for t in R['tabs']:
        has=pg.evaluate("()=>{return 1}")
    for t in R['tabs']:
        tab(t)
        n=pg.evaluate("[...document.querySelectorAll('#app button')].filter(b=>b.textContent.trim()==='Share slip').length")
        if n:
            R['slip_tab']=t; pg.evaluate("[...document.querySelectorAll('#app button')].filter(b=>b.textContent.trim()==='Share slip').forEach(b=>b.click())"); pg.wait_for_timeout(500); R['slips']=pg.evaluate("window.__shared"); break
    # child detail dashboard
    tab('Class'); pg.evaluate("[...document.querySelectorAll('#app button')].filter(b=>b.textContent.trim()==='Detail')[3].click()"); pg.wait_for_timeout(1200)
    R['dash']=pg.evaluate("[...document.querySelectorAll('#child-detail table tr')].map(r=>[...r.children].map(c=>c.textContent).join(' | ')).slice(-3)")
    R['errors']=h.real_errors(pg); b.close()
h.save('t5_teacher.json',R); print(json.dumps(R,ensure_ascii=False,indent=1))
