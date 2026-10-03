import sys
sys.argv=['x','none']
exec(open('sw_tests.py').read().split("with sync_playwright() as p:\n    if MODE")[0])
with sync_playwright() as p:
    srv = serve(); point('A')
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport=VP, service_workers='allow'); pg = ctx.new_page()
    pg.on('console', lambda m: print('console', m.text[:200])); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300]))
    pg.goto(BASE+'?skiponb'); wait_sw(pg); pg.wait_for_timeout(1500); point('B'); pg.evaluate("window.__swReg.update()"); pg.wait_for_selector('.sw-toast', timeout=30000)
    print(pg.evaluate("({w:window.__swReg.waiting&&window.__swReg.waiting.state,a:window.__swReg.active&&window.__swReg.active.state})"))
    pg.click('.sw-go'); pg.wait_for_timeout(4000); print(pg.title(), pg.inner_text('.sw-toast') if pg.query_selector('.sw-toast') else None, pg.evaluate("({w:window.__swReg.waiting&&window.__swReg.waiting.state,a:window.__swReg.active&&window.__swReg.active.state})"))
    b.close(); srv.shutdown()
