# Screenshot the main screens at phone width for the design gauntlet. Usage: python3 tools/shots.py [port] [outdir]
import sys; from playwright.sync_api import sync_playwright
port=sys.argv[1] if len(sys.argv)>1 else '5199'; out=sys.argv[2] if len(sys.argv)>2 else '../.audit/ui'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}, device_scale_factor=2); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)[:300])); pg.on("dialog", lambda d: d.accept())
    pg.goto(f"http://localhost:{port}/"); pg.wait_for_timeout(2000); pg.screenshot(path=f"{out}/01_mode.png")
    pg.click("text=Just me"); pg.wait_for_timeout(400); pg.click("text=+ Add a learner"); pg.wait_for_timeout(300); pg.screenshot(path=f"{out}/02_add.png")
    pg.fill("input[placeholder=Name]","Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1800); pg.screenshot(path=f"{out}/03_path.png", full_page=True)
    pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1200); pg.screenshot(path=f"{out}/04_lesson_rules.png")
    pg.click("button:has-text('Continue')"); pg.wait_for_timeout(500); pg.click("button:has-text('Continue')"); pg.wait_for_timeout(500); pg.click("button:has-text('Continue')"); pg.wait_for_timeout(900); pg.screenshot(path=f"{out}/05_lesson_done.png")
    pg.click("button:has-text('Next')"); pg.wait_for_timeout(600); pg.click("button:has-text('Unlock')"); pg.wait_for_timeout(900); pg.click("button:has-text('Back to path')"); pg.wait_for_timeout(1200); pg.screenshot(path=f"{out}/06_path_u1.png", full_page=True)
    pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1500); pg.screenshot(path=f"{out}/07_letter.png", full_page=True)
    for tab,n in [("Units","08_units"),("Review","09_review"),("Read","10_read"),("Progress","11_progress"),("More","12_more")]:
        pg.click(f".bottom button:has-text('{tab}')"); pg.wait_for_timeout(900); pg.screenshot(path=f"{out}/{n}.png", full_page=(tab!='Units'))
    print("errors:", errs); b.close()
