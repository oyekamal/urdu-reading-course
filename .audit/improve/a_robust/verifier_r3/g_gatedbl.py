import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
with sync_playwright() as p:
    b=p.chromium.launch()
    for how in ['dbl','click3']:
        ctx,pg=newpage(b); quick_profile(pg,'Zara'); nav(pg,'me'); pg.wait_for_timeout(800)
        sel="button:has-text('Export backup')"
        n=0
        try:
            with pg.expect_download(timeout=7000) as dl:
                (pg.dblclick(sel) if how=='dbl' else pg.click(sel,click_count=3)); pg.wait_for_timeout(600)
                print(how,'gate sheets open:',pg.evaluate("document.querySelectorAll('.gate-sheet').length"), 'overlays', pg.evaluate("document.querySelectorAll('.gate-back, .sheet-back, [role=dialog]').length"))
                gate_pass(pg)
            print(how,'download ok'); 
        except Exception as e: print(how,'EXC',str(e)[:150])
        pg.wait_for_timeout(1500); print(how,'after: gates',pg.evaluate("document.querySelectorAll('.gate-sheet').length"),'downloads/toast',toast(pg)); ctx.close()
