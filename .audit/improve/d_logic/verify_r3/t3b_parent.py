import sys, json
sys.path.insert(0,'../verify_r1')
import h
h.URL='http://localhost:5490/?skiponb'
from playwright.sync_api import sync_playwright
CASES={'old_noband_65_c1':dict(orf={'cwpm':65,'acc':90},comp=1),'new_notested':dict(orf={'cwpm':0,'acc':0},orfDone=False,comp=5,compDone=True,band='not tested',level='x'),'legacy_fluent_c1':dict(orf={'cwpm':95,'acc':90},comp=1,band='fluent',level='exceeds grade-2 standard')}
R={}
with sync_playwright() as p:
    for name,rec in CASES.items():
        b,pg=h.fresh2(p,'Par')
        pg.evaluate("""async ([rec])=>{const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; await db.put('assessments',{id:'a1',profileId:prof.id,ts:Date.now(),letters:1,nonwords:1,words:1,by:'teacher',...rec});}""",[rec])
        pg.reload(); pg.wait_for_selector('.bottom button',timeout=30000); pg.wait_for_timeout(1200)
        pg.evaluate("()=>{window.__shared=[]; navigator.share=async d=>{window.__shared.push(d.text||d.title)}}")
        pg.evaluate("[...document.querySelectorAll('.bottom button')].find(b=>b.textContent.includes('Learn')).click()"); pg.wait_for_timeout(600)
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent.includes('Parent report'))?.click()"); pg.wait_for_timeout(1200)
        R[name]=pg.evaluate("window.__shared")
        if not R[name]: R[name]=pg.inner_text('#app')[-500:] ; R[name+'_toast']=pg.evaluate("document.getElementById('toast')?.textContent")
        R[name+'_err']=pg.errors; b.close()
print(json.dumps(R,ensure_ascii=False,indent=1))
