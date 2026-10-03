from common import *
import sys
sys.path.insert(0, '../verifier_r1')
reqs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newpage(b); pg.goto(BASE); pg.wait_for_timeout(1500)
    print('meta:', pg.evaluate("document.querySelector('meta[http-equiv=Content-Security-Policy]')?.content")[:60])
    r = pg.evaluate("""async()=>{const out={};
      window.__ran=0;
      const s=document.createElement('script'); s.textContent='window.__ran=1'; document.head.append(s); out.inlineScript=window.__ran;
      const d=document.createElement('div'); d.innerHTML='<img src=x onerror="window.__ran=2">'; document.body.append(d); await new Promise(r=>setTimeout(r,300)); out.imgOnerror=window.__ran;
      const b=document.createElement('button'); b.setAttribute('onclick','window.__ran=4'); document.body.append(b); b.click(); out.onclickAttr=window.__ran;
      try{ out.eval=(0,eval)('1+1') }catch(e){out.eval='blocked'}
      try{ out.fn=new Function('return 2')() }catch(e){out.fn='blocked'}
      try{ await fetch('https://example.com/'); out.fetch='ALLOWED' }catch(e){out.fetch='blocked'}
      const im=document.createElement('img'); im.src='https://example.com/x.png'; document.body.append(im);
      await new Promise(r=>setTimeout(r,800)); return out}""")
    print(r); print('violations:', pg.evaluate('window.__csp'))
    ctx.close()
    ctx, pg = newpage(b); pg.on('request', lambda r: reqs.append(r.url))
    onboard_child(pg, 'Zara'); pg.wait_for_timeout(1500)
    print('after onboarding:', pg.inner_text('#app')[:80].replace('\n', ' | '))
    do_rules(pg); click(pg, '.cel-go'); pg.wait_for_timeout(900)
    for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
    try: pg.wait_for_selector('.celebrate', timeout=8000)
    except Exception as e: print('no cel')
    pg.evaluate("document.querySelector('.cel-go')?.click()"); pg.wait_for_timeout(700)
    for k in ['review', 'read', 'me', 'today']: nav(pg, k)
    nav(pg, 'me')
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/sticker/i.test(b.innerText))?.click()"); pg.wait_for_timeout(1200)
    pg.evaluate("()=>document.querySelector('.stk-back')?.click()"); pg.wait_for_timeout(400)
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/practice/i.test(b.innerText))?.click()"); pg.wait_for_timeout(1500)
    print('practice overlay', pg.query_selector('.pr-ov') is not None)
    try:
        with pg.expect_download(timeout=8000) as dl: pg.evaluate("()=>document.querySelector('.pr-ov a.btn')?.click()")
        print('pdf download', dl.value.suggested_filename)
    except Exception as e: print('pdf dl fail', str(e)[:80])
    pg.evaluate("()=>document.querySelector('.pr-ov .pr-act button')?.click()"); pg.wait_for_timeout(1500)
    pg.evaluate("()=>document.querySelector('.pr-back')?.click()"); pg.wait_for_timeout(300)
    with pg.expect_download(timeout=8000) as dl:
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Export backup/.test(b.innerText)).click()"); gate_pass(pg)
    print('backup dl', dl.value.suggested_filename); open('/tmp/claude-1000/vr2_backup1.json', 'w').write(open(dl.value.path()).read())
    print('csp:', csp(pg), 'errs', pg._errs)
    ctx.close()
    ctx, pg = newpage(b); pg.on('request', lambda r: reqs.append(r.url))
    from t1_teacher import setup, unlock, tab
    setup(pg); unlock(pg)
    for t in ['Class', 'Lesson', 'Groups', 'Assess', 'Reports', 'Device']: tab(pg, t)
    tab(pg, 'Reports')
    with pg.expect_download(timeout=8000) as dl:
        pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Export CSV').click()"); gate_pass(pg)
    pg.evaluate("[...document.querySelectorAll('button')].find(b=>b.innerText==='Share slip')?.click()"); pg.wait_for_timeout(500)
    print('csp teacher:', csp(pg), pg._errs)
    ctx.close(); b.close()
ext = [u for u in reqs if not u.startswith(BASE) and not u.startswith('data:') and not u.startswith('blob:')]
print('requests', len(reqs), 'off-origin', ext[:5])
