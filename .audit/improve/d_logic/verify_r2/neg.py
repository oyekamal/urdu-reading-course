import json, math, random
from lib import *
R={}
def mount(pg,ch,style='naskh'):
    pg.evaluate(MOUNT,[[ch,'ب' if ch!='ب' else 'ا'],style]); pg.wait_for_timeout(300)
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for ch in 'ابدرڈژپ':
        mount(pg,ch); P=Pad(pg,ch,'naskh'); P.refresh()
        sk=zs(P.comps[0]['mask']); body=thin(walk(sk,P.dot),2); marks=P.comps[1:]
        n=len(body); out={}
        def run(name,fn):
            P.clear(); P.refresh(); fn(); out[name]=P.verdict()['t']
        def taps_along(k):
            idx=[int(i*(n-1)/(k-1)) for i in range(k)]
            for i in idx: P.tap(body[i])
            for m in marks: P.tap(m['c'])
        for k in (3,4,5,6,8): run(f'{k}_taps_along_body',lambda k=k: taps_along(k))
        def dashes(k,gap):
            L=n//k
            for i in range(k):
                seg=body[i*L:max(i*L+2,(i+1)*L-gap)]; 
                if len(seg)>1: P.drag(seg)
            for m in marks: P.tap(m['c'])
        for k in (3,4,6): run(f'{k}_dashes_gapped',lambda k=k: dashes(k,3))
        run('reversed_body',lambda:( P.drag(body[::-1]), [P.tap(m['c']) for m in marks]))
        run('only_dots',lambda: [P.tap(m['c']) for m in marks] if marks else P.tap(P.dot))
        run('scribble_zigzag',lambda: P.drag([(P.dot[0]-60+ (i%2)*120, P.dot[1]+i*6) for i in range(40)]))
        run('start_far_left',lambda: P.drag(body[::-1] if False else [(40,250)]+body))
        run('body_start_100px_off',lambda: (P.drag([(P.dot[0]-100,P.dot[1])]+body), [P.tap(m['c']) for m in marks]))
        R[ch]=out
    b.close()
for ch,o in R.items():
    print(ch)
    for k,v in o.items(): print('  ',k,'->',v)
json.dump(R,open('neg.json','w'),ensure_ascii=False,indent=1)
