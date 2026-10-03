import sys, json
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5460/?skiponb'
from lib import Pad, zs, walk, thin
import numpy as np, cv2
from playwright.sync_api import sync_playwright
R={}
with sync_playwright() as p:
    b,pg=h.fresh2(p,'Nast'); h.tamper(pg,0,{})
    pg.click(".bottom button[data-k=me]"); pg.wait_for_timeout(800)
    sels=pg.evaluate("[...document.querySelectorAll('select')].map(s=>[s.value,[...s.options].map(o=>o.value).join(',')])"); R['selects']=sels
    # find the one with naskh
    pg.evaluate("()=>{const s=[...document.querySelectorAll('select')].find(s=>[...s.options].some(o=>o.value==='nastaliq')); s.value='nastaliq'; s.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    R['body_style']=pg.evaluate("document.body.dataset.style")
    pg.click(".bottom button[data-k=today]"); pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.tc-go').click()"); pg.wait_for_timeout(800)
    # walk lesson until trace canvas appears
    for i in range(60):
        if pg.evaluate("!!document.querySelector('canvas.trace')"): break
        pg.wait_for_timeout(150)
        pg.evaluate("""()=>{const t=document.querySelector('.lesson .tile[data-right]:not(.ok)'); if(t){t.click();return} const b=[...document.querySelectorAll('.lesson button.btn-primary')].find(b=>!b.disabled&&b.offsetParent); if(b) b.click();}""")
    R['trace_found']=pg.evaluate("!!document.querySelector('canvas.trace')"); pg.wait_for_timeout(500)
    P=Pad(pg,'ا','nastaliq'); P.refresh()
    sk=zs(P.comps[0]['mask']); body=thin(walk(sk,P.dot),4)
    P.drag(body); v=P.verdict(); R['alif_nastaliq_trace']=v
    R['errors']=h.real_errors(pg); b.close()
print(json.dumps(R,ensure_ascii=False,indent=1))
