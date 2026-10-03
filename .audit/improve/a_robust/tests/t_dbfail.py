# Database failures: unavailable / hung / blocked / aborted / malformed / deleted store. Never a frozen "Loading…". Production build.
from common import *
RES = []
def chk(name, ok, extra=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name, extra)
INIT = """(()=>{
 const real = indexedDB; const flag = () => { try { return localStorage.getItem('__idb') } catch (e) { return null } };
 const open = real.open.bind(real);
 const proxy = new Proxy(real, { get(t, k) { if (k === 'open') return (...a) => { if (flag() === 'hang') return {}; if (flag() === 'throw') throw new DOMException('denied', 'SecurityError'); return open(...a); }; const v = t[k]; return typeof v === 'function' ? v.bind(t) : v; } });
 Object.defineProperty(window, 'indexedDB', { get() { return flag() === 'none' ? undefined : proxy } });
})()"""
def txt(pg): return pg.inner_text('#app')[:140].replace('\n', ' | ')
def gate_pass(pg):
    pg.wait_for_selector('.gate-sheet', timeout=4000); words = pg.inner_text('.gate-en').strip()
    ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']; TEENS = ['ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']; TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
    n = [i for i in range(10, 100) if (TEENS[i-10] if i < 20 else TENS[i//10] + ('-' + ONES[i%10] if i % 10 else '')) == words][0]
    pg.fill('#gate-input', str(n)); pg.evaluate("()=>document.querySelector('.gate-ok').click()"); pg.wait_for_timeout(600)
def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        for mode in ['none', 'throw', 'hang']:
            ctx, pg = newpage(b, init=INIT); pg.goto(BASE + 'manifest.webmanifest'); pg.evaluate(f"localStorage.setItem('__idb','{mode}')")
            t0 = time.time(); pg.goto(BASE);
            try: pg.wait_for_selector('.recovery', timeout=16000)
            except Exception: pass
            chk(f'idb {mode}: recovery screen (not Loading...)', 'could not open' in txt(pg), f'{txt(pg)[:70]} after {time.time()-t0:.1f}s')
            labels = pg.evaluate("[...document.querySelectorAll('.recovery button')].map(b=>b.innerText)")
            chk(f'idb {mode}: Try again / Export / Start fresh offered', labels == ['Try again', 'Export what can be saved', 'Start fresh'], labels)
            pg.evaluate("localStorage.removeItem('__idb')"); pg.evaluate("()=>[...document.querySelectorAll('.recovery button')][0].click()"); pg.wait_for_timeout(3000)
            chk(f'idb {mode}: Try again recovers once storage works', 'Read Urdu' in txt(pg) or "Let's begin" in txt(pg), txt(pg)[:60])
            ctx.close()
        # Export + Start fresh are behind the gate
        ctx, pg = newpage(b, init=INIT); quick_profile(pg, 'Keep'); pg.evaluate("localStorage.setItem('__idb','none')"); pg.reload(); pg.wait_for_selector('.recovery', timeout=15000)
        pg.evaluate("()=>[...document.querySelectorAll('.recovery button')][2].click()"); pg.wait_for_timeout(700)
        chk('Start fresh opens the grown-up gate first', pg.query_selector('.gate-sheet') is not None)
        pg.evaluate("()=>document.querySelector('.gate-cancel').click()"); pg.wait_for_timeout(400)
        pg.evaluate("localStorage.removeItem('__idb')"); pg.evaluate("()=>[...document.querySelectorAll('.recovery button')][0].click()"); pg.wait_for_timeout(2500)
        chk('cancelling the gate deleted nothing', 'Keep' in txt(pg) or 'Learn' in pg.inner_text('body'), txt(pg)[:50])
        ctx.close()
        # malformed records of every store do not crash boot
        ctx, pg = newpage(b); quick_profile(pg, 'Mal'); pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        pg.evaluate("""p=>Promise.all([__put('progress',{id:p,units:{'0':null,'1':'x','2':{lessons:5,steps:'y'}},wpm:[null,{wpm:'a'}],sessions:'z'}),
          __put('cards',{id:p+':q',profileId:p,item:null,kind:7,box:'x',due:'y'}), __put('attempts',{id:'bad',profileId:p,unit:'z',drill:null}), __put('sessions',{id:'s',profileId:p,bites:'x'}), __put('assessments',{id:'as',profileId:p,ts:'x',orf:null})]).catch(e=>String(e))""", pid)
        pg.reload(); pg.wait_for_timeout(2500); chk('malformed progress/cards/attempts/sessions/assessments: Today renders', 'Mal' in txt(pg), txt(pg)[:60])
        for k in ['review', 'read', 'me', 'today']: nav(pg, k)
        pg.wait_for_timeout(500); chk('all tabs render with malformed records', 'Mal' in pg.inner_text('body') or 'Learn' in pg.inner_text('body'), pg._errs[:2])
        ctx.close()
        # deleted store at runtime (another tab upgrades the DB without the cards store)
        ctx, pg = newpage(b); quick_profile(pg, 'Del'); page2 = ctx.new_page(); page2.goto(BASE + 'manifest.webmanifest')
        page2.evaluate("""()=>new Promise(r=>{const q=indexedDB.open('urdu-reader',5);q.onupgradeneeded=()=>{q.result.deleteObjectStore('cards');q.result.deleteObjectStore('attempts')};q.onsuccess=()=>{q.result.close();r()};q.onerror=()=>r()})""")
        pg.bring_to_front(); pg.reload(); pg.wait_for_timeout(3500)
        chk('deleted stores (db version 5 without cards/attempts): app repairs or shows recovery, never Loading...', 'Loading' not in txt(pg), txt(pg)[:80])
        print('  errors', pg._errs); ctx.close()
        # quota abort during lesson finish -> retry works, not frozen
        QUOTA = "(()=>{const p=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(v,k){if(window.__q&&this.name!=='settings'){const r=p.call(this,v,k);try{this.transaction.abort()}catch(e){}return r}return p.call(this,v,k)}})()"
        ctx, pg = newpage(b, init=QUOTA); quick_profile(pg, 'Quota'); pg.evaluate("window.__q=1")
        click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
        for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(600)
        pg.wait_for_timeout(2500); chk('write abort at lesson end: calm retry screen shown', 'did not save' in txt(pg), txt(pg)[:80])
        pg.evaluate("window.__q=0"); pg.wait_for_timeout(400); pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Try again').click()")
        try: pg.wait_for_selector('.celebrate', timeout=8000); ok = True
        except Exception: ok = False
        chk('Try again after the storage recovers -> celebration', ok)
        c, d = counts(pg); chk('pearl saved exactly once', [list((x.get('units') or {}).get('0', {}).get('lessons', {}).keys()) for x in d['progress']] == [['rules']])
        print('  errors', pg._errs); ctx.close(); b.close()
    print('RESULT', 'PASS' if all(RES) else 'FAIL', f'{sum(RES)}/{len(RES)}')
main()
