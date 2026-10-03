from common import *
import json, tempfile, time
from g1_backup import good, P
d = good(profiles=[P('p1', 'Big')], attempts=[{'id': 'a%d' % i, 'profileId': 'p1', 'ts': 5 + i} for i in range(60000)],
         cards=[{'id': 'p1:c%d' % i, 'profileId': 'p1', 'item': 'ب'} for i in range(20000)], sessions=[{'id': 's%d' % i, 'profileId': 'p1'} for i in range(19000)])
raw = json.dumps(d); print('bytes', len(raw))
f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(raw)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2000)
    t0 = time.time()
    with pg.expect_file_chooser(timeout=6000) as fc:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()")
    fc.value.set_files(f)
    for i in range(40):
        pg.wait_for_timeout(1000)
        t = toast(pg)
        if t and 'Restored' in t: break
    print('restore finished after', round(time.time() - t0, 1), 's toast', toast(pg), '| screen', pg.inner_text('#app')[:40].replace('\n', ' | '), pg._errs[:2])
    time.sleep(3); c, d2 = counts(pg); print({k: v for k, v in c.items() if v})
    b.close()
