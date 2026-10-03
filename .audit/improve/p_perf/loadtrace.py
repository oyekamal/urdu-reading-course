import sys, json, collections
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport={'width':412,'height':823}, device_scale_factor=1.75, service_workers='block'); pg = ctx.new_page()
    cdp = ctx.new_cdp_session(pg); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    b.start_tracing(page=pg, path='/tmp/claude-1000/p_perf/out/load.json', categories=['devtools.timeline', 'v8.execute', 'blink.user_timing', 'loading', 'disabled-by-default-devtools.timeline'])
    pg.goto(BASE); pg.wait_for_timeout(4000); b.stop_tracing(); b.close()
ev = json.load(open('/tmp/claude-1000/p_perf/out/load.json'))['traceEvents']
agg = collections.defaultdict(collections.Counter)
for e in ev:
    if e.get('ph') == 'X' and 'dur' in e: agg[(e['pid'], e['tid'])][e['name']] += e['dur']
key = max(agg, key=lambda k: agg[k].get('RunTask', 0)); t0 = min(e['ts'] for e in ev if e.get('name') in ('navigationStart', 'RunTask') and (e['pid'], e['tid']) == key)
marks = {e['name']: round((e['ts'] - t0) / 1000) for e in ev if e.get('name') in ('firstPaint', 'firstContentfulPaint', 'largestContentfulPaint::Candidate', 'domContentLoadedEventEnd', 'loadEventEnd') and e.get('pid') == key[0]}
print('marks', marks)
tasks = sorted([e for e in ev if e.get('ph') == 'X' and (e['pid'], e['tid']) == key and e['name'] == 'RunTask' and e['dur'] > 25000], key=lambda e: e['ts'])
for t in tasks:
    inner = collections.Counter()
    for e in ev:
        if e.get('ph') == 'X' and (e['pid'], e['tid']) == key and e['ts'] >= t['ts'] and e['ts'] + e['dur'] <= t['ts'] + t['dur'] and e['name'] not in ('RunTask',):
            inner[e['name']] += e['dur']
    print(f"t={round((t['ts']-t0)/1000):5} dur={round(t['dur']/1000):4} ms", [(n, round(d / 1000)) for n, d in inner.most_common(5)])
