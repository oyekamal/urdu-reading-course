# python3 leak.py PORT [navs]: heap snapshot after N tab navigations: detached nodes by name + who retains them (non-DOM retainers)
import sys, json, collections
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'; NAVS = int(sys.argv[2]) if len(sys.argv) > 2 else 60
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport=VP, service_workers='block'); pg = ctx.new_page(); pg.on('dialog', lambda d: d.accept('5'))
    quick_profile(pg, BASE, 'Amal'); pg.wait_for_timeout(1500); cdp = ctx.new_cdp_session(pg)
    def nav(k): pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`).click()", k); pg.wait_for_timeout(350)
    def cyc():
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Start:|Continue:/.test(b.textContent))?.click()"); pg.wait_for_timeout(500)
        for _ in range(2): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(250)
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Leave lesson')?.click()"); pg.wait_for_timeout(250); pg.evaluate("()=>document.querySelector('.a11y-leave')?.click()"); pg.wait_for_timeout(250); nav('today')
    for i in range(NAVS): cyc()
    chunks = []; cdp.on('HeapProfiler.addHeapSnapshotChunk', lambda e: chunks.append(e['chunk']))
    cdp.send('HeapProfiler.collectGarbage'); cdp.send('HeapProfiler.takeHeapSnapshot', {'reportProgress': False})
    snap = json.loads(''.join(chunks)); m = snap['snapshot']['meta']; nf = m['node_fields']; N = len(nf); nodes = snap['nodes']; strs = snap['strings']
    ti = nf.index('type'); ni = nf.index('name'); di = nf.index('detachedness'); ec = nf.index('edge_count'); ef = m['edge_fields']; E = len(ef); edges = snap['edges']
    cnt = collections.Counter(); det = []
    for k in range(0, len(nodes), N):
        if nodes[k + di] == 2: cnt[strs[nodes[k + ni]]] += 1; det.append(k)
    print('detached total', len(det), cnt.most_common(10))
    detset = set(det); ret = collections.defaultdict(list); pos = 0
    ei_type = ef.index('type'); ei_name = ef.index('name_or_index'); ei_to = ef.index('to_node'); et = m['edge_types'][0]; nt = m['node_types'][0]
    for k in range(0, len(nodes), N):
        c = nodes[k + ec]
        for j in range(c):
            e = pos + j * E; to = edges[e + ei_to]
            if to in detset: ret[to].append((k, et[edges[e + ei_type]], edges[e + ei_name]))
        pos += c * E
    rc = collections.Counter()
    for t in det:
        for (k, ty, nm) in ret[t]:
            if ty in ('element', 'hidden', 'weak', 'shortcut'): continue
            if nodes[k + di] == 2: continue  # retained by another detached node: look for the non-detached holder
            rc[(nt[nodes[k + ti]], strs[nodes[k + ni]][:60], strs[nm] if ty in ('property', 'context') else ty)] += 1
    print('holders (not themselves detached):', rc.most_common(14))
    # shortest retaining paths (BFS from the root over all edges except weak) to a few detached home-hero divs
    nodes_n = len(nodes) // N; first = [0] * (nodes_n + 1); pos = 0
    adj = [None] * nodes_n
    for idx in range(nodes_n):
        k = idx * N; c = nodes[k + ec]; lst = []
        for j in range(c):
            e = pos + j * E; ty = et[edges[e + ei_type]]
            if ty != 'weak': lst.append((edges[e + ei_to] // N, ty, edges[e + ei_name]))
        adj[idx] = lst; pos += c * E
    import collections as C
    par = {0: None}; dq = C.deque([0])
    while dq:
        u = dq.popleft()
        for v, ty, nm in adj[u]:
            if v not in par: par[v] = (u, ty, nm); dq.append(v)
    targets = [k // N for k in det if strs[nodes[k + ni]].startswith('<div class="progress live"')][:2]
    for t in targets:
        chain = []; cur = t
        while par.get(cur):
            u, ty, nm = par[cur]; chain.append(f"{nt[nodes[u*N+ti]]}:{strs[nodes[u*N+ni]][:40]} -[{ty}:{strs[nm] if ty in ('property','context') else nm}]->"); cur = u
        print('PATH to detached hero:'); [print('   ', c) for c in reversed(chain[:18])]
    b.close()
