# Gate test: the grown-up gate (src/gate.js) works and Email / Copy address / Support (bank) / Reset / Export are all behind it.
# Usage: python3 tools/gate_test.py [port]     (dev server: npx vite --port 5188)
import sys, os, re
from playwright.sync_api import sync_playwright
PORT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('PORT', '5188')
BASE = f'http://localhost:{PORT}/'
ONES = {w: i for i, w in enumerate('zero one two three four five six seven eight nine'.split())}
TEENS = {w: 10 + i for i, w in enumerate('ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split())}
TENS = {w: 10 * i for i, w in enumerate('zero ten twenty thirty forty fifty sixty seventy eighty ninety'.split()) if i > 1}
def num(words):
    if words in TEENS: return TEENS[words]
    a, _, b = words.partition('-'); return TENS[a] + (ONES[b] if b else 0)
fails = []
def check(name, cond, extra=''):
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + str(extra) if extra and not cond else ''))
    if not cond: fails.append(name)

with sync_playwright() as p:
    import glob
    try: b = p.chromium.launch()
    except Exception:  # installed browser build differs from this playwright version: use the newest one on disk
        exe = sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')))[-1]; b = p.chromium.launch(executable_path=exe)
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, accept_downloads=True); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.add_init_script("""window.__calls={prompt:0,confirm:0,alert:0,open:[],anchor:0};
      window.prompt=()=>{window.__calls.prompt++;return null};window.confirm=()=>{window.__calls.confirm++;return false};window.alert=()=>{window.__calls.alert++};
      window.open=(u)=>{window.__calls.open.push(String(u));return null};
      HTMLAnchorElement.prototype.click=function(){window.__calls.anchor++};
      Object.defineProperty(navigator,'clipboard',{value:{writeText:async t=>{window.__clip=t}},configurable:true});""")
    click = lambda sel: pg.evaluate('e=>e.click()', pg.wait_for_selector(sel, timeout=8000))
    pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1800); click('text=Just me'); pg.wait_for_timeout(300)
    click('text=+ Add a learner'); pg.wait_for_timeout(300); pg.fill('input[placeholder=Name]', 'Sam'); pg.select_option('select >> nth=0', 'adult'); click("button:has-text('Start')"); pg.wait_for_timeout(1500)
    click(".bottom button[data-k='more']"); pg.wait_for_timeout(800)
    calls = lambda: pg.evaluate('window.__calls')
    shown = lambda: pg.evaluate("!!document.querySelector('.gate-sheet')")
    target = lambda: num(pg.inner_text('.gate-en').strip())
    check('window.__gate exported', pg.evaluate("typeof window.__gate?.askGrownup==='function'"))
    # 1. each action opens the gate and does nothing before it is passed
    actions = {
        'Email Kamal': "button:has-text('Email Kamal')", 'Copy email address': "button:has-text('Copy email address')",
        'Support Urdu Qaida': "button:has-text('Support Urdu Qaida')", 'Reset progress': "button:has-text('Reset this profile')",
        'Export backup': "button:has-text('Export backup')"}
    effect_before = lambda: pg.evaluate("({addr:!document.querySelector('.contact-addr').hidden, donate:!document.querySelector('.donate-card').hidden, open:window.__calls.open.length, anchor:window.__calls.anchor, clip:window.__clip||null})")
    for name, sel in actions.items():
        pg.evaluate('e=>e.scrollIntoView()', pg.wait_for_selector(sel)); click(sel); pg.wait_for_timeout(250)
        check(f'{name}: gate sheet opens', shown())
        e = effect_before(); check(f'{name}: nothing happened before the gate', not e['addr'] and not e['donate'] and e['open'] == 0 and e['anchor'] == 0 and e['clip'] is None, e)
        a11y = pg.evaluate("(()=>{const d=document.querySelector('.gate-sheet');const i=d.querySelector('input');return d.getAttribute('role')==='dialog'&&d.getAttribute('aria-modal')==='true'&&!!document.querySelector('label[for='+i.id+']')&&i.inputMode==='numeric'})()")
        check(f'{name}: role=dialog, aria-modal, labelled numeric input', a11y)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300); check(f'{name}: Escape closes, still nothing happened', not shown() and effect_before()['open'] == 0 and not effect_before()['donate'])
    # 2. wrong number does not open; correct one does; keyboard only
    click(actions['Support Urdu Qaida']); pg.wait_for_timeout(250)
    ur = pg.inner_text('.gate-ur'); check('number is spelled in Urdu words', bool(re.search(r'[؀-ۿ]{2,}', ur)) and not re.search(r'\d', ur), ur)
    n1 = target(); wrong = str(n1 + 1 if n1 < 98 else n1 - 1)
    pg.focus('.gate-input'); pg.keyboard.type(wrong); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    check('wrong number: gate stays, card hidden', shown() and not effect_before()['donate'])
    check('wrong number: message is calm and a new number is shown', 'not it' in pg.inner_text('.gate-msg') and pg.input_value('.gate-input') == '')
    n2 = target(); pg.keyboard.type(str(n2)); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    check('correct number (keyboard only: type + Enter): gate closes and bank card opens', not shown() and effect_before()['donate'])
    txt = pg.inner_text('.donate-card')
    check('bank details shown', all(s in txt for s in ['HBL', 'MUHAMMAD KAMAL', '22927917193503', 'PK64HABB0022927917193503', 'NUST Branch, Islamabad']), txt[:200])
    check('no phone/Easypaisa/ElevenLabs text anywhere on page', not re.search(r'0336|easypaisa|eleven ?labs|wa\.me', pg.inner_text('body'), re.I))
    pg.evaluate('e=>e.click()', pg.query_selector("button[aria-label='Copy IBAN']")); pg.wait_for_timeout(200)
    check('Copy IBAN copies the IBAN (donate card is behind the gate, copy needs no second gate)', pg.evaluate('window.__clip') == 'PK64HABB0022927917193503')
    # 3. Email Kamal after the gate: mailto + address text; Copy address
    click(actions['Email Kamal']); pg.wait_for_timeout(250); pg.keyboard.type(str(target())); pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
    o = calls()['open']; check('Email opens mailto with subject only after gate', any(u == 'mailto:oyekamalkhan@gmail.com?subject=Urdu%20Qaida' for u in o), o)
    check('address shown as text', 'oyekamalkhan@gmail.com' in pg.inner_text('.contact-addr'))
    click(actions['Copy email address']); pg.wait_for_timeout(250); pg.keyboard.type(str(target())); pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
    check('Copy address copies the email after the gate', pg.evaluate('window.__clip') == 'oyekamalkhan@gmail.com')
    # 4. Export after gate
    pg.evaluate('e=>e.scrollIntoView()', pg.wait_for_selector(actions['Export backup'])); click(actions['Export backup']); pg.wait_for_timeout(250)
    check('Export: no download before the gate', calls()['anchor'] == 0)
    pg.keyboard.type(str(target())); pg.keyboard.press('Enter'); pg.wait_for_function('window.__calls.anchor>0', timeout=6000) if True else 0
    check('Export: download happens after the gate', calls()['anchor'] >= 1, calls())
    # 5. Reset after gate: deletes (toast Reset) only after it
    click(actions['Reset progress']); pg.wait_for_timeout(250); pg.keyboard.type('00'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    check('Reset: wrong number does not reset', shown() and 'Reset' not in (pg.inner_text('.toast') if pg.query_selector('.toast.show') else ''))
    pg.keyboard.type(str(target())); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    check('Reset: correct number runs the reset', 'Reset' in pg.inner_text('.toast'), pg.inner_text('.toast'))
    # 5b. import is gated too, and the try counter survives a reload (no brute force by restarting)
    pg.evaluate("localStorage.removeItem('urdu-gate-lock');localStorage.removeItem('urdu-gate-tries')")
    click(".bottom button[data-k='more']"); pg.wait_for_timeout(600)
    pg.evaluate('e=>e.scrollIntoView()', pg.wait_for_selector("button:has-text('Restore from a backup')")); click("button:has-text('Restore from a backup')"); pg.wait_for_timeout(250)
    check('Import backup: gate opens before any file picker', shown())
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    for i in range(2):
        click(actions['Email Kamal']); pg.wait_for_timeout(200); n = target(); pg.keyboard.type('11' if n != 11 else '12'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    pg.reload(); pg.wait_for_timeout(1800)
    click(".bottom button[data-k='more']"); pg.wait_for_timeout(800)
    pg.evaluate('e=>e.scrollIntoView()', pg.wait_for_selector(actions['Email Kamal'])); click(actions['Email Kamal']); pg.wait_for_timeout(250)
    n = target(); pg.keyboard.type('11' if n != 11 else '12'); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    check('2 wrong + reload + 1 wrong still locks out (counter persists)', pg.evaluate("document.querySelector('.gate-input').disabled"))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200); pg.evaluate("localStorage.removeItem('urdu-gate-lock');localStorage.removeItem('urdu-gate-tries')")
    # 6. focus trap
    click(".bottom button[data-k='more']"); pg.wait_for_timeout(800); pg.evaluate('e=>e.scrollIntoView()', pg.wait_for_selector(actions['Support Urdu Qaida'])); click(actions['Support Urdu Qaida'])
    pg.wait_for_timeout(250)
    seq = []
    for _ in range(6):
        seq.append(pg.evaluate("document.activeElement.closest('.gate-sheet')?1:0")); pg.keyboard.press('Tab')
    check('focus trap: Tab never leaves the dialog', all(seq), seq)
    pg.keyboard.press('Shift+Tab'); check('focus trap: Shift+Tab stays inside', pg.evaluate("!!document.activeElement.closest('.gate-sheet')"))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    # 7. lockout after 3 wrong tries (and randomness)
    click(actions['Email Kamal']); pg.wait_for_timeout(250); seen = set()
    for i in range(3):
        n = target(); seen.add(n); pg.focus('.gate-input'); pg.keyboard.type('11' if n != 11 else '12'); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    check('3 wrong tries: input disabled, calm lockout message', pg.evaluate("document.querySelector('.gate-input').disabled") and 'pause' in pg.inner_text('.gate-msg').lower(), pg.inner_text('.gate-msg'))
    check('lockout says about 30 seconds', re.search(r'(29|30) seconds', pg.inner_text('.gate-msg')) is not None, pg.inner_text('.gate-msg'))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    click(actions['Email Kamal']); pg.wait_for_timeout(300)
    check('re-opening during lockout is still locked (no bypass by closing)', pg.evaluate("document.querySelector('.gate-input').disabled"))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    # new random number each time: check via __gate API after clearing the lock
    pg.evaluate("localStorage.removeItem('urdu-gate-lock');localStorage.removeItem('urdu-gate-tries')")
    nums = set()
    for _ in range(6):
        click(actions['Email Kamal']); pg.wait_for_timeout(200); nums.add(pg.inner_text('.gate-en')); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    check('number is random each time', len(nums) >= 3, nums)
    check('no window.prompt/confirm/alert was ever called', calls()['prompt'] == 0 and calls()['confirm'] == 0 and calls()['alert'] == 0, calls())
    check('no page errors', not errs, errs)
    b.close()
print('\nRESULT:', 'ALL PASS' if not fails else f'{len(fails)} FAILED: {fails}')
sys.exit(1 if fails else 0)
