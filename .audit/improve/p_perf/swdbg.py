import sys
sys.argv=['x','none']
exec(open('sw_tests.py').read().split("with sync_playwright() as p:\n    if MODE")[0])
with sync_playwright() as p:
    srv = serve(); point('A')
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport=VP, service_workers='allow'); pg = ctx.new_page()
    pg.on('console', lambda m: print('console', m.type, m.text[:300])); pg.on('pageerror', lambda e: print('pageerror', str(e)[:300])); pg.on('requestfailed', lambda r: print('reqfail', r.url[-80:]))
    pg.goto(BASE); pg.wait_for_timeout(8000)
    print(pg.title(), pg.evaluate('!!window.Capacitor'), pg.evaluate('document.readyState'), len(pg.content()))
    print(pg.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration();return r?{a:r.active&&r.active.state,i:r.installing&&r.installing.state,w:r.waiting&&r.waiting.state}:null}"""))
    b.close(); srv.shutdown()
