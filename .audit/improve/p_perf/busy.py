# python3 busy.py PORT [runs]: main-thread busy % at 6x CPU on Today, no rAF probe loop (it forces frames).
#  from_load = 10 s starting right after the Today screen appears (the harsh reading); awake_idle = 3.5 s after a touch with the wave finished; calm = 5 s of rest
import sys, statistics
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'; RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
def meas(cdp, pg, ms):
    m0 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}; pg.wait_for_timeout(ms)
    m1 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}; w = m1['Timestamp'] - m0['Timestamp']
    return round((m1['TaskDuration'] - m0['TaskDuration']) / w * 100, 1)
R = {'from_load': [], 'awake_idle': [], 'calm': []}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    for _ in range(RUNS):
        ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page(); pg.on('dialog', lambda d: d.accept('5'))
        cdp = ctx.new_cdp_session(pg); cdp.send('Performance.enable')
        quick_profile(pg, BASE)       # last input = the Start click; Today is up ~1.5 s later
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': 6})
        R['from_load'].append(meas(cdp, pg, 10000))
        pg.evaluate("window.dispatchEvent(new Event('pointerdown'))"); pg.wait_for_timeout(2600)   # wave plays out
        R['awake_idle'].append(meas(cdp, pg, 1200))
        pg.wait_for_timeout(5000); R['calm'].append(meas(cdp, pg, 5000)); ctx.close()
    b.close()
for k, v in R.items(): print(f'{k:11}', v, 'median', statistics.median(v))
