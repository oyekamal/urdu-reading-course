#!/usr/bin/env python3
"""Offline analysis of drive_audit_raw.json (recorded while driving every lesson of units 0-12 in the real app)."""
import json, os, re, collections, unicodedata
ROOT = os.path.expanduser('~/Documents/free_work/urdu-reading-course'); HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(HERE + '/drive_audit_raw.json')); L = json.load(open(ROOT + '/data/letters.json', encoding='utf8')); BYID = {l['id']: l for l in L['letters']}; BYCH = {l['ch']: l for l in L['letters']}
U = json.load(open(ROOT + '/data/units.json', encoding='utf8'))['units']; M = re.compile('[ً-ْٰـ]'); TAT = 'ـ'
VOW = {'a': 'ا', 'i': 'ی', 'u': 'و'}; HOM = {'س':'s','ث':'s','ص':'s','ز':'z','ذ':'z','ض':'z','ظ':'z','ت':'t','ط':'t','ہ':'h','ح':'h'}
def sound(ch): return HOM.get(ch, ch)
out = collections.OrderedDict(); issues = []
rec = D['rec']; out['questions_recorded'] = len(rec)
kinds = collections.Counter((r['key'].split('/')[0] if r['key'] else 'none') for r in rec); out['by_audio_kind'] = dict(kinds)
two_opt = []; dup_choices = []; missing_t = []; multi = []; dr_mis = []; hom_rounds = []; unmatched = []
per_unit = collections.defaultdict(lambda: collections.Counter())
for r in rec:
    ch = r['choices']; key = r['key'] or ''; kind, _, ident = key.partition('/'); un = r['unit']
    per_unit[un]['q'] += 1
    # duplicate / look-alike choices
    norm = [M.sub('', c) for c in ch]
    if len(set(norm)) != len(norm) and 'Make:' not in r['q']: dup_choices.append((un, r['q'][:90], ch))
    if len(ch) <= 2 and 'Make:' not in r['q']: two_opt.append((un, r['q'][-70:], ch))
    # independent target from audio key
    exp = None
    if kind == 'names' and ident in BYID: exp = BYID[ident]['ch']
    elif kind == 'syllables':
        lid, _, v = ident.rpartition('_'); exp = BYID[lid]['ch'] + VOW[v]
    elif kind == 'sight': exp = L['sight_words'][int(ident)]
    elif kind == 'units':
        a, _, b = ident.partition('_'); w = U[int(a[1:])]['words'][int(b)]; exp = (w[0], w[3] if len(w) > 3 else w[0])
    r['_exp'] = exp
    if r.get('data_right') and r['data_right'] != key: dr_mis.append((un, r['q'], r['data_right'], key))
    if r.get('unmatched'): unmatched.append((un, r['q'], key, ch))
    # does a tile exist for the expected answer, exactly once?
    textq = bool(re.search(r'Which is|Question \d/4.*Tap |Which one says|Make:', r['q'])) 
    if textq and r.get('target') is not None:
        tcount = sum(1 for c in ch if c == r['target'])
        if tcount != 1 and 'Make:' not in r['q']: multi.append((un, r['q'][-60:], r['target'], ch, tcount))
    if exp and r.get('target') is not None and not textq:
        e = exp if isinstance(exp, tuple) else (exp,)
        cnt = sum(1 for c in ch if c in e or M.sub('', c) in [M.sub('', x) for x in e])
        if kind in ('names', 'syllables', 'sight') and cnt != 1: multi.append((un, r['q'], key, ch, cnt))
    # same-sound distractors in syllable rounds
    if kind == 'syllables' and exp:
        same = [c for c in ch if len(c) == 2 and sound(c[0]) == sound(exp[0]) and c[1] == exp[1]]
        if len(same) > 1: hom_rounds.append((un, key, ch, same))
out['duplicate_look_alike_choices'] = dup_choices[:10]; out['n_duplicate_choice_screens'] = len(dup_choices); out['two_option_questions'] = two_opt[:10]; out['n_two_option_questions'] = len(two_opt)
out['data_right_vs_played_key_mismatch'] = dr_mis[:10]; out['target_not_exactly_once_in_choices'] = multi[:15]; out['n_target_problems'] = len(multi)
out['same_sound_options_in_syllable_rounds'] = hom_rounds[:12]; out['n_same_sound_rounds'] = len(hom_rounds)
out['driver_could_not_identify_target'] = unmatched[:12]; out['n_unidentified'] = len(unmatched)
# quiz
qz = D['quiz']; bad_q = []
allw = {w[1]: w for u in U for w in u['words']}
for q in qz:
    w = allw.get(q['rom']); 
    if not w: bad_q.append(('unknown rom', q)); continue
    e = (w[0], w[3] if len(w) > 3 else w[0]); n = sum(1 for c in q['choices'] if c in e)
    if n != 1: bad_q.append((q['unit'], q['rom'], q['choices'], n))
    if len(set(M.sub('', c) for c in q['choices'])) != len(q['choices']): bad_q.append(('dup', q['unit'], q['rom'], q['choices']))
out['quiz_questions_recorded'] = len(qz); out['quiz_problems'] = bad_q[:10]
# hints
hints = D['hints']; out['wrong_taps_with_hint'] = len(hints); hbad = []
NUM = {'no': 0, 'one': 1, 'two': 2, 'three': 3}
truth = json.load(open(HERE + '/dots_truth.json'))
for h in hints:
    t = h['hint'] or ''; m = re.match(r'Count the dots: (\S+) has (\w+)', t)
    if m:
        ch = m.group(1); said = NUM[m.group(2)]
        # truth: isolated-form dots (the form the tile shows)
        iso = {'ی': 0, 'ٹ': 0, 'ڈ': 0, 'ڑ': 0, 'ئ': 0}.get(ch)
        if iso is not None and said != iso: hbad.append((h['unit'], h['hint'], 'tile shows the isolated glyph with ' + str(iso) + ' dots'))
out['wrong_hint_examples'] = hbad; out['hint_texts'] = collections.Counter(re.sub(r'(has|is|dots:) \S+', r'\1 X', (h['hint'] or 'NONE')) for h in hints).most_common(8)
json.dump(out, open(HERE + '/analyze_drills.json', 'w'), ensure_ascii=False, indent=1, default=str); print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:7000])
