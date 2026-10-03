import sys; sys.path.insert(0,'.')
from common import *
from t_teacher_add import teacher
BASE='http://localhost:5371/'
def FAULT(store,how):
    body={'throw':"throw new DOMException('x','NotFoundError')",'hang':"const tx=t.apply(this,a); return new Proxy(tx,{get(o,k){const v=o[k]; return typeof v==='function'?v.bind(o):v}, set(o,k,v){ if(k==='oncomplete'||k==='onerror'||k==='onabort') return true; o[k]=v; return true}})"}[how]
    return f"window.__fault=false; const t=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){{ if(window.__fault && [].concat(a[0]).includes('{store}')) {{ {body} }} return t.apply(this,a)}}"
stores=sys.argv[1].split(',') if len(sys.argv)>1 else ['profiles','progress','assessments','attempts','cards','sessions','settings']
hows=sys.argv[2].split(',') if len(sys.argv)>2 else ['throw','hang']
with sync_playwright() as p:
    b=p.chromium.launch()
    for st in stores:
        for how in hows:
            ctx,pg=newpage(b,init=FAULT(st,how)); teacher(pg)
            pg.fill('input[placeholder=Name]','Amna'); click(pg,"button:has-text('Add child')"); pg.wait_for_timeout(800)
            pg.evaluate("window.__fault=true"); res={}
            for t in ['Class','Lesson','Groups','Assess','Reports','Device']:
                pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText===t).click()",t)
                pg.wait_for_timeout(1500 if how=='throw' else 9500)
                txt=pg.evaluate("(()=>{const a=document.getElementById('app'); const body=a.querySelector('.tabs').nextElementSibling; return (body?body.innerText.replace(/\\s+/g,' ').trim():'NOBODY').slice(0,40)})()")
                res[t]=txt or 'BLANK'
            pg.evaluate("window.__fault=false")
            print(st,how,res,'errs',len(pg._errs),flush=True); ctx.close()
