import sys; sys.path.insert(0,'.')
from common import *
from t_teacher_add import teacher
BASE='http://localhost:5371/'
FAULT="""window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ if(window.__fault && [].concat(a[0]).includes('settings')) throw new DOMException('x','NotFoundError'); return t.apply(this,a)}"""
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,init=FAULT); teacher(pg)
    pg.fill('input[placeholder=Name]','Amna'); click(pg,"button:has-text('Add child')"); pg.wait_for_timeout(800)
    pg.evaluate("[...document.querySelectorAll('.tab')].find(x=>x.innerText==='Assess').click()"); pg.wait_for_timeout(700)
    pg.evaluate("window.__fault=true")
    click(pg,"button:has-text('Start assessment')"); pg.wait_for_timeout(2500)
    print('after start w/ settings fault:', repr(pg.inner_text('#app')[:140]), '| toast', toast(pg), '| errs', pg._errs[:2])
    pg.evaluate("window.__fault=false"); pg.wait_for_timeout(300)
    print('buttons now', pg.evaluate("[...document.querySelectorAll('#app button')].map(b=>b.innerText).slice(0,12)"))
