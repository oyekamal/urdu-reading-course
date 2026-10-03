from common import *
from d1_helpers import *
NAMES={'W40':'W'*40,'ur40':'م'*40,'nospace300':'x'*300,'zw':'​'*8,'mixed':'A‮B<b>x</b>⁦C','nbsp':'  ','zalgo':'a'+'́'*39}
with sync_playwright() as p:
    b=p.chromium.launch()
    for label,nm in NAMES.items():
        ctx,pg=newpage(b); pg.goto(BASE+'?skiponb'); pg.wait_for_timeout(1300)
        click(pg,'text=Just me'); pg.wait_for_timeout(300); click(pg,'text=+ Add a learner'); pg.wait_for_timeout(300)
        pg.fill('input[placeholder=Name]', nm)
        stored=pg.evaluate("document.querySelector('input[placeholder=Name]').value.length")
        click(pg,"button:has-text('Start')"); pg.wait_for_timeout(1500)
        if not pg.query_selector('.bottom'):
            print(label,'-> no profile created:', toast(pg)); ctx.close(); continue
        out=[]
        for k in ['today','review','read','me']:
            nav(pg,k); out.append((k, sw(pg)))
        d=pg.evaluate('__dump()'); name=d['profiles'][0]['name'] if d['profiles'] else None
        print(f'{label}: typed len {stored} stored={name!r}'[:110], '| screens', out, '| inert', inert(pg)[:1])
        # profile picker + parent report
        pg.evaluate("()=>document.querySelector('.hh-who, .page-head .btn')?.click()"); pg.wait_for_timeout(700); print('   picker sw', sw(pg))
        ctx.close()
    b.close()
