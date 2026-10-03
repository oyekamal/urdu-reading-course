import sys
from lib import *
style=sys.argv[1]; ch=sys.argv[2]; f=sys.argv[3]
FORMS=['isolated','initial','medial','final']
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
    pg.click(f'.pchip:nth-child({FORMS.index(f)+1})'); pg.wait_for_timeout(300)
    glyph= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
    P=Pad(pg,glyph,style)
    mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); sk=zs(mask)
    pts=[(int(x),int(y)) for y,x in zip(*np.nonzero(sk))]; S=set(pts)
    nb=lambda u:[(u[0]+dx,u[1]+dy) for dx in(-1,0,1) for dy in(-1,0,1) if (dx or dy) and (u[0]+dx,u[1]+dy) in S]
    ends=[q for q in pts if len(nb(q))==1]; tip=max(ends,key=lambda q:q[0]); print('dot',P.dot,'tip',tip,'dist',math.hypot(tip[0]-P.dot[0],tip[1]-P.dot[1]))
    cs=cover_strokes(sk,tip); body=thin(max(cs,key=len),4)
    P.clear(); P.refresh(); P.drag(body)
    for m in P.comps[1:]: P.tap(m['c'])
    print(P.verdict())
    b.close()
