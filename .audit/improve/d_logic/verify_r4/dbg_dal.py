import sys, json
from lib import *
style=sys.argv[1]; ch=sys.argv[2]; f=sys.argv[3]
FORMS=['isolated','initial','medial','final']
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
    pg.click(f'.pchip:nth-child({FORMS.index(f)+1})'); pg.wait_for_timeout(300)
    glyph= ch if f=='isolated' else ch+'ـ' if f=='initial' else 'ـ'+ch+'ـ' if f=='medial' else 'ـ'+ch
    P=Pad(pg,glyph,style); print('dot',P.dot,'comps',[(c['area'],[round(v) for v in c['c']]) for c in P.comps])
    mask=cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); ys,xs=np.nonzero(mask); print('body bbox',xs.min(),xs.max(),ys.min(),ys.max())
    sk=zs(mask); cs=cover_strokes(sk,P.dot); b0=thin(max(cs,key=len),4); print('first pt',b0[0],'last',b0[-1],'n',len(b0))
    # judge directly
    ink=P.m['ink']
    for name,st in (('body',[b0]),):
        r=pg.evaluate("""async ([ink,strokes,start,ch,form])=>{const D=await import('/src/drills.js'); const ref=new Uint8ClampedArray(360*300*4); for(let i=0;i<ink.length;i++){ref[i*4+3]=ink[i]?255:0; ref[i*4]=255;} return D.judgeTrace({strokes,ref,start,ch,form});}""",[ink,[ [list(q) for q in s] for s in st],list(P.dot),ch,f])
        print(name,r)
    b.close()
