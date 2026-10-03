from common import *
with sync_playwright() as p:
    b = p.chromium.launch(); ctx, pg = newpage(b); onboard_child(pg, 'Zed')
    print(pg.inner_text('#app')[:300].replace('\n',' | ')); pg.screenshot(path='/tmp/claude-1000/a_robust/dbg5.png')
