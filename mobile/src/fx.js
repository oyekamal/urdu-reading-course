// Lottie animations from LottieFiles (public/lottie/*.json, credits in CREDITS.md), played with lottie-web's light SVG
// player. fx('confetti_burst') returns an element that starts playing once its JSON loads; respects reduced motion.
import lottie from 'lottie-web/build/player/lottie_light';
const cache = {};
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
export function fx(name, { size = 160, loop = false, cls = '', speed = 1, onDone } = {}) {
  const box = document.createElement('div'); box.className = 'fx ' + cls; box.style.width = box.style.height = typeof size === 'number' ? size + 'px' : size; box.setAttribute('aria-hidden', 'true');
  (cache[name] ||= fetch(`./lottie/${name}.json`).then(r => r.json())).then(data => {
    const a = lottie.loadAnimation({ container: box, renderer: 'svg', loop: loop && !still, autoplay: !still, animationData: JSON.parse(JSON.stringify(data)) });
    a.setSpeed(speed); if (still) a.goToAndStop(a.totalFrames - 1, true);
    if (onDone) a.addEventListener('complete', onDone);
    box._anim = a;
  }).catch(() => {});
  return box;
}
// a one-shot overlay burst over the whole screen (confetti on a win); removes itself
export function burst(name = 'confetti_burst', ms = 2600) { const b = fx(name, { size: '100%', cls: 'fx-burst' }); document.body.append(b); setTimeout(() => b.remove(), ms); return b; }
