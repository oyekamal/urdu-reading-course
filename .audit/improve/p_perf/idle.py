# Idle Today profile: python3 idle.py PORT  -> main-thread busy % at 6x CPU over 10s + frame stats
import sys, statistics, json
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept('5'))
    cdp = ctx.new_cdp_session(pg); cdp.send('Performance.enable')
    quick_profile(pg, BASE); pg.wait_for_timeout(3000)
    print('markos', pg.evaluate("document.querySelectorAll('.marko').length"), 'screen', pg.evaluate("(document.querySelector('#app')||{}).className"))
    pg.screenshot(path=OUT+'/idle_today_'+sys.argv[1]+'.png')
    AW = len(sys.argv) > 2 and sys.argv[2] == 'awake'
    if AW: pg.evaluate("document.dispatchEvent(new Event('pointerdown'))"); pg.mouse.move(5,5); pg.evaluate("window.dispatchEvent(new Event('keydown'))")
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 6})
    m0 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}
    DUR = 4000 if AW else 10000
    res = pg.evaluate("""()=>new Promise(res=>{const ts=[];let last=performance.now(),t0=last;function f(t){ts.push(t-last);last=t;if(t-t0<DUR)requestAnimationFrame(f);else res(ts)}requestAnimationFrame(f)})""".replace("DUR", str(DUR)))
    m1 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}
    wall = (m1['Timestamp'] - m0['Timestamp'])
    busy = {k: round((m1[k]-m0[k]) / wall * 100, 1) for k in ['TaskDuration','ScriptDuration','LayoutDuration','RecalcStyleDuration']}
    ts = res[1:]; n = len(ts); ss = sorted(ts)
    print('busy pct 6x wall', round(wall,1), busy)
    print('frames', n, 'fps', round(n/(DUR/1000),1), 'median', round(statistics.median(ts),1), 'p95', round(ss[int(n*.95)],1), 'over33 %', round(100*sum(1 for x in ts if x>33.4)/n,1))
    print('errors', errs[:5]); b.close()
