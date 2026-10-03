import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
FAULT="""window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ const tx=t.apply(this,a); if(window.__fault && a[1]==='readwrite' && [].concat(a[0]).includes('progress')) setTimeout(()=>{try{tx.abort()}catch(e){}},0); return tx}"""
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,init=FAULT); quick_profile(pg,'Zara')
    click(pg,"button:has-text('Take the placement check')"); pg.wait_for_timeout(800)
    # answer correctly until stage 1 finished? simply answer wrong at once: finish(0) -> markUnit(0)
    pg.evaluate("window.__fault=true")
    pg.evaluate("()=>{const t=[...document.querySelectorAll('.choices .tile')].find(x=>!x.dataset.right); t.click()}"); pg.wait_for_timeout(2500)
    print('after failed placement write: text', repr(pg.inner_text('#app')[:120]), '| buttons', pg.evaluate("[...document.querySelectorAll('#app button')].map(b=>b.innerText.trim().slice(0,20))"), 'errs', pg._errs[:2], 'toast', toast(pg))
