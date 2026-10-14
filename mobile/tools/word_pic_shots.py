# Screens that show word pictures, for the critic loop. Usage: python3 tools/word_pic_shots.py [port] [outdir]
import sys, os; from playwright.sync_api import sync_playwright
port = sys.argv[1] if len(sys.argv) > 1 else '5188'; out = sys.argv[2] if len(sys.argv) > 2 else '../.audit/wordimg/app'; os.makedirs(out, exist_ok=True)
SEED = """async(ids)=>{const {db}=await import('/src/db.js');const p=(await db.all('profiles'))[0];const now=Date.now();const pr=(await db.get('progress',p.id))||{id:p.id,units:{},wpm:[],sessions:0};pr.units[0]={passed:true,score:3,total:3,at:now,lessons:{rules:now,done:now}};pr.units[1]={lessons:Object.fromEntries(ids.map(i=>[i,now]))};await db.put('progress',pr);}"""
U1 = ['Lalif', 'Lbe', 'Lkaf', 'Llam', 'Lmim', 'Lnun', 'marks', 'join', 'blend']
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    def start(ids):
        pg = b.new_page(viewport={"width": 412, "height": 880}, device_scale_factor=2); pg.on("dialog", lambda d: d.accept()); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        pg.goto(f"http://localhost:{port}/?skiponb"); pg.wait_for_timeout(1500)
        pg.click("text=Just me"); pg.wait_for_timeout(300); pg.click("text=+ Add a learner"); pg.fill("input[placeholder=Name]", "Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
        pg.evaluate(SEED, ids); pg.reload(); pg.wait_for_timeout(2500); return pg
    js = lambda pg, h: pg.evaluate("e=>e.click()", h)
    pg = start(['Lalif']); pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1800); pg.screenshot(path=f"{out}/letter_be.png"); pg.close()
    pg = start(U1[:5]); pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1800); pg.screenshot(path=f"{out}/letter_nun.png"); pg.close()
    pg = start(U1); pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1800); pg.screenshot(path=f"{out}/words_1.png")
    for i in range(2, 6):
        b1 = pg.query_selector(".btn-primary.btn-wide")
        if not b1: break
        js(pg, b1); pg.wait_for_timeout(1200); pg.screenshot(path=f"{out}/words_{i}.png")
    print("errors:", errs); b.close()
