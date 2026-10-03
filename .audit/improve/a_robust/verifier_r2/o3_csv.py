from common import *
with sync_playwright() as p:
    b = p.chromium.launch()
    for ts in ['x', 1e20, None]:
        ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
        pg.evaluate("""async(ts)=>{await __put('settings',{key:'mode',value:'school'}); await __put('settings',{key:'teacherPin',value:'1234'}); await __put('profiles',{id:'t1',kind:'learner',name:'Bil',track:'child',grade:2,createdAt:1});
          await __put('assessments',{id:'e1',profileId:'t1',ts:ts===null?Date.now():ts,letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:'words',by:'T'}); if(ts===null) await __put('assessments',{id:'e2',profileId:'t1',ts:Date.now()+1,letters:5,nonwords:5,words:5,orf:{cwpm:30},comp:3,band:'words',by:'T',orfDone:'x'}) }""", ts); pg.reload(); pg.wait_for_timeout(1500)
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(400)
        pg.fill('input[type=password]', '1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1200)
        pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t)?.click()", 'Reports'); pg.wait_for_timeout(800)
        print('ts', ts, 'reports text', pg.inner_text('#app')[:80].replace('\n', ' | '), pg._errs[:1])
        try:
            with pg.expect_download(timeout=5000) as dl:
                pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Export CSV').click()"); gate_pass(pg)
            print('  csv ok')
        except Exception as e: print('  csv FAIL', str(e)[:60], pg._errs[:2])
        ctx.close()
    b.close()
