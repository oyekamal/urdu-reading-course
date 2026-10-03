import json,glob,collections,sys
runs={}
for f in sorted(glob.glob('runs/*/results.json')):
    d=json.load(open(f)); runs[d['tag']]=d
IGN={'tap44-47','edge-lr','gap<6'}
print('HARNESS FAILS / NOTES')
for t,d in runs.items():
    hf=[r['screen'] for r in d['results'] if r['screen'].startswith('HARNESS')]+[r['screen'] for r in d['results'] if 'error' in r and not r['screen'].startswith('HARNESS')]
    n=len(d['results']); print(t,n,hf,d['errors'][:1])
print()
rule=sys.argv[1:] 
for t,d in runs.items():
    c=collections.Counter(); ex={}
    for r in d['results']:
        for v in r.get('layout',[]):
            c[v[0]]+=1; ex.setdefault(v[0],[]).append((r['screen'],v[1][:30],v[2][:50]))
    print('##',t,dict(c))
