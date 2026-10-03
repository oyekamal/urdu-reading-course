import sys; sys.path.insert(0,'.')
from common import *
import json
BASE='http://localhost:5371/'
exec(open('n1_classexport.py').read().split("with sync_playwright")[0].replace("import sys; sys.path.insert(0,'.')",""))
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg=newpage(b); pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500)
    pg.evaluate(SEED,[NP,items]); pg.reload(); pg.wait_for_timeout(1500)
    click(pg,'.card.btn >> nth=0'); pg.wait_for_timeout(2500)
    nav(pg,'me')
    pg.wait_for_timeout(800)
    with pg.expect_download(timeout=60000) as dl:
        click(pg,"button:has-text('Export backup')"); gate_pass(pg)
    path='/tmp/claude-1000/vr3_export.json'; dl.value.save_as(path)
    import os; print('export bytes',os.path.getsize(path), 'cards', len(json.load(open(path))['cards']))
    ctx.close()
    ctx,pg=newpage(b); pg.goto(BASE); pg.wait_for_timeout(2500)
    with pg.expect_file_chooser() as fc: click(pg,'.ob-restore')
    fc.value.set_files(path); pg.wait_for_timeout(8000)
    print('toast',toast(pg)); print('counts',counts(pg)[0])
