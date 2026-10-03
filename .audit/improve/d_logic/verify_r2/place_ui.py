import sys, json
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5460/?skiponb'
from playwright.sync_api import sync_playwright
R={}
def run(p,label,plan):
    b,pg=h.fresh2(p,'Plc')
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/placement/i.test(b.textContent))?.click()"); pg.wait_for_timeout(800)
    asked=[]; stages=[]
    for step in range(200):
        pg.wait_for_timeout(80)
        info=pg.evaluate("""()=>{const h2=document.querySelector('#app h2')?.textContent||''; const t=[...document.querySelectorAll('#app .choices .tile')]; const right=t.find(x=>x.dataset.right); const q=document.querySelector('#app .score')?.textContent; const go=[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim()==='Go'); return {h2,n:t.length,q,hasRight:!!right,go:!!go}}""")
        if info['go']: break
        if not info['n']: continue
        key=(info['h2'],info['q'])
        if key in asked: pg.wait_for_timeout(300); continue
        asked.append(key); stage=info['h2']
        unit=int(info['h2'].split()[1]) if info['h2'].startswith('Unit') else -1
        qn=int(info['q'].split()[1]) if info['q'] else 0
        wrong = plan.get('wrong_at')==(unit,qn)
        sel="#app .choices .tile[data-right]" if not wrong else "#app .choices .tile:not([data-right])"
        pg.evaluate("s=>document.querySelector(s).click()",sel); pg.wait_for_timeout(900 if wrong else 500)
    R[label]={'asked':asked[:60],'result':pg.evaluate("document.querySelector('#app h2')?.textContent"),'sub':pg.evaluate("document.querySelector('#app .muted')?.textContent"),'errors':pg.errors}
    prog=pg.evaluate("""async()=>{const {db}=await import('/src/db.js'); const p=(await db.all('progress'))[0]; return Object.entries(p.units).filter(([k,v])=>v.passed).map(([k])=>+k)}""")
    R[label]['passed_units']=prog
    b.close()
with sync_playwright() as p:
    run(p,'wrong_at_unit3_q2',{'wrong_at':(3,2)})
    run(p,'wrong_at_unit1_q1',{'wrong_at':(1,1)})
    run(p,'all_right',{})
for k,v in R.items(): print(k,json.dumps({a:v[a] for a in ('result','sub','errors','passed_units')},ensure_ascii=False),len(v['asked']))
print(R['all_right']['asked'][-3:])
