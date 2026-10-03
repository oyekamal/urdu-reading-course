import json
from lib import *
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate(MOUNT,[['ک','ا'],'nastaliq']); pg.wait_for_timeout(400)
    pg.click('.pchip:nth-child(2)'); pg.wait_for_timeout(400)
    P=Pad(pg,'ک'+'ـ','nastaliq'); P.refresh()
    print('comps',[c['area'] for c in P.comps])
    sk=zs(cv2.morphologyEx(P.comps[0]['mask'],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))); body=thin(walk(sk,P.dot),4); print(len(body),body[:3],body[-3:])
    P.drag(body); print(P.verdict())
    pg.locator('canvas.trace').screenshot(path='k_nast.png')
    pg.locator('.trace-wrap').screenshot(path='k_nast_wrap.png')
    b.close()
