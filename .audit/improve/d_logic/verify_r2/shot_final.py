from lib import *
import math
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    for style in ('naskh','nastaliq'):
        pg.evaluate(MOUNT,[['ڈ','ا'],style]); pg.wait_for_timeout(400)
        pg.click('.pchip:nth-child(4)'); pg.wait_for_timeout(400)
        P=Pad(pg,'ـڈ',style); P.refresh()
        sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); cs=cover_strokes(sk,P.dot); body=max(cs,key=len)
        print(style,'dot',[round(v) for v in P.dot],'body start',body[0],'dist',round(math.hypot(body[0][0]-P.dot[0],body[0][1]-P.dot[1])),'comps',[(c['area'],[round(v) for v in c['c']]) for c in P.comps])
        pg.locator('.trace-wrap').screenshot(path=f'dfinal_{style}.png')
    b.close()
