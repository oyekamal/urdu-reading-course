# Accelerated simulated-use soak. python3 soak2.py PORT MINUTES [snap_every_min]
# cycle: 4 tab navigations (review/read/me/today) + open the current lesson, advance two screens, leave it (confirm), back on Today. ~ every 6 s.
# metrics each interval (after 3x GC): JS heap used, Blink DOM nodes, JS listeners, DETACHED nodes in a heap snapshot (the real leak signal), live markos.
import sys, json, time, collections
from h import *
PORT = sys.argv[1]; MIN = float(sys.argv[2]); EVERY = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
BASE = f'http://localhost:{PORT}/'
def detached(cdp):
    chunks = []; cdp.on('HeapProfiler.addHeapSnapshotChunk', lambda e: chunks.append(e['chunk']))
    cdp.send('HeapProfiler.takeHeapSnapshot', {'reportProgress': False}); snap = json.loads(''.join(chunks)); cdp.remove_listener('HeapProfiler.addHeapSnapshotChunk', None) if False else None
    m = snap['snapshot']['meta']; nf = m['node_fields']; N = len(nf); nodes = snap['nodes']; strs = snap['strings']; ni = nf.index('name'); di = nf.index('detachedness'); se = nf.index('self_size')
    n = 0; names = collections.Counter(); size = 0
    for k in range(0, len(nodes), N):
        if nodes[k + di] == 2: n += 1; names[strs[nodes[k + ni]][:30]] += 1
        size += nodes[k + se]
    return n, names.most_common(4), round(size / 1e6, 2)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox', '--js-flags=--expose-gc'])
    ctx = b.new_context(viewport=VP, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept('5'))
    quick_profile(pg, BASE, 'Amal'); pg.wait_for_timeout(2000); cdp = ctx.new_cdp_session(pg)
    def nav(k): pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`)?.click()", k); pg.wait_for_timeout(120)
    def cycle():
        for k in ('review', 'read', 'me', 'today'): nav(k)
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Start:|Continue:/.test(b.textContent))?.click()"); pg.wait_for_timeout(500)
        for _ in range(2): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(250)
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Leave lesson')?.click()"); pg.wait_for_timeout(250); pg.evaluate("()=>document.querySelector('.a11y-leave')?.click()"); pg.wait_for_timeout(250)
        nav('today'); pg.wait_for_timeout(200)
    def snap(tag):
        for _ in range(3): cdp.send('HeapProfiler.collectGarbage'); pg.wait_for_timeout(150)
        h = cdp.send('Runtime.getHeapUsage'); c = cdp.send('Memory.getDOMCounters'); d, top, tot = detached(cdp)
        r = {'tag': tag, 'heapMB': round(h['usedSize'] / 1e6, 2), 'domNodes': c['nodes'], 'listeners': c['jsEventListeners'], 'detached': d, 'snapMB': tot, 'top': top,
             'markos': pg.evaluate("document.querySelectorAll('.marko').length"), 'screen': pg.evaluate("document.querySelector('#app')?.firstElementChild?.className||''")[:30]}
        print(r, flush=True); return r
    rows = [snap('start')]; t0 = time.time(); nxt = EVERY * 60; cycles = 0
    while time.time() - t0 < MIN * 60:
        cycle(); cycles += 1
        if time.time() - t0 >= nxt: rows.append(snap(f'{round((time.time()-t0)/60,1)}min c{cycles}')); nxt += EVERY * 60
    rows.append(snap('end c%d' % cycles))
    json.dump({'rows': rows, 'errs': errs, 'cycles': cycles}, open(f'/tmp/claude-1000/p_perf/out/soak2_{PORT}_{int(MIN)}.json', 'w'), indent=1)
    xs = [(i, r['heapMB']) for i, r in enumerate(rows) if i >= 2]
    if len(xs) > 2:
        n = len(xs); mx = sum(i for i, _ in xs) / n; my = sum(y for _, y in xs) / n
        sl = sum((i - mx) * (y - my) for i, y in xs) / sum((i - mx) ** 2 for i, _ in xs); print('heap slope MB per snapshot interval (excl first two):', round(sl, 4), '= KB/min', round(sl * 1000 / EVERY, 1))
    print('errors', errs[:5]); b.close()
