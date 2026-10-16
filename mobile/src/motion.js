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
let timer = 0, due = 0;
function frame() {
  timer = 0;
  const now = performance.now(), late = due ? now - due : 0;
  let live = 0, next = 1e9;
  for (const p of players) { p._step(now); if (!p.paused && p.running) { live++; next = Math.min(next, p.interval); } }
  if (live) { const d = Math.max(8, next); due = performance.now() + d; timer = setTimeout(frame, d); } else due = 0;   // all paused: the loop sleeps (resume() / play() kick it again)
  gov.frame(late, performance.now() - now, live > 0);
}
const kick = () => { if (!timer && players.size) { due = 0; timer = setTimeout(frame, 0); } };

// ---------------- adaptive quality governor ----------------
// Slow phones: Marko (and every other Lottie on the shared loop) costs 40-65 % of the main thread at 4x CPU throttle. Watch long tasks and
// the loop's own lateness/cost; when the device struggles step the frame cap down (native -> 12 -> 8 -> 6 fps and no breathe/blink/hop), and step back
// up after 30 s without trouble. The level is saved per device (localStorage 'urdu-marko-q') so a slow phone starts low next time.
// Level 0 = no cap (marko.js's own rates), so a good phone is untouched.
export const Q_CAPS = [Infinity, 12, 8, 6];
const Q_KEY = 'urdu-marko-q', Q_WINDOW = 5000, Q_CALM_MS = 30000, Q_COOL = 6000;
const lsGet = () => { try { const v = localStorage.getItem(Q_KEY); return v == null ? NaN : Number(v); } catch (e) { return NaN; } };
const lsSet = v => { try { localStorage.setItem(Q_KEY, String(v)); } catch (e) { /* private mode */ } };
const gov = {
  lvl: 0, best: 0, changes: 0, lastDown: 0, lastUp: 0, lastSignal: performance.now(), upT: 0, lt: [], fr: [], log: [], on: true, share: 0, source: 'default',
  init() {
    const s = lsGet();
    if (s >= 0 && s <= 3) { gov.lvl = s | 0; gov.source = 'saved'; }
    else if ((navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 2) { gov.lvl = gov.best = 1; gov.source = 'hardware'; }   // a weak phone never climbs above 12 fps on its own
    gov.applyLevel(false);
    try { new PerformanceObserver(l => { const t = performance.now(); if (document.hidden || !gov.on) return; for (const e of l.getEntries()) if (e.duration >= 50) gov.lt.push(t); gov.check(); }).observe({ entryTypes: ['longtask'] }); } catch (e) { /* no longtask API: the loop's own timing still works */ }
    document.addEventListener('visibilitychange', () => { gov.fr.length = 0; gov.lt.length = 0; gov.lastSignal = performance.now(); gov.schedUp(); });
    gov.schedUp();
  },
  frame(late, cost, live) {
    if (!gov.on || document.hidden || !live) return;
    const f = gov.fr; f.push({ t: performance.now(), cost, slow: late > 50 || cost > 35 }); if (f.length > 8) f.shift(); gov.check();
  },
  struggling() {
    const t = performance.now(); gov.lt = gov.lt.filter(x => t - x < Q_WINDOW);
    const f = gov.fr.filter(x => t - x.t < Q_WINDOW);
    gov.share = f.length >= 8 ? f.reduce((a, x) => a + x.cost, 0) / Math.max(1, f[f.length - 1].t - f[0].t + 1000 / 12) : 0;   // share of the main thread the shared loop's own frames take
    return gov.lt.length > 3 || (f.length >= 6 && f.filter(x => x.slow).length >= 5) || gov.share > 0.3;
  },
  check() {
    const t = performance.now(); if (!gov.struggling()) return;
    gov.lastSignal = t; gov.schedUp();
    if (t - Math.max(gov.lastDown, gov.lastUp) < Q_COOL || gov.lvl >= 3) return;   // let the last change settle before judging again
    if (gov.lastUp && t - gov.lastUp < 60000) gov.best = gov.lvl + 1;               // went back down soon after stepping up: that level is too much for this phone, stay below it
    gov.set(gov.lvl + 1, 'down');
  },
  schedUp() {
    clearTimeout(gov.upT); if (gov.lvl <= gov.best) return;
    gov.upT = setTimeout(() => { if (document.hidden || performance.now() - gov.lastSignal < Q_CALM_MS - 500) return gov.schedUp(); gov.lastUp = gov.lastSignal = performance.now(); gov.set(gov.lvl - 1, 'up'); gov.schedUp(); /* one step per 30 calm seconds */ }, Math.max(1000, Q_CALM_MS - (performance.now() - gov.lastSignal)));
  },
  set(l, why) {
    l = Math.max(0, Math.min(3, l | 0)); if (l === gov.lvl) return;
    if (why === 'down') gov.lastDown = performance.now();
    gov.log.push({ t: Math.round(performance.now()), from: gov.lvl, to: l, why }); gov.lvl = l; gov.changes++; gov.lt.length = 0; gov.fr.length = 0; if (why !== 'up') lsSet(l); gov.applyLevel(true);   // saved = the lowest level this phone had to drop to; calm step-ups do not raise it
  },
  applyLevel(kicked) {
    root.dataset.mq = String(gov.lvl); root.classList.toggle('m-q3', gov.lvl >= 3);
    players.forEach(p => p._cap()); if (kicked) kick();
  },
};
export const quality = () => gov.lvl;
export const qualityCap = () => Q_CAPS[gov.lvl];
export const lowQuality = () => gov.lvl >= 3;   // spring.js: skip the hop / blink / glance timers
// test hook (Playwright): window.__markoQ.get() -> {level, cap, changes, log, players}; .set(n) forces a level; .off() stops governing
window.__markoQ = { get: () => ({ level: gov.lvl, share: Math.round(gov.share * 100), cap: Q_CAPS[gov.lvl], best: gov.best, changes: gov.changes, source: gov.source, log: gov.log.slice(), players: players.size, running: [...players].filter(p => !p.paused && p.running).length, fps: [...players].map(p => Math.round(1000 / p.interval)) }), set: l => gov.set(l, 'forced'), off: () => { gov.on = false; }, on: () => { gov.on = true; } };
gov.init();

export function createPlayer(anim, fr, { fps = 24 } = {}) {
  try { anim.setSubframe(false); } catch (e) {}
  const P = {
    anim, base: fps, interval: 1000 / fps, gap: 800 / fps /* timer jitter tolerance */, seg: null, loop: false, t0: 0, last: -1e9, lastF: -1, cycle: 0, onDone: null, stopWhen: null,
    paused: false, pausedAt: 0, running: false, dead: false, fr: fr || 60,
    play(seg, { loop = false, onDone = null, stopWhen = null } = {}) {
      if (P.dead) return;
      P.seg = seg; P.loop = loop; P.onDone = onDone; P.stopWhen = stopWhen; P.t0 = performance.now(); P.last = -1e9; P.lastF = -1; P.cycle = 0;
      P.running = true; players.add(P); kick();
    },
    pause() { if (!P.paused) { P.paused = true; P.pausedAt = performance.now(); } },
    resume() { if (P.paused) { P.paused = false; P.t0 += performance.now() - P.pausedAt; kick(); } },
    setFps(f) { P.base = f; P._cap(); },   // calm: the hero Marko drops to a low rate instead of freezing
    _cap() { const f = Math.min(P.base, qualityCap()); P.interval = 1000 / f; P.gap = P.interval * 0.8; },   // the quality governor's cap applies on top of every requested rate
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
      if (now - P.last < P.gap) return;
      P.last = now; f = Math.floor(f); if (f !== P.lastF) { P.lastF = f; P.render(f); }
    },
  };
  try { anim.addEventListener('destroy', () => P.kill()); } catch (e) {}
  P._cap(); return P;
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
