#!/usr/bin/env python3
"""Pure-data simulations of app logic (no UI): (1) unit-check cheat bot that knows NO Urdu letters, (2) placement coverage,
(3) homophone options in blend drills, (4) Leitner interval table, (5) EGRA cwpm formula edge cases (re-implemented from egra.js lines 169-180)."""
import json, os, re, random, unicodedata, itertools, math, collections
ROOT = os.path.expanduser('~/Documents/free_work/urdu-reading-course')
LET = json.load(open(ROOT + '/data/letters.json', encoding='utf8')); L = LET['letters']; BY = {l['ch']: l for l in L}
U = json.load(open(ROOT + '/data/units.json', encoding='utf8'))['units']
MARKS = re.compile('[ً-ْٰـ]'); random.seed(1); out = {}
def known(n, ul):
    k = {c for u in U if u['n'] < n for c in u['letters'] if c in BY} | {c for c in ul if c in BY} | {'ـ'}
    if n >= 10: k |= set('ءئؤآۃ')
    return k
def spell(n, ul, ur): k = known(n, ul); return all(c in k or MARKS.match(c) for c in ur)
# (1) cheat bot
def rl(rom): return len(re.sub(r"[^a-z]", '', ''.join(c for c in unicodedata.normalize('NFD', rom.lower()) if not unicodedata.combining(c)).replace('ʾ', '')))
pairs = [(rl(w[1]), len(MARKS.sub('', w[0]))) for u in U for w in u['words']]
n = len(pairs); mx = sum(a for a, _ in pairs) / n; my = sum(b for _, b in pairs) / n
slope = sum((a - mx) * (b - my) for a, b in pairs) / sum((a - mx) ** 2 for a, _ in pairs); icpt = my - slope * mx
res = {}
for u in U:
    if not u['words']: continue
    qw = [w for w in u['words'] if spell(u['n'], u['letters'], w[0])]
    if len(qw) < 4: continue
    passes = 0; T = 4000; tot = 0
    for _ in range(T):
        qs = random.sample(qw, min(10, len(qw))); sc = 0
        for w in qs:
            opts = [w] + random.sample([x for x in qw if x[0] != w[0]], 3); est = slope * rl(w[1]) + icpt
            best = min(abs(len(MARKS.sub('', o[0])) - est) for o in opts); cand = [o for o in opts if abs(len(MARKS.sub('', o[0])) - est) == best]
            sc += random.choice(cand) is opts[0] or random.choice(cand)[0] == w[0] and False
            sc += 0
        # redo cleanly (keeps code short): second pass counting correctness once
    # clean simulation
    passes = 0; accsum = 0
    for _ in range(T):
        qs = random.sample(qw, min(10, len(qw))); sc = 0
        for w in qs:
            opts = [w] + random.sample([x for x in qw if x[0] != w[0]], 3); est = slope * rl(w[1]) + icpt
            d = [abs(len(MARKS.sub('', o[0])) - est) for o in opts]; m = min(d); pick = random.choice([o for o, x in zip(opts, d) if x == m]); sc += pick[0] == w[0]
        passes += sc >= 8; accsum += sc
    res[u['n']] = {'pass_rate_pct': round(100 * passes / T, 2), 'mean_score_of_10': round(accsum / T, 2)}
out['quiz_length_bot(knows zero letters; guess=25%)'] = res
# random guesser for reference
out['quiz_random_guess_pass_pct'] = round(100 * sum(math.comb(10, k) * 0.25 ** k * 0.75 ** (10 - k) for k in range(8, 11)), 4)
# (2) placement coverage: stage draws 6 targets WITH replacement from the unit's letters; pass needs >=5/6
plc = {}
for u in U:
    ls = [c for c in u['letters'] if c in BY]
    if not ls: continue
    k = len(ls); t = 20000; unseen = 0; missed_all = 0
    for _ in range(t):
        d = {random.choice(ls) for _ in range(6)}; unseen += len(d) < k
    # a learner who knows ONLY the letters drawn... probability that a learner ignorant of exactly 1 letter passes the stage
    pass1 = sum(1 for _ in range(t) if sum(random.choice(ls) != ls[0] or random.random() < 1/6 for _ in range(6)) >= 5) / t
    plc[u['n']] = {'letters': k, 'P(some letter never asked)': round(unseen / t, 3), 'P(learner who does NOT know one letter still passes)': round(pass1, 3)}
out['placement'] = plc
# pure guesser passing whole placement (6 options, p=1/6 per question, need >=5 of 6 per unit, units 1..10)
pg = sum(math.comb(6, k) * (1/6) ** k * (5/6) ** (6 - k) for k in (5, 6)); out['placement_guesser_clears_unit1_pct'] = round(100 * pg, 3)
# (3) homophone classes among blend options (consonant+long vowel clips are phonetically identical within a class)
CLS = {'س':'s','ث':'s','ص':'s','ز':'z','ذ':'z','ض':'z','ظ':'z','ت':'t','ط':'t','ہ':'h','ح':'h'}
hom = {}
for u in U:
    cons = [BY[c] for c in u['letters'] if c in BY and BY[c]['role'] == 'consonant' and not BY[c]['never_initial']]
    groups = collections.defaultdict(list)
    for l in cons: groups[CLS.get(l['ch'], l['ch'])].append(l['ch'])
    h = {k: v for k, v in groups.items() if len(v) > 1}
    if h: hom[u['n']] = h
out['same_sound_consonants_inside_a_unit_blend_pool'] = hom
# also across the whole 'tell apart' pool is names (distinct) -> n/a. Letter lesson blend uses vowels only -> n/a
# probability a 4-option blend round has >=2 same-sound options (unit 9), pool = consonants x 3 vowels (vowels learned: a,i,u => 3)
u9 = [l for l in U if l['n'] == 9][0]; cons9 = [c for c in u9['letters'] if BY[c]['role'] == 'consonant' and not BY[c]['never_initial']]
opts = [(c, v) for c in cons9 for v in 'aiu']; bad = 0; T = 20000
for _ in range(T):
    t = random.choice(opts); pick = [t] + random.sample([o for o in opts if o != t], 3)
    if sum(1 for o in pick if CLS.get(o[0], o[0]) == CLS.get(t[0], t[0]) and o[1] == t[1]) > 1: bad += 1
out['unit9_blend_round_has_two_identical_sounding_options_pct'] = round(100 * bad / T, 1)
# (4) Leitner table from session.js
BOX = [0, 1, 2, 4, 8, 16]
out['leitner'] = {'box_days': BOX, 'sequence_for_always_correct_from_box1': [BOX[min(b, 5)] for b in range(2, 7)], 'wrong_goes_to_box1_due_days': BOX[1]}
# (5) EGRA passage formula, copy of egra.js finish()
words = LET['assessment']['passage'].split(); N = len(words)
def cwpm(attempted, errors, seconds): return max(0, round((attempted - errors) * 60 / max(1, seconds)))
out['egra_passage_words'] = N
out['egra_cases'] = {'read 12 words in 60s, teacher forgot to mark last word (attempted=N)': cwpm(N, 0, 60), 'read 12 words in 60s, marked correctly': cwpm(12, 0, 60), 'child finished all, 36s, 0 err': cwpm(N, 0, 36), 'finish pressed at 0.2s by accident': cwpm(N, 0, 0.2), 'exactly 60 correct in 60s': cwpm(60, 0, 60), 'PRP band for 90': ('exceeds' if 90 > 90 else 'meets')}
json.dump(out, open('sim_logic.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(out, ensure_ascii=False, indent=1))
