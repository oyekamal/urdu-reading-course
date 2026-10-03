import json, math, sys
from lib import *
style='naskh'
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    ch='ڈ'
    pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(400)
    pg.evaluate("""()=>{window.__S=[]; const cv=document.querySelector('canvas.trace'); const pos=e=>{const r=cv.getBoundingClientRect(); return [(e.clientX-r.left)*cv.width/r.width,(e.clientY-r.top)*cv.height/r.height]};
      cv.addEventListener('pointerdown',e=>{window.__S.push([pos(e)])},true); cv.addEventListener('pointermove',e=>{ if(e.buttons&&window.__S.length){ for(const ev of (e.getCoalescedEvents?.()||[e])) window.__S[window.__S.length-1].push(pos(ev)) } },true)}""")
    P=Pad(pg,ch,style); P.refresh()
    sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); cs=cover_strokes(sk,P.dot); body=thin(max(cs,key=len),4); n=len(body)
    print('cs strokes',len(cs),[len(c) for c in cs])
    P.clear(); P.refresh()
    for s in ([body[:n//2], body[n//2+2:]]+[thin(c,4) for c in cs if c is not max(cs,key=len)]): P.drag(s)
    for m in P.comps[1:]: P.tap(m['c'])
    v=P.verdict(); print('UI',v)
    S=pg.evaluate("window.__S"); print('captured strokes',[len(s) for s in S])
    res=pg.evaluate("""async ([ink,strokes,dot,ch])=>{const D=await import('/src/drills.js'); const ref=new Uint8ClampedArray(360*300*4); for(let i=0;i<ink.length;i++){ if(ink[i]){ref[i*4]=200;ref[i*4+1]=200;ref[i*4+2]=200;ref[i*4+3]=255} }
         return D.judgeTrace({strokes,ref,start:dot,ch,form:'isolated'})}""",[P.ink.flatten().tolist(),S,list(P.dot),ch])
    print('judge on captured',res)
    print('mine strokes',[ (len(s)) for s in ([body[:n//2], body[n//2+2:]]+[thin(c,4) for c in cs if c is not max(cs,key=len)])])
    b.close()
