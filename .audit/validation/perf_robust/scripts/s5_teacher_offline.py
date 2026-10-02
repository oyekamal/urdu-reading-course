from h import *
BASE='http://localhost:5302/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE,args=['--no-sandbox']); ctx=b.new_context(viewport=VP); pg=ctx.new_page(); fails=[]
    pg.on('dialog', lambda d: d.accept('5'))
    pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(9000)
    ctx.set_offline(True); pg.on('requestfailed', lambda r: fails.append(r.url.replace(BASE,'')))
    pg.reload(); pg.wait_for_timeout(2000)
    click(pg,'text=My class'); pg.wait_for_timeout(500)
    pg.fill('input[placeholder="Your name"]','T'); pg.fill('input[placeholder="4-digit PIN"]','1234'); click(pg,"button:has-text('Save')"); pg.wait_for_timeout(800)
    click(pg,"button:has-text('Teacher')"); pg.wait_for_timeout(500); pg.fill('input[type=password]','1234'); click(pg,"button:has-text('Unlock')"); pg.wait_for_timeout(2500)
    print('teacher screen text:', pg.inner_text('#app')[:150].replace('\n',' | ')); print('fails', fails)
    pg.screenshot(path=OUT+'/s5_teacher_offline.png'); b.close()
