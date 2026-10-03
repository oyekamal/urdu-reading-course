from common import *
from h1_flows import mk
def dup_report(pg):
    return pg.evaluate("""()=>({h1:[...document.querySelectorAll('#app h1')].map(h=>h.innerText.trim()), lessonBoxes:document.querySelectorAll('.lesson .t-kids').length, cont:document.querySelectorAll('.lesson .btn-primary').length, progressBars:document.querySelectorAll('.lesson .progress').length, lessons:document.querySelectorAll('.lesson').length})""")
with sync_playwright() as p:
    b = p.chromium.launch()
    for times in [(0,), (0, 0, 0), (0, 100, 200), (0, 250), (0, 400)]:
        ctx, pg = newpage(b); quick_profile(pg, 'S'); mk(pg, [])
        burst_sel(pg, '.tc-go', times); pg.wait_for_timeout(1500)
        print('Today Start', times, dup_report(pg), flush=True)
        # then advance by one Continue: does one tap on the visible Continue advance exactly one screen even if duplicated?
        ctx.close()
    b.close()
