# Full drive on the PRODUCTION build: onboarding with an XSS name, lessons, tabs, stickers, practice PDFs, audio. Expect: 0 CSP violations, 0 XSS.
from common import *
PAY = '<img src=x onerror=alert(1)>'
def probe(pg, label):
    r = pg.evaluate("""()=>({xss: window.__xss, alerts: window.__alerts, img: document.querySelectorAll('img[src="x"], [onerror]').length, sw: document.documentElement.scrollWidth, iw: innerWidth})""")
    print(label, r); return r
def bad_of(r): return (r['xss'] or 0) + (r['alerts'] or 0) + (r['img'] or 0)
def main():
    bad = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx, pg = newpage(b); onboard_child(pg, PAY)
        bad += bad_of(probe(pg, 'after onboarding'))
        print('Today header:', pg.inner_text('.home-hero h1')[:80])
        do_rules(pg); click(pg, '.cel-back, .cel-go'); pg.wait_for_timeout(700)
        bad += bad_of(probe(pg, 'after lesson'))
        for k in ['review', 'read', 'me', 'today']:
            nav(pg, k); bad += bad_of(probe(pg, 'tab ' + k))
        nav(pg, 'me')
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Sticker book/.test(b.innerText))?.click()"); pg.wait_for_timeout(900); probe(pg, 'stickers')
        pg.evaluate("()=>document.querySelector('.stk-back')?.click()"); pg.wait_for_timeout(400)
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/practice/i.test(b.innerText))?.click()"); pg.wait_for_timeout(1500); probe(pg, 'practice')
        pg.evaluate("()=>document.querySelector('.pr-back')?.click()"); pg.wait_for_timeout(300)
        nav(pg, 'today'); pg.wait_for_timeout(600)
        v = csp(pg); print('CSP violations:', v); print('page errors:', pg._errs)
        c, d = counts(pg); print('stored profile name:', [x['name'] for x in d['profiles']])
        bad += len(v)
        ctx.close()
        ctx, pg = newpage(b); quick_profile(pg, PAY)
        bad += bad_of(probe(pg, 'add-learner payload'))
        print('Today header:', pg.inner_text('.home-hero h1')[:80])
        ctx.close()
        # payload written straight into the DB (legacy / tampered data), every screen
        ctx, pg = newpage(b); quick_profile(pg, 'Amal')
        pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        pg.evaluate("""p=>__put('profiles',{id:p,kind:'learner',name:'<img src=x onerror=alert(1)>',track:'child',grade:'<img src=x onerror=alert(1)>',avatar:'#fff" onmouseover="alert(1)',createdAt:1})""", pid)
        pg.reload(); pg.wait_for_timeout(2000)
        for k in ['today', 'review', 'read', 'me']:
            nav(pg, k); bad += bad_of(probe(pg, 'tampered tab ' + k))
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Switch profile/.test(b.innerText))?.click()"); pg.wait_for_timeout(800)
        bad += bad_of(probe(pg, 'tampered picker'))
        print('picker html has onmouseover:', pg.evaluate("document.body.innerHTML.includes('onmouseover')"))
        ctx.close(); b.close()
    print('RESULT', 'FAIL' if bad else 'PASS', 'bad=', bad)
main()
