#!/usr/bin/env python3
"""EGRA through the REAL egra.js with a fake clock (Playwright clock). Passage traps + comprehension-aware overall level."""
import json
from common import *
R = {}
with sync_playwright() as p:
    b, pg = bare(p)
    pg.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=egra-root></div>')"); pg.clock.install()
    N = pg.evaluate("(async()=>{const {loadContent,C}=await import('/src/content.js'); await loadContent(); return C.letters.assessment.passage.split(/\\s+/).filter(Boolean).length})()"); R['passage_words'] = N
    def start():
        pg.evaluate("""async () => { window.__res = null; const E = await import('/src/egra.js'); document.getElementById('egra-root').innerHTML=''; E.runEgra(document.getElementById('egra-root'), null, {id:'egra-p', name:'Syn'}, r => { window.__res = r; }); }"""); pg.clock.run_for(300)
    t = lambda: pg.inner_text('#egra-root h2')
    def to_passage():
        start()
        for _ in range(3): pg.click('#egra-root button:has-text("Skip")'); pg.clock.run_for(50)
        assert 'Passage' in t(), t()
    def comp(correct):
        for k in range(5): pg.click('#egra-root button:has-text("%s")' % ('Correct' if k < correct else 'Incorrect')); pg.clock.run_for(20)
    def rows(): return {k.strip(): v.strip() for k, v in (r.split('\t') for r in pg.inner_text('#egra-root table').split('\n') if '\t' in r)}
    def click(txt): pg.click(f'#egra-root button:has-text("{txt}")'); pg.clock.run_for(30)
    def word(i): pg.click(f'#egra-root .item[data-i="{i}"]'); pg.clock.run_for(10)
    note = lambda: pg.inner_text('#egra-root p[role=status]')
    S = {}
    # 1. accidental Finish at 0.2 s and 1 s and 14 s: ignored, still on the passage, timer still running
    to_passage(); pg.clock.run_for(200); click('Child finished'); S['finish_at_0.2s'] = {'still_passage': 'Passage' in t(), 'note': note()}
    pg.clock.run_for(800); click('Child finished'); S['finish_at_1s'] = {'still_passage': 'Passage' in t()}
    pg.clock.run_for(13000); click('Child finished'); S['finish_at_14s'] = {'still_passage': 'Passage' in t()}
    # ... and the forgotten-mark timeout afterwards: no score is made up
    pg.clock.run_for(50000); S['timeout_without_mark'] = {'still_passage': 'Passage' in t(), 'note': note(), 'score_button': pg.inner_text('#egra-root .row button:nth-of-type(2)')}
    # 2. the headline trap: 12 words read in 60 s, teacher forgot to mark -> must NOT become 52 cwpm. Teacher is asked, taps word 12, scores.
    word(11); click('Score it'); comp(0); S['12_words_forgot_mark_then_asked'] = dict(rows())
    # 3. 12 words, marked in time
    to_passage(); click('Mark last word reached'); word(11); pg.clock.run_for(60500); S['12_words_marked_cwpm'] = {'passage_after': t()}; comp(5); S['12_words_marked_rows'] = rows()
    # 4. nothing read ('Read no words') -> 0
    to_passage(); pg.clock.run_for(60500); click('Read no words'); comp(5); S['read_none'] = rows()
    # 5. finish at 36 s with no mark: asked; whole passage -> 52 words/36 s
    to_passage(); pg.clock.run_for(36000); click('Child finished'); S['finish_36s_asks'] = {'ask_visible': pg.is_visible('#egra-root button:has-text("Read to the end")')}; click('Read to the end'); comp(5); S['finish_36s_whole_passage'] = rows()
    # 6. finish at 36 s, child stopped early at word 20: choose "stopped early", tap word, Finish -> 20 words/36 s
    to_passage(); pg.clock.run_for(36000); click('Child finished'); click('Stopped early'); word(19); click('Child finished'); comp(5); S['finish_36s_stopped_word20'] = rows()
    # 7. every word wrong, whole passage read -> 0 cwpm
    to_passage(); [word(i) for i in range(N)]; pg.clock.run_for(40000); click('Child finished'); click('Read to the end'); comp(5); S['all_words_wrong'] = rows()
    # 8. finish at exactly 15 s whole passage -> 208 raw -> capped at 200 and flagged
    to_passage(); pg.clock.run_for(15000); click('Child finished'); click('Read to the end'); comp(5); S['whole_passage_in_15s'] = rows()
    # 9. comprehension: fluent 90 cwpm with 0/5, 3/5, 4/5, skipped
    for label, c in [('comp_0', 0), ('comp_3', 3), ('comp_4', 4), ('comp_5', 5)]:
        to_passage(); pg.clock.run_for(34667); click('Child finished'); click('Read to the end'); comp(c); S[label] = rows()   # 52 words in 34.7 s = 90 cwpm
    to_passage(); pg.clock.run_for(34667); click('Child finished'); click('Read to the end'); click('Skip'); S['comp_skipped'] = rows()
    # 10. what gets saved
    click('Save assessment'); pg.clock.run_for(200); S['saved_record'] = pg.evaluate("window.__res && {cwpm: window.__res.orf.cwpm, band: window.__res.band, level: window.__res.level, compDone: window.__res.compDone}")
    R['scenarios'] = S; R['page_errors'] = pg.errors; b.close()
json.dump(R, open(HERE + '/t5_egra.json', 'w'), ensure_ascii=False, indent=1)
for k, v in R['scenarios'].items(): print(k, '->', json.dumps(v, ensure_ascii=False)[:420])
print('errors', R['page_errors'])
