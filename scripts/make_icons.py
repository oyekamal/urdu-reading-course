#!/usr/bin/env python3
"""Store icon (512 + 1024), adaptive launcher mipmaps, splash screens and feature-graphic base, all from the mascot art.

  python3 scripts/make_icons.py            # uses design/gen/out/mascot_hello.png

Icon: turquoise rounded field, saffron alif (ا) on the right, mascot peeking from the left. The alif is the first
letter of the course and reads as "Urdu" at any size; the mascot makes it ours."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASCOT = sys.argv[1] if len(sys.argv) > 1 else f"{R}/design/gen/out/mascot_hello.png"
TURQ, SAFF, INK, PAPER, CREAM = "#1E9C8F", "#F2A93B", "#1E2F55", "#F2F7F6", "#F7EBD5"
NASKH = f"{R}/assets/fonts/NotoNaskhArabic.ttf"
FREDOKA_TTF = None  # woff2 only; the icon has no Latin text


ICON_SRC = f"{R}/design/gen/out/icon_a.jpg"  # Gemini-illustrated icon (Marko holding the alif card), content inside the centre circle


def icon(size, fg_only=False):
    """Store/legacy icon = the illustration full-bleed. Adaptive foreground = same image at full canvas: Android masks the outer
    third, and the illustration keeps its subject inside the safe circle, so nothing important is cut."""
    im = Image.open(ICON_SRC).convert("RGBA"); w, h = im.size; c = min(w, h); im = im.crop(((w - c) // 2, (h - c) // 2, (w - c) // 2 + c, (h - c) // 2 + c)).resize((size, size), Image.LANCZOS)
    if not fg_only:
        mask = Image.new("L", (size, size), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * .2), fill=255)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0)); out.paste(im, (0, 0), mask); return out
    return im


def splash(w, h):
    im = Image.new("RGB", (w, h), PAPER); d = ImageDraw.Draw(im)
    m = Image.open(MASCOT).convert("RGBA"); side = int(min(w, h) * .5); m.thumbnail((side, side))
    im.paste(m, ((w - m.width) // 2, (h - m.height) // 2 - int(h * .06)), m)
    f = ImageFont.truetype(NASKH, int(min(w, h) * .09)); d.text((w // 2, (h + m.height) // 2 + int(h * .02)), "اردو پڑھنا سیکھیں", font=f, fill=TURQ, anchor="mm")
    return im


def main():
    out = f"{R}/store"; os.makedirs(out, exist_ok=True)
    icon(512).save(f"{out}/icon-512.png"); icon(1024).save(f"{out}/icon-1024.png")
    for n in (192, 512): icon(n).save(f"{R}/mobile/public/icon-{n}.png")
    res = f"{R}/mobile/android/app/src/main/res"
    for dpi, px in {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}.items():
        fg = icon(px, fg_only=True); fg.save(f"{res}/mipmap-{dpi}/ic_launcher_foreground.png")
        legacy = icon(px); legacy.convert("RGBA").save(f"{res}/mipmap-{dpi}/ic_launcher.png")
        rnd = Image.new("RGBA", (px, px), (0, 0, 0, 0)); mask = Image.new("L", (px, px), 0); ImageDraw.Draw(mask).ellipse((0, 0, px, px), fill=255); rnd.paste(legacy, (0, 0), mask); rnd.save(f"{res}/mipmap-{dpi}/ic_launcher_round.png")
    open(f"{res}/values/ic_launcher_background.xml", "w").write(f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">{TURQ}</color>\n</resources>')
    for dpi, (pw, ph) in {"mdpi": (320, 480), "hdpi": (480, 800), "xhdpi": (720, 1280), "xxhdpi": (960, 1600), "xxxhdpi": (1280, 1920)}.items():
        splash(pw, ph).save(f"{res}/drawable-port-{dpi}/splash.png"); splash(ph, pw).save(f"{res}/drawable-land-{dpi}/splash.png")
    splash(480, 320).save(f"{res}/drawable/splash.png")
    print("icons + splash written; store/ has icon-512 and icon-1024")


if __name__ == "__main__":
    main()
