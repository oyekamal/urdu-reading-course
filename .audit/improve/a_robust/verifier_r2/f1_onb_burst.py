from common import *
import sys, json
TIMES = {'0-0-0': (0, 0, 0), '0-100-200': (0, 100, 200), '0-100-200-300': (0, 100, 200, 300), '0-60-150': (0, 60, 150)}
if len(sys.argv) > 1: TIMES = {k: v for k, v in TIMES.items() if k in sys.argv[1:]}
def onb_i(pg): return pg.evaluate("__dump().then(d=>(d.settings.find(s=>s.key==='onb')||{}).value?.i)")
SEQ = []
def onboard_burst(pg, times, name='Zara'):
    pg.goto(BASE); pg.wait_for_timeout(2200)
    seq = SEQ; seq.clear()
    def s(sel, w=420):
        log = burst_sel(pg, sel, times); pg.wait_for_timeout(w); seq.append((sel, onb_i(pg), pg.inner_text('.ob')[:28].replace('\n',' ') if pg.query_selector('.ob') else pg.inner_text('#app')[:20].replace('\n',' ')))
    s("text=Let's begin", 500)
    s('.ob-sleeper', 2800)
    s('.ob-sw >> nth=0'); s('.ob-cta')
    s(".ob-opt:has-text('My child')", 1600); pg.fill('#ob-name', name); pg.wait_for_timeout(200)
    s('.ob-cta'); s('.ob-opt >> nth=1', 1600)
    s('.ob-opt >> nth=0', 1600); s('.ob-opt >> nth=0', 1600)
    pg.wait_for_timeout(400); click(pg, '.ob-opt >> nth=0'); click(pg, '.ob-opt >> nth=3'); pg.wait_for_timeout(400); s('.ob-cta', 1800); s('.ob-cta', 800)
    s('.ob-opt >> nth=1', 1600); pg.wait_for_timeout(3600)
    s('.ob-cta'); s('.ob-cta')
    for t in ['ب', 'ا', 'ب']:
        click(pg, f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(950)
    s('.ob-cta'); s('text=Join them', 1600); s('.ob-cta')
    s('.ob-word', 1500); s('.ob-cta')
    s(".ob-choices .tile:text-is('بابا')", 1400); s('.ob-cta')
    pg.wait_for_timeout(1000); s('.ob-foot .btn-primary', 900); s('.ob-cta')
    s('.ob-opt >> nth=1', 2200); s('.ob-cta', 2000)
    return seq
with sync_playwright() as p:
    b = p.chromium.launch()
    for nm, tm in TIMES.items():
        ctx, pg = newpage(b)
        try:
            seq = onboard_burst(pg, tm)
            err = None
        except Exception as e:
            err = str(e)[:150]; seq = []
        c, d = counts(pg)
        print(nm, 'profiles', c.get('profiles'), 'attempts', c.get('attempts'), 'screen:', pg.inner_text('#app')[:50].replace('\n', ' | '), 'err', err, 'pageerrs', pg._errs[:2])
        print('   i-seq', [x[1] for x in (seq or SEQ)], flush=True)
        if err: print('   TRACE', [(x[0][:18], x[1], x[2]) for x in SEQ][-6:], flush=True)
        if d.get('profiles'): print('   profile', {k: v for k, v in d['profiles'][0].items() if k in ('name', 'track', 'goal', 'speaks', 'pains', 'minutes', 'days', 'grade')})
        ctx.close()
    b.close()
