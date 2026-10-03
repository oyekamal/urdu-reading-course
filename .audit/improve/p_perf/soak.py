# Today screen frame pacing at 6x CPU, then leak test over many navigations. Usage: s2_perf.py port minutes_for_soak
import sys, json, time
from h import *
PORT = sys.argv[1]; BASE = f'http://localhost:{PORT}/'; SOAK_MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0
TIMERS = """(()=>{window.__T=new Set();const st=window.setTimeout,ct=window.clearTimeout,si=window.setInterval,ci=window.clearInterval;
window.__Tn={timeoutsSet:0,intervalsSet:0};
window.setTimeout=function(f,ms,...a){window.__Tn.timeoutsSet++;const id=st(function(){window.__T.delete('t'+id);return typeof f==='function'?f.apply(this,arguments):0},ms,...a);window.__T.add('t'+id);return id};
window.clearTimeout=function(id){window.__T.delete('t'+id);return ct(id)};
window.setInterval=function(f,ms,...a){window.__Tn.intervalsSet++;const id=si(f,ms,...a);window.__T.add('i'+id);return id};
window.clearInterval=function(id){window.__T.delete('i'+id);return ci(id)};
window.__RAF=0;const r=window.requestAnimationFrame;window.requestAnimationFrame=f=>{window.__RAF++;return r(f)};})()"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox', '--js-flags=--expose-gc'])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block')
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept('5'))
    pg.add_init_script(TIMERS)
    cdp = ctx.new_cdp_session(pg); cdp.send('Performance.enable')
    quick_profile(pg, BASE)
    pg.wait_for_timeout(2500)
    def snap(tag):
        cdp.send('HeapProfiler.collectGarbage'); 
        c = cdp.send('Memory.getDOMCounters'); h = cdp.send('Runtime.getHeapUsage')
        d = pg.evaluate("()=>({marko:document.querySelectorAll('.marko').length,fx:document.querySelectorAll('.fx').length,svg:document.querySelectorAll('svg').length,svgNodes:document.querySelectorAll('svg *').length,canvas:document.querySelectorAll('canvas').length,audio:document.querySelectorAll('audio').length,img:document.querySelectorAll('img').length,timers:window.__T.size,all:document.querySelectorAll('*').length,bodyChildren:document.body.children.length,screen:(document.querySelector('#app')||{}).className})")
        r = {'tag': tag, 'domNodes': c['nodes'], 'jsListeners': c['jsEventListeners'], 'docs': c['documents'], 'heapMB': round(h['usedSize']/1e6, 2), **d}; return r
    print(snap('today_initial'))
    pg.screenshot(path=OUT+f'/soak_today_{PORT}.png')
    # ---- frame pacing, 6x CPU
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 6})
    res = pg.evaluate("""()=>new Promise(res=>{const ts=[];const lt=[];new PerformanceObserver(l=>l.getEntries().forEach(e=>lt.push(Math.round(e.duration)))).observe({type:'longtask'});
      let last=performance.now(),t0=last;function f(t){ts.push(t-last);last=t;if(t-t0<10000)requestAnimationFrame(f);else res({ts,lt})}requestAnimationFrame(f)})""")
    ts = res['ts'][1:]; import statistics
    ts_sorted = sorted(ts); n = len(ts)
    out = {'frames': n, 'fps': round(n/10, 1), 'median_ms': round(statistics.median(ts), 1), 'p95_ms': round(ts_sorted[int(n*.95)], 1), 'max_ms': round(max(ts), 1),
           'dropped_>33ms': sum(1 for x in ts if x > 33.4), 'dropped_>50ms': sum(1 for x in ts if x > 50), 'longtasks': len(res['lt']), 'longtask_total_ms': sum(res['lt']), 'longtask_max_ms': max(res['lt'] or [0])}
    print('TODAY 6x CPU 10s:', out)
    # ---- same with 1x for reference
    cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
    res = pg.evaluate("""()=>new Promise(res=>{const ts=[];let last=performance.now(),t0=last;function f(t){ts.push(t-last);last=t;if(t-t0<5000)requestAnimationFrame(f);else res(ts)}requestAnimationFrame(f)})""")
    ts = res[1:]; print('TODAY 1x 5s: fps', round(len(ts)/5,1), 'max', round(max(ts),1), 'dropped>33', sum(1 for x in ts if x>33.4))
    # metrics: script/layout duration at 1x for 5s
    m0 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}; pg.wait_for_timeout(5000)
    m1 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}
    cpu = {k: round(m1[k]-m0[k], 3) for k in ['ScriptDuration','LayoutDuration','RecalcStyleDuration','TaskDuration'] if k in m1}
    print('Today idle 5s CPU seconds (1x):', cpu)
    # ---- nav leak
    rows = [snap('before_nav')]
    keys = ['review', 'read', 'me', 'today']
    soak_end = time.time() + SOAK_MIN*60; i = 0; t_start = time.time()
    def navcycle(n):
        for _ in range(n):
            k = keys[i_[0] % 4]; i_[0] += 1
            try: pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`).click()", k)
            except Exception as e: errs.append('nav '+str(e)[:100])
            pg.wait_for_timeout(350)
    i_ = [0]
    for rnd in range(1, 6):
        navcycle(10); rows.append(snap(f'after_{rnd*10}_navs'))
    # open a lesson and back repeatedly
    def lessoncycle(n):
        for _ in range(n):
            try:
                click(pg, "button:has-text('Start:'), button:has-text('Continue:')", 4000); pg.wait_for_timeout(700)
                for _k in range(2):
                    pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
                pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Leave lesson')?.click()"); pg.wait_for_timeout(500)
                pg.evaluate("()=>document.querySelector(\".bottom button[data-k='today']\")?.click()"); pg.wait_for_timeout(400)
            except Exception as e: errs.append('lesson '+str(e)[:100])
    for rnd in range(1, 4):
        lessoncycle(5); rows.append(snap(f'after_lesson_open_x{rnd*5}'))
    while time.time() < soak_end:
        navcycle(16); lessoncycle(2); i_[0]=0; navcycle(0); pg.evaluate("document.querySelector(`.bottom button[data-k='today']`)?.click()"); pg.wait_for_timeout(400); r = snap(f'soak_{round((time.time()-t_start)/60,1)}min'); rows.append(r); print(r)
    for r in rows: print(r)
    print('timer sets total', pg.evaluate('window.__Tn'), 'raf calls', pg.evaluate('window.__RAF'))
    print('errors', errs[:8])
    json.dump({'frames': out, 'rows': rows, 'errs': errs}, open(OUT+f'/soak_{PORT}_{int(SOAK_MIN)}.json', 'w'), indent=1)
    b.close()
