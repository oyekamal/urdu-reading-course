#!/usr/bin/env python3
"""Render letter cards (PNG) from data/letters.json using PIL + libraqm shaping.

Outputs (assets/images/):
  letters/<id>_<style>.png        big isolated letter, name, IPA, hint, example word
  forms/<id>_<style>.png          the four positional forms: isolated / initial / medial / final
  contrast/<group>_<style>.png    dot-confusable clusters side by side
  words/<unit>_<idx>_<style>.png  unit word cards, vowel marks shown
style = naskh (Noto Naskh Arabic, units 0-10) | nastaliq (Noto Nastaliq Urdu, unit 11+)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
UNITS = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
OUT = f"{ROOT}/assets/images"
FONTS = {
    "naskh": f"{ROOT}/assets/fonts/NotoNaskhArabic.ttf",
    "nastaliq": f"{ROOT}/assets/fonts/NotoNastaliqUrdu-Regular.ttf",
}
LATIN = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LATIN_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INK, MUTED, ACCENT, BG = (20, 24, 40), (110, 115, 130), (200, 60, 40), (252, 250, 245)
ZWJ, TATWEEL = "‍", "ـ"


def font(style, size):
    return ImageFont.truetype(FONTS[style], size)


def urdu(d, xy, text, f, fill=INK, anchor="ra"):
    d.text(xy, text, font=f, fill=fill, direction="rtl", language="ur", anchor=anchor, features=["kern", "calt"])


def latin(d, xy, text, size=28, fill=INK, bold=False):
    d.text(xy, text, font=ImageFont.truetype(LATIN_B if bold else LATIN, size), fill=fill)


def forms(letter):
    """Isolated / initial / medial / final strings. Tatweel forces the joined shapes."""
    ch, j = letter["ch"], letter["joiner"]
    return [("isolated", ch),
            ("initial", ch + TATWEEL if j else None),
            ("medial", TATWEEL + ch + TATWEEL if j else None),
            ("final", TATWEEL + ch)]


def letter_card(L, style):
    im = Image.new("RGB", (1200, 800), BG)
    d = ImageDraw.Draw(im)
    urdu(d, (1140, 60), L["ch"], font(style, 300 if style == "naskh" else 240), anchor="ra")
    urdu(d, (1140, 520 if style == "naskh" else 560), L["name_ur"], font(style, 72), fill=MUTED)
    latin(d, (60, 80), L["name"], 64, bold=True)
    latin(d, (60, 170), f"/{L['ipa']}/", 40, MUTED)
    # wrap hint
    words, lines, cur = L["hint"].split(), [], ""
    for w in words:
        if len(cur) + len(w) > 34:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    for i, ln in enumerate(lines[:4]):
        latin(d, (60, 250 + i * 40), ln, 30)
    ex = L["example"]
    urdu(d, (1140, 690), ex[0], font(style, 64), fill=ACCENT, anchor="ra")
    latin(d, (60, 690), f"{ex[1]}  —  {ex[2]}", 34, ACCENT)
    tag = ("joins forward" if L["joiner"] else "does NOT join forward") + ("  ·  never starts a word" if L["never_initial"] else "")
    latin(d, (60, 740), tag, 24, MUTED)
    im.save(f"{OUT}/letters/{L['id']}_{style}.png")


def forms_card(L, style):
    im = Image.new("RGB", (1400, 520), BG)
    d = ImageDraw.Draw(im)
    latin(d, (40, 30), f"{L['name']}  {L['ch']}  — where it sits in a word", 34, bold=True)
    cols = forms(L)
    w = 1400 // 4
    # RTL reading order: isolated on the right
    for i, (label, s) in enumerate(cols):
        x0 = 1400 - (i + 1) * w
        cx = x0 + w // 2
        d.line([(x0, 100), (x0, 480)], fill=(225, 222, 215), width=2)
        latin(d, (x0 + 20, 100), label, 26, MUTED)
        if s is None:
            latin(d, (x0 + 20, 260), "— (no such form)", 24, MUTED)
        else:
            urdu(d, (cx, 150), s, font(style, 170 if style == "naskh" else 130), anchor="ma")
    im.save(f"{OUT}/forms/{L['id']}_{style}.png")


def contrast_card(name, chars, style):
    im = Image.new("RGB", (200 * len(chars) + 100, 420), BG)
    d = ImageDraw.Draw(im)
    latin(d, (40, 20), "Same body — count the dots", 30, bold=True)
    for i, ch in enumerate(chars):
        cx = im.width - 50 - (i * 200) - 100
        urdu(d, (cx, 80), ch, font(style, 180), anchor="ma")
        L = next(l for l in DATA["letters"] if l["ch"] == ch)
        latin(d, (cx - 60, 340), L["name"], 26, MUTED)
    im.save(f"{OUT}/contrast/{name}_{style}.png")


def word_card(u, idx, word, style):
    ur, rom, en = word
    im = Image.new("RGB", (900, 360), BG)
    d = ImageDraw.Draw(im)
    urdu(d, (450, 40), ur, font(style, 150 if style == "naskh" else 110), anchor="ma")
    latin(d, (40, 290), f"{rom}   —   {en}", 32, MUTED)
    im.save(f"{OUT}/words/u{u:02d}_{idx:02d}_{style}.png")


def main():
    styles = sys.argv[1:] or ["naskh", "nastaliq"]
    for sub in ["letters", "forms", "contrast", "words"]:
        os.makedirs(f"{OUT}/{sub}", exist_ok=True)
    n = 0
    for style in styles:
        for L in DATA["letters"]:
            letter_card(L, style); forms_card(L, style); n += 2
        for name, chars in {"be_family": "ب پ ت ٹ ث".split(), "nun_ye_be": "ب ن ی".split(), "jim_family": "ج چ ح خ".split(),
                            "dal_family": "د ڈ ذ".split(), "re_family": "ر ڑ ز ژ".split(), "kaf_gaf": "ک گ".split(),
                            "he_vs_he": "ہ ھ".split(), "sin_shin_swad": "س ش ص".split(), "toe_zoe": "ط ظ".split(), "ain_ghain": "ع غ".split()}.items():
            contrast_card(name, chars, style); n += 1
        for u in UNITS:
            for i, w in enumerate(u["words"]):
                word_card(u["n"], i, w, style); n += 1
    print(f"rendered {n} cards into {OUT}")


if __name__ == "__main__":
    main()
