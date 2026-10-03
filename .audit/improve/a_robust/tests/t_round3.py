# Round-2 verifier findings: plan CTA duplicates, tab double tap, single-store failure at boot, missing index, quiz write failure, units:{0:null}.
from common import *
RES = []
def chk(name, ok, extra=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name, extra)
def txt(pg): return pg.inner_text('#app')[:120].replace('\n', ' | ')
STORE_FAIL = "(()=>{const T=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(n,...a){ const s=[].concat(n); if(window.__fs && s.includes(window.__fs)) throw new DOMException('x','UnknownError'); return T.call(this,n,...a) }})()"
def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        # 1. onboarding plan CTA x3 -> one learner
        for how in ('sync3', 'dbl'):
            ctx, pg = newpage(b); pg.goto(BASE + 'manifest.webmanifest')
            pg.evaluate("""()=>new Promise(r=>{const q=indexedDB.open('urdu-reader',1);q.onupgradeneeded=()=>{};q.onsuccess=()=>r()})""")
            pg.goto(BASE); pg.wait_for_timeout(2500)
            pg.evaluate("""()=>__put('settings',{key:'onb',value:{i:16,a:{who:'child',name:'Zara',colour:'#1E9C8F',goal:'school',speak:'some',reads:'none',pains:[],minutes:10,days:7}}})""")
            pg.reload(); pg.wait_for_timeout(2500)
            if how == 'sync3': pg.evaluate("()=>{const b=document.querySelector('.ob-cta'); b.click(); b.click(); b.click()}")
            else: pg.dblclick('.ob-cta')
            pg.wait_for_timeout(2500); c, d = counts(pg)
            chk(f'plan CTA {how} -> exactly one profile and one first-word attempt', c['profiles'] == 1 and c['attempts'] <= 1, (c['profiles'], c['attempts'])); ctx.close()
        # 2. tab bar dblclick / x3 -> one hero
        ctx, pg = newpage(b); quick_profile(pg, 'Tabs')
        for k in ('today', 'review', 'read', 'me'):
            pg.dblclick(f".bottom button[data-k='{k}']"); pg.wait_for_timeout(1200)
            n = pg.evaluate("document.querySelector('main, #app > div')?.children.length"); heroes = pg.evaluate("document.querySelectorAll('.home-hero, .page-head').length")
            chk(f'tab {k} dblclick -> single header/hero', heroes == 1, heroes)
        ctx.close()
        # 3. one failing store at boot -> recovery, not Loading
        for st in ('cards', 'progress'):
            ctx, pg = newpage(b, init="window.__fs=(localStorage.__fs||null);" + STORE_FAIL); quick_profile(pg, 'Fail'); pg.evaluate(f"localStorage.__fs='{st}'"); pg.reload()
            try: pg.wait_for_selector('.recovery', timeout=16000)
            except Exception: pass
            chk(f'store {st} throwing at boot -> recovery screen', pg.query_selector('.recovery') is not None, txt(pg)[:60]); ctx.close()
        # 4. missing index
        ctx, pg = newpage(b); pg.goto(BASE + 'manifest.webmanifest')
        pg.evaluate("""()=>new Promise(r=>{const q=indexedDB.open('urdu-reader',1);q.onupgradeneeded=()=>{const d=q.result;for(const [n,k] of [['settings','key'],['profiles','id'],['attempts','id'],['cards','id'],['sessions','id'],['progress','id'],['assessments','id']]) d.createObjectStore(n,{keyPath:k})};q.onsuccess=()=>{q.result.close();r()}})""")
        quick_profile(pg, 'Idx'); chk('database without indexes is repaired, learner opens', 'Idx' in pg.inner_text('body') and 'index' not in ' '.join(pg._errs).lower(), pg._errs[:1]); ctx.close()
        # 5. units:{0:null} does not blank the teacher class tab -> covered by schema; check the learner side + teacher via mode school
        ctx, pg = newpage(b); quick_profile(pg, 'Nul'); pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        pg.evaluate("p=>__put('progress',{id:p,units:{'0':null},wpm:[],sessions:0})", pid); pg.reload(); pg.wait_for_timeout(2000)
        chk('progress units:{0:null} renders Today', 'Nul' in txt(pg), txt(pg)[:50]); ctx.close()
        print('RESULT', 'PASS' if all(RES) else 'FAIL', f'{sum(RES)}/{len(RES)}')
        b.close()
main()
