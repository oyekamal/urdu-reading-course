# Seed every store with payloads straight into IDB, walk every learner + teacher screen, check inertness (DOM-level) and page errors.
from common import *
import json, sys
PAYS = [
 '<img src=x onerror=window.__xss=1>',
 '"><svg onload=window.__xss=1>',
 "'><script>window.__xss=1</script>",
 '</script><script>window.__xss=1</script>',
 '&lt;img src=x onerror=window.__xss=1&gt;',
 '&#x3c;img src=x onerror=window.__xss=1&#x3e;',
 'javascript:window.__xss=1',
 '‮<b id=pwn>RTL</b>‭',
]
P = PAYS[0]
def seed(pg, pay, track='adult'):
    js = """async([pay,track])=>{
      const pid='pp1';
      await __put('profiles',{id:pid,kind:'learner',name:pay,track,grade:pay,avatar:'#fff" data-pwn="1" onmouseover="window.__xss=1',createdAt:1,goal:pay,speaks:pay,pains:[pay],minutes:pay,days:pay,unit:pay});
      await __put('profiles',{id:'pp2',kind:'learner',name:'Normal',track:'child',grade:3,createdAt:2});
      await __put('profiles',{id:'pp3',kind:'learner',name:'x'.repeat(300),track:'child',grade:1,createdAt:3});
      await __put('profiles',{id:'pp4',kind:'learner',track:'child',createdAt:4});
      await __put('attempts',{id:'a1',profileId:pid,unit:1,drill:pay,item:pay,correct:false,ms:1,ts:Date.now()});
      await __put('attempts',{id:'a2',profileId:pid,unit:1,drill:'tell',item:pay,correct:false,ms:1,ts:Date.now()});
      await __put('cards',{id:pid+':'+pay,profileId:pid,item:pay,kind:'word',v:pay,rom:pay,en:pay,unit:1,idx:0,box:1,due:1,seen:0});
      await __put('cards',{id:pid+':b',profileId:pid,item:'ب',kind:'letter',box:1,due:1,seen:0});
      await __put('sessions',{id:'s1',profileId:pid,startedAt:Date.now(),bites:pay,reviewDone:pay,correct:pay,total:pay});
      await __put('progress',{id:pid,units:{0:{passed:true,lessons:{[pay]:Date.now(),rules:Date.now()}},1:{passed:pay,score:pay}},wpm:[{ts:1,wpm:pay,unit:pay}],sessions:pay});
      await __put('assessments',{id:'as1',profileId:pid,ts:Date.now(),letters:pay,nonwords:pay,words:pay,orf:{cwpm:30,acc:pay},comp:pay,band:pay,by:pay});
      await __put('assessments',{id:'as2',profileId:'pp2',ts:Date.now(),letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:'words',by:'T'});
      await __put('settings',{key:'ui',value:{style:pay,scale:pay,spacing:pay,marks:pay}});
      await __put('settings',{key:'mode',value:'family'});
      await __put('settings',{key:'activeProfile',value:pid});
      await __put('settings',{key:'stickersSeen:'+pid,value:[pay]});
      await __put('settings',{key:'teacherName',value:pay});
    }"""
    pg.evaluate(js, [pay, track])
def walk(pg, label, issues):
    def chk(where):
        b = inert(pg)
        if b or pg.evaluate('window.__xss'): issues.append((label, where, b[:3], pg.evaluate('window.__xss')))
    pg.wait_for_timeout(1500); chk('boot')
    # learner tabs
    keys = pg.evaluate("[...document.querySelectorAll('.bottom button')].map(b=>b.dataset.k)")
    for k in keys:
        try: nav(pg, k); pg.wait_for_timeout(500); chk('tab '+k)
        except Exception as e: issues.append((label,'tab '+k,'EXC '+str(e)[:80]))
    return keys
def main():
    issues = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for i, pay in enumerate(PAYS):
            for track in ['adult', 'child']:
                ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1500)
                seed(pg, pay, track); pg.reload(); 
                keys = walk(pg, f'pay{i}/{track}', issues)
                if track=='child':
                    nav(pg,'today'); pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(500)
                # profile picker
                pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Switch profile|Zara|pp|img/.test(b.innerText)||b.classList.contains('hh-who'))?.click()"); pg.wait_for_timeout(800)
                b2 = inert(pg)
                if b2: issues.append((f'pay{i}/{track}','picker',b2[:3]))
                errs = pg._errs[:]
                if errs: issues.append((f'pay{i}/{track}', 'pageerrors', errs[:3]))
                v = csp(pg)
                print(i, track, 'keys', keys, 'csp', v[:2], 'sw', sw(pg))
                ctx.close()
        b.close()
    print('ISSUES'); [print(' ', x) for x in issues]
main()
