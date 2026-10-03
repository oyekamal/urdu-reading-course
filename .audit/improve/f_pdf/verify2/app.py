import json,os
from playwright.sync_api import sync_playwright
idx=json.load(open(os.path.expanduser('~/Documents/free_work/urdu-reading-course/mobile/public/pdf/index.json')))
out='appshots';os.makedirs(out,exist_ok=True)
res=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for (w,h) in [(360,640),(390,844)]:
      for scheme in ['light','dark']:
        ctx=b.new_context(viewport={'width':w,'height':h},color_scheme=scheme,accept_downloads=True)
        pg=ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('http://localhost:5188/?skiponb');pg.wait_for_timeout(1800)
        pg.click('text=Just me');pg.wait_for_timeout(400);pg.click('text=+ Add a learner');pg.wait_for_timeout(300)
        pg.fill('input[placeholder=Name]','Zee');pg.click("button:has-text('Start')");pg.wait_for_timeout(1800)
        # Me tab
        try:
            pg.click('.bottom >> text=/Me|More/i',timeout=3000)
        except Exception as e:
            print('menav',e); print(pg.inner_text('.bottom'))
        pg.wait_for_timeout(500)
        pg.click('text=Open practice sheets');pg.wait_for_timeout(1200)
        tag=f'{w}_{scheme}'
        pg.screenshot(path=f'{out}/{tag}_start.png')
        tabs=pg.query_selector_all('.pr-tab')
        info={'tabs':len(tabs),'hscroll':pg.evaluate('document.documentElement.scrollWidth>innerWidth+1 || document.querySelector(".pr-ov").scrollWidth>innerWidth+1')}
        for k in (0,3,9):
            pg.evaluate(f'document.querySelectorAll(".pr-tab")[{k}].click()');pg.wait_for_timeout(400)
            pg.screenshot(path=f'{out}/{tag}_tab{k}.png')
            cards=pg.query_selector_all('.pr-card')
            shown=[]
            for c in cards:
                t=c.query_selector('.pr-en').inner_text();pills=[x.inner_text() for x in c.query_selector_all('.pill')]
                shown.append((t,pills))
            g=[i for i in idx['items'] if (i['unit'] is None if k==0 else i['unit']==k-1)]
            exp=[(i['title'],[f"{i['pages']} page"+('' if i['pages']==1 else 's'),(f"{i['size']/1048576:.1f} MB" if i['size']>=1048576 else f"{max(1,round(i['size']/1024))} KB"),'A4']) for i in g]
            info[f'tab{k}']=(len(cards),len(g),sorted(shown)==sorted(exp))
            # small tap sizes
            btns=pg.evaluate('[...document.querySelectorAll(".pr-card .btn")].map(e=>{const r=e.getBoundingClientRect();return Math.round(Math.min(r.width,r.height))}).reduce((a,b)=>Math.min(a,b),999)')
            info[f'minbtn{k}']=btns
            a=pg.query_selector_all('.pr-card a.btn')[0]
            with pg.expect_download(timeout=8000) as d: a.click()
            dl=d.value; path=f'{out}/dl_{tag}_{k}_{dl.suggested_filename}'; dl.save_as(path); info[f'dl{k}']=(dl.suggested_filename,os.path.getsize(path))
        res.append((tag,info,errs)); print(tag,info,errs)
        if scheme=='light' and w==390:
            # offline
            ctx.set_offline(True)
            pg.evaluate('document.querySelectorAll(".pr-tab")[3].click()');pg.wait_for_timeout(300)
            a=pg.query_selector_all('.pr-card a.btn')[0]
            try:
                with pg.expect_download(timeout=5000) as d: a.click()
                print('offline dl (cached blob) ok',d.value.suggested_filename)
            except Exception as e: print('offline dl fail',str(e)[:80])
            a=pg.query_selector_all('.pr-card a.btn')[2]
            try:
                with pg.expect_download(timeout=4000) as d: a.click()
                print('offline UNCACHED dl ok?',d.value.suggested_filename)
            except Exception as e: print('offline uncached: no download;',pg.inner_text('.pr-status'))
            pg.screenshot(path=f'{out}/offline.png')
            # reload offline
            try:
                pg.reload();pg.wait_for_timeout(1500);print('reload offline ok',pg.title())
            except Exception as e: print('reload offline fail',str(e)[:80])
        ctx.close()
    b.close()
