# Walk the first-run onboarding on a fresh profile and screenshot every screen. Usage: python3 tools/onb_shots.py [port] [outdir] [who]
import sys, os; from playwright.sync_api import sync_playwright
port = sys.argv[1] if len(sys.argv) > 1 else '5188'; out = sys.argv[2] if len(sys.argv) > 2 else '../.audit/onboarding/ours'; who = sys.argv[3] if len(sys.argv) > 3 else 'My child'
os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:300])); pg.on("console", lambda m: m.type == "error" and errs.append(m.text[:300]))
    n = [0]
    def shot(name, wait=700):
        pg.wait_for_timeout(wait); n[0] += 1; pg.screenshot(path=f"{out}/{n[0]:02d}_{name}.png")
    pg.goto(f"http://localhost:{port}/"); shot("welcome", 2200)
    pg.click("text=Let's begin"); shot("wake"); pg.click(".ob-sleeper"); shot("woke", 900); pg.wait_for_timeout(1800); shot("colour", 300); pg.click(".ob-sw >> nth=0"); shot("colour_picked", 500); pg.click(".ob-cta"); shot("who")
    pg.click(f".ob-opt:has-text('{who}')"); shot("who_reply", 500); pg.wait_for_timeout(1000); shot("name")
    pg.fill("#ob-name", "Zara"); shot("name_typed", 300); pg.click(".ob-cta"); shot("goal")
    pg.click(".ob-opt >> nth=1"); shot("goal_reply", 500); pg.wait_for_timeout(1000); shot("speak")
    pg.click(".ob-opt >> nth=0"); pg.wait_for_timeout(1400); shot("reads")
    pg.click(".ob-opt >> nth=0"); pg.wait_for_timeout(1400); shot("pains")
    pg.click(".ob-opt >> nth=0"); pg.click(".ob-opt >> nth=3"); pg.click(".ob-opt >> nth=4"); shot("pains_picked", 300); pg.click(".ob-cta"); shot("solution", 900)
    pg.click(".ob-cta"); shot("minutes")
    pg.click(".ob-opt >> nth=1"); pg.wait_for_timeout(1400); shot("processing", 1600)
    pg.wait_for_timeout(2400); shot("demo_alif", 400)
    pg.click(".ob-cta"); shot("demo_be")
    pg.click(".ob-cta"); shot("demo_tap")
    for t in ['ب', 'ا', 'ب']:
        pg.click(f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(900)
    shot("demo_tap_done", 200)
    pg.click(".ob-cta"); shot("demo_blend")
    pg.click("text=Join them"); shot("demo_blend_done", 1500)
    pg.click(".ob-cta"); shot("demo_word")
    pg.click(".ob-word"); shot("demo_word_read", 1300)
    pg.click(".ob-cta"); shot("demo_check")
    pg.click(".ob-choices .tile:text-is('بابا')"); shot("demo_check_ok", 1200)
    pg.click(".ob-cta"); shot("value", 1000)
    pg.click(".ob-foot .btn-primary"); shot("streak", 1000)
    pg.click(".ob-cta"); shot("commit")
    pg.click(".ob-opt >> nth=1"); shot("commit_reply", 500); pg.wait_for_timeout(1000); shot("plan")
    pg.click(".ob-cta"); shot("path", 2000)
    print("errors:", errs); b.close()
