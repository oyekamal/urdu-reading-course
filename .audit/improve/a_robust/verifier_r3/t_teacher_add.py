import sys; sys.path.insert(0,'.')
from common import *
BASE='http://localhost:5371/'
def teacher(pg):
    pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500)
    pg.evaluate("__put('settings',{key:'mode',value:'school'}); __put('settings',{key:'teacherPin',value:'1234'}); __put('settings',{key:'activeProfile',value:null})"); pg.wait_for_timeout(300); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText)).click()"); pg.wait_for_timeout(500)
    pg.fill('input[type=password]','1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1500)
if __name__=="__main__":
    with sync_playwright() as p:
        b=p.chromium.launch()
        for how in ['js3','dblclick','click3','mouse']:
            ctx,pg=newpage(b); teacher(pg)
            pg.fill('input[placeholder=Name]','Amna'); sel="button:has-text('Add child')"
            if how=='js3': print(bursts(pg, xy_of(pg, sel), (0,100,200)))
            elif how=='dblclick': pg.dblclick(sel)
            elif how=='click3': pg.click(sel, click_count=3)
            else:
                xy=xy_of(pg,sel)
                for _ in range(3): pg.mouse.click(xy[0],xy[1]); pg.wait_for_timeout(80)
            pg.wait_for_timeout(1500)
            print(how,'profiles',[ (x['name'],x['kind']) for x in pg.evaluate('__dump()')['profiles']])
            ctx.close()
