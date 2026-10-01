#!/usr/bin/env python3
"""Marko (the Urdu Qaida markhor) as a real Lottie cut-out rig with real keyframes.

Parts: head / body / arm are on-model art (Gemini, referenced on the approved PNG, then cleaned + palette-quantised by
prep_parts.py -> design/marko-rig/parts/*.png, embedded as image layers). Everything that has to MOVE inside the face is
vector on top: eyes (blink, look), closed-eye lids, smile, open mouth, zZz, stars, pointing tip. The raster eyes and
mouth are painted out of the head art so the vector ones replace them.

    python3 design/marko-rig/make_marko.py            # writes mobile/public/lottie/marko_<state>.json
    python3 design/marko-rig/gen_parts.py ; python3 design/marko-rig/prep_parts.py   # (once) part art -> parts/*.png
    python3 design/marko-rig/sheet.py lottie|web|strip   # verification contact sheets in /tmp/claude-1000/

Follows the lottie-motion skill: idle -> anticipation -> action -> settle; rest >= 40%; blink 100/50/100 ms every
3-5 s; mouth 200-300 ms; secondary action lags 50-100 ms; overshoot explicit keyframes; first shape in a list is on top.

Each file carries markers the player (mobile/src/marko.js) reads:
  still  - the frame shown under prefers-reduced-motion
  loop   - the looping segment (frames before it are a one-time intro from the rest pose)
  outro  - optional segment that returns to the rest pose before switching state
No marker 'loop' = one-shot (cheer, wave): play once, then the app switches to idle.
"""
import json, math, sys
from PIL import Image
from pathlib import Path
from lottie import objects
from lottie.objects import easing
from lottie.nvector import NVector as V

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "mobile/public/lottie"
FPS = 60
W = H = 512


def col(h):
    h = h.lstrip("#"); return objects.Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


TURQ, TURQ_D, CREAM, SAFF, INK, WHITE, PINK = (col(c) for c in
    ("#1E9C8F", "#178478", "#F7EBD5", "#F2A93B", "#1E2F55", "#FFFFFF", "#E8737A"))
FUR = col("#29968B")  # the fur colour as painted in the part art
SW = 6.5  # one outline width for the whole character (512 canvas -> ~1.5 px at 120 px)


def bez(x1, y1, x2, y2): return easing.Bezier(V(x1, y1), V(x2, y2))
STD, DECEL, ACCEL, SOFT, HOLD = bez(.4, 0, .2, 1), bez(0, 0, .2, 1), bez(.4, 0, 1, 1), bez(.45, 0, .55, 1), easing.Hold()

# ------------------------------------------------------------------ geometry helpers


def smooth_closed(pts, tension=1.0):
    """Closed Catmull-Rom spline through pts as a Lottie bezier."""
    b = objects.Bezier(); b.closed = True; n = len(pts)
    for i in range(n):
        p0, p1, p2 = V(*pts[i - 1]), V(*pts[i]), V(*pts[(i + 1) % n])
        t = (p2 - p0) * (tension / 6)
        b.add_point(p1, t * -1, t)
    return b


def smooth_open(pts, tension=1.0):
    b = objects.Bezier(); b.closed = False; n = len(pts)
    for i in range(n):
        p0 = V(*pts[max(i - 1, 0)]); p1 = V(*pts[i]); p2 = V(*pts[min(i + 1, n - 1)])
        t = (p2 - p0) * (tension / 6)
        b.add_point(p1, t * -1, t)
    return b


def poly(pts, closed=False):
    b = objects.Bezier(); b.closed = closed
    for p in pts: b.add_point(V(*p))
    return b


# ------------------------------------------------------------------ rig
import base64
PARTS = Path(__file__).with_name("parts")
R = 1.5                                   # parts are stored at 1.5x the 512-canvas size (crisp at 260 px on 3x screens)
HX0, HY0 = 256 - 503 / (2 * R), 8         # head art placement on the canvas
def Hp(ix, iy): return (HX0 + ix / R, HY0 + iy / R)
EYE_L, EYE_R = Hp(174, 291), Hp(325, 291)
NECK = Hp(250, 470)
SH_L, SH_R = (172, 322), (340, 322)       # shoulder pivots
ARM_PIV = (35, 20)                         # pivot inside arm.png (top centre)


class Rig:
    def __init__(self, seconds):
        self.an = objects.Animation(round(seconds * FPS), FPS)
        self.an.width, self.an.height = W, H
        self.parts, self.keys, self.rest = {}, {}, {}
        self.layers = []                    # top first
        self.build()
        for i, l in enumerate(self.layers): l.index = i + 1
        for l, p in self.parents: l.parent_index = p.index
        for l in self.layers: l.in_point, l.out_point = 0, self.an.out_point
        self.an.layers = self.layers

    # shape-group helpers (vector overlay parts)
    def grp(self, name, pivot, *children):
        g = objects.Group(); g.name = name or "g"
        for c in children: g.add_shape(c)
        if pivot is not None:
            g.transform.anchor_point.value = V(*pivot); g.transform.position.value = V(*pivot)
        if name: self.parts[name] = g; self.rest[name] = pivot
        return g

    shape = staticmethod(lambda b, fill=None, stroke=None, width=SW: Rig._shape(b, fill, stroke, width))

    @staticmethod
    def _shape(b, fill, stroke, width):
        g = objects.Group(); g.add_shape(b if not isinstance(b, objects.Bezier) else objects.Path(b))
        if stroke is not None:
            st = g.add_shape(objects.Stroke(stroke, width)); st.line_cap = objects.LineCap.Round; st.line_join = objects.LineJoin.Round
        if fill is not None: g.add_shape(objects.Fill(fill))
        return g

    def ell(self, c, r, fill, stroke=None, width=SW):
        r = r if isinstance(r, tuple) else (r, r)
        return self.shape(objects.Ellipse(V(*c), V(2 * r[0], 2 * r[1])), fill, stroke, width)

    # layer helpers
    def _place(self, l, name, pivot):
        l.name = name
        l.transform.anchor_point.value = V(*pivot); l.transform.position.value = V(*pivot)
        self.parts[name] = l; self.rest[name] = pivot

    def null(self, name, pivot, parent=None):
        l = objects.NullLayer(); self._place(l, name, pivot); self._nulls.append(l)
        if parent is not None: self.parents.append((l, parent))
        return l

    def image(self, name, asset, ipivot, wpivot, parent, sx=100, sy=100):
        l = objects.ImageLayer(asset); l.name = name
        l.transform.anchor_point.value = V(*ipivot); l.transform.position.value = V(*wpivot)
        l.transform.scale.value = V(sx / R, sy / R)
        self.parts[name] = l; self.rest[name] = wpivot; self.parents.append((l, parent)); self.layers.append(l)
        return l

    def shapes(self, name, parent, *groups):
        l = objects.ShapeLayer(); l.name = name
        for g in groups: l.add_shape(g)
        self.parents.append((l, parent)); self.layers.append(l)
        return l

    def build(self):
        self.parents, self._nulls = [], []
        world = self.null("world", (256, 500)); world.transform.scale.value = V(93, 93)
        root = self.null("root", (256, 500), world)
        body = self.null("body", (256, 500), root)
        head_b = self.null("headB", NECK, root); head = self.null("head", NECK, head_b)
        arms = {}
        for side, sh in (("L", SH_L), ("R", SH_R)):
            for F in ("", "F"):
                b = self.null("armB" + side + F, sh, root); a = self.null("arm" + side + F, sh, b); arms[side + F] = a
        # vector face parts, in head space
        eye = lambda side, c: self.grp("eye" + side, c, self.ell((c[0] + 6, c[1] - 7), 6, WHITE),
                                      self.ell((c[0] - 6, c[1] + 8), 2.6, WHITE), self.ell(c, (17.5, 18), INK))
        eyes = self.grp("eyes", (256, EYE_L[1]), eye("L", EYE_L), eye("R", EYE_R))
        lid = lambda c: self.shape(smooth_open([(c[0] - 17, c[1] + 1), (c[0], c[1] + 10), (c[0] + 17, c[1] + 1)]), None, INK, 6)
        closed = self.grp("closed", (256, EYE_L[1]), lid(EYE_L), lid(EYE_R)); closed.transform.opacity.value = 0
        my = 250
        tongue = self.ell((255, my + 18), (10, 6), PINK)
        mouth_open = self.grp("mouthO", (255, my), self.grp(None, None, tongue, self.shape(
            smooth_closed([(236, my), (255, my), (274, my), (269, my + 14), (255, my + 23), (241, my + 14)], 0.8), INK)))
        mouth_open.transform.scale.value = V(100, 0)
        smile = self.grp("smile", (255, my),
                         self.shape(poly([(255.5, 237), (255.5, 249)]), None, INK, 5.5),
                         self.shape(smooth_open([(228, 245), (241, 256.5), (255.5, 250), (270, 256.5), (283, 245)], 0.9), None, INK, 5.5))
        zzz = self.grp("zzz", None, *[self.zee(i) for i in range(3)])
        stars = self.grp("stars", None, *[self.star(i) for i in range(4)])
        ptr = {}
        for k, a in arms.items():
            side, F = k[0], k[1:]; sh = SH_L if side == "L" else SH_R
            tip = (sh[0], sh[1] + 104)
            g = self.grp("ptr" + k, (tip[0], tip[1] - 6), self.shape(objects.Rect(V(tip[0], tip[1] + 10), V(17, 34), 8.5), SAFF, INK, 5.5))
            g.transform.opacity.value = 0; ptr[k] = g
        # layers, top first
        self.shapes("stars", world, stars)
        for k in ("LF", "RF"):
            self.shapes("ptrLayer" + k, arms[k], ptr[k])
            sh = SH_L if k[0] == "L" else SH_R
            img = self.image("armImg" + k, "arm", ARM_PIV, sh, arms[k], -130 if k[0] == "R" else 130, 106)
            img.transform.opacity.value = 0
        self.shapes("face", head, zzz, eyes, closed, mouth_open, smile)
        self.image("headImg", "head", (250, 470), NECK, head)
        # turquoise neck patch between torso and head: merges the head into the shoulders (no white gap at the chin)
        self.shapes("neck", body, self.ell((256, 312), (74, 15), FUR))
        self.image("bodyImg", "body", (103, 215), (256, 504), body, 142, 150)
        for k in ("L", "R"):
            self.shapes("ptrLayer" + k, arms[k], ptr[k])
            sh = SH_L if k == "L" else SH_R
            self.image("armImg" + k, "arm", ARM_PIV, sh, arms[k], -130 if k == "R" else 130, 106)
        self.layers += self._nulls

    def zee(self, i):
        x, y, s = 394, 74, 30
        g = self.grp("z%d" % i, (x, y), self.shape(poly([(x - s / 2, y - s / 2), (x + s / 2, y - s / 2),
                                                        (x - s / 2, y + s / 2), (x + s / 2, y + s / 2)]), None, INK, 5))
        g.transform.opacity.value = 0
        return g

    def star(self, i):
        cx, cy = [(110, 150), (402, 130), (90, 300), (424, 290)][i]
        r1, r2 = 30 - (i % 2) * 7, 12 - (i % 2) * 3
        pts = [(cx + (r1 if k % 2 == 0 else r2) * math.cos(-math.pi / 2 + k * math.pi / 5),
                cy + (r1 if k % 2 == 0 else r2) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)]
        g = self.grp("star%d" % i, (cx, cy), self.shape(poly(pts, True), SAFF, INK, 4))
        g.transform.scale.value = V(0, 0)
        return g

    # --- keyframes
    MIRROR = ("armL", "armR", "ptrL", "ptrR")

    def key(self, name, prop, t_ms, value, ease=STD):
        self.keys.setdefault((name, prop), []).append((t_ms, value, ease))
        if name in self.MIRROR or (name in ("armBL", "armBR") and prop != "op"):
            self.keys.setdefault((name + "F", prop), []).append((t_ms, value, ease))

    def front_arm(self, side, t_on, t_off=None):
        """Swap to the front copy of an arm (drawn over head/body) from t_on until t_off."""
        for n, a, b2 in (("armImg" + side + "F", 0, 100), ("armImg" + side, 100, 0)):
            self.key(n, "op", 0, a, HOLD); self.key(n, "op", t_on, b2, HOLD)
            if t_off is not None: self.key(n, "op", t_off, a, HOLD)
        p = "ptr" + side  # keep the pointing tip on whichever copy is visible
        if (p, "op") in self.keys:
            for t, v, e in list(self.keys[(p, "op")]): self.keys.setdefault((p + "F", "op"), [])

    def pose(self, t, pose, ease=STD):
        for k, v in pose.items():
            name, prop = k.split("."); self.key(name, prop, t, v, ease)

    def bake(self):
        for (name, prop), ks in self.keys.items():
            if name not in self.parts: continue
            tr = self.parts[name].transform; pv = self.rest[name]
            target = {"rot": tr.rotation, "off": tr.position, "scale": tr.scale, "op": tr.opacity}[prop]
            base_scale = tr.scale.value if prop == "scale" else None
            ks = sorted(ks, key=lambda k: k[0]); frames, last = [], -1
            for t, _, _ in ks:
                f = max(round(t / 1000 * FPS), last + 1); frames.append(f); last = f
            def conv(v):
                if prop == "off": return V(pv[0] + v[0], pv[1] + v[1])
                if prop == "scale": return V(*v) if isinstance(v, tuple) else V(v, v)
                return v
            if len(ks) == 1: target.value = conv(ks[0][1]); continue
            for f, (_, v, e) in zip(frames, ks): target.add_keyframe(f, conv(v), e)
        return self.an

# ------------------------------------------------------------------ poses

REST = {"armL.rot": 14, "armR.rot": -14, "head.rot": 0, "head.off": (0, 0), "eyes.off": (0, 0)}


def blink(r, t):
    for side in "LR":
        r.key("eye" + side, "scale", t, (100, 100), ACCEL)
        r.key("eye" + side, "scale", t + 100, (106, 8), HOLD)
        r.key("eye" + side, "scale", t + 150, (106, 8), DECEL)
        r.key("eye" + side, "scale", t + 250, (100, 100), STD)


def eyes_static(r, t0, t1):
    for side in "LR":
        r.key("eye" + side, "scale", t0, (100, 100)); r.key("eye" + side, "scale", t1, (100, 100))


def breathe(r, t0, t1, period, amp=1.0, head=-4, arms=True):
    """Body scales up from the feet; head and arms ride it ~110 ms later (secondary action)."""
    n = round((t1 - t0) / period)
    for i in range(n + 1):
        t = t0 + i * period
        r.key("body", "scale", t, (100, 100), SOFT)
        if i < n: r.key("body", "scale", t + period / 2, (100 + 1.4 * amp, 100 + 2.4 * amp), SOFT)
    lag = 110
    def val(t): return head * amp * (0.5 - 0.5 * math.cos(2 * math.pi * ((t - t0 - lag) / period)))
    for part, k in (("headB", 1.0), ("armBL", 0.7), ("armBR", 0.7)) if arms else (("headB", 1.0),):
        r.key(part, "off", t0, (0, val(t0) * k), SOFT)
        for i in range(n + 1):
            for ph in (0, 0.5):
                t = t0 + lag + (i + ph) * period
                if t0 < t < t1: r.key(part, "off", t, (0, (head * amp if ph else 0) * k), SOFT)
        r.key(part, "off", t1, (0, val(t1) * k), SOFT)


def markers(an_dict, **segs):
    an_dict["markers"] = [{"tm": round(a / 1000 * FPS), "cm": name, "dr": round((b - a) / 1000 * FPS)}
                          for name, (a, b) in segs.items()]


def aim(side, target):
    """Arm rotation that points the hoof at a world target (arm hangs straight down at 0, + = clockwise)."""
    sx, sy = SH_L if side == "L" else SH_R
    return math.degrees(math.atan2(-(target[0] - sx), target[1] - sy))

# ------------------------------------------------------------------ states


def s_idle():
    r = Rig(9.0); T = 9000
    r.pose(0, REST); r.pose(T, REST)
    breathe(r, 0, T, 3000)
    blink(r, 2000); blink(r, 6200)
    for t, v in [(0, (0, 0)), (3900, (0, 0)), (4150, (6, 1)), (5050, (6, 1)), (5300, (0, 0)), (T, (0, 0))]:
        r.key("eyes", "off", t, v)                      # glance: hold, move 250 ms, hold 900, return
    for t, v in [(0, 0), (7100, 0), (7250, -3), (7550, 2.5), (7800, -1), (8000, 0), (T, 0)]:
        r.key("head", "rot", t, v, SOFT)                # small curious head tilt (secondary beat)
    for t, v in [(0, -14), (7180, -14), (7400, -19), (7700, -12), (7900, -14), (T, -14)]:
        r.key("armR", "rot", t, v, SOFT)
    return r, dict(still=(0, 0), loop=(0, T))


def s_talk():
    r = Rig(2.0); T = 2000
    r.pose(0, REST); r.pose(T, REST)
    breathe(r, 0, T, 2000, amp=0.6)
    syll = [(80, 90), (230, 40), (380, 100), (540, 55), (700, 0), (1000, 80), (1150, 30), (1310, 95), (1480, 45), (1640, 0)]
    r.key("mouthO", "scale", 0, (100, 0))
    for t, v in syll: r.key("mouthO", "scale", t, (100, v), STD)
    r.key("mouthO", "scale", T, (100, 0))
    for t, v in [(0, 0), (230, 2.5), (540, -1.5), (760, 0), (1150, -2.5), (1480, 1.5), (1700, 0), (T, 0)]:
        r.key("head", "rot", t, v, SOFT)
    for t, v in [(0, 0), (100, -3), (380, -4), (700, 0), (1000, -3), (1310, -4), (1680, 0), (T, 0)]:
        r.key("head", "off", t, (0, v), SOFT)
    for t, v in [(0, -14), (300, -24), (700, -14), (1200, -24), (1650, -14), (T, -14)]:
        r.key("armR", "rot", t, v, SOFT)
    blink(r, 1720)
    return r, dict(still=(380, 380), loop=(0, T))


def s_cheer():
    r = Rig(1.6); T = 1600
    up = {"armL.rot": 150, "armR.rot": -150}; down = {"armL.rot": 4, "armR.rot": -4}
    r.pose(0, REST); r.pose(220, {**REST, **down}, STD)
    r.pose(470, {**REST, **up}, DECEL); r.pose(560, {**REST, "armL.rot": 160, "armR.rot": -160}, SOFT)
    r.pose(700, {**REST, **up}, SOFT); r.pose(1150, {**REST, **up}, STD)
    r.pose(1500, REST, STD); r.pose(T, REST)
    rk = lambda t, off, sc, e=STD: (r.key("root", "off", t, off, e), r.key("root", "scale", t, sc, e))
    rk(0, (0, 0), (100, 100)); rk(220, (0, 0), (107, 90))
    rk(330, (0, -10), (95, 108), DECEL); rk(520, (0, -20), (98, 103), SOFT); rk(640, (0, -22), (100, 100), ACCEL)
    rk(820, (0, 0), (100, 100), DECEL); rk(900, (0, 0), (108, 91), SOFT); rk(1020, (0, 0), (97, 103), SOFT)
    rk(1120, (0, 0), (101, 99), SOFT); rk(1220, (0, 0), (100, 100)); rk(T, (0, 0), (100, 100))
    for t, v in [(0, 0), (220, 0), (400, 110), (480, 95), (1250, 95), (1450, 0), (T, 0)]:
        r.key("mouthO", "scale", t, (100, v))
    for side in "LR":   # happy squint at the apex
        for t, v in [(0, (100, 100)), (420, (100, 100)), (520, (106, 55)), (1100, (106, 55)), (1250, (100, 100)), (T, (100, 100))]:
            r.key("eye" + side, "scale", t, v)
    for t, v in [(0, 0), (240, -3), (500, 4), (700, 0), (T, 0)]: r.key("head", "rot", t, v, SOFT)
    for i in range(4):
        t0 = 420 + i * 90; n = "star%d" % i
        r.key(n, "scale", 0, (0, 0), HOLD); r.key(n, "scale", t0, (0, 0), DECEL)
        r.key(n, "scale", t0 + 180, (118, 118), SOFT); r.key(n, "scale", t0 + 300, (100, 100))
        r.key(n, "scale", 1200 + i * 50, (100, 100), ACCEL); r.key(n, "scale", 1420 + i * 40, (0, 0), HOLD)
        r.key(n, "rot", t0, -30, DECEL); r.key(n, "rot", t0 + 400, 0)
    return r, dict(still=(700, 700))


def s_wave():
    r = Rig(2.6); T = 2600
    r.pose(0, REST); r.pose(140, {**REST, "armL.rot": 6}, STD)              # anticipation dip
    r.pose(480, {**REST, "armL.rot": 140, "head.rot": -4, "eyes.off": (-2, 0)}, DECEL)
    t, hi = 480, True
    while t + 280 <= 1880:                                                  # 2.5 waves about the shoulder
        r.key("armL", "rot", t + 140, 162 if hi else 140, SOFT); r.key("armL", "rot", t + 280, 140 if hi else 162, SOFT)
        t += 280; hi = not hi
    r.pose(1900, {**REST, "armL.rot": 142, "head.rot": -4, "eyes.off": (-2, 0)}, STD)
    r.pose(2300, {**REST, "armL.rot": 20}, SOFT); r.pose(2420, REST, SOFT); r.pose(T, REST)
    for t, v in [(0, 0), (420, 0), (520, 60), (1700, 60), (1900, 0), (T, 0)]: r.key("mouthO", "scale", t, (100, v))
    breathe(r, 0, T, 2600, amp=0.5); eyes_static(r, 0, T)
    return r, dict(still=(900, 900))


def loop_state(seconds_loop, intro, outro, pose, extra):
    T0, T1 = intro, intro + seconds_loop; T = T1 + outro
    r = Rig(T / 1000); full = {**REST, **pose(r)}
    r.pose(0, REST); r.pose(T0, full, DECEL); r.pose(T1, full); r.pose(T, REST, STD)
    extra(r, T0, T1, full)
    return r, dict(still=(T0 + 300, T0 + 300), loop=(T0, T1), outro=(T1, T))


def s_think():
    def pose(r): return {"armR.rot": aim("R", (262, 284)), "head.rot": -7, "head.off": (0, -2), "eyes.off": (-4, -7)}
    def extra(r, T0, T1, full):
        a = full["armR.rot"]; r.front_arm("R", 140, T1 + 300)
        for t in (T0 + 1500, T0 + 1900):   # hoof taps the chin twice
            r.key("armR", "rot", t, a, SOFT); r.key("armR", "rot", t + 110, a - 6, SOFT); r.key("armR", "rot", t + 220, a, SOFT)
        for t, v in [(T0 + 2400, (-4, -7)), (T0 + 2650, (4, -7)), (T0 + 3500, (4, -7)), (T0 + 3750, (-4, -7))]: r.key("eyes", "off", t, v)
        for t, v in [(T0 + 2400, -7), (T0 + 2700, -4), (T0 + 3600, -4), (T0 + 3900, -7)]: r.key("head", "rot", t, v, SOFT)
        breathe(r, T0, T1, 4000); blink(r, T0 + 900)
    return loop_state(4000, 500, 450, pose, extra)


def s_listen():
    def pose(r): return {"armL.rot": aim("L", (104, 150)) , "armBL.off": (-8, -40), "head.rot": -8, "eyes.off": (-3, -2)}
    def extra(r, T0, T1, full):
        for t, v in [(T0 + 1000, -8), (T0 + 1300, -11), (T0 + 1550, -7), (T0 + 1800, -10), (T0 + 2100, -8)]: r.key("head", "rot", t, v, SOFT)
        r.key("armBL", "off", 0, (0, 0)); r.key("armBL", "off", T1 + 450, (0, 0))   # shoulder lifts so the hoof cups the ear
        breathe(r, T0, T1, 4000, arms=False); blink(r, T0 + 3200)
    return loop_state(4000, 500, 450, pose, extra)


def s_sleep():
    def pose(r): return {"armL.rot": 5, "armR.rot": -5, "head.rot": 5, "head.off": (0, 5), "root.scale": (102, 97)}
    def extra(r, T0, T1, full):
        T = T1 + 600
        r.key("root", "scale", 0, (100, 100)); r.key("root", "scale", T, (100, 100))   # settles down, heavy and sleepy
        for s in "LR":
            r.key("eye" + s, "scale", 0, (100, 100)); r.key("eye" + s, "scale", 300, (100, 100), ACCEL)
            r.key("eye" + s, "scale", 600, (106, 6), HOLD); r.key("eye" + s, "scale", T1 + 200, (106, 6), DECEL)
            r.key("eye" + s, "scale", T1 + 420, (100, 100))
        for t, v, e in [(0, 0, HOLD), (560, 0, STD), (640, 100, HOLD), (T1 + 160, 100, STD), (T1 + 220, 0, HOLD), (T, 0, STD)]:
            r.key("closed", "op", t, v, e)
        breathe(r, T0, T1, 4000, amp=1.5, head=-5)
        for i in range(3):
            t0 = T0 + 200 + i * 800; n = "z%d" % i
            r.key(n, "op", 0, 0, HOLD); r.key(n, "op", t0, 0, DECEL); r.key(n, "op", t0 + 400, 100, SOFT)
            r.key(n, "op", t0 + 1700, 100, ACCEL); r.key(n, "op", t0 + 2300, 0, HOLD); r.key(n, "op", T, 0)
            r.key(n, "off", 0, (0, 0), HOLD); r.key(n, "off", t0, (0, 0), SOFT); r.key(n, "off", t0 + 2300, (34, -60), HOLD)
            r.key(n, "off", T, (34, -60))
            sc = 70 + i * 20
            r.key(n, "scale", 0, (sc * .6, sc * .6), HOLD); r.key(n, "scale", t0, (sc * .6, sc * .6), SOFT)
            r.key(n, "scale", t0 + 2300, (sc * 1.2, sc * 1.2), HOLD); r.key(n, "scale", T, (sc * 1.2, sc * 1.2))
    return loop_state(4000, 800, 600, pose, extra)


def s_point():
    def pose(r): return {"armL.rot": 108, "head.rot": -5, "eyes.off": (-6, 0)}
    def extra(r, T0, T1, full):
        a = full["armL.rot"]
        for t, v, e in [(0, 0, HOLD), (T0 - 150, 0, DECEL), (T0, 100, HOLD), (T1 + 50, 100, ACCEL), (T1 + 200, 0, HOLD), (T1 + 400, 0, STD)]:
            r.key("ptrL", "op", t, v, e)
        for t in (T0 + 200, T0 + 520):     # two jabs toward the letter: pull back, poke, settle
            r.key("armL", "rot", t, a, STD); r.key("armL", "rot", t + 90, a - 5, STD)
            r.key("armL", "rot", t + 200, a + 6, DECEL); r.key("armL", "rot", t + 300, a, SOFT)
            r.key("armBL", "off", t, (0, 0), STD); r.key("armBL", "off", t + 90, (5, 0), STD)
            r.key("armBL", "off", t + 200, (-7, 0), DECEL); r.key("armBL", "off", t + 300, (0, 0), SOFT)
        r.key("armBL", "off", 0, (0, 0)); r.key("armBL", "off", T1 + 400, (0, 0))
        for t, v in [(0, 0), (T0, 45), (T0 + 900, 45), (T0 + 1150, 0), (T1, 0), (T1 + 200, 45), (T1 + 400, 0)]:
            r.key("mouthO", "scale", t, (100, v))
        blink(r, T0 + 1500)
    return loop_state(2400, 450, 400, pose, extra)


STATES = {"idle": s_idle, "talk": s_talk, "cheer": s_cheer, "wave": s_wave, "think": s_think,
          "listen": s_listen, "sleep": s_sleep, "point": s_point}


def rnd(o):
    if isinstance(o, float): return round(o, 2) if abs(o) < 2 else round(o, 1)
    if isinstance(o, list): return [rnd(x) for x in o]
    if isinstance(o, dict): return {k: (v if k == "p" and isinstance(v, str) else rnd(v)) for k, v in o.items() if k not in ("mn",)}
    return o


def assets():
    out = []
    for n in ("head", "body", "arm"):
        p = PARTS / f"{n}.png"; im = Image.open(p)
        out.append({"id": n, "w": im.width, "h": im.height, "u": "", "e": 1,
                    "p": "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()})
    return out


def build(name):
    r, segs = STATES[name]()
    an = r.bake()
    d = an.to_dict(); d["nm"] = "marko_" + name; d["assets"] = assets()
    markers(d, **segs)
    return an, rnd(d)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name in STATES:
        an, d = build(name)
        p = OUT / f"marko_{name}.json"
        p.write_text(json.dumps(d, separators=(",", ":")))
        print(f"{p.name:22s} {p.stat().st_size / 1024:5.1f} KB  {an.out_point / FPS:.2f}s  markers={[m['cm'] for m in d['markers']]}")
    lst = OUT / "list.json"; cur = json.loads(lst.read_text())
    for name in STATES:
        e = f"lottie/marko_{name}.json"
        if e not in cur: cur.append(e)
    lst.write_text(json.dumps(cur))
