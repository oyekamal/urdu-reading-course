from common import *
import json, tempfile
f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(json.dumps({'format': 'urdu-qaida-backup', 'version': 1, 'exportedAt': 'x', 'profiles': [{'id': 'p1', 'name': 'Amal', 'updatedAt': 100}]}))
with sync_playwright() as p:
    b = p.chromium.launch()
    for times in [(0, 0, 0), (0, 100, 200)]:
        ctx, pg = newpage(b); n = []; pg.on('filechooser', lambda fc: (n.append(1), fc.set_files(f)))
        pg.goto(BASE); pg.wait_for_timeout(2000)
        burst_sel(pg, "button:has-text('Restore from a backup')", times); pg.wait_for_timeout(3000)
        c, d = counts(pg); print('welcome restore burst', times, 'choosers', len(n), 'profiles', c['profiles'], 'toast', toast(pg), 'screen', pg.inner_text('#app')[:30].replace('\n', ' | '), pg._errs[:2])
        ctx.close()
    # picker with data (gate): burst -> how many gates / choosers
    for times in [(0, 0, 0), (0, 100, 200)]:
        ctx, pg = newpage(b); n = []; pg.on('filechooser', lambda fc: (n.append(1), fc.set_files(f)))
        pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
        pg.evaluate("async()=>{await __put('profiles',{id:'z1',kind:'learner',name:'Zed',track:'child',grade:1,createdAt:1})}"); pg.reload(); pg.wait_for_timeout(1800)
        print('picker:', pg.inner_text('#app')[:40].replace('\n', ' | '))
        burst_sel(pg, "button:has-text('Restore from a backup')", times); pg.wait_for_timeout(800)
        print(' gates open', pg.evaluate("document.querySelectorAll('.gate-back, .gate-sheet').length"), 'choosers before gate', len(n))
        gate_pass(pg); pg.wait_for_timeout(2500)
        c, d = counts(pg); print(' after gate: choosers', len(n), 'profiles', c['profiles'], 'toast', toast(pg), 'confirm sheet', bool(pg.query_selector('.a11y-sheet')))
        ctx.close()
    b.close()
