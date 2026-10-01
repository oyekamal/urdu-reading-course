# Round 9c premium captures at 390x844 @2x -> /tmp/claude-1000/premium9c/ (+ contact sheets).
# Usage: python3 tools/premium_seq.py [port] [outdir]
# Sets: trace (in progress + finished + shimmer), home by day / evening, sticker book 0 / 3 earned, new-sticker reveal at 0/100/250/500/1000 ms.
# Animations are paused and seeked with the Web Animations API so frame times are exact, not screenshot-timing luck.
import sys, math, os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
port = sys.argv[1] if len(sys.argv) > 1 else '5188'; out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-1000/premium9c'; os.makedirs(out, exist_ok=True)
SEED = """async(ids)=>{const {db}=await import('/src/db.js');const p=(await db.all('profiles'))[0];const now=Date.now();const pr=(await db.get('progress',p.id))||{id:p.id,units:{},wpm:[],sessions:0};pr.units[0]={passed:true,score:3,total:3,at:now,lessons:{rules:now,done:now}};pr.units[1]={lessons:Object.fromEntries(ids.map(i=>[i,now]))};await db.put('progress',pr);}"""
MASTER = """async(n)=>{const {db}=await import('/src/db.js');const p=(await db.all('profiles'))[0];const L=['ا','ب','ک','ل','م','ن'];for(const c of await db.by('cards','profileId',p.id)) await db.del('cards',c.id);await db.setting('stickersSeen:'+p.id,null);for(let i=0;i<n;i++)await db.put('cards',{id:p.id+':'+L[i],profileId:p.id,item:L[i],kind:'letter',box:5,due:Date.now()+9e8,seen:6,last:Date.now()-(9-i)*1000});}"""
CLOCK = "(h)=>{Date.prototype.getHours=function(){return h}}"
SEEK = """(t)=>{document.getAnimations().forEach(a=>{const n=a.animationName||'';a.pause();const fl=/^stk(Flip|Sp)/.test(n);let d=0;try{d=a.effect.getTiming().delay||0}catch(e){}a.currentTime=fl?t+d:t+420;})}"""

def sheet(paths, name, cols=None, label=None):
    ims = [Image.open(p).convert('RGB') for p in paths]; w = 300; ims = [i.resize((w, int(i.height * w / i.width))) for i in ims]
    cols = cols or len(ims); rows = math.ceil(len(ims) / cols); h = max(i.height for i in ims)
    S = Image.new('RGB', (cols * (w + 8) + 8, rows * (h + 26) + 8), '#222')
    d = ImageDraw.Draw(S)
    for k, (im, p) in enumerate(zip(ims, paths)):
        x = 8 + (k % cols) * (w + 8); y = 8 + (k // cols) * (h + 26); S.paste(im, (x, y + 18)); d.text((x + 2, y + 2), (label[k] if label else os.path.basename(p)), fill='#ddd')
    S.save(f"{out}/{name}"); print('sheet', f"{out}/{name}")

with sync_playwright() as p:
    b = p.chromium.launch()
    def start(hour=None):
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2); pg.on("dialog", lambda d: d.accept())
        pg.on("pageerror", lambda e: print("PAGEERR", e))
        if hour is not None: pg.add_init_script(f"Date.prototype.getHours=function(){{return {hour}}}")
        pg.goto(f"http://localhost:{port}/?skiponb"); pg.wait_for_timeout(1500)
        pg.click("text=Just me"); pg.wait_for_timeout(300); pg.click("text=+ Add a learner"); pg.fill("input[placeholder=Name]", "Zara"); pg.click("button:has-text('Start')"); pg.wait_for_timeout(1500)
        pg.evaluate(SEED, []); pg.reload(); pg.wait_for_timeout(2500); return pg
    # ---- 1. glowing ink
    pg = start(); pg.click(".btn-primary.btn-wide"); pg.wait_for_timeout(1300)
    for _ in range(12):
        if pg.query_selector("canvas.trace"): break
        pr = pg.query_selector(".btn-primary.btn-wide")
        if not pr: break
        pg.evaluate("e=>e.click()", pr); pg.wait_for_timeout(900)
    cv = pg.query_selector("canvas.trace"); cv.scroll_into_view_if_needed(); bb = cv.bounding_box(); pg.wait_for_timeout(300)
    clip = {"x": 0, "y": max(0, bb['y'] - 20), "width": 390, "height": bb['height'] + 150}
    P = []
    def shot(n): f = f"{out}/trace_{n}.png"; pg.screenshot(path=f, clip=clip); P.append(f)
    gb = pg.evaluate("()=>{const c=document.querySelector('canvas.trace'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let a=c.width,b=0,t=c.height,u=0;for(let i=3;i<d.length;i+=4)if(d[i]>0&&d[i-3]>150){const x=(i>>2)%c.width,y=(i>>2)/c.width|0;if(x<a)a=x;if(x>b)b=x;if(y<t)t=y;if(y>u)u=y}return[a,b,t,u]}")
    sx = lambda gx: bb['x'] + bb['width'] * gx / 360; sy = lambda gy: bb['y'] + bb['height'] * gy / 300
    cx = (gb[0] + gb[1]) / 2; y0, y1 = gb[2] + 6, gb[3] - 6
    pg.mouse.move(sx(cx + 3), sy(y0)); pg.mouse.down()
    for k in range(34):
        pg.mouse.move(sx(cx + 3 - 3 * k / 33 + 1.5 * math.sin(k / 5)), sy(y0 + (y1 - y0) * k / 33)); pg.wait_for_timeout(14)
        if k == 14: shot('1_inprogress')
    shot('2_fingerdown'); pg.mouse.up(); pg.wait_for_timeout(90); shot('3_pop'); pg.wait_for_timeout(700); shot('4_done')
    pg.click("button:has-text('Check')"); pg.wait_for_timeout(260); shot('5_shimmer_a'); pg.wait_for_timeout(260); shot('6_shimmer_b'); pg.wait_for_timeout(900); shot('7_settled')
    sheet(P, 'sheet_trace.png', cols=4); pg.close()
    # ---- 2. home by day and evening
    H = []
    for name, hr in (('day', 10), ('evening', 20)):
        pg = start(hr); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(900)
        for k, (dx, dy) in enumerate(((0, 0),)):
            f = f"{out}/home_{name}.png"; pg.screenshot(path=f); H.append(f)
        # tilt: simulate pointer drift to show parallax shift
        pg.mouse.move(40, 300); pg.wait_for_timeout(700); f = f"{out}/home_{name}_tilt_left.png"; pg.screenshot(path=f); H.append(f)
        pg.mouse.move(350, 300); pg.wait_for_timeout(700); f = f"{out}/home_{name}_tilt_right.png"; pg.screenshot(path=f); H.append(f); pg.close()
    sheet(H, 'sheet_home.png', cols=3)
    # ---- 3. sticker book 0 / 3 earned
    B = []
    for n in (0, 3):
        pg = start(); pg.evaluate(MASTER, n); pg.evaluate("()=>{}"); pg.reload(); pg.wait_for_timeout(1800)
        # Me tab -> button -> book. (With n>0 the reveal queue may show first: dismiss it, we shoot the book separately.)
        for _ in range(4):
            if pg.query_selector(".stk-cta"): pg.click(".stk-cta"); pg.wait_for_timeout(500)
        pg.click(".bottom button[data-k=me]"); pg.wait_for_timeout(700); f = f"{out}/me_entry_{n}.png"; pg.screenshot(path=f); B.append(f)
        pg.click(".stk-entry"); pg.wait_for_timeout(1300); f = f"{out}/book_{n}.png"; pg.screenshot(path=f); B.append(f); pg.close()
    sheet(B, 'sheet_book.png', cols=4)
    # ---- 4. reveal frames
    pg = start(); pg.evaluate(MASTER, 6); pg.evaluate("()=>{const p=0}"); pg.evaluate("async()=>{const {db}=await import('/src/db.js');const p=(await db.all('profiles'))[0];await db.setting('stickersSeen:'+p.id,['ا','ب','ک','ل','م'])}"); pg.reload(); pg.wait_for_selector(".stk-flip.go", timeout=8000)
    R = []
    for t in (0, 100, 250, 500, 1000):
        pg.evaluate(SEEK, t); pg.wait_for_timeout(60); f = f"{out}/reveal_{t:04d}.png"; pg.screenshot(path=f); R.append(f)
    sheet(R, 'sheet_reveal.png', cols=5, label=[f"+{t} ms" for t in (0, 100, 250, 500, 1000)]); b.close()
