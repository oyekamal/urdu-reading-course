from common import *
PAY='<img src=x onerror=window.__xss=1>'
with sync_playwright() as p:
    b=p.chromium.launch()
    for label, js in [
      ('attempt.item', "__put('attempts',{id:'a1',profileId:'pp1',unit:1,drill:'tell',item:PAY,correct:false,ms:1,ts:Date.now()})"),
      ('assessment.band', "__put('assessments',{id:'as1',profileId:'pp1',ts:Date.now(),orf:{cwpm:30},band:PAY,by:'x'})"),
      ('assessment.by', "__put('assessments',{id:'as1',profileId:'pp1',ts:Date.now(),orf:{cwpm:30},band:'words',by:PAY})"),
      ('card.item(kind word)', "__put('cards',{id:'pp1:q',profileId:'pp1',item:PAY,kind:'word',v:PAY,rom:PAY,en:PAY,unit:1,idx:0,box:1,due:1,seen:0})"),
      ('profile.goal etc', "__put('profiles',{id:'pp1',kind:'learner',name:'A',track:'adult',goal:PAY,speaks:PAY,pains:[PAY],createdAt:1})"),
      ('onb colour/minutes', "__put('settings',{key:'onb',value:{i:11,a:{who:'me',name:'A',colour:'red\" data-pwn=\"1',minutes:PAY,days:PAY,goal:PAY,speak:PAY,reads:PAY,pains:[PAY]}}})"),
    ]:
        ctx,pg=newpage(b)
        pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1200)
        pg.evaluate("__put('profiles',{id:'pp1',kind:'learner',name:'A',track:'adult',createdAt:1})")
        pg.evaluate("__put('settings',{key:'mode',value:'personal'})"); pg.evaluate("__put('settings',{key:'activeProfile',value:'pp1'})")
        if label.startswith('onb'):
            pg.evaluate("__dump().then(d=>0)"); 
            pg.evaluate("(async()=>{const d=await new Promise(r=>{const q=indexedDB.open('urdu-reader');q.onsuccess=()=>r(q.result)});await new Promise(r=>{const t=d.transaction('profiles','readwrite');t.objectStore('profiles').delete('pp1');t.oncomplete=r});await new Promise(r=>{const t=d.transaction('settings','readwrite');t.objectStore('settings').delete('mode');t.oncomplete=r});})()")
        pg.evaluate("PAY=>{window.PAY=PAY}",PAY)
        pg.evaluate("(js)=>eval(js)" , "0")  # eval blocked by CSP? (expected)
        r=pg.evaluate("""async([src,PAY])=>{ const f=new Function('PAY','return '+src) ; return 1}""",[js,PAY]) if False else None
        # run via a closure-free approach: build call by string substitution
        code=js.replace('PAY',repr(PAY).replace("'",'"') if False else '__P')
        pg.evaluate("p=>{window.__P=p}",PAY)
        # Playwright evaluate evaluates expression strings in page context: allowed (CDP), not CSP-bound
        pg.evaluate(code)
        pg.reload(); pg.wait_for_timeout(1800)
        res={}
        if label.startswith('onb'):
            res['onb']=inert(pg)
            pg.wait_for_timeout(200)
            res['html']=pg.evaluate("document.querySelector('#app').innerHTML.includes('data-pwn')")
        else:
            nav(pg,'progress'); res['progress']=inert(pg)[:2]; nav(pg,'more'); res['more']=inert(pg)[:2]
        print(label, res, pg._errs[:2])
        ctx.close()
    b.close()
