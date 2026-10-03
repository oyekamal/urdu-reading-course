# Unit gating + quiz submit. Needs the DEV server (modules importable): BASE=http://localhost:5188/
import os
os.environ.setdefault('BASE', 'http://localhost:5188/')
from common import *
RES = []
def chk(name, ok, extra=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name, extra)
def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx, pg = newpage(b); dialogs = []
        pg.on('dialog', lambda d: dialogs.append(d.message))
        quick_profile(pg, 'Gate')
        pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        base = counts(pg)[0]
        # API level: tampering with a locked unit
        r = pg.evaluate("""async pid=>{const S=await import('/src/session.js');
          const a=await S.markUnit(pid,5,10,10); await S.ensureCards(pid,6); await S.recordAttempt(pid,5,'quiz','ب',false,0); const cur=await S.currentUnit(pid); const p=await S.getProgress(pid); return {a,cur,units:Object.keys(p.units)}}""", pid)
        c, d = counts(pg)
        chk('markUnit(5) on a locked unit refuses and writes nothing', r['a'] is False and r['cur'] == 0 and '5' not in r['units'], r)
        chk('ensureCards(6) creates no review cards for locked units', c['cards'] == base['cards'], f"{base['cards']} -> {c['cards']}")
        chk('recordAttempt on a locked unit records nothing', c['attempts'] == base['attempts'], f"{base['attempts']} -> {c['attempts']}")
        # forged progress: unit 5 'passed' without 0-4 -> current unit stays 0
        pg.evaluate("p=>__put('progress',{id:p,units:{'5':{passed:true,score:10,total:10}},wpm:[],sessions:0})", pid); pg.reload(); pg.wait_for_timeout(2000)
        chk('forged progress (unit 5 passed, 0-4 not) -> Learn still on Unit 0', 'Unit 0' in pg.inner_text('.home-hero'), pg.inner_text('.home-hero')[:60].replace('\n', ' | '))
        c, d = counts(pg); chk('no review cards after boot with forged progress', c['cards'] == 0, c['cards'])
        # UI: Units tab, tap a locked unit -> read-only preview, no confirm()
        nav(pg, 'today'); pg.evaluate("()=>[...document.querySelectorAll('button')].find(b=>/All units/.test(b.innerText))?.click()"); pg.wait_for_timeout(700)
        pg.evaluate("()=>[...document.querySelectorAll('.ucard')].find(b=>/Unit 5,/.test(b.getAttribute('aria-label')))?.click()"); pg.wait_for_timeout(1200)
        chk('no confirm() dialog on a locked unit', not dialogs, dialogs)
        txt = pg.inner_text('#app'); chk('locked unit shows Preview only note', 'Preview only' in txt, txt[:80].replace('\n', ' | '))
        chk('preview has no unit-check (quiz) Submit', pg.evaluate("![...document.querySelectorAll('button')].some(b=>b.innerText.trim()==='Submit')"))
        # interact with everything tappable in the preview, then check nothing was recorded
        pg.evaluate("()=>document.querySelectorAll('.tile').forEach(t=>t.click())"); pg.wait_for_timeout(600)
        pg.evaluate("()=>[...document.querySelectorAll('button')].filter(b=>/Check|Next|Got it|Again|Done/.test(b.innerText)).forEach(b=>b.click())"); pg.wait_for_timeout(600)
        c, d = counts(pg)
        chk('preview interaction recorded no attempts/cards/progress for unit 5', c['attempts'] == 0 and c['cards'] == 0 and all(x['units'].get('5') == {'passed': True, 'score': 10, 'total': 10} for x in d['progress']), c)
        pg.evaluate("()=>{}")
        # openLesson on locked unit: runLesson guard
        r = pg.evaluate("""async pid=>{const S=await import('/src/session.js'); return await S.currentUnit(pid)}""", pid); chk('current unit still 0', r == 0)
        ctx.close()
        # quiz submit x3: unit 1 with all lessons but the quiz done; a unit-0 pass first
        ctx, pg = newpage(b); quick_profile(pg, 'Quiz')
        pid = pg.evaluate("__dump().then(d=>d.profiles[0].id)")
        pg.evaluate("""async p=>{const {lessonsFor}=await import('/src/path.js'); const {C, loadContent}=await import('/src/content.js'); await loadContent(); const u1=C.units[1]; const ls=lessonsFor(u1); const lessons={}; ls.slice(0,-1).forEach(l=>lessons[l.id]=1);
          await __put('progress',{id:p,units:{'0':{passed:true,score:10,total:10,lessons:{rules:1,done:1}},'1':{lessons}},wpm:[],sessions:0}); window.__lastId=ls[ls.length-1].id}""", pid)
        pg.reload(); pg.wait_for_timeout(2200)
        print('  today:', pg.inner_text('.home-hero')[:90].replace('\n', ' | '))
        click(pg, "button:has-text('Continue:'), button:has-text('Start:')"); pg.wait_for_timeout(1200)
        pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Submit'); if(!b) throw new Error('no submit'); b.click(); b.click(); b.click()}"); pg.wait_for_timeout(1500)
        c, d = counts(pg); quiz = [a for a in d['attempts'] if a['drill'] == 'quiz']
        chk('quiz Submit x3 -> one set of 10 answers recorded', len(quiz) == 10, len(quiz))
        print('  errors', pg._errs); ctx.close(); b.close()
    print('RESULT', 'PASS' if all(RES) else 'FAIL', f'{sum(RES)}/{len(RES)}')
main()
