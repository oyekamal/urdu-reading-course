from common import *
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=newpage(b)
    pg.goto(BASE)
    print(pg.evaluate("""async()=>{ try{ const f=async(pv)=>{ const dc = pv ? 1 : dc; return dc}; return await f(false)}catch(e){return 'ERR '+e.message} }"""))
    print(b.version)
    b.close()
