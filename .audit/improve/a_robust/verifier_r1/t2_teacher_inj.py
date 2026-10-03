from common import *
from t1_teacher import setup, unlock, tab
PAY='<img src=x onerror=window.__xss=1>'
with sync_playwright() as p:
    b=p.chromium.launch()
    for field in ['letters','nonwords','words','comp']:
        ctx,pg=newpage(b); setup(pg, "__put('assessments',{id:'z1',profileId:'t2',ts:Date.now()+9,%s:'%s',letters:5,nonwords:5,words:5,orf:{cwpm:40},comp:2,band:'words',by:'T'})" % (field, PAY) if False else None)
        pg.evaluate("""async([f,PAY])=>{ const r={id:'z1',profileId:'t2',ts:Date.now()+99,letters:5,nonwords:5,words:5,orf:{cwpm:40},comp:2,band:'words',by:'T'}; r[f]=PAY; await __put('assessments',r)}""",[field,PAY])
        pg.reload(); pg.wait_for_timeout(1500); unlock(pg)
        res={}
        for t in ['Class','Groups','Reports']:
            tab(pg,t); res[t]=inert(pg)[:1]
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Detail')"); 
        print(field, res, pg._errs[-1:])
        ctx.close()
    b.close()
