#!/usr/bin/env python3
"""Generate the app's illustrated assets with Gemini image models, in one consistent style.

  python3 gen_assets.py mascot      # mascot poses (design/gen/out/mascot_<pose>.png, transparent)
  python3 gen_assets.py units       # 13 unit header illustrations
  python3 gen_assets.py one "<prompt>" name.png

Every prompt is wrapped in STYLE so the set stays consistent; a reference image (the approved mascot) is attached
to every mascot prompt so the character stays the same. Output is JPEG on white from the API; we convert white to
transparent with a flood fill from the edges (safe for flat art with dark outlines) and downscale to the target size.
"""
import base64, json, os, re, sys, time, urllib.request
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"; os.makedirs(OUT, exist_ok=True)
KEY = [l.split('=', 1)[1].strip().strip('"') for l in open('/home/oye/Documents/free_work/personal-agent-v2/.env') if l.startswith('GEMINI_API_KEY=')][0]
MODEL = os.environ.get("GEN_MODEL", "gemini-3.1-flash-image")
STYLE = ("Flat vector illustration for a children's app, thick clean indigo outlines (#1E2F55), no gradients, no shading, "
         "no texture, no text, no letters, plain pure white background, centered subject with generous margin, "
         "limited palette: Multani turquoise #1E9C8F, saffron #F2A93B, ajrak indigo #1E2F55, ralli red #C74A3B, chai cream #F7EBD5, leaf green #5FA55A. "
         "Warm, simple, rounded shapes, friendly, Pakistani everyday life, suitable for age 5.")
REF = f"{HERE}/markhor_ref.png"  # v0.7: Marko the markhor (Pakistan's national animal) replaced Toto the parrot


def call(prompt, ref=None, tries=3):
    parts = [{"text": STYLE + "\n\n" + prompt}]
    if ref and os.path.exists(ref):
        parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(open(ref, "rb").read()).decode()}})
        parts.append({"text": "Keep this exact character design: same colours, proportions, eye style and outline weight."})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for t in range(tries):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=180))
            for p in d["candidates"][0]["content"]["parts"]:
                if "inlineData" in p: return base64.b64decode(p["inlineData"]["data"])
            raise RuntimeError("no image in response: " + str(d)[:200])
        except Exception as e:
            if t == tries - 1: raise
            time.sleep(3 * (t + 1))


def transparent(img, thresh=235, tol=18):
    """White background -> alpha, flood-filled from the edges so white inside the drawing (eyes, teeth) survives."""
    im = img.convert("RGBA"); w, h = im.size; px = im.load()
    mask = Image.new("L", (w, h), 0); ImageDraw.floodfill  # noqa
    from collections import deque
    seen = bytearray(w * h); q = deque()
    for x in range(w): q.append((x, 0)); q.append((x, h - 1))
    for y in range(h): q.append((0, y)); q.append((w - 1, y))
    isbg = lambda p: p[0] > thresh - tol and p[1] > thresh - tol and p[2] > thresh - tol
    mp = mask.load()
    while q:
        x, y = q.popleft(); i = y * w + x
        if seen[i]: continue
        seen[i] = 1
        if not isbg(px[x, y]): continue
        mp[x, y] = 255
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))
    a = im.split()[3]; a = Image.eval(mask, lambda v: 255 - v); im.putalpha(a)
    return im


def save(data, name, size=None, alpha=True, trim=True):
    tmp = f"{OUT}/_raw.jpg"; open(tmp, "wb").write(data); im = Image.open(tmp)
    if alpha: im = transparent(im)
    if trim and alpha:
        bbox = im.getchannel("A").getbbox(); im = im.crop(bbox) if bbox else im
    if size: im.thumbnail(size, Image.LANCZOS)
    im.save(f"{OUT}/{name}", optimize=True); return f"{OUT}/{name} {im.size}"


MASCOT = "a small round baby markhor mascot named Marko (مارخور), turquoise fluffy body, cream chest and face, two short saffron spiral horns, big kind eyes, tiny beard, little hooves"
POSES = {"hello": "waving hello with one front hoof, cheerful", "listen": "head tilted, one hoof cupped behind the ear, listening", "think": "looking up with a hoof on chin, thinking", "cheer": "both front hooves up, jumping, celebrating, a few small stars around", "oops": "gentle encouraging smile, one hoof raised as if to say try again, no sad face", "sleep": "asleep sitting down, eyes closed, small z shapes", "read": "holding an open book and reading", "point": "pointing to the right with one hoof"}
UNITS = {0: "an open door with sunlight, a welcome mat", 1: "six colourful building blocks stacked", 2: "a magnifying glass over three dots", 3: "a tomato, a cap and a bridge in one scene", 4: "a wooden door, a moon and a night sky", 5: "a lion in a small jungle with a rose", 6: "a house with a flag on the roof and a bowl of steaming food", 7: "a girl and a boy holding a big box and a doll", 8: "a pen writing a letter beside a garden wall", 9: "a green parrot on a branch in the morning sun", 10: "a mango, a cup of chai and a small mirror", 11: "a calligraphy reed pen (qalam) and an ink pot beside a rolled newspaper, decorative swirling ribbon shapes, absolutely no letters, no writing, no glyphs", 12: "a stopwatch and a trophy on a school desk"}


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "mascot"
    if what == "one": print(save(call(sys.argv[2]), sys.argv[3])); return
    if what == "mascot":
        if not os.path.exists(REF):
            data = call(MASCOT + ", standing, waving hello, character sheet, single pose"); open(REF, "wb").write(data); print("reference saved", REF)
        for k, p in POSES.items(): print(save(call(f"{MASCOT}, {p}. Single character, full body.", REF), f"mascot_{k}.png", (512, 512)))
    if what == "units":
        for n, p in UNITS.items(): print(save(call(f"Unit header illustration: {p}. Wide composition, no characters, no letters."), f"unit_{n:02d}.png", (900, 500), alpha=False, trim=False))


if __name__ == "__main__":
    main()
