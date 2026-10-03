# Round-2 regressions found by the hostile verifier: tab failures, bad cards, garbage settings, burst taps through overlays, import replace confirm.
from common import *
RES = []
def chk(name, ok, extra=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name, extra)
FAIL = "(()=>{const T=IDBDatabase.prototype.transaction; IDBDatabase.prototype.transaction=function(...a){ if(window.__fail) throw new DOMException('x','UnknownError'); return T.apply(this,a) }})()"
def txt(pg): return pg.inner_text('#app')[:150].replace('\n', ' | ')
def taps(pg, sel, n=3, gap=200):
    box = pg.evaluate("s=>{const r=document.querySelector(s).getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}", sel)
    for i in range(n):
        pg.mouse.click(box[0], box[1]); pg.wait_for_timeout(gap)
def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        # 1. every transaction fails while the learner is on a tab -> recovery screen, not a half-empty screen
        ctx, pg = newpage(b, init=FAIL); quick_profile(pg, 'Tab')
        pg.evaluate("window.__fail=1"); nav(pg, 'review'); pg.wait_for_timeout(1500)
        chk('tab load failure -> recovery screen with Try again', 'could not open' in txt(pg) and pg.query_selector('.recovery') is not None, txt(pg)[:70])
        pg.evaluate("window.__fail=0"); pg.evaluate("()=>[...document.querySelectorAll('.recovery button')][0].click()"); pg.wait_for_timeout(2500)
        chk('Try again returns to the learner', 'Tab' in pg.inner_text('body'), txt(pg)[:60])
        ctx.close()
        # 2. schema-valid but unknown letter card does not freeze Review
        ctx, pg = newpage(b); quick_profile(pg, 'Card'); pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        pg.evaluate("p=>Promise.all([__put('cards',{id:p+':zzz',profileId:p,item:'zzz',kind:'letter',box:1,due:1,seen:0}),__put('cards',{id:p+':ا',profileId:p,item:'ا',kind:'letter',box:1,due:1,seen:0})])", pid)
        pg.reload(); pg.wait_for_timeout(2000); nav(pg, 'review'); pg.wait_for_timeout(600)
        chk('Review shows only usable cards (1 card)', '1 card' in pg.inner_text('#app'), txt(pg)[:80])
        pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Not yet').click()"); pg.wait_for_timeout(2200)
        chk('Not yet works, no page error', not pg._errs, pg._errs); ctx.close()
        # 3. garbage settings
        ctx, pg = newpage(b); quick_profile(pg, 'Garb')
        pg.evaluate("Promise.all([__put('settings',{key:'mode',value:{a:1}}),__put('settings',{key:'activeProfile',value:{}})])"); pg.reload(); pg.wait_for_timeout(2500)
        chk('garbage mode/activeProfile -> device-type picker, not recovery', 'Who is this device for' in pg.inner_text('body') and pg.query_selector('.recovery') is None, txt(pg)[:70])
        ctx.close()
        # 4. burst taps (gaps 100/200/300) never pass through the celebration to the tab bar
        for gap in (100, 200, 300):
            ctx, pg = newpage(b); quick_profile(pg, 'Burst')
            click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
            for _ in range(3): pg.evaluate("()=>document.querySelector('.lesson .btn-primary')?.click()"); pg.wait_for_timeout(500)
            pg.wait_for_selector('.celebrate', timeout=8000); pg.wait_for_timeout(1800)
            taps(pg, '.cel-go', 3, gap); pg.wait_for_timeout(1000)
            chk(f'celebration Next x3 at {gap} ms: lesson 2 open, still on Learn', 'lesson 2 of 2' in pg.inner_text('#app') and pg.evaluate("document.querySelector('.bottom .active')?.dataset.k") == 'today', txt(pg)[:50])
            ctx.close()
        # 5. review Got it burst at 100/200/300
        for gap in (100, 200, 300):
            ctx, pg = newpage(b); quick_profile(pg, 'Rev'); pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
            pg.evaluate("p=>Promise.all(['ا','ب','ک','ل'].map(c=>__put('cards',{id:p+':'+c,profileId:p,item:c,kind:'letter',box:1,due:1,seen:0})))", pid)
            pg.reload(); pg.wait_for_timeout(2000); nav(pg, 'review'); pg.wait_for_timeout(600)
            pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Got it'); b.dataset.t='1'}")
            taps(pg, "button[data-t='1']", 3, gap); pg.wait_for_timeout(600)
            c, d = counts(pg); graded = [x for x in d['cards'] if x.get('seen')]
            chk(f'review Got it x3 at {gap} ms -> exactly one card graded', len(graded) == 1, len(graded)); ctx.close()
        # 6. lesson Continue burst
        for gap in (100, 200, 300):
            ctx, pg = newpage(b); quick_profile(pg, 'Cont'); click(pg, "button:has-text('Start:')"); pg.wait_for_timeout(900)
            pg.evaluate("()=>document.querySelector('.lesson .btn-primary').dataset.t='1'"); taps(pg, ".lesson .btn-primary[data-t='1']", 3, gap); pg.wait_for_timeout(500)
            chk(f'lesson Continue x3 at {gap} ms -> one screen', pg.evaluate("document.querySelector('.progress i')?.style.width") == '33%'); ctx.close()
        # 7. import that would replace data asks first; Cancel changes nothing
        ctx, pg = newpage(b); quick_profile(pg, 'Zed'); nav(pg, 'me'); pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        import tempfile
        bk = {'format': 'urdu-qaida-backup', 'version': 1, 'profiles': [{'id': pid, 'name': 'Hacked', 'updatedAt': 4 * 10 ** 12}], 'progress': [{'id': pid, 'units': {'0': {'passed': True}}, 'updatedAt': 4 * 10 ** 12}]}
        f = tempfile.mktemp(suffix='.json'); open(f, 'w').write(json.dumps(bk))
        with pg.expect_file_chooser(timeout=8000) as fc:
            pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/Import a backup|Restore from a backup/.test(b.innerText)).click()")
            pg.wait_for_selector('.gate-sheet'); w = pg.inner_text('.gate-en').strip()
            ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']; TEENS = ['ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']; TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
            n = [i for i in range(10, 100) if (TEENS[i-10] if i < 20 else TENS[i//10] + ('-' + ONES[i%10] if i % 10 else '')) == w][0]
            pg.fill('#gate-input', str(n)); pg.evaluate("()=>document.querySelector('.gate-ok').click()")
        fc.value.set_files(f); pg.wait_for_timeout(1500); print('toast', pg.evaluate("document.getElementById('toast')?.textContent"), pg._errs, pg.evaluate("document.body.innerHTML.includes('a11y-sheet')")); pg.wait_for_selector('.a11y-sheet', timeout=6000)
        chk('replacing import shows a confirm sheet naming what changes', 'replaces' in pg.inner_text('.a11y-sheet'), pg.inner_text('.a11y-sheet')[:120].replace('\n', ' '))
        pg.evaluate("()=>document.querySelector('.a11y-stay').click()"); pg.wait_for_timeout(800)
        d = pg.evaluate('__dump()'); chk('Cancel: learner unchanged', [x['name'] for x in d['profiles']] == ['Zed'], [x['name'] for x in d['profiles']])
        print('  errors', pg._errs); ctx.close(); b.close()
    print('RESULT', 'PASS' if all(RES) else 'FAIL', f'{sum(RES)}/{len(RES)}')
main()
