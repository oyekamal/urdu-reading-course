from common import *
from t1_teacher import tab, unlock
PAY='"><img src=x onerror=window.__xss=1><svg onload=window.__xss=1>'
with sync_playwright() as p:
    b=p.chromium.launch()
    # onboarding with payload name, scan each step
    ctx,pg=newpage(b); onboard_child(pg,PAY); pg.wait_for_timeout(1500)
    print('onboarding name payload -> inert:', inert(pg)[:2], 'xss', pg.evaluate('window.__xss'), 'name', pg.evaluate("__dump().then(d=>d.profiles.map(p=>p.name))"), 'csp', csp(pg)[:1], pg._errs[:1])
    ctx.close()
    # teacher: add child + edit (prompt) with payload
    ctx,pg=newpage(b)
    pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1200)
    pg.evaluate("__put('settings',{key:'mode',value:'school'}); __put('settings',{key:'teacherPin',value:'1234'})"); pg.reload(); pg.wait_for_timeout(1500); unlock(pg)
    pg.fill('input[placeholder=Name]', PAY); pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Add child').click()"); pg.wait_for_timeout(1200)
    print('teacher add child:', pg.evaluate("__dump().then(d=>d.profiles.map(p=>p.name))"), inert(pg)[:2])
    pg.remove_listener('dialog', pg.listeners('dialog')[0]) if False else None
    ctx.close()
    b.close()
