# Round 10b captures -> /tmp/claude-1000/premium10b/: tracing (lesson + unit-page variants), sticker book 0 / 3 earned, Today.
# Usage: python3 tools/finish_seq.py [port] [outdir]
import sys, os, math
from playwright.sync_api import sync_playwright
port = sys.argv[1] if len(sys.argv) > 1 else '5188'; out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-1000/premium10b'; os.makedirs(out, exist_ok=True)
src = open(os.path.join(os.path.dirname(__file__), 'premium_seq.py')).read()
SEED = src.split('SEED = """')[1].split('"""')[0]; MASTER = src.split('MASTER = """')[1].split('"""')[0]
with sync_playwright() as p:
    b = p.chromium.launch()
    def start(hour=None):
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2); pg.on("dialog", lambda d: d.accept()); pg.on("pageerror", lambda e: print("PAGEERR", e))
        if hour is not None: pg.add_init_script(f"Date.prototype.getHours=function(){{return {hour}}}")
        pg.goto(f"http://localhost:{port}/?skiponb"); pg.wait_for_timeout(1500)
        pg.click("text=Just me"); pg.wait_for_timeout(300); pg.click("text=+ Add a learner"); pg.fill("input[placeholder=Name]", "Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
        pg.evaluate(SEED, []); pg.reload(); pg.wait_for_timeout(2500); return pg
    # Today
    pg = start(10); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(900); pg.screenshot(path=f"{out}/today.png")
    pg.screenshot(path=f"{out}/today_pressed.png") if False else None
    # lesson tracing
    pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1300)
    for _ in range(12):
        if pg.query_selector("canvas.trace"): break
        pr = pg.query_selector(".btn-primary.btn-wide")
        if not pr: break
        pg.evaluate("e=>e.click()", pr); pg.wait_for_timeout(900)
    pg.wait_for_timeout(500); pg.screenshot(path=f"{out}/trace_lesson.png")
    cv = pg.query_selector("canvas.trace"); bb = cv.bounding_box()
    pg.mouse.move(bb['x'] + bb['width'] * .6, bb['y'] + 60); pg.mouse.down()
    for k in range(25): pg.mouse.move(bb['x'] + bb['width'] * (.6 - .004 * k), bb['y'] + 60 + 6 * k); pg.wait_for_timeout(12)
    pg.mouse.up(); pg.wait_for_timeout(300); pg.click("button.btn-check"); pg.wait_for_timeout(500); pg.screenshot(path=f"{out}/trace_lesson_checked.png")
    # unit-page variant (multi-letter, pickers) mounted into the live app so real CSS applies
    pg.evaluate("""async()=>{const D=await import('/src/drills.js'),{C}=await import('/src/content.js');document.querySelector('#app').innerHTML='';const u=C.units[1];document.querySelector('#app').append(D.writeIt(u,{record(){}},()=>'naskh',()=>{}))}""")
    pg.wait_for_timeout(700); pg.screenshot(path=f"{out}/trace_unitpage.png")
    pg.click(".trace-letters .tchip:nth-child(3)"); pg.click(".trace-pos .tchip:nth-child(2)"); pg.wait_for_timeout(500); pg.screenshot(path=f"{out}/trace_unitpage_sel.png")
    pg.click(".trace-letters .tchip:nth-child(1)"); pg.click(".trace-pos .tchip:nth-child(3)"); pg.wait_for_timeout(500); pg.screenshot(path=f"{out}/trace_unitpage_nonjoiner.png"); pg.close()
    for n in (0, 3):
        pg = start(); pg.evaluate(MASTER, n); pg.reload(); pg.wait_for_timeout(1800)
        for _ in range(4):
            if pg.query_selector(".stk-cta"): pg.click(".stk-cta"); pg.wait_for_timeout(500)
        pg.click(".bottom button[data-k=me]"); pg.wait_for_timeout(700); pg.click(".stk-entry"); pg.wait_for_timeout(1500); pg.screenshot(path=f"{out}/book_{n}.png")
        if n == 3:
            pg.click(".stk-tab:nth-child(2)"); pg.wait_for_timeout(700); pg.screenshot(path=f"{out}/book_{n}_unit2.png")
            pg.mouse.move(360, 500); pg.wait_for_timeout(500); pg.click(".stk-tab:nth-child(1)"); pg.wait_for_timeout(900); pg.screenshot(path=f"{out}/book_{n}_tilt.png")
        pg.close()
    b.close()
