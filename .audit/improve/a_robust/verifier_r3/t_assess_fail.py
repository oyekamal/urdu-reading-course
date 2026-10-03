import sys; sys.path.insert(0,'.')
from common import *
from t_teacher_add import teacher
BASE='http://localhost:5371/'
FAULT="""window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ const tx=t.apply(this,a); if(window.__fault && a[1]==='readwrite' && [].concat(a[0]).includes('assessments')) setTimeout(()=>{try{tx.abort()}catch(e){}},0); return tx}"""
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b,init=FAULT); teacher(pg)
    pg.fill('input[placeholder=Name]','Amna'); click(pg,"button:has-text('Add child')"); pg.wait_for_timeout(800)
    pg.evaluate("[...document.querySelectorAll('.tab')].find(x=>x.innerText==='Assess').click()"); pg.wait_for_timeout(700)
    click(pg,"button:has-text('Start assessment')"); pg.wait_for_timeout(800)
    for _ in range(6):
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText==='Skip')?.click()"); pg.wait_for_timeout(500)
    print('screen:', pg.inner_text('#app')[:100].replace('\n',' | '))
    pg.evaluate("window.__fault=true")
    click(pg,"button:has-text('Save assessment')"); pg.wait_for_timeout(2500)
    print('after failed save: toast=',toast(pg),'| save btn:', pg.evaluate("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/Save assessment/.test(b.innerText)); return b?{disabled:b.disabled}:null})()"), '| errs', pg._errs[:2])
    print('assessments in db', len(pg.evaluate('__dump()')['assessments']))
    pg.evaluate("window.__fault=false"); pg.wait_for_timeout(300)
    try: click(pg,"button:has-text('Save assessment'):not([disabled])",2000); pg.wait_for_timeout(1200); print('retry worked', len(pg.evaluate('__dump()')['assessments']))
    except Exception as e: print('no enabled Save button to retry ->', pg.inner_text('#app')[:80].replace('\n',' | '))
