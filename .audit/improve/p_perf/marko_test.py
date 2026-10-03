# functional checks for the Marko/motion policy. python3 marko_test.py PORT
import sys, json
from h import *
BASE = f'http://localhost:{sys.argv[1]}/'
INFO = """()=>[...document.querySelectorAll('.marko')].map(m=>{const x=m._marko||{};return {st:x.state,ph:x.phase,ok:x.ok,anim:!!x.anim,paused:!!(x.player&&x.player.paused),running:!!(x.player&&x.player.running),f:x.anim?Math.round(x.anim.currentFrame):null,rest:!!m.querySelector('.marko-rest.on'),still:m.classList.contains('marko-still'),vis:m.getBoundingClientRect().top<844}})"""
res = []
def check(name, ok, extra=''):
    res.append((name, bool(ok))); print(('PASS ' if ok else 'FAIL ') + name, extra)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    ctx = b.new_context(viewport=VP, device_scale_factor=2, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.accept('5'))
    quick_profile(pg, BASE)
    pg.wait_for_timeout(300); pg.evaluate("window.dispatchEvent(new Event('pointerdown'))")
    i = pg.evaluate(INFO); print(i)
    animated = [m for m in i if m['anim']]
    check('exactly one animated Marko on Today', len(animated) == 1, len(animated))
    check('offscreen Marko is a still poster', all(m['still'] for m in i if not m['anim']))
    f0 = pg.evaluate(INFO)[0]['f']; pg.wait_for_timeout(1200); f1 = pg.evaluate(INFO)[0]['f']
    check('awake: frames advance', f0 != f1, (f0, f1))
    # calm
    pg.wait_for_timeout(5500); i = pg.evaluate(INFO)[0]
    check('calm: rest pose shown and player paused', i['rest'] and i['paused'], i)
    check('calm: html.calm set', pg.evaluate("document.documentElement.classList.contains('calm')"))
    pg.evaluate("window.dispatchEvent(new Event('pointerdown'))"); pg.wait_for_timeout(700)
    i = pg.evaluate(INFO)[0]; check('wake: resumed', (not i['paused']) and not i['rest'], i)
    f0 = i['f']; pg.wait_for_timeout(1000); check('wake: frames advance again', pg.evaluate(INFO)[0]['f'] != f0)
    # hidden tab
    pg.evaluate("Object.defineProperty(document,'hidden',{get:()=>true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(300)
    check('hidden tab: paused', pg.evaluate(INFO)[0]['paused'])
    pg.evaluate("Object.defineProperty(document,'hidden',{get:()=>false,configurable:true});document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(300)
    check('visible again: resumed', not pg.evaluate(INFO)[0]['paused'])
    # overlay
    pg.evaluate("document.body.append(Object.assign(document.createElement('div'),{className:'celebrate',id:'tov'}))"); pg.wait_for_timeout(300)
    check('overlay: paused', pg.evaluate(INFO)[0]['paused'] and pg.evaluate("document.documentElement.classList.contains('m-cover')"))
    pg.evaluate("document.getElementById('tov').remove()"); pg.wait_for_timeout(300)
    check('overlay closed: resumed', not pg.evaluate(INFO)[0]['paused'])
    # reaction: poke wakes and plays one-shot
    pg.evaluate("window.dispatchEvent(new Event('pointerdown'))")
    pg.evaluate("document.querySelector('.hh-marko')&&document.querySelector('.hh-marko').click()"); pg.wait_for_timeout(400)
    print(pg.evaluate(INFO)[0])
    # offscreen: scroll away
    pg.evaluate("window.scrollTo(0,99999);document.querySelectorAll('*').forEach(e=>{if(e.scrollHeight>e.clientHeight+50&&getComputedStyle(e).overflowY!='visible')e.scrollTop=99999})"); pg.wait_for_timeout(600)
    print('after scroll', pg.evaluate(INFO))
    # lesson: coach talks while audio plays
    pg.evaluate("document.querySelector(`.bottom button[data-k='today']`)?.click()"); pg.wait_for_timeout(500)
    pg.evaluate("()=>{[...document.querySelectorAll('button')].find(b=>/Start:|Continue:/.test(b.textContent))?.click()}"); pg.wait_for_timeout(1500)
    i = pg.evaluate(INFO); print('lesson markos', i)
    check('lesson: at most one animated', sum(1 for m in i if m['anim']) <= 1)
    check('no page errors', not errs, errs[:3])
    b.close()
print('RESULT', sum(1 for _, o in res if o), '/', len(res))
