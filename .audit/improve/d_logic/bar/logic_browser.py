#!/usr/bin/env python3
"""Drives the REAL modules (session.js, egra.js, drills.js) in the dev-server page with Playwright: Leitner math with a fake clock,
gating by tampering, unit-check retry, placement, EGRA scoring with synthetic taps. Output: logic_browser.json"""
import json, os, re, sys
from playwright.sync_api import sync_playwright
PORT = os.environ.get('PORT', '5188'); HERE = os.path.dirname(os.path.abspath(__file__)); R = {}
EXE = '/home/oye/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE); pg = b.new_page(viewport={'width': 390, 'height': 800}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('dialog', lambda d: d.accept())
    pg.goto(f'http://localhost:{PORT}/?skiponb'); pg.wait_for_timeout(2500)
    pg.click('text=Just me'); pg.wait_for_timeout(400); pg.click('text=+ Add a learner'); pg.wait_for_timeout(300); pg.fill('input[placeholder=Name]', 'Tester')
    # ---------- Leitner ----------
    R['leitner'] = pg.evaluate("""async () => {
      const S = await import('/src/session.js'); const {C, loadContent} = await import('/src/content.js'); const {db} = await import('/src/db.js'); await loadContent();
      const pid = 'logic-test-1'; for (const c of await db.by('cards','profileId',pid)) await db.del('cards', c.id);
      const real = Date.now; let now = real(); Date.now = () => now; const DAY = 86400000; const out = {};
      await S.ensureCards(pid, 3);
      let cards = await db.by('cards','profileId',pid);
      const expLetters = C.units.filter(u=>u.n<3).flatMap(u=>u.letters).filter(c=>C.by[c]).length, expWords = C.units.filter(u=>u.n<3).reduce((n,u)=>n+u.words.length,0);
      out.cards_after_ensure_unit3 = {total: cards.length, letters: cards.filter(c=>c.kind==='letter').length, expLetters, words: cards.filter(c=>c.kind==='word').length, expWords, allDueNow: cards.every(c=>c.due<=now)};
      // always-correct ladder on one card
      let c0 = cards.find(c=>c.kind==='letter'); const ladder = [];
      for (let i=0;i<7;i++){ await S.gradeCard(c0, true); c0 = (await db.by('cards','profileId',pid)).find(c=>c.id===c0.id); ladder.push({box:c0.box, due_in_days:Math.round((c0.due-now)/DAY)}); }
      out.correct_ladder = ladder;
      // wrong from box 5 goes to box 1
      await S.gradeCard(c0, false); c0 = (await db.by('cards','profileId',pid)).find(c=>c.id===c0.id); out.after_wrong = {box:c0.box, due_in_days:Math.round((c0.due-now)/DAY), seen:c0.seen, lastOk:c0.lastOk};
      // due logic: nothing due tomorrow-1, due after advancing
      const dueNow = (await S.dueCards(pid, 12)).length; const dueAll = (await S.dueCards(pid, 999)).length; out.due = {limit12: dueNow, all: dueAll, total: (await db.by('cards','profileId',pid)).length};
      now += 1*DAY + 1000; out.due_after_1day = (await S.dueCards(pid, 999)).length;
      // ordering: lowest box first then oldest due
      const ds = await S.dueCards(pid, 999); out.order_ok = ds.every((c,i)=> i===0 || ds[i-1].box < c.box || (ds[i-1].box===c.box && ds[i-1].due<=c.due));
      // no card disappears: grade 40 random answers then count
      for (let i=0;i<40;i++){ const all = await db.by('cards','profileId',pid); await S.gradeCard(all[i%all.length], i%3!==0); }
      out.total_after_40_grades = (await db.by('cards','profileId',pid)).length;
      // re-ensure does not reset boxes
      const before = JSON.stringify((await db.by('cards','profileId',pid)).map(c=>[c.id,c.box,c.due]).sort()); await S.ensureCards(pid, 3); const after = JSON.stringify((await db.by('cards','profileId',pid)).map(c=>[c.id,c.box,c.due]).sort()); out.ensure_idempotent = before===after;
      // card id collisions: sight words + duplicate words
      await S.ensureCards(pid, 12); cards = await db.by('cards','profileId',pid);
      const allWords = C.units.flatMap(u=>u.words.map(w=>w[0])); out.at_unit12 = {cards: cards.length, uniqueWordsInUnits: new Set(allWords).size, sightCards: cards.filter(c=>c.kind==='sight').length, sightWords: C.letters.sight_words.length, wordCards: cards.filter(c=>c.kind==='word').length, letterCards: cards.filter(c=>c.kind==='letter').length};
      // a sight card's audio key + word card audio key resolve
      const miss = []; for (const c of cards){ const k = S.audioKeyFor(c); if (!C.audio[k]) miss.push([c.item,k]); } out.cards_with_unresolved_audio = miss.slice(0,10); out.n_unresolved = miss.length;
      // preview words in Leitner before their letters are taught
      Date.now = real; return out; }""")
    # ---------- gating by tampering ----------
    R['gating'] = pg.evaluate("""async () => {
      const S = await import('/src/session.js'); const {db} = await import('/src/db.js'); const pid='logic-test-2'; await db.del('progress', pid);
      const o = {}; o.fresh = await S.currentUnit(pid);
      await S.markUnit(pid, 5, 9, 10); o.after_pass_unit5_only = await S.currentUnit(pid);      // tamper: pass unit 5 without 0-4
      await S.markUnit(pid, 0, 10, 10); await S.markUnit(pid, 1, 7, 10); o.unit1_7of10_passed = (await S.getProgress(pid)).units[1].passed;
      await S.markUnit(pid, 1, 8, 10); o.unit1_8of10_passed = (await S.getProgress(pid)).units[1].passed;
      await S.markUnit(pid, 1, 0, 10); o.unit1_after_later_0 = (await S.getProgress(pid)).units[1].passed;     // passed is sticky
      for (const n of [2,3,4]) await S.markUnit(pid, n, 10, 10); o.after_filling_gap_jumps_to = await S.currentUnit(pid);  // unit 5 pre-passed => jumps to 6
      o.threshold_total10 = Math.ceil(10*0.8); return o; }""")
    # ---------- EGRA scoring through the real module ----------
    pg.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=egra-root></div>')")
    R['egra_setup'] = 'ok'
    def egra_run(letters_wrong=0, passage_mode='finish', last_idx=None, wait_s=0):
        pg.evaluate("""async () => { window.__res = null; const E = await import('/src/egra.js'); const {db} = await import('/src/db.js'); document.getElementById('egra-root').innerHTML='';
          E.runEgra(document.getElementById('egra-root'), null, {id:'egra-p', name:'Syn'}, r => { window.__res = r; }); }""")
        pg.wait_for_timeout(600)
        return None
    # we drive subtasks with a controllable clock
    pg.evaluate("async () => { window.__res=null }")
    pg.clock.install()
    def start():
        pg.evaluate("""async () => { window.__res = null; const E = await import('/src/egra.js'); document.getElementById('egra-root').innerHTML='';
          E.runEgra(document.getElementById('egra-root'), null, {id:'egra-p', name:'Syn'}, r => { window.__res = r; }); }""")
        pg.clock.run_for(300)
    def title(): return pg.inner_text('#egra-root h2')
    def skip():
        pg.click('#egra-root button:has-text("Skip")'); pg.clock.run_for(50)
    scen = {}
    # scenario A: skip subtasks 1-3, passage: tap "Child finished" after 36 s, no errors, no 'last word' mark -> all 52 words counted
    start(); [skip() for _ in range(3)]
    scen['A_title'] = title(); pg.clock.run_for(36000); pg.click('#egra-root button:has-text("Child finished")'); pg.clock.run_for(50)
    scen['A_after_passage'] = title()
    # comprehension: 3 correct
    for k in range(5): pg.click('#egra-root button:has-text("Correct")' if k < 3 else '#egra-root button:has-text("Incorrect")'); pg.clock.run_for(20)
    scen['A_result_rows'] = pg.inner_text('#egra-root table').replace('\t', ' | ').replace('\n', ' ; ')
    pg.click('#egra-root button:has-text("Save assessment")'); pg.clock.run_for(200); scen['A_saved'] = pg.evaluate('window.__res && {cwpm: window.__res.orf.cwpm, band: window.__res.band, level: window.__res.level}')
    # scenario B: child reads only 12 words in 60 s, teacher marks word 12 -> expect 12 cwpm
    start(); [skip() for _ in range(3)]
    pg.click('#egra-root button:has-text("Mark last word reached")'); pg.click('#egra-root .item[data-i="11"]'); pg.clock.run_for(60500)
    scen['B_after'] = title()
    for k in range(5): pg.click('#egra-root button:has-text("Skip")') if False else pg.click('#egra-root button:has-text("Incorrect")'); pg.clock.run_for(20)
    scen['B_rows'] = pg.inner_text('#egra-root table').replace('\n', ' ; ')
    # scenario C: same but teacher forgets to mark last word -> times out at 60 s
    start(); [skip() for _ in range(3)]; pg.clock.run_for(60500)
    for k in range(5): pg.click('#egra-root button:has-text("Incorrect")'); pg.clock.run_for(20)
    scen['C_timeout_no_mark_rows'] = pg.inner_text('#egra-root table').replace('\n', ' ; ')
    # scenario D: letter-sounds: stop rule (first 10 wrong) and a normal 60 s run with 5 wrong on page 1
    start(); pg.click('#egra-root button:has-text("Skip")') if False else None
    for i in range(10): pg.click(f'#egra-root .item[data-i="{i}"]')
    pg.clock.run_for(100); scen['D_after_stop_rule'] = title()
    start(); [pg.click(f'#egra-root .item[data-i="{i}"]') for i in range(3)]; pg.click('#egra-root button:has-text("Next")'); pg.click('#egra-root button:has-text("Next")'); pg.clock.run_for(60500)
    scen['E_letters_3wrong_reached_page3_title_after'] = title()
    R['egra'] = scen
    # fast reader: results for 20s finish
    b.close(); R['page_errors'] = errs[:5]
json.dump(R, open(HERE + '/logic_browser.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1)[:6000])
