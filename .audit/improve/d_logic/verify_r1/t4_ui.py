import json, random, sys, time, h
from playwright.sync_api import sync_playwright
TAT='ـ'
def run(p, known, label, seed=0, dbl=False, units_script=None):
    rnd = random.Random(seed); b, pg = h.fresh2(p, 'Pl'+label[:4])
    pg.click(".bottom button:has-text('Learn')"); pg.wait_for_timeout(1200)
    btn = pg.query_selector("button:has-text('placement check')")
    if not btn: return {'label': label, 'err': 'no placement button', 'btns': pg.evaluate("[...document.querySelectorAll('button')].map(b=>b.textContent.trim().slice(0,30))")}
    btn.click(); pg.wait_for_timeout(800)
    nq = 0; log = []; t0 = time.time(); stuck = 0
    while True:
        res = pg.query_selector('.hero h2')
        if res and 'Start at unit' in res.inner_text(): break
        r = pg.evaluate("""([known, rv, dbl]) => { const tiles=[...document.querySelectorAll('.choices .tile')]; if(tiles.length<2) return null; const right=tiles.find(t=>t.dataset.right); if(!right) return null;
          if(tiles.some(t=>t.classList.contains('ok')||t.classList.contains('no'))) return {busy:1};
          const rt=right.textContent.trim().replace(/\u0640/g,''); const K=new Set([...known]); const knows=[...rt].every(c=>K.has(c)||/[\u064B-\u0652\u0670]/.test(c));
          const pick = knows? right : tiles[Math.floor(rv*tiles.length)]; const status=(document.querySelector('.score')||{}).textContent||'';
          pick.click(); if(dbl){ for(const t of tiles) t.click(); }
          return {rt, knows, correct: pick===right, status}; }""", [''.join(known), rnd.random(), dbl])
        if not r: stuck += 1; pg.wait_for_timeout(150)
        elif r.get('busy'): pg.wait_for_timeout(100)
        else:
            stuck = 0; nq += 1; log.append(r); pg.wait_for_timeout(560 if r['correct'] else 900)
        if stuck > 60: break
    pg.wait_for_timeout(500)
    heading = pg.inner_text('.hero h2'); sub = pg.inner_text('.hero .muted')
    st = pg.evaluate("""async()=>{const {db}=await import('/src/db.js');const prof=(await db.all('profiles'))[0];const pr=await db.get('progress',prof.id);const cards=await db.by('cards','profileId',prof.id);
      return {passed:Object.entries(pr.units).filter(([n,u])=>u.passed).map(([n])=>+n).sort((a,b)=>a-b), ncards:cards.length, ids:cards.map(c=>c.id), kinds:cards.reduce((a,c)=>{a[c.kind]=(a[c.kind]||0)+1;return a},{})}}""")
    dupids = len(st['ids']) - len(set(st['ids']))
    # go button works?
    go = pg.query_selector("button:has-text('Go')"); go.click(); pg.wait_for_timeout(1200); after = pg.inner_text('#app h1')[:40]
    r = {'label': label, 'questions': nq, 'secs': round(time.time()-t0,1), 'heading': heading, 'sub': sub, 'passed': st['passed'], 'ncards': st['ncards'], 'kinds': st['kinds'], 'dup_card_ids': dupids, 'after_go': after, 'errors': h.real_errors(pg), 'last_log': log[-2:]}
    b.close(); return r
UNITS = None
if __name__ == '__main__':
    out = []
    with sync_playwright() as p:
        L = json.load(open('/home/oye/Documents/free_work/urdu-reading-course/mobile/public/data/units.json'))['units']
        letters = lambda *ns: set(c for u in L if u['n'] in ns for c in u['letters'])
        sc = [('all', set(c for u in L for c in u['letters']) | set('ۃ')), ('none', set()),
              ('u1-3', letters(1,2,3)), ('u1-5', letters(1,2,3,4,5)),
              ('u1_minus1', letters(1)-{'ک'}), ('u1-4_minus_u5_one', letters(1,2,3,4)|(letters(5)-{'گ'})),
              ('u1-9_minus_ظ', letters(1,2,3,4,5,6,7,8,9)-{'ظ'})]
        for lab, K in sc:
            for seed in (1,):
                try: out.append(run(p, K, lab, seed))
                except Exception as e: out.append({'label': lab, 'exc': str(e)[:200]})
                print(json.dumps(out[-1], ensure_ascii=False)[:900], flush=True)
    h.save('t4_ui.json', out)
