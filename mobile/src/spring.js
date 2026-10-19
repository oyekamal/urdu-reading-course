// Spring motion layer, ported from the Cookling prototype (springVal): everything that appears settles with a little overshoot instead of
// fading in flat. One delegated module, no per-screen edits: a MutationObserver finds new cards, tiles, options and bubbles and springs them in
// (staggered), using the independent CSS properties `scale` / `translate` so it never fights the existing `transform` animations.
// prefers-reduced-motion: nothing here runs.
const calm = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

// x(t) follows a damped spring from `from` to `to` (k stiffness, d damping); fn(x) each frame; done() when settled. Returns cancel().
export function spring(from, to, { k = 260, d = 14 } = {}, fn, done) {
  let x = from, v = 0, last = performance.now(), raf = 0, dead = false;
  const step = now => {
    if (dead) return; const dt = Math.min(0.032, (now - last) / 1000); last = now;
    for (let i = 0; i < 2; i++) { v += (-k * (x - to) - d * v) * dt / 2; x += v * dt / 2; }
    fn(x);
    if (Math.abs(x - to) < 0.002 && Math.abs(v) < 0.02) { fn(to); if (done) done(); return; }
    raf = requestAnimationFrame(step);
  };
  raf = requestAnimationFrame(step); return () => { dead = true; cancelAnimationFrame(raf); };
}

// pop: scale from `from` up through 1 and settle (overshoot comes from the spring)
export function pop(node, from = 0.86, opts = { k: 300, d: 11 }) {
  if (calm() || !node || !node.isConnected) return;
  node.__popStop?.(); node.style.scale = String(from);
  node.__popStop = spring(from, 1, opts, s => { node.style.scale = String(s); }, () => { node.style.scale = ''; node.__popStop = null; });
}
// shake: horizontal damped wobble (a wrong answer: a soft shake, never a buzzer)
export function shake(node, amp = 8) {
  if (calm() || !node || !node.isConnected) return;
  node.__shakeStop?.(); node.__shakeStop = spring(amp, 0, { k: 300, d: 14 }, x => { node.style.translate = `${x}px 0`; }, () => { node.style.translate = ''; node.__shakeStop = null; });
}
// enter: rise + scale + fade with overshoot; `delay` in ms for staggering
export function enter(node, delay = 0, { rise = 26, from = 0.94, dx = 0 } = {}) {
  if (calm() || !node || !node.isConnected) return;
  node.style.opacity = '0.35'; node.style.scale = String(from); node.style.translate = `${dx}px ${rise}px`;
  setTimeout(() => {
    if (!node.isConnected) { node.style.opacity = node.style.scale = node.style.translate = ''; return; }
    node.__enterStop = spring(0, 1, { k: 230, d: 15 }, p => {
      node.style.opacity = String(Math.min(1, Math.max(0.35, 0.35 + p * 1.2)));
      node.style.scale = String(from + (1 - from) * p); node.style.translate = `${(1 - p) * dx}px ${(1 - p) * rise}px`;
    }, () => { node.style.opacity = node.style.scale = node.style.translate = ''; });
  }, delay);
}

// slide: a screen's own pieces glide in from the side the user came from (no fade-from-nothing, so nothing is ever blank): spring k140 d14.5, 24 px
export function slide(node, dir = 1, delay = 0) {
  if (calm() || !node || !node.isConnected) return;
  node.style.opacity = '0.4'; node.style.translate = `${24 * dir}px 0`;
  setTimeout(() => {
    if (!node.isConnected) { node.style.opacity = node.style.translate = ''; return; }
    spring(0, 1, { k: 140, d: 14.5 }, p => { node.style.opacity = String(Math.min(1, 0.4 + p * 1.6)); node.style.translate = `${24 * dir * (1 - p)}px 0`; }, () => { node.style.opacity = node.style.translate = ''; });
  }, delay);
}

const BLOCKS = '.card, .word, .ucard, .ob-opt, .ob-card-prev, .today-card, .sent-row';   // content blocks: rise in, staggered
const BUBBLES = '.ob-bubble, .hh-say, .feel-say, .peek-say, .sw-toast, .toast.show';       // speech bubbles / toasts: pop
const CHOICES = '.choices > .tile, .ob-choices > .tile';                                  // answer tiles: pop in one after another
const SKIP = '.hh-stage, .celebrate, .stk-ov, .gate-back, .a11y-sheet, .pr-ov, [data-nospring]';
const ALL = `${BLOCKS}, ${BUBBLES}, ${CHOICES}`;
let queue = [], pending = false, dirT = 0, dir = 1, lastTab = -1;

// which way did the user just go? Back buttons slide the new screen in from the left, tabs follow their order, everything else comes from the right.
function track(e) {
  const t = e.target; if (!t?.closest) return; dirT = performance.now();
  const tab = t.closest('.bottom button');
  if (tab) { const i = [...tab.parentElement.children].indexOf(tab); dir = lastTab < 0 || i === lastTab ? 1 : Math.sign(i - lastTab); lastTab = i; }
  else dir = t.closest('[aria-label="Back"], [aria-label="Leave lesson"], [aria-label="Back to path"], .page-back, .cel-back') ? -1 : 1;
}
const slideDir = () => (performance.now() - dirT < 2500 ? dir : 1);

// exitScreen: the screen being replaced stays on screen, as the SAME node (no clone, no snapshot), until the new one has its first child, so there is never
// an empty frame; then it pushes out (spring k140 d14.5, 24 px the opposite way the new screen comes from, fading to 0) and is removed after 260 ms.
// The caller inserts `next` (with data-screen) beside `old` first. Returns false (caller just removes `old`) for reduced motion, an empty/tiny/canvas screen
// or a page scrolled far down. The old node is inert + aria-hidden + pointer-events none, has no ids (no duplicates), and its Lotties / docks are hidden by CSS.
export function exitScreen(old, next) {
  if (calm() || !old?.isConnected || !old.firstElementChild || old.querySelector('canvas') || scrollY > innerHeight * 2 || old.querySelectorAll('*').length > 600) return false;   // a heavy old screen is not worth animating out on a weak phone
  const r = old.getBoundingClientRect(); if (r.width < 40 || r.height < 40) return false;
  const c0 = old.firstElementChild.getBoundingClientRect().top;
  old.querySelectorAll('[id]').forEach(n => n.removeAttribute('id')); old.removeAttribute('id');
  old.setAttribute('data-exit', ''); old.setAttribute('aria-hidden', 'true'); old.inert = true;
  old.style.cssText += `;position:fixed;z-index:-1;margin:0;left:${r.left}px;top:${r.top}px;width:${r.width}px;pointer-events:none`;
  const dy = c0 - old.firstElementChild.getBoundingClientRect().top; if (dy) old.style.top = `${r.top + dy}px`;   // out of flow the first child's margin no longer collapses through the parent: put it back exactly where it was
  let go = false, stop = null, t1 = 0, t2 = 0; const mo = new MutationObserver(() => { if (next.firstChild) start(); });
  const kill = () => { stop?.(); clearTimeout(t1); clearTimeout(t2); mo.disconnect(); old.remove(); };
  function start() {
    if (go) return; go = true; mo.disconnect(); clearTimeout(t1); const d = slideDir();
    stop = spring(0, 1, { k: 140, d: 14.5 }, p => { old.style.opacity = String(Math.max(0, 1 - 1.3 * p)); old.style.translate = `${-24 * d * p}px 0`; });
    t2 = setTimeout(kill, 260);
  }
  mo.observe(next, { childList: true }); if (next.firstChild) start(); else t1 = setTimeout(() => { start(); }, 450);   // slow build: do not hold the old screen forever
  setTimeout(kill, 1500);   // failsafe
  return true;
}

function flush() {
  pending = false; const batch = queue; queue = []; let i = 0, t = 0, c = 0, sl = 0;
  for (const n of batch) {
    if (!n.isConnected || n.closest(SKIP)) continue;
    const r = n.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight + 40) continue;       // only what is on screen
    const side = n.__side; n.__side = 0;
    if (n.matches(CHOICES)) { n.style.scale = '0.86'; setTimeout(() => pop(n, 0.86, { k: 300, d: 13 }), 45 * c++); continue; }
    if (n.matches(BUBBLES)) { pop(n, 0.55, { k: 280, d: 11 }); continue; }
    const cs = getComputedStyle(n);
    if (cs.animationName !== 'none') continue;                                                         // it already has its own entrance
    if (n.matches(BLOCKS)) { if (i++ < 9) enter(n, 40 * t++, { dx: 24 * (side || 0) }); }
    else if (side && cs.position !== 'fixed' && cs.position !== 'sticky' && sl < 8) slide(n, side, 30 * sl++);
  }
}
function note(n) {
  if (n.nodeType !== 1) return;
  // a whole screen arrived (a direct child of #app other than the tab bar): its blocks rise from the side the user came from, its other pieces slide in
  const top = n.parentElement === appRoot || n.parentElement?.hasAttribute('data-screen');   // a direct child of #app, or of a screen container made by exitScreen's callers
  if (top && !n.matches('.bottom, .hh-stage, .celebrate, [data-nospring], [data-exit]')) { const d = slideDir(); for (const k of n.children) { k.__side = d; queue.push(k); } }
  for (const e of [n, ...n.querySelectorAll(ALL)]) if (e.matches(ALL)) { if (!e.__side && top) e.__side = slideDir(); queue.push(e); }
  if (queue.length && !pending) { pending = true; queueMicrotask(flush); }
}
const appRoot = document.getElementById('app') || document.body;

/* ------------------------------------------------ celebration choreography ----
   path.js appends `.celebrate` to <body> (rays, top bar, stage with the character, title, +1 pearl chip, total line, Next). Its CSS animations
   all fire at once, so we take them over (class cel-spring switches them off) and run six staged spring beats instead, ~1.4 s end to end:
   rays swell -> character pops with squash/stretch -> title rises -> pearl chip pops and its pearls burst -> total line + Next rise ->
   the pearl total pulses when the count-up lands. A failsafe at 2.4 s clears every inline style, so nothing can stay hidden. */
function squashPop(n, from = 0.2, o = { k: 210, d: 9 }) {
  let prev = from; n.style.opacity = '1';
  return spring(from, 1, o, s => { const v = Math.max(-0.12, Math.min(0.12, (s - prev) * 4)); prev = s; n.style.scale = `${s * (1 - v * 0.8)} ${s * (1 + v)}`; }, () => { n.style.scale = ''; });
}
function celebrate(c) {
  if (c.__cel) return; c.__cel = true; c.classList.add('cel-spring');
  const q = sel => c.querySelector(sel);
  const rays = q('.cel-rays'), top = q('.cel-top'), stage = q('.cel-stage'), h1 = q('.cel-body > h1'), chip = q('.cel-chip'), line = q('.cel-body > p'), foot = q('.cel-foot'), tot = q('.cel-total');
  const hidden = [[rays, '0', '.5'], [top, '0', ''], [stage, '0', '.2'], [h1, '0', ''], [chip, '0', '.3'], [line, '0', ''], [foot, '0', '']].filter(x => x[0]);
  for (const [n, o, sc] of hidden) { n.style.opacity = o; if (sc) n.style.scale = sc; }
  if (h1) h1.style.translate = '0 22px'; if (line) line.style.translate = '0 16px'; if (foot) foot.style.translate = '0 70px'; if (top) top.style.translate = '0 -14px';
  c.querySelectorAll('.cel-pearl').forEach((p, k) => p.style.setProperty('--d', (0.56 + (k % 3) * 0.08) + 's'));   // the pearls burst out of the chip as it pops
  const stops = [], timers = []; let alive = true;
  const at = (ms, fn) => timers.push(setTimeout(() => { if (alive && c.isConnected) fn(); }, ms));
  const rise = (n, y, o = { k: 200, d: 14 }, from = 0) => stops.push(spring(0, 1, o, p => { n.style.opacity = String(Math.min(1, Math.max(from, p * 1.5))); n.style.translate = `0 ${y * (1 - p)}px`; }, () => { n.style.opacity = n.style.translate = ''; }));
  if (rays) { stops.push(spring(0, 1, { k: 90, d: 14 }, p => { rays.style.opacity = String(Math.min(1, p * 1.4)); rays.style.scale = String(0.5 + 0.5 * p); }, () => { rays.style.opacity = rays.style.scale = ''; })); }       // beat 1, 0 ms
  if (stage) at(80, () => { stops.push(squashPop(stage)); at(620, () => hop(stage)); });                                              // beat 2, 80 ms: pop, then one hop
  if (top) at(260, () => rise(top, -14));
  if (h1) at(380, () => rise(h1, 22, { k: 220, d: 13 }));                                                                              // beat 3
  if (chip) at(560, () => stops.push(squashPop(chip, 0.3, { k: 300, d: 10 })));                                                        // beat 4: pearl chip pop
  if (line) at(720, () => rise(line, 16));                                                                                           // beat 5
  if (foot) at(900, () => rise(foot, 70, { k: 190, d: 13 }));                                                                           // beat 6: Next button rises
  if (tot) { let t = 0; new MutationObserver(() => { clearTimeout(t); t = setTimeout(() => { if (alive && tot.isConnected) pop(tot, 1.5, { k: 420, d: 13 }); }, 140); }).observe(tot, { childList: true, characterData: true, subtree: true }); }   // count-up landed: swell
  timers.push(setTimeout(() => {   // failsafe: whatever happened (hidden tab, cancelled frames), nothing stays hidden or half-scaled
    alive = false; stops.forEach(f => f());
    for (const [n] of hidden) n.style.opacity = n.style.scale = n.style.translate = '';
  }, 2400));
  new MutationObserver((_, ob) => { if (!c.isConnected) { alive = false; timers.forEach(clearTimeout); stops.forEach(f => f()); ob.disconnect(); } }).observe(document.body, { childList: true });
}

if (!calm()) {
  new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(note))).observe(appRoot, { childList: true, subtree: true });
  addEventListener('pointerdown', track, { passive: true, capture: true });
  new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(n => { if (n.nodeType !== 1) return; if (n.matches?.('.celebrate')) celebrate(n); else if (n.matches?.(BUBBLES)) note(n); }))).observe(document.body, { childList: true });
  // answer feedback has ONE owner: this observer. A correct tile pops once (1.16, k260 d10), a wrong tile shakes once (amp 8, k300 d14). feel.js adds only sound,
  // haptics, sparkles and the glow ring; the CSS keyframes for .tile.ok/.tile.no are switched off in style.css. The flags reset when the class goes away, so a tile that is wrong twice shakes twice.
  new MutationObserver(ms => ms.forEach(m => {
    const t = m.target; if (m.attributeName !== 'class' || !t.classList?.contains('tile')) return;
    const no = t.classList.contains('no'), ok = t.classList.contains('ok');
    if (no && !t.__shook) shake(t, 8); if (ok && !t.__won) pop(t, 1.16, { k: 260, d: 10 });
    t.__shook = no; t.__won = ok;
  })).observe(appRoot, { attributes: true, subtree: true, attributeFilter: ['class'] });
}

/* ------------------------------------------------ Marko is never static ----
   marko.js keeps the one animated Marko running (12 fps when the app is calm instead of freezing it) and a CSS breath (scale 1 -> 1.02) on the rig.
   Here, one randomized timer adds the spring life on top: every ~7.5 s a squash-and-stretch hop, in between a quick blink-squash or a glance to the side. */
function hop(n) {
  if (calm() || !n.isConnected || n.__hop) return; n.__hop = true;
  spring(1, 0.88, { k: 600, d: 26 }, s => { n.style.scale = `${2 - s} ${s}`; }, () => {
    spring(0, 1, { k: 170, d: 9 }, p => { const a = Math.sin(Math.PI * Math.min(Math.max(p, 0), 1)); n.style.translate = `0 ${-24 * a}px`; n.style.scale = `${1 - 0.06 * a} ${1 + 0.1 * a}`; }, () => { n.style.translate = n.style.scale = ''; n.__hop = false; });
  });
}
function blink(n) {
  if (n.__hop) return; n.__hop = true;
  n.animate([{ scale: '1 1' }, { scale: '1.03 .94', offset: .38 }, { scale: '.995 1.012', offset: .7 }, { scale: '1 1' }], { duration: 230, easing: 'ease-out' }).onfinish = () => { n.__hop = false; };
}
function glance(n) {
  if (n.__hop) return; n.__hop = true; const d = Math.random() < .5 ? -1 : 1;
  n.animate([{ translate: '0 0', rotate: '0deg' }, { translate: `${4 * d}px 0`, rotate: `${4 * d}deg`, offset: .32 }, { translate: `${4 * d}px 0`, rotate: `${4 * d}deg`, offset: .68 }, { translate: '0 0', rotate: '0deg' }],
    { duration: 780, easing: 'cubic-bezier(.3,1.5,.5,1)' }).onfinish = () => { n.__hop = false; };
}
let lastHop = 0;
function life() {
  setTimeout(life, 2200 + Math.random() * 2400);
  if (document.documentElement.classList.contains('m-q3')) return;   // quality governor level 3 (motion.js): slow phone, no hop/blink/glance
  if (document.hidden || document.querySelector('.celebrate, .gate-back, .a11y-sheet, .stk-ov')) return;
  const m = [...document.querySelectorAll('#app .marko, #app img.mascot')].find(e => { if (e.closest('[data-exit]')) return false; const r = e.getBoundingClientRect(); return r.width > 60 && r.top > 0 && r.bottom < innerHeight; });
  if (!m) return; const now = performance.now();
  if (now - lastHop > 7500 && !m.closest('.hh-stage') && Math.random() < 0.7) { lastHop = now; hop(m); return; }   // Today's hero Marko has its own poke squash: it only blinks and glances
  Math.random() < 0.55 ? blink(m) : glance(m);
}
if (!calm()) setTimeout(life, 4000);
