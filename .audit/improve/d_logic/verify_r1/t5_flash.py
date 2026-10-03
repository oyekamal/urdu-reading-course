import json, h
from playwright.sync_api import sync_playwright
import t5_egra as T
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=h.EXE); pg = b.new_context(viewport={'width':390,'height':800}).new_page(); pg.errors=[]; pg.on('pageerror', lambda e: pg.errors.append(str(e)[:200]))
    pg.clock.install(time=1_700_000_000_000); pg.goto(h.URL); pg.wait_for_timeout(1500); pg.clock.pause_at(1_700_000_100_000)
    pg.evaluate(T.BOOT); pg.wait_for_timeout(200)
    # subtask 1: the child reads 3 letters in 60 s; teacher marks nothing; timer expires
    pg.clock.run_for(61000); pg.wait_for_timeout(100)
    print('after s1:', pg.inner_text('#eg h2'))
    for _ in range(2): T.btn(pg,'Skip')
    T.btn(pg,'Skip')   # passage skip
    r = T.finish_to_result(pg, None); print(r)
    b.close()
