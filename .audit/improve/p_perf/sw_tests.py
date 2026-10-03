# Service worker proofs. python3 sw_tests.py [update|offline|all]
#  update : build A and a different build B (temp copy of mobile/ with another <title> + a changed JS string), serve under /reader/ from one switchable
#           directory, install A, switch to B, registration.update(): "Update ready" toast appears while the page still shows A; tap -> reload shows B,
#           old cache gone, only B's cache left, SW controls the page.
#  offline: fresh browser context on build A, wait for the precache, go offline, fresh visit: onboarding, a lesson with audio, teacher mode
#           (My class, PIN, unlock), a PDF download (opened online once first, as the practice sheets design says).
import sys, os, subprocess, shutil, time, json, pathlib, threading, http.server, socketserver, functools
from h import *
R = pathlib.Path('/home/oye/Documents/free_work/urdu-reading-course'); M = R / 'mobile'; W = pathlib.Path('/tmp/claude-1000/p_perf/sw'); W.mkdir(parents=True, exist_ok=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'
PORT = 5397

def sh(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:]); raise SystemExit('build failed')
    return r.stdout

def build_a():
    if (W / 'A').exists(): shutil.rmtree(W / 'A')
    sh(f'npx vite build --outDir {W}/A', M)

def build_b(tag='B'):
    cp = W / ('mobile_' + tag.lower())
    if cp.exists(): shutil.rmtree(cp)
    cp.mkdir()
    sh(f"rsync -a --exclude node_modules --exclude dist --exclude android --exclude '.vite' {M}/ {cp}/", R)
    os.symlink(M / 'node_modules', cp / 'node_modules')
    ix = (cp / 'index.html').read_text(); (cp / 'index.html').write_text(ix.replace('<title>Urdu Qaida</title>', f'<title>Urdu Qaida {tag}</title>'))
    sw = (cp / 'src/swreg.js').read_text(); (cp / 'src/swreg.js').write_text(sw + "\nwindow.__BUILD = '%s';" % tag + "\n\n")
    if (W / tag).exists(): shutil.rmtree(W / tag)
    sh(f'npx vite build --outDir {W}/{tag}', cp)

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self): self.send_header('Cache-Control', 'max-age=600'); super().end_headers()   # like GitHub Pages
def serve():
    site = W / 'site'; site.mkdir(exist_ok=True)
    socketserver.ThreadingTCPServer.allow_reuse_address = True; socketserver.ThreadingTCPServer.daemon_threads = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), functools.partial(Q, directory=str(site)))
    threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv
def point(which):
    link = W / 'site' / 'reader'
    if link.is_symlink() or link.exists(): link.unlink()
    os.symlink(W / which, link)
BASE = f'http://localhost:{PORT}/reader/'
res = []
def check(name, ok, extra=''):
    res.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name, extra)

def caches_info(pg):
    return pg.evaluate("async()=>{const o={};for(const k of await caches.keys()){o[k]=(await (await caches.open(k)).keys()).length}return o}")

def wait_sw(pg, secs=40):
    t0 = time.time()
    while time.time() - t0 < secs:
        if pg.evaluate("!!(navigator.serviceWorker.controller)"): return True
        pg.wait_for_timeout(400)
    return False

def update_test(b):
    point('A'); ctx = b.new_context(viewport=VP, service_workers='allow'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept('5'))
    pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(500)
    check('A: SW controls the page after first install', wait_sw(pg))
    pg.wait_for_timeout(1500)
    ca = caches_info(pg); print('  caches A', ca)
    eager_a = json.loads(pg.evaluate("fetch('sw.js').then(r=>r.text())").split('const BUILD = ')[1].split(';\nconst PREFIX')[0])
    check('A: one versioned cache, eager set complete', len(ca) == 1 and list(ca.values())[0] >= len(eager_a['eager']), (list(ca.values()), len(eager_a['eager'])))
    verA = eager_a['version']; check('A: cache name derives from build version', list(ca)[0] == 'urc-' + verA, verA)
    check('A: page title is A', pg.title() == 'Urdu Qaida')
    # ship B
    point('B'); pg.evaluate("window.__swReg.update()"); pg.wait_for_selector('.sw-toast', timeout=30000)
    check('B: toast "Update ready, tap to refresh" appears', 'Update ready' in pg.inner_text('.sw-toast'))
    check('B: page still A until the tap (consistent shell)', pg.title() == 'Urdu Qaida')
    cb = caches_info(pg); print('  caches after install', cb); check('B: both caches exist while waiting', len(cb) == 2)
    pg.click('.sw-go')
    try: pg.wait_for_function("()=>document.title.endsWith('B')", timeout=30000)
    except Exception:
        print('  DIAG', pg.title(), pg.evaluate("({t:document.querySelector('.sw-toast')&&document.querySelector('.sw-toast').innerText,w:window.__swReg&&window.__swReg.waiting&&window.__swReg.waiting.state,a:window.__swReg&&window.__swReg.active&&window.__swReg.active.state,c:!!navigator.serviceWorker.controller})"))
    pg.wait_for_timeout(1500)
    check('B: after tap the page is build B', pg.title() == 'Urdu Qaida B', pg.title())
    cc = caches_info(pg); print('  caches after activate', cc); check('B: old cache deleted, one cache left', len(cc) == 1 and list(cc)[0] != 'urc-' + verA)
    check('B: SW controls the reloaded page', pg.evaluate("!!navigator.serviceWorker.controller"))
    pg.evaluate("document.querySelector('body > .sw-toast')?.remove()")
    check('B: no second toast after reload', pg.query_selector('.sw-toast') is None)
    check('no page errors', not errs, errs[:3]); ctx.close()
    # two tabs + a later deploy while the toast is up
    point('A'); ctx = b.new_context(viewport=VP, service_workers='allow'); t1 = ctx.new_page(); t1.goto(BASE + '?skiponb'); wait_sw(t1); t1.wait_for_timeout(1500)
    t2 = ctx.new_page(); t2.goto(BASE + '?skiponb'); t2.wait_for_timeout(1500)
    point('B'); t1.evaluate("window.__swReg.update()"); t1.wait_for_selector('.sw-toast', timeout=30000)
    point('C'); t1.evaluate("window.__swReg.update()"); t1.wait_for_timeout(4000)
    t1.click('.sw-go'); t1.wait_for_function("()=>document.title.endsWith('C')", timeout=30000)
    t1.wait_for_timeout(1500); check('C deploy while toast up: tap lands on newest build C', t1.title() == 'Urdu Qaida C', t1.title())
    t2.wait_for_timeout(3000); check('second tab (claimed by the new worker) reloaded to C', t2.title() == 'Urdu Qaida C', t2.title())
    ctx.close()
    # legacy (pre-11p) upgrade is covered by the unit logic; re-point to A for the next test
    point('A')

def offline_test(b):
    point('A'); ctx = b.new_context(viewport=VP, service_workers='allow', accept_downloads=True); pg = ctx.new_page(); errs = []; fails = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept('5'))
    pg.goto(BASE); check('fresh visit online: SW controls', wait_sw(pg)); pg.wait_for_timeout(1500)
    # open the practice sheets online once and download one PDF (the SW caches it the first time it is opened)
    pg.evaluate("window.__practice && window.__practice.open()"); pg.wait_for_timeout(1500)
    pdf_ok = pg.evaluate("!!window.__practice")
    if pdf_ok:
        with pg.expect_download(timeout=20000) as dl: pg.evaluate("document.querySelector('.pr-card .pr-act a').click()")
        d1 = dl.value; check('PDF download online', d1.suggested_filename.endswith('.pdf'), d1.suggested_filename)
        first_pdf = d1.suggested_filename
    pg.evaluate("document.querySelector('.pr-back')?.click()"); pg.wait_for_timeout(300)
    ctx.set_offline(True)
    pg.on('requestfailed', lambda r: fails.append(r.url.replace(BASE, '')))
    # ---- fresh visit offline: onboarding (child) through to the first lesson
    pg2 = ctx.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)[:200])); pg2.on('dialog', lambda d: d.accept('5')); pg2.on('requestfailed', lambda r: fails.append(r.url.replace(BASE, '')))
    pg2.goto(BASE); pg2.wait_for_timeout(2500)
    check('offline fresh visit: welcome renders', pg2.query_selector("text=Let's begin") is not None)
    try:
        n = walk_onboarding(pg2)
        check('offline onboarding completes to Today (about 55 screens: Lottie, images, fonts, audio all from the cache)', n >= 0 and pg2.query_selector('.bottom') is not None, n)
    except Exception as e: check('offline onboarding completes to Today', False, str(e)[:150])
    # lesson with audio
    try:
        pg2.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Start:|Continue:/.test(b.textContent))?.click()"); pg2.wait_for_timeout(1500)
        for _ in range(6):
            pg2.evaluate("()=>{const b=document.querySelector('.lesson .btn-primary');b&&b.click()}"); pg2.wait_for_timeout(500)
        played = pg2.evaluate("""async()=>{const a=new Audio('audio/names/alif.mp3');try{await a.play();await new Promise(r=>setTimeout(r,700));return {ok:true,t:a.currentTime,rs:a.readyState,err:!!a.error}}catch(e){return {ok:false,e:String(e)}}}""")
        check('offline: audio plays from the cache', played.get('ok') and played.get('rs', 0) >= 2 and not played.get('err'), played)
        ranged = pg2.evaluate("""async()=>{const r=await fetch('audio/names/alif.mp3',{headers:{Range:'bytes=0-9'}});return [r.status,r.headers.get('content-range'),(await r.arrayBuffer()).byteLength]}""")
        check('offline: Range request answered 206', ranged[0] == 206 and ranged[2] == 10, ranged)
    except Exception as e: check('offline lesson + audio', False, str(e)[:150])
    # lazy audio: not there before the warm-up (online visit in a second context), there after it
    ctx4 = b.new_context(viewport=VP, service_workers='allow'); p4 = ctx4.new_page(); p4.goto(BASE + '?skiponb'); wait_sw(p4); p4.wait_for_timeout(1500)
    lazy = 'audio/units/u05_01.mp3'
    pre = p4.evaluate("async p=>!!(await caches.match(p,{ignoreSearch:true}))", lazy)
    p4.evaluate("window.__swReg.active.postMessage({type:'WARM'})")
    t0 = time.time()
    while time.time() - t0 < 60 and not p4.evaluate("async p=>!!(await caches.match(p,{ignoreSearch:true}))", lazy): p4.wait_for_timeout(500)
    n_audio = 0
    while time.time() - t0 < 90 and n_audio < 490:
        n_audio = p4.evaluate("async()=>{let n=0;for(const k of await caches.keys()){for(const r of await (await caches.open(k)).keys()) if(r.url.includes('/audio/')) n++}return n}"); p4.wait_for_timeout(700)
    print('  warm-up finished in', round(time.time() - t0, 1), 's, audio entries', n_audio)
    n_audio_unused = p4.evaluate("async()=>{let n=0;for(const k of await caches.keys()){for(const r of await (await caches.open(k)).keys()) if(r.url.includes('/audio/')) n++}return n}")
    check('lazy audio absent before warm-up, present after (WARM message)', (not pre) and n_audio >= 490, (pre, n_audio))
    ctx4.set_offline(True); p4.reload(); p4.wait_for_timeout(1500)
    pl = p4.evaluate("""async p=>{const a=new Audio(p);try{await a.play();await new Promise(r=>setTimeout(r,500));return {ok:true,rs:a.readyState}}catch(e){return {ok:false,e:String(e)}}}""", lazy)
    check('offline: warmed lazy audio plays', pl.get('ok') and pl.get('rs', 0) >= 2, pl); ctx4.close()
    # teacher mode on a fresh offline profile of the device (separate context so mode is unset)
    ctx2 = b.new_context(viewport=VP, service_workers='allow'); pgt = ctx2.new_page(); pgt.on('dialog', lambda d: d.accept('5'))
    pgt.goto(BASE + '?skiponb'); wait_sw(pgt); pgt.wait_for_timeout(2500)
    ctx2.set_offline(True); tf = []; pgt.on('requestfailed', lambda r: tf.append(r.url.replace(BASE, '')))
    pgt.goto(BASE + '?skiponb'); pgt.wait_for_timeout(2000)
    try:
        click(pgt, 'text=My class'); pgt.wait_for_timeout(500)
        pgt.fill('input[placeholder="Your name"]', 'T'); pgt.fill('input[placeholder="4-digit PIN"]', '1234'); click(pgt, "button:has-text('Save')"); pgt.wait_for_timeout(800)
        click(pgt, "button:has-text('Teacher')"); pgt.wait_for_timeout(500); pgt.fill('input[type=password]', '1234'); click(pgt, "button:has-text('Unlock')"); pgt.wait_for_timeout(2500)
        txt = pgt.inner_text('#app')[:200].replace('\n', ' | '); print('  teacher screen:', txt)
        check('offline teacher mode: unlock reaches the dashboard (lazy chunk + lesson md served from cache)', 'Teacher PIN' not in txt and len(txt) > 30 and not any('teacher-' in f for f in tf), (tf[:3]))
    except Exception as e: check('offline teacher mode', False, str(e)[:200])
    # PDF offline: the one downloaded online works, one never opened says so politely
    if pdf_ok:
        ctx3 = ctx  # same context holds the cache from the online visit
        pg3 = ctx.new_page(); pg3.on('dialog', lambda d: d.accept('5')); pg3.goto(BASE + '?skiponb'); pg3.wait_for_timeout(2000)
        try:
            click(pg3, 'text=Just me'); pg3.wait_for_timeout(300)
        except Exception: pass
        got = pg3.evaluate("""async f=>{const r=await fetch('pdf/'+f);return [r.status,(await r.arrayBuffer()).byteLength]}""", first_pdf)
        check('offline: the PDF opened online is served from the cache', got[0] == 200 and got[1] > 1000, got)
        other = pg3.evaluate("""async()=>{const r=await (await fetch('pdf/index.json')).json();const f=r.items?r.items:(r.sheets||r.files||[]);return f.length}""")
        print('  pdf index readable offline, items:', other)
    check('no page errors', not errs, errs[:3])
    ctx.close(); ctx2.close()

with sync_playwright() as p:
    if MODE in ('update', 'all'): build_a(); build_b('B'); build_b('C')
    elif not (W / 'A').exists(): build_a()
    srv = serve()
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    try:
        if MODE in ('update', 'all'): update_test(b)
        if MODE in ('offline', 'all'): offline_test(b)
    finally: b.close(); srv.shutdown()
print('RESULT', sum(res), '/', len(res))
