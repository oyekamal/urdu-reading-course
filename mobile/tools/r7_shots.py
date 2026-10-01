# Round-7 design shots: home (Learn), units, review, Me/Progress/More for a child and an adult profile at 390x844.
# Usage: python3 tools/r7_shots.py [port] [outdir] [prefix]
import sys, os
from playwright.sync_api import sync_playwright
port = sys.argv[1] if len(sys.argv) > 1 else '5188'; out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-1000/r7a'; pre = sys.argv[3] if len(sys.argv) > 3 else 'after'
os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    for track in ['child', 'adult']:
        pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept())
        pg.add_init_script("window.__mod=n=>performance.getEntriesByType('resource').map(e=>e.name).find(x=>x.includes('/src/'+n+'.js'))||('/src/'+n+'.js')")
        pg.goto(f'http://localhost:{port}/?skiponb'); pg.wait_for_timeout(1800); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300)
        pg.fill('input[placeholder=Name]', 'Zara'); pg.select_option('select >> nth=0', track); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
        # pass unit 0 and a couple of unit-1 lessons so the home shows real progress, then reload Learn
        pg.evaluate("""async()=>{const S=await import(window.__mod('session'));const P=await import(window.__mod('path'));const {db}=await import(window.__mod('db'));const {C}=await import(window.__mod('content'));const pid=await db.setting('activeProfile');
          await S.markUnit(pid,0,10,10);await S.ensureCards(pid,1);const p=await S.getProgress(pid);const ls=P.lessonsFor(C.units[1]);p.units[1]={...(p.units[1]||{}),lessons:{[ls[0].id]:Date.now(),[ls[1].id]:Date.now()}};await db.put('progress',p);
          await S.ensureCards(pid,2);await S.ensureCardsFor(pid,['ا','ب'])}""")
        pg.reload(); pg.wait_for_timeout(3500); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(600)
        t = track[0]
        pg.screenshot(path=f'{out}/{pre}_{t}_home.png'); pg.screenshot(path=f'{out}/{pre}_{t}_home_full.png', full_page=True)
        def nav(k):
            pg.evaluate(f"()=>document.querySelector(\".bottom button[data-k='{k}']\").click()"); pg.wait_for_timeout(1200)
        if pg.query_selector(".bottom button[data-k='units']"): nav('units')
        else: pg.evaluate("()=>document.querySelector('.all-units').click()"); pg.wait_for_timeout(1200)
        pg.screenshot(path=f'{out}/{pre}_{t}_units.png'); pg.screenshot(path=f'{out}/{pre}_{t}_units_full.png', full_page=True)
        nav('review'); pg.screenshot(path=f'{out}/{pre}_{t}_review.png')
        if pg.query_selector(".bottom button[data-k='me']"): nav('me'); pg.screenshot(path=f'{out}/{pre}_{t}_me.png'); pg.screenshot(path=f'{out}/{pre}_{t}_me_full.png', full_page=True)
        else:
            nav('progress'); pg.screenshot(path=f'{out}/{pre}_{t}_progress.png'); nav('more'); pg.screenshot(path=f'{out}/{pre}_{t}_more.png')
        pg.close()
    print('errors:', errs); b.close()
