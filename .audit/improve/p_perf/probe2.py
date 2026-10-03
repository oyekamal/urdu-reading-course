import sys, json
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
EXPS = {
 'baseline': '',
 'contain strict-ish': "document.head.insertAdjacentHTML('beforeend','<style>.marko{contain:layout style paint}</style>')",
 'content: layout style paint + will-change': "document.head.insertAdjacentHTML('beforeend','<style>.marko{contain:layout style paint;will-change:transform}</style>')",
 'shape-rendering speed': "document.head.insertAdjacentHTML('beforeend','<style>.marko svg{shape-rendering:optimizeSpeed;text-rendering:optimizeSpeed}</style>')",
 'pm off + contain': "document.head.insertAdjacentHTML('beforeend','<style>.marko{contain:layout style paint}.pm *{animation:none!important}</style>')",
}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    for lab, js in EXPS.items():
        ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page(); pg.on('dialog', lambda d: d.accept('5'))
        cdp = ctx.new_cdp_session(pg); cdp.send('Performance.enable'); quick_profile(pg, BASE); pg.wait_for_timeout(1500)
        pg.evaluate("window.dispatchEvent(new Event('pointerdown'))")
        if js: pg.evaluate(js)
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': 6}); pg.wait_for_timeout(500)
        m0 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}; pg.wait_for_timeout(4000)
        m1 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}; w = m1['Timestamp']-m0['Timestamp']
        print(f'{lab:26} task%', round((m1['TaskDuration']-m0['TaskDuration'])/w*100,1)); ctx.close()
    b.close()
