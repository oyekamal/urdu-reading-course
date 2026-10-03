import json, math, sys
from lib import *
style=sys.argv[1]; chs=sys.argv[2]; forms=sys.argv[3].split(',')
FORMS=['isolated','initial','medial','final']
def clamp(pt): return (min(357,max(3,pt[0])),min(297,max(3,pt[1])))
def offset(path,d):
    out=[]
    for i,(x,y) in enumerate(path):
        a=path[max(0,i-3)]; b=path[min(len(path)-1,i+3)]; tx,ty=b[0]-a[0],b[1]-a[1]; n=math.hypot(tx,ty) or 1
        out.append(clamp((x-ty/n*d, y+tx/n*d)))
    return out
R=[]
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for ch in chs:
        pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
        for f in forms:
            fi=FORMS.index(f); pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(250)
            g= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
            P=Pad(pg,g,style); sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); body=[clamp(q) for q in thin(walk(sk,P.dot),4)]
            marks=P.comps[1:]
            def go(name,strokes):
                P.clear(); P.refresh()
                for s in strokes: P.drag(s)
                for m in marks: P.tap(clamp(m['c']))
                R.append((ch,f,name,P.verdict()['t']))
            go('center',[body]); go('3passes',[body,offset(body,8),offset(body,-8)])
            go('2passes',[body,offset(body,7)])
            zz=[]; 
            for i,(x,y) in enumerate(body):
                a=body[max(0,i-3)]; c=body[min(len(body)-1,i+3)]; tx,ty=c[0]-a[0],c[1]-a[1]; n=math.hypot(tx,ty) or 1; s=8*math.sin(i*1.2)
                zz.append(clamp((x-ty/n*s,y+tx/n*s)))
            go('zigzag_one_stroke',[thin(zz,2)])
    b.close()
for r in R: print(*r)
