from common import *
NAMES = {'W': 'W' * 300, 'ur': 'م' * 300, 'emoji': '😀' * 150, 'spaced': 'Wide Name ' * 30, 'zalgo': 'a' + '̀́̂' * 100, 'M': 'M' * 40}
with sync_playwright() as p:
    b = p.chromium.launch()
    for k, nm in NAMES.items():
        for track, teacher in [('child', False), ('adult', False), ('child', True)]:
            ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
            pg.evaluate("""async([nm,track,teacher])=>{ await __put('settings',{key:'mode',value:teacher?'school':'family'}); await __put('settings',{key:'activeProfile',value:teacher?null:'n1'}); await __put('settings',{key:'teacherPin',value:'1234'});
              await __put('profiles',{id:'n1',kind:'learner',name:nm,track,grade:2,createdAt:1});
              await __put('profiles',{id:'n2',kind:'learner',name:'Other',track:'child',grade:2,createdAt:2});
              await __put('assessments',{id:'x1',profileId:'n1',ts:Date.now(),letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:'words',by:nm});
              await __put('progress',{id:'n1',units:{0:{passed:true}},wpm:[{ts:1,wpm:30,unit:1}],sessions:1}); }""", [nm, track, teacher]); pg.reload(); pg.wait_for_timeout(1800)
            wide = []
            def chk(w):
                s = sw(pg); 
                if s[0] > s[1]: wide.append((w, s))
            chk('boot')
            if not teacher:
                for kk in pg.evaluate("[...document.querySelectorAll('.bottom button')].map(b=>b.dataset.k)"): nav(pg, kk); chk(kk)
                pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Parent report/.test(b.innerText))?.click()"); pg.wait_for_timeout(600); chk('report')
                nav(pg, 'today'); pg.evaluate("()=>[...document.querySelectorAll('.page-head button, .hh-who')].find(b=>b)?.click()"); pg.wait_for_timeout(800); chk('picker')
            else:
                chk('home'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(400)
                pg.fill('input[type=password]', '1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1200)
                for t in ['Class', 'Groups', 'Assess', 'Reports']:
                    pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t)?.click()", t); pg.wait_for_timeout(600); chk(t)
                pg.evaluate("[...document.querySelectorAll('.tab')].find(x=>x.innerText==='Class').click()"); pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Detail')?.click()"); pg.wait_for_timeout(900); chk('detail')
            print(k, track, 'teacher' if teacher else 'learner', 'WIDE:' if wide else 'ok', wide, flush=True)
            ctx.close()
    b.close()
