import json, collections
from urllib.parse import urlparse
from h import *
from s6_data import newpage, nav, do_rules
BASE='http://localhost:5301/'
hosts=collections.Counter(); ext=[]; cons=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE,args=['--no-sandbox'])
    def hook(ctx,pg):
        ctx.on('request',lambda r:(hosts.update([urlparse(r.url).netloc or r.url[:20]]),None) if True else None)
        ctx.on('request',lambda r: ext.append(r.url) if urlparse(r.url).netloc not in ('localhost:5301',) and not r.url.startswith('data:') and not r.url.startswith('blob:') else None)
        pg.on('console',lambda m: cons.append((m.type,m.text[:160])) if m.type in('error','warning') else None)
        pg.on('pageerror',lambda e: cons.append(('pageerror',str(e)[:160])))
    # child
    ctx,pg=newpage(b); hook(ctx,pg); quick_profile(pg,BASE,'Zara'); do_rules(pg); pg.evaluate("()=>(document.querySelector('.cel-back')||document.querySelector('.cel-go')).click()"); pg.wait_for_timeout(600)
    for k in ['review','read','me','today']: nav(pg,k)
    pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Sticker book/.test(b.innerText))?.click()"); pg.wait_for_timeout(1500)
    # external links behind gate? click WhatsApp with wrong answer (prompt answers '5' -> likely wrong) and count window.open calls
    nav(pg,'me'); pg.evaluate("window.__opens=[];window.open=(u)=>{window.__opens.push(u)}")
    pg.on('dialog',lambda d: None)
    for label in ['WhatsApp Kamal','Donate to keep it free']:
        pg.evaluate("l=>[...document.querySelectorAll('button')].find(b=>b.innerText.includes(l))?.click()",label); pg.wait_for_timeout(300)
    print('opens after wrong gate answers (prompt returned "5"):', pg.evaluate('window.__opens'), '| toast:', pg.evaluate("document.getElementById('toast')?.innerText"))
    ctx.close()
    # teacher
    ctx,pg=newpage(b); hook(ctx,pg); pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1500); click(pg,'text=My class'); pg.fill('input[placeholder="Your name"]','T'); pg.fill('input[placeholder="4-digit PIN"]','1234'); click(pg,"button:has-text('Save')"); pg.wait_for_timeout(600)
    click(pg,"button:has-text('Teacher')"); pg.fill('input[type=password]','1234'); click(pg,"button:has-text('Unlock')"); pg.wait_for_timeout(2500); print('teacher view:', pg.inner_text('#app')[:60].replace('\n',' | '))
    ctx.close(); b.close()
print('request hosts:',dict(hosts)); print('external requests:',ext[:5]); print('console errors/warnings:',cons[:10])
