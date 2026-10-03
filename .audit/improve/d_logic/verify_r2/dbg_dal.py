import json, math, sys
from lib import *
style='nastaliq'
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for ch in 'ڈڑدر':
        pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
        P=Pad(pg,ch,style); P.refresh()
        sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); body=thin(walk(sk,P.dot),4)
        print(ch,'dot',P.dot,'body start',body[0],'end',body[-1],'comps',[(c['area'],tuple(int(v) for v in c['c'])) for c in P.comps],'bbox',np.nonzero(P.ink)[1].min(),np.nonzero(P.ink)[1].max(),np.nonzero(P.ink)[0].min(),np.nonzero(P.ink)[0].max())
        res=pg.evaluate("""async ([ink,body,marks,dot,ch])=>{const D=await import('/src/drills.js'); const ref=new Uint8ClampedArray(360*300*4); for(let i=0;i<ink.length;i++){ if(ink[i]){ref[i*4]=200;ref[i*4+1]=200;ref[i*4+2]=200;ref[i*4+3]=255} }
           const strokes=[body, ...marks.map(c=>[c])]; return D.judgeTrace({strokes,ref,start:dot,ch,form:'isolated'})}""",[P.ink.flatten().tolist(),[list(q) for q in body],[list(c['c']) for c in P.comps[1:]],list(P.dot),ch])
        print('  judge',res)
    b.close()
