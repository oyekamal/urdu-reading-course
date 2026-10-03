import json, re
from playwright.sync_api import sync_playwright
PORT='5530'; EXE='/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
URL=f'http://localhost:{PORT}/?skiponb'
# name -> record fields (None => unassessed)
CASES=[
 ('c01_old_65_comp1',   dict(orf={'cwpm':65,'acc':90}, comp=1)),
 ('c02_old_65_nocomp',  dict(orf={'cwpm':65,'acc':90})),
 ('c03_old_95_comp5',   dict(orf={'cwpm':95,'acc':95}, comp=5)),
 ('c04_old_65_comp4',   dict(orf={'cwpm':65,'acc':95}, comp=4)),
 ('c05_new_notested',   dict(orf={'cwpm':0,'acc':0,'seconds':0,'errors':0}, orfDone=False, comp=5, compDone=True, band='not tested', level='passage not tested: no standard result')),
 ('c06_new_compskip70', dict(orf={'cwpm':70,'acc':90}, orfDone=True, comp=0, compDone=False, band='sentences', level='fluent, comprehension not tested: not yet a standard result')),
 ('c07_oldband_fluent_comp1', dict(orf={'cwpm':65,'acc':90}, comp=1, band='fluent')),
 ('c08_empty_band_65_c2',dict(orf={'cwpm':65,'acc':90}, comp=2, band='')),
 ('c09_old_30_compFalse', dict(orf={'cwpm':30,'acc':90}, comp=0, compDone=False)),
 ('c10_orfDoneFalse_noband', dict(orf={'cwpm':0,'acc':0}, orfDone=False, comp=3, compDone=True)),
 ('c11_new_0_orfdone',  dict(orf={'cwpm':0,'acc':0,'seconds':60}, orfDone=True, comp=0, compDone=True, band='pre-reader', level='nonreader')),
 ('c12_noorf_nocomp',   dict()),
 ('c13_new_fluent_ok',  dict(orf={'cwpm':100,'acc':98}, orfDone=True, comp=5, compDone=True, band='fluent', level='exceeds grade-2 standard')),
 ('c14_new_95_comp3',   dict(orf={'cwpm':95,'acc':98}, orfDone=True, comp=3, compDone=True, band='sentences', level='below standard: reads fast, understands too little')),
 ('c15_old_60_comp5',   dict(orf={'cwpm':60,'acc':98}, comp=5)),
 ('c16_old_cwpm_missing', dict(orf={'acc':90}, comp=5)),
 ('c17_old_90_comp4',   dict(orf={'cwpm':90,'acc':98}, comp=4)),
 ('c18_old_91_comp4',   dict(orf={'cwpm':91,'acc':98}, comp=4)),
 ('c19_nothing_assessed', None),
 ('x01_legacy_fluent_band_comp1_nocompDone', dict(orf={'cwpm':80,'acc':95}, comp=1, band='fluent', level='exceeds grade-2 standard')),
 ('x02_orf_null', dict(orf=None, comp=3)),
 ('x03_orfDoneFalse_cwpm70', dict(orf={'cwpm':70,'acc':90}, orfDone=False, comp=5, compDone=True, band='fluent', level='exceeds grade-2 standard')),
 ('x04_cwpm_string', dict(orf={'cwpm':'70','acc':90}, comp=5)),
 ('x05_comp_null', dict(orf={'cwpm':70,'acc':90}, comp=None)),
 ('x06_orfDoneTrue_noorf', dict(orfDone=True, comp=5, compDone=True)),
 ('x07_legacy_exceeds_nocomp', dict(orf={'cwpm':99,'acc':98}, band='fluent', level='exceeds grade-2 standard')),
 ('x08_cwpm_null', dict(orf={'cwpm':None,'acc':90}, comp=5, band='fluent')),
 ('x09_new_complete_75_c4', dict(orf={'cwpm':75,'acc':95}, orfDone=True, comp=4, compDone=True, band='fluent', level='meets standard')),
 ('x10_legacy_orfDoneFalse_noflags_cwpm0', dict(orf={'cwpm':0}, comp=0)),

 ('c21_legacy_exceeds_comp1', dict(orf={'cwpm':95,'acc':98}, comp=1, band='fluent', level='exceeds grade-2 standard')),
 ('c22_legacy_meets_comp2', dict(orf={'cwpm':65,'acc':98}, comp=2, band='fluent', level='meets standard')),
 ('c20_old_levelmeets_comp2', dict(orf={'cwpm':80,'acc':98}, comp=2, level='meets standard')),
]
SEED='''async (cases) => { const {db}=await import('/src/db.js'); await db.setting('mode','school'); await db.setting('teacherPin','1234'); await db.setting('teacherName','T');
 let i=0; const t=Date.now();
 for (const [name,rec] of cases) { i++; const id='p'+i; await db.put('profiles',{id,kind:'learner',name,track:'child',grade:'2',createdAt:1});
   if (rec) await db.put('assessments',{id:'a'+i,profileId:id,ts:t-1000*i,letters:30,nonwords:20,words:25,by:'teacher',...rec}); }
}'''
EN={w:i for i,w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split())}
TENS={'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90}
def parse(s):
    n=0
    for w in s.split('-'):
        n+=EN.get(w,0) or TENS.get(w,0)
    return n
R={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE,args=[]); ctx=b.new_context(viewport={'width':390,'height':900},accept_downloads=True); pg=ctx.new_page(); pg.errors=[]; pg.on('pageerror',lambda e:pg.errors.append(str(e)[:200])); pg.on('dialog',lambda d:d.accept())
    pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate(SEED,[[n,r] for n,r in CASES]); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{window.__shared=[]; navigator.share=async d=>{ if(d.text===undefined) throw new Error('nofile'); window.__shared.push(d.text)}; Object.defineProperty(navigator,'canShare',{value:undefined})}")
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent.includes('Teacher')).click()"); pg.wait_for_timeout(500)
    pg.fill('input[type=password]','1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Unlock').click()"); pg.wait_for_timeout(1500)
    def tab(n): pg.evaluate("n=>[...document.querySelectorAll('.tabs .tab')].find(t=>t.textContent===n).click()", n); pg.wait_for_timeout(700)
    tab('Class'); R['class']=pg.evaluate("[...document.querySelectorAll('#app table tr')].map(r=>[...r.children].slice(0,3).map(c=>c.textContent).join(' | '))")
    tab('Groups'); R['groups']=pg.evaluate("[...document.querySelectorAll('#app .card')].map(c=>c.innerText.replace(/\\n+/g,' / '))")
    tab('Reports'); R['reports']=pg.evaluate("[...document.querySelectorAll('#app table tr')].map(r=>[...r.children].map(c=>c.textContent).join(' | '))")
    R['hist']=pg.evaluate("[...document.querySelectorAll('#app .card')].find(c=>c.innerText.includes('Band histogram')).innerText.replace(/\\n+/g,' / ')")
    # CSV
    pg.evaluate("[...document.querySelectorAll('#app button')].find(b=>b.textContent.trim()==='Export CSV').click()"); pg.wait_for_timeout(500)
    en=pg.inner_text('.gate-en'); n=parse(en); pg.fill('#gate-input',str(n))
    with pg.expect_download(timeout=8000) as dl:
        pg.click('.gate-ok')
    path=dl.value.path(); R['csv']=open(path,encoding='utf8').read().split('\n')
    # slips
    pg.evaluate("window.__shared=[]")
    names=pg.evaluate("[...document.querySelectorAll('#app .card')].find(c=>c.innerText.includes('Parent slip')).querySelectorAll('.row').length")
    pg.evaluate("[...document.querySelectorAll('#app button')].filter(b=>b.textContent.trim()==='Share slip').forEach(b=>b.click())"); pg.wait_for_timeout(1000)
    R['slips']=pg.evaluate("window.__shared")
    # dashboard rows
    tab('Class'); R['dash']={}
    for name,_ in CASES:
        tab('Class')
        ok=pg.evaluate("n=>{const r=[...document.querySelectorAll('#app tr')].find(r=>r.children[0]&&r.children[0].textContent===n); if(!r) return false; [...r.querySelectorAll('button')].find(b=>b.textContent.trim()==='Detail').click(); return true}", name); pg.wait_for_timeout(700)
        R['dash'][name]=pg.evaluate("[...document.querySelectorAll('#child-detail table tr')].map(r=>[...r.children].map(c=>c.textContent).join(' | ')).slice(-1)[0]||null") if ok else 'noRow'
    R['errors']=pg.errors; b.close()
json.dump(R,open('r4_teacher.json','w'),ensure_ascii=False,indent=1)
print('done',len(R['slips']), R['errors'])
