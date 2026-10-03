import h, json
from t6_trace import *
with sync_playwright() as p:
    b, pg = h.bare(p, 420, 900); pg.evaluate(MOUNT.replace("['ا','ب']", "['پ','ا']")); pg.wait_for_timeout(300)
    select(pg,'پ','isolated'); pg.evaluate("document.querySelector('.trace-clear').click()"); pg.wait_for_timeout(200)
    pad=Pad(pg); sol=solve(pad); print(sol['all'], len(sol['dots']), sol['dots'])
    cv2.imwrite('pe_mask.png', pad.ink*255)
    b.close()
