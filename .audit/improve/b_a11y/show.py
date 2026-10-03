import json,sys
for t in sys.argv[1:]:
    d=json.load(open(f'runs/{t}/results.json')); print('##',t,[n[:80] for n in d['notes']],d['errors'][:2])
    for r in d['results']:
        for v in r.get('layout',[]):
            if v[0] in ('tap44-47','edge-lr') : continue
            print(' ',r['screen'],v[0],v[1][:38],'|',v[2][:60])
