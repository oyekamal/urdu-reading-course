import sys, json, math
from lib import *
FORMS=['isolated','initial','medial','final']
def cl(q): return (min(357,max(3,q[0])),min(297,max(3,q[1])))
CASES=[('naskh','ڈ','isolated'),('naskh','ڑ','isolated'),('naskh','ژ','isolated'),('naskh','ز','isolated'),('naskh','ا','final'),('naskh','ا','isolated'),('naskh','ر','isolated'),('naskh','د','isolated'),
       ('nastaliq','ک','isolated'),('nastaliq','ے','isolated'),('nastaliq','س','isolated'),('nastaliq','ا','final'),('nastaliq','ا','isolated'),('nastaliq','ڈ','isolated')]
out=[]
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for style,ch,f in CASES:
        pg.evaluate(MOUNT,[[ch,'ب' if ch=='ا' else 'ا'],style]); pg.wait_for_timeout(300)
        fi=FORMS.index(f); pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(250)
        glyph = ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
        P=Pad(pg,glyph,style)
        mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); sk=zs(mask); cs=cover_strokes(sk,P.dot)
        body=max(cs,key=len); bt=thin(body,4); extra=[thin(c,4) for c in cs if c is not body]
        marks=[('tap',cl(m['c'])) for m in P.comps[1:]]
        ys,xs=np.nonzero(P.ink)
        for name,(dx,dy) in {'L100':(-100,0),'L120':(-120,0),'L80':(-80,0),'D100':(0,100),'UL90':(-64,-64),'R60':(60,0)}.items():
            st=cl((P.dot[0]+dx,P.dot[1]+dy)); dink=float(np.hypot(xs-st[0],ys-st[1]).min())
            P.clear(); P.refresh()
            # bridge from the start point straight to the first body point (a child sliding in), then the body
            P.drag([st]+[cl(q) for q in bt]); [P.drag(e) for e in extra]; [P.tap(m[1]) for m in marks]
            v=P.verdict(); out.append((style,ch,f,name,round(dink),v['ok'],v['t']))
    b.close()
for o in out: print(o)
json.dump(out,open('o_t10.json','w'),ensure_ascii=False)
