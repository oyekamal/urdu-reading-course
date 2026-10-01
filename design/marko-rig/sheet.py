#!/usr/bin/env python3
"""Contact sheets for the Marko Lottie states, rendered from the EXPORTED JSON.

    python3 design/marko-rig/sheet.py lottie   # python-lottie (cairo)  -> /tmp/claude-1000/marko_sheet_lottie.png
    python3 design/marko-rig/sheet.py web      # lottie-web light in Chromium via playwright -> marko_sheet_web.png
    python3 design/marko-rig/sheet.py strip    # one row of web frames next to the static PNG poses (critic input)

Each row: the static PNG pose for that state, then 7 frames spread over the whole file (intro, loop, outro).
"""
import io, json, sys, subprocess, time, socket
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
LOT = ROOT / "mobile/public/lottie"
POSES = ROOT / "design/gen/out"
OUTD = Path("/tmp/claude-1000"); OUTD.mkdir(parents=True, exist_ok=True)
STATES = ["idle", "talk", "cheer", "wave", "think", "listen", "sleep", "point"]
POSE = {"idle": "hello", "talk": "hello", "cheer": "cheer", "wave": "wave2", "think": "think", "listen": "listen",
        "sleep": "sleep", "point": "letter"}
CELL, N = 200, 7
PORT = 5302


def frames_for(d):
    op = d["op"]; return [round(i * (op - 1) / (N - 1)) for i in range(N)]


def pose_img(state, size=CELL):
    im = Image.open(POSES / f"mascot_{POSE[state]}.png").convert("RGBA"); im.thumbnail((size, size))
    c = Image.new("RGBA", (size, size), "white"); c.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im); return c


def compose(rows, path, label_fr):
    sheet = Image.new("RGB", (CELL * (N + 1) + 90, CELL * len(rows) + 24), "white"); dr = ImageDraw.Draw(sheet)
    for r, (state, ims, frs) in enumerate(rows):
        y = 24 + r * CELL
        dr.text((6, y + CELL // 2), state, fill="black")
        sheet.paste(pose_img(state), (90, y))
        for i, (im, f) in enumerate(zip(ims, frs)):
            sheet.paste(im.convert("RGB"), (90 + CELL * (i + 1), y))
            if label_fr: dr.text((90 + CELL * (i + 1) + 4, y + 4), f"f{f}", fill=(120, 120, 120))
    dr.text((90, 4), "static PNG", fill="black"); dr.text((90 + CELL, 4), label_fr, fill="black")
    sheet.save(path); print("wrote", path)


def sheet_lottie():
    from lottie.objects import Animation
    from lottie.exporters.cairo import export_png
    rows = []
    for s in STATES:
        d = json.loads((LOT / f"marko_{s}.json").read_text()); an = Animation.load(d); ims = []
        for f in frames_for(d):
            buf = io.BytesIO(); export_png(an, buf, frame=f); buf.seek(0)
            im = Image.open(buf).convert("RGBA"); bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
            ims.append(bg.resize((CELL, CELL), Image.LANCZOS))
        rows.append((s, ims, frames_for(d)))
    compose(rows, OUTD / "marko_sheet_lottie.png", "python-lottie frames")


def serve():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"], cwd=ROOT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try: socket.create_connection(("127.0.0.1", PORT), 0.2).close(); break
        except OSError: time.sleep(0.1)
    return srv


def web_frames(states, cell=CELL):
    """Render each requested frame in a fresh lottie-web light instance (autoplay off, goToAndStop)."""
    from playwright.sync_api import sync_playwright
    out = {}
    srv = serve()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": cell, "height": cell})
            pg.goto(f"http://127.0.0.1:{PORT}/design/marko-rig/frame.html")
            for s in states:
                d = json.loads((LOT / f"marko_{s}.json").read_text()); ims = []
                for f in frames_for(d):
                    pg.evaluate("([s,f]) => window.show(s,f)", [s, f]); pg.wait_for_function("window.ready === true")
                    ims.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGBA"))
                out[s] = (ims, frames_for(d))
            b.close()
    finally:
        srv.terminate()
    return out


def sheet_web():
    fr = web_frames(STATES)
    compose([(s, *fr[s]) for s in STATES], OUTD / "marko_sheet_web.png", "lottie-web frames")


def strip():
    """Critic input: top row static PNG poses, bottom row the matching lottie-web 'still' frame, at 160 px."""
    from playwright.sync_api import sync_playwright
    c = 180; srv = serve()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": c, "height": c})
            pg.goto(f"http://127.0.0.1:{PORT}/design/marko-rig/frame.html"); ims = []
            for s in STATES:
                d = json.loads((LOT / f"marko_{s}.json").read_text())
                f = next(m["tm"] for m in d["markers"] if m["cm"] == "still")
                pg.evaluate("([s,f]) => window.show(s,f)", [s, f]); pg.wait_for_function("window.ready === true")
                ims.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
            b.close()
    finally:
        srv.terminate()
    sh = Image.new("RGB", (c * len(STATES), c * 2 + 40), "white"); dr = ImageDraw.Draw(sh)
    for i, s in enumerate(STATES):
        sh.paste(pose_img(s, c).convert("RGB"), (i * c, 20)); sh.paste(ims[i], (i * c, c + 40))
        dr.text((i * c + 4, 4), f"PNG {POSE[s]}", fill="black"); dr.text((i * c + 4, c + 24), f"anim {s}", fill="black")
    sh.save(OUTD / "marko_strip_critic.png"); print("wrote", OUTD / "marko_strip_critic.png")


if __name__ == "__main__":
    {"lottie": sheet_lottie, "web": sheet_web, "strip": strip}[sys.argv[1] if len(sys.argv) > 1 else "lottie"]()
