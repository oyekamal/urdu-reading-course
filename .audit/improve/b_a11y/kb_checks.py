# Regression checks for round 11b a11y fixes (keyboard, dialogs, focus, live regions, lang, nav, celebration reach).
# Usage: python3 kb_checks.py [port]   -> writes probes/kb_checks.json, prints PASS/FAIL per check, exit 1 on any FAIL.
import sys, os, json, glob
from playwright.sync_api import sync_playwright
PORT = sys.argv[1] if len(sys.argv) > 1 else '5188'
BASE = f'http://localhost:{PORT}/'
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = f'{ROOT}/probes'; os.makedirs(OUT, exist_ok=True)
EXE = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell'))[0]
INIT_MOD = "window.__mod=n=>performance.getEntriesByType('resource').map(e=>e.name).find(x=>x.includes('/src/'+n+'.js'))||('/src/'+n+'.js')"
INIT_PLAY = "const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){return _p.call(this).catch(()=>{})}"
FS_JS = r"""(f) => { const els = [...document.querySelectorAll('body, body *')].filter(e => !['SCRIPT','STYLE'].includes(e.tagName) && !e.closest('svg'));
  const sizes = els.map(e => parseFloat(getComputedStyle(e).fontSize)); els.forEach((e, i) => e.style.setProperty('font-size', (sizes[i] * f).toFixed(2) + 'px', 'important')); }"""
res = []
def check(name, ok, detail=''):
    res.append({'name': name, 'ok': bool(ok), 'detail': str(detail)[:300]}); print(('PASS' if ok else 'FAIL'), name, '' if ok else str(detail)[:300])

def new_ctx(b, w=390, h=844, scheme='light', motion='reduce'):
    c = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, reduced_motion=motion, color_scheme=scheme, has_touch=True, is_mobile=True)
    pg = c.new_page(); pg.add_init_script(INIT_MOD); pg.add_init_script(INIT_PLAY); pg.on('dialog', lambda d: d.accept('5'))
    pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200])); return pg
def click(pg, sel, to=8000): pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=to))
def nav(pg, k): click(pg, f".bottom button[data-k='{k}']"); pg.wait_for_timeout(800)
def make_learner(pg, track='child'):
    pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1800)
    click(pg, 'text=Just me'); pg.wait_for_timeout(300); click(pg, 'text=+ Add a learner'); pg.wait_for_timeout(300)
    pg.fill('input[placeholder=Name]', 'Zara'); pg.select_option('select >> nth=0', track); click(pg, "button:has-text('Start')"); pg.wait_for_timeout(1800)
    return pg.evaluate("async()=>{const {db}=await import(window.__mod('db'));return db.setting('activeProfile')}")
def primary(pg):
    pg.wait_for_function("()=>[...document.querySelectorAll('.btn-primary')].some(e=>e.getClientRects().length)", timeout=15000)
    pg.evaluate("()=>{const p=[...document.querySelectorAll('.btn-primary')].filter(e=>e.getClientRects().length);p[p.length-1].click()}"); pg.wait_for_timeout(450)
def open_lesson(pg, pid, lid, unit=1):
    pg.evaluate("""async([pid,lid,ui])=>{const S=await import(window.__mod('session'));const P=await import(window.__mod('path'));const {db}=await import(window.__mod('db'));const {C}=await import(window.__mod('content'));
      const u=C.units[ui];const ls=P.lessonsFor(u);const p=await S.getProgress(pid);const done={};for(const l of ls){if(l.id===lid)break;done[l.id]=Date.now()}p.units[ui]={...(p.units[ui]||{}),lessons:done};await db.put('progress',p)}""", [pid, lid, unit])
    nav(pg, 'read'); nav(pg, 'today'); click(pg, "button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(700)
AE = "(()=>{const e=document.activeElement;return e?e.tagName.toLowerCase()+'.'+(e.className&&e.className.toString().trim().split(/\\s+/)[0]||'')+'|'+(e.getAttribute('aria-label')||e.textContent||'').trim().slice(0,30):null})()"
IN = lambda sel: f"(()=>{{const e=document.activeElement;const r=document.querySelector('{sel}');return !!(e&&r&&r.contains(e))}})()"

def run():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE)
        pg = new_ctx(b); pid = make_learner(pg)
        # ---- unit 0 through the celebration, keyboard only on the celebration
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(600); primary(pg); primary(pg); primary(pg)
        pg.wait_for_selector('.celebrate', timeout=8000); pg.wait_for_timeout(600)
        check('celebrate role=dialog aria-modal', pg.evaluate("(()=>{const c=document.querySelector('.celebrate');return c.getAttribute('role')==='dialog'&&c.getAttribute('aria-modal')==='true'&&!!c.getAttribute('aria-labelledby')})()"))
        check('celebrate focus moved in (h1)', pg.evaluate(IN('.celebrate')) and pg.evaluate("document.activeElement.tagName")=='H1', pg.evaluate(AE))
        check('page behind celebrate is inert', pg.evaluate("document.getElementById('app').inert===true"))
        seen = set()
        for _ in range(10):
            pg.keyboard.press('Tab'); seen.add(pg.evaluate(AE));
            if not pg.evaluate(IN('.celebrate')): break
        check('Tab stays inside celebrate', pg.evaluate(IN('.celebrate')), seen)
        pg.keyboard.press('Shift+Tab'); check('Shift+Tab stays inside celebrate', pg.evaluate(IN('.celebrate')))
        # focus the Next button and Enter -> next lesson, focus on its heading
        pg.evaluate("document.querySelector('.cel-go').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(900)
        check('celebrate closed, app no longer inert', pg.evaluate("!document.querySelector('.celebrate') && document.getElementById('app').inert!==true"))
        check('focus after celebrate Next is a heading in the new screen', pg.evaluate("/^H[12]$/.test(document.activeElement.tagName)"), pg.evaluate(AE))
        # ---- leave lesson sheet
        gap = pg.evaluate("(()=>{const x=document.querySelector('.lesson-x').getBoundingClientRect();const r=[...document.querySelectorAll('.lesson>.row:first-child .btn-play')][0].getBoundingClientRect();return Math.round(x.left-r.right)})()")
        check('leave X is >=16px from the speaker button', gap >= 16, gap)
        pg.evaluate("document.querySelector('.lesson-x').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
        check('leave sheet opens (not window.confirm), focus on Keep going', pg.evaluate("!!document.querySelector('.a11y-sheet')") and 'Keep going' in (pg.evaluate(AE) or ''), pg.evaluate(AE))
        check('leave sheet copy', pg.evaluate("document.querySelector('.a11y-sheet h2').textContent")=='Leave this lesson?' and 'progress here is saved' in pg.evaluate("document.querySelector('.a11y-sheet p').textContent"))
        for _ in range(6): pg.keyboard.press('Tab')
        check('Tab trapped in leave sheet', pg.evaluate(IN('.a11y-sheet')))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(500)
        check('Escape closes leave sheet and stays in lesson', pg.evaluate("!document.querySelector('.a11y-sheet') && !!document.querySelector('.lesson')"))
        check('focus returns to the X after the sheet', 'Leave lesson' in (pg.evaluate(AE) or ''), pg.evaluate(AE))
        pg.keyboard.press('Enter'); pg.wait_for_timeout(400); pg.evaluate("document.querySelector('.a11y-leave').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(900)
        check('Leave goes back to the path', pg.evaluate("!document.querySelector('.lesson') && !!document.querySelector('.home-hero, .unit')"))
        # ---- wrong answer announced
        pg2 = new_ctx(b); pid2 = make_learner(pg2); click(pg2, "button:has-text('Start:')"); pg2.wait_for_timeout(500); primary(pg2); primary(pg2); primary(pg2); pg2.wait_for_selector('.celebrate'); click(pg2, '.cel-go'); pg2.wait_for_timeout(600); primary(pg2); pg2.wait_for_selector('.celebrate'); pg2.evaluate("(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg2.wait_for_timeout(800)
        open_lesson(pg2, pid2, 'Lbe'); primary(pg2); pg2.wait_for_selector('.choices .tile', timeout=10000); pg2.wait_for_timeout(900)
        pg2.evaluate("()=>{window.__a=[]}")
        for k in range(10):
            pg2.evaluate("k=>{const t=[...document.querySelectorAll('.choices .tile:not([disabled])')];t[k%2]&&t[k%2].click()}", k); pg2.wait_for_timeout(700)
            if pg2.query_selector('.choices .tile.no'): break
        txt = pg2.evaluate("document.getElementById('a11y-live').textContent"); print('live:', txt, pg2.evaluate("window.__a"))
        check('wrong answer is announced in the live region', txt.startswith('Not quite'), txt)
        check('hint bubble is not double-read (aria-hidden)', pg2.evaluate("[...document.querySelectorAll('.feel-say')].every(b=>b.getAttribute('aria-hidden')==='true')"))
        check('right tile labelled as the answer', pg2.evaluate("[...document.querySelectorAll('.tile.feel-answer')].every(t=>/the answer$/.test(t.getAttribute('aria-label')))") )
        check('live region + toast exist at load', pg2.evaluate("!!document.getElementById('a11y-live') && document.getElementById('toast').getAttribute('role')==='status'"))
        # ---- nav semantics + lang + decorative
        check('nav is labelled navigation with one aria-current=page', pg2.evaluate("(()=>{const n=document.querySelector('.bottom');return n.getAttribute('role')==='navigation'&&n.querySelectorAll('[aria-current=page]').length===1&&n.querySelector('[aria-current=page]').classList.contains('active')})()"))
        nav(pg2, 'read'); check('aria-current follows the active tab', pg2.evaluate("document.querySelector('.bottom [aria-current=page]').dataset.k")=='read')
        nav(pg2, 'today')
        miss = pg2.evaluate("""()=>{const out=[];const A=/[\\u0600-\\u06FF]/;const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);for(let t=w.nextNode();t;t=w.nextNode()){if(!A.test(t.nodeValue))continue;const p=t.parentElement;if(!p||p.closest('[aria-hidden=true]')||p.closest('[lang=ur]')||p.closest('script,style'))continue;out.push(p.tagName+'.'+p.className+':'+t.nodeValue.trim().slice(0,12))}return out.slice(0,8)}""")
        check('every Urdu text node is inside lang=ur', not miss, miss)
        check('decorative Marko/Lottie hidden from AT', pg2.evaluate("[...document.querySelectorAll('.marko,.fx')].every(e=>e.getAttribute('aria-hidden')==='true'||e.closest('[aria-hidden=true]'))"))
        check('inline Urdu px sizes follow --ur-scale', pg2.evaluate("[...document.querySelectorAll('.ur[data-urpx]')].every(e=>e.style.fontSize.includes('--ur-scale'))"))
        # ---- sticker book keyboard
        nav(pg2, 'me'); pg2.wait_for_selector('.stk-entry'); pg2.evaluate("document.querySelector('.stk-entry').focus()"); pg2.keyboard.press('Enter'); pg2.wait_for_selector('.stk-book'); pg2.wait_for_timeout(800)
        check('sticker book role=dialog aria-modal, focus inside', pg2.evaluate("(()=>{const o=document.querySelector('.stk-book');return o.getAttribute('role')==='dialog'&&o.getAttribute('aria-modal')==='true'})()") and pg2.evaluate(IN('.stk-book')), pg2.evaluate(AE))
        stay = True
        for _ in range(40):
            pg2.keyboard.press('Tab'); stay = stay and pg2.evaluate(IN('.stk-book'))
        check('sticker book traps Tab (40 presses)', stay)
        check('page behind sticker book inert', pg2.evaluate("document.getElementById('app').inert===true"))
        pg2.evaluate("document.querySelector('.stk-back').focus()"); pg2.keyboard.press('Enter'); pg2.wait_for_timeout(600)
        check('Enter on Back closes the book', pg2.evaluate("!document.querySelector('.stk-book')"))
        check('focus returns to the Sticker book button', 'Sticker book' in (pg2.evaluate(AE) or ''), pg2.evaluate(AE))
        check('page no longer inert after book', pg2.evaluate("document.getElementById('app').inert!==true"))
        pg2.keyboard.press('Enter'); pg2.wait_for_selector('.stk-book'); pg2.wait_for_timeout(700)
        pg2.evaluate("document.querySelectorAll('.stk-tab')[2].focus()"); pg2.keyboard.press('Enter'); pg2.wait_for_timeout(300)
        t3 = pg2.evaluate("document.querySelectorAll('.stk-tab')[2].getAttribute('aria-selected')")
        pg2.evaluate("document.querySelectorAll('.stk-tab')[3].focus()"); pg2.keyboard.press('Space'); pg2.wait_for_timeout(300)
        check('Enter and Space select a unit tab', t3 == 'true' and pg2.evaluate("document.querySelectorAll('.stk-tab')[3].getAttribute('aria-selected')") == 'true')
        pg2.keyboard.press('Escape'); pg2.wait_for_timeout(600)
        check('Escape closes the book', pg2.evaluate("!document.querySelector('.stk-book')"))
        check('focus returns to opener after Escape', 'Sticker book' in (pg2.evaluate(AE) or ''), pg2.evaluate(AE))
        # ---- double overlay: book then confirm sheet, closed in reverse order
        pg2.keyboard.press('Enter'); pg2.wait_for_selector('.stk-book'); pg2.wait_for_timeout(600)
        pg2.evaluate("(()=>{window.__a11y.confirmSheet({title:'Leave?',body:'x'});return 1})()"); pg2.wait_for_timeout(400)
        check('stacked: sheet on top has focus, book inert', pg2.evaluate(IN('.a11y-sheet')) and pg2.evaluate("document.querySelector('.stk-book').inert===true"), pg2.evaluate(AE))
        pg2.keyboard.press('Escape'); pg2.wait_for_timeout(500)
        check('stacked: closing the sheet returns focus to the book', pg2.evaluate(IN('.stk-book')) and pg2.evaluate("document.querySelector('.stk-book').inert!==true"), pg2.evaluate(AE))
        pg2.keyboard.press('Escape'); pg2.wait_for_timeout(600)
        check('stacked: closing the book returns focus to opener, page live', 'Sticker book' in (pg2.evaluate(AE) or '') and pg2.evaluate("document.getElementById('app').inert!==true"), pg2.evaluate(AE))
        # double open
        pg2.evaluate("window.__stickers.openBook();window.__stickers.openBook()"); pg2.wait_for_timeout(900)
        check('double openBook gives exactly one dialog', pg2.evaluate("document.querySelectorAll('.stk-book').length")==1)
        pg2.keyboard.press('Escape'); pg2.wait_for_timeout(500)
        # ---- teacher PIN typed with a keyboard
        pg3 = new_ctx(b); make_learner(pg3)
        pg3.evaluate("async()=>{const {db}=await import(window.__mod('db'));await db.setting('mode','school');await db.setting('teacherPin','1234');await db.setting('activeProfile',null)}"); pg3.goto(BASE + '?skiponb'); pg3.wait_for_timeout(2000)
        click(pg3, "button:has-text('Teacher')")
        pg3.wait_for_selector('.gate-sheet', timeout=4000) if pg3.query_selector('.gate-sheet') else None
        res.append({'name': 'info: teacher gate', 'ok': True, 'detail': 'gate sheet present' if pg3.query_selector('.gate-sheet') else 'PIN field'})
        if pg3.query_selector('input[type=password]'):
            pg3.focus('input[type=password]'); pg3.keyboard.type('1234', delay=60)
            check('PIN field accepts typed digits and Enter unlocks', pg3.evaluate("document.querySelector('input[type=password]').value")=='1234')
            pg3.keyboard.press('Enter'); pg3.wait_for_timeout(1500)
            check('Enter on PIN opens teacher mode', not pg3.query_selector('input[type=password]'))
        errs = pg.errs + pg2.errs + pg3.errs
        check('no page errors', not errs, errs[:3])
        b.close()
    json.dump(res, open(f'{OUT}/kb_checks.json', 'w'), indent=1)
    bad = [r for r in res if not r['ok']]; print(f"\n{len(res)-len(bad)}/{len(res)} passed"); sys.exit(1 if bad else 0)
run()
