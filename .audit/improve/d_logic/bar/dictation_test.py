import json,re
from playwright.sync_api import sync_playwright
ROOT='/home/oye/Documents/free_work/urdu-reading-course'; U=json.load(open(ROOT+'/data/units.json',encoding='utf8'))['units']
EXE='/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
M=re.compile('[ً-ْٰـ]'); res=[]
js=lambda pg,h: pg.evaluate('e=>e.click()',h)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); pg=b.new_context(viewport={'width':390,'height':800}).new_page(); pg.on('dialog',lambda d:d.accept())
    pg.add_init_script("const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__last=this.src.split('/audio/')[1];return _p.call(this)}")
    pg.goto('http://localhost:5188/?skiponb'); pg.wait_for_timeout(2200); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.fill('input[placeholder=Name]','T'); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2500)
    js(pg,pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(800)
    for n in (1,5,10):
        js(pg,pg.query_selector_all('.ucard')[n]); pg.wait_for_timeout(1500)
        h=[x for x in pg.query_selector_all('#app h2') if x.inner_text()=='Dictation'][0]; card=h.evaluate_handle('e=>e.closest(".card")').as_element(); card.scroll_into_view_if_needed()
        def typed(s):
            for ch in s:
                for k in card.query_selector_all('.keys .tile'):
                    if k.inner_text().strip()==ch: js(pg,k); break
        for trial in range(5):
            key=pg.evaluate('window.__last'); un,_,wi=key.replace('.mp3','').split('/')[-1].partition('_'); w=U[int(un[1:])]['words'][int(wi)]; bare=M.sub('',w[0])
            row={'unit':n,'word':w[0],'bare':bare}
            # near miss: swap first two letters if different else drop last
            nm=(bare[1]+bare[0]+bare[2:]) if len(bare)>1 and bare[0]!=bare[1] else bare[:-1]
            typed(nm); js(pg,card.query_selector('button:has-text("Check")')); pg.wait_for_timeout(300); row['near_miss']=nm; row['near_miss_result']=pg.evaluate("document.getElementById('toast')?.textContent"); 
            for _ in range(len(nm)): js(pg,card.query_selector('button[aria-label=Erase]'))
            typed(bare); js(pg,card.query_selector('button:has-text("Check")')); pg.wait_for_timeout(300); row['correct_result']=pg.evaluate("document.getElementById('toast')?.textContent"); res.append(row); pg.wait_for_timeout(1100)
        pg.evaluate('history.back()') if False else None
        js(pg,pg.query_selector(".bottom button[data-k=units], .bottom button[data-k=today]")); pg.wait_for_timeout(800)
        if not pg.query_selector_all('.ucard'): js(pg,pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(800)
    b.close()
json.dump(res,open('dictation_test.json','w'),ensure_ascii=False,indent=1)
for r in res: print(r)
