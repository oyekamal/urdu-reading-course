from common import *
A = {'who': 'child', 'name': 'Zara', 'colour': '#1E9C8F', 'goal': 'family', 'speak': 'fluent', 'reads': 'none', 'pains': ['dots'], 'minutes': 10, 'days': 7, 'firstWord': True}
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
    reqs = []; pg.on('request', lambda r: reqs.append(r.url))
    for i in (13, 14):
        pg.evaluate("([i,a])=>__put('settings',{key:'onb',value:{i,a}})", [i, A]); pg.goto(BASE); pg.wait_for_timeout(1800)
        if pg.query_selector("button:has-text('first word')"): break
    print('share button present:', bool(pg.query_selector("button:has-text('first word')")), pg.inner_text('.ob')[:50].replace('\n', ' | '))
    try:
        with pg.expect_download(timeout=8000) as dl: pg.evaluate("[...document.querySelectorAll('button')].find(b=>/first word/.test(b.innerText)).click()")
        print('share card download:', dl.value.suggested_filename, len(open(dl.value.path(), 'rb').read()), 'bytes')
    except Exception as e: print('share FAIL', str(e)[:80])
    print('csp', csp(pg), 'errs', pg._errs, 'off-origin', [u for u in reqs if not u.startswith(BASE) and not u.startswith('blob:') and not u.startswith('data:')])
    b.close()
