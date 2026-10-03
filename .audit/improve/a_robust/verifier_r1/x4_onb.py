from common import *
PAY='<img src=x onerror=window.__xss=1>'
with sync_playwright() as p:
    b=p.chromium.launch()
    for i in [3,4,5,6,7,8,9,10,11,12,13,14,15,16]:
        ctx,pg=newpage(b); pg.goto(BASE); pg.wait_for_timeout(1500)
        pg.evaluate("""async([i,PAY])=>{ await __put('settings',{key:'onb',value:{i,a:{who:'children',name:PAY,colour:'red" data-pwn="1',goal:PAY,speak:PAY,reads:PAY,pains:[PAY,'dots'],minutes:PAY,days:PAY,firstWord:true}}}) }""",[i,PAY])
        pg.reload(); pg.wait_for_timeout(2500)
        bad=inert(pg); pwn=pg.evaluate("document.body.innerHTML.includes('data-pwn')")
        if bad or pwn or pg._errs: print('onb i=',i,'inert',bad[:2],'data-pwn attr injected:',pwn,'errs',pg._errs[:1], pg.inner_text('.ob')[:40].replace('\n',' '))
        ctx.close()
    b.close()
