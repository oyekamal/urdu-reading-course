import json
from playwright.sync_api import sync_playwright
PORT='5490'; EXE='/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
R={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); pg=b.new_context(viewport={'width':390,'height':800}).new_page(); pg.errors=[]; pg.on('pageerror',lambda e:pg.errors.append(str(e)[:200]))
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2500)
    pg.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=egra-root></div>')"); pg.clock.install()
    pg.evaluate("""async () => { window.__res=null; const Cn=await import('/src/content.js'); await Cn.loadContent(); const E=await import('/src/egra.js'); E.runEgra(document.getElementById('egra-root'), null, {id:'x', name:'S'}, r=>{window.__res=r}); }"""); pg.clock.run_for(400)
    c=lambda t:(pg.click(f'#egra-root button:has-text("{t}")'),pg.clock.run_for(5))
    for _ in range(3): c('Skip')
    pg.clock.run_for(15001); c('Child finished'); 
    R['ask']=pg.is_visible('#egra-root button:has-text("Read to the end")'); c('Read to the end')
    for _ in range(5): c('Correct')
    R['rows']=pg.inner_text('#egra-root table'); c('Save assessment'); pg.clock.run_for(100)
    R['saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,band:window.__res.band,level:window.__res.level}")
    R['errors']=pg.errors; b.close()
print(json.dumps(R,ensure_ascii=False,indent=1))
