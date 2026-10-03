#!/usr/bin/env python3
"""Static content-integrity validation for the Urdu Qaida app (read-only: touches no app source).
Run:  python3 check_content.py      -> prints a report, writes check_content.json next to itself.
Sections: A audio, B decodability, C glosses, D duplicates, E letter flags / joining, F rendering, G drill-pool eligibility
"""
import json, os, re, sys, unicodedata, subprocess, collections, itertools
ROOT = os.path.expanduser('~/Documents/free_work/urdu-reading-course')
HERE = os.path.dirname(os.path.abspath(__file__))
PUB = f'{ROOT}/mobile/public'
SRC = f'{ROOT}/mobile/src'
LET = json.load(open(f'{ROOT}/data/letters.json', encoding='utf8'))
UNITS = json.load(open(f'{ROOT}/data/units.json', encoding='utf8'))['units']
LETTERS = LET['letters']
BY = {l['ch']: l for l in LETTERS}
IDX = json.load(open(f'{PUB}/data/audio_index.json'))
MANI = json.load(open(f'{ROOT}/assets/audio/manifest.json'))
OVR = json.load(open(f'{ROOT}/data/audio_overrides.json'))
MARKS = re.compile('[ً-ْٰ]')
TAT = 'ـ'
R = collections.OrderedDict()   # results
F = []                          # findings: (severity, id, text)
def find(sev, fid, text): F.append((sev, fid, text))
def pad(n): return f'{n:02d}'

# ---------------------------------------------------------------- A. audio
exp = {}   # expected key -> expected text (the text that SHOULD have been spoken)
for l in LETTERS:
    exp[f'names/{l["id"]}'] = l['name_ur']
    exp[f'words/{l["id"]}'] = l['example'][0]
    if l['role'] == 'consonant' and not l['never_initial']:
        for t in 'aiu': exp[f'syllables/{l["id"]}_{t}'] = None
for u in UNITS:
    for i, w in enumerate(u['words']): exp[f'units/u{pad(u["n"])}_{pad(i)}'] = w[0]
    for i, s in enumerate(u['sentences']): exp[f'sentences/u{pad(u["n"])}_{pad(i)}'] = s[0]
for i, w in enumerate(LET['sight_words']): exp[f'sight/{pad(i)}'] = w
for u in UNITS:
    if u.get('passage'): exp[f'passages/u{pad(u["n"])}'] = u['passage'][0]   # added 2026-10-03: every unit passage has a clip
JS_ASP = ['aspirates/' + ''.join(ch if re.match('[A-Za-z0-9]', ch) else '_' for ch in a[1]) for a in LET['aspirates']]   # exactly what learner.js aspirates() requests
for a in LET['aspirates']: exp['aspirates/' + a[1]] = None
for d in LET['diacritics']: exp[f'diacritics/{d["id"]}'] = None; exp[f'diacritics/{d["id"]}_ex'] = None
for i, n in enumerate(LET['numerals']): exp[f'numerals/{i}'] = None
UI = ['listen','tap_heard','tap_word','look','trace','blend','build','read','write','check','correct','wrong','next','done','unit_done','welcome']
for k in UI: exp['ui/' + k] = None

missing_idx = [k for k in exp if k not in IDX]
missing_file = [k for k, v in IDX.items() if not os.path.isfile(f'{PUB}/{v}')]
extra_idx = [k for k in IDX if k not in exp]
files_disk = sorted(os.path.relpath(os.path.join(r, f), PUB) for r, _, fs in os.walk(f'{PUB}/audio') for f in fs)
orph_files = sorted(set(files_disk) - set(IDX.values()))
asp_req_missing = [k for k in JS_ASP if k not in IDX]
R['aspirates_keys_requested_by_learner_js_missing_from_index'] = asp_req_missing
R['aspirates_html_id_collisions'] = [k for k, n in collections.Counter(re.sub('[^a-z]', '_', a[1]) for a in LET['aspirates']).items() if n > 1]
if asp_req_missing: find('major', 'A1', f'learner.js aspirates() builds audio keys by replacing every non [a-z0-9] char with "_": {len(asp_req_missing)} of 11 rows (ṭh, ḍh, ṛh) request "aspirates/_h", which is not in the index -> "No audio for this item"; their table-cell ids also collide (#asp-_h), so all three buttons land in the first row')
R['audio_index_entries'] = len(IDX); R['audio_files_on_disk'] = len(files_disk)
R['expected_keys'] = len(exp); R['missing_in_index'] = missing_idx; R['index_points_to_missing_file'] = missing_file
R['index_keys_not_expected'] = extra_idx; R['orphan_files_on_disk'] = orph_files
mani_pre = {f'{m["kind"]}/{m["id"]}': m for m in MANI}
# file validity + duration
bad_media, durs = [], {}
for k, v in IDX.items():
    p = f'{PUB}/{v}'
    if not os.path.isfile(p): continue
    sz = os.path.getsize(p)
    try:
        d = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True,timeout=20).stdout.strip() or 0)
    except Exception: d = 0
    durs[k] = d
    if sz < 1500 or d < 0.15: bad_media.append((k, sz, d))
R['unplayable_or_tiny_clips'] = bad_media
VOW = {'a': 'ا', 'i': 'ی', 'u': 'و'}
syl_bad = []
for l in LETTERS:
    if l['role'] == 'consonant' and not l['never_initial']:
        for t, v in VOW.items():
            m = mani_pre.get(f'syllables/{l["id"]}_{t}')
            if not m or m['text'].replace(' ', '') != l['ch'] + v: syl_bad.append((l['ch'], t, m and m['text']))
R['syllable_manifest_text_wrong'] = syl_bad
# manifest text vs expected text
mani = {f'{m["kind"]}/{m["id"]}': m for m in MANI}
mism = []
for k, t in exp.items():
    if t is None: continue
    m = mani.get(k)
    if not m: mism.append((k, t, 'NO MANIFEST ENTRY')); continue
    if m['text'].strip() != t.strip(): mism.append((k, t, m['text']))
R['manifest_text_mismatch'] = mism
# overrides: what ElevenLabs was actually asked to say
o_mism = [(k, exp[k], v['text']) for k, v in OVR.items() if exp.get(k) and v['text'] != exp[k]]
R['override_text_mismatch'] = o_mism
# duration outliers (per kind, > 3 sigma or ratio)
import statistics
by_kind = collections.defaultdict(list)
for k, d in durs.items(): by_kind[k.split('/')[0]].append((k, d))
outl = []
for kind, xs in by_kind.items():
    if len(xs) < 8: continue
    ds = [d for _, d in xs]; mu, sd = statistics.mean(ds), statistics.pstdev(ds) or 1
    outl += [(k, round(d, 2), round(mu, 2)) for k, d in xs if abs(d - mu) > 3 * sd]
R['duration_outliers_3sigma'] = outl
# keys referenced from code (static grep + dynamic-pattern expansion)
code = ''.join(open(f'{SRC}/{f}', encoding='utf8').read() for f in os.listdir(SRC) if f.endswith('.js'))
ref = set()
for m in re.finditer(r"""ui/(\w+)""", code): ref.add('ui/' + m.group(1))
for m in re.finditer(r"""ctx\.say\(\s*'(\w+)'""", code): ref.add('ui/' + m.group(1))
dyn = {
    'names/': 'names/\' + ' in code or 'names/${' in code, 'words/': "'words/' +" in code or 'words/${' in code,
    'units/': 'units/u${' in code or 'wordKey' in code, 'sentences/': 'sentences/u${' in code or 'sentKey' in code,
    'sight/': "'sight/' +" in code, 'aspirates/': "'aspirates/' +" in code, 'diacritics/': "'diacritics/' +" in code,
    'syllables/': 'syllables/${' in code, 'numerals/': ("'numerals/'" in code or 'numerals/${' in code),
}
R['dynamic_prefix_used_in_code'] = dyn
unref = [k for k in IDX if (k.startswith('ui/') and k not in ref) or not dyn.get(k.split('/')[0] + '/', True)]
R['clips_never_referenced_by_code'] = unref
# ui keys used in code but missing
R['ui_keys_used_but_missing'] = sorted(k for k in ref if k not in IDX)
# passage audio: does any passage have a clip?
R['passages_without_audio'] = [u['n'] for u in UNITS if u.get('passage') and f'passages/u{pad(u["n"])}' not in IDX]
for k in missing_idx: find('blocker', 'A1b', f'audio key missing from index: {k}')
for k in missing_file: find('blocker', 'A2', f'index entry has no file on disk: {k}')
if orph_files: find('minor', 'A3', f'{len(orph_files)} orphan audio files on disk not in index')
if mism: find('major', 'A4', f'{len(mism)} clips whose manifest text differs from the content they are played for: {mism[:3]}')
if unref: find('minor', 'A5', f'{len(unref)} indexed clips are never played by any code path: {unref[:12]}')
if R['passages_without_audio']: find('major', 'A6', f'unit passages (units {R["passages_without_audio"]}) and the assessment passage have no audio at all')

# ---------------------------------------------------------------- B. decodability
FOLD = {'آ': 'ا', 'أ': 'ا', 'ؤ': 'و', 'ء': 'ئ'}
def letters_of(s): return [FOLD.get(c, c) for c in s if unicodedata.category(c) != 'Mn' and c != TAT]
dec = {'bare_bad': [], 'voc_bad': [], 'preview': [], 'voc_mismatch': [], 'voc_stray_marks': [], 'no_marks_units_le10': 0, 'marks_total_words_le10': 0, 'mark_gap': []}
taught = set();
for u in UNITS:
    taught |= set(u['letters'])
    for i, w in enumerate(u['words'] + [('sent',) + tuple(s) for s in []]):
        ur, rom, en = w[0], w[1], w[2]; v = w[3] if len(w) > 3 else w[0]
        miss = set(letters_of(ur)) - taught
        if miss:
            (dec['preview'] if 'preview' in en else dec['bare_bad']).append((u['n'], ur, ''.join(miss)))
        missv = set(letters_of(v)) - taught
        if missv and not miss: dec['voc_bad'].append((u['n'], v, ''.join(missv)))
        if MARKS.sub('', v) != MARKS.sub('', ur):
            dec['voc_mismatch'].append((u['n'], ur, v))
        if u['n'] <= 10:
            dec['marks_total_words_le10'] += 1
            if v == ur: dec['no_marks_units_le10'] += 1
    for kind in ('sentences',):
        for s in u[kind]:
            ur = s[0]; v = s[3] if len(s) > 3 else s[0]
            for tok in ur.split():
                if set(letters_of(tok)) - taught - set('۔،؟: ') - (set('۰۱۲۳۴۵۶۷۸۹') if u['n'] >= 10 else set()): dec['bare_bad'].append((u['n'], 'sentence:' + ur, ''.join(set(letters_of(tok)) - taught)))
    if u.get('passage'):
        p = u['passage']
        miss = set(letters_of(p[0])) - taught - set('۔،؟: ۰۱۲۳۴۵۶۷۸۹')
        if miss: dec['bare_bad'].append((u['n'], 'PASSAGE', ''.join(miss)))
R['decodability'] = {k: v for k, v in dec.items()}
for x in dec['bare_bad']: find('major', 'B1', f'not decodable from letters taught by then (bare): {x}')
for x in dec['voc_bad']: find('major', 'B2', f'not decodable (vowelled form): {x}')
for x in dec['voc_mismatch']: find('major', 'B3', f'vowelled form changes the letters: {x}')
# passages: vowelled?
R['passage_has_marks'] = {u['n']: bool(MARKS.search(u['passage'][0])) for u in UNITS if u.get('passage')}
# words whose vowelled form is identical to bare although a consonant+consonant cluster needs a short vowel (units<=10)
VOWELS = set('اویےآ')
def needs_mark(ur):
    ls = [c for c in ur if unicodedata.category(c) != 'Mn']
    for a, b in zip(ls, ls[1:]):
        if a not in VOWELS and a in BY and b in BY and b not in VOWELS and BY[a]['role'] == 'consonant': return True
    return False
gap = []
for u in UNITS:
    if u['n'] > 10: continue
    for w in u['words']:
        v = w[3] if len(w) > 3 else w[0]
        if v == w[0] and needs_mark(w[0]): gap.append((u['n'], w[0], w[1]))
R['words_le_unit10_with_cluster_but_no_marks'] = gap
if gap: find('minor', 'B4', f'{len(gap)} words in units 1-10 show NO vowel marks although the design keeps marks on all text through unit 10: {gap[:6]}')

# ---------------------------------------------------------------- C. glosses
glo = {'blank': [], 'en_eq_rom': [], 'non_ascii_en': [], 'dup_rom_in_unit': [], 'dup_en_in_unit': [], 'long_en': [], 'rom_skeleton_mismatch': []}
RC = [('kh','خ'),('gh','غ'),('sh','ش'),('ch','چ'),('zh','ژ'),('th','ت'),('dh','د'),('ph','پ'),('bh','ب'),('jh','ج'),('kk','ک'),('ṭ','ٹ'),('ḍ','ڈ'),('ṛ','ڑ')]
URD_C = {}  # urdu letter -> consonant class (None = vowel-ish)
CONS = {'ب':'b','پ':'p','ت':'t','ٹ':'T','ث':'s','ج':'j','چ':'c','ح':'h','خ':'x','د':'d','ڈ':'D','ذ':'z','ر':'r','ڑ':'R','ز':'z','ژ':'Z','س':'s','ش':'S','ص':'s','ض':'z','ط':'t','ظ':'z','غ':'G','ف':'f','ق':'q','ک':'k','گ':'g','ل':'l','م':'m','ن':'n','ہ':'h'}
def urd_skel(ur):
    out = []; ls = [c for c in ur if unicodedata.category(c) != 'Mn' and c != TAT]
    for i, c in enumerate(ls):
        if c == 'ھ': continue  # aspirate marker: merges with previous
        if c in CONS:
            if c == 'ہ' and i == len(ls) - 1 and i > 0: continue   # final -a/-e
            out.append(CONS[c])
        elif c in 'وی' and (i == 0 or ls[i-1] in 'ا') : out.append('v' if c == 'و' else 'y')
    return out
def rom_skel(r):
    r = unicodedata.normalize('NFC', r.lower()); r = re.sub(r'[̣̱̄̇ʾʿ\-\' ]', '', unicodedata.normalize('NFD', r)); r = unicodedata.normalize('NFC', r)
    for a, b in [('kh','x'),('gh','G'),('sh','S'),('ch','c'),('zh','Z'),('ph','p'),('bh','b'),('th','t'),('dh','d'),('jh','j'),('kk','k'),('gg','g'),('ṭ','T'),('ḍ','D'),('ṛ','R')]: r = r.replace(a, b)
    return [c for c in r if c in 'bpt T s j c h x d D z r R Z S G f q k g l m n v y w'.replace(' ', '') or c in 'TDRSZGx']
for u in UNITS:
    seen_r, seen_e = collections.defaultdict(list), collections.defaultdict(list)
    for w in u['words']:
        ur, rom, en = w[0], w[1], w[2]
        if not rom.strip() or not en.strip(): glo['blank'].append((u['n'], ur))
        if en.strip().lower() == rom.strip().lower(): glo['en_eq_rom'].append((u['n'], ur, en))
        if re.search(r'[^\x00-\x7F]', en): glo['non_ascii_en'].append((u['n'], ur, en))
        if len(en) > 40: glo['long_en'].append((u['n'], ur, en))
        seen_r[rom].append(ur); seen_e[re.sub(r'\s*\(.*?\)', '', en).strip().lower()].append(ur)
        a = [x for x in urd_skel(ur) if x not in 'vy']; b = [x for x in rom_skel(rom) if x not in 'vyw']
        if len(a) != len(b) and abs(len(a) - len(b)) >= 1: glo['rom_skeleton_mismatch'].append((u['n'], ur, rom, ''.join(a), ''.join(b)))
    glo['dup_rom_in_unit'] += [(u['n'], r, v) for r, v in seen_r.items() if len(v) > 1]
    glo['dup_en_in_unit'] += [(u['n'], e, v) for e, v in seen_e.items() if len(v) > 1]
R['glosses'] = glo
for k in ('blank', 'en_eq_rom'):
    for x in glo[k]: find('major', 'C1', f'gloss {k}: {x}')
for x in glo['dup_rom_in_unit']: find('minor', 'C2', f'same romanisation for different words (quiz asks by roman!): {x}')

# ---------------------------------------------------------------- D. duplicates across units
pos = collections.defaultdict(list)
for u in UNITS:
    for i, w in enumerate(u['words']): pos[w[0]].append((u['n'], i, w[2]))
dups = {k: v for k, v in pos.items() if len(v) > 1}
R['duplicate_words_across_units'] = dups
lw = [w for u in UNITS for w in u['words']]
R['word_totals'] = {'words': len(lw), 'unique': len(set(w[0] for w in lw)), 'sentences': sum(len(u['sentences']) for u in UNITS), 'per_unit_words': {u['n']: len(u['words']) for u in UNITS}}
if dups: find('minor', 'D1', f'{len(dups)} words appear in more than one unit (they share card ids in Leitner): {list(dups)[:8]}')
# word also equals a sight word or letter char (card id collision profile:item)
coll = [w for w in dups] + [w[0] for w in lw if w[0] in BY]
sight = set(LET['sight_words']); R['words_equal_sight_words'] = sorted({w[0] for w in lw if w[0] in sight})

# ---------------------------------------------------------------- E. letter flags
NONJOIN = set('ادڈذرڑزژوے')
flag_err = []
for l in LETTERS:
    if l['ch'] in NONJOIN and l['joiner']: flag_err.append((l['ch'], 'listed joiner but is one of the 10 non-joiners'))
    if l['ch'] not in NONJOIN and not l['joiner']: flag_err.append((l['ch'], 'non-joiner flag; informational'))
R['joiner_flags_vs_ten'] = flag_err
# empirical joining via HarfBuzz (Noto Naskh): does the following ب take a connected form?
try:
    import uharfbuzz as hb
    def face(path):
        blob = hb.Blob.from_file_path(path); return hb.Face(blob), blob
    def shape(font, text, feats=None):
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(font, buf, feats or {})
        return [(font.glyph_to_string(i.codepoint), i.codepoint) for i in buf.glyph_infos]
    faces = {}
    for nm, fn in (('naskh', 'NotoNaskhArabic.ttf'), ('nastaliq', 'NotoNastaliqUrdu-Regular.ttf')):
        fc, bl = face(f'{PUB}/fonts/{fn}'); faces[nm] = (hb.Font(fc), fc, bl)
    join_emp = {}
    for l in LETTERS + [{'ch': 'ۃ', 'id': 'teh_goal'}, {'ch': 'ء', 'id': 'hamza_bare'}, {'ch': 'ؤ', 'id': 'waw_hamza'}, {'ch': 'آ', 'id': 'alif_madda'}, {'ch': 'ۓ', 'id': 'ye_hamza'}]:
        g = shape(faces['naskh'][0], l['ch'] + 'ب')     # HarfBuzz returns visual order: g[-1] is the first logical letter. It is in its INITIAL form iff it joins forward
        iso = shape(faces['naskh'][0], l['ch'])
        joined = any(n.endswith('.fina') for n, _ in g)   # the following beh took its FINAL form => this letter joins forward
        join_emp[l['ch']] = joined
    R['harfbuzz_joins_forward'] = join_emp
    bad = [(c, 'json says joiner' if BY[c]['joiner'] else 'json says non-joiner', 'harfbuzz says ' + ('joins' if join_emp[c] else 'does not join')) for c in BY if BY[c]['joiner'] != join_emp[c] and c not in 'ںھ']
    R['joiner_flag_vs_harfbuzz_disagree'] = bad
    for x in bad: find('major', 'E1', f'joiner flag disagrees with the shaping engine: {x}')
    # ں: dual-joining in Unicode? record shaping facts
    R['nun_ghunna_note'] = {'ں_joins_forward_in_font': join_emp.get('ں'), 'json_joiner': BY['ں']['joiner']}
    # glyph coverage for every letter and every form string the app builds
    cov = {}
    tofu = []
    for nm, (font, fc, bl) in faces.items():
        for l in LETTERS:
            forms = {'isolated': l['ch'], 'initial': l['ch'] + TAT if l['joiner'] else None, 'medial': TAT + l['ch'] + TAT if l['joiner'] else None, 'final': TAT + l['ch']}
            for pos_, s in forms.items():
                if not s: continue
                gl = shape(font, s)
                if any(c == 0 for _, c in gl): tofu.append((nm, l['ch'], pos_, 'notdef'))
        # every character used anywhere in units/passages
        allchars = set(''.join(w[0] + (w[3] if len(w) > 3 else '') for u in UNITS for w in u['words'] + u['sentences']) + ''.join(u['passage'][0] for u in UNITS if u.get('passage')) + LET['assessment']['passage'] + ''.join(LET['assessment']['nonwords']))
        for c in sorted(allchars):
            if c == ' ': continue
            gl = shape(font, c)
            if any(g == 0 for _, g in gl): tofu.append((nm, c, hex(ord(c)), 'notdef in content'))
    R['tofu_or_notdef'] = tofu
    for x in tofu: find('major', 'F1', f'missing glyph / tofu: {x}')
    # form distinctness (initial/medial/final glyph different from isolated) per font
    same = []
    for nm, (font, fc, bl) in faces.items():
        for l in LETTERS:
            iso = [g for g, _ in shape(font, l['ch'])]
            fin = [g for g, _ in shape(font, 'ب' + l['ch'])]  # joined to the right neighbour -> final form of l
            if l['joiner']:
                ini = [g for g, _ in shape(font, l['ch'] + 'ب')]
                if ini[-1] == iso[0] if nm == 'naskh' else False: same.append((nm, l['ch'], 'initial shaped same as isolated'))
            if fin[-1] == iso[0] and nm == 'naskh' and l['ch'] != 'ا': pass
    R['form_distinct_problems'] = same
except Exception as e:
    R['harfbuzz_error'] = repr(e)

# never_initial vs the words we ship
first = collections.Counter(w[0][0] for u in UNITS for w in u['words'])
ni_viol = [(c, first[c]) for c, l in BY.items() if l['never_initial'] and first[c]]
ni_unproven = [c for c, l in BY.items() if (not l['never_initial']) and not first[c]]
R['never_initial_but_word_starts_with_it'] = ni_viol
R['not_never_initial_but_no_shipped_word_starts_with_it'] = ni_unproven
for x in ni_viol: find('major', 'E2', f'never_initial letter starts a word: {x}')
# letters taught in units.json but absent from letters.json
R['unit_letters_missing_from_letters_json'] = [c for u in UNITS for c in u['letters'] if c not in BY]
R['letters_json_not_in_any_unit'] = [c for c in BY if not any(c in u['letters'] for u in UNITS)]
for c in R['unit_letters_missing_from_letters_json']: find('minor', 'E3', f'unit lists {c} as a taught letter but letters.json has no record: it gets no lesson, card, audio or trace practice')
# per-letter positional example coverage (replicates path.js posWord: words from units <= letter unit)
def posword(l, position):
    for u in UNITS:
        if u['n'] > l['unit']: break
        for w in u['words']:
            s = w[0]; n = len(s)
            if l['ch'] not in s: continue
            f, la = s.index(l['ch']), s.rindex(l['ch'])
            if position == 'initial' and f == 0 and n > 1: return w
            if position == 'final' and la == n - 1 and n > 1: return w
            if position == 'medial' and any(c == l['ch'] and 0 < i < n - 1 for i, c in enumerate(s)): return w
            if position == 'isolated': return w
    return None
nopos = []
for l in LETTERS:
    for p_ in (['isolated', 'initial', 'medial', 'final'] if l['joiner'] else ['isolated', 'final']):
        if p_ in ('initial',) and l['never_initial']: continue
        if not posword(l, p_): nopos.append((l['ch'], p_))
R['letter_positions_without_example_word_in_lesson'] = nopos
if nopos: find('minor', 'E4', f'{len(nopos)} (letter, position) pairs show "—" instead of a real example word in the "where it sits" screen: {nopos[:10]}')

# ---------------------------------------------------------------- G. drill-pool eligibility (mirrors drills.js spellable/joinIt/dictation)
def known(n, unit_letters):
    k = set(c for u in UNITS if u['n'] < n for c in u['letters'] if c in BY) | set(c for c in unit_letters if c in BY) | {TAT}
    if n >= 10: k |= set('ءئؤآۃ')
    return k
def spellable(n, ul, ur): k = known(n, ul); return all(c in k or MARKS.match(c) for c in ur)
elig = []
for u in UNITS:
    nw = len(u['words'])
    if not nw: continue
    halves = [(0, -(-nw // 2)), (-(-nw // 2), nw)]
    for hi, (a, b) in enumerate(halves):
        ws = u['words'][a:b]
        sp = [w for w in ws if spellable(u['n'], u['letters'], w[0])]
        bare3 = [w for w in sp if len(MARKS.sub('', w[0]).replace(TAT, '')) >= 3]
        elig.append({'unit': u['n'], 'half': hi + 1, 'words': len(ws), 'spellable': len(sp), 'joinIt_pool(>=3 letters)': len(bare3[:6]), 'dictation_ok': (len(ws) >= 5 and len(sp) >= 3)})
R['lesson_drill_eligibility'] = elig
for e in elig:
    if e['joinIt_pool(>=3 letters)'] == 0: find('major', 'G1', f'unit {e["unit"]} Words {e["half"]}: build-the-word has no eligible word, screen is silently skipped')
    if not e['dictation_ok']: find('major', 'G2', f'unit {e["unit"]} Words {e["half"]}: dictation not available ({e["spellable"]} spellable words)')
    if e['joinIt_pool(>=3 letters)'] < 3 and e['joinIt_pool(>=3 letters)'] > 0: find('minor', 'G3', f'unit {e["unit"]} Words {e["half"]}: build-the-word pool is only {e["joinIt_pool(>=3 letters)"]}; joinIt onDone needs 3 completions and cycles the same word(s)')

# quiz eligibility (unit check)
for u in UNITS:
    sp = [w for w in u['words'] if spellable(u['n'], u['letters'], w[0])]
    if u['words'] and len(sp) < 10: find('major', 'G4', f'unit {u["n"]} check: only {len(sp)} spellable words, but the check asks 10 distinct questions -> fewer questions (pass threshold stays 8)')
R['quiz_pool'] = {u['n']: len([w for w in u['words'] if spellable(u['n'], u['letters'], w[0])]) for u in UNITS if u['words']}

# assessment passage vs unit-11 practice passage overlap
def sents(t): return [s.strip() for s in re.split('[۔]', t) if s.strip()]
a = set(sents(LET['assessment']['passage']))
for u in UNITS:
    if u.get('passage'):
        ov = a & set(sents(u['passage'][0]))
        if ov: R.setdefault('assessment_passage_overlap', {})[u['n']] = (len(ov), len(a))
if R.get('assessment_passage_overlap'): find('major', 'H1', f'EGRA-style assessment passage ({len(a)} sentences) is mostly already in the practice passages: {R["assessment_passage_overlap"]} -> memorised, not decoded')
nw_unit = [w for u in UNITS for w in u['words']]
R['assessment_words_in_pool_not_yet_taught_at_unit12'] = 0

json.dump(R, open(f'{HERE}/check_content.json', 'w'), ensure_ascii=False, indent=1, default=str)
# ------------------------------------------------------------------ report
print('== AUDIO ==')
print(f'index entries {len(IDX)} | expected keys {len(exp)} | files on disk {len(files_disk)}')
print('missing in index:', len(missing_idx), '| index->missing file:', len(missing_file), '| orphan files:', len(orph_files), '| unexpected index keys:', len(extra_idx))
print('tiny/unplayable:', bad_media[:5], '| manifest text mismatch:', len(mism), '| override mismatch:', len(o_mism))
print('duration outliers:', outl[:8])
print('never referenced by code:', len(unref), unref[:12])
print('== DECODABILITY ==', {k: (v if isinstance(v, int) else len(v)) for k, v in dec.items()})
print('preview words:', dec['preview'])
print('passage has marks:', R['passage_has_marks'])
print('words with no marks though cluster (u<=10):', len(gap), 'of', dec['marks_total_words_le10'])
print('== GLOSSES ==', {k: len(v) for k, v in glo.items()})
for k in ('blank','en_eq_rom','non_ascii_en','dup_rom_in_unit','dup_en_in_unit','long_en'): print(' ', k, glo[k][:8])
print('  roman skeleton mismatches (review):', len(glo['rom_skeleton_mismatch'])); [print('   ', x) for x in glo['rom_skeleton_mismatch'][:40]]
print('== DUPLICATES ==', {k: v for k, v in list(dups.items())[:10]}, '| words equal sight words:', R['words_equal_sight_words'])
print('totals', R['word_totals'])
print('== FLAGS ==', R['joiner_flags_vs_ten'], '| harfbuzz disagree:', R.get('joiner_flag_vs_harfbuzz_disagree'), '| nun ghunna:', R.get('nun_ghunna_note'))
print('tofu:', R.get('tofu_or_notdef'), '| form problems:', R.get('form_distinct_problems'), '| hb err:', R.get('harfbuzz_error'))
print('never_initial violated:', ni_viol, '| not-NI with no word starting:', ni_unproven)
print('unit letters missing from letters.json:', R['unit_letters_missing_from_letters_json'])
print('positions with no example word:', nopos)
print('== ELIGIBILITY =='); [print('  ', e) for e in elig]
print('quiz pool', R['quiz_pool'])
print('== FINDINGS =='); [print(f'[{s}] {i}: {t}') for s, i, t in F]
