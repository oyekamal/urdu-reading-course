# Validation walker (read-only: does not touch app source). Walks every screen type for one track at one viewport/mode and
# records layout findings, axe-core violations, aria snapshots and screenshots.
# Usage: python3 walk.py --track child|adult --vp 390x844 [--fs 1.3] [--scheme light|dark] [--axe 1] [--motion reduce|no-preference] [--tag name]
import argparse, os, json, glob, sys, traceback
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--track', default='child'); ap.add_argument('--vp', default='390x844'); ap.add_argument('--fs', type=float, default=1.0)
ap.add_argument('--scheme', default='light'); ap.add_argument('--axe', type=int, default=0); ap.add_argument('--aria', type=int, default=0)
ap.add_argument('--motion', default='reduce'); ap.add_argument('--tag', default=''); ap.add_argument('--port', default='5188')
ap.add_argument('--touch', type=int, default=1)
A = ap.parse_args()
W, H = map(int, A.vp.split('x'))
TAG = A.tag or f'{A.track}_{A.vp}_fs{A.fs}_{A.scheme}'
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = f'{ROOT}/runs/{TAG}'; os.makedirs(OUT + '/shots', exist_ok=True)
BASE = f'http://localhost:{A.port}/'
AXE = '/tmp/axe_tmp/node_modules/axe-core/axe.min.js'
EXE = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell'))[0]

LAYOUT_JS = r"""
(o) => {
  const V = [], W = innerWidth, H = innerHeight;
  const R = e => e.getBoundingClientRect();
  const vis = e => { if (!e.isConnected) return false; const r = R(e); if (r.width < 1 || r.height < 1) return false;
    for (let x = e; x && x !== document.documentElement; x = x.parentElement) { const s = getComputedStyle(x); if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false; } return true; };
  const lbl = e => (e.getAttribute('aria-label') || e.innerText || e.value || e.className || e.tagName).toString().replace(/\s+/g, ' ').trim().slice(0, 40);
  const sel = e => { let s = e.tagName.toLowerCase(); if (e.id) s += '#' + e.id; else if (e.className && typeof e.className === 'string') s += '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.'); return s; };
  const inCel = !!document.querySelector('.celebrate');
  const noise = '.fx-burst,.fx-bg,.cel-rays,#toast,.feel-rip,.feel-spark,.confetti,.confetti i,.pg-spark';
  // chrome: fixed bars
  const fixed = [...document.querySelectorAll('body *')].filter(e => getComputedStyle(e).position === 'fixed' && vis(e) && R(e).width > W * .45 && !e.matches(noise) && !e.closest('.celebrate') && getComputedStyle(e).pointerEvents !== 'none');
  let bottomChrome = 0, topChrome = 0;
  for (const f of fixed) { const r = R(f); if (r.height > H * .7) continue; if (r.top > H / 2) bottomChrome = Math.max(bottomChrome, H - r.top); else if (r.bottom < H / 2) topChrome = Math.max(topChrome, r.bottom); }
  const meta = { W, H, scrollH: document.documentElement.scrollHeight, scrollW: document.documentElement.scrollWidth, bottomChrome: Math.round(bottomChrome), topChrome: Math.round(topChrome), freeH: Math.round(H - bottomChrome - topChrome), inCel, h: (document.querySelector('h1,h2')?.innerText || '').slice(0, 40) };
  // 1. page horizontal scroll
  if (document.documentElement.scrollWidth > W + 1) V.push(['hscroll-page', 'document', `${document.documentElement.scrollWidth}px > ${W}`]);
  // 2. elements beyond the viewport horizontally and not inside a clipping/scrolling ancestor
  const clipped = e => { for (let x = e.parentElement; x && x !== document.body; x = x.parentElement) { const s = getComputedStyle(x); if (s.overflowX !== 'visible') return true; } return false; };
  const over = [...document.body.querySelectorAll('*')].filter(e => !e.closest('svg') && !e.matches(noise) && !e.closest(noise) && vis(e)).filter(e => { const r = R(e); return (r.right > W + 1 || r.left < -1) && !clipped(e); });
  over.filter(e => !over.includes(e.parentElement)).slice(0, 5).forEach(e => { const r = R(e); V.push(['h-overflow', lbl(e), `${sel(e)} l${Math.round(r.left)} r${Math.round(r.right)}`]); });
  // 3. clipped text
  const textEls = [...document.querySelectorAll('#app *, .toast, .celebrate *')].filter(e => !e.closest('svg') && vis(e) && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
  for (const e of textEls) { const s = getComputedStyle(e);
    const clips = s.overflowX !== 'visible' || s.overflowY !== 'visible' || s.textOverflow === 'ellipsis' || s.webkitLineClamp !== 'none';
    if (clips && !(s.overflowY === 'auto' || s.overflowY === 'scroll') && (e.scrollWidth > e.clientWidth + 2 || e.scrollHeight > e.clientHeight + 2)) V.push(['text-clipped-self', lbl(e), `${sel(e)} scroll ${e.scrollWidth}x${e.scrollHeight} client ${e.clientWidth}x${e.clientHeight}`]);
    // nearest clipping ancestor
    for (let x = e.parentElement; x && x !== document.body; x = x.parentElement) { const ps = getComputedStyle(x); if ((ps.overflowX === 'hidden' || ps.overflowX === 'clip' || ps.overflowY === 'hidden' || ps.overflowY === 'clip') && !x.matches('.celebrate,#app')) {
      const ar = R(x), er = R(e); const dx = Math.max(ar.left - er.left, er.right - ar.right), dy = Math.max(ar.top - er.top, er.bottom - ar.bottom);
      if ((ps.overflowX !== 'visible' && dx > 3) || (ps.overflowY !== 'visible' && dy > 3)) V.push(['text-clipped-by-ancestor', lbl(e), `${sel(e)} in ${sel(x)} out by ${Math.round(Math.max(dx, dy))}px`]); break; }
      if (ps.overflowY === 'auto' || ps.overflowY === 'scroll') break; } }
  // 4. interactive controls
  const taps = [...document.querySelectorAll('button, a[href], select, input:not([type=hidden]):not([type=file]), textarea, [role=button], [tabindex]:not([tabindex="-1"]), summary, canvas.trace')].filter(vis).filter(e => !e.matches(noise) && !e.closest('svg'));
  // fixed full-screen overlay (celebration, sticker book, ...) hides everything beneath it
  const ov = [...document.querySelectorAll('body > *, #app > *')].filter(e => getComputedStyle(e).position === 'fixed' && vis(e) && R(e).width >= W * .95 && R(e).height >= H * .9 && !e.matches(noise)).pop();
  meta.overlay = ov ? sel(ov) : null;
  const tview = ov ? taps.filter(e => ov.contains(e)) : taps;
  const inNav = e => !!e.closest('.bottom');
  const scrolls = e => { for (let x = e.parentElement; x && x !== document.body; x = x.parentElement) { const s = getComputedStyle(x); if (s.overflowX === 'auto' || s.overflowX === 'scroll') return true; } return false; };
  const limitY = H - (ov ? 0 : bottomChrome) + 2;
  for (const e of tview) { const r = R(e), w = Math.round(r.width), h = Math.round(r.height);
    if (Math.min(w, h) < 44 && !e.matches('input[type=checkbox],input[type=radio]')) V.push(['tap<44', lbl(e), `${sel(e)} ${w}x${h}`]);
    else if (Math.min(w, h) < 48) V.push(['tap44-47', lbl(e), `${sel(e)} ${w}x${h}`]); }
  // 4b. spacing between neighbouring controls (fat finger) and overlapping controls
  const leaf = tview.filter(e => !tview.some(o => o !== e && e.contains(o)) && !inNav(e) && R(e).top >= -1 && R(e).bottom <= limitY && !scrolls(e));
  let gapN = 0, ovN = 0;
  for (let i = 0; i < leaf.length && gapN + ovN < 12; i++) for (let j = i + 1; j < leaf.length; j++) { const a = R(leaf[i]), b = R(leaf[j]);
    const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left), iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    if (ix > 2 && iy > 2) { V.push(['controls-overlap', lbl(leaf[i]) + ' | ' + lbl(leaf[j]), `${Math.round(ix)}x${Math.round(iy)}px overlap`]); ovN++; continue; }
    const gx = -ix, gy = -iy; // gap along an axis when the other axis overlaps
    if ((iy > Math.min(a.height, b.height) * .5 && gx >= 0 && gx < 6) || (ix > Math.min(a.width, b.width) * .5 && gy >= 0 && gy < 6)) { V.push(['gap<6', lbl(leaf[i]) + ' | ' + lbl(leaf[j]), `${Math.round(Math.max(gx, gy))}px apart`]); gapN++; } }
  // 4c. edge proximity (left/right 12px, bottom 16px)
  for (const e of leaf) { const r = R(e); if (r.width > W * .9) continue; if (r.left < 10 || r.right > W - 10) V.push(['edge-lr', lbl(e), `${sel(e)} l${Math.round(r.left)} r${Math.round(W - r.right)}`]); }
  // 5. primary action
  let prims = [...document.querySelectorAll('.btn-primary')].filter(vis); if (inCel) prims = prims.filter(e => e.closest('.celebrate'));
  const info = {};
  if (prims.length) { const p = prims[prims.length - 1]; const r = R(p); info.primary = { label: lbl(p), top: Math.round(r.top), bottom: Math.round(r.bottom), w: Math.round(r.width), h: Math.round(r.height) };
    const cx = Math.min(W - 1, Math.max(1, r.left + r.width / 2)), cy = r.top + r.height / 2;
    if (r.top < 0 || r.bottom > H) V.push(['primary-offscreen', lbl(p), `top ${Math.round(r.top)} bottom ${Math.round(r.bottom)} H ${H}`]);
    else { const t = document.elementFromPoint(cx, cy); if (t && !(p.contains(t) || t.contains(p))) V.push(['primary-covered', lbl(p), `covered by ${sel(t)}`]); } }
  // 6. every control reachable: scroll into view, elementFromPoint at its centre must be itself
  const y0 = scrollY; let obs = 0;
  for (const e of tview.slice(0, 90)) { if (obs > 8) break; if (e.closest('.bottom') || getComputedStyle(e).position === 'fixed') { const r0 = R(e); const t0 = document.elementFromPoint(Math.min(W - 1, Math.max(1, r0.left + r0.width / 2)), Math.min(H - 1, r0.top + r0.height / 2)); if (r0.bottom > H + 1 || r0.top < -1) { V.push(['fixed-control-offscreen', lbl(e), `top ${Math.round(r0.top)} bottom ${Math.round(r0.bottom)}`]); obs++; } continue; }
    e.scrollIntoView({ block: 'center', inline: 'nearest' }); const r = R(e); const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    if (cx < 0 || cx > W || cy < 0 || cy > H) { V.push(['unreachable', lbl(e), `${sel(e)} centre ${Math.round(cx)},${Math.round(cy)} after scrollIntoView`]); obs++; continue; }
    const t = document.elementFromPoint(cx, cy); if (t && !(e.contains(t) || t.contains(e))) { V.push(['obscured', lbl(e), `${sel(e)} covered by ${sel(t)}`]); obs++; } }
  window.scrollTo(0, y0);
  // 7. text sizes
  const small = textEls.filter(e => parseFloat(getComputedStyle(e).fontSize) < 11 && !e.closest('.ur')).map(e => lbl(e) + ' ' + getComputedStyle(e).fontSize);
  if (small.length) V.push(['font<11px', small.slice(0, 3).join(' | '), `${small.length} elements`]);
  // aria-live regions on screen
  info.live = [...document.querySelectorAll('[aria-live],[role=status],[role=alert],[role=log]')].map(e => sel(e) + ' ' + (e.getAttribute('aria-live') || e.getAttribute('role')));
  return { V, meta, info };
}
"""

FS_JS = r"""
(f) => { const els = [...document.querySelectorAll('body, body *')].filter(e => !['SCRIPT', 'STYLE'].includes(e.tagName) && !e.closest('svg'));
  for (const e of els) if (e.dataset.fs0 !== undefined) { e.style.fontSize = e.dataset.fs0; delete e.dataset.fs0; }
  const sizes = els.map(e => parseFloat(getComputedStyle(e).fontSize));
  els.forEach((e, i) => { e.dataset.fs0 = e.style.fontSize || ''; e.style.setProperty('font-size', (sizes[i] * f).toFixed(2) + 'px', 'important'); }); }
"""
# note: restore for fs0 '' removes the property

AXE_JS = r"""
async () => { const r = await axe.run(document, { resultTypes: ['violations', 'incomplete'], runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } });
  const m = v => ({ id: v.id, impact: v.impact, help: v.help, n: v.nodes.length, nodes: v.nodes.slice(0, 4).map(n => ({ t: (n.target || []).join(' '), h: (n.html || '').slice(0, 130), s: (n.any && n.any[0] && n.any[0].message || n.failureSummary || '').slice(0, 170) })) });
  return { v: r.violations.map(m), inc: r.incomplete.map(m) }; }
"""

results = []; n = [0]; notes = []

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE)
        mk = lambda: b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1, reduced_motion=A.motion, color_scheme=A.scheme, has_touch=bool(A.touch), is_mobile=bool(A.touch))
        ctx = mk(); pg = ctx.new_page(); errs = []
        def setup(pg):
            pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept('5'))
            pg.add_init_script("window.__mod=n=>performance.getEntriesByType('resource').map(e=>e.name).find(x=>x.includes('/src/'+n+'.js'))||('/src/'+n+'.js')")
            pg.add_init_script("const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){return _p.call(this).catch(()=>{})}")
        setup(pg)
        cur = {'pg': pg}

        def check(name, expect=False, wait=600):
            pg = cur['pg']; pg.wait_for_timeout(wait); n[0] += 1
            try:
                if A.fs != 1.0: pg.evaluate(FS_JS, A.fs); pg.wait_for_timeout(150)
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(60)
                fn = f'{OUT}/shots/{n[0]:02d}_{name}.jpg'; pg.screenshot(path=fn, type='jpeg', quality=72)
                r = pg.evaluate(LAYOUT_JS, {})
                rec = {'i': n[0], 'screen': name, 'layout': r['V'], 'meta': r['meta'], 'info': r['info']}
                if expect and not r['info'].get('primary'): rec['layout'].append(['no-primary', '-', 'expected a .btn-primary'])
                if A.axe:
                    if not pg.evaluate('typeof axe!=="undefined"'): pg.add_script_tag(path=AXE)
                    rec['axe'] = pg.evaluate(AXE_JS)
                if A.aria:
                    rec['aria'] = pg.locator('body').aria_snapshot()
                    open(f'{OUT}/shots/{n[0]:02d}_{name}.aria.txt', 'w').write(rec['aria'])
                results.append(rec)
            except Exception as ex:
                results.append({'i': n[0], 'screen': name, 'error': str(ex)[:300]}); print('CHECK FAIL', name, str(ex)[:200])

        def click(sel, to=8000):
            pg = cur['pg']; pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=to))
        def safe(label, fn):
            try: fn()
            except Exception as ex:
                notes.append(f'{label}: {str(ex)[:160]}'); print('SEGMENT FAIL', label, str(ex)[:160]); results.append({'i': n[0], 'screen': 'HARNESS_FAIL_' + label, 'error': str(ex)[:300]})
        def close_cel():
            pg = cur['pg']; pg.wait_for_selector('.celebrate', timeout=8000); pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(500)
        def primary():
            pg = cur['pg']
            pg.wait_for_function("()=>[...document.querySelectorAll('.btn-primary')].some(e=>e.offsetParent||getComputedStyle(e).position==='fixed')", timeout=15000)
            pg.evaluate("()=>{const p=[...document.querySelectorAll('.btn-primary')].filter(e=>e.getClientRects().length);p[p.length-1].click()}"); pg.wait_for_timeout(450)
        nav = lambda k: (click(f".bottom button[data-k='{k}']"), cur['pg'].wait_for_timeout(900))
        adult = A.track == 'adult'

        # ---------- onboarding ----------
        def onboarding():
            pg = cur['pg']
            pg.goto(BASE); pg.wait_for_timeout(2200); check('onb_welcome', True)
            click("text=Let's begin"); check('onb_wake')
            click('.ob-sleeper'); pg.wait_for_timeout(2600); check('onb_colour', True)
            click('.ob-sw >> nth=0'); click('.ob-cta'); check('onb_who')
            click(".ob-opt >> nth=0" if adult else ".ob-opt:has-text('My child')"); pg.wait_for_timeout(1500); pg.fill('#ob-name', 'Sam' if adult else 'Zara'); check('onb_name', True)
            click('.ob-cta'); check('onb_goal'); click('.ob-opt >> nth=1'); pg.wait_for_timeout(1500)
            check('onb_speak'); click('.ob-opt >> nth=2' if adult else '.ob-opt >> nth=0'); pg.wait_for_timeout(1500)
            click('.ob-opt >> nth=0'); pg.wait_for_timeout(1500)
            click('.ob-opt >> nth=0'); click('.ob-opt >> nth=3'); check('onb_pains', True); click('.ob-cta')
            check('onb_solution', True, wait=900); click('.ob-cta'); check('onb_minutes')
            click('.ob-opt >> nth=1'); pg.wait_for_timeout(1500); check('onb_processing', wait=500); pg.wait_for_timeout(3000)
            check('onb_demo_alif', True); click('.ob-cta'); check('onb_demo_be', True); click('.ob-cta'); check('onb_demo_tap')
            for t in ['ب', 'ا', 'ب']:
                click(f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(950)
            check('onb_demo_tap_done', True, wait=300); click('.ob-cta'); check('onb_demo_blend', True)
            click('text=Join them'); check('onb_demo_blend_done', True, wait=1500); click('.ob-cta'); check('onb_demo_word')
            click('.ob-word'); check('onb_demo_word_read', True, wait=1400); click('.ob-cta'); check('onb_demo_check')
            click(".ob-choices .tile:text-is('بابا')"); check('onb_demo_check_ok', True, wait=1300); click('.ob-cta')
            check('onb_value', True, wait=1000); click('.ob-foot .btn-primary'); check('onb_streak', True, wait=900); click('.ob-cta')
            check('onb_commit'); click('.ob-opt >> nth=1'); pg.wait_for_timeout(1500); check('onb_plan', True); click('.ob-cta')
        safe('onboarding', onboarding)
        pg = cur['pg']
        pg.wait_for_timeout(2000)
        track = pg.evaluate("document.body.dataset.track")
        notes.append(f'body.dataset.track after onboarding = {track}')
        check('today_first', True)
        pid = pg.evaluate("async()=>{const {db}=await import(window.__mod('db'));return db.setting('activeProfile')}")

        def unit0():
            click("button:has-text('Start:')"); pg.wait_for_timeout(600); check('lesson_rules', True)
            primary(); primary(); primary(); check('celebrate_lesson', True, wait=900)
            click('.cel-go'); pg.wait_for_timeout(600); check('lesson_done_unit', True); primary(); check('celebrate_unit', True, wait=900)
            close_cel(); pg.wait_for_timeout(800)
        safe('unit0', unit0)

        def open_lesson(lid):
            pg.evaluate("""async([pid,lid])=>{const S=await import(window.__mod('session'));const P=await import(window.__mod('path'));const {db}=await import(window.__mod('db'));const {C}=await import(window.__mod('content'));
              const u=C.units[1];const ls=P.lessonsFor(u);const p=await S.getProgress(pid);const done={};for(const l of ls){if(l.id===lid)break;done[l.id]=Date.now()}p.units[1]={...(p.units[1]||{}),lessons:done};await db.put('progress',p)}""", [pid, lid])
            nav('read'); nav('today'); click("button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(700)

        def brute_tiles(maxclicks=80):
            for k in range(maxclicks):
                if pg.query_selector('.lesson .btn-primary.btn-wide'): return True
                if pg.query_selector("button:has-text('Next word')") and pg.evaluate("()=>{const t=[...document.querySelectorAll('.choices .tile')];return t.length&&t.every(x=>x.disabled)}"):
                    click("button:has-text('Next word')"); continue
                ts = pg.query_selector_all('.choices .tile:not([disabled]):not(.no):not(.ok)')
                if not ts: pg.wait_for_timeout(300); continue
                pg.evaluate('e=>e.click()', ts[k % len(ts)]); pg.wait_for_timeout(260)
            return False

        def letter():
            open_lesson('Lbe'); check('L_intro', True)
            primary(); check('L_tellapart_start')
            click('.choices .tile'); pg.wait_for_timeout(300); check('L_tellapart_round'); brute_tiles(); check('L_tellapart_done', True)
            primary(); check('L_forms', True); primary(); check('L_trace', True)
            primary()
            if pg.query_selector("h2:has-text('Blend it')"): check('L_blend', True); primary()
            check('L_check')
            for _ in range(4):
                pg.evaluate("""async()=>{const {C,forms}=await import(window.__mod('content'));const L=C.by['ب'];const ch=document.querySelector('.choices');if(!ch)return;const q=ch.previousElementSibling.textContent;const m=q.match(/at the (\\w+) position/);const g=m?forms(L).find(f=>f[0]===m[1])[1]:L.ch;const t=[...ch.querySelectorAll('.tile')].find(x=>x.textContent===g)||ch.querySelector('.tile');t&&t.click()}""")
                pg.wait_for_timeout(650)
            check('L_check_done', True); primary(); pg.wait_for_timeout(800); check('celebrate_letter', True, wait=300); close_cel(); pg.wait_for_timeout(600)
        safe('letter', letter)
        def marks():
            open_lesson('marks'); check('marks_intro', True); primary(); check('marks_find'); brute_tiles(); primary(); pg.wait_for_timeout(700); close_cel()
        safe('marks', marks)
        def join():
            open_lesson('join'); check('join_forms', True); primary(); check('join_build'); brute_tiles(); check('join_build_done', True); primary(); pg.wait_for_timeout(700); close_cel()
        safe('join', join)
        def blend():
            open_lesson('blend'); check('blend'); brute_tiles(); check('blend_done', True); primary(); pg.wait_for_timeout(700); close_cel()
        safe('blend', blend)
        def words():
            open_lesson('W1'); check('words_read', True); primary(); check('words_build'); brute_tiles(); primary(); check('words_dictation')
            for _ in range(6):
                s = pg.query_selector("button:has-text('Skip'):not([disabled])")
                if not s: break
                pg.evaluate('e=>e.click()', s); pg.wait_for_timeout(1000)
            check('words_dictation_done', True); primary(); pg.wait_for_timeout(700); close_cel()
        safe('words', words)
        def quiz():
            open_lesson('quiz'); check('quiz', True)
            pg.evaluate("()=>document.querySelectorAll('ol li').forEach(li=>{const r=li.querySelector('b').textContent;const t=[...li.querySelectorAll('.tile')].find(x=>x.getAttribute('aria-label')===r);t&&t.click()})")
            pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Submit').click()"); pg.wait_for_timeout(900); check('quiz_done', True)
            primary(); pg.wait_for_timeout(800); close_cel(); pg.wait_for_timeout(800)
        safe('quiz', quiz)

        # ---------- tabs ----------
        def tabs():
            check('today_unit2', True)
            pg.evaluate("async(pid)=>{const {db}=await import(window.__mod('db'));for(const c of await db.by('cards','profileId',pid))await db.put('cards',{...c,due:Date.now()+9e9})}", pid)
            nav('review'); check('review_empty', True)
            pg.evaluate("async(pid)=>{const {db}=await import(window.__mod('db'));for(const c of await db.by('cards','profileId',pid))await db.put('cards',{...c,due:0})}", pid)
            nav('read'); nav('review'); check('review_due', True); click("button:has-text('Not yet')"); pg.wait_for_timeout(300); check('review_due_reveal', True, wait=200)
            nav('read'); check('read_tab')
        safe('tabs', tabs)
        def me():
            if adult:
                for k in ['units', 'progress', 'more']: nav(k); check('adult_' + k)
            else:
                nav('me'); check('me_tab')
            def book():
                pg.evaluate("window.__stickers && window.__stickers.openBook()"); pg.wait_for_selector('.stk-book', timeout=5000); check('sticker_book', wait=900)
                pg.evaluate("document.querySelector('.stk-back').click()"); pg.wait_for_timeout(400)
            safe('sticker', book)
            nav('today')
            if not adult:
                click('.all-units'); pg.wait_for_timeout(900); check('units_tab')
        safe('me', me)
        # tracing: adult has it in unit detail ("Write it"); child already covered in L_trace
        def adult_trace():
            nav('units'); pg.wait_for_timeout(600)
            for sel in ['.unit button', '.ucard', '.unit']:
                el = pg.query_selector(sel)
                if el: pg.evaluate('e=>e.click()', el); break
            pg.wait_for_timeout(900); check('adult_unit_detail')
            cv = pg.query_selector('canvas.trace')
            if cv: cv.scroll_into_view_if_needed(); check('adult_tracing')
        if adult: safe('adult_trace', adult_trace)

        # ---------- mode picker ----------
        def mode():
            c2 = mk(); cur['pg'] = c2.new_page(); setup(cur['pg']); q = cur['pg']
            q.goto(BASE + '?skiponb'); q.wait_for_timeout(1800); check('mode_picker', True)
            click('text=Just me'); q.wait_for_timeout(500); check('profile_picker')
            click('text=+ Add a learner'); q.wait_for_timeout(400); check('add_learner_form')
        safe('mode', mode)
        b.close()
        json.dump({'tag': TAG, 'args': vars(A), 'notes': notes, 'errors': errs[:10], 'results': results}, open(f'{OUT}/results.json', 'w'), ensure_ascii=False, indent=1)
        print('DONE', TAG, len(results), 'screens', 'notes:', len(notes))

main()
