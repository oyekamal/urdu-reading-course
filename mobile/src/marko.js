// Marko, the animated mascot. Vector Lottie states from design/marko-rig/make_marko.py (public/lottie/marko_<state>.json),
// played with lottie-web's light SVG player.
//
//   marko(state = 'idle', size = 120, cls = '') -> HTMLElement (div.marko, size x size, aria-hidden)
//   setMarko(el, state)                        -> changes the state in place (plays the old state's outro first)
//
// States: idle talk cheer wave think listen sleep point. Looping states loop (after a one-time intro from the rest
// pose, read from the file's 'loop' marker); one-shots (cheer, wave) play once, then switch to idle.
// prefers-reduced-motion: shows the file's 'still' frame, no playback. If the JSON can't load: the static webp pose.
import lottie from 'lottie-web/build/player/lottie_light';

export const MARKO_STATES = ['idle', 'talk', 'cheer', 'wave', 'think', 'listen', 'sleep', 'point'];
const POSE = { idle: 'hello', talk: 'hello', cheer: 'cheer', wave: 'wave2', think: 'think', listen: 'listen', sleep: 'sleep', point: 'letter' };
const cache = {};
const still = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

let styled = false;
function injectStyle() {
  if (styled) return; styled = true;
  const s = document.createElement('style'); s.dataset.marko = '';
  s.textContent = '.marko{position:relative;display:inline-block;flex:none;line-height:0;pointer-events:none}' +
    '.marko>.marko-l,.marko>img{position:absolute;inset:0;width:100%;height:100%}' +
    '.marko>img{object-fit:contain}.marko svg{display:block}';
  document.head.append(s);
}

const load = state => (cache[state] ||= fetch(`./lottie/marko_${state}.json`).then(r => {
  if (!r.ok) throw new Error(r.status); return r.json();
}).catch(e => { delete cache[state]; throw e; }));

const marker = (data, name) => (data.markers || []).find(m => m.cm === name);

export function marko(state = 'idle', size = 120, cls = '') {
  injectStyle();
  const el = document.createElement('div');
  el.className = ('marko ' + cls).trim();
  el.style.width = el.style.height = typeof size === 'number' ? size + 'px' : size;
  el.setAttribute('aria-hidden', 'true');
  el._marko = { state: null, anim: null, data: null, token: 0, phase: null };
  setMarko(el, MARKO_STATES.includes(state) ? state : 'idle');
  return el;
}

export function setMarko(el, state) {
  const m = el && el._marko; if (!m) return;
  if (!MARKO_STATES.includes(state)) state = 'idle';
  if (m.state === state && m.anim) return;
  const token = ++m.token; m.state = state;
  const go = () => { if (m.token === token) swap(el, state, token); };
  const out = m.anim && m.data && marker(m.data, 'outro');
  if (out && m.phase === 'loop' && !still()) {   // ease back to the rest pose before the new state starts
    m.phase = 'outro';
    const a = m.anim; a.loop = false;
    a.addEventListener('complete', go, { once: true });  // lottie-web ignores {once}; token check makes repeats harmless
    a.playSegments([out.tm, out.tm + out.dr], true);
    setTimeout(go, (out.dr / (m.data.fr || 60)) * 1000 + 120);  // safety net if 'complete' never fires
  } else go();
  load(state).catch(() => {});  // warm the cache while the outro plays
}

function swap(el, state, token) {
  const m = el._marko;
  if (m.swapped === token) return; m.swapped = token;
  load(state).then(data => {
    if (m.token !== token) return;
    const box = document.createElement('div'); box.className = 'marko-l';
    const loopM = marker(data, 'loop'), stillM = marker(data, 'still');
    const reduce = still();
    const a = lottie.loadAnimation({ container: box, renderer: 'svg', loop: false, autoplay: false,
      animationData: JSON.parse(JSON.stringify(data)), rendererSettings: { preserveAspectRatio: 'xMidYMid meet' } });
    const show = () => {
      if (m.token !== token) { a.destroy(); return; }
      if (m.anim) m.anim.destroy();
      el.querySelectorAll(':scope > .marko-l, :scope > img').forEach(n => n.remove());
      el.append(box); m.anim = a; m.data = data;
      if (reduce) { a.goToAndStop(stillM ? stillM.tm : 0, true); m.phase = 'still'; return; }
      if (!loopM) {                       // one-shot: play once, then idle
        m.phase = 'once';
        a.addEventListener('complete', () => { if (m.token === token) setMarko(el, 'idle'); });
        a.goToAndPlay(0, true); return;
      }
      const loopSeg = [loopM.tm, loopM.tm + loopM.dr];
      const startLoop = () => { if (m.token !== token) return; m.phase = 'loop'; a.loop = true; a.playSegments(loopSeg, true); };
      if (loopM.tm > 0) {                 // one-time intro from the rest pose
        m.phase = 'intro';
        const onDone = () => { a.removeEventListener('complete', onDone); startLoop(); };
        a.addEventListener('complete', onDone);
        a.playSegments([0, loopM.tm], true);
      } else startLoop();
    };
    a.addEventListener('DOMLoaded', show);
    a.addEventListener('data_failed', () => fallback(el, state, token));
  }).catch(() => fallback(el, state, token));
}

function fallback(el, state, token) {
  const m = el._marko; if (m.token !== token) return;
  if (m.anim) { m.anim.destroy(); m.anim = null; m.data = null; }
  el.querySelectorAll(':scope > .marko-l, :scope > img').forEach(n => n.remove());
  const img = document.createElement('img'); img.alt = ''; img.src = `./img/mascot_${POSE[state]}.webp`;
  el.append(img); m.phase = 'static';
}
