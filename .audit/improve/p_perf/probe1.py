import sys, json
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page()
    pg.on('dialog', lambda d: d.accept('5'))
    cdp = ctx.new_cdp_session(pg); cdp.send('Performance.enable')
    quick_profile(pg, BASE); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{const o={};document.getAnimations().forEach(a=>{const e=a.effect;const kf=e.getKeyframes?e.getKeyframes():[];const props=[...new Set(kf.flatMap(k=>Object.keys(k)).filter(k=>!['offset','easing','composite','computedOffset'].includes(k)))];const t=e.target;const key=(a.animationName||'?')+' ['+props.join(',')+'] on '+(t&&t.className&&t.className.baseVal===undefined?t.className:(t&&t.tagName));o[key]=(o[key]||0)+1});return o}"""))
    print('markos', pg.evaluate("[...document.querySelectorAll('.marko')].map(m=>[m.getBoundingClientRect().width,m.getBoundingClientRect().top|0,m._marko.state])"))
    def busy(lab, ms=5000):
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': 6})
        m0 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}; pg.wait_for_timeout(ms)
        m1 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}
        w = m1['Timestamp']-m0['Timestamp']
        print(f'{lab:30}', {k: round((m1[k]-m0[k])/w*100,1) for k in ['TaskDuration','ScriptDuration','LayoutDuration','RecalcStyleDuration']})
    busy('all')
    pg.evaluate("document.querySelectorAll('.marko').forEach(m=>m._marko.anim&&m._marko.anim.pause())"); busy('lottie paused')
    pg.evaluate("document.getAnimations().forEach(a=>a.pause())"); busy('lottie+css paused')
    b.close()
