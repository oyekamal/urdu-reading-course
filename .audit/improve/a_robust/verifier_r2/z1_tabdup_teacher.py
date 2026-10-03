from common import *
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1200)
    pg.evaluate("async()=>{await __put('settings',{key:'mode',value:'school'}); await __put('settings',{key:'teacherPin',value:'1234'}); await __put('profiles',{id:'t1',kind:'learner',name:'Child',track:'child',grade:2,createdAt:1})}"); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Teacher/.test(b.innerText))?.click()"); pg.wait_for_timeout(400)
    pg.fill('input[type=password]', '1234'); pg.evaluate("[...document.querySelectorAll('button')].find(b=>/Unlock/.test(b.innerText)).click()"); pg.wait_for_timeout(1200)
    for t in ['Groups', 'Class', 'Reports']:
        pg.evaluate("t=>[...document.querySelectorAll('.tab')].find(x=>x.innerText==='Reports'||x.innerText==='Groups'||x.innerText==='Class').click()", t)
        pg.wait_for_timeout(500)
        pg.dblclick(f".tab:text-is('{t}')"); pg.wait_for_timeout(1500)
        print(t, 'h2 count', pg.evaluate("[...document.querySelectorAll('#app h2')].map(h=>h.innerText)"))
    b.close()
