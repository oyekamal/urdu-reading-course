import json, math, sys
from lib import *
style='naskh'
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for ch in 'ڈڑزژذ':
        pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(300)
        P=Pad(pg,ch,style); P.refresh()
        sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); body=thin(cover_strokes(sk,P.dot)[0],4); n=len(body); t=n//3
        for name,strokes in (('natural',[body]),('lift2',[body[:t+1],body[t:2*t+1],body[2*t:]]),('lift1',[body[:n//2],body[n//2+2:]])):
            allst=strokes+[[tuple(c['c'])] for c in P.comps[1:]]
            res=pg.evaluate("""async ([ink,strokes,dot,ch])=>{const D=await import('/src/drills.js'); const ref=new Uint8ClampedArray(360*300*4); for(let i=0;i<ink.length;i++){ if(ink[i]){ref[i*4]=200;ref[i*4+1]=200;ref[i*4+2]=200;ref[i*4+3]=255} }
               return D.judgeTrace({strokes,ref,start:dot,ch,form:'isolated'})}""",[P.ink.flatten().tolist(),[[list(q) for q in s] for s in allst],list(P.dot),ch])
            print(ch,name,res['ok'],res['msg'],res['m'], 'body n',n,'comps',[(c['area'],tuple(int(v) for v in c['c'])) for c in P.comps],'dot',[round(v) for v in P.dot])
    b.close()
