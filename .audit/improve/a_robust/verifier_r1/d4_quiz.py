from common import *
from d1_helpers import *
import json
U=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/units.json'))['units']
L1=['Lalif','Lbe','Lkaf','Llam','Lmim','Lnun']
def mk(pg, done):
    pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    prog={'id':pid,'units':{'0':{'passed':True,'score':10,'total':10,'at':1,'lessons':{'rules':1,'done':1}},'1':{'lessons':{k:1 for k in done}}}}
    pg.evaluate("p=>__put('progress',p)",prog); pg.reload(); pg.wait_for_timeout(2000); return pid
def cur_btn(pg): click(pg, "button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(1000)
with sync_playwright() as p:
    b=p.chromium.launch()
    # QUIZ: lessons through 'read' done -> quiz is next
    ctx,pg=newpage(b); quick_profile(pg,'Q'); pid=mk(pg, L1+['marks','join','blend','W1','W2','read'])
    print('today:', pg.inner_text('.today-card')[:80].replace('\n',' | '))
    cur_btn(pg)
    print('lesson screen:', pg.inner_text('#app')[:60].replace('\n',' | '))
    # answer all questions correctly
    n=pg.evaluate("""()=>{const lis=[...document.querySelectorAll('.lesson ol > li')]; lis.forEach(li=>{const rom=li.querySelector('b').innerText; [...li.querySelectorAll('.tile')].find(t=>t.getAttribute('aria-label')===rom).click()}); return lis.length}""")
    print('questions', n)
    xy=center(pg,'.lesson .btn-primary.act, .lesson .btn-primary'); 
    pg.evaluate("()=>{const b=[...document.querySelectorAll('.lesson button')].find(b=>b.innerText.trim()==='Submit'); b.click(); b.click(); b.click()}"); pg.wait_for_timeout(1500)
    c,d=counts(pg); print('after Submit x3 attempts:', len([a for a in d['attempts'] if a['drill']=='quiz']), 'cards', c['cards'], 'progress', [(u,v.get('passed')) for x in d['progress'] for u,v in x['units'].items()])
    # Finish x3 with real taps 200ms
    print('screen:', pg.inner_text('.lesson')[-120:].replace('\n',' | '))
    xy=centerText(pg,'^Finish$'); taps(pg,xy,3,200); pg.wait_for_timeout(2500)
    c,d=counts(pg); print('after Finish x3 (200ms):', 'pearls', [list(v.get('lessons',{}).keys()) for x in d['progress'] for u,v in x['units'].items() if u=='1'], 'cards', c['cards'], 'celebrations', pg.evaluate("document.querySelectorAll('.celebrate').length"))
    print('errs', pg._errs); ctx.close()
    # DICTATION wrong Check x3
    ctx,pg=newpage(b); quick_profile(pg,'D'); pid=mk(pg, L1+['marks','join','blend'])
    cur_btn(pg)
    print('words lesson:', pg.inner_text('#app')[:50].replace('\n',' | '))
    pg.evaluate("()=>[...document.querySelectorAll('.lesson button')].find(b=>/Read them/.test(b.innerText)).click()"); pg.wait_for_timeout(900)
    # join: solve 3 words
    import re
    for _ in range(3):
        rom=pg.evaluate("document.querySelector('.lesson .row b')?.innerText")
        word=next(w for w in U[1]['words'] if w[1]==rom)[0]
        bare=''.join(ch for ch in word if not ('ً'<=ch<='ْ' or ch in 'ٰـ'))
        for ch in bare:
            pg.evaluate("ch=>{const t=[...document.querySelectorAll('.lesson .choices .tile')].find(t=>!t.disabled&&t.innerText===ch); t.click()}", ch); pg.wait_for_timeout(60)
        pg.wait_for_timeout(300)
        pg.evaluate("()=>{const b=[...document.querySelectorAll('.lesson button')].find(b=>b.innerText.trim()==='Next word'); b&&b.click()}"); pg.wait_for_timeout(200)
    pg.wait_for_timeout(500)
    pg.evaluate("()=>{const b=[...document.querySelectorAll('.lesson .btn-primary')].find(b=>/Continue/.test(b.innerText)); b&&b.click()}"); pg.wait_for_timeout(900)
    print('dictation screen:', pg.inner_text('.lesson')[:60].replace('\n',' | '))
    pg.evaluate("()=>{document.querySelector('.lesson .keys .tile').click()}")
    xy=centerText(pg,'^Check$'); pg.evaluate("()=>{const b=[...document.querySelectorAll('.lesson button')].find(b=>b.innerText.trim()==='Check'); b.click(); b.click(); b.click()}"); pg.wait_for_timeout(800)
    c,d=counts(pg); print('dictation wrong Check x3 attempts:', [(a['drill'],a['correct']) for a in d['attempts'] if a['drill']=='dictation'])
    print('errs', pg._errs); ctx.close(); b.close()
