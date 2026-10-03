"""Playwright check of the Practice screen (round 11f). Usage: python3 screen_test.py [port]"""
import sys, glob, json
from playwright.sync_api import sync_playwright
port = sys.argv[1] if len(sys.argv) > 1 else '5188'
URL = f'http://localhost:{port}/'
exe = (sorted(glob.glob('/home/oye/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')) or [None])[-1]
SH = '/home/oye/Documents/free_work/urdu-reading-course/.audit/improve/f_pdf/shots/'
res = []
def ok(name, cond, extra=''):
    res.append((name, bool(cond), extra)); print(('PASS ' if cond else 'FAIL ') + name, extra, flush=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    for label, vp, scheme, reduce in [('phone', (360, 640), 'light', 'no-preference'), ('phone_dark', (360, 640), 'dark', 'no-preference'), ('tablet', (820, 1180), 'light', 'reduce')]:
        ctx = b.new_context(viewport={'width': vp[0], 'height': vp[1]}, color_scheme=scheme, reduced_motion=reduce, accept_downloads=True, service_workers='allow')
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'favicon' not in m.text else None)
        pg.goto(URL); pg.wait_for_timeout(1500)
        pg.evaluate("import('/src/practice.js').then(m => m.openPractice())"); pg.wait_for_selector('.pr-card', timeout=8000)
        ok(f'{label}: window.__practice exposed', pg.evaluate("typeof window.__practice?.open === 'function'"))
        pg.wait_for_timeout(400); pg.screenshot(path=SH + f'{label}_start.png')
        # tap targets and overflow
        small = pg.evaluate("""() => [...document.querySelectorAll('.pr-ov button, .pr-ov a.btn, .pr-ov summary')].filter(e => { const r = e.getBoundingClientRect(); return r.width && (r.height < 44 || r.width < 44); }).map(e => e.textContent.trim().slice(0, 20))""")
        ok(f'{label}: all tap targets >= 44px', not small, str(small))
        ok(f'{label}: no horizontal overflow', pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1 && document.querySelector('.pr-scroll').scrollWidth <= document.querySelector('.pr-scroll').clientWidth + 1"))
        prim = pg.evaluate("document.querySelectorAll('.pr-ov .btn-primary').length")
        ok(f'{label}: exactly one primary action', prim == 1, str(prim))
        if label == 'phone':
            # open unit tab 1 and tap Open on 3 sheets
            pg.click('[role=tab][aria-label^="Unit 1,"]'); pg.wait_for_timeout(300); pg.screenshot(path=SH + f'{label}_unit1.png')
            hdr = pg.inner_text('.pr-gh b'); ok('unit tab shows unit title', 'Unit 1' in hdr, hdr)
            n = 0
            for i in (0, 2, 5):
                with pg.expect_download(timeout=10000) as d:
                    pg.locator('.pr-card a.btn').nth(i).click()
                dl = d.value; path = dl.path(); data = open(path, 'rb').read(4); n += 1
                ok(f'download #{i}: {dl.suggested_filename} is a PDF', data == b'%PDF', str(dl.suggested_filename))
            # Share/Print on web (no navigator.share in headless chromium -> opens the file in a tab)
            with ctx.expect_page(timeout=8000) as np_:
                pg.locator('.pr-card button.btn').nth(1).click()
            ok('Share/Print opens the PDF (fallback) or shares', True, np_.value.url[-30:]); np_.value.close()
            # offline: a sheet opened before must still download
            pg.wait_for_timeout(800)
            ctx.set_offline(True)
            try:
                with pg.expect_download(timeout=8000) as d:
                    pg.locator('.pr-card a.btn').nth(0).click()
                ok('offline: previously opened sheet still downloads', open(d.value.path(), 'rb').read(4) == b'%PDF')
            except Exception as e:
                ok('offline: previously opened sheet still downloads', False, str(e)[:120])
            ctx.set_offline(False)
            # keyboard: Escape closes, focus returns
            pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
            ok('Escape closes the screen', pg.evaluate("!document.querySelector('.pr-ov')"))
        else:
            pg.click('[role=tab][aria-label^="Unit 4,"]'); pg.wait_for_timeout(300); pg.screenshot(path=SH + f'{label}_unit4.png')
        ok(f'{label}: no console/page errors', not errs, str(errs[:2]))
        ctx.close()
    b.close()
fails = [r for r in res if not r[1]]
print(f'\n{len(res) - len(fails)}/{len(res)} passed')
sys.exit(1 if fails else 0)
