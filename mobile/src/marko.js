// Marko, the animated mascot. Vector Lottie states from design/marko-rig/make_marko.py (public/lottie/marko_<state>.json),
// played with lottie-web's light SVG player.
//
//   marko(state = 'idle', size = 120, cls = '') -> HTMLElement (div.marko, size x size, aria-hidden)
//   setMarko(el, state)                        -> changes the state in place (plays the old state's outro first)
//
// States: idle talk cheer wave think listen sleep point. Looping states loop (after a one-time intro from the rest
// pose, read from the file's 'loop' marker); one-shots (cheer, wave) play once, then switch to idle.
// round 11p: ONE animated Marko at a time (the newest-touched one that is on screen, tab visible and not under an overlay);
// the others sit on their still webp pose with a CSS breathing effect. Frames come from motion.js (capped rate, one shared
// loop). After CALM_MS with no input an idle loop finishes its cycle and rests on the loop's first frame until a touch wakes it.
// prefers-reduced-motion: shows the file's 'still' frame, no playback. If the JSON can't load: the static webp pose.
import { watch, createPlayer, isCalm, onCalm, reduceMotion, settled, heavy } from './motion.js';

export const MARKO_STATES = ['idle', 'talk', 'cheer', 'wave', 'think', 'listen', 'sleep', 'point'];
// 'wave' shows the standard hello pose while the Lottie loads (the screens mark Marko up as mascot_hello.webp, so the upgrade reuses the same file: no second request, no pose jump)
const POSE = { idle: 'hello', talk: 'hello', cheer: 'cheer', wave: 'hello', think: 'think', listen: 'listen', sleep: 'sleep', point: 'letter' };
const cache = {};
// lottie-web (the light SVG player, ~150 KB of script to parse and run) loads AFTER the first screen has painted; the still pose covers the gap
let lottieP = null;
const getLottie = () => (lottieP ||= settled.then(() => import('lottie-web/build/player/lottie_light')).then(m => m.default || m));
const still = reduceMotion;
const FPS = 24, FPS_AMBIENT = 15;   // reactions (talk, cheer, wave) 24; slow ambient loops 15: they are subtle, and each SVG frame is the expensive part
const AMBIENT = new Set(['idle', 'think', 'listen', 'sleep', 'point']);
const NO_CALM = new Set(['talk']);   // a talking Marko keeps moving while the clip plays, whatever the idle clock says

let styled = false;
function injectStyle() {
  if (styled) return; styled = true;
  const s = document.createElement('style'); s.dataset.marko = '';
  s.textContent = '.marko{position:relative;display:inline-block;flex:none;line-height:0;pointer-events:none}' +
    '.marko>.marko-l,.marko>img{position:absolute;inset:0;width:100%;height:100%}' +
    '.marko>img{object-fit:contain}.marko svg{display:block}' +
    '.marko>.marko-rest{opacity:0;transition:opacity .45s ease}.marko>.marko-rest.on{opacity:1}' +
    '@media (prefers-reduced-motion:no-preference){.marko.marko-still>img{transform-origin:50% 100%;animation:markoBreathe 3.6s ease-in-out infinite}}' +
    '@keyframes markoBreathe{50%{transform:scale(1.025,1.04)}}' +
    'html.calm .marko.marko-still>img,html.m-cover .marko.marko-still>img{animation-play-state:paused}';
  document.head.append(s);
}

const load = state => (cache[state] ||= settled.then(() => fetch(`./lottie/marko_${state}.json`)).then(r => {
  if (!r.ok) throw new Error(r.status); return r.json();
}).catch(e => { delete cache[state]; throw e; }));

const marker = (data, name) => (data.markers || []).find(m => m.cm === name);

// ---------------- who may animate ----------------
const all = new Set();      // every live marko element
let slot = null, clock = 0; // slot = the one allowed to run Lottie right now

function poster(el, state) {
  el.querySelectorAll(':scope > .marko-l, :scope > img').forEach(n => n.remove());
  const img = document.createElement('img'); img.alt = ''; img.decoding = 'sync'; img.src = `./img/mascot_${POSE[state] || 'hello'}.webp`;
  el.append(img); el.classList.add('marko-still');
}
function release(el) {      // gone from the page: free the player, the observer and the closures
  const m = el._marko; if (!m) return;
  m.token++; m.player?.kill(); m.player = null; try { m.anim?.destroy(); } catch (e) {} m.anim = null; m.data = null;
  m.unwatch?.(); m.unwatch = null; clearTimeout(m.restT);
  poster(el, m.state || 'idle');   // a node that is re-attached later still shows its pose
}
function demote(el) {
  const m = el._marko; if (!m) return;
  m.token++; clearTimeout(m.restT); m.player?.kill(); m.player = null; try { m.anim?.destroy(); } catch (e) {} m.anim = null; m.data = null; m.phase = null;
  poster(el, m.state || 'idle');
}
function arbitrate() {
  const now = performance.now();
  for (const e of all) {
    const m = e._marko;
    if (e.isConnected) { m.seen = true; continue; }
    if (m.seen || now - m.born > 3000) { release(e); all.delete(e); if (slot === e) slot = null; }   // removed (or never attached)
  }
  let best = null;
  for (const e of all) { const m = e._marko; if (m.ok && (!best || m.touched > best._marko.touched)) best = e; }
  if (!best) { slot?._marko?.player?.pause(); return; }       // nothing may run (hidden / offscreen / covered): freeze, keep the instance
  if (best !== slot) {
    if (slot && slot.isConnected) demote(slot);
    slot = best; const m = slot._marko;
    if (!m.anim) swap(slot, m.state, ++m.token);
  }
  if (slot._marko.phase !== 'calm') slot._marko.player?.resume();
}
// calm: crossfade to the still pose and pause the player (no per-frame work while nobody is touching the app); wake: fade back and resume
function rest(el) {
  const m = el._marko; if (!m.anim || m.phase !== 'loop' || NO_CALM.has(m.state)) return;
  m.phase = 'calm';
  let r = el.querySelector(':scope > .marko-rest');
  if (!r) { r = document.createElement('img'); r.className = 'marko-rest'; r.alt = ''; r.decoding = 'async'; r.src = `./img/mascot_${POSE[m.state] || 'hello'}.webp`; el.append(r); }
  requestAnimationFrame(() => r.classList.add('on'));
  const t = m.token; clearTimeout(m.restT);
  m.restT = setTimeout(() => { if (m.token === t && m.phase === 'calm') m.player?.pause(); }, 520);
}
function unrest(el) {
  const m = el._marko; if (m.phase !== 'calm') return;
  clearTimeout(m.restT); m.phase = 'loop';
  el.querySelector(':scope > .marko-rest')?.classList.remove('on');
  if (m.ok) m.player?.resume();
}
onCalm(c => { if (slot) c ? rest(slot) : unrest(slot); });

export function marko(state = 'idle', size = 120, cls = '') {
  injectStyle();
  const el = document.createElement('div');
  el.className = ('marko ' + cls).trim();
  el.style.width = el.style.height = typeof size === 'number' ? size + 'px' : size;
  el.setAttribute('aria-hidden', 'true');
  const st = MARKO_STATES.includes(state) ? state : 'idle';
  el._marko = { state: null, anim: null, data: null, token: 0, phase: null, player: null, ok: false, touched: 0, unwatch: null, seen: false, born: performance.now() };
  // instant still pose while the Lottie loads (slow phones showed an empty spot for seconds); removed on DOMLoaded
  poster(el, st);
  if (still()) { setMarko(el, st); return el; }   // reduced motion: static still frame per marko, no slot logic
  all.add(el); el._marko.unwatch = watch(el, ok => { el._marko.ok = ok; arbitrate(); });
  setMarko(el, st);
  return el;
}

export function setMarko(el, state) {
  const m = el && el._marko; if (!m) return;
  if (!MARKO_STATES.includes(state)) state = 'idle';
  const reduce = still();
  if (state === 'wave' && isCalm() && m.state === 'idle' && !reduce) return;   // the unprompted wave (a timer in learner.js) is skipped while the app is calm; a poke wakes the app first
  if (reduce) { if (m.state === state && m.anim) return; }
  else if (m.state === state) return;
  m.state = state; m.touched = ++clock;
  load(state).catch(() => {});  // warm the cache (also while an outro plays)
  if (!reduce && !m.anim) {     // not the animated one (yet): show this state's pose; arbitrate decides who runs
    if (el.querySelector(':scope > img')) el.querySelector(':scope > img').src = `./img/mascot_${POSE[state]}.webp`;
    if (el === slot) swap(el, state, ++m.token); else arbitrate();
    return;
  }
  const token = ++m.token;
  const go = () => { if (m.token === token) swap(el, state, token); };
  const out = m.anim && m.data && marker(m.data, 'outro');
  if (out && m.player && (m.phase === 'loop' || m.phase === 'calm') && !reduce) {   // ease back to the rest pose before the new state starts
    m.phase = 'outro';
    m.player.play([out.tm, out.tm + out.dr], { onDone: go });
    if (m.ok) m.player.resume();
    setTimeout(go, (out.dr / (m.data.fr || 60)) * 1000 + 160);  // safety net (e.g. the tab went hidden mid-outro); token check makes repeats harmless
  } else go();
}

function swap(el, state, token) {
  const m = el._marko;
  if (m.swapped === token) return; m.swapped = token;
  Promise.all([load(state), getLottie()]).then(r => heavy(() => r)).then(([data, lottie]) => {
    if (m.token !== token || (!el.isConnected && !still())) return;
    const box = document.createElement('div'); box.className = 'marko-l';
    const loopM = marker(data, 'loop'), stillM = marker(data, 'still');
    const reduce = still();
    const a = lottie.loadAnimation({ container: box, renderer: 'svg', loop: false, autoplay: false,
      animationData: JSON.parse(JSON.stringify(data)), rendererSettings: { preserveAspectRatio: 'xMidYMid meet' } });
    const show = () => {
      if (m.token !== token) { a.destroy(); return; }
      m.player?.kill(); if (m.anim) m.anim.destroy();
      el.querySelectorAll(':scope > .marko-l, :scope > img').forEach(n => n.remove());
      el.classList.remove('marko-still'); el.append(box); m.anim = a; m.data = data;
      if (reduce) { a.goToAndStop(stillM ? stillM.tm : 0, true); m.phase = 'still'; return; }
      const P = m.player = createPlayer(a, data.fr || 60, { fps: AMBIENT.has(state) ? FPS_AMBIENT : FPS });
      if (!m.ok) P.pause();               // hidden / offscreen / covered right now: build it frozen
      if (!loopM) {                       // one-shot: play once, then idle
        m.phase = 'once';
        P.play([0, a.totalFrames - 1], { onDone: () => { if (m.token === token) setMarko(el, 'idle'); } });
        return;
      }
      const loopSeg = [loopM.tm, loopM.tm + loopM.dr];
      const startLoop = () => {
        if (m.token !== token) return; m.phase = 'loop';
        P.play(loopSeg, { loop: true });
        if (m.ok) P.resume(); if (isCalm()) rest(el);
      };
      if (loopM.tm > 0) {                 // one-time intro from the rest pose
        m.phase = 'intro';
        P.play([0, loopM.tm], { onDone: startLoop });
      } else startLoop();
    };
    a.addEventListener('DOMLoaded', show);
    a.addEventListener('data_failed', () => fallback(el, state, token));
  }).catch(() => fallback(el, state, token));
}

function fallback(el, state, token) {
  const m = el._marko; if (m.token !== token) return;
  m.player?.kill(); m.player = null;
  if (m.anim) { m.anim.destroy(); m.anim = null; m.data = null; }
  poster(el, state); el.classList.remove('marko-still'); m.phase = 'static';
}
