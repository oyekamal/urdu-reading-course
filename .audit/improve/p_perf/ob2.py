import sys
from h import *
BASE = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport=VP, service_workers='block'); pg = ctx.new_page(); pg.on('dialog', lambda d: d.accept('5'))
    pg.goto(BASE); pg.wait_for_timeout(2500); n = walk_onboarding(pg); print('steps', n, pg.inner_text('#app')[:120].replace('\n', ' | '))
    b.close()
