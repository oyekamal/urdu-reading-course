import sys, json, collections
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport={'width':412,'height':823}, device_scale_factor=1.75, service_workers='block'); pg = ctx.new_page()
    cdp = ctx.new_cdp_session(pg); cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval', {'interval': 100}); cdp.send('Profiler.start')
    pg.goto(BASE); pg.wait_for_timeout(3500)
    prof = cdp.send('Profiler.stop')['profile']; b.close()
nodes = {n['id']: n for n in prof['nodes']}; dt = prof['timeDeltas']; self_t = collections.Counter()
for sid, d in zip(prof['samples'], dt): self_t[sid] += d
agg = collections.Counter(); tot = 0
for nid, t in self_t.items():
    cf = nodes[nid]['callFrame']; key = (cf['functionName'] or '(anon)', cf['url'].split('/')[-1], cf['lineNumber']); agg[key] += t; tot += t
print('total sampled ms', round(tot/1000))
for k, t in agg.most_common(16): print(f'{t/1000:7.1f} ms  {k}')
