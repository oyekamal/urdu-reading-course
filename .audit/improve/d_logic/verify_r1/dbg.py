import h, t1_real as T
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b, pg = h.fresh2(p, 'D1')
    h.tamper(pg, 2, {})
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1200)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/^(Start|Continue):/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(900)
    for i in range(8):
        print(i, pg.inner_text('h1')[:30], '|', pg.evaluate("[...document.querySelectorAll('.lesson button')].map(b=>b.className.split(' ').slice(0,3).join('.')+':'+b.textContent.trim().slice(0,12)+(b.offsetParent?'':'(hid)'))"))
        prim = pg.evaluate_handle("[...document.querySelectorAll('.lesson button.btn-primary')].filter(b=>b.offsetParent&&!b.disabled).slice(-1)[0]||null").as_element()
        print(' prim', bool(prim), 'tiles', len(pg.query_selector_all('.lesson .choices .tile')), pg.evaluate("document.querySelector('.lesson')?.className"))
        if prim: prim.click()
        pg.wait_for_timeout(700)
        tl=pg.query_selector_all('.lesson .choices .tile')
        if tl: print('tiles', [t.inner_text() for t in tl], [t.get_attribute('data-right') for t in tl]); break
    b.close()
