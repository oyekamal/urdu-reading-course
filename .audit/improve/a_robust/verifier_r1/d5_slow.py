from common import *
from d1_helpers import *
with sync_playwright() as p:
    b=p.chromium.launch()
    for gap in [360,450,700]:
        ctx,pg=newpage(b); quick_profile(pg,'Slow')
        click(pg,"button:has-text('Start:')"); pg.wait_for_timeout(900)
        steps=[]
        for i in range(3):
            xy=center(pg,'.lesson .btn-primary'); pg.mouse.click(*xy); pg.wait_for_timeout(gap); steps.append(pg.evaluate("document.querySelector('.progress i')?.style.width"))
        pg.wait_for_timeout(1200)
        print(f'gap={gap}: widths {steps}, celebrate={pg.evaluate("document.querySelectorAll(\".celebrate\").length")}')
        ctx.close()
    b.close()
