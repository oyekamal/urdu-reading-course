from common import *
from h1_flows import mk, L1, TIMES
import sys, json
def review_test(b, times, which):
    ctx, pg = newpage(b); quick_profile(pg, 'Rv'); pid = mk(pg, [])
    pg.evaluate("""async(pid)=>{ for (const [i,ch] of ['ا','ب','ک','ل','م'].entries()) await __put('cards',{id:pid+':'+ch,profileId:pid,item:ch,kind:'letter',box:1,due:1,seen:0}); }""", pid)
    nav(pg, 'review'); pg.wait_for_timeout(1000)
    sel = "button:has-text('Got it')" if which == 'got' else "button:has-text('Not yet')"
    burst_sel(pg, sel, times); pg.wait_for_timeout(2600)
    c, d = counts(pg)
    seen = sorted([(x['item'], x['seen'], x['box']) for x in d['cards'] if x['seen']])
    ctr = pg.evaluate("document.querySelector('.muted')?.innerText")
    out = (which, times, 'graded cards', seen, 'counter', pg.evaluate("[...document.querySelectorAll('.muted')].map(m=>m.innerText).find(t=>/ \\/ /.test(t))"))
    ctx.close(); return out
def addlearner_test(b, times):
    ctx, pg = newpage(b); pg.goto(BASE + '?skiponb'); pg.wait_for_timeout(1500)
    burst_sel(pg, 'text=Just me', times); pg.wait_for_timeout(1200)
    mode = pg.evaluate("__dump().then(d=>(d.settings.find(s=>s.key==='mode')||{}).value)")
    out = ['mode picker', times, 'screen', pg.inner_text('#app')[:30].replace('\n', ' | '), 'mode', mode]
    burst_sel(pg, 'text=+ Add a learner', times); pg.wait_for_timeout(800)
    pg.fill('input[placeholder=Name]', 'Dup')
    burst_sel(pg, "button:has-text('Start')", times); pg.wait_for_timeout(2500)
    c, d = counts(pg); out += ['profiles', c['profiles'], 'screen', pg.inner_text('#app')[:30].replace('\n', ' | ')]
    ctx.close(); return out
def dict_test(b, times, right):
    ctx, pg = newpage(b); quick_profile(pg, 'D'); pid = mk(pg, L1 + ['marks', 'join', 'blend'])
    # jump straight to the Units tab lesson page of unit 1 (all drills inline; dictation has Check)
    from i1_gate import open_unit
    open_unit(pg, 1)
    pg.evaluate("()=>{const h=[...document.querySelectorAll('h3')].find(h=>/dictation/i.test(h.innerText)); h.scrollIntoView()}"); pg.wait_for_timeout(300)
    info = pg.evaluate("""()=>{const h=[...document.querySelectorAll('h3')].find(h=>/dictation/i.test(h.innerText)); const card=h.nextElementSibling; return !!card}""")
    # find the dictation card's check button: the one whose card has h2 Dictation
    pg.evaluate("""()=>{const c=[...document.querySelectorAll('.card')].find(c=>c.querySelector('h2')?.innerText==='Dictation'); c.querySelector('.keys .tile').click(); window.__dc=c; }""")
    xy = pg.evaluate("()=>{const b=[...window.__dc.querySelectorAll('button')].find(b=>b.innerText.trim()==='Check'); b.scrollIntoView({block:'center'}); const r=b.getBoundingClientRect(); return [r.x+r.width/2,r.y+r.height/2]}")
    bursts(pg, xy, times); pg.wait_for_timeout(1500)
    c, d = counts(pg); att = [(a['drill'], a['correct']) for a in d['attempts'] if a['drill'] == 'dictation']
    ctx.close(); return ('dictation wrong x', times, att)
if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        for t in TIMES: print(dict_test(b, t, False), flush=True)
        b.close()
