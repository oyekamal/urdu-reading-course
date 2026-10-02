import json, collections
from h import *
from s6_data import newpage, nav
BASE='http://localhost:5301/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE,args=['--no-sandbox']); ctx,pg=newpage(b); quick_profile(pg,BASE,'Amal'); pg.wait_for_timeout(1500)
    cdp=ctx.new_cdp_session(pg)
    for i in range(60): nav(pg,['review','read','me','today'][i%4])
    chunks=[]; cdp.on('HeapProfiler.addHeapSnapshotChunk',lambda e:chunks.append(e['chunk']))
    cdp.send('HeapProfiler.collectGarbage'); cdp.send('HeapProfiler.takeHeapSnapshot',{'reportProgress':False})
    snap=json.loads(''.join(chunks)); m=snap['snapshot']['meta']; nf=m['node_fields']; N=len(nf); nodes=snap['nodes']; strs=snap['strings']
    ti=nf.index('type'); ni=nf.index('name'); di=nf.index('detachedness') if 'detachedness' in nf else None
    ef=m['edge_fields']; E=len(ef); edges=snap['edges']; ec=nf.index('edge_count'); nt=m['node_types'][0]
    cnt=collections.Counter(); det=[]
    for k in range(0,len(nodes),N):
        if di is not None and nodes[k+di]==2: cnt[strs[nodes[k+ni]]]+=1; det.append(k)
    print('detached nodes by name:',cnt.most_common(12), 'total',len(det))
    # retainers: build reverse edges for detached nodes only
    detset=set(det); ret=collections.defaultdict(list); pos=0
    ei_type=ef.index('type'); ei_name=ef.index('name_or_index'); ei_to=ef.index('to_node'); et=m['edge_types'][0]
    for k in range(0,len(nodes),N):
        c=nodes[k+ec]
        for j in range(c):
            e=pos+j*E; to=edges[e+ei_to]
            if to in detset: ret[to].append((k,et[edges[e+ei_type]],edges[e+ei_name]))
        pos+=c*E
    rc=collections.Counter()
    for t in det:
        for (k,ty,nm) in ret[t]:
            if ty in ('element','hidden','internal','weak','shortcut'): continue
            nn=strs[nodes[k+ni]] if True else ''; rc[(nn[:50],strs[nm] if ty in('property','context') else ty)]+=1
    print('top retainers of detached nodes:',rc.most_common(15))
    b.close()
