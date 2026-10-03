# Which Urdu-text elements ignore --ur-scale? Compares computed font-size at scale 1 vs 1.5 on key screens.
import sys; sys.argv=['x','5199']
exec(open('kb_checks.py').read().split('def run():')[0])
JS="""()=>[...document.querySelectorAll('[lang=ur]')].filter(e=>e.getClientRects().length).map(e=>[e.tagName+'.'+(e.className||'').toString().split(' ').slice(0,2).join('.'),(e.textContent||'').trim().slice(0,6),parseFloat(getComputedStyle(e).fontSize)])"""
def sc(pg,v): pg.evaluate("v=>document.documentElement.style.setProperty('--ur-scale',v)",v); pg.wait_for_timeout(150)
bad={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE)
    for track in ['child','adult']:
        pg=new_ctx(b); pid=make_learner(pg,track)
        def snap(name):
            sc(pg,'1'); a=pg.evaluate(JS); sc(pg,'1.5'); c=pg.evaluate(JS); sc(pg,'1')
            n=min(len(a),len(c)); nb=[(a[i][0],a[i][1],a[i][2],c[i][2]) for i in range(n) if a[i][0]==c[i][0] and abs(c[i][2]-a[i][2])<0.5]
            bad[f'{track}:{name}']=(len(a),nb[:12]); print(track,name,len(a),'unscaled',len(nb),nb[:6])
        snap('today')
        click(pg,"button:has-text('Start:')"); pg.wait_for_timeout(600); primary(pg);primary(pg);primary(pg); pg.wait_for_selector('.celebrate'); snap('celebrate'); click(pg,'.cel-go'); pg.wait_for_timeout(600); primary(pg); pg.wait_for_selector('.celebrate'); pg.evaluate("(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(800)
        for lid in ['Lbe','W1']:
            open_lesson(pg,pid,lid); pg.wait_for_timeout(500); snap('lesson_'+lid)
            if lid=='Lbe':
                primary(pg); pg.wait_for_timeout(700); snap('tellapart')
        nav(pg,'read'); snap('read'); nav(pg,'review'); snap('review')
        nav(pg,'me' if track=='child' else 'progress'); snap('me')
        pg.evaluate("window.__stickers.openBook()"); pg.wait_for_timeout(900); snap('stickers')
    b.close()
json.dump(bad,open('probes/urscale.json','w'),ensure_ascii=False,indent=1)
