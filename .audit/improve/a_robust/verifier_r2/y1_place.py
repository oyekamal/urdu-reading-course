from common import *
A = {'who': 'me', 'name': 'Ad', 'colour': '#1E9C8F', 'goal': 'family', 'speak': 'fluent', 'reads': 'some', 'pains': ['dots'], 'minutes': 10, 'days': 7, 'firstWord': True}
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
    pg.evaluate("a=>__put('settings',{key:'onb',value:{i:16,a}})", A); pg.goto(BASE); pg.wait_for_timeout(1800)
    pg.evaluate("document.querySelector('.ob-cta').click()"); pg.wait_for_timeout(2500)
    print('screen:', pg.inner_text('#app')[:60].replace('\n', ' | '))
    stages = 0
    for _ in range(80):
        r = pg.evaluate("()=>{const t=[...document.querySelectorAll('.lesson .tile, #app .choices .tile, #app .tile')].find(x=>x.dataset.right); const h=document.querySelector('#app h2')?.innerText||''; return {has:!!t, h}}")
        if not r['has']: break
        h = r['h']; unit = int(''.join(c for c in h if c.isdigit()) or 0)
        if unit >= 3:   # answer wrong at unit 3
            pg.evaluate("()=>{const ts=[...document.querySelectorAll('#app .choices .tile')]; ts.find(x=>!x.dataset.right).click()}"); pg.wait_for_timeout(1500); break
        pg.evaluate("()=>[...document.querySelectorAll('#app .choices .tile')].find(x=>x.dataset.right).click()"); pg.wait_for_timeout(600)
    print('after placement:', pg.inner_text('#app')[:90].replace('\n', ' | '))
    c, d = counts(pg); print('passed units:', [(u, v.get('passed')) for x in d['progress'] for u, v in sorted(x['units'].items())], 'cards', c['cards'], pg._errs)
    b.close()
