import subprocess, shutil, os, sys
from h import *
S = '/tmp/claude-1000/swtest'
def swap(src):
    for f in os.listdir(S+'/site'):
        pth = S+'/site/'+f; shutil.rmtree(pth) if os.path.isdir(pth) else os.remove(pth)
    shutil.copytree(S+'/'+src, S+'/site', dirs_exist_ok=True)
    if src == 'A': open(S+'/site/assets/index-CTkYO871.js','a').write(";window.__BUILD='A';")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    for variant in ['B', 'B2']:
        swap('A')
        ctx = b.new_context(viewport=VP, service_workers='allow'); pg = ctx.new_page()
        pg.goto('http://localhost:5303/'); pg.wait_for_timeout(5000)
        print(variant, 'first load build:', pg.evaluate('window.__BUILD'), 'caches', pg.evaluate("caches.keys()"))
        swap(variant)
        pg.reload(); pg.wait_for_timeout(3000); r1 = pg.evaluate('window.__BUILD')
        pg.reload(); pg.wait_for_timeout(3000); r2 = pg.evaluate('window.__BUILD')
        pg.goto('http://localhost:5303/index.html?x=1'); pg.wait_for_timeout(2000); r3 = pg.evaluate('window.__BUILD')
        # explicit update check
        pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())"); pg.wait_for_timeout(3000); pg.reload(); pg.wait_for_timeout(3000); r4 = pg.evaluate('window.__BUILD')
        print(variant, 'after deploying new build -> reload1:', r1, 'reload2:', r2, 'query-url:', r3, 'after reg.update()+reload:', r4, 'caches', pg.evaluate("caches.keys()"))
        print('  html in page references:', pg.evaluate("[...document.scripts].map(s=>s.src).filter(x=>x.includes('assets'))"))
        ctx.close()
    b.close()
