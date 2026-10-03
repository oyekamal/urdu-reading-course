import sys
from lib import *
style=sys.argv[1]; ch=sys.argv[2]; f=sys.argv[3]
FORMS=['isolated','initial','medial','final']
with sync_playwright() as p:
    b,pg=browser(p); pg.goto(URL); pg.wait_for_timeout(1500)
    pg.evaluate(MOUNT,[[ch,'ا'],style]); pg.wait_for_timeout(500)
    pg.click(f'.pchip:nth-child({FORMS.index(f)+1})'); pg.wait_for_timeout(500)
    pg.query_selector('.trace-wrap').screenshot(path=f'q3_{ch}_{f}_{style}.png')
    print(pg.evaluate("()=>{const d=document.querySelector('.trace-start'); const r=d.getBoundingClientRect(), c=document.querySelector('canvas.trace').getBoundingClientRect(); return [(r.left+r.width/2-c.left)*360/c.width,(r.top+r.height/2-c.top)*300/c.height, c.width,c.height]}"))
    b.close()
