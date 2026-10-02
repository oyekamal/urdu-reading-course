# First-run load: request log + weights by type, with CPU 4x + Slow4G, through onboarding to Today (fresh context, SW blocked)
import sys, json, time
from collections import defaultdict
from h import *
PORT = sys.argv[1]; BASE = f'http://localhost:{PORT}/'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=["--no-sandbox"])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block', reduced_motion='no-preference')
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type in ('error','warning') and errs.append(m.type+': '+m.text[:200]))
    pg.on('dialog', lambda d: d.accept('5'))
    cdp = ctx.new_cdp_session(pg); cdp.send('Network.enable'); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150, 'downloadThroughput': 1.6*1024*1024/8*0.9, 'uploadThroughput': 750*1024/8, 'connectionType': 'cellular4g'})
    reqs = {}; phase = ['boot']; t0 = time.time()
    def rq(e): reqs[e['requestId']] = {'url': e['request']['url'], 'phase': phase[0], 't': round(time.time()-t0,2), 'type': e.get('type')}
    def fin(e):
        r = reqs.get(e['requestId']); 
        if r: r['bytes'] = e['encodedDataLength']
    cdp.on('Network.requestWillBeSent', rq); cdp.on('Network.loadingFinished', fin)
    pg.add_init_script("""window.__lt=[];new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__lt.push([Math.round(e.startTime),Math.round(e.duration)]))).observe({type:'longtask',buffered:true});
    window.__cls=0;new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__cls+=e.value})).observe({type:'layout-shift',buffered:true});
    window.__lcp=0;new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});""")
    pg.goto(BASE, wait_until='load'); pg.wait_for_timeout(3000)
    nav = pg.evaluate("()=>{const n=performance.getEntriesByType('navigation')[0];const f=performance.getEntriesByType('paint');return {dcl:Math.round(n.domContentLoadedEventEnd),load:Math.round(n.loadEventEnd),paint:f.map(x=>[x.name,Math.round(x.startTime)]),lcp:Math.round(window.__lcp),cls:window.__cls}}")
    print('welcome', nav); pg.screenshot(path=OUT+'/s1_welcome.png')
    phase[0] = 'onboarding'
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1}); cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 0, 'downloadThroughput': -1, 'uploadThroughput': -1})
    onboard_child(pg, BASE) if False else None
    # drive onboarding using page already loaded
    click(pg, "text=Let's begin"); pg.wait_for_timeout(500)
    click(pg, '.ob-sleeper'); pg.wait_for_timeout(2600)
    click(pg, '.ob-sw >> nth=0'); click(pg, '.ob-cta')
    click(pg, ".ob-opt:has-text('My child')"); pg.wait_for_timeout(1500); pg.fill('#ob-name', 'Zara')
    click(pg, '.ob-cta'); click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(1500)
    click(pg, '.ob-opt >> nth=0'); pg.wait_for_timeout(1500); click(pg, '.ob-opt >> nth=0'); pg.wait_for_timeout(1500)
    click(pg, '.ob-opt >> nth=0'); click(pg, '.ob-opt >> nth=3'); click(pg, '.ob-cta')
    pg.wait_for_timeout(900); click(pg, '.ob-cta'); click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(5000)
    click(pg, '.ob-cta'); click(pg, '.ob-cta')
    for t in ['ب', 'ا', 'ب']:
        click(pg, f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(950)
    click(pg, '.ob-cta'); click(pg, 'text=Join them'); pg.wait_for_timeout(1500); click(pg, '.ob-cta')
    click(pg, '.ob-word'); pg.wait_for_timeout(1400); click(pg, '.ob-cta')
    click(pg, ".ob-choices .tile:text-is('بابا')"); pg.wait_for_timeout(1300); click(pg, '.ob-cta')
    pg.wait_for_timeout(1000); click(pg, '.ob-foot .btn-primary'); pg.wait_for_timeout(900); click(pg, '.ob-cta')
    click(pg, '.ob-opt >> nth=1'); pg.wait_for_timeout(1500); click(pg, '.ob-cta'); pg.wait_for_timeout(2500)
    phase[0] = 'today'; pg.screenshot(path=OUT+'/s1_today.png')
    # start a lesson
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(1500); phase[0] = 'lesson'
    pg.screenshot(path=OUT+'/s1_lesson.png')
    lt = pg.evaluate('window.__lt'); cls = pg.evaluate('window.__cls')
    # aggregate
    agg = defaultdict(lambda: [0,0]); byphase = defaultdict(lambda: defaultdict(lambda:[0,0]))
    def kind(u):
        u = u.split('?')[0]
        for k,ext in [('audio','.mp3'),('lottie','.json'),('img','.webp'),('img','.png'),('font','.ttf'),('font','.woff2'),('js','.js'),('css','.css'),('data','.json')]:
            if u.endswith(ext) and (k!='lottie' or '/lottie/' in u) and (k!='data' or '/data/' in u): return k
        return 'other'
    for r in reqs.values():
        k = kind(r['url']); n = r.get('bytes') or 0
        agg[k][0]+=1; agg[k][1]+=n; byphase[r['phase']][k][0]+=1; byphase[r['phase']][k][1]+=n
    print('TOTAL by kind', {k:(v[0], round(v[1]/1024)) for k,v in agg.items()})
    for ph, d in byphase.items(): print(ph, {k:(v[0], round(v[1]/1024)) for k,v in d.items()})
    print('longtasks (start,dur)', lt[:30], 'cls', cls)
    print('errors', errs[:10])
    json.dump({'nav': nav, 'reqs': list(reqs.values()), 'longtasks': lt, 'cls': cls, 'errs': errs}, open(OUT+'/s1_first_run.json','w'), indent=1)
    b.close()
