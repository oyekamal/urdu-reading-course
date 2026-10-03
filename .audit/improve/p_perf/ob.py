import sys
from h import *
BASE = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox']); ctx = b.new_context(viewport=VP, service_workers='block'); pg = ctx.new_page(); pg.on('dialog', lambda d: d.accept('5'))
    try: onboard_child(pg, BASE); print('ok', pg.inner_text('body')[:100].replace('\n',' | '))
    except Exception as e: print('FAIL', str(e)[:300]); print(pg.inner_text('#app')[:300])
    b.close()
