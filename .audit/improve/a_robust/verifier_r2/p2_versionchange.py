from common import *
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); quick_profile(pg, 'Vc')
    pg2 = ctx.new_page(); pg2.goto(BASE + 'robots.txt'); pg2.wait_for_timeout(300)
    r = pg2.evaluate("""()=>new Promise(res=>{ const t=setTimeout(()=>res('B BLOCKED >3s'),3000); const q=indexedDB.open('urdu-reader',2); q.onupgradeneeded=()=>{q.result.createObjectStore('extra',{keyPath:'id'})}; q.onsuccess=()=>{clearTimeout(t); q.result.close(); res('B upgraded ok')}; q.onerror=()=>res('B error '+q.error); q.onblocked=()=>{} })""")
    print(r); pg2.close()
    # A keeps working? navigate tabs (reads) and write (grade nothing) -> tab changes
    for k in ['review', 'read', 'me', 'today']:
        nav(pg, k)
    print('A after version bump:', pg.inner_text('#app')[:50].replace('\n', ' | '), 'errs', pg._errs[:2], 'rec', bool(pg.query_selector('.recovery')))
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
    for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
    pg.wait_for_selector('.celebrate', timeout=8000)
    c, d = counts(pg); print('A wrote lesson after bump: lessons', [list(v.get('lessons', {})) for x in d['progress'] for v in x['units'].values()], 'errs', pg._errs[:2])
    b.close()
