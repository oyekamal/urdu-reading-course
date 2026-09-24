# Hi-res raws of the playful lesson states for the store screenshots (1080-wide). Usage: python3 tools/store_shots_play.py [port]
# Complements store_shots.py (progress / teacher / nastaliq / words). Seeds lesson progress straight into IndexedDB.
import sys; from playwright.sync_api import sync_playwright
port = sys.argv[1] if len(sys.argv) > 1 else '5188'; out = '../store/raw'
SEED = """async(ids)=>{const {db}=await import('/src/db.js');const p=(await db.all('profiles'))[0];const now=Date.now();const pr=(await db.get('progress',p.id))||{id:p.id,units:{},wpm:[],sessions:0};pr.units[0]={passed:true,score:3,total:3,at:now,lessons:{rules:now,done:now}};pr.units[1]={lessons:Object.fromEntries(ids.map(i=>[i,now]))};await db.put('progress',pr);}"""
U1 = ['Lalif', 'Lbe', 'Lkaf', 'Llam', 'Lmim', 'Lnun', 'marks', 'join', 'blend']
with sync_playwright() as p:
    b = p.chromium.launch()
    def start(ids):
        pg = b.new_page(viewport={"width": 412, "height": 880}, device_scale_factor=2.62); pg.on("dialog", lambda d: d.accept())
        pg.goto(f"http://localhost:{port}/"); pg.wait_for_timeout(1500)
        pg.click("text=Just me"); pg.wait_for_timeout(300); pg.click("text=+ Add a learner"); pg.fill("input[placeholder=Name]", "Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
        pg.evaluate(SEED, ids); pg.reload(); pg.wait_for_timeout(2500); return pg
    js = lambda pg, h: pg.evaluate("e=>e.click()", h)
    pg = start(U1[:4]); pg.screenshot(path=f"{out}/11_path.png")                       # pearl path, 4 ticks, mim glowing
    pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1300); js(pg, pg.query_selector(".btn-primary.btn-wide")); pg.wait_for_timeout(900)
    pg.screenshot(path=f"{out}/09_tap.png"); pg.close()                                # tap what you hear, 5 letter tiles
    pg = start(U1[:8]); pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1300); pg.screenshot(path=f"{out}/14_blend.png"); pg.close()
    pg = start(U1); pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1300); js(pg, pg.query_selector(".btn-primary.btn-wide")); pg.wait_for_timeout(900)
    for ch in "با":  # baba is built right to left: ب then ا (half-built looks alive)
        for t in pg.query_selector_all(".choices .tile:not([disabled])"):
            if t.inner_text().strip() == ch: js(pg, t); pg.wait_for_timeout(250); break
    pg.screenshot(path=f"{out}/10_build.png"); pg.close()
    pg = start([]); pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1300)          # alif: trace, then quiz answered right, then celebration
    for _ in range(12):
        cv = pg.query_selector("canvas.trace")
        if cv:
            bb = cv.bounding_box(); pg.mouse.move(bb['x'] + bb['width'] * 0.5, bb['y'] + bb['height'] * 0.18); pg.mouse.down()
            for k in range(24): pg.mouse.move(bb['x'] + bb['width'] * 0.5, bb['y'] + bb['height'] * (0.18 + 0.64 * k / 23))
            pg.mouse.up(); pg.wait_for_timeout(300); pg.screenshot(path=f"{out}/13_traced.png")
        q = pg.evaluate("()=>{const c=document.querySelector('.choices');return c?c.parentElement.innerText:''}")
        tiles = pg.query_selector_all(".choices .tile:not([disabled])")
        if tiles and not pg.query_selector(".btn-primary.btn-wide"):
            want_joined = ('final' in q.split('\n')[-2] if len(q.split('\n')) > 1 else False) or 'final' in q[-60:]
            pick = [t for t in tiles if ('ـ' in t.inner_text()) == want_joined] or tiles
            js(pg, pick[0]); pg.wait_for_timeout(600); continue
        if 'done' in (pg.evaluate("()=>document.querySelector('#app').innerText") or '')[:200]: break
        pr = pg.query_selector(".btn-primary.btn-wide")
        if not pr: break
        js(pg, pr); pg.wait_for_timeout(900)
    pg.wait_for_timeout(800); pg.screenshot(path=f"{out}/12_done.png"); print("play raws done"); b.close()
