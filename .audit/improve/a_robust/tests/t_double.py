# Double / triple activation: every primary action advances exactly once. Production build (5311) unless noted.
from common import *
RES = []
def chk(name, ok, extra=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name, extra)
def multi(pg, sel, n=3):
    pg.evaluate("([s,n])=>{const b=document.querySelector(s); for(let i=0;i<n;i++) b.click()}", [sel, n])
def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        # 1. onboarding: triple tap on the colour CTA and on later CTAs
        ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2200)
        click(pg, "text=Let's begin"); pg.wait_for_timeout(500); click(pg, '.ob-sleeper'); pg.wait_for_timeout(2800)
        multi(pg, '.ob-cta', 3); pg.wait_for_timeout(900)
        onb = pg.evaluate("__dump().then(d=>d.settings.find(s=>s.key==='onb').value)")
        chk('onboarding colour CTA x3 -> exactly one step (i == 3, Who is learning?)', onb['i'] == 3, onb['i'])
        print('  screen:', pg.inner_text('.ob')[:40].replace('\n', ' '))
        click(pg, ".ob-opt:has-text('My child')"); pg.wait_for_timeout(1700)
        chk('Who answered, name screen next', pg.query_selector('#ob-name') is not None)
        pg.fill('#ob-name', 'Zed'); pg.wait_for_timeout(300)
        multi(pg, '.ob-cta', 3); pg.wait_for_timeout(900)
        onb = pg.evaluate("__dump().then(d=>d.settings.find(s=>s.key==='onb').value)")
        chk('name CTA x3 -> one step (goal screen, i == 5)', onb['i'] == 5, onb['i'])
        ctx.close()
        # 2. option double tap on a single-select answer
        ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(2200)
        click(pg, "text=Let's begin"); pg.wait_for_timeout(500); click(pg, '.ob-sleeper'); pg.wait_for_timeout(2800); click(pg, '.ob-cta'); pg.wait_for_timeout(600)
        pg.evaluate("()=>{const o=[...document.querySelectorAll('.ob-opt')].find(x=>/My child/.test(x.innerText)); o.click(); o.click(); o.click()}"); pg.wait_for_timeout(2200)
        onb = pg.evaluate("__dump().then(d=>d.settings.find(s=>s.key==='onb').value)")
        chk('single-select option x3 -> one step (name screen i == 4)', onb['i'] == 4, onb['i'])
        ctx.close()
        # 3. add learner Start x3 -> exactly one profile
        ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1500)
        click(pg, 'text=Just me'); pg.wait_for_timeout(400); click(pg, 'text=+ Add a learner'); pg.wait_for_timeout(400)
        pg.fill('input[placeholder=Name]', 'Dup')
        pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Start'); b.click(); b.click(); b.click()}"); pg.wait_for_timeout(2500)
        c, d = counts(pg); chk('Add learner Start x3 -> one profile', c['profiles'] == 1, c['profiles'])
        # 4. lesson Continue x3 advances one screen; finishing x3 awards exactly one pearl; celebration button x3 -> one next lesson
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
        w0 = pg.evaluate("document.querySelector('.progress i')?.style.width")
        multi(pg, '.lesson .btn-primary', 3); pg.wait_for_timeout(700)
        w1 = pg.evaluate("document.querySelector('.progress i')?.style.width")
        chk('lesson Continue x3 -> one screen (33%)', w1 == '33%', f'{w0}->{w1}')
        pg.wait_for_timeout(500); multi(pg, '.lesson .btn-primary', 3); pg.wait_for_timeout(700)
        w2 = pg.evaluate("document.querySelector('.progress i')?.style.width"); chk('second Continue x3 -> 67%', w2 == '67%', w2)
        pg.wait_for_timeout(500); multi(pg, '.lesson .btn-primary', 3); pg.wait_for_selector('.celebrate', timeout=8000); pg.wait_for_timeout(1500)
        c, d = counts(pg); lessons = [list((x.get('units') or {}).get('0', {}).get('lessons', {}).keys()) for x in d['progress']]
        chk('finish x3 -> exactly one pearl', lessons == [['rules']], lessons)
        print('  celebrations:', pg.evaluate("document.querySelectorAll('.celebrate').length"))
        chk('exactly one celebration overlay', pg.evaluate("document.querySelectorAll('.celebrate').length") == 1)
        multi(pg, '.cel-go', 3); pg.wait_for_timeout(1200)
        chk('celebration Next x3 -> one lesson opened (lesson 2 of 2)', 'lesson 2 of 2' in pg.inner_text('#app'), pg.inner_text('#app')[:60].replace('\n', ' | '))
        chk('no leftover celebration', pg.evaluate("document.querySelectorAll('.celebrate').length") == 0)
        ctx.close()
        # 5. review grading: three due cards, Got it x3 on the first card
        ctx, pg = newpage(b); quick_profile(pg, 'Rev')
        pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        pg.evaluate("""p=>Promise.all(['ا','ب','ک'].map(c=>__put('cards',{id:p+':'+c,profileId:p,item:c,kind:'letter',box:1,due:1,seen:0})))""", pid)
        pg.reload(); pg.wait_for_timeout(2000); nav(pg, 'review'); pg.wait_for_timeout(500)
        pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Got it'); b.click(); b.click(); b.click()}"); pg.wait_for_timeout(800)
        ctr = pg.inner_text('#app'); chk('review Got it x3 -> second card shown (2 / 3), one card graded', '2 / 3' in ctr, re.findall(r'\d / 3', ctr))
        c, d = counts(pg); graded = [x for x in d['cards'] if x.get('seen')]; chk('exactly one card graded', len(graded) == 1, len(graded))
        pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Not yet'); b.click(); b.click(); b.click()}"); pg.wait_for_timeout(2200)
        c, d = counts(pg); graded = [x for x in d['cards'] if x.get('seen')]; chk('Not yet x3 -> exactly two cards graded', len(graded) == 2, len(graded))
        print('  errors', pg._errs); ctx.close(); b.close()
    print('RESULT', 'PASS' if all(RES) else 'FAIL', f'{sum(RES)}/{len(RES)}')
main()
