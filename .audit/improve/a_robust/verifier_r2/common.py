import json, os, sys, time, re
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:5361/')
VP = {'width': 390, 'height': 844}
IDB = """
const idb = () => new Promise((res, rej) => { const r = indexedDB.open('urdu-reader'); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
window.__dump = async () => { const d = await idb(); const out = {}; for (const n of d.objectStoreNames) { out[n] = await new Promise(r => { const q = d.transaction(n).objectStore(n).getAll(); q.onsuccess = () => r(q.result); }); } d.close(); return out; };
window.__put = async (s, v) => { const d = await idb(); await new Promise(r => { const t = d.transaction(s, 'readwrite'); t.objectStore(s).put(v); t.oncomplete = r; }); d.close(); };
window.__csp = []; document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));
window.__alerts = 0; window.alert = () => { window.__alerts++; }; window.__xss = 0;
"""
def newpage(b, init=None, sw='block', **kw):
    ctx = b.new_context(viewport=VP, service_workers=sw, accept_downloads=True, **kw); pg = ctx.new_page()
    errs = []; cons = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.on('console', lambda m: cons.append(m.text[:200]) if ('Content Security' in m.text or 'Refused' in m.text) else None)
    pg.on('dialog', lambda d: d.accept('5'))
    pg.add_init_script(IDB)
    if init: pg.add_init_script(init)
    pg._errs = errs; pg._cons = cons; return ctx, pg
def click(pg, sel, t=8000):
    if sel == '.ob-cta': sel = '.ob-cta:not([disabled])'
    pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=t))
def counts(pg): d = pg.evaluate('__dump()'); return {k: len(v) for k, v in d.items()}, d
def csp(pg): return pg.evaluate('window.__csp') + pg._cons
def onboard_child(pg, name='Zara', base=None):
    base = base or BASE
    pg.goto(base); pg.wait_for_timeout(2200)
    s = lambda sel, w=420: (click(pg, sel), pg.wait_for_timeout(w))
    s("text=Let's begin", 500); s('.ob-sleeper', 2800)
    s('.ob-sw >> nth=0'); s('.ob-cta')
    s(".ob-opt:has-text('My child')", 1600); pg.fill('#ob-name', name); pg.wait_for_timeout(200)
    s('.ob-cta'); s('.ob-opt >> nth=1', 1600)
    s('.ob-opt >> nth=0', 1600); s('.ob-opt >> nth=0', 1600)
    pg.wait_for_timeout(400); click(pg, '.ob-opt >> nth=0'); click(pg, '.ob-opt >> nth=3'); pg.wait_for_timeout(400); s('.ob-cta', 1800); s('.ob-cta', 800)
    s('.ob-opt >> nth=1', 1600); pg.wait_for_timeout(3600)
    s('.ob-cta'); s('.ob-cta')
    for t in ['ب', 'ا', 'ب']:
        click(pg, f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(950)
    s('.ob-cta'); s('text=Join them', 1600); s('.ob-cta')
    s('.ob-word', 1500); s('.ob-cta')
    s(".ob-choices .tile:text-is('بابا')", 1400); s('.ob-cta')
    pg.wait_for_timeout(1000); s('.ob-foot .btn-primary', 900); s('.ob-cta')
    s('.ob-opt >> nth=1', 1600); s('.ob-cta', 2000)
def nav(pg, k): pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`).click()", k); pg.wait_for_timeout(700)
def quick_profile(pg, name='Zara', base=None):
    pg.goto((base or BASE) + '?skiponb'); pg.wait_for_timeout(1500)
    click(pg, 'text=Just me'); pg.wait_for_timeout(300)
    click(pg, 'text=+ Add a learner'); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', name)
    click(pg, "button:has-text('Start')"); pg.wait_for_timeout(1500)
def do_rules(pg):
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(700)
    for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
    pg.wait_for_selector('.celebrate', timeout=8000); pg.wait_for_timeout(500)

# ---- verifier helpers
import tempfile
ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']; TEENS = ['ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']; TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
def gate_pass(pg):
    pg.wait_for_selector('.gate-sheet', timeout=4000)
    words = pg.inner_text('.gate-en').strip(); n = None
    for i in range(10, 100):
        w = TEENS[i-10] if i < 20 else TENS[i//10] + ('-' + ONES[i%10] if i % 10 else '')
        if w == words: n = i
    pg.fill('#gate-input', str(n)); pg.evaluate("()=>document.querySelector('.gate-ok').click()"); pg.wait_for_timeout(500)
def settings(pg): return {s['key']: s['value'] for s in pg.evaluate('__dump()')['settings']}
def toast(pg): return pg.evaluate("document.getElementById('toast')?.textContent")
def inert(pg):
    """DOM-level inertness check, independent of CSP: any injected element / on* attribute / script"""
    return pg.evaluate("""()=>{const bad=[];document.querySelectorAll('*').forEach(e=>{for(const a of e.attributes){if(/^on/i.test(a.name)||/javascript:/i.test(a.value)) bad.push(e.tagName+'['+a.name+'='+a.value.slice(0,50)+']')} if(e.tagName==='IMG'&&/(^|\\/)x$/.test(e.getAttribute('src')||'')) bad.push('IMG src=x'); if(e.tagName==='SCRIPT'&&!e.src) bad.push('inline SCRIPT'); if(e.tagName==='SVG'&&e.getAttribute('onload')) bad.push('svg onload'); if(e.id==='pwn'||e.className==='pwn') bad.push('PWN '+e.tagName)});return bad}""")
def sw(pg): return pg.evaluate("[document.documentElement.scrollWidth, innerWidth]")

# ---- r2 helpers: exact-timing tap bursts against whatever is under a point (so a fall-through lands on the new screen / tab bar)
BURST_JS = """([x,y,times])=>new Promise(res=>{const t0=performance.now(); const log=[]; times.forEach(t=>setTimeout(()=>{const e=document.elementFromPoint(x,y); log.push([Math.round(performance.now()-t0), e&&(e.className&&e.className.baseVal===undefined?e.className:'')+':'+(e&&e.tagName)]); e&&e.click&&e.click()}, t)); setTimeout(()=>res(log), Math.max(...times)+30)})"""
def bursts(pg, xy, times=(0,100,200)): return pg.evaluate(BURST_JS, [xy[0], xy[1], list(times)])
def xy_of(pg, sel):
    l = pg.locator(sel).first; l.scroll_into_view_if_needed(); bb = l.bounding_box(); return [bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2]
def burst_sel(pg, sel, times=(0,100,200), t=8000):
    if sel == '.ob-cta': sel = '.ob-cta:not([disabled])'
    pg.wait_for_selector(sel, timeout=t); xy = xy_of(pg, sel); return bursts(pg, xy, times)
