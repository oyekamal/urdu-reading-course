#!/usr/bin/env python3
"""Independent Whisper round-trip over the SHIPPED mp3 clips (mobile/public/audio): does each clip say the text the UI shows for it?
Homophone letters are folded (س ث ص, ز ذ ض ظ, ت ط, ہ ح, ا ع) so spelling-only differences do not count as errors."""
import json, os, re, sys, difflib, unicodedata, whisper, torch
ROOT = os.path.expanduser('~/Documents/free_work/urdu-reading-course'); PUB = ROOT + '/mobile/public'
HERE = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(PUB + '/data/audio_index.json')); MANI = {f'{m["kind"]}/{m["id"]}': m for m in json.load(open(ROOT + '/assets/audio/manifest.json'))}
FOLD = str.maketrans({'ث':'س','ص':'س','ذ':'ز','ض':'ز','ظ':'ز','ط':'ت','ح':'ہ','ۃ':'ہ','ع':'ا','آ':'ا','ء':'','ئ':'ی','ؤ':'و','ے':'ی','ں':'ن','ھ':'','ڑ':'ر','ٹ':'ت','ڈ':'د','ق':'ک','غ':'گ','خ':'ک','ہ':'ہ','ي':'ی','ك':'ک','ۓ':'ی'})
def norm(s):
    s = unicodedata.normalize('NFC', s); s = re.sub('[ً-ْٰـ۔،؟?.,!؛:\\-\\s]', '', s); return s.translate(FOLD)
kinds = sys.argv[1].split(',') if len(sys.argv) > 1 else ['units', 'sentences', 'sight', 'words', 'names', 'syllables']
model = whisper.load_model('small', device='cpu')
out = {}; path = HERE + '/whisper_verify.json'
if os.path.exists(path): out = json.load(open(path))
keys = [k for k in IDX if k.split('/')[0] in kinds and k in MANI]
for n, k in enumerate(keys):
    if k in out: continue
    r = model.transcribe(f'{PUB}/{IDX[k]}', language='ur', fp16=False, temperature=0, condition_on_previous_text=False)
    exp, heard = MANI[k]['text'], r['text']
    out[k] = {'expected': exp, 'heard': heard, 'ratio': round(difflib.SequenceMatcher(None, norm(exp), norm(heard)).ratio(), 2)}
    if n % 10 == 0: json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1); print(n, len(keys), k, out[k], flush=True)
json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1); print('DONE', len(out))
