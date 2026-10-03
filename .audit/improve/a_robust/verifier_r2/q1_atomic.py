from common import *
import json, tempfile
from g1_backup import good, P
FAULT = "window.__arm=0; const _p = IDBObjectStore.prototype.put; let n=0; IDBObjectStore.prototype.put = function(...a){ if (window.__arm && ++n===window.__arm) throw new DOMException('quota','QuotaExceededError'); return _p.apply(this, a) }"
raw = json.dumps(good(profiles=[P('p1', 'A'), P('p2', 'B')], attempts=[{'id': 'a%d' % i, 'profileId': 'p1', 'ts': 5} for i in range(20)], cards=[{'id': 'p1:ا', 'profileId': 'p1', 'item': 'ا'}]))
f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(raw)
with sync_playwright() as p:
    b = p.chromium.launch()
    for arm in [3, 10, 25]:
        ctx, pg = newpage(b, init=FAULT); pg.goto(BASE); pg.wait_for_timeout(2000)
        pg.evaluate(f"window.__arm={arm}")
        with pg.expect_file_chooser(timeout=6000) as fc:
            pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText)).click()")
        fc.value.set_files(f); pg.wait_for_timeout(3000)
        c, d = counts(pg); print('arm', arm, 'toast', toast(pg), '| counts', {k: v for k, v in c.items() if v}, '| screen', pg.inner_text('#app')[:30].replace('\n', ' | '), pg._errs[:2])
        pg.evaluate("window.__arm=0")
        # retry works?
        with pg.expect_file_chooser(timeout=6000) as fc:
            pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Restore from a backup/.test(b.innerText))?.click()")
        fc.value.set_files(f); pg.wait_for_timeout(3000); c, d = counts(pg); print('   retry -> toast', toast(pg), {k: v for k, v in c.items() if v})
        ctx.close()
    b.close()
