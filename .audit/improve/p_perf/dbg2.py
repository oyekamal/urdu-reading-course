import sys
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page()
    pg.on('dialog', lambda d: d.accept('5'))
    quick_profile(pg, BASE)
    print(pg.evaluate("""()=>({hidden:document.hidden, mw:[...document.querySelectorAll('.marko')].map(m=>m._mw&&{in:m._mw.inView,last:m._mw.last}), cls:document.documentElement.className, ov:[...document.querySelectorAll('body > .celebrate, body > .gate-back, body > .pr-ov, body > .stk-ov, body > .a11y-sheet, body > [role=dialog], body > [aria-modal=true]')].map(n=>n.className)})"""))
    b.close()
