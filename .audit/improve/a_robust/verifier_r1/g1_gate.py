from common import *
from d1_helpers import *
import json
dialogs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b); pg.on('dialog', lambda d: dialogs.append(d.message)); quick_profile(pg,'Gate')
    pid=pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    def snap(): d=pg.evaluate('__dump()'); return {k:len(v) for k,v in d.items() if k not in ('settings',)}, d
    s0,_=snap()
    pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(600)
    for un in [5, 11, 12, 1]:
        pg.evaluate("n=>document.querySelectorAll('.ucard')[n]?.click()", un); pg.wait_for_timeout(1200)
        print(f'unit {un} preview:', pg.inner_text('.preview-note') if pg.query_selector('.preview-note') else 'NO PREVIEW NOTE', '| quiz present:', pg.evaluate("[...document.querySelectorAll('h3')].some(h=>/Check/.test(h.innerText)&&/gate/.test(h.innerText))"))
        # hammer every button/tile in the preview
        pg.evaluate("""()=>{ document.querySelectorAll('#app .tile, #app .keys .tile').forEach(b=>{ try{ b.click() }catch(e){} }); [...document.querySelectorAll('#app button')].filter(b=>/^(Check|Submit|Skip|Next word|Again|Play word)$/.test(b.innerText.trim())).forEach(b=>b.click()) }""")
        pg.wait_for_timeout(800)
        pg.evaluate("()=>{ [...document.querySelectorAll('button')].filter(b=>/Submit|Check$/.test(b.innerText.trim())).forEach(b=>b.click()) }"); pg.wait_for_timeout(800)
        s1,d=snap(); print('   after hammering:', s1, 'progress', [(k,v.get('passed')) for x in d['progress'] for k,v in x['units'].items()], 'errs', pg._errs[-1:])
        nav(pg,'today'); pg.wait_for_timeout(600); pg.evaluate("document.querySelector('.all-units')?.click()"); pg.wait_for_timeout(500)
    print('confirm/alert dialogs seen:', dialogs)
    print('learn tab still says:', end=' '); nav(pg,'today'); print(pg.inner_text('.home-hero h1'), pg.inner_text('.home-hero .muted')[:40])
    b.close()
