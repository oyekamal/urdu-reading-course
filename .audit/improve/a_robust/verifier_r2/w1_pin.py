from common import *
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
    pg.evaluate("async()=>{await __put('settings',{key:'mode',value:'school'}); await __put('settings',{key:'teacherPin',value:'1234'}); await __put('profiles',{id:'t1',kind:'learner',name:'Child',track:'child',grade:2,createdAt:1})}"); pg.reload(); pg.wait_for_timeout(1500)
    print('home:', pg.inner_text('#app')[:60].replace('\n', ' | '))
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Change device type/.test(b.innerText)).click()"); pg.wait_for_timeout(800)   # dialog auto-accepted by harness
    print('after change device type:', pg.inner_text('#app')[:60].replace('\n', ' | '))
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/My class/.test(b.innerText)).click()"); pg.wait_for_timeout(800)
    print('after My class:', pg.inner_text('#app')[:80].replace('\n', ' | '))
    pg.fill('input[type=password]', '9999'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Save').click()"); pg.wait_for_timeout(800)
    print('pin now:', {s['key']: s['value'] for s in counts(pg)[1]['settings']}.get('teacherPin'), '| gate asked:', False)
    b.close()
