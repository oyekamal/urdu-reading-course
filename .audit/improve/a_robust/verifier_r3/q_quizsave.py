import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
FAULT="""window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ const tx=t.apply(this,a); if(window.__fault && a[1]==='readwrite' && [].concat(a[0]).some(n=>['progress','cards'].includes(n))) setTimeout(()=>{try{tx.abort()}catch(e){}},0); return tx}"""
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,init=FAULT); quick_profile(pg,'Zara')
    pg.evaluate("__put('progress',{id:(window.__dump? null:null)||'x',units:{}})") if False else None
    pid=pg.evaluate('__dump()')['profiles'][0]['id']
    pg.evaluate("pid=>__put('progress',{id:pid,units:{0:{passed:true,score:10,total:10,at:1}}})",pid); pg.reload(); pg.wait_for_timeout(1500)
    nav(pg,'today'); pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(800)
    pg.evaluate("[...document.querySelectorAll('.ucard')].find(u=>/Unit 1\\b/.test(u.innerText) && !u.classList.contains('locked'))?.click()"); pg.wait_for_timeout(1500)
    print('on:', pg.inner_text('#app h1')[:40], '| quiz present', pg.evaluate("!!document.querySelector('.lesson, #app')&&[...document.querySelectorAll('button')].some(b=>b.innerText==='Submit')"))
    # answer correctly
    pg.evaluate("""()=>{const ol=[...document.querySelectorAll('ol')].find(o=>o.querySelector('.tile')&&o.parentElement.querySelector('.act')); ol.querySelectorAll(':scope > li').forEach(li=>{const rom=li.querySelector('b').innerText; const t=[...li.querySelectorAll('.tile')].find(x=>x.getAttribute('aria-label')===rom); t&&t.click()})}""")
    pg.evaluate("window.__fault=true")
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Submit').click()"); pg.wait_for_timeout(2500)
    ret=pg.evaluate("[...document.querySelectorAll('button')].filter(b=>/Try saving again/.test(b.innerText)).length")
    print('score line:', pg.evaluate("document.querySelector('.score')?.innerText"), '| retry buttons:', ret, '| progress units:', list(pg.evaluate('__dump()')['progress'][0]['units'].keys()))
    pg.evaluate("window.__fault=false")
    if ret:
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Try saving again/.test(b.innerText)).click()"); pg.wait_for_timeout(2500)
        print('after retry: units', {k:v.get('passed') for k,v in pg.evaluate('__dump()')['progress'][0]['units'].items()}, 'cards', len(pg.evaluate('__dump()')['cards']), 'retry buttons left', pg.evaluate("[...document.querySelectorAll('button')].filter(b=>/Try saving again/.test(b.innerText)).length"))
