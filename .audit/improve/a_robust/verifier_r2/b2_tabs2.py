from common import *
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); quick_profile(pg, 'Zara')
    for k in ['today','review','read','me']:
        for mode in ['dbl','mouse2']:
            pg.evaluate("(k)=>document.querySelector(`.bottom button[data-k='${k}']`).click()", 'review' if k!='review' else 'read'); pg.wait_for_timeout(1500)
            if mode=='dbl':
                pg.dblclick(f".bottom button[data-k='{k}']")
            else:
                pg.click(f".bottom button[data-k='{k}']", click_count=3)
            pg.wait_for_timeout(1800)
            print(k, mode, 'h1s', pg.evaluate("[...document.querySelectorAll('.t-kids h1')].map(h=>h.innerText.trim())"), 'children', pg.evaluate("document.querySelectorAll('.t-kids > *').length"))
    b.close()
