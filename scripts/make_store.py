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
CAPTIONS = [  # (raw file prefix, EN, UR)
    ("01", "Hear every letter, then tap it", "ہر حرف سنیں، پھر چھوئیں"),
    ("02", "One letter per lesson", "ہر سبق میں ایک حرف"),
    ("03", "Trace it, dots last", "لکھیں، نقطے آخر میں"),
    ("04", "Letters become real words", "حروف الفاظ بن جاتے ہیں"),
    ("05", "Naskh and Nastaliq, both", "نسخ اور نستعلیق دونوں"),
    ("06", "Teacher mode assesses reading", "استاد موڈ: پڑھائی جانچیں"),
    ("07", "Parents see real progress, offline", "والدین پیشرفت دیکھیں، آف لائن"),
    ("08", "Just me, my family, or my class", "میں، میرا گھر، یا میری کلاس"),
]


def fit(text, font_path, max_w, start, rtl=False):
    for size in range(start, 20, -2):
        f = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
        if f.getlength(text, direction="rtl" if rtl else "ltr") <= max_w: return f
    return f


def screenshot(raw, en, ur, lang, n):
    W, H = 1080, 1920; im = Image.new("RGB", (W, H), PAPER if n % 2 else CREAM); d = ImageDraw.Draw(im)
    text = ur if lang == "ur" else en; rtl = lang == "ur"
    f = fit(text, NASTALIQ if rtl else LATIN, 960, 72 if rtl else 78, rtl)
    d.text((W // 2, 150 if not rtl else 170), text, font=f, fill=INK, anchor="mm", direction="rtl" if rtl else "ltr")
    shot = Image.open(raw).convert("RGB"); sw = 880; shot = shot.resize((sw, int(shot.height * sw / shot.width)), Image.LANCZOS); shot = shot.crop((0, 0, sw, min(shot.height, 1560)))
    frame = Image.new("RGB", (sw + 24, shot.height + 24), INK); mask = Image.new("L", frame.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, frame.width - 1, frame.height - 1), radius=56, fill=255)
    inner = Image.new("L", shot.size, 0); ImageDraw.Draw(inner).rounded_rectangle((0, 0, sw - 1, shot.height - 1), radius=44, fill=255)
    frame.paste(shot, (12, 12), inner); im.paste(frame, ((W - frame.width) // 2, 300), mask)
    return im


def feature():
    bg = Image.open(f"{R}/design/gen/out/feature_bg.jpg").convert("RGB"); w, h = bg.size; tw = int(h * 1024 / 500)
    bg = bg.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h)).resize((1024, 500), Image.LANCZOS); d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(NASTALIQ, 58, layout_engine=ImageFont.Layout.RAQM); d.text((980, 92), "اردو پڑھنا سیکھیں", font=f1, fill=INK, anchor="rm", direction="rtl")
    f2 = ImageFont.truetype(LATIN, 40); d.text((980, 176), "Urdu Qaida: Read & Quiz", font=f2, fill=TURQ, anchor="rm")
    f3 = ImageFont.truetype(LATIN, 24); d.text((980, 222), "letters, words, sentences. Fully offline.", font=f3, fill=INK, anchor="rm")
    return bg


def main():
    out = f"{R}/store"; os.makedirs(f"{out}/screenshots_en", exist_ok=True); os.makedirs(f"{out}/screenshots_ur", exist_ok=True)
    feature().save(f"{out}/feature-graphic-1024x500.png")
    for i, (pre, en, ur) in enumerate(CAPTIONS, 1):
        raws = glob.glob(f"{out}/raw/{pre}_*.png")
        if not raws: print("missing raw", pre); continue
        for lang in ("en", "ur"): screenshot(raws[0], en, ur, lang, i).save(f"{out}/screenshots_{lang}/{pre}.png")
    print("store assets written to", out)


if __name__ == "__main__":
    main()
