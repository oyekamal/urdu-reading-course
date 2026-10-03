// Lottie animations from LottieFiles (public/lottie/*.json, credits in CREDITS.md), played with lottie-web's light SVG
// player. fx('confetti_burst') returns an element that starts playing once its JSON loads; respects reduced motion.
// round 11p: frames come from motion.js (capped at ~30 fps, one shared loop); a player pauses while its element is offscreen,
// the tab is hidden or an overlay covers it, looping fx also rest while the app is calm (no input for a few seconds), and a
// player is released as soon as its element leaves the page.
import { watch, createPlayer, isCalm, onCalm, reduceMotion, settled, heavy } from './motion.js';
const cache = {};
let lottieP = null;   // loaded on first use, after the first screen has painted
const getLottie = () => (lottieP ||= settled.then(() => import('lottie-web/build/player/lottie_light')).then(m => m.default || m));
const FPS = 30;
function whenConnected(box, cb, n = 90) { if (box.isConnected) cb(); else if (n > 0) requestAnimationFrame(() => whenConnected(box, cb, n - 1)); }
export function fx(name, { size = 160, loop = false, cls = '', speed = 1, onDone } = {}) {
  const box = document.createElement('div'); box.className = 'fx ' + cls; box.style.width = box.style.height = typeof size === 'number' ? size + 'px' : size; box.setAttribute('aria-hidden', 'true');
  Promise.all([(cache[name] ||= settled.then(() => fetch(`./lottie/${name}.json`)).then(r => r.json())), getLottie()]).then(r => heavy(() => r)).then(([data, lottie]) => whenConnected(box, () => {
    const still = reduceMotion();
    const a = lottie.loadAnimation({ container: box, renderer: 'svg', loop: false, autoplay: false, animationData: JSON.parse(JSON.stringify(data)) });
    box._anim = a;
    if (still) { a.goToAndStop((data.op - data.ip) - 1, true); return; }
    const P = createPlayer(a, (data.fr || 60) * speed, { fps: FPS }), total = (data.op - data.ip) - 1;
    let ok = true;
    const sync = () => { if (ok && !(loop && isCalm())) P.resume(); else P.pause(); };
    const off = onCalm(sync);
    const unwatch = watch(box, v => {
      ok = v; sync();
      if (!v && !box.isConnected) { off(); unwatch(); P.kill(); try { a.destroy(); } catch (e) {} box._anim = null; }  // left the page
    });
    a.addEventListener('destroy', () => { off(); unwatch(); });
    P.play([0, total], { loop, onDone });
    sync();
  })).catch(() => {});
  return box;
}
// a one-shot overlay burst over the whole screen (confetti on a win); removes itself
export function burst(name = 'confetti_burst', ms = 2600) { const b = fx(name, { size: '100%', cls: 'fx-burst' }); document.body.append(b); setTimeout(() => b.remove(), ms); return b; }
