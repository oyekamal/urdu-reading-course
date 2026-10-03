import json,glob,sys,collections
style=sys.argv[1]; d='.' if len(sys.argv)<3 else sys.argv[2]
R=[]
for f in glob.glob(f'{d}/t1_{style}_*.json'): R+=json.load(open(f))
pos=[r for r in R if r.get('kind')=='pos']; neg=[r for r in R if r.get('kind')=='neg']
fr=[r for r in pos if not r['ok']]; fa=[r for r in neg if r['ok']]
print(style,'POS',len(pos),'falseRej',len(fr),'NEG',len(neg),'falseAcc',len(fa))
c=collections.Counter(r['var'] for r in fr); print('rej by var',dict(c))
c=collections.Counter(r['t'].split('—')[-1].strip()[:50] for r in fr); print('rej msgs',dict(c))
c=collections.Counter((r['ch'],r['form']) for r in fr); print('rej by letter/form',dict(c))
c=collections.Counter(r['var'] for r in fa); print('acc by var',dict(c))
print([ (r['ch'],r['form'],r['var']) for r in fa])
