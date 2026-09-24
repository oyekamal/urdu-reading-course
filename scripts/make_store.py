#!/usr/bin/env python3
"""Store assets: feature graphic 1024x500 and captioned phone screenshots 1080x1920 (EN + UR sets).

  python3 scripts/make_store.py                 # expects raw shots in store/raw/NN_*.png (from mobile/tools/store_shots.py)

Captions are the storyboard in research/17_aso.md §5, adapted to screens that exist. Feature background is Gemini art
(design/gen/out/feature_bg.jpg); the title lockup is added here so the text stays crisp and editable."""
import glob, os
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TURQ, SAFF, INK, PAPER, CREAM = "#1E9C8F", "#F2A93B", "#1E2F55", "#F2F7F6", "#F7EBD5"
NASKH = f"{R}/assets/fonts/NotoNaskhArabic.ttf"; NASTALIQ = f"{R}/assets/fonts/NotoNastaliqUrdu-Regular.ttf"
LATIN = "/usr/share/fonts/truetype/quicksand/Quicksand-Bold.ttf"  # rounded, close to Fredoka; woff2 can't be read by PIL
FREDOKA = f"{R}/store/fonts/Fredoka-Bold.ttf"; FREDOKA_M = f"{R}/store/fonts/Fredoka-Medium.ttf"  # instanced from assets/fonts/Fredoka.woff2
# (raw prefix, bg colour, mascot pose, tilt deg, EN headline, EN sub, UR headline, UR sub). Order = conversion order, not app order:
# benefit first (research/17 §3: install decisions ride on the first 2-3 shots). Style bar: Khan Academy Kids' Play screenshots.
SHOTS = [  # (raw prefix, bg, mascot, tilt, EN headline, EN sub, UR headline, UR sub, crop box in the 1079-wide raw)
    ("01", "#1E9C8F", "hello", 0, "Learn to read Urdu", "Alif, Bay, Pay: one letter at a time", "اردو پڑھنا سیکھیں", "الف، بے، پے: ایک ایک حرف", None),
    ("09", "#E8664F", "listen", -3, "Hear it, tap it", "A clear Urdu voice for every letter", "سنیں اور چھوئیں", "ہر حرف کی صاف اردو آواز", (20, 280, 1059, 1010)),
    ("10", "#3B4BA8", "read", 3, "Build real words", "Letters join into بابا and نام", "الفاظ خود بنائیں", "حروف مل کر بابا اور نام بنتے ہیں", (20, 230, 1059, 1080)),
    ("13", "#F2A93B", "point", -3, "Trace every letter", "With a finger, dots last", "انگلی سے حرف لکھیں", "نقطے سب سے آخر میں", (20, 330, 1059, 1570)),
    ("12", "#4FA35E", "cheer", 3, "Cheers for every win", "A pearl for every lesson finished", "ہر کامیابی پر شاباش", "ہر سبق مکمل کرنے پر ایک موتی", (20, 230, 1059, 1250)),
    ("11", "#8E5BB5", "think", -3, "One small step a day", "A new letter in every lesson", "روز ایک چھوٹا قدم", "ہر سبق میں ایک نیا حرف", (0, 0, 1079, 1690)),
    ("05", "#3E8ED0", "read", 3, "Naskh and Nastaliq", "Ready for real books and newspapers", "نسخ اور نستعلیق", "کتابیں اور اخبار بھی پڑھیں", (0, 0, 1079, 1450)),
    ("07", "#C9577A", "hello", -3, "For parents and teachers", "Progress reports and reading checks", "والدین اور اساتذہ کے لیے", "پیشرفت کی رپورٹ اور پڑھائی کا جائزہ", (0, 0, 1079, 1500)),
]
BG_LETTERS = "ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنوہھءیے"
TILE_COLOURS = ["#F2A93B", "#E8664F", "#3B4BA8", "#4FA35E", "#8E5BB5", "#1E9C8F", "#3E8ED0", "#C9577A"]
TILES = {"09": "مک", "10": "با", "13": "اب", "12": "لن", "11": "من", "05": "کت", "07": "رس"}  # letters that float by each phone


def fit(text, font_path, max_w, start, rtl=False):
    for size in range(start, 20, -2):
        f = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        if f.getlength(text, direction="rtl" if rtl else "ltr") <= max_w: return f
    return f


def draw_mixed(d, xy, text, latin_path, size, fill):
    """Centre a line that mixes Latin and Urdu words (e.g. 'Read بابا and نام'): each run in its own font."""
    import re
    runs = [r for r in re.split(r"([\u0600-\u06FF]+)", text) if r]
    fonts = [ImageFont.truetype(NASKH if re.match(r"[\u0600-\u06FF]", r) else latin_path, size if not re.match(r"[\u0600-\u06FF]", r) else int(size * 1.05), layout_engine=ImageFont.Layout.RAQM) for r in runs]
    widths = [f.getlength(r, direction="rtl" if re.match(r"[\u0600-\u06FF]", r) else "ltr") for r, f in zip(runs, fonts)]
    x = xy[0] - sum(widths) / 2
    for r, f, w in zip(runs, fonts, widths):
        d.text((x, xy[1]), r, font=f, fill=fill, anchor="lm", direction="rtl" if re.match(r"[\u0600-\u06FF]", r) else "ltr"); x += w


def phone(raw, width):
    shot = Image.open(raw).convert("RGB"); shot = shot.resize((width, int(shot.height * width / shot.width)), Image.LANCZOS)
    b = 22; fr = Image.new("RGBA", (width + 2 * b, shot.height + 2 * b), (0, 0, 0, 0)); d = ImageDraw.Draw(fr)
    d.rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=90, fill="#152040")
    m = Image.new("L", shot.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, width - 1, shot.height - 1), radius=70, fill=255)
    fr.paste(shot, (b, b), m); return fr


def tile(ch, colour, size, rot):
    """A chunky letter tile like the app's pearl buttons: colour block, white letter, soft drop shadow."""
    from PIL import ImageFilter
    t = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.rounded_rectangle((20, 26, size + 20, size + 26), radius=size // 4, fill=(0, 0, 0, 70)); t = t.filter(ImageFilter.GaussianBlur(8)); d = ImageDraw.Draw(t)
    d.rounded_rectangle((20, 20, size + 20, size + 20), radius=size // 4, fill=colour, outline="white", width=max(4, size // 22))
    f = ImageFont.truetype(NASKH, int(size * 0.62), layout_engine=ImageFont.Layout.RAQM)
    d.text((20 + size // 2, 20 + int(size * 0.44)), ch, font=f, fill="white", anchor="mm", direction="rtl")
    return t.rotate(rot, expand=True, resample=Image.BICUBIC)


def background(bg, n):
    import random
    W, H = 1080, 1920; im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im, "RGBA"); rnd = random.Random(n)
    for _ in range(22):  # faint qaida letters: the "traditional qaida imagery" the critic asked for
        f = ImageFont.truetype(NASKH, rnd.randint(110, 240), layout_engine=ImageFont.Layout.RAQM)
        d.text((rnd.randint(-40, W), rnd.randint(380, H)), rnd.choice(BG_LETTERS), font=f, fill=(255, 255, 255, 30), anchor="mm", direction="rtl")
    return im, d


def captions(d, hl, sub, lang, W=1080):
    if lang == "ur":
        f1 = fit(hl, NASTALIQ, 980, 100, True); d.text((W // 2, 150), hl, font=f1, fill="white", anchor="mm", direction="rtl")
        f2 = fit(sub, NASKH, 960, 54, True); d.text((W // 2, 300), sub, font=f2, fill=(255, 255, 255, 240), anchor="mm", direction="rtl")
    else:
        f1 = fit(hl, FREDOKA, 1000, 112); d.text((W // 2, 140), hl, font=f1, fill="white", anchor="mm")
        draw_mixed(d, (W // 2, 252), sub, FREDOKA_M, 52, (255, 255, 255, 240))


def mascot(pose, h):
    m = Image.open(f"{R}/design/gen/out/mascot_{pose}.png").convert("RGBA"); return m.resize((int(m.width * h / m.height), h), Image.LANCZOS)


def hero(bg, hl, sub, lang):
    """Shot 1 has no phone: Marko, a giant alif card and the first letters, so the thumbnail reads 'kids + Urdu letters' instantly."""
    W, H = 1080, 1920; im, d = background(bg, 0); captions(d, hl, sub, lang)
    card = Image.new("RGBA", (560, 640), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, 559, 639), radius=70, fill="white")
    cd.text((280, 300), "ا", font=ImageFont.truetype(NASKH, 420, layout_engine=ImageFont.Layout.RAQM), fill="#1E2F55", anchor="mm", direction="rtl")
    cd.text((280, 560), "الف", font=ImageFont.truetype(NASKH, 88, layout_engine=ImageFont.Layout.RAQM), fill="#1E9C8F", anchor="mm", direction="rtl")
    card = card.rotate(6, expand=True, resample=Image.BICUBIC); im.paste(card, (430, 470), card)
    for i, (ch, x, y, sz, r) in enumerate([("ب", 90, 470, 230, -10), ("پ", 150, 760, 200, 8), ("ت", 820, 1180, 190, -6), ("ٹ", 600, 1250, 170, 10), ("ث", 880, 1440, 160, -12)]):
        t = tile(ch, TILE_COLOURS[i], sz, r); im.paste(t, (x, y), t)
    m = mascot("hello", 900); im.paste(m, (-20, H - m.height - 10), m)
    return im


def ui_card(pre, box, width):
    """Zoomed, frameless UI card: only the part of the screen that shows the activity (v2 critic: empty screen = 'clinical')."""
    from PIL import ImageFilter
    raw = Image.open(glob.glob(f"{R}/store/raw/{pre}_*.png")[0]).convert("RGB").crop(box)
    raw = raw.resize((width, int(raw.height * width / raw.width)), Image.LANCZOS)
    b = 14; c = Image.new("RGBA", (width + 2 * b, raw.height + 2 * b), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, c.width - 1, c.height - 1), radius=64, fill="white")
    m = Image.new("L", raw.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, width - 1, raw.height - 1), radius=52, fill=255)
    c.paste(raw, (b, b), m); return c


def screenshot(pre, bg, pose, tilt, hl, sub, lang, n, box):
    if n == 1:
        return hero(bg, hl, sub, lang)
    from PIL import ImageFilter
    W, H = 1080, 1920; im, d = background(bg, n); captions(d, hl, sub, lang)
    card = ui_card(pre, box, 1000)
    max_h = 1060  # leave the bottom for Marko
    if card.height > max_h:
        k = max_h / card.height; card = card.resize((int(card.width * k), max_h), Image.LANCZOS)
    card = card.rotate(tilt, expand=True, resample=Image.BICUBIC)
    sh = Image.merge("RGBA", (*[Image.new("L", card.size, 0)] * 3, card.getchannel("A").point(lambda a: int(a * 0.33)))).filter(ImageFilter.GaussianBlur(26))
    x = (W - card.width) // 2; y = 380
    im.paste(sh, (x + 16, y + 28), sh); im.paste(card, (x, y), card)
    for i, ch in enumerate(TILES.get(pre, "")[:2]):  # two tiles in the margins below the card, never on app text
        t = tile(ch, TILE_COLOURS[(n + i) % 8], 170 - i * 20, (-10, 8)[i]); im.paste(t, ((W - 260, 40)[i] if n % 2 else (40, W - 240)[i], y + card.height - 40 + i * 150), t)
    m = mascot(pose, 470); mx = 20 if n % 2 else W - m.width - 20; im.paste(m, (mx, H - m.height - 6), m)
    return im


def feature():
    bg = Image.open(f"{R}/design/gen/out/feature_bg.jpg").convert("RGB"); w, h = bg.size; tw = int(h * 1024 / 500)
    bg = bg.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h)).resize((1024, 500), Image.LANCZOS).convert("RGBA")
    for ch, (x, y), sz, rot, col in [("ا", (425, 282), 108, -8, "#E8664F"), ("ب", (590, 322), 96, 6, "#3B4BA8"), ("پ", (735, 272), 100, -5, "#F2A93B")]:
        t = tile(ch, col, sz, rot); bg.alpha_composite(t, (x, y))  # real letters on the path's blank cards
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(NASTALIQ, 60, layout_engine=ImageFont.Layout.RAQM); d.text((985, 92), "اردو پڑھنا سیکھیں", font=f1, fill=INK, anchor="rm", direction="rtl")
    f2 = ImageFont.truetype(FREDOKA, 50); d.text((985, 180), "Urdu Qaida", font=f2, fill=TURQ, anchor="rm")
    f3 = ImageFont.truetype(FREDOKA_M, 30); d.text((985, 228), "Learn to read Urdu, offline", font=f3, fill=INK, anchor="rm")
    return bg.convert("RGB")


def main():
    out = f"{R}/store"; os.makedirs(f"{out}/screenshots_en", exist_ok=True); os.makedirs(f"{out}/screenshots_ur", exist_ok=True)
    feature().save(f"{out}/feature-graphic-1024x500.png")
    for i, (pre, bg, pose, tilt, eh, es, uh, us, box) in enumerate(SHOTS, 1):
        for lang, hl, sub in (("en", eh, es), ("ur", uh, us)):
            screenshot(pre, bg, pose, tilt, hl, sub, lang, i, box).save(f"{out}/screenshots_{lang}/{i:02d}.png")
    print("store assets written to", out)


if __name__ == "__main__":
    main()
