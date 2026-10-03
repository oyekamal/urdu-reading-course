from common import *
import sys
from e1_malformed import *
n = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1000)
    pg.evaluate(BASEREC)
    pg.evaluate("async()=>{await __put('settings',{key:'mode',value:'school'}); await __put('settings',{key:'activeProfile',value:null});}")
    for store, rec in SC[n]: pg.evaluate("async([s,r])=>{ if(r.ts==='NOW') r.ts=Date.now(); await __put(s,r) }", [store, rec])
    pg.reload(); pg.wait_for_timeout(2000)
    print('home:', pg.inner_text('#app')[:100].replace('\n', ' | '), pg._errs)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(600)
    print('gate:', pg.inner_text('#app')[:100].replace('\n', ' | '), pg._errs)
    pg.fill('input[type=password]', '1234', timeout=3000); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1500)
    print('class:', pg.inner_text('#app')[:200].replace('\n', ' | '), pg._errs)
    ctx.close(); b.close()
