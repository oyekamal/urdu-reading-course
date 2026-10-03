import sys; sys.path.insert(0,'.')
from common import *
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b); quick_profile(pg,'Zara'); nav(pg,'me'); pg.wait_for_timeout(800)
    sel="button:has-text('Export backup')"; xy=xy_of(pg,sel)
    pg.mouse.click(*xy); pg.wait_for_timeout(700); print('single click -> gate sheets', pg.evaluate("document.querySelectorAll('.gate-sheet').length"))
    pg.evaluate("document.querySelector('.gate-cancel').click()"); pg.wait_for_timeout(500)
    for gap in (30,120,250):
        pg.mouse.click(*xy); pg.wait_for_timeout(gap); pg.mouse.click(*xy); pg.wait_for_timeout(700); print('2 taps gap',gap,'-> sheets', pg.evaluate("document.querySelectorAll('.gate-sheet').length"))
        pg.evaluate("document.querySelector('.gate-cancel')?.click()"); pg.wait_for_timeout(500)
