import json, math, sys
from lib import *
style=sys.argv[1]; chs=sys.argv[2]; forms=sys.argv[3].split(',')
FORMS=['isolated','initial','medial','final']
cl=lambda q:(min(357,max(3,q[0])),min(297,max(3,q[1])))
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for ch in chs:
        pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
        for f in forms:
            fi=FORMS.index(f); pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(250)
            g= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
            P=Pad(pg,g,style); sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); cs=cover_strokes(sk,P.dot); body=[cl(q) for q in thin(max(cs,key=len),4)]; extra=[[cl(q) for q in thin(c,4)] for c in cs if c is not max(cs,key=len)]
            marks=P.comps[1:]
            def mk(mode):
                out=[]
                for m in marks:
                    if mode=='tap': out.append(('tap',cl(m['c'])))
                    elif mode=='walk':
                        k=zs(m['mask']); w=walk(k,(m['c'][0]+40,m['c'][1])); out.append(thin(w,4) if len(w)>1 else ('tap',cl(m['c'])))
                    elif mode=='tap_bbox_ends':
                        ys,xs=np.nonzero(m['mask']); out.append(('tap',cl((xs.min()+8,ys.mean()))));out.append(('tap',cl((xs.max()-8,ys.mean()))))
                return out
            for mode in ('tap','walk','tap_bbox_ends'):
                P.clear(); P.refresh()
                P.drag(body)
                for e in extra: P.drag(e)
                for m in mk(mode):
                    if isinstance(m,tuple): P.tap(m[1])
                    else: P.drag(m)
                print(style,ch,f,mode,'marks',[c['area'] for c in marks],P.verdict()['t'],flush=True)
    b.close()
