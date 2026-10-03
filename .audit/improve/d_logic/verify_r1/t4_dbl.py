import json, h, t4_ui as T
from playwright.sync_api import sync_playwright
L = json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/units.json'))['units']
letters = lambda *ns: set(c for u in L if u['n'] in ns for c in u['letters'])
out=[]
with sync_playwright() as p:
    for lab,K,seed in [('dbl_all', set(c for u in L for c in u['letters']), 3), ('dbl_u1-3', letters(1,2,3), 4), ('dbl_none', set(), 5)]:
        r = T.run(p, K, lab, seed, dbl=True); out.append(r); print(json.dumps(r, ensure_ascii=False)[:600], flush=True)
h.save('t4_dbl.json', out)
