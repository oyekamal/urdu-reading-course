import json, os
from playwright.sync_api import sync_playwright
PORT='5490'; EXE='/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
R={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); pg=b.new_context(viewport={'width':390,'height':800}).new_page(); pg.errors=[]; pg.on('pageerror',lambda e:pg.errors.append(str(e)[:200]))
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2000)
    pg.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=egra-root></div>')"); pg.clock.install()
    def start():
        pg.evaluate("""async () => { window.__res = null; const Cn=await import('/src/content.js'); await Cn.loadContent(); const E = await import('/src/egra.js'); document.getElementById('egra-root').innerHTML=''; E.runEgra(document.getElementById('egra-root'), null, {id:'egra-p', name:'Syn'}, r => { window.__res = r; }); }"""); pg.clock.run_for(400)
    def click(t, ex=False):
        pg.click(f'#egra-root button:has-text("{t}")' if not ex else f'#egra-root button:text-is("{t}")'); pg.clock.run_for(30)
    h2=lambda: pg.inner_text('#egra-root h2')
    rows=lambda: {k.strip(): v.strip() for k, v in (r.split('\t') for r in pg.inner_text('#egra-root table').split('\n') if '\t' in r)}
    def to_passage():
        start(); 
        for _ in range(3): click('Skip')
        assert 'Passage' in h2(), h2()
    # A: time-up, no last word; press Mark twice; then tap word
    to_passage(); pg.clock.run_for(60500)
    st=lambda: pg.evaluate("()=>{const bs=[...document.querySelectorAll('#egra-root .row button')];return bs.map(b=>[b.textContent,b.disabled,b.className])}")
    R['A_after_timeup']=st(); R['A_note']=pg.inner_text('#egra-root p[role=status]')
    click('Mark last word reached'); R['A_after_mark1']=st()
    click('Mark last word reached'); R['A_after_mark2']=st()
    # tap two words wrong then the last word 39
    pg.click('#egra-root .item[data-i="3"]'); pg.click('#egra-root .item[data-i="5"]')
    R['A_wrong_marked']=pg.evaluate("[...document.querySelectorAll('#egra-root .item.wrong')].map(e=>e.dataset.i)")
    # mark mode must still be on? after clicking Mark twice it is on; the next tap sets last word
    pg.click('#egra-root .item[data-i="39"]')
    R['A_after_last']=st(); R['A_note2']=pg.inner_text('#egra-root p[role=status]')
    R['A_words']=pg.evaluate("document.querySelectorAll('#egra-root .item').length")
    click('Score it'); R['A_next']=h2()
    # B: mark pressed before tapping, user taps wrong words BEFORE pressing mark (already did), mark pressed after setting last (re-mark)
    for _ in range(5): click('Correct')
    R['A_rows']=rows()
    click('Save assessment'); pg.clock.run_for(100); R['A_saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,orfDone:window.__res.orfDone,band:window.__res.band,level:window.__res.level,comp:window.__res.comp,compDone:window.__res.compDone}")
    # C: time-up; Read no words
    to_passage(); pg.clock.run_for(60500); click('Read no words'); R['C_next']=h2()
    for _ in range(5): click('Incorrect')
    R['C_rows']=rows(); click('Save assessment'); pg.clock.run_for(100); R['C_saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,orfDone:window.__res.orfDone,band:window.__res.band,level:window.__res.level}")
    # D: passage skipped
    start()
    for _ in range(4): click('Skip')
    for _ in range(5): click('Correct')
    R['D_rows']=rows(); click('Save assessment'); pg.clock.run_for(100); R['D_saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,orfDone:window.__res.orfDone,band:window.__res.band,level:window.__res.level,comp:window.__res.comp,compDone:window.__res.compDone}")
    R['D_groupnote']='immediate small-group' in pg.inner_text('#egra-root') if False else None
    # E: passage skipped and comp skipped
    start()
    for _ in range(5): click('Skip')
    R['E_rows']=rows(); click('Save assessment'); pg.clock.run_for(100); R['E_saved']=pg.evaluate("window.__res&&{band:window.__res.band,level:window.__res.level,compDone:window.__res.compDone,orfDone:window.__res.orfDone}")
    # F: Child finished < 15s ignored; at 20s no last word -> ask -> read to end; fast read cap
    to_passage(); pg.clock.run_for(3000); click('Child finished'); R['F_early_note']=pg.inner_text('#egra-root p[role=status]'); R['F_still_passage']='Passage' in h2()
    pg.clock.run_for(17000); click('Child finished'); R['F_ask_visible']=pg.is_visible('#egra-root button:has-text("Read to the end")')
    click('Read to the end'); R['F_next']=h2()
    for _ in range(5): click('Correct')
    R['F_rows']=rows(); click('Save assessment'); pg.clock.run_for(100); R['F_saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,band:window.__res.band,level:window.__res.level}")
    # G: stopped early path: after 20s, Child finished -> Stopped early -> tap word 10 -> finish
    to_passage(); pg.clock.run_for(20000); click('Child finished'); click('Stopped early'); R['G_note']=pg.inner_text('#egra-root p[role=status]')
    pg.click('#egra-root .item[data-i="9"]'); click('Child finished'); R['G_next']=h2()
    for _ in range(5): click('Correct')
    click('Save assessment'); pg.clock.run_for(100); R['G_saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,band:window.__res.band}")
    # H: cwpm cap: finish at 15s with whole passage: words*60/15 
    to_passage(); pg.clock.run_for(15500); click('Child finished'); click('Read to the end'); 
    for _ in range(5): click('Correct')
    click('Save assessment'); pg.clock.run_for(100); R['H_saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,band:window.__res.band,level:window.__res.level}")
    # I: comprehension 3/5 with fast reader -> level
    to_passage(); pg.clock.run_for(60500); click('Mark last word reached'); pg.click('#egra-root .item[data-i="'+str(R['A_words']-1)+'"]'); click('Score it')
    for i in range(5): click('Correct' if i<3 else 'Incorrect')
    R['I_rows']=rows(); click('Save assessment'); pg.clock.run_for(100); R['I_saved']=pg.evaluate("window.__res&&{orf:window.__res.orf,band:window.__res.band,level:window.__res.level}")
    # J: flash subtask nothing tapped
    start(); pg.clock.run_for(60500)
    R['J_asked']=pg.is_visible('#egra-root input[type=number]')
    pg.fill('#egra-root input[type=number]',''); pg.click('#egra-root button:has-text("Score it")'); R['J_empty_stays']=pg.is_visible('#egra-root input[type=number]')
    pg.fill('#egra-root input[type=number]','7'); click('Score it'); R['J_next']=h2()
    # K: flash: nothing tapped but pressed Next page -> counted pages
    start(); click('Next ›'); pg.clock.run_for(60500); R['K_asked']=pg.is_visible('#egra-root input[type=number]'); R['K_h2']=h2()
    # L: huge number clamp
    start(); pg.clock.run_for(60500); pg.fill('#egra-root input[type=number]','9999'); click('Score it'); 
    pg.evaluate("1"); 
    for _ in range(4): click('Skip')
    R['L_rows']=rows()
    R['errors']=pg.errors; b.close()
print(json.dumps(R,ensure_ascii=False,indent=1)); json.dump(R,open('t2_egra.json','w'),ensure_ascii=False,indent=1)
