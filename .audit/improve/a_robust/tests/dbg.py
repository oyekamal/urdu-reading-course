from common import *
import common
with sync_playwright() as p:
    b = p.chromium.launch(); ctx, pg = newpage(b)
    try: onboard_child(pg, 'Zara')
    except Exception as e: print('ERR', str(e)[:80])
    print(pg.inner_text('#app')[:400]); print(pg._errs, csp(pg))
    pg.screenshot(path='/tmp/claude-1000/a_robust/dbg.png')
