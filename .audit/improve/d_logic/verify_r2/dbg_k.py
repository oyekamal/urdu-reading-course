import json
from lib import *
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for style,ch,fi in (('nastaliq','ک',1),('naskh','ک',1),('nastaliq','ب',1)):
        pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(400)
        pg.click(f'.pchip:nth-child({fi+1})'); pg.wait_for_timeout(400)
        g=ch+'ـ'
        P=Pad(pg,g,style)
        app=pg.evaluate("()=>{const cv=document.querySelector('canvas.trace'); const d=cv.getContext('2d').getImageData(0,0,360,300).data; const a=[]; for(let i=0;i<360*300;i++) a.push(d[i*4+3]>12?1:0); return a}")
        A=np.array(app,dtype=np.uint8).reshape(300,360)
        def bb(m): ys,xs=np.nonzero(m); return (xs.min(),xs.max(),ys.min(),ys.max(),int(m.sum())) if len(xs) else None
        print(style,ch,'mine',bb(P.ink),'app(visible)',bb(A), 'dot',P.dot)
    b.close()
