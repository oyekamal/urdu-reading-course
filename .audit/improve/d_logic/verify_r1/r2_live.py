import json, h, t1_real as T, t4_ui as T4
from playwright.sync_api import sync_playwright
L = json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/units.json'))['units']
out={}
with sync_playwright() as p:
    log=[]; T.ONE=True; T.BUDGET=4
    t,e = T.run_letter(p,'ب',log); out['lesson_ب']={'title':t,'errors':e,'hints':len(log),'bad':[x for x in log if x['verdict'] and x['verdict']!='no truth']}
    out['placement_all']=T4.run(p,set(c for u in L for c in u['letters'])|set('ۃ'),'liveall',1)
    out['placement_u1-3']=T4.run(p,set(c for u in L for c in u['letters'] if u['n'] in (1,2,3)),'liveu13',2)
h.save('r2_live.json',out); print(json.dumps(out,ensure_ascii=False)[:2500])
