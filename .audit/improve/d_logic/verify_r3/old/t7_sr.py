#!/usr/bin/env python3
"""In-lesson mistakes feed spaced repetition. UI: wrong tap in the real 'tap what you hear' drill; direct: real session.recordAttempt for every drill kind.
Leitner math regression: gradeCard sequence + ordering checked against the documented table."""
import json
from common import *
R = {}
with sync_playwright() as p:
    b, pg = fresh(p, 'SR')
    pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const {loadContent,C}=await import('/src/content.js'); await loadContent(); const S=await import('/src/session.js'); const prof=(await db.all('profiles'))[0];
      const pr={id:prof.id,units:{},wpm:[],sessions:0}; pr.units[0]={passed:true,score:10,total:10,lessons:{}}; pr.units[1]={lessons:{Lalif:Date.now()}}; await db.put('progress',pr);
      await db.put('cards',{id:prof.id+':ب',profileId:prof.id,item:'ب',kind:'letter',box:4,due:Date.now()+8*86400000,seen:7}); }""")
    pg.reload(); pg.wait_for_timeout(2500)
    js(pg, pg.query_selector(".bottom button:has-text('Learn')")); pg.wait_for_timeout(1200); js(pg, pg.query_selector("button:has-text('Continue:'), button:has-text('Start:')")); pg.wait_for_timeout(1000)
    R['lesson'] = pg.inner_text('#app h1')[:30]
    for _ in range(6):
        if pg.query_selector('.choices .tile'): break
        c = pg.query_selector('.btn-primary.btn-wide:not(.act)')
        if c: js(pg, c); pg.wait_for_timeout(800)
    got = False
    for _ in range(40):
        tiles = pg.query_selector_all('.choices .tile'); right = [t for t in tiles if t.get_attribute('data-right')]
        if len(tiles) >= 2 and not right: js(pg, tiles[0]); pg.wait_for_timeout(500); continue      # first tap only starts round 1
        if len(tiles) < 2: pg.wait_for_timeout(300); c = pg.query_selector('.btn-primary.btn-wide:not(.act)'); (js(pg, c) if c else None); continue
        key = right[0].get_attribute('data-right')
        if key == 'names/be' and not got: js(pg, [t for t in tiles if t is not right[0]][0]); got = True; pg.wait_for_timeout(400); break
        js(pg, right[0]); pg.wait_for_timeout(600)
    R['wrong_tap_on_be_happened'] = got
    R['card_be_after_ui_miss'] = pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const prof=(await db.all('profiles'))[0]; const c=await db.get('cards', prof.id+':ب'); return {box:c.box, seen:c.seen, due_in_days:+((c.due-Date.now())/86400000).toFixed(2), lastOk:c.lastOk}; }""")
    R['direct'] = pg.evaluate("""async () => { const {db}=await import('/src/db.js'); const S=await import('/src/session.js'); const {C,loadContent}=await import('/src/content.js'); await loadContent(); const prof=(await db.all('profiles'))[0]; const out={}; const day=86400000;
      const card=async it=>{const c=await db.get('cards',prof.id+':'+it); return c?{kind:c.kind,box:c.box,due_days:+((c.due-Date.now())/day).toFixed(2),seen:c.seen,unit:c.unit,idx:c.idx}:null};
      const w=C.units[3].words[2][0]; const sw=C.letters.sight_words[1];
      out.before={w:await card(w), letter:await card('ک')};
      await S.recordAttempt(prof.id,1,'quiz',w,false,0); out.word_quiz_miss=await card(w);
      await S.recordAttempt(prof.id,1,'blend','کی',false,0); out.blend_miss_sends_letter=await card('ک');
      await S.recordAttempt(prof.id,1,'tell','ن',true,0); out.correct_answer_creates_nothing=await card('ن');
      await S.recordAttempt(prof.id,1,'sight',sw,false,0); out.sight_miss=await card(sw);
      await S.recordAttempt(prof.id,1,'dictation',w,false,0); out.dictation_miss=await card(w);
      await S.recordAttempt(prof.id,1,'trace','ک',false,0); out.trace_miss_ignored_for_SR=(await card('ک'))?.seen;
      await S.recordAttempt(prof.id,1,'self-letters','letters',false,0); out.self_test_not_a_card=await card('letters');
      // a card already due earlier must not be postponed
      await db.put('cards',{id:prof.id+':م',profileId:prof.id,item:'م',kind:'letter',box:2,due:Date.now()-3*day,seen:1}); await S.recordAttempt(prof.id,1,'tell','م',false,0); out.overdue_not_postponed=await card('م');
      const due=await S.dueCards(prof.id,50); out.due_includes_overdue=due.some(c=>c.item==='م');
      // Leitner math: untouched. box1 -1d(1), correct x5 -> boxes 2..5 days 2,4,8,16,16 ; wrong from box5 -> box1, 1 day
      const t={id:prof.id+':ا',profileId:prof.id,item:'ا',kind:'letter',box:1,due:0,seen:0}; const seq=[]; let c=t;
      for (let i=0;i<5;i++){ await S.gradeCard(c,true); c=await db.get('cards',t.id); seq.push([c.box,Math.round((c.due-Date.now())/day)]); }
      await S.gradeCard(c,false); c=await db.get('cards',t.id); seq.push([c.box,Math.round((c.due-Date.now())/day)]); out.leitner_sequence=seq;
      return out; }""")
    R['page_errors'] = pg.errors; b.close()
d = R['direct']
checks = {
 'ui_wrong_tap_demoted_box4_card': R['card_be_after_ui_miss']['box'] == 1 and R['card_be_after_ui_miss']['due_in_days'] <= 1.01 and R['card_be_after_ui_miss']['seen'] == 7,
 'word_quiz_miss_creates_card_box1_due<=1d': bool(d['word_quiz_miss']) and d['word_quiz_miss']['box'] == 1 and d['word_quiz_miss']['kind'] == 'word' and d['word_quiz_miss']['due_days'] <= 1.01 and d['word_quiz_miss']['unit'] == 3,
 'blend_miss_sends_the_letter': bool(d['blend_miss_sends_letter']) and d['blend_miss_sends_letter']['box'] == 1,
 'correct_answer_changes_nothing': d['correct_answer_creates_nothing'] is None,
 'sight_miss': bool(d['sight_miss']) and d['sight_miss']['kind'] in ('sight', 'word'),
 'overdue_not_postponed': d['overdue_not_postponed']['box'] == 1 and d['overdue_not_postponed']['due_days'] < 0 and d['due_includes_overdue'],
 'leitner_unchanged_2_4_8_16_16_then_1': d['leitner_sequence'] == [[2, 2], [3, 4], [4, 8], [5, 16], [5, 16], [1, 1]],
 'self_test_row_is_not_a_card': d['self_test_not_a_card'] is None,
}
R['checks'] = checks; R['all_pass'] = all(checks.values())
json.dump(R, open(HERE + '/t7_sr.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1)[:3500])
