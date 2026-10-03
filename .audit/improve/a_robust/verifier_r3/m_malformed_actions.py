import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
V={
 'assess_ts_x':[('assessments',{'id':'e1','profileId':'p1','ts':'x','letters':5,'nonwords':5,'words':5,'orf':{'cwpm':30},'comp':3,'band':'words','by':'T'})],
 'assess_ts_big':[('assessments',{'id':'e1','profileId':'p1','ts':1e20,'letters':5,'nonwords':5,'words':5,'orf':{'cwpm':30},'comp':3,'band':'words','by':'T'})],
 'assess_nums_str':[('assessments',{'id':'e1','profileId':'p1','ts':1790000000000,'letters':'x','nonwords':None,'words':{},'orf':{'cwpm':'zz','acc':'q'},'comp':'x','band':'words','by':'T'})],
 'assess_nan_inf':[('assessments',{'id':'e1','profileId':'p1','ts':1790000000000,'letters':-1e9,'nonwords':1e300,'words':5,'orf':{'cwpm':-5},'comp':99,'band':'x','by':'T'})],
 'prog_at_x':[('progress',{'id':'p1','units':{'0':{'passed':True,'at':'x','score':'x','total':'y','lessons':{'rules':'x','done':{}}}},'wpm':[{'ts':'x','wpm':50,'unit':1}],'sessions':1,'lastSession':'x'})],
 'prof_created_x':[('profiles',{'id':'p1','kind':'learner','name':'Zed','track':'child','grade':2,'createdAt':'x'})],
 'sess_x':[('sessions',{'id':'s1','profileId':'p1','startedAt':'x','endedAt':{},'bites':'x'})],
 'att_ts_big':[('attempts',{'id':'a1','profileId':'p1','unit':1,'drill':'tell','item':'ا','correct':False,'ms':5,'ts':1e20})],
 'att_ts_neg':[('attempts',{'id':'a1','profileId':'p1','unit':1,'drill':'tell','item':'ا','correct':False,'ms':-5,'ts':-1e15})],
 'card_due_x':[('cards',{'id':'p1:ب','profileId':'p1','item':'ب','kind':'letter','box':1,'due':'x','seen':0,'last':'x','lastOk':'x'})],
}
BASE_SEED="""async()=>{ await __put('settings',{key:'mode',value:'MODE'}); await __put('settings',{key:'teacherPin',value:'1234'}); await __put('settings',{key:'activeProfile',value:ACTIVE});
 await __put('profiles',{id:'p1',kind:'learner',name:'Zed',track:'child',grade:2,createdAt:1}); await __put('progress',{id:'p1',units:{0:{passed:true}},wpm:[],sessions:1}); }"""
names=sys.argv[1:] or list(V)
CLICKALL="""()=>{const out=[]; document.querySelectorAll('#app button, #app .tab').forEach(b=>{ if(/Delete|Reset|Start fresh|Export what|Switch|Lock|Back|Teacher$/.test(b.innerText)) return; try{b.click()}catch(e){out.push(String(e))} }); return out}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for name in names:
        for mode in ['learner','teacher']:
            ctx,pg=newpage(b); pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1000)
            pg.evaluate(BASE_SEED.replace('MODE','family' if mode=='learner' else 'school').replace('ACTIVE',"'p1'" if mode=='learner' else 'null')); 
            for st,rec in V[name]: pg.evaluate("([s,r])=>__put(s,r)",[st,rec])
            pg.reload(); pg.wait_for_timeout(1500)
            errs0=len(pg._errs)
            if mode=='teacher':
                pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(400)
                pg.fill('input[type=password]','1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1200)
                tabs=['Class','Lesson','Groups','Assess','Reports','Device']
                for t in tabs:
                    pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t)?.click()",t); pg.wait_for_timeout(700)
                    pg.evaluate("[...document.querySelectorAll('button')].filter(b=>/Detail|Share slip/.test(b.innerText)).forEach(b=>b.click())"); pg.wait_for_timeout(500)
                # CSV via gate
                pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t)?.click()",'Reports'); pg.wait_for_timeout(600)
                try:
                    with pg.expect_download(timeout=4000):
                        pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Export CSV').click()"); gate_pass(pg)
                    csv='ok'
                except Exception as e: csv='NO DOWNLOAD'
            else:
                keys=pg.evaluate("[...document.querySelectorAll('.bottom button')].map(b=>b.dataset.k)")
                for k in keys:
                    nav(pg,k); pg.wait_for_timeout(500)
                    pg.evaluate("()=>[...document.querySelectorAll('#app button')].filter(b=>/Parent report|Share report|Sticker/i.test(b.innerText)).forEach(b=>b.click())"); pg.wait_for_timeout(600)
                    pg.evaluate("()=>document.querySelector('.stk-back, .pr-back')?.click()")
                csv='-'
            new=pg._errs[errs0:]
            blank=pg.evaluate("document.getElementById('app').innerText.trim().length")
            print(f'{name:16s} {mode:8s} pageerrors={new[:3]} csv={csv} appTextLen={blank} recovery={bool(pg.query_selector(".recovery"))}',flush=True); ctx.close()
