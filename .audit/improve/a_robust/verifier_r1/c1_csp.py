from common import *
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b); pg.goto(BASE); pg.wait_for_timeout(1500)
    print('meta:', pg.evaluate("document.querySelector('meta[http-equiv=Content-Security-Policy]')?.content"))
    r=pg.evaluate("""async()=>{const out={};
      window.__ran=0;
      const s=document.createElement('script'); s.textContent='window.__ran=1'; document.head.append(s); out.inlineScript=window.__ran;
      const d=document.createElement('div'); d.innerHTML='<img src=x onerror="window.__ran=2">'; document.body.append(d); await new Promise(r=>setTimeout(r,300)); out.imgOnerror=window.__ran;
      const a=document.createElement('a'); a.href='javascript:window.__ran=3'; document.body.append(a); a.click(); out.jsurl=window.__ran;
      try{ out.eval=(0,eval)('1+1') }catch(e){out.eval='blocked: '+e.message.slice(0,40)}
      try{ await fetch('https://example.com/'); out.fetch='ALLOWED' }catch(e){out.fetch='blocked'}
      const f=document.createElement('iframe'); f.src='https://example.com'; document.body.append(f); 
      const sc=document.createElement('script'); sc.src='https://example.com/x.js'; document.head.append(sc);
      const im=document.createElement('img'); im.src='https://example.com/x.png'; document.body.append(im);
      const form=document.createElement('form'); form.action='https://example.com'; document.body.append(form);
      const bs=document.createElement('base'); bs.href='https://evil.example/'; document.head.append(bs);
      await new Promise(r=>setTimeout(r,800)); return out}""")
    print(r)
    print('violations:', pg.evaluate('window.__csp'))
    # drive full app for violations
    ctx2,pg2=newpage(b); onboard_child(pg2,'Zara')
    do_rules(pg2); click(pg2,'.cel-back, .cel-go'); pg2.wait_for_timeout(600)
    for k in ['review','read','me','today']: nav(pg2,k)
    nav(pg2,'me')
    pg2.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Sticker book/.test(b.innerText))?.click()"); pg2.wait_for_timeout(900)
    pg2.evaluate("()=>document.querySelector('.stk-back')?.click()"); pg2.wait_for_timeout(300)
    pg2.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/practice sheets/i.test(b.innerText))?.click()"); pg2.wait_for_timeout(1800)
    print('practice screen:', pg2.inner_text('#app')[:100].replace('\n',' | '))
    # try to open a pdf
    pg2.evaluate("()=>[...document.querySelectorAll('button')].filter(b=>/download|share|open|save/i.test(b.innerText))[0]?.click()"); pg2.wait_for_timeout(1500)
    print('csp during drive:', csp(pg2), pg2._errs)
    b.close()
