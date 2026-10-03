import json, sys
from lib import *
SEED = '''async () => { const {db}=await import('/src/db.js'); await db.setting('mode','school'); await db.setting('teacherPin','1234'); await db.setting('teacherName','T');
 const P=[['pA','OldBand'],['pB','OldNoBand'],['pC','UiSkipPassage'],['pD','UiCompSkipped'],['pE','UiLetterSkipped'],['pF','OldNoBandNoComp']];
 for(const [id,name] of P) await db.put('profiles',{id,kind:'learner',name,track:'child',grade:'2',createdAt:1});
 const t=Date.now();
 await db.put('assessments',{id:'a1',profileId:'pA',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:65,acc:90},comp:1,band:'fluent',by:'teacher'});
 await db.put('assessments',{id:'a2',profileId:'pB',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:45,acc:90},comp:5,by:'teacher'});
 await db.put('assessments',{id:'a6',profileId:'pF',ts:t,letters:30,nonwords:20,words:25,orf:{cwpm:0,acc:0},by:'teacher'});
}'''
R={}
def btn(pg,text,exact=True,root='#app'):
    return pg.evaluate("""([t,ex,r])=>{const b=[...document.querySelectorAll(r+' button')].find(b=>ex?b.textContent.trim()===t:b.textContent.includes(t)); if(!b) return 'missing'; if(b.disabled) return 'disabled'; b.click(); return 'ok'}""",[text,exact,root])
with sync_playwright() as p:
    b,pg=browser(p,390,900)
    pg.clock.install(time=1_700_000_000_000)
    pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{window.__shared=[]; navigator.share=async d=>{window.__shared.push(d.text)}}")
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent.includes('Teacher')).click()"); pg.wait_for_timeout(500)
    pg.fill('input[type=password]','1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Unlock').click()"); pg.wait_for_timeout(1500)
    def tab(n): pg.evaluate("n=>[...document.querySelectorAll('.tabs .tab')].find(t=>t.textContent===n).click()", n); pg.wait_for_timeout(600)
    R['tabs']=pg.evaluate("[...document.querySelectorAll('.tabs .tab')].map(t=>t.textContent)")
    def assess(name, plan):
        tab('Assess')
        pg.evaluate("n=>{const r=[...document.querySelectorAll('#app tr')].find(r=>r.children[0]&&r.children[0].textContent===n); r.querySelector('button').click()}", name); pg.wait_for_timeout(400)
        # flash subtasks 1-3
        for i,act in enumerate(plan[:3]):
            if act=='skip': btn(pg,'Skip')
            elif act=='ask0':   # time out untouched, answer 12
                pg.clock.run_for(61000); pg.wait_for_timeout(100)
                pg.fill('input[type=number]','12'); btn(pg,'Score it')
            elif act=='touch':
                pg.evaluate("document.querySelector('#app .item').click()"); pg.evaluate("document.querySelector('#app .item').click()"); pg.clock.run_for(61000); pg.wait_for_timeout(100)
            pg.wait_for_timeout(100)
        pas=plan[3]
        if pas=='skip': btn(pg,'Skip')
        elif pas=='full':
            pg.evaluate("[...document.querySelectorAll('#app .item')].slice(0,3).forEach(e=>e.click())"); btn(pg,'Mark last word reached'); pg.evaluate("document.querySelector('#app .item[data-i=\"39\"]').click()"); pg.clock.run_for(61000); pg.wait_for_timeout(100)
        elif pas=='fast': # fluent 60+
            pg.clock.run_for(20000); btn(pg,'Child finished'); btn(pg,'Read to the end')
        pg.wait_for_timeout(150)
        cm=plan[4]
        h2=pg.inner_text('#app h2')
        if 'Comprehension' in h2:
            if cm=='skip': btn(pg,'Skip')
            else:
                for i in range(5): btn(pg,'Correct' if i<cm else 'Incorrect'); pg.wait_for_timeout(40)
        pg.wait_for_timeout(150)
        res=pg.evaluate("[...document.querySelectorAll('#app tr')].map(r=>[...r.children].map(c=>c.textContent).join(' | '))")
        btn(pg,'Save assessment'); pg.wait_for_timeout(400)
        return res
    R['ui_skip_passage']=assess('UiSkipPassage',['skip','skip','skip','skip',3])
    R['ui_comp_skipped']=assess('UiCompSkipped',['touch','touch','touch','fast','skip'])
    R['ui_letter_skipped']=assess('UiLetterSkipped',['skip','touch','touch','fast',5])
    pg.evaluate("window.__shared=[]")
    def dump():
        o={}
        tab('Class'); o['class']=pg.evaluate("[...document.querySelectorAll('#app table tr')].map(r=>[...r.children].slice(0,3).map(c=>c.textContent).join(' | '))")
        tab('Groups'); o['groups']=pg.evaluate("[...document.querySelectorAll('#app .card')].map(c=>c.innerText.replace(/\\n+/g,' / ').slice(0,200))")
        tab('Reports'); o['reports']=pg.evaluate("[...document.querySelectorAll('#app table tr')].map(r=>[...r.children].map(c=>c.textContent).join(' | '))"); o['hist']=pg.evaluate("[...document.querySelectorAll('#app .card')].map(c=>c.innerText.replace(/\\n+/g,' / ').slice(0,300))").__getitem__(-1) if False else ''
        # slips
        for t in R['tabs']:
            tab(t)
            n=pg.evaluate("[...document.querySelectorAll('#app button')].filter(b=>b.textContent.trim()==='Share slip').length")
            if n:
                pg.evaluate("[...document.querySelectorAll('#app button')].filter(b=>b.textContent.trim()==='Share slip').forEach(b=>b.click())"); pg.wait_for_timeout(500); o['slips']=pg.evaluate("window.__shared"); o['slip_tab']=t; break
        return o
    R['dump']=dump()
    tab('Class')
    names=pg.evaluate("[...document.querySelectorAll('#app tr')].map(r=>r.children[0]&&r.children[0].textContent)")
    R['dash']={}
    for i,n in enumerate(names):
        if not n or n=='Name': continue
        tab('Class')
        pg.evaluate("n=>{const r=[...document.querySelectorAll('#app tr')].find(r=>r.children[0]&&r.children[0].textContent===n); [...r.querySelectorAll('button')].find(b=>b.textContent.trim()==='Detail').click()}", n); pg.wait_for_timeout(1000)
        R['dash'][n]=pg.evaluate("[...document.querySelectorAll('#child-detail table tr')].map(r=>[...r.children].map(c=>c.textContent).join(' | ')).slice(-2)")
    R['assess_records']=pg.evaluate("async()=>{const {db}=await import('/src/db.js'); return (await db.all('assessments')).map(a=>({id:a.id,p:a.profileId,orf:a.orf,orfDone:a.orfDone,comp:a.comp,compDone:a.compDone,band:a.band,level:a.level,letters:a.letters}))}")
    R['errors']=pg.errors; b.close()
json.dump(R,open('teacher_ui.json','w'),ensure_ascii=False,indent=1); print(json.dumps(R,ensure_ascii=False,indent=1))
