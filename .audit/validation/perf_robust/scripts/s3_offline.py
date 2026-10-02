import sys, json, os, glob, time
from h import *
BASE = sys.argv[1] if sys.argv[1].startswith('http') else f'http://localhost:{sys.argv[1]}/'; TAG = sys.argv[2] if len(sys.argv)>2 else 'x'; DIST = '/home/oye/Documents/free_work/urdu-reading-course/mobile/dist'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    ctx = b.new_context(viewport=VP, service_workers='allow'); pg = ctx.new_page(); errs = []; fails = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept('5'))
    t0 = time.time(); pg.goto(BASE); 
    pg.wait_for_function("navigator.serviceWorker.controller!==null || true")
    # wait for cache to fill (SW install is async; precache of 490 audio)
    last = -1; stable = 0
    while stable < 4 and time.time()-t0 < 120:
        n = pg.evaluate("async()=>{let t=0;for(const k of await caches.keys()){t+=(await (await caches.open(k)).keys()).length}return t}")
        stable = stable+1 if n == last else 0; last = n; pg.wait_for_timeout(500)
    print('cache entries', last, 'filled in ~', round(time.time()-t0,1), 's')
    info = pg.evaluate("async()=>{const out={};for(const k of await caches.keys()){const c=await caches.open(k);const ks=(await c.keys()).map(r=>new URL(r.url).pathname);out[k]=ks}return out}")
    print({k: len(v) for k, v in info.items()}, 'sw controller:', pg.evaluate("!!navigator.serviceWorker.controller"))
    cached = set(); [cached.update(v) for v in info.values()]
    files = [ '/' + os.path.relpath(f, DIST) for f in glob.glob(DIST + '/**/*', recursive=True) if os.path.isfile(f)]
    base = '/'
    unc = sorted(f for f in files if f not in cached and f not in ('/index.html',))
    from collections import Counter
    print('dist files', len(files), 'not cached', len(unc), Counter(u.split('/')[1] for u in unc))
    print('uncached sample', [u for u in unc if not u.startswith('/audio')][:40])
    json.dump({'cache_count': last, 'uncached': unc, 'secs': round(time.time()-t0,1)}, open(OUT+'/s3_cache_'+TAG+'.json','w'), indent=1)
    # ---- go offline, reload, walk
    ctx.set_offline(True)
    pg.on('requestfailed', lambda r: fails.append(('FAIL', r.url.replace(BASE,''))))
    pg.on('response', lambda r: r.status >= 400 and fails.append((r.status, r.url.replace(BASE,''))))
    reqs = []; pg.on('request', lambda r: reqs.append(r.url.replace(BASE,'')))
    pg.reload(); pg.wait_for_timeout(2500)
    print('offline reload title:', pg.title(), '| welcome visible:', pg.query_selector('text=Let\'s begin') is not None)
    onboard_child(pg, BASE) if False else None
    # onboarding walk offline (same steps)
    try:
        click(pg, "text=Let's begin"); pg.wait_for_timeout(500)
        click(pg, '.ob-sleeper'); pg.wait_for_timeout(2600)
        click(pg, '.ob-sw >> nth=0'); click(pg, '.ob-cta')
        click(pg, ".ob-opt:has-text('My child')"); pg.wait_for_timeout(1500); pg.fill('#ob-name', 'Zara')
        click(pg, '.ob-cta'); click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(1500)
        click(pg, '.ob-opt >> nth=0'); pg.wait_for_timeout(1500); click(pg, '.ob-opt >> nth=0'); pg.wait_for_timeout(1500)
        click(pg, '.ob-opt >> nth=0'); click(pg, '.ob-opt >> nth=3'); click(pg, '.ob-cta')
        pg.wait_for_timeout(900); click(pg, '.ob-cta'); click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(4500)
        click(pg, '.ob-cta'); click(pg, '.ob-cta')
        for t in ['ب', 'ا', 'ب']:
            click(pg, f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(950)
        click(pg, '.ob-cta'); click(pg, 'text=Join them'); pg.wait_for_timeout(1500); click(pg, '.ob-cta')
        click(pg, '.ob-word'); pg.wait_for_timeout(1400); click(pg, '.ob-cta')
        click(pg, ".ob-choices .tile:text-is('بابا')"); pg.wait_for_timeout(1300); click(pg, '.ob-cta')
        pg.wait_for_timeout(1000); click(pg, '.ob-foot .btn-primary'); pg.wait_for_timeout(900); click(pg, '.ob-cta')
        click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(1500); click(pg, '.ob-cta'); pg.wait_for_timeout(2500)
        print('onboarding offline OK -> today:', pg.query_selector("button:has-text('Start:')") is not None)
        pg.screenshot(path=OUT+'/s3_offline_today_'+TAG+'.png')
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(800)
        for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(600)
        pg.evaluate("()=>document.querySelector('.btn-play')?.click()"); pg.wait_for_timeout(1500)
        # visit all tabs incl. lazy chunk (teacher) via adult path? tabs
        for k in ['review','read','me','today']:
            pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`)?.click()", k); pg.wait_for_timeout(700)
        pg.screenshot(path=OUT+'/s3_end_'+TAG+'.png')
    except Exception as e:
        print('WALK ERROR', str(e)[:300]); pg.screenshot(path=OUT+'/s3_error_'+TAG+'.png')
    print('offline failures:', sorted(set(map(str, fails)))[:40]); print('page errors', errs[:5])
    print('audio played src:', pg.evaluate("window.__last||null"))
    b.close()
