import h, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b, pg = h.fresh2(p, 'Asp2')
    h.tamper(pg, 5, {})
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1000)
    print(pg.evaluate("[...document.querySelectorAll('button,a')].map(b=>b.textContent.trim().slice(0,30))")[:30])
    pg.evaluate("[...document.querySelectorAll('button,a')].find(b=>/All units/i.test(b.textContent))?.click()"); pg.wait_for_timeout(1000)
    print(pg.inner_text('#app')[:300]); print(h.real_errors(pg))
    pg.evaluate("[...document.querySelectorAll('#app button')].find(b=>/^Unit 6/.test(b.textContent.trim())).click()"); pg.wait_for_timeout(1500)
    print(pg.inner_text('#app')[:300]); print(pg.evaluate("document.querySelectorAll('td[id^=asp-]').length"), h.real_errors(pg))
    b.close()
