# UI audit: visit every screen type at 390x844, screenshot it, and check tap targets, horizontal overflow, the docked
# primary action, content hidden under fixed bars, and button text contrast. Prints a violations table.
# Usage: python3 tools/ui_audit.py [port] [outdir]     (dev server: npx vite --port 5188)
import sys, os, json, re
from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('PORT', '5188')
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-1000/qa'
os.makedirs(OUT, exist_ok=True)
BASE = f'http://localhost:{PORT}/'

AUDIT_JS = r"""
(opts) => {
  const V = [], W = innerWidth, H = innerHeight;
  const vis = e => { if (!e.isConnected) return false; const r = e.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false;
    for (let x = e; x && x !== document.documentElement; x = x.parentElement) { const s = getComputedStyle(x); if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false; } return true; };
  const label = e => (e.getAttribute('aria-label') || e.innerText || e.value || e.className || e.tagName).replace(/\s+/g, ' ').trim().slice(0, 34);
  const child = document.body.dataset.track === 'child';
  // fixed overlays: bottom nav, onboarding foot, docks
  const nav = [...document.querySelectorAll('.bottom')].find(vis);
  const navTop = nav ? nav.getBoundingClientRect().top : H;
  const inCel = !!document.querySelector('.celebrate');
  const limit = inCel ? H : navTop;
  // 1. tap targets
  const taps = [...document.querySelectorAll('button, a[href], select, input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=file]), [role=button], summary, label:has(> input[type=checkbox])')].filter(vis);
  const isAudio = e => !e.matches('.ob-opt, .pearl, .ucard') && (e.matches('.btn-play') || !!e.querySelector('path[d^="M4 10v4h3"]') || /^(▶|play again|play sound|play word|hear it|say it again)/i.test((e.innerText || '').trim()));
  for (const e of taps) { if (inCel && !e.closest('.celebrate')) continue; const r = e.getBoundingClientRect(); const w = Math.round(r.width), h = Math.round(r.height);
    if (Math.min(w, h) < 44) V.push(['tap<44', label(e), `${w}x${h}`]);
    else if (child && e.matches('.choices .tile, .keys .tile, .ob-choices .tile') && Math.min(w, h) < 64) V.push(['child-tile<64', label(e), `${w}x${h}`]);
    if (child && isAudio(e) && Math.min(w, h) < 56) V.push(['child-audio<56', label(e), `${w}x${h}`]);
    if (isAudio(e) && !e.matches('.btn-play') && !e.closest('.bottom')) V.push(['audio-style', label(e), 'not the round speaker button']);
  }
  // 2. horizontal overflow
  if (document.documentElement.scrollWidth > W + 1) V.push(['page-hscroll', 'document', `${document.documentElement.scrollWidth}px wide`]);
  const clipped = e => { for (let x = e.parentElement; x && x !== document.body; x = x.parentElement) { const s = getComputedStyle(x); if (s.overflowX !== 'visible') return true; } return false; };
  const over = [...document.body.querySelectorAll('*')].filter(e => !e.closest('svg') && !e.matches('.fx-burst,.fx-bg,.cel-rays,#toast') && vis(e)).filter(e => { const r = e.getBoundingClientRect(); return (r.right > W + 1 || r.left < -1) && !clipped(e); });
  over.filter(e => !over.includes(e.parentElement)).slice(0, 6).forEach(e => { const r = e.getBoundingClientRect(); V.push(['h-overflow', label(e), `l${Math.round(r.left)} r${Math.round(r.right)}`]); });
  // 3. primary action: exactly one, visible without scrolling, docked at the bottom above the nav
  let prims = [...document.querySelectorAll('.btn-primary')].filter(vis); if (inCel) prims = prims.filter(e => e.closest('.celebrate'));
  const primInfo = prims.map(e => { const r = e.getBoundingClientRect(); return { label: label(e), top: Math.round(r.top), bottom: Math.round(r.bottom), w: Math.round(r.width), h: Math.round(r.height) }; });
  if (prims.length > 1) V.push(['multi-primary', prims.map(label).join(' | ').slice(0, 60), `${prims.length} primaries`]);
  if (!prims.length && opts.expectPrimary) V.push(['no-primary', '-', 'screen has no .btn-primary']);
  if (prims.length) { const p = prims[prims.length - 1]; const r = p.getBoundingClientRect();
    if (r.top < 0 || r.bottom > limit + 1) V.push(['primary-offscreen', label(p), `top ${Math.round(r.top)} bottom ${Math.round(r.bottom)} limit ${Math.round(limit)}`]);
    else if (!opts.inlinePrimaryOk && limit - r.bottom > 48) V.push(['primary-not-docked', label(p), `${Math.round(limit - r.bottom)}px above the bottom`]);
    if (!opts.inlinePrimaryOk && Math.round(r.height) < 52) V.push(['primary-size', label(p), `${Math.round(r.width)}x${Math.round(r.height)} (docked = wide, 56 tall)`]); }
  // 4. contrast of button text
  const rgb = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = ({ r, g, b }) => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const bgOf = e => { for (let x = e; x; x = x.parentElement) { const s = getComputedStyle(x); if (s.backgroundImage !== 'none' && x !== document.body) return null; const c = rgb(s.backgroundColor); if (c && c.a > .5) return c; } return { r: 242, g: 247, b: 246 }; };
  for (const e of taps.filter(e => e.matches('button') && !e.matches('.pearl') && !e.disabled && (e.innerText || '').trim())) { const s = getComputedStyle(e); const fg = rgb(s.color), bg = bgOf(e); if (!fg || !bg) continue;
    const L1 = lum(fg), L2 = lum(bg); const cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05); const px = parseFloat(s.fontSize), bold = +s.fontWeight >= 600; const large = px >= 24 || (bold && px >= 18.66);
    if (cr < (large ? 3 : 4.5)) V.push(['contrast', label(e), `${cr.toFixed(2)}:1 at ${px}px/${s.fontWeight}`]); }
  return { V, primInfo, navTop: Math.round(navTop), scrollH: document.documentElement.scrollHeight };
}
"""

# 5. content hidden under fixed bars: scroll to the end, nothing in the page flow may sit under a fixed bar
HIDDEN_JS = r"""
() => { const V = []; window.scrollTo(0, document.documentElement.scrollHeight); const H = innerHeight;
  const vis = e => { const r = e.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false; for (let x = e; x && x !== document.documentElement; x = x.parentElement) { const s = getComputedStyle(x); if (s.display === 'none' || s.visibility === 'hidden') return false; } return true; };
  const fixedOf = e => { for (let x = e; x && x !== document.body; x = x.parentElement) { const p = getComputedStyle(x).position; if (p === 'fixed' || p === 'sticky') return x; } return null; };
  const bars = [...document.querySelectorAll('.bottom, .ob-foot, .dock, .dock-row')].filter(vis).filter(b => getComputedStyle(b).position === 'fixed');
  let top = H; for (const b of bars) { const solid = b.matches('.ob-foot, .dock-row') ? [...b.children].filter(vis) : [b]; for (const s of solid) top = Math.min(top, s.getBoundingClientRect().top); }
  if (document.querySelector('.celebrate')) return V;
  const leaves = [...document.querySelectorAll('#app *')].filter(e => !e.closest('svg') && !(e.closest('details:not([open])') && !e.closest('summary')) && !fixedOf(e) && vis(e) && (e.children.length === 0 || e.matches('button, .tile, .word, canvas, img')));
  for (const e of leaves) { const r = e.getBoundingClientRect(); if (r.bottom > top + 1 && r.top < H) V.push(['under-fixed-bar', (e.innerText || e.className || e.tagName).replace(/\s+/g, ' ').trim().slice(0, 34), `bottom ${Math.round(r.bottom)} > bar ${Math.round(top)}`]); }
  window.scrollTo(0, 0); return V.slice(0, 4); }
"""

rows, sizes, shots = [], [], []

def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, reduced_motion='reduce')
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept('5'))
        pg.add_init_script("window.__mod=n=>performance.getEntriesByType('resource').map(e=>e.name).find(x=>x.includes('/src/'+n+'.js'))||('/src/'+n+'.js')")
        pg.add_init_script("const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){if(!String(this.src).includes('/ui/'))window.__last=this.src;return _p.call(this).catch(()=>{})}")
        n = [0]
        def audit(name, expect=False, inline=False, wait=600):
            pg.wait_for_timeout(wait); n[0] += 1; fn = f'{OUT}/{n[0]:02d}_{name}.png'
            pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(80); pg.screenshot(path=fn); shots.append(fn)
            r = pg.evaluate(AUDIT_JS, {'expectPrimary': expect, 'inlinePrimaryOk': inline})
            hid = pg.evaluate(HIDDEN_JS)
            for v in r['V'] + hid: rows.append((name, *v))
            for pi in r['primInfo'][-1:]: sizes.append((name, pi['label'], pi['w'], pi['h'], r['navTop'] - pi['bottom'] if not pg.query_selector('.celebrate') else 844 - pi['bottom']))
        click = lambda sel: pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=8000))
        def close_cel():
            pg.wait_for_selector('.celebrate', timeout=8000); pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(500)
        def primary():  # the last visible primary (docked continue)
            pg.wait_for_function("()=>[...document.querySelectorAll('.btn-primary')].some(e=>e.offsetParent||getComputedStyle(e).position==='fixed')", timeout=15000)
            pg.evaluate("()=>{const p=[...document.querySelectorAll('.btn-primary')].filter(e=>e.getClientRects().length);p[p.length-1].click()}")
            pg.wait_for_timeout(450)

        # ---------- onboarding ----------
        pg.goto(BASE); pg.wait_for_timeout(2200); audit('onb_welcome', True)
        click("text=Let's begin"); audit('onb_wake')
        click('.ob-sleeper'); pg.wait_for_timeout(2600); audit('onb_colour', True)
        click('.ob-sw >> nth=0'); click('.ob-cta'); audit('onb_who')
        click(".ob-opt:has-text('My child')"); pg.wait_for_timeout(1500); pg.fill('#ob-name', 'Zara'); audit('onb_name', True)
        click('.ob-cta'); audit('onb_goal'); click('.ob-opt >> nth=1'); pg.wait_for_timeout(1500)
        click('.ob-opt >> nth=0'); pg.wait_for_timeout(1500); click('.ob-opt >> nth=0'); pg.wait_for_timeout(1500)
        click('.ob-opt >> nth=0'); click('.ob-opt >> nth=3'); audit('onb_pains', True); click('.ob-cta')
        audit('onb_solution', True, wait=900); click('.ob-cta'); audit('onb_minutes')
        click('.ob-opt >> nth=1'); pg.wait_for_timeout(1500); audit('onb_processing', wait=500); pg.wait_for_timeout(3000)
        audit('onb_demo_alif', True); click('.ob-cta'); audit('onb_demo_be', True); click('.ob-cta'); audit('onb_demo_tap')
        for t in ['ب', 'ا', 'ب']:
            click(f".ob-choices .tile:text-is('{t}')"); pg.wait_for_timeout(950)
        audit('onb_demo_tap_done', True, wait=300); click('.ob-cta'); audit('onb_demo_blend', True)
        click('text=Join them'); audit('onb_demo_blend_done', True, wait=1500); click('.ob-cta'); audit('onb_demo_word')
        click('.ob-word'); audit('onb_demo_word_read', True, wait=1400); click('.ob-cta'); audit('onb_demo_check')
        click(".ob-choices .tile:text-is('بابا')"); audit('onb_demo_check_ok', True, wait=1300); click('.ob-cta')
        audit('onb_value', True, wait=1000); click('.ob-foot .btn-primary'); audit('onb_streak', True, wait=900); click('.ob-cta')
        audit('onb_commit'); click('.ob-opt >> nth=1'); pg.wait_for_timeout(1500); audit('onb_plan', True); click('.ob-cta')

        # ---------- learner app (child track) ----------
        pg.wait_for_timeout(2000); audit('today_first', True)
        pid = pg.evaluate("async()=>{const {db}=await import(window.__mod('db'));return db.setting('activeProfile')}")
        # unit 0: three rules -> celebration -> finish unit -> gold celebration
        click("button:has-text('Start:')"); pg.wait_for_timeout(600); audit('lesson_rules', True)
        primary(); primary(); primary(); audit('celebrate_lesson', True, wait=900)
        click('.cel-go'); pg.wait_for_timeout(600); audit('lesson_done_unit', True); primary(); audit('celebrate_unit', True, wait=900)
        close_cel(); pg.wait_for_timeout(800)
        nav = lambda k: (click(f".bottom button[data-k='{k}']"), pg.wait_for_timeout(900))

        def open_lesson(lid):
            pg.evaluate("""async([pid,lid])=>{const S=await import(window.__mod('session'));const P=await import(window.__mod('path'));const {db}=await import(window.__mod('db'));const {C}=await import(window.__mod('content'));
              const u=C.units[1];const ls=P.lessonsFor(u);const p=await S.getProgress(pid);const done={};for(const l of ls){if(l.id===lid)break;done[l.id]=Date.now()}p.units[1]={...(p.units[1]||{}),lessons:done};await db.put('progress',p)}""", [pid, lid])
            nav('units'); nav('today'); click("button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(700)

        def brute_tiles(rounds_sel_done, maxclicks=80):
            # click tiles until the docked continue appears (wrong taps are harmless in these drills)
            for k in range(maxclicks):
                if pg.query_selector('.lesson .btn-primary.btn-wide'): return True
                if pg.query_selector("button:has-text('Next word')") and pg.evaluate("()=>{const t=[...document.querySelectorAll('.choices .tile')];return t.length&&t.every(x=>x.disabled)}"):
                    click("button:has-text('Next word')"); continue
                ts = pg.query_selector_all('.choices .tile:not([disabled]):not(.no):not(.ok)')
                if not ts: pg.wait_for_timeout(300); continue
                pg.evaluate('e=>e.click()', ts[k % len(ts)]); pg.wait_for_timeout(260)
            pg.screenshot(path=OUT + '/zz_brute_fail.png'); print('BRUTE FAIL', pg.inner_text('#app')[:300].replace('\n', ' | ')); return False

        # letter lesson: be (second letter, so the tap-the-sound drill has a pool)
        open_lesson('Lbe'); audit('L_intro', True)
        primary(); audit('L_tellapart_start')
        click('.choices .tile'); pg.wait_for_timeout(300); audit('L_tellapart_round'); brute_tiles(None); audit('L_tellapart_done', True)
        primary(); audit('L_forms', True); primary(); audit('L_trace', True); primary()
        if pg.query_selector("h2:has-text('Blend it')"): audit('L_blend', True); primary()
        audit('L_check')
        for _ in range(4):
            pg.evaluate("""async()=>{const {C,forms}=await import(window.__mod('content'));const L=C.by['ب'];const ch=document.querySelector('.choices');if(!ch)return;const q=ch.previousElementSibling.textContent;const m=q.match(/at the (\\w+) position/);const g=m?forms(L).find(f=>f[0]===m[1])[1]:L.ch;const t=[...ch.querySelectorAll('.tile')].find(x=>x.textContent===g)||ch.querySelector('.tile');t&&t.click()}""")
            pg.wait_for_timeout(650)
        audit('L_check_done', True); primary(); pg.wait_for_timeout(800); close_cel(); pg.wait_for_timeout(600)

        open_lesson('marks'); audit('marks_intro', True); primary(); audit('marks_find'); brute_tiles(None); primary(); pg.wait_for_timeout(700); close_cel()
        open_lesson('join'); audit('join_forms', True); primary(); audit('join_build'); brute_tiles(None); audit('join_build_done', True); primary(); pg.wait_for_timeout(700); close_cel()
        open_lesson('blend'); audit('blend'); brute_tiles(None); audit('blend_done', True); primary(); pg.wait_for_timeout(700); close_cel()
        open_lesson('W1'); audit('words_read', True); primary(); audit('words_build'); brute_tiles(None); primary(); audit('words_dictation')
        for _ in range(6):
            s = pg.query_selector("button:has-text('Skip'):not([disabled])")
            if not s: break
            pg.evaluate('e=>e.click()', s); pg.wait_for_timeout(1000)
        audit('words_dictation_done', True); primary(); pg.wait_for_timeout(700); close_cel()
        has_read = pg.evaluate("async()=>{const P=await import(window.__mod('path'));const {C}=await import(window.__mod('content'));return P.lessonsFor(C.units[1]).some(l=>l.id==='read')}")
        if has_read: open_lesson('read'); audit('read_lesson', True); primary(); pg.wait_for_timeout(700); close_cel()
        open_lesson('quiz'); audit('quiz', True)
        pg.evaluate("()=>document.querySelectorAll('ol li').forEach(li=>{const r=li.querySelector('b').textContent;const t=[...li.querySelectorAll('.tile')].find(x=>x.getAttribute('aria-label')===r);t&&t.click()})")
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Submit').click()"); pg.wait_for_timeout(900); audit('quiz_done', True)
        primary(); pg.wait_for_timeout(800); close_cel(); pg.wait_for_timeout(800)

        # tabs
        audit('today_unit2', True)
        pg.evaluate("async(pid)=>{const {db}=await import(window.__mod('db'));for(const c of await db.by('cards','profileId',pid))await db.put('cards',{...c,due:Date.now()+9e9})}", pid)
        nav('review'); audit('review_empty', True)
        pg.evaluate("async(pid)=>{const {db}=await import(window.__mod('db'));for(const c of await db.by('cards','profileId',pid))await db.put('cards',{...c,due:0})}", pid)
        nav('read'); nav('review'); audit('review_due', True); click("button:has-text('Not yet')"); pg.wait_for_timeout(300); audit('review_due_reveal', True, wait=200)
        nav('read'); audit('read_tab'); nav('progress'); audit('progress_tab'); nav('more'); audit('more_tab'); nav('units'); audit('units_tab')
        # placement check (fresh learner path): open from Today on a new profile is heavy; run it via the module directly
        b.close()
        if errs: print('page errors:', errs[:5])

main()
from collections import Counter
print(f"\n{'screen':24} {'rule':20} {'element':36} detail")
for r in rows: print(f'{r[0]:24} {r[1]:20} {r[2]:36} {r[3]}')
print('\nviolations:', len(rows), dict(Counter(r[1] for r in rows)))
print('\nprimary sizes (screen, label, w, h, gap above bottom bar):')
for s in sizes: print('  ', s)
json.dump({'rows': rows, 'sizes': sizes, 'shots': shots}, open(f'{OUT}/audit.json', 'w'), ensure_ascii=False, indent=1)
