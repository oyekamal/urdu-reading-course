"""Build blind A/B images for the verifier. Usage: python3 blind.py <round>
Writes blind_rN/ (neutral names, branding whited out) and blind_key_rN.json (the key, kept OUT of that folder)."""
import sys, os, random, json, subprocess
from PIL import Image, ImageDraw
R = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f'{HERE}/blind_r{R}'; os.makedirs(OUT, exist_ok=True)
PDF = '/home/oye/Documents/free_work/urdu-reading-course/mobile/public/pdf'; BAR = f'{HERE}/bar'; TMP = f'{HERE}/_tmp_r{R}'; os.makedirs(TMP, exist_ok=True)
def ras(pdf, page, name, dpi=90):
    out = f'{TMP}/{name}'; subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-f', str(page), '-l', str(page), '-singlefile', pdf, out], check=True); return Image.open(out + '.png').convert('RGB')
def clean(im, kind):
    d = ImageDraw.Draw(im); w, h = im.size
    if kind == 'k5': d.rectangle([0, 0, int(w * .35), int(h * .075)], fill='white'); d.rectangle([0, int(h * .955), w, h], fill='white')
    if kind == 'ours': d.rectangle([0, int(h * .955), w, h], fill='white')
    return im
def montage(ims):
    h = max(i.height for i in ims); w = sum(i.width for i in ims) + 10 * (len(ims) - 1); s = Image.new('RGB', (w, h), 'white'); x = 0
    for i in ims: s.paste(i, (x, 0)); x += i.width + 10
    return s
def fims():
    im = Image.open(f'{BAR}/fims_urdu.png').convert('RGB'); im = im.resize((794, int(im.height * 794 / im.width))); d = ImageDraw.Draw(im); d.rectangle([0, int(im.height * .94), im.width, im.height], fill='white'); d.rectangle([int(im.width * .3), 0, im.width, int(im.height * .1)], fill='white'); return im
def find(pdf, phrase, nth=1):
    n = int(subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout.split('Pages:')[1].split()[0]); hit = 0
    for p in range(1, n + 1):
        t = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), pdf, '-'], capture_output=True, text=True).stdout
        if phrase.lower() in t.lower().replace('\n', ' '):
            hit += 1
            if hit == nth: return p
    return 1
def O(f, p, n):
    if isinstance(p, str): p = find(f'{PDF}/{f}.pdf', p)
    return clean(ras(f'{PDF}/{f}.pdf', p, n), 'ours')
K = lambda f, p, n: clean(ras(f'{BAR}/{f}.pdf', p, n), 'k5')
def bel(p): return ras(f'{BAR}/belaraby_ar.pdf', p, f'bel{p}', 80)
types = {
 '1_trace': ([O('u01_trace', 2, 'o1'), O('u05_trace', 1, 'o2')], [K('k5_k', 1, 'b1'), bel(3), fims()]),
 '2_wordbuilding': ([O('u01_join', 1, 'o3'), O('u01_check', 1, 'o4')], [K('k5_cvc', 1, 'b2'), K('k5_cvc2', 1, 'b3')]),
 '3_read_and_match': ([O('u01_match', 1, 'o5'), O('u01_reading', 'Read the words', 'o6')], [K('k5_cvc', 1, 'b4'), K('k5_cvc2', 1, 'b5')]),
 '4_sentences': ([O('u01_reading', 'Read the sentences', 'o7'), O('u01_dictation', 1, 'o8')], [K('k5_sentences', 1, 'b6')]),
 '5_flashcards': ([O('course_flashcards_letters', 1, 'o9'), O('course_flashcards_sight_words', 1, 'o10')], [K('k5_flash', 1, 'b7'), K('k5_flash', 2, 'b8')]),
}
rng = random.Random(int(R) * 7 + 3); key = {}
for t, (ours, bar) in types.items():
    sides = [('ours', ours), ('bar', bar)]; rng.shuffle(sides)
    for lab, (who, ims) in zip('AB', sides):
        montage(ims).save(f'{OUT}/{t}_{lab}.png'); key[f'{t}_{lab}'] = who
abs_pages = {'6_lookalike': ('u01_lookalike', 1), '7_chart': ('course_alphabet_chart', 1), '8_vowel_card': ('course_vowel_marks', 1), '9_certificate': ('course_certificate', 1), '10_guide': ('u01_guide', 1), '11_answer_key': ('u01_pack', 'Answer key: unit'), '12_dictation_sentences': ('u01_dictation', 'Listen and write: sentences'), '13_trace_joiner_late': ('u08_trace', 3), '14_nastaliq_check': ('u11_check', 1), '15_trace_tall_letters': ('u04_trace', 3)}
for t, (f, p) in abs_pages.items(): O(f, p, 'x' + t).save(f'{OUT}/{t}.png')
json.dump(key, open(f'{HERE}/blind_key_r{R}.json', 'w'))
print(sorted(os.listdir(OUT)))
