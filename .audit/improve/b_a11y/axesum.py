import json,collections,sys
for t in sys.argv[1:]:
    d=json.load(open(f'runs/{t}/results.json')); print('##',t,d['notes'])
    c=collections.defaultdict(list)
    for r in d['results']:
        for v in r.get('axe',{}).get('v',[]):
            c[(v['id'],v['impact'])].append((r['screen'],v['n'],v['nodes'][0]['t'][:50],v['nodes'][0]['s'][:100] if v['id']=='color-contrast' else ''))
    for k,v in c.items():
        if k[0] in ('landmark-one-main','region','heading-order','page-has-heading-one','empty-table-header') : print(' (best-practice)',k,len(v)); continue
        print(k,len(v),v[:6])
