import json,re
from playwright.sync_api import sync_playwright
EXE='/home/oye/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
js=lambda pg,h: pg.evaluate('e=>e.click()',h)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); pg=b.new_context(viewport={'width':390,'height':800}).new_page(); pg.on('dialog',lambda d:d.accept())
    pg.add_init_script("const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){(window.__plays=window.__plays||[]).push(this.src.split('/audio/')[1]);return _p.call(this)}")
    pg.goto('http://localhost:5188/?skiponb'); pg.wait_for_timeout(2200); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.fill('input[placeholder=Name]','T'); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2500)
    js(pg,pg.query_selector("button:has-text('All units')")); pg.wait_for_timeout(900); js(pg,pg.query_selector_all('.ucard')[1]); pg.wait_for_timeout(1500)
    h=[x for x in pg.query_selector_all('#app h2') if 'Tap what you hear' in x.inner_text()][0]; card=h.evaluate_handle('e=>e.closest(".card")').as_element()
    before={'status':card.query_selector('.score').inner_text(),'tiles':len(card.query_selector_all('.choices .tile')),'plays_so_far':pg.evaluate('window.__plays||[]')[-3:]}
    pg.evaluate('window.__plays=[]'); js(pg,card.query_selector('.choices .tile')); pg.wait_for_timeout(500)
    att=pg.evaluate("async()=>{const {db}=await import('/src/db.js');return (await db.all('attempts')).length}")
    after={'status':card.query_selector('.score').inner_text(),'attempts_recorded':att,'plays':pg.evaluate('window.__plays')}
    print(json.dumps({'before_first_tap':before,'after_first_tap':after},ensure_ascii=False)); json.dump({'before':before,'after':after},open('tell_first_tap.json','w'),ensure_ascii=False); b.close()
