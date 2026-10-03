#!/usr/bin/env python3
"""Same-sound options. (a) 1000 rounds per unit through the real drills.blendOptions with the same pool the Blend lesson builds;
(b) the old builder (4 random options) for contrast; (c) real UI: unit 9 Blend lesson, many rounds, tiles read from the page."""
import json
from common import *
R = {}
with sync_playwright() as p:
    b, pg = bare(p)
    R['sim'] = pg.evaluate("""async () => {
      const {loadContent, C, soundOf, shuffle} = await import('/src/content.js'); await loadContent(); const D = await import('/src/drills.js');
      const VOW = ['ا','ی','و']; const res = {};
      for (const u of C.units) { const learned = [...C.units.filter(x => x.n < u.n).flatMap(x => x.letters), ...u.letters].filter(c => C.by[c]);
        const cons = u.letters.map(c => C.by[c]).filter(L => L && L.role === 'consonant' && !L.never_initial); const syl = [['a','ا'],['i','ی'],['u','و']].filter(x => learned.includes(x[1]));
        const all = cons.flatMap(L => syl.map(sy => ({L, sy}))); if (all.length < 2) continue;
        const snd = x => soundOf(x.L.ch) + x.sy[0]; let bad = 0, oldBad = 0, noTarget = 0, dup = 0, short = 0, minOpts = 9, pairsSeen = new Set();
        for (let r = 0; r < 1000; r++) { const t = all[Math.floor(Math.random() * all.length)]; const o = D.blendOptions(all, t);
          if (o.filter(x => x === t).length !== 1) noTarget++; if (new Set(o).size !== o.length) dup++; if (o.length < Math.min(4, all.length)) short++; minOpts = Math.min(minOpts, o.length);
          if (new Set(o.map(snd)).size !== o.length) bad++;
          const old = shuffle([t, ...shuffle(all.filter(x => x !== t)).slice(0, 3)]); if (new Set(old.map(snd)).size !== old.length) oldBad++; }
        res[u.n] = {pool: all.length, rounds: 1000, same_sound_rounds_NEW: bad, same_sound_rounds_OLD: oldBad, target_missing_or_twice: noTarget, duplicate_options: dup, fewer_than_4_options: short, min_options: minOpts, homophone_consonants_in_pool: cons.map(L => L.ch).filter(c => soundOf(c) !== c)}; }
      return res; }""")
    b.close()
bad = {n: v for n, v in R['sim'].items() if v['same_sound_rounds_NEW'] or v['target_missing_or_twice'] or v['duplicate_options']}
R['sim_defects'] = bad; json.dump(R, open(HERE + '/t3_blend.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({n: {k: v[k] for k in ('pool','same_sound_rounds_NEW','same_sound_rounds_OLD','fewer_than_4_options','min_options','homophone_consonants_in_pool')} for n, v in R['sim'].items()}, ensure_ascii=False)); print('defects:', bad)
