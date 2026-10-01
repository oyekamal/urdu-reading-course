# Feel sequences: open a unit-1 letter lesson (tap-the-sound drill), tap a correct tile (2nd in a row, so the combo chip shows)
# and a wrong tile, and record screenshot SEQUENCES at ~0/80/160/320/640/1000 ms after the tap into
# /tmp/claude-1000/feel9a/{correct,wrong}/ plus contact.png for each. Motion is ON (no reduced-motion), 390x844 @2x by default.
# Usage: python3 tools/feel_seq.py [port] [outdir] [WxH]      (dev server: npx vite --port 5188)
import sys, os, time, json
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

PORT = sys.argv[1] if len(sys.argv) > 1 else '5188'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-1000/feel9a'
W, H = map(int, (sys.argv[3] if len(sys.argv) > 3 else '390x844').split('x'))
TARGETS = [0, 80, 160, 320, 640, 1000]
BASE = f'http://localhost:{PORT}/'
for k in ('correct', 'wrong'): os.makedirs(f'{OUT}/{k}', exist_ok=True)

def sheet(kind, frames):
    ims = []
    for t in TARGETS:
        ms, fn = min(frames, key=lambda f: abs(f[0] - t))
        ims.append((t, ms, Image.open(fn)))
    cw = 420; sc = cw / ims[0][2].width; crop_h = int(ims[0][2].height * 0.50); ch = int(crop_h * sc) + 24
    out = Image.new('RGB', (cw * 3, ch * 2), 'white'); d = ImageDraw.Draw(out)
    for i, (t, ms, im) in enumerate(ims):
        x, y = (i % 3) * cw, (i // 3) * ch
        out.paste(im.crop((0, 0, im.width, crop_h)).resize((cw, int(crop_h * sc))), (x, y + 24)); d.text((x + 6, y + 6), f'+{t}ms (frame @{ms}ms)', fill='black')
    out.save(f'{OUT}/{kind}/contact.png'); print('contact sheet', f'{OUT}/{kind}/contact.png')

with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept('5'))
    pg.add_init_script("window.__mod=n=>performance.getEntriesByType('resource').map(e=>e.name).find(x=>x.includes('/src/'+n+'.js'))||('/src/'+n+'.js')")
    pg.add_init_script("const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){if(!String(this.src).includes('/ui/'))window.__last=this.src;return _p.call(this).catch(()=>{})}")
    click = lambda sel: pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=8000))
    pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1800); click('text=Just me'); pg.wait_for_timeout(300)
    click('text=+ Add a learner'); pg.wait_for_timeout(300); pg.fill('input[placeholder=Name]', 'Zee'); click("button:has-text('Start')"); pg.wait_for_timeout(1800)
    pid = pg.evaluate("async()=>{const {db}=await import(window.__mod('db'));return db.setting('activeProfile')}")
    pg.evaluate("""async(pid)=>{const S=await import(window.__mod('session'));const P=await import(window.__mod('path'));const {db}=await import(window.__mod('db'));const {C}=await import(window.__mod('content'));
      await S.markUnit(pid,0,10,10);await S.ensureCards(pid,1);const u=C.units[1];const ls=P.lessonsFor(u);const p=await S.getProgress(pid);const done={};for(const l of ls){if(l.id==='Lbe')break;done[l.id]=Date.now()}p.units[1]={...(p.units[1]||{}),lessons:done};await db.put('progress',p)}""", pid)
    for k in ('read', 'today'): pg.evaluate('e=>e.click()', pg.wait_for_selector(f".bottom button[data-k='{k}']")); pg.wait_for_timeout(900)
    click("button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(1000)
    pg.evaluate("()=>{const p=[...document.querySelectorAll('.btn-primary')].filter(e=>e.getClientRects().length);p[p.length-1].click()}"); pg.wait_for_timeout(1500)  # -> tap-the-sound drill
    pg.screenshot(path=f'{OUT}/lesson_start.png')

    def pick(right):
        return pg.evaluate("""async(right)=>{const {C}=await import(window.__mod('content'));const key=(window.__last||'').split('/audio/')[1]||'';const id=key.replace('names/','').replace('.mp3','');
          const ts=[...document.querySelectorAll('.choices .tile:not(.no):not(.ok)')];const good=ts.find(t=>C.by[t.textContent.trim()]&&C.by[t.textContent.trim()].id===id);
          const t=right?good:ts.find(x=>x!==good);if(!t)return null;const r=t.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}""", right)

    import base64
    cdp = ctx.new_cdp_session(pg); got = []
    def on_frame(f):
        got.append((f['metadata']['timestamp'], f['data'])); cdp.send('Page.screencastFrameAck', {'sessionId': f['sessionId']})
    cdp.on('Page.screencastFrame', on_frame)

    def capture(kind, right):
        pos = pick(right)
        if not pos: print('no tile for', kind); return
        for f in os.listdir(f'{OUT}/{kind}'):
            if f.endswith('.png'): os.remove(f'{OUT}/{kind}/{f}')
        pg.mouse.move(*pos); pg.wait_for_timeout(250); got.clear()
        cdp.send('Page.startScreencast', {'format': 'png', 'maxWidth': W * 2, 'maxHeight': H * 2, 'everyNthFrame': 1})
        pg.wait_for_timeout(120)
        t0 = time.time(); pg.mouse.down(); pg.mouse.up(); pg.wait_for_timeout(1250)
        cdp.send('Page.stopScreencast'); pg.wait_for_timeout(100)
        frames = []
        for ts, data in got:
            ms = int((ts - t0) * 1000)
            if -150 <= ms <= 1150:
                fn = f'{OUT}/{kind}/f_{ms + 150:04d}.png'; open(fn, 'wb').write(base64.b64decode(data)); frames.append((ms, fn))
        if not frames: print('no frames', kind, len(got)); return
        keep = {t: min(frames, key=lambda f: abs(f[0] - t)) for t in TARGETS}
        for fr in frames:
            if fr not in keep.values(): os.remove(fr[1])
        sheet(kind, list(keep.values()))
        print(kind, 'frames', len(frames), 'picked', [f[0] for f in keep.values()])

    click('.choices .tile'); pg.wait_for_timeout(700)   # the first tap only starts round 1
    pg.mouse.click(*pick(True)); pg.wait_for_timeout(1400)   # warm-up correct, so the captured one is "2 in a row"
    capture('correct', True); pg.wait_for_timeout(1500)
    capture('wrong', False); pg.wait_for_timeout(300)
    pg.screenshot(path=f'{OUT}/after.png')
    if errs: print('page errors:', errs[:5])
    b.close()
