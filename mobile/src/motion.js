// round 11p: one place that decides WHEN animation may run, so Marko, fx and the ambient scene never burn the main thread
// for nothing. Pure policy + one shared frame driver; no screen knowledge beyond "what counts as an overlay".
//   watch(el, cb)        cb(ok) when el is on screen AND the tab is visible AND no overlay covers it (el inside the overlay is fine)
//   isCalm() / onCalm(f) after CALM_MS without a touch/key/scroll the ambient layer goes quiet (<html class="calm">); any input wakes it
//   wake()               treat as input
//   createPlayer(anim,fr,{fps})  drives a lottie-web instance at a capped rate from ONE shared requestAnimationFrame loop
//                        (lottie's own loop renders every rAF, 60 fps, which is what cost ~50 % of the main thread on Today)
const root = document.documentElement;
export const CALM_MS = 4000;
export const reduceMotion = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------------- calm (idle) state ----------------
let calm = false, calmT = 0;
const calmSubs = new Set();
export const isCalm = () => calm;
export const onCalm = f => { calmSubs.add(f); return () => calmSubs.delete(f); };
export function wake() {
  clearTimeout(calmT);
  if (calm) { calm = false; root.classList.remove('calm'); calmSubs.forEach(f => f(false)); }
  calmT = setTimeout(() => { calm = true; root.classList.add('calm'); calmSubs.forEach(f => f(true)); }, CALM_MS);
}
for (const ev of ['pointerdown', 'keydown', 'touchstart', 'wheel']) addEventListener(ev, wake, { passive: true, capture: true });
addEventListener('scroll', wake, { passive: true, capture: true });
wake();

// ---------------- overlays ----------------
const OVERLAY = 'body > .celebrate, body > .gate-back, body > .pr-ov, body > .stk-ov, body > .a11y-sheet, body > [role="dialog"], body > [aria-modal="true"]';
let overlays = [];
const coverSubs = new Set();
function scanOverlays() {
  const now = [...document.querySelectorAll(OVERLAY)];
  const same = now.length === overlays.length && now.every((n, i) => n === overlays[i]);
  overlays = now; if (same) return;
  root.classList.toggle('m-cover', now.length > 0);
  coverSubs.forEach(f => f());
}
// body children only (no subtree): overlays are always appended to <body>; attributes catch role/aria-modal being set late
new MutationObserver(scanOverlays).observe(document.body, { childList: true });
export const covered = el => overlays.length > 0 && !overlays.some(o => o.contains(el));

// ---------------- visibility ----------------
const watchers = new Set();
const io = typeof IntersectionObserver === 'function' ? new IntersectionObserver(es => {
  for (const e of es) { const w = e.target._mw; if (w) { w.inView = e.isIntersecting; w.eval(); } }
}) : null;
function evalAll() { watchers.forEach(w => w.eval()); }
document.addEventListener('visibilitychange', () => { if (!document.hidden) wake(); evalAll(); });
coverSubs.add(evalAll);

export function watch(el, cb) {
  const w = { el, cb, inView: !io, last: null,
    eval() { const ok = this.inView && !document.hidden && !covered(el); if (ok !== this.last) { this.last = ok; cb(ok); } } };
  el._mw = w; watchers.add(w); io && io.observe(el);
  return function unwatch() { watchers.delete(w); io && io.unobserve(el); el._mw = null; };
}

// ---------------- shared capped frame driver ----------------
// A setTimeout at the target rate, NOT requestAnimationFrame: a rAF loop asks for a main-thread frame on every vsync, which also
// drags every running CSS animation onto the main thread (measured: ~50 % busy at 6x CPU even at 12 fps of Lottie work). A timer
// wakes the main thread only when a frame is really drawn.
const players = new Set();
let timer = 0;
function frame() {
  timer = 0;
  const now = performance.now();
  let live = 0, next = 1e9;
  for (const p of players) { p._step(now); if (!p.paused && p.running) { live++; next = Math.min(next, p.interval); } }
  if (live) timer = setTimeout(frame, Math.max(8, next));   // all paused: the loop sleeps (resume() / play() kick it again)
}
const kick = () => { if (!timer && players.size) timer = setTimeout(frame, 0); };

export function createPlayer(anim, fr, { fps = 24 } = {}) {
  try { anim.setSubframe(false); } catch (e) {}
  const interval = 1000 / fps, gap = interval * 0.8;   // timer jitter tolerance
  const P = {
    anim, interval, seg: null, loop: false, t0: 0, last: -1e9, lastF: -1, cycle: 0, onDone: null, stopWhen: null,
    paused: false, pausedAt: 0, running: false, dead: false, fr: fr || 60,
    play(seg, { loop = false, onDone = null, stopWhen = null } = {}) {
      if (P.dead) return;
      P.seg = seg; P.loop = loop; P.onDone = onDone; P.stopWhen = stopWhen; P.t0 = performance.now(); P.last = -1e9; P.lastF = -1; P.cycle = 0;
      P.running = true; players.add(P); kick();
    },
    pause() { if (!P.paused) { P.paused = true; P.pausedAt = performance.now(); } },
    resume() { if (P.paused) { P.paused = false; P.t0 += performance.now() - P.pausedAt; kick(); } },
    stop() { P.running = false; players.delete(P); },
    kill() { P.dead = true; P.stop(); },
    render(f) { try { anim.goToAndStop(f, true); } catch (e) { P.kill(); } },
    _step(now) {
      if (P.paused || !P.running) return;
      const len = P.seg[1] - P.seg[0], el = (now - P.t0) / 1000 * P.fr;
      if (!P.loop && el >= len) {
        P.running = false; players.delete(P); P.render(P.seg[1]);
        const cb = P.onDone; P.onDone = null; cb && cb(); return;
      }
      let f;
      if (P.loop) {
        const c = Math.floor(el / len);
        if (c > P.cycle) { P.cycle = c; if (P.stopWhen && P.stopWhen()) { P.running = false; players.delete(P); P.render(P.seg[0]); return; } }
        f = P.seg[0] + (el % len);
      } else f = P.seg[0] + el;
      if (now - P.last < gap) return;
      P.last = now; f = Math.floor(f); if (f !== P.lastF) { P.lastF = f; P.render(f); }
    },
  };
  try { anim.addEventListener('destroy', () => P.kill()); } catch (e) {}
  return P;
}

// resolves once the first screen has painted and settled (1.2 s after window load, then browser idle): heavy optional work (the Lottie player,
// Marko/fx JSON, Urdu webfont warm-up) waits for this so it never competes with the first paint / largest paint for bandwidth or the main thread
export const settled = new Promise(res => {
  const idle = () => (window.requestIdleCallback ? requestIdleCallback(() => res(), { timeout: 1500 }) : setTimeout(res, 300));
  const go = () => setTimeout(() => requestAnimationFrame(idle), 1200);
  document.readyState === 'complete' ? go() : addEventListener('load', go, { once: true });
});

// heavy(fn): run fn in its own macrotask, at least ~24 ms after the previous heavy job, so building a Lottie (tens of ms of SVG work) never
// stacks with another one into a single long task (Total Blocking Time counts every task over 50 ms)
let heavyQ = Promise.resolve();
export const heavy = fn => { const p = heavyQ.then(() => new Promise(r => setTimeout(r, 24))).then(fn); heavyQ = p.catch(() => {}); return p; };
