# Targeted probes (read-only against the app): keyboard, live announcements, reduced motion, Urdu rendering, focus ring contrast.
# Usage: python3 probes.py <keyboard|live|motion|urdu|dark> [child|adult]
import sys, os, json, glob
from playwright.sync_api import sync_playwright
MODE = sys.argv[1]; TRACK = sys.argv[2] if len(sys.argv) > 2 else 'child'
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = f'{ROOT}/probes'; os.makedirs(OUT, exist_ok=True)
BASE = 'http://localhost:5188/'
EXE = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-1243/*/chrome-headless-shell'))[0]
INIT_MOD = "window.__mod=n=>performance.getEntriesByType('resource').map(e=>e.name).find(x=>x.includes('/src/'+n+'.js'))||('/src/'+n+'.js')"
INIT_PLAY = "const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){return _p.call(this).catch(()=>{})}"
res = {}

def new_ctx(b, motion='reduce', scheme='light', w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, reduced_motion=motion, color_scheme=scheme, has_touch=True, is_mobile=True)
    pg = c.new_page(); pg.add_init_script(INIT_MOD); pg.add_init_script(INIT_PLAY); pg.on('dialog', lambda d: d.accept('5')); return pg

def make_learner(pg, track):
    pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1800)
    pg.evaluate("e=>e.click()", pg.wait_for_selector('text=Just me')); pg.wait_for_timeout(300)
    pg.evaluate("e=>e.click()", pg.wait_for_selector('text=+ Add a learner')); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', 'Zara'); pg.select_option('select >> nth=0', track)
    pg.evaluate("e=>e.click()", pg.wait_for_selector("button:has-text('Start')")); pg.wait_for_timeout(1800)
    return pg.evaluate("async()=>{const {db}=await import(window.__mod('db'));return db.setting('activeProfile')}")

def click(pg, sel): pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=8000))
def nav(pg, k): click(pg, f".bottom button[data-k='{k}']"); pg.wait_for_timeout(800)
def open_lesson(pg, pid, lid, unit=1):
    pg.evaluate("""async([pid,lid,ui])=>{const S=await import(window.__mod('session'));const P=await import(window.__mod('path'));const {db}=await import(window.__mod('db'));const {C}=await import(window.__mod('content'));
      const u=C.units[ui];const ls=P.lessonsFor(u);const p=await S.getProgress(pid);const done={};for(const l of ls){if(l.id===lid)break;done[l.id]=Date.now()}p.units[ui]={...(p.units[ui]||{}),lessons:done};await db.put('progress',p)}""", [pid, lid, unit])
    nav(pg, 'read'); nav(pg, 'today'); click(pg, "button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(700)
def primary(pg):
    pg.wait_for_function("()=>[...document.querySelectorAll('.btn-primary')].some(e=>e.offsetParent||getComputedStyle(e).position==='fixed')", timeout=15000)
    pg.evaluate("()=>{const p=[...document.querySelectorAll('.btn-primary')].filter(e=>e.getClientRects().length);p[p.length-1].click()}"); pg.wait_for_timeout(450)

def finish_unit0(pg):
    click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(600); primary(pg); primary(pg); primary(pg)
    pg.wait_for_selector('.celebrate', timeout=8000); click(pg, '.cel-go'); pg.wait_for_timeout(600); primary(pg)
    pg.wait_for_selector('.celebrate', timeout=8000); pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(800)

DESC = "e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return {tag:e.tagName.toLowerCase()+(e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\\s+/).slice(0,2).join('.'):''),name:(e.getAttribute('aria-label')||e.innerText||e.value||'').replace(/\\s+/g,' ').trim().slice(0,40),role:e.getAttribute('role'),rect:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)],outline:s.outlineStyle+' '+s.outlineWidth+' '+s.outlineColor,shadow:s.boxShadow.slice(0,50),inView:r.top>=0&&r.bottom<=innerHeight&&r.width>0}}"

def tab_through(pg, limit=45):
    pg.evaluate("document.activeElement&&document.activeElement.blur();window.scrollTo(0,0)"); seq = []; first = None
    for i in range(limit):
        pg.keyboard.press('Tab'); pg.wait_for_timeout(60)
        d = pg.evaluate("()=>{const e=document.activeElement;return e&&e!==document.body?(" + DESC + ")(e):null}")
        if d is None: seq.append(None); continue
        key = json.dumps(d['rect']) + d['name']
        if first is None: first = key
        elif key == first: break
        seq.append(d)
    return seq

NONFOCUS = """() => { const ok = e => e.matches('button,a[href],input,select,textarea,summary,[tabindex]:not([tabindex="-1"]),[role=button],canvas'); const out = [];
  for (const e of document.querySelectorAll('#app *, .celebrate *, body > div *')) { const r = e.getBoundingClientRect(); if (r.width < 8 || r.height < 8) continue; const s = getComputedStyle(e); if (s.cursor !== 'pointer' || s.visibility === 'hidden' || s.display === 'none') continue;
    if (ok(e) || e.closest('button,a[href],summary,label,[role=button],[tabindex]')) continue; out.push((e.tagName.toLowerCase() + '.' + (e.className || '')).slice(0, 50) + ' "' + (e.innerText || '').trim().slice(0, 20) + '"'); } return out.slice(0, 12); }"""

def run():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE)
        if MODE == 'keyboard':
            pg = new_ctx(b); pid = make_learner(pg, TRACK); finish_unit0(pg)
            def snap(name, extra=None):
                seq = tab_through(pg); res[name] = {'tabs': len([s for s in seq if s]), 'nulls': len([s for s in seq if s is None]), 'seq': seq, 'nonfocusable_clickables': pg.evaluate(NONFOCUS), 'offscreen_focus': [s['name'] for s in seq if s and not s['inView']][:6],
                  'no_ring': [s['name'] for s in seq if s and s['outline'].startswith('none') and s['shadow'] == 'none'][:6], 'activeAfter': None}
                pg.screenshot(path=f'{OUT}/kb_{TRACK}_{name}.png')
            snap('today')
            open_lesson(pg, pid, 'Lbe'); snap('lesson_intro')
            # focus after pressing the primary with the keyboard
            for _ in range(10):
                pg.keyboard.press('Tab'); a = pg.evaluate("document.activeElement.className||document.activeElement.tagName")
                if 'btn-primary' in str(a): break
            pg.keyboard.press('Enter'); pg.wait_for_timeout(700)
            res['focus_after_continue'] = pg.evaluate("(" + DESC + ")(document.activeElement)") if pg.evaluate("document.activeElement!==document.body") else 'document.body (focus lost)'
            snap('tellapart_start')
            if pg.query_selector('.choices .tile'):
                pg.evaluate("document.activeElement&&document.activeElement.blur()")
                for _ in range(12):
                    pg.keyboard.press('Tab'); on = pg.evaluate("document.activeElement.classList.contains('tile')")
                    if on: break
                before = pg.evaluate("document.querySelector('.choices').outerHTML.length+'|'+[...document.querySelectorAll('.choices .tile')].map(t=>t.className).join(',')")
                pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
                after = pg.evaluate("[...document.querySelectorAll('.choices .tile')].map(t=>t.className).join(',')")
                res['tile_enter'] = {'classes_before': before.split('|')[1], 'classes_after': after}
                pg.screenshot(path=f'{OUT}/kb_{TRACK}_tile_after_enter.png')
            nav(pg, 'me'); snap('me')
            pg.evaluate("window.__stickers&&window.__stickers.openBook()"); pg.wait_for_timeout(900)
            seq = tab_through(pg, 60); res['sticker_book_overlay'] = {'tabs': len([s for s in seq if s]), 'reaches_nav_behind_overlay': [s['name'] for s in seq if s and 'bottom' in s['tag']][:4], 'seq_names': [s['name'] for s in seq if s][:25]}
            pg.screenshot(path=f'{OUT}/kb_{TRACK}_stickerbook.png')
            # trace canvas keyboard alternative?
            res['trace_canvas_keyboard'] = 'see L_trace screen in walk results'
        elif MODE == 'pin':
            pg = new_ctx(b); pid = make_learner(pg, TRACK)
            pg.evaluate("async()=>{const {db}=await import(window.__mod('db'));await db.setting('mode','school');await db.setting('teacherPin','1234');await db.setting('activeProfile',null)}"); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(2000)
            click(pg, "button:has-text('Teacher')"); pg.wait_for_selector('input[type=password]'); pg.focus('input[type=password]')
            pg.keyboard.type('1234', delay=80); res['pin_value_after_typing_1234'] = pg.evaluate("document.querySelector('input[type=password]').value")
            pg.fill('input[type=password]', '1234'); res['pin_value_after_fill'] = pg.evaluate("document.querySelector('input[type=password]').value")
            # sticker book: Enter on a focused control
            pg2 = new_ctx(b); pid2 = make_learner(pg2, TRACK); nav(pg2, 'me'); pg2.evaluate("window.__stickers.openBook()"); pg2.wait_for_timeout(1200)
            pg2.keyboard.press('Tab'); res['book_active_after_tab'] = pg2.evaluate("document.activeElement.className"); pg2.keyboard.press('Enter'); pg2.wait_for_timeout(600); res['book_still_open_after_Enter_on_Back'] = bool(pg2.query_selector('.stk-book'))
            pg2.keyboard.press('Escape'); pg2.wait_for_timeout(600); res['book_open_after_Escape'] = bool(pg2.query_selector('.stk-book'))
            pg2.evaluate("window.__stickers.openBook()"); pg2.wait_for_timeout(1000); pg2.evaluate("document.querySelector('.stk-tab:nth-of-type(2)').focus()"); pg2.keyboard.press('Enter'); pg2.wait_for_timeout(500)
            res['book_tab2_selected_after_Enter'] = pg2.evaluate("document.querySelector('.stk-tab:nth-of-type(2)').getAttribute('aria-selected')")
        elif MODE == 'live':
            pg = new_ctx(b); pid = make_learner(pg, TRACK); finish_unit0(pg)
            pg.evaluate("""() => { window.__ann = []; const sel = '[aria-live],[role=status],[role=alert],[role=log]';
              new MutationObserver(ms => { for (const m of ms) { const t = m.target.nodeType === 3 ? m.target.parentElement : m.target; const live = t && t.closest && t.closest(sel); window.__ann.push({live: live ? (live.getAttribute('aria-live') || live.getAttribute('role')) : null, type: m.type, attr: m.attributeName, el: (t.tagName + '.' + (t.className || '')).slice(0, 40), txt: (m.type === 'attributes' ? t.getAttribute(m.attributeName) : (t.textContent || '')).slice(0, 80), added: [...m.addedNodes].map(n => (n.textContent || '').slice(0, 40)).join('|')}); } }).observe(document.body, {subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ['aria-label', 'aria-live', 'class', 'aria-pressed', 'aria-disabled', 'disabled']}); }""")
            open_lesson(pg, pid, 'Lbe'); primary(pg); pg.wait_for_timeout(500)
            pg.evaluate("window.__ann=[]"); pg.wait_for_selector('.choices .tile', timeout=10000); pg.wait_for_timeout(800)
            tiles = pg.query_selector_all('.choices .tile')
            res['tile_names_before'] = [t.get_attribute('aria-label') or t.inner_text() for t in tiles]
            # find the wrong one and the right one: click the first tile, record, then continue
            pg.evaluate('e=>e.click()', tiles[0]); pg.wait_for_timeout(1400)
            res['after_first_tap'] = pg.evaluate("window.__ann.filter(a=>a.type!=='attributes'||a.attr!=='class').slice(0,25)")
            res['after_first_tap_class_changes'] = pg.evaluate("window.__ann.filter(a=>a.attr==='class').length")
            res['tile_state_after'] = pg.evaluate("[...document.querySelectorAll('.choices .tile')].map(t=>({cls:t.className,label:t.getAttribute('aria-label'),pressed:t.getAttribute('aria-pressed'),dis:t.disabled,ad:t.getAttribute('aria-disabled')}))")
            res['live_regions_in_dom'] = pg.evaluate("[...document.querySelectorAll('[aria-live],[role=status],[role=alert]')].map(e=>e.tagName+'.'+e.className+' '+(e.getAttribute('aria-live')||e.getAttribute('role'))+' text='+e.textContent.slice(0,40))")
            pg.evaluate("window.__ann=[]")
            for _ in range(6):
                ts = pg.query_selector_all('.choices .tile:not([disabled]):not(.no):not(.ok)')
                if not ts: break
                pg.evaluate('e=>e.click()', ts[0]); pg.wait_for_timeout(700)
            res['announcements_during_round'] = pg.evaluate("window.__ann.filter(a=>a.live).slice(0,20)")
            res['toast_probe'] = pg.evaluate("(async()=>{const {toast}=await import(window.__mod('content'));window.__ann=[];toast('Saved');await new Promise(r=>setTimeout(r,300));return {ann:window.__ann.slice(0,6),el:document.getElementById('toast').outerHTML.slice(0,160)}})()")
        elif MODE == 'motion':
            PROBE = """() => { const ans = document.getAnimations().filter(a => a.playState === 'running').map(a => { const t = a.effect && a.effect.target; const ct = a.effect && a.effect.getComputedTiming ? a.effect.getComputedTiming() : {}; return {type: a.constructor.name, name: a.animationName || a.transitionProperty || 'waapi', el: t ? (t.tagName + '.' + (t.className && t.className.baseVal === undefined ? t.className : '')).slice(0, 36) : '?', dur: Math.round(ct.duration || 0), iter: ct.iterations === Infinity ? 'inf' : ct.iterations}; });
              const lot = [...document.querySelectorAll('svg')].filter(s => s.closest('.fx,.marko,[class*=fx],[class*=marko],.mascot,.ob-m')).length; return {n: ans.length, inf: ans.filter(a => a.iter === 'inf').length, list: ans.slice(0, 8), lottieSvgs: lot}; }"""
            LOT = "() => [...document.querySelectorAll('svg g[transform]')].slice(0, 80).map(g => g.getAttribute('transform')).join('')"
            out = []
            def probe(name, delay=60, lottie=True):
                pg_ = cur[0]; pg_.wait_for_timeout(delay); r = pg_.evaluate(PROBE)
                if lottie: a = pg_.evaluate(LOT); pg_.wait_for_timeout(500); r['lottie_moves'] = a != pg_.evaluate(LOT)
                r['screen'] = name; out.append(r)
            for motion in ['reduce', 'no-preference']:
                out = []; pg = new_ctx(b, motion); cur = [pg]
                pg.goto(BASE); pg.wait_for_timeout(1800); probe('onb_welcome', 100)
                click(pg, "text=Let's begin"); probe('onb_wake', 300); click(pg, '.ob-sleeper'); probe('onb_wake_awake', 200)
                pg = new_ctx(b, motion); cur[0] = pg; pid = make_learner(pg, TRACK); probe('today_idle', 1500)
                nav(pg, 'review'); probe('tab_switch_review', 30, False); nav(pg, 'today')
                click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(600); probe('lesson_idle', 800)
                primary(pg); primary(pg); primary(pg); probe('celebrate_150ms', 150); probe('celebrate_2s', 1800)
                click(pg, '.cel-go'); pg.wait_for_timeout(600); primary(pg); pg.wait_for_selector('.celebrate', timeout=8000); pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(800)
                open_lesson(pg, pid, 'Lbe'); primary(pg); pg.wait_for_timeout(500)
                pg.wait_for_selector('.choices .tile', timeout=10000); pg.wait_for_timeout(800); tiles = pg.query_selector_all('.choices .tile'); pg.evaluate('e=>e.click()', tiles[0]); probe('tile_tap_60ms', 60, False); probe('tile_tap_400ms', 340, False)
                ts = pg.query_selector_all('.choices .tile:not([disabled]):not(.no):not(.ok)')
                if ts: pg.evaluate('e=>e.click()', ts[0]); probe('tile_tap2_60ms', 60, False)
                res[motion] = out
                css = pg.evaluate("() => { const r = []; for (const e of document.querySelectorAll('button,.tile,.btn,.card')) { const s = getComputedStyle(e); if (parseFloat(s.transitionDuration) > 0 || (s.animationName !== 'none')) r.push(e.className.toString().slice(0, 30) + ' t=' + s.transitionDuration + ' a=' + s.animationName); } return [...new Set(r)].slice(0, 12); }")
                res[motion + '_css_transitions_on_controls'] = css
        elif MODE == 'urdu':
            pg = new_ctx(b); pid = make_learner(pg, TRACK); finish_unit0(pg)
            INK = r"""() => { const out = []; const cv = document.createElement('canvas').getContext('2d');
              for (const e of document.querySelectorAll('.ur')) { const r = e.getBoundingClientRect(); if (r.width < 4 || r.height < 4) continue; const s = getComputedStyle(e); const txt = (e.innerText || '').trim(); if (!txt) continue;
                cv.font = `${s.fontWeight} ${s.fontSize} ${s.fontFamily}`; const m = cv.measureText(txt.split('\n')[0]); const ink = m.actualBoundingBoxAscent + m.actualBoundingBoxDescent; const lh = parseFloat(s.lineHeight) || r.height;
                let clip = null; for (let x = e; x && x !== document.body; x = x.parentElement) { const ps = getComputedStyle(x); if (ps.overflowY !== 'visible' || ps.overflowX !== 'visible') { clip = x; break; } }
                const cr = clip ? clip.getBoundingClientRect() : null;
                const overflowsClip = clip && (r.top < cr.top - 1 || r.bottom > cr.bottom + 1 || r.left < cr.left - 1 || r.right > cr.right + 1) && !/auto|scroll/.test(getComputedStyle(clip).overflowY);
                const selfClip = (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) && getComputedStyle(e).overflow !== 'visible';
                const bad = ink > lh * 1.02 || overflowsClip || selfClip || r.right > innerWidth + 1 || r.left < -1;
                if (bad) out.push({txt: txt.slice(0, 14), fs: s.fontSize, lh: Math.round(lh), ink: Math.round(ink), box: Math.round(r.height), w: Math.round(r.width), clip: clip ? clip.className.toString().slice(0, 20) : null, overflowsClip: !!overflowsClip, selfClip, off: r.right > innerWidth + 1 || r.left < -1}); }
              return out.slice(0, 8); }"""
            combos = [('naskh', '1', '0'), ('nastaliq', '1', '0'), ('naskh', '1.5', '0'), ('nastaliq', '1.5', '0'), ('nastaliq', '1.5', '0.12'), ('naskh', '1', '0.12'), ('naskh', '1', '0.05')]
            res['rows'] = []
            screens = [('L_intro', lambda: open_lesson(pg, pid, 'Lbe')), ('L_tellapart', lambda: primary(pg)), ('words_read', None)]
            for style, sc, sp in combos:
                tag = f'{style}_s{sc}_sp{sp}'
                for sname, setup in [('L_intro', 'intro'), ('tell', 'tell'), ('words', 'words')]:
                    open_lesson(pg, pid, 'Lbe' if setup != 'words' else 'W1')
                    if setup == 'tell': primary(pg); pg.wait_for_timeout(500)
                    pg.evaluate("([a,b,c])=>{document.body.dataset.style=a;document.documentElement.style.setProperty('--ur-scale',b);document.documentElement.style.setProperty('--ur-spacing',c+'em')}", [style, sc, sp]); pg.wait_for_timeout(500)
                    bad = pg.evaluate(INK); hs = pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
                    res['rows'].append({'combo': tag, 'screen': sname, 'bad_ur': bad, 'hscroll': hs})
                    pg.screenshot(path=f'{OUT}/urdu_{TRACK}_{tag}_{sname}.png')
                    nav(pg, 'read'); nav(pg, 'today')
                    pg.evaluate("()=>document.querySelector('.stk-back')?.click()")
        b.close()
    json.dump(res, open(f'{OUT}/{MODE}_{TRACK}.json', 'w'), ensure_ascii=False, indent=1, default=str)
    print('wrote', f'{OUT}/{MODE}_{TRACK}.json')
run()
