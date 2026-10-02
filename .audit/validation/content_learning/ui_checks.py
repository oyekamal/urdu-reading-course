#!/usr/bin/env python3
"""UI-level checks with Playwright: placement behaviour, unit-gating bypass through Units->confirm, aspirates audio buttons, quiz retry."""
import json, os, re, sys
from playwright.sync_api import sync_playwright
ROOT = os.path.expanduser('~/Documents/free_work/urdu-reading-course'); HERE = os.path.dirname(os.path.abspath(__file__)); PORT = os.environ.get('PORT', '5188')
L = json.load(open(ROOT + '/data/letters.json', encoding='utf8')); BYID = {l['id']: l for l in L['letters']}
U = json.load(open(ROOT + '/data/units.json', encoding='utf8'))['units']; R = {}
EXE = '/home/oye/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
INIT = "const _p=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__plays=(window.__plays||[]);if(!this.src.includes('/ui/')){window.__last=this.src;window.__plays.push(this.src)}return _p.call(this)}"
def fresh(p, name='Zee'):
    b = p.chromium.launch(executable_path=EXE); ctx = b.new_context(viewport={'width': 390, 'height': 800}); pg = ctx.new_page(); pg.on('dialog', lambda d: (R.setdefault('dialogs', []).append(d.message[:120]), d.accept()))
    pg.add_init_script(INIT); pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2200); pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300); pg.fill('input[placeholder=Name]', name); pg.click('button:has-text("Start")'); pg.wait_for_timeout(2500)
    return b, pg
DUMP = lambda pg: pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const pr=(await db.all('progress'))[0]||{}; const cards=await db.all('cards'); return {passed:Object.entries(pr.units||{}).filter(([k,v])=>v.passed).map(([k])=>+k), lessonsDone:Object.values(pr.units||{}).reduce((n,u)=>n+Object.keys(u.lessons||{}).length,0), cards:cards.length, cardLetters:cards.filter(c=>c.kind==='letter').length, cardWords:cards.filter(c=>c.kind==='word').length} }""")
def last(pg): return pg.evaluate("window.__last||''").split('/audio/')[-1].replace('.mp3', '')
js = lambda pg, h: pg.evaluate('e=>e.click()', h)
def placement(pg, know_up_to):
    js(pg, pg.query_selector("button:has-text('Take the placement check')")); pg.wait_for_timeout(800); asked = []
    for _ in range(300):
        h2 = pg.query_selector('#app h2'); t = h2.inner_text() if h2 else ''
        m = re.match(r'Unit (\d+) letters', t)
        if not m: break
        n = int(m.group(1)); tiles = pg.query_selector_all('.choices .tile')
        if not tiles: pg.wait_for_timeout(200); continue
        tgt = BYID[last(pg).split('/')[-1]]['ch']; asked.append((n, tgt))
        pick = [x for x in tiles if (x.inner_text().strip() == tgt) == (n <= know_up_to)][0]; js(pg, pick); pg.wait_for_timeout(480)
    return asked, pg.inner_text('#app h2'), pg.inner_text('#app .hero .muted') if pg.query_selector('#app .hero .muted') else ''
with sync_playwright() as p:
    # ---- placement: knows units 1-4 perfectly, nothing after
    b, pg = fresh(p); asked, head, sub = placement(pg, 4)
    seen = {}
    for n, c in asked: seen.setdefault(n, set()).add(c)
    R['placement_knows_1_to_4'] = {'result': head, 'sub': sub, 'letters_asked_per_unit': {n: len(s) for n, s in seen.items()}, 'unit_sizes': {u['n']: len(u['letters']) for u in U if 1 <= u['n'] <= 5}}
    js(pg, pg.query_selector("button:has-text('Go')")); pg.wait_for_timeout(1500)
    R['placement_after_go'] = DUMP(pg)
    b.close()
    # ---- placement: knows nothing -> stops at first unit
    b, pg = fresh(p); asked, head, sub = placement(pg, 0); R['placement_knows_nothing'] = {'result': head, 'sub': sub, 'questions_asked': len(asked)}; b.close()
    # ---- placement: knows everything (letters only)
    b, pg = fresh(p); asked, head, sub = placement(pg, 99); R['placement_knows_all_letters'] = {'result': head, 'sub': sub, 'questions_asked': len(asked)}; b.close()
    # ---- gating bypass: Units tab -> locked unit 5 -> confirm -> full lesson page with quiz
    b, pg = fresh(p, 'Gate')
    js(pg, pg.query_selector("button:has-text('All units')")) if pg.query_selector("button:has-text('All units')") else js(pg, pg.query_selector(".bottom button[data-k=units]"))
    pg.wait_for_timeout(900)
    cards = pg.query_selector_all('.ucard'); R['units_tab'] = {'cards': len(cards), 'locked_classes': sum(1 for c in cards if 'locked' in (c.get_attribute('class') or ''))}
    js(pg, cards[5]); pg.wait_for_timeout(1200)
    R['open_locked_unit5'] = {'dialog': R.get('dialogs', [])[-1:], 'page_h1': pg.inner_text('#app h1')[:60], 'has_quiz': bool(pg.query_selector('ol li .tile')), 'sections': [h.inner_text()[:40] for h in pg.query_selector_all('#app h3')][:10]}
    # pass the quiz by oracle (roman -> urdu)
    for li in pg.query_selector_all('ol li'):
        m = re.search(r'Which one says (\S+)', li.inner_text())
        if not m: continue
        for u in U:
            for w in u['words']:
                if w[1] == m.group(1):
                    for t in li.query_selector_all('.tile'):
                        if t.inner_text().strip() in (w[0], w[3] if len(w) > 3 else w[0]): js(pg, t); break
    sub = pg.query_selector("button:has-text('Submit')"); js(pg, sub); pg.wait_for_timeout(800)
    R['quiz_result_text'] = pg.evaluate("document.querySelector('.score')?.textContent")
    R['state_after_bypass'] = DUMP(pg)
    pg.evaluate("window.scrollTo(0,0)"); js(pg, pg.query_selector(".bottom button[data-k=today]")); pg.wait_for_timeout(1500)
    R['learn_screen_after_bypass'] = {'cur_text': (pg.query_selector('.hh-h3') and pg.inner_text('.today-card'))[:120] if pg.query_selector('.today-card') else None, 'unit_pills': [x.inner_text() for x in pg.query_selector_all('.card.unit .pill')][:4], 'passed_pills': len(pg.query_selector_all('.card.unit .pill[style*=good]'))}
    b.close()
    # ---- aspirates audio in the path lesson (unit 6): tamper progress so the lesson is reachable
    b, pg = fresh(p, 'Asp')
    pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const {C,loadContent}=await import('/src/content.js'); await loadContent(); const prof=(await db.all('profiles'))[0]; const pr=(await db.get('progress',prof.id))||{id:prof.id,units:{},wpm:[],sessions:0};
      for (let n=0;n<6;n++) pr.units[n]={passed:true,score:10,total:10,lessons:{}}; const u=C.units[6]; pr.units[6]={lessons:{...Object.fromEntries(u.letters.map(c=>['L'+C.by[c].id,Date.now()]))}}; await db.put('progress',pr); }""")
    pg.reload(); pg.wait_for_timeout(2500)
    js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1500)
    js(pg, pg.query_selector("button:has-text('Continue:'), button:has-text('Start:')")); pg.wait_for_timeout(1200)
    R['aspirates_screen_title'] = pg.inner_text('#app h1')[:50]
    rows = pg.query_selector_all('#app table tr'); res = []
    for r in rows:
        btns = r.query_selector_all('button.btn-play'); res.append({'row': r.inner_text().replace('\n', ' ')[:40], 'play_buttons': len(btns)})
    R['aspirates_rows'] = res
    # click every play button, record which audio got requested
    plays = []
    for bt in pg.query_selector_all('#app table button.btn-play'):
        pg.evaluate("window.__plays=[]"); js(pg, bt); pg.wait_for_timeout(250); plays.append(pg.evaluate("(window.__plays||[]).map(x=>x.split('/audio/')[1])") or [pg.evaluate("document.getElementById('toast')?.textContent")])
    R['aspirates_clicks'] = plays
    b.close()
json.dump(R, open(HERE + '/ui_checks.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1))
