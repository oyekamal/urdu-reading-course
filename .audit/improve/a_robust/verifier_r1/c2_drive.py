from common import *
from d1_helpers import *
from t1_teacher import setup, unlock, tab
reqs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b); pg.on('request', lambda r: reqs.append(r.url))
    onboard_child(pg,'Zara'); pg.wait_for_timeout(1500)
    do_rules(pg); click(pg,'.cel-go'); pg.wait_for_timeout(900)
    for _ in range(2): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
    pg.wait_for_selector('.celebrate', timeout=8000); click(pg,'.cel-back, .cel-go'); pg.wait_for_timeout(700)
    for k in ['review','read','me','today']: nav(pg,k)
    nav(pg,'me')
    # sticker book
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Sticker book|sticker/i.test(b.innerText))?.click()"); pg.wait_for_timeout(1200); print('sticker overlay:', pg.query_selector('.stk-ov, .stk-head') is not None)
    pg.evaluate("()=>document.querySelector('.stk-back')?.click()"); pg.wait_for_timeout(400)
    # practice overlay + download + share
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Open practice sheets/i.test(b.innerText))?.click()"); pg.wait_for_timeout(1500)
    print('practice overlay:', pg.query_selector('.pr-ov') is not None)
    try:
        with pg.expect_download(timeout=8000) as dl: pg.evaluate("()=>document.querySelector('.pr-ov a.btn')?.click()")
        print('pdf download ok:', dl.value.suggested_filename)
    except Exception as e: print('pdf download:', str(e)[:80])
    pg.evaluate("()=>document.querySelector('.pr-ov .pr-act button')?.click()"); pg.wait_for_timeout(1200)
    pg.evaluate("()=>document.querySelector('.pr-back')?.click()"); pg.wait_for_timeout(300)
    # backup export
    with pg.expect_download(timeout=8000) as dl:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Export backup/.test(b.innerText)).click()"); gate_pass(pg)
    print('backup download ok:', dl.value.suggested_filename)
    # onboarding share card (canvas)
    print('csp learner drive:', csp(pg), pg._errs)
    ctx.close()
    # teacher drive
    ctx,pg=newpage(b); pg.on('request', lambda r: reqs.append(r.url)); setup(pg); unlock(pg)
    for t in ['Class','Lesson','Groups','Assess','Reports','Device']: tab(pg,t)
    tab(pg,'Lesson'); pg.evaluate("()=>document.querySelector('.card .btn-play, .card button.btn')?.click()"); pg.wait_for_timeout(500)
    tab(pg,'Reports')
    with pg.expect_download(timeout=8000) as dl:
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Export CSV').click()"); gate_pass(pg)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Share slip')?.click()"); pg.wait_for_timeout(500)
    tab(pg,'Assess'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Start assessment/.test(b.innerText))?.click()"); pg.wait_for_timeout(1200)
    print('EGRA screen:', pg.inner_text('#app')[:70].replace('\n',' | '))
    print('csp teacher drive:', csp(pg), pg._errs)
    ctx.close(); b.close()
ext=[u for u in reqs if not u.startswith(BASE) and not u.startswith('data:') and not u.startswith('blob:')]
print('requests total', len(reqs), 'leaving origin:', ext[:5])
