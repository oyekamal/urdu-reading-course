from common import *
from d1_helpers import *
import json
U=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/units.json'))['units']
L=json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/letters.json'))
with sync_playwright() as p:
    b=p.chromium.launch()
    # IDB tamper: unit 5 passed, unit 0 not
    ctx,pg=newpage(b); quick_profile(pg,'Tam'); pid=pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    pg.evaluate("p=>__put('progress',{id:p,units:{5:{passed:true,score:10,total:10},3:{passed:true}}})",pid); pg.reload(); pg.wait_for_timeout(2000)
    c,d=counts(pg); print('tamper: Learn shows', pg.inner_text('.home-hero .muted')[:30], '| cards', c['cards'])
    ctx.close()
    # placement: all correct -> where does it end?
    ctx,pg=newpage(b); quick_profile(pg,'Pl'); pid=pg.evaluate("__dump().then(d=>d.profiles[0].id)")
    click(pg,"button:has-text('Take the placement check')"); pg.wait_for_timeout(800)
    n=0
    for _ in range(400):
        if pg.query_selector('text=Start at unit'): break
        ok=pg.evaluate("()=>{const t=document.querySelector('.choices [data-right]'); if(!t) return false; t.click(); return true}")
        pg.wait_for_timeout(520 if ok else 200); n+=ok
    print('questions answered:', n, '|', pg.inner_text('.hero')[:60].replace('\n',' | ') if pg.query_selector('.hero') else pg.inner_text('#app')[:80])
    pg.wait_for_timeout(800)
    c,d=counts(pg); passed=sorted(int(k) for x in d['progress'] for k,v in x['units'].items() if v.get('passed'))
    print('passed units:', passed, 'cards:', c['cards'], 'errs', pg._errs)
    top=max(passed) if passed else -1
    exp=sum(len(u['letters'])+len(u['words']) for u in U if u['n']<top+1) + (len(L['sight_words']) if top+1>=6 else 0)
    print('expected cards for units <', top+1, '=', exp)
    pg.reload(); pg.wait_for_timeout(1800); print('Learn shows:', pg.inner_text('.home-hero .muted')[:40])
    ctx.close()
    # wrong at first question -> stays at unit 1 (start)
    ctx,pg=newpage(b); quick_profile(pg,'Pw')
    click(pg,"button:has-text('Take the placement check')"); pg.wait_for_timeout(800)
    pg.evaluate("()=>{const t=[...document.querySelectorAll('.choices .tile')].find(t=>!t.dataset.right); t.click()}"); pg.wait_for_timeout(2000)
    print('wrong first ->', pg.inner_text('#app')[:70].replace('\n',' | '))
    c,d=counts(pg); print('passed', [ (k,v.get('passed')) for x in d['progress'] for k,v in x['units'].items()], 'cards', c['cards'])
    ctx.close(); b.close()
