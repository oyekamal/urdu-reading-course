def center(pg, sel):
    return pg.evaluate("s=>{const e=document.querySelector(s); const r=e.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]}", sel)
def centerText(pg, rx, tag='button'):
    return pg.evaluate("([rx,tag])=>{const b=[...document.querySelectorAll(tag)].find(b=>new RegExp(rx).test(b.innerText)); const r=b.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]}", [rx,tag])
def taps(pg, xy, n, gap):
    for i in range(n):
        pg.mouse.click(xy[0], xy[1])
        if i < n-1: pg.wait_for_timeout(gap)
