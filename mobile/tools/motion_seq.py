# Motion sequences: records frame SEQUENCES (target 0/100/250/500/1000/2000 ms, plus 3000) after a trigger at 390x844,
# device_scale_factor 2, and builds a contact sheet per sequence. Real screenshots take ~60-120 ms, so every frame is labelled
# with the ACTUAL elapsed ms. Sequences: progress (lesson step advances the bar), celebrate (lesson-complete count-up),
# unlock (new unit opens on returning to the path), poke (tap Marko on Today).
# Usage: python3 tools/motion_seq.py [port] [outdir] [only,names]      (dev server: npx vite --port 5188)
import sys, os, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

PORT = sys.argv[1] if len(sys.argv) > 1 else '5188'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-1000/motion9b'
ONLY = sys.argv[3].split(',') if len(sys.argv) > 3 else None
TIMES = [0, 100, 250, 500, 1000, 2000, 3000]
os.makedirs(OUT, exist_ok=True)
MOD = "window.__mod=n=>performance.getEntriesByType('resource').map(e=>e.name).find(x=>x.includes('/src/'+n+'.js'))||('/src/'+n+'.js')"

def fresh(b, seed=True):
    """New child profile 'Zara' (unit 0 open), optionally seeded: 6 old pearls + ~9.6 minutes practised today."""
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, reduced_motion='no-preference')
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept())
    pg.add_init_script(MOD)
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(1800)
    pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', 'Zara'); pg.select_option('select >> nth=0', 'child'); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
    if seed:
        pg.evaluate("""async()=>{const S=await import(window.__mod('session'));const P=await import(window.__mod('path'));const {db,uid}=await import(window.__mod('db'));const {C}=await import(window.__mod('content'));
          const pid=await db.setting('activeProfile');const p=await S.getProgress(pid);const ls=P.lessonsFor(C.units[1]);const old=Date.now()-2*86400000;
          p.units[1]={lessons:Object.fromEntries(ls.slice(0,6).map((l,i)=>[l.id,old+i]))};await db.put('progress',p);
          const now=Date.now();for(let i=0;i<38;i++)await db.put('attempts',{id:uid(),profileId:pid,unit:0,drill:'seed',item:'x',correct:true,ms:0,ts:now-120000-(37-i)*15000});
          const pr=await db.get('profiles',pid);await db.put('profiles',{...pr,minutes:10});}""")
        pg.reload(); pg.wait_for_timeout(2800)
    return ctx, pg, errs

def grab(pg, name, trigger, clip=None, times=TIMES):
    d = f'{OUT}/{name}'; os.makedirs(d, exist_ok=True)
    for f in os.listdir(d): os.remove(f'{d}/{f}')
    frames = []
    trigger(); t0 = time.perf_counter()
    for t in times:
        while (time.perf_counter() - t0) * 1000 < t: time.sleep(0.003)
        el = round((time.perf_counter() - t0) * 1000); fn = f'{d}/{t:04d}.png'
        pg.screenshot(path=fn, clip=clip); frames.append((el, fn))
    sheet(name, frames, d); return frames

def sheet(name, frames, d, cols=None):
    ims = [(el, Image.open(fn).convert('RGB')) for el, fn in frames]; w, h = ims[0][1].size; s = 0.5 if w > 500 else 1
    tw, th = int(w * s), int(h * s); cols = cols or min(len(ims), 7 if tw < 250 else 4); rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * tw, rows * (th + 22)), (30, 30, 40)); dr = ImageDraw.Draw(S)
    for i, (el, im) in enumerate(ims):
        x, y = (i % cols) * tw, (i // cols) * (th + 22); S.paste(im.resize((tw, th)), (x, y + 22)); dr.text((x + 6, y + 5), f'{name}  +{el} ms', fill=(255, 255, 255))
    S.save(f'{d}/sheet.png'); S.save(f'{OUT}/{name}_sheet.png'); print('sheet', f'{OUT}/{name}_sheet.png')

def main():
    run = lambda n: ONLY is None or n in ONLY
    with sync_playwright() as p:
        b = p.chromium.launch(); allerrs = []
        # 1. progress: the first lesson screen's Continue advances the bar
        if run('progress'):
            ctx, pg, errs = fresh(b)
            # unit 0 has a 3-screen rules lesson; bar goes 0 -> 33%
            pg.click("button:has-text('Start:'), button:has-text('Continue:')"); pg.wait_for_timeout(1200)
            pg.screenshot(path=f'{OUT}/progress_before.png')
            clip = {'x': 0, 'y': 60, 'width': 390, 'height': 150}
            grab(pg, 'progress', lambda: pg.evaluate("()=>[...document.querySelectorAll('.btn-primary')].pop().click()"), clip=clip)
            pg.wait_for_timeout(1300)
            grab(pg, 'progress2', lambda: pg.evaluate("()=>[...document.querySelectorAll('.btn-primary')].pop().click()"), clip=clip, times=[0, 100, 250, 500, 1000, 1500, 2000])
            allerrs += errs; ctx.close()
        # 2. celebrate: finishing the last screen -> count-up on the full-screen celebration (6 old pearls -> 7, goal crossed)
        if run('celebrate'):
            ctx, pg, errs = fresh(b)
            pg.click("button:has-text('Start:'), button:has-text('Continue:')"); pg.wait_for_timeout(900)
            for _ in range(2):
                pg.evaluate("()=>[...document.querySelectorAll('.btn-primary')].pop().click()"); pg.wait_for_timeout(1200)
            grab(pg, 'celebrate', lambda: pg.evaluate("()=>[...document.querySelectorAll('.btn-primary')].pop().click()"), times=[0, 100, 250, 500, 800, 1000, 1500, 2000, 3000])
            allerrs += errs; ctx.close()
        # 3. unlock: pass unit 0 while on another tab, return to Today -> unit 1 card unlocks
        if run('unlock'):
            ctx, pg, errs = fresh(b, seed=False)
            pg.evaluate("window.scrollTo(0,0)")
            pg.evaluate("()=>document.querySelector(\".bottom button[data-k='review']\").click()"); pg.wait_for_timeout(700)
            pg.evaluate("""async()=>{const S=await import(window.__mod('session'));const {db}=await import(window.__mod('db'));const pid=await db.setting('activeProfile');await S.markUnit(pid,0,10,10);await S.ensureCards(pid,1)}""")
            grab(pg, 'unlock', lambda: pg.evaluate("()=>document.querySelector(\".bottom button[data-k='today']\").click()"), times=[0, 100, 250, 500, 1000, 1400, 1800, 2200, 3000])
            allerrs += errs; ctx.close()
        # 4. poke Marko on Today
        if run('poke'):
            ctx, pg, errs = fresh(b)
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(2500)
            clip = {'x': 0, 'y': 60, 'width': 390, 'height': 560}
            grab(pg, 'poke', lambda: pg.evaluate("()=>document.querySelector('.hh-poke').click()"), clip=clip, times=[0, 100, 250, 500, 1000, 2000, 3000, 4200])
            pg.screenshot(path=f'{OUT}/today_full.png')
            allerrs += errs; ctx.close()
        b.close()
    print('page errors:', allerrs[:5])

main()
