#!/usr/bin/env python3
"""Placement. (a) 1000 stages per unit through the real drills.placementItems: coverage, a word per stage, option sanity, and the chance
that a learner who misses ONE letter of the unit still clears the stage (guess among the options). (b) real UI runs with an audio-reading oracle."""
import json
from common import *
R = {}
U = json.load(open(os.path.expanduser('~/Documents/free_work/urdu-reading-course/data/units.json'), encoding='utf8'))['units']
L = json.load(open(os.path.expanduser('~/Documents/free_work/urdu-reading-course/data/letters.json'), encoding='utf8'))['letters']; BYID = {l['id']: l for l in L}
with sync_playwright() as p:
    b, pg = bare(p)
    R['sim'] = pg.evaluate("""async () => {
      const {loadContent, C} = await import('/src/content.js'); await loadContent(); const D = await import('/src/drills.js'); const res = {}; let totalQ = 0;
      for (const u of C.units) { if (u.n < 1 || !u.letters.filter(c => C.by[c]).length) continue; const pool = C.units.filter(x => x.n <= u.n).flatMap(x => x.letters).filter(c => C.by[c]); const letters = u.letters.filter(c => C.by[c]);
        let notCovered = 0, noWord = 0, badOpts = 0, passMissOne = 0, passMissOneWeighted = 0, T = 1000, nq = 0, passAll = 0;
        for (let r = 0; r < T; r++) { const items = D.placementItems(u, pool); nq = items.length; const asked = items.filter(i => i.kind === 'letter').map(i => i.target);
          if (new Set(asked).size !== letters.length || asked.length !== letters.length) notCovered++; if (!items.some(i => i.kind === 'word')) noWord++;
          for (const it of items) { const rights = it.options.filter(o => o.right).length; if (rights !== 1 || new Set(it.options.map(o => o.text)).size !== it.options.length || (it.kind === 'letter' && it.options.length < Math.min(6, pool.length)) || (it.kind === 'word' && it.options.length < 2)) badOpts++; }
          // learner knows everything except ONE random letter of the unit: guesses uniformly among the options there
          const miss = letters[Math.floor(Math.random() * letters.length)]; let ok = true; for (const it of items) if (it.kind === 'letter' && it.target === miss && Math.random() >= 1 / it.options.length) ok = false; if (ok) passMissOne++; passAll++; }
        res[u.n] = {letters: letters.length, questions: nq, stages: T, letter_not_covered: notCovered, no_word_item: noWord, bad_option_sets: badOpts, P_pass_when_one_letter_unknown: +(passMissOne / T).toFixed(3)}; totalQ += nq; }
      res.total_questions_if_everything_known = totalQ; return res; }""")
    b.close()
    # ---- UI runs
    NAMES = {}
    def run(p, know, label):
        """know(unitN, kind, target) -> bool. Reads what is PLAYED (audio key) to know the target, then taps the right/wrong tile."""
        b, pg = fresh(p, 'Pl')
        js(pg, pg.query_selector("button:has-text('Take the placement check')")); pg.wait_for_timeout(700); qs = []
        for _ in range(400):
            h2 = pg.query_selector('#app h2'); t = h2.inner_text() if h2 else ''
            m = re.match(r'Unit (\d+) letters', t)
            if not m: break
            n = int(m.group(1)); tiles = pg.query_selector_all('.choices .tile')
            if not tiles: pg.wait_for_timeout(150); continue
            key = pg.evaluate("window.__last||''").split('/audio/')[-1].replace('.mp3', ''); kind = 'word' if key.startswith('units/') else 'letter'
            right = [x for x in tiles if x.get_attribute('data-right')][0]; wrong = [x for x in tiles if x is not right][0]
            qs.append((n, kind, key)); js(pg, right if know(n, kind, key) else wrong); pg.wait_for_timeout(520)
        res = {'label': label, 'result': pg.inner_text('#app h2'), 'sub': pg.inner_text('#app .hero .muted') if pg.query_selector('#app .hero .muted') else '', 'questions': len(qs), 'per_unit': {}, 'page_errors': pg.errors}
        for n, k, _ in qs: res['per_unit'].setdefault(n, {'letter': 0, 'word': 0})[k] += 1
        b.close(); return res
    ui = []
    ui.append(run(p, lambda n, k, key: True, 'knows everything'))
    ui.append(run(p, lambda n, k, key: False, 'knows nothing (first answer wrong)'))
    ui.append(run(p, lambda n, k, key: n <= 4, 'knows units 1-4 completely, then misses unit 5'))
    miss = {'done': False}
    def one_letter_missing(n, k, key):          # knows units 1-4, and in unit 5 everything except the FIRST letter question
        if n < 5: return True
        if k == 'letter' and not miss['done']: miss['done'] = True; return False
        return True
    ui.append(run(p, one_letter_missing, 'knows 1-4, in unit 5 misses one letter (rest right)'))
    R['ui'] = ui
json.dump(R, open(HERE + '/t4_placement.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R['sim'], ensure_ascii=False)); [print(u) for u in R['ui']]
