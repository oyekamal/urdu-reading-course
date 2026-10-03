from common import *
import sys, json
PAYS = {
 'img': '<img src=x onerror=window.__xss=1>',
 'attr': '" autofocus onfocus=window.__xss=1 x="',
 'sq': "' onmouseover='window.__xss=1' x='",
 'svg': '<svg/onload=window.__xss=1>',
 'ent': '&lt;img src=x onerror=window.__xss=1&gt; &#60;b id=pwn&#62;',
 'close': '</td></tr></table></div><img src=x onerror=window.__xss=1>',
 'tpl': '${window.__xss=1}`+window.__xss=1+`',
}
SEED = """async([pay,track,teacher])=>{
 const now=Date.now(); const p=pay;
 await __put('settings',{key:'mode',value: teacher?'school':'family'}); await __put('settings',{key:'activeProfile',value: teacher?null:'pp1'}); await __put('settings',{key:'teacherPin',value:'1234'});
 await __put('settings',{key:'ui',value:{style:p,scale:p,spacing:p,marks:p,rom:p}}); await __put('settings',{key:'teacherName',value:p}); await __put('settings',{key:'stickersSeen:pp1',value:[p,'ا']});
 await __put('settings',{key:'onb',value:{i:3,a:{name:p,who:p,goal:p,speak:p,colour:p,minutes:p,days:p,pains:[p],reads:p}}});
 await __put('profiles',{id:'pp1',kind:'learner',name:p,track,grade:p,avatar:p,createdAt:now-1e6,goal:p,speaks:p,pains:[p],minutes:p,days:p,unit:p,updatedAt:p});
 await __put('profiles',{id:'pp2',kind:'learner',name:'Normal',track:'child',grade:3,createdAt:2});
 await __put('profiles',{id:'pp3',kind:'learner',name:'x'.repeat(300),track:'child',grade:1,createdAt:3});
 await __put('profiles',{id:'pp4',kind:'learner',name:p,track:p,grade:p,createdAt:4});
 await __put('profiles',{id:p,kind:'learner',name:'IdPayload',track:'child',grade:2,createdAt:5});
 await __put('attempts',{id:'a1',profileId:'pp1',unit:p,drill:p,item:p,correct:false,ms:p,ts:now-1000,updatedAt:p});
 await __put('attempts',{id:'a2',profileId:'pp1',unit:1,drill:'tell',item:p,correct:false,ms:1,ts:now-500});
 await __put('cards',{id:'pp1:'+p,profileId:'pp1',item:p,kind:'word',v:p,rom:p,en:p,unit:1,idx:0,box:1,due:1,seen:0});
 await __put('cards',{id:'pp1:w2',profileId:'pp1',item:'w2',kind:p,v:p,rom:p,en:p,unit:p,idx:p,box:p,due:p,seen:p,last:p,lastOk:p,lastMiss:p});
 await __put('cards',{id:'pp1:ب',profileId:'pp1',item:'ب',kind:'letter',box:1,due:1,seen:0});
 await __put('sessions',{id:'s1',profileId:'pp1',startedAt:now-1000,endedAt:p,bites:p,reviewDone:p,correct:p,total:p});
 await __put('progress',{id:'pp1',units:{0:{passed:true,lessons:{[p]:now,rules:now},steps:{[p]:true}},1:{passed:p,score:p,total:p,at:p},[p]:{passed:true}},wpm:[{ts:p,wpm:p,unit:p},{ts:1,wpm:50,unit:1}],sessions:p,lastSession:p,updatedAt:p});
 await __put('progress',{id:'pp2',units:{0:{passed:true}},wpm:[],sessions:1});
 await __put('assessments',{id:'as1',profileId:'pp1',ts:now,letters:p,nonwords:p,words:p,orf:{cwpm:p,acc:p,seconds:p,errors:p},orfDone:p,comp:p,compDone:p,band:p,level:p,by:p,updatedAt:p});
 await __put('assessments',{id:'as2',profileId:'pp2',ts:now,letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:p,level:p,by:'T'});
 await __put('assessments',{id:'as3',profileId:'pp2',ts:now+5,letters:5,nonwords:5,words:5,orf:p,comp:p,band:'words',by:p});
}"""
def walk(pg, label, issues, teacher):
    def chk(where):
        b = inert(pg); x = pg.evaluate('window.__xss'); w = sw(pg); v = pg.evaluate('window.__csp.length')
        if b or x or w[0] > w[1] + 1: issues.append((label, where, b[:3], x, w))
    pg.wait_for_timeout(1500); chk('boot')
    if not teacher:
        keys = pg.evaluate("[...document.querySelectorAll('.bottom button')].map(b=>b.dataset.k)")
        for k in keys:
            nav(pg, k); pg.wait_for_timeout(400); chk('tab ' + k)
            if k in ('me', 'more', 'progress'):
                for rx in ['Parent report', 'Sticker', 'practice', 'Share report']:
                    try:
                        pg.evaluate("rx=>[...document.querySelectorAll('button')].find(b=>new RegExp(rx,'i').test(b.innerText))?.click()", rx); pg.wait_for_timeout(700); chk(f'{k}/{rx}')
                        pg.evaluate("()=>(document.querySelector('.stk-back, .pr-back'))?.click()"); pg.wait_for_timeout(300)
                    except Exception as e: issues.append((label, rx, 'EXC ' + str(e)[:60]))
        # lesson
        nav(pg, keys[0]); pg.evaluate("()=>document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(600); chk('units')
        pg.evaluate("()=>document.querySelector('.ucard')?.click()"); pg.wait_for_timeout(900); chk('unit-lesson')
        nav(pg, keys[0]); pg.evaluate("()=>document.querySelector('.tc-go, .dock')?.click()"); pg.wait_for_timeout(900); chk('lesson-run')
        pg.reload(); pg.wait_for_timeout(1500)
        pg.evaluate("()=>[...document.querySelectorAll('.hh-who, .page-head button')].find(b=>b)?.click()"); pg.wait_for_timeout(800); chk('picker')
    else:
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(500)
        pg.fill('input[type=password]', '1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1500)
        for t in ['Class', 'Lesson', 'Groups', 'Assess', 'Reports', 'Device']:
            pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t)?.click()", t); pg.wait_for_timeout(700); chk('T ' + t)
            if t == 'Class':
                pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.innerText==='Detail').forEach(b=>b.click())"); pg.wait_for_timeout(1200); chk('T detail')
            if t == 'Assess':
                pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Start assessment|Assess/.test(b.innerText))?.click()"); pg.wait_for_timeout(900); chk('T assess-start')
            if t == 'Reports':
                pg.evaluate("[...document.querySelectorAll('button')].filter(b=>/slip/i.test(b.innerText)).forEach(b=>b.click())"); pg.wait_for_timeout(500); chk('T slips')
if __name__ == '__main__':
    issues = []
    sel = sys.argv[1:] or list(PAYS)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for key in sel:
            for track, teacher in [('child', False), ('adult', False), ('child', True)]:
                label = f'{key}/{track}/{"teacher" if teacher else "learner"}'
                ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1300)
                pg.evaluate(SEED, [PAYS[key], track, teacher]); pg.reload()
                try: walk(pg, label, issues, teacher)
                except Exception as e: issues.append((label, 'WALK EXC', str(e)[:100]))
                v = csp(pg);
                print(label, 'csp', v[:2], 'errs', pg._errs[:2], 'sw', sw(pg), flush=True)
                ctx.close()
        b.close()
    print('ISSUES'); [print(' ', x) for x in issues]
