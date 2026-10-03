import json
R=json.load(open('t1_blobs.json'))
by={(r['ch'],r['form']):r for r in R}
ref=sorted(b['n'] for b in by[('ب','isolated')]['naskh'])[0]; print('ref dot area',ref)
def classify(bl):
    bl=sorted(bl,key=lambda b:-b['n']); body=bl[0]; marks=bl[1:]
    dots=[];other=[]
    for m in marks:
        w=m['x1']-m['x0']+1; hh=m['y1']-m['y0']+1; asp=max(w,hh)/max(1,min(w,hh)); fill=m['n']/(w*hh)
        isdot = 0.5*ref<=m['n']<=2.2*ref and asp<2.0 and fill>0.5
        (dots if isdot else other).append(m)
    return body,dots,other
truth={}
for (ch,form),r in by.items():
    body,dots,other=classify(r['naskh'])
    pos=''
    if dots:
        ab=sum(1 for d in dots if d['cy']<body['cy']); pos='above' if ab>len(dots)/2 else 'below'
    truth[f'{ch}|{form}']={'n':len(dots),'pos':pos,'other':len(other),'blobs':[b['n'] for b in r['naskh']]}
json.dump(truth,open('t1_truth.json','w'),ensure_ascii=False,indent=1)
for k,v in truth.items(): print(k,v)
