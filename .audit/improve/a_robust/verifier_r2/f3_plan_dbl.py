from common import *
A = {'who': 'child', 'name': 'Zara', 'colour': '#1E9C8F', 'goal': 'family', 'speak': 'fluent', 'reads': 'none', 'pains': ['dots'], 'minutes': 10, 'days': 7, 'firstWord': True}
with sync_playwright() as p:
    b = p.chromium.launch()
    for how in ['dbl', 'cc3', 'cc2']:
        ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
        pg.evaluate("a=>__put('settings',{key:'onb',value:{i:16,a}})", A); pg.goto(BASE); pg.wait_for_timeout(1800)
        if how == 'dbl': pg.dblclick('.ob-cta')
        else: pg.click('.ob-cta', click_count=3 if how == 'cc3' else 2)
        pg.wait_for_timeout(2500); c, d = counts(pg); print(how, 'profiles', c['profiles'], 'attempts', c['attempts'])
        ctx.close()
    b.close()
