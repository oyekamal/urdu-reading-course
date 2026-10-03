# python3 trace.py PORT [mode]  -> aggregates main-thread time by event name over 4s at 6x CPU
import sys, json, collections
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'; mode = sys.argv[2] if len(sys.argv) > 2 else 'all'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page()
    pg.on('dialog', lambda d: d.accept('5'))
    cdp = ctx.new_cdp_session(pg)
    quick_profile(pg, BASE); pg.wait_for_timeout(6000 if mode=='calm' else 3000)
    if mode == 'nolottie': pg.evaluate("document.querySelectorAll('.marko').forEach(m=>m._marko.anim&&m._marko.anim.pause())")
    if mode == 'nocss': pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
    if mode == 'none':
        pg.evaluate("document.querySelectorAll('.marko').forEach(m=>m._marko.anim&&m._marko.anim.pause());document.getAnimations().forEach(a=>a.pause())")
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 6})
    b.start_tracing(page=pg, path='/tmp/claude-1000/p_perf/out/trace.json', categories=['devtools.timeline','disabled-by-default-devtools.timeline'])
    pg.wait_for_timeout(8000 if mode=='calm' else 4000); b.stop_tracing(); b.close()
ev = json.load(open('/tmp/claude-1000/p_perf/out/trace.json'))['traceEvents']
# find renderer main thread: thread with most 'RunTask'
agg = collections.defaultdict(lambda: collections.Counter()); 
for e in ev:
    if e.get('ph') == 'X' and 'dur' in e: agg[(e['pid'], e['tid'])][e['name']] += e['dur']
key = max(agg, key=lambda k: agg[k].get('RunTask', 0)); c = agg[key]
print('mode', mode, 'RunTask ms', round(c['RunTask']/1000), 'of window')
for n, d in c.most_common(14): print(f'{n:35} {d/1000:8.0f} ms')
tasks=sorted([e for e in ev if e.get('ph')=='X' and (e['pid'],e['tid'])==key and e['name']=='RunTask'],key=lambda e:-e['dur'])[:6]
print('longest tasks ms', [round(t['dur']/1000) for t in tasks])
fc=collections.Counter()
for e in ev:
    if e.get('ph')=='X' and (e['pid'],e['tid'])==key and e['name'] in('FunctionCall','EvaluateScript','TimerFire','FireAnimationFrame'):
        a=e.get('args',{}).get('data',{}); fc[(e['name'],a.get('functionName') or a.get('url','')[-30:])]+=e['dur']
print([ (k,round(v/1000)) for k,v in fc.most_common(8)])
