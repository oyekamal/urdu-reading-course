from common import *
def center(pg, sel):
    bb = pg.evaluate("s=>{const e=document.querySelector(s); const r=e.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]}", sel); return bb
def taps(pg, xy, n, gap):
    for i in range(n):
        pg.mouse.click(xy[0], xy[1]); 
        if i < n-1: pg.wait_for_timeout(gap)
def wpct(pg): return pg.evaluate("document.querySelector('.progress i')?.style.width")
with sync_playwright() as p:
    b = p.chromium.launch()
    for gap in [100, 200, 300]:
        # lesson Continue triple tap
        ctx, pg = newpage(b); quick_profile(pg, 'Zed')
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
        xy = center(pg, '.lesson .btn-primary'); w0 = wpct(pg)
        taps(pg, xy, 3, gap); pg.wait_for_timeout(1500)
        print(f'lesson Continue x3 gap={gap}: {w0} -> {wpct(pg)}  celeb={pg.evaluate("document.querySelectorAll(\".celebrate\").length")}', pg.inner_text('#app')[:40].replace('\n',' | '))
        ctx.close()
    for gap in [100, 200, 300]:
        # review Got it x2 / x3 at the same coordinates
        ctx, pg = newpage(b); quick_profile(pg, 'Rev')
        pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        pg.evaluate("""p=>Promise.all(['ا','ب','ک','ل','م'].map(c=>__put('cards',{id:p+':'+c,profileId:p,item:c,kind:'letter',box:1,due:1,seen:0})))""", pid)
        pg.reload(); pg.wait_for_timeout(2000); nav(pg, 'review'); pg.wait_for_timeout(600)
        xy = pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Got it'); const r=b.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]}")
        taps(pg, xy, 3, gap); pg.wait_for_timeout(1200)
        c, d = counts(pg); graded = [x['item'] for x in d['cards'] if x.get('seen')]
        print(f'review Got it x3 gap={gap}: graded={graded}', re.findall(r'\d / 5', pg.inner_text('#app')))
        ctx.close()
    # mode picker 'Just me' double tap 150ms
    for gap in [100, 200, 300]:
        ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1500)
        xy = pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>/Just me/.test(b.innerText)); const r=b.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]}")
        taps(pg, xy, 3, gap); pg.wait_for_timeout(1200)
        c,d=counts(pg); print(f'mode picker Just me x3 gap={gap}:', pg.inner_text('#app')[:60].replace('\n',' | '), c['profiles'], settings(pg).get('mode'))
        ctx.close()
    b.close()
