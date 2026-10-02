import json, sys, time, os, re
from h import *
from s6_data import newpage, counts, nav, do_rules
BASE = 'http://localhost:5301/'
CLOCK = "(()=>{const D=Date;const off=()=>+(localStorage.getItem('__off')||0);class F extends D{constructor(...a){if(a.length)super(...a);else super(D.now()+off())}static now(){return D.now()+off()}}window.Date=F;})()"
def T(name, fn):
    print(f'\n=== {name}'); 
    try: fn()
    except Exception as e: print('TEST ERROR', str(e)[:300])
def main():
  with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
    # ---- 1. two children isolation + switch mid-lesson
    def t1():
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Amal')
        do_rules(pg); pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(700)
        nav(pg, 'me'); pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Switch profile/.test(b.innerText)).click()"); pg.wait_for_timeout(800)
        click(pg, "text=+ Add a learner"); pg.fill('input[placeholder=Name]', 'Bina'); click(pg, "button:has-text('Start')"); pg.wait_for_timeout(1500)
        txt = pg.inner_text('#app'); print('Bina Today shows pearls:', re.findall(r'(\d+)\s*\n?pearls', txt), '| streak chip:', re.findall(r'(First day today|\d+ days?[^\n]*)', txt)[:1])
        # start a lesson as Bina, advance, switch to Amal mid-lesson
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(700); pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(400)
        nav(pg, 'me'); pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Switch profile/.test(b.innerText)).click()"); pg.wait_for_timeout(500)
        pg.evaluate("()=>[...document.querySelectorAll('button.card')].find(b=>/Amal/.test(b.innerText)).click()"); pg.wait_for_timeout(2500)
        c, d = counts(pg); prof = {x['id']: x['name'] for x in d['profiles']}
        print('progress rows by profile:', {prof.get(r['id'], r['id']): {k: list((v or {}).keys()) if k in ('units',) else v for k, v in r.items() if k in ('units', 'sessions')} for r in d['progress']})
        print('attempts by profile:', {prof.get(k): sum(1 for a in d['attempts'] if a['profileId'] == k) for k in prof}, 'cards:', {prof.get(k): sum(1 for a in d['cards'] if a['profileId'] == k) for k in prof}, 'sessions rows:', len(d['sessions']))
        print('settings keys:', [s['key'] for s in d['settings']]); print('errors', pg._errs)
        print('Amal Today pearls text:', re.findall(r'(\d+)\s*\n?pearls', pg.inner_text('#app')))
        ctx.close()
    T('two children / switch mid-lesson', t1)
    # ---- 2. double tap
    def t2():
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Amal'); click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(700)
        h0 = pg.inner_text('.lesson h1') if pg.query_selector('.lesson h1') else ''
        before = pg.evaluate("document.querySelector('.progress i')?.style.width")
        pg.evaluate("()=>{const b=document.querySelector('.lesson .btn-primary');b.click();b.click()}"); pg.wait_for_timeout(700)
        after = pg.evaluate("document.querySelector('.progress i')?.style.width"); print('Continue double-click: progress', before, '->', after, '(single click would be ~33%)')
        pg.evaluate("()=>{const b=document.querySelector('.lesson .btn-primary');b&&(b.click(),b.click())}"); pg.wait_for_timeout(1500)
        print('after 2nd double-click, celebrate?', pg.query_selector('.celebrate') is not None)
        pg.wait_for_timeout(1500); c, d = counts(pg); print('rows', c); pr = d['progress']; print('lessons marked:', [list((x.get('units') or {}).get('0', {}).get('lessons', {}).keys()) for x in pr])
        # onboarding CTA double click
        ctx2, pg2 = newpage(b); pg2.goto(BASE); pg2.wait_for_timeout(2000); click(pg2, "text=Let's begin"); pg2.wait_for_timeout(600)
        s0 = pg2.evaluate("document.querySelector('.ob')?.innerText.slice(0,40)")
        pg2.evaluate("()=>{const b=document.querySelector('.ob-cta,.ob-foot .btn');b.click();b.click()}"); pg2.wait_for_timeout(800)
        onb = pg2.evaluate("__dump().then(d=>d.settings.find(s=>s.key==='onb'))"); print('onboarding: after double-click on first CTA, saved step i =', onb and onb['value']['i'], '(single click => 2: welcome=0 wake=1... )')
        # kill mid-onboarding and resume
        pg2.reload(); pg2.wait_for_timeout(2000); print('after reload, onboarding screen starts with:', pg2.evaluate("document.querySelector('.ob')?.innerText.slice(0,50)").replace('\n', ' '))
        ctx.close(); ctx2.close()
    T('double-tap + resume', t2)
    # ---- 3. kill mid-lesson
    def t3():
        ctx, pg = newpage(b); quick_profile(pg, BASE, 'Amal'); click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(600); pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
        pg.reload(); pg.wait_for_timeout(2500); print('after kill mid-lesson shows:', pg.inner_text('#app')[:70].replace('\n', ' | '), '| sessions rows', counts(pg)[0]['sessions'])
        ctx.close()
    T('kill mid-lesson', t3)
    # ---- 4. XSS / names
    def t4():
        for nm in ['<img src=x onerror="window.__xss=1">', 'A' * 300, '😀👨‍👩‍👧 سارہ', '   ']:
            ctx, pg = newpage(b); pg.on('dialog', lambda d: d.accept()); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200); click(pg, 'text=Just me'); pg.wait_for_timeout(300); click(pg, 'text=+ Add a learner'); pg.fill('input[placeholder=Name]', nm); click(pg, "button:has-text('Start')"); pg.wait_for_timeout(1500)
            ov = pg.evaluate("()=>({xss:window.__xss||0,sw:document.documentElement.scrollWidth,iw:innerWidth,header:document.querySelector('h1')?.innerText.slice(0,40),toast:document.getElementById('toast')?.innerText})")
            print(repr(nm[:25]), '->', ov); pg.screenshot(path=OUT + f'/s7_name_{abs(hash(nm))%1000}.png'); ctx.close()
        # empty name on onboarding: is Continue disabled?
        ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2000); click(pg, "text=Let's begin"); click(pg, '.ob-sleeper'); pg.wait_for_timeout(2600); click(pg, '.ob-sw >> nth=0'); click(pg, '.ob-cta'); click(pg, ".ob-opt:has-text('My child')"); pg.wait_for_timeout(1500)
        print('onboarding name empty: CTA disabled =', pg.evaluate("document.querySelector('.ob-cta').disabled")); pg.fill('#ob-name', '<img src=x onerror="window.__xss=1">'); pg.evaluate("document.querySelector('.ob-cta').click()"); pg.wait_for_timeout(800)
        print('onboarding xss fired on next screen:', pg.evaluate('window.__xss||0'), '| screen:', pg.evaluate("document.querySelector('.ob')?.innerText.slice(0,60)").replace('\n',' '))
        ctx.close()
    T('names/XSS', t4)
    # ---- 5. clock
    def t5():
        ctx, pg = newpage(b, init=CLOCK); quick_profile(pg, BASE, 'Amal'); do_rules(pg); pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(700)
        def chips(): 
            nav(pg, 'today'); return re.sub(r'\s+', ' ', pg.inner_text('.home-scene, #app')[:260])
        print('t0:', chips())
        for off, lab in [(3 * 86400000, '+3 days'), (-5 * 86400000, '-5 days (before first practice)'), (400 * 86400000, '+400 days')]:
            pg.evaluate("o=>localStorage.setItem('__off',o)", off); pg.reload(); pg.wait_for_timeout(2000); print(lab, ':', chips()[:200])
            nav(pg, 'review'); print('   review:', re.sub(r'\s+', ' ', pg.inner_text('#app'))[:110]); 
        c, d = counts(pg); print('errors', pg._errs)
        ctx.close()
    T('clock changes', t5)
    # ---- 6. 1000 / 10000 attempts
    def t6():
        for N in [0, 1000, 10000]:
            ctx, pg = newpage(b); quick_profile(pg, BASE, 'Sam', 'adult')
            pg.evaluate("""async N=>{const pid=(await __dump()).settings.find(s=>s.key==='activeProfile').value;const d=await new Promise(r=>{const q=indexedDB.open('urdu-reader');q.onsuccess=()=>r(q.result)});
              await new Promise(r=>{const t=d.transaction('attempts','readwrite');const s=t.objectStore('attempts');for(let i=0;i<N;i++)s.put({id:'a'+i,profileId:pid,unit:1+i%5,drill:'tap',item:'ابکلمن'[i%6],correct:i%3>0,ms:700,ts:Date.now()-i*60000,updatedAt:Date.now()});t.oncomplete=r});d.close()}""", N)
            pg.reload(); pg.wait_for_timeout(2500)
            cdp = ctx.new_cdp_session(pg); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
            res = {}
            for k in ['progress', 'more', 'today']:
                t0 = time.time(); pg.evaluate("k=>document.querySelector(`.bottom button[data-k='${k}']`).click()", k)
                pg.wait_for_function("()=>document.querySelector('#app')&&document.querySelector('#app').innerText.length>40"); pg.wait_for_timeout(50)
                res[k] = round((time.time() - t0) * 1000)
            print(f'{N} attempts @4x CPU: tab render ms (incl. 50ms wait)', res); ctx.close()
    T('attempts volume', t6)
    b.close()
if __name__ == '__main__': main()
