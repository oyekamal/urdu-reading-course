from common import *
IDS = ['__proto__', 'constructor', 'toString', 'hasOwnProperty', 5, [1, 2], 'a:b']
with sync_playwright() as p:
    b = p.chromium.launch()
    for pid in IDS:
        for mode in ['family', 'school']:
            ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1000)
            pg.evaluate("""async([pid,mode])=>{ await __put('settings',{key:'mode',value:mode}); await __put('settings',{key:'teacherPin',value:'1234'});
              await __put('profiles',{id:pid,kind:'learner',name:'Odd',track:'child',grade:2,createdAt:1});
              await __put('progress',{id:pid,units:{0:{passed:true}},wpm:[{ts:1,wpm:30,unit:1}],sessions:1});
              await __put('attempts',{id:'a1',profileId:pid,unit:1,drill:'tell',item:'constructor',correct:false,ms:1,ts:Date.now()});
              await __put('attempts',{id:'a2',profileId:pid,unit:1,drill:'tell',item:'__proto__',correct:false,ms:1,ts:Date.now()});
              await __put('cards',{id:'k1',profileId:pid,item:'toString',kind:'word',v:'x',rom:'x',en:'x',unit:1,idx:0,box:1,due:1,seen:0});
              await __put('assessments',{id:'as1',profileId:pid,ts:Date.now(),letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:'words',by:'T'}); }""", [pid, mode])
            pg.reload(); pg.wait_for_timeout(1800)
            out = {}
            if mode == 'family':
                pg.evaluate("[...document.querySelectorAll('#app .card.btn')].find(b=>/Odd/.test(b.innerText))?.click()"); pg.wait_for_timeout(1500)
                out['open'] = pg.inner_text('#app')[:40].replace('\n', ' | ')
                for k in ['review', 'read', 'me', 'today']:
                    nav(pg, k); out[k] = pg.evaluate("document.getElementById('app').innerText.length")
            else:
                pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(500)
                pg.fill('input[type=password]', '1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1500)
                out['class'] = pg.inner_text('#app')[:140].replace('\n', ' ')
                pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Detail')?.click()"); pg.wait_for_timeout(1000); out['detail'] = pg.evaluate("document.getElementById('app').innerText.length")
                pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Open')?.click()"); pg.wait_for_timeout(1500); out['openlearner'] = pg.inner_text('#app')[:40].replace('\n', ' | ')
            print(repr(pid), mode, out, pg._errs[:2], flush=True)
            ctx.close()
    b.close()
