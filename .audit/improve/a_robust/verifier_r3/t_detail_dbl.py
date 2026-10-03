import sys; sys.path.insert(0,'.')
from common import *
from t_teacher_add import teacher
BASE='http://localhost:5371/'
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b); teacher(pg)
    pg.fill('input[placeholder=Name]','Amna'); click(pg,"button:has-text('Add child')"); pg.wait_for_timeout(1000)
    pg.dblclick("button:has-text('Detail')"); pg.wait_for_timeout(2000)
    print('detail panels after dblclick:', pg.evaluate("document.querySelectorAll('#child-detail').length"), 'h2 detail', pg.evaluate("[...document.querySelectorAll('h2')].filter(h=>/detail/.test(h.innerText)).length"))
    ctx.close()
    ctx,pg=newpage(b); teacher(pg)
    pg.fill('input[placeholder=Name]','Amna'); click(pg,"button:has-text('Add child')"); pg.wait_for_timeout(1000)
    pg.click("button:has-text('Detail')",click_count=3); pg.wait_for_timeout(2000)
    print('detail panels after triple:', pg.evaluate("document.querySelectorAll('#child-detail').length"))
