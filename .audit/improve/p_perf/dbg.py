import sys
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200])); pg.on('dialog', lambda d: d.accept('5'))
    quick_profile(pg, BASE)
    for i in range(6):
        print(pg.evaluate("""()=>[...document.querySelectorAll('.marko')].map(m=>({st:m._marko.state,ph:m._marko.phase,ok:m._marko.ok,anim:!!m._marko.anim,pl:!!m._marko.player,run:m._marko.player&&m._marko.player.running,pau:m._marko.player&&m._marko.player.paused,f:m._marko.anim&&Math.round(m._marko.anim.currentFrame),calm:document.documentElement.classList.contains('calm'),kids:m.children.length}))"""))
        pg.wait_for_timeout(1500)
    print(errs); b.close()
