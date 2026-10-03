from common import *
import random, sys
from h1_flows import mk
def sig(pg): return pg.evaluate("(document.querySelector('.lesson')?.innerText||'').slice(0,200)+'|'+(document.querySelector('.progress i')?.style.width||'')")
def run(gap, seed, slowdown=False):
    random.seed(seed)
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx, pg = newpage(b); quick_profile(pg, 'Fast'); mk(pg, [])
        click(pg, "button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(900)
        last = sig(pg); stuck_since = None; steps = 0; t_end = 90
        import time; t0 = time.time()
        while time.time() - t0 < t_end:
            if pg.query_selector('.celebrate'): break
            # choose target: primary action if present (Continue/Next/Check/Submit/Finish), else a random tile
            xy = pg.evaluate("""()=>{ const vis=e=>{const r=e.getBoundingClientRect(); return r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight&&!e.disabled};
               let prim=[...document.querySelectorAll('.lesson .btn-primary, .lesson button.act')].filter(vis);
               const tiles=[...document.querySelectorAll('.lesson .tile, .lesson .choices button, .lesson .keys .tile, .lesson .ob-opt')].filter(e=>vis(e)&&!e.classList.contains('ok')&&!e.classList.contains('no'));
               let pool = (prim.length && Math.random()<0.6) || !tiles.length ? prim : tiles; if(!pool.length) pool=[...document.querySelectorAll('.lesson button')].filter(vis);
               if(!pool.length) return null; const e=pool[Math.floor(Math.random()*pool.length)]; e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); return [r.x+r.width/2,r.y+r.height/2, e.innerText.slice(0,10)] }""")
            if xy: pg.mouse.click(xy[0], xy[1]); steps += 1
            pg.wait_for_timeout(gap)
            s = sig(pg)
            if s != last: last = s; stuck_since = time.time()
            elif stuck_since is None: stuck_since = time.time()
            elif time.time() - stuck_since > 12: print('  STUCK for 12s at', repr(s[:80])); break
        print(f'gap {gap} seed {seed}: celebrate={bool(pg.query_selector(".celebrate"))} steps={steps} secs={round(time.time()-t0)} errs={pg._errs[:2]}', flush=True)
        b.close()
for gap in [150, 400]:
    for seed in [1, 2]:
        run(gap, seed)
