import sys, json, math
from lib import *
style=sys.argv[1]; ch=sys.argv[2]; f=sys.argv[3]
FORMS=['isolated','initial','medial','final']
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
    pg.click(f'.pchip:nth-child({FORMS.index(f)+1})'); pg.wait_for_timeout(250)
    glyph= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
    P=Pad(pg,glyph,style); print('dot',P.dot, 'comps',[(c['area'],[round(v) for v in c['c']]) for c in P.comps])
    mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); sk=zs(mask)
    cs=cover_strokes(sk,P.dot); print([ (len(c),c[0],c[-1]) for c in cs])
    ys,xs=np.nonzero(mask); print('bbox',xs.min(),xs.max(),ys.min(),ys.max())
    cv2.imwrite(f'dbg_{ch}_{f}_{style}.png',P.ink*255)
    b.close()
