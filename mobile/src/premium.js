// round 9c: premium layer. One import from main.js; everything attaches through observers and document listeners,
// so the screens owned by other modules are never edited.
//  1. light-catching objects: pearls, letter tiles, stickers and the letter card get a specular sheen that follows the finger or
//     the phone's tilt (two CSS variables on <html>, a gloss layer moved with transform only: no per-frame paint)
//  2. the Today village scene gets depth: three parallax layers + time-of-day ambient life (clouds, leaves, sun rays, stars, fireflies)
import { initStickers } from './stickers.js';
import './memory.js';

const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const root = document.documentElement;

// ---------- light source: pointer first, device tilt when it reports ----------
let lx = -0.35, ly = -0.45, raf = 0, gyro = false;
const clamp = v => Math.max(-1, Math.min(1, v));
function push() { raf = 0; root.style.setProperty('--tx', lx.toFixed(3)); root.style.setProperty('--ty', ly.toFixed(3)); }
function aim(x, y) { if (reduce.matches) return; lx = x; ly = y; if (!raf) raf = requestAnimationFrame(push); }
addEventListener('pointermove', e => { if (!gyro) aim(clamp((e.clientX / innerWidth) * 2 - 1), clamp((e.clientY / innerHeight) * 2 - 1)); }, { passive: true });
addEventListener('pointerdown', e => { aim(clamp((e.clientX / innerWidth) * 2 - 1), clamp((e.clientY / innerHeight) * 2 - 1)); gyro || askTilt(); }, { passive: true });
let asked = false;
function listen() { addEventListener('deviceorientation', e => { if (e.gamma == null) return; gyro = true; aim(clamp(e.gamma / 28), clamp(((e.beta ?? 45) - 50) / 28)); }, { passive: true }); }
// iOS only hands out tilt after a user gesture + permission; Android/desktop just start firing. Never blocks, never prompts twice.
function askTilt() { if (asked) return; asked = true; try { const D = window.DeviceOrientationEvent; if (D && typeof D.requestPermission === 'function') D.requestPermission().then(r => r === 'granted' && listen()).catch(() => {}); else if (D) listen(); } catch (e) {} }

// ---------- gloss layer on light-catching objects ----------
const LIT = '.pearl, .tile, .stk, .blob, .home-hero .today-card, .card.lc-card';
const vis = new IntersectionObserver(es => es.forEach(e => e.target.firstElementChild?.classList.contains('lc-spec') && (e.isIntersecting ? e.target.firstElementChild.setAttribute('data-v', '') : e.target.firstElementChild.removeAttribute('data-v'))), { rootMargin: '80px' });
function light(n) {
  if (n.nodeType !== 1) return; n.querySelectorAll?.('.ur.big').forEach(b => b.closest('.card')?.classList.add('lc-card')); // the letter card = a .card holding the big glyph
  const hits = n.matches?.(LIT) ? [n] : []; if (n.querySelectorAll) hits.push(...n.querySelectorAll(LIT));
  for (const t of hits) { if (t.dataset.lc || t.classList.contains('stk-ghost') || t.classList.contains('ghost')) continue; t.dataset.lc = '1'; const s = document.createElement('i'); s.className = 'lc-spec'; s.setAttribute('aria-hidden', 'true'); t.prepend(s); vis.observe(t); }
}

// ---------- the village scene ----------
const night = () => { const h = new Date().getHours(); return h >= 18 || h < 5; };
function grade() { const h = new Date().getHours(); return h >= 18 || h < 5 ? 'night' : h < 10 ? 'morning' : h < 15 ? 'noon' : 'golden'; }
const rnd = (a, b, i) => a + ((Math.sin(i * 91.7 + a * 13.1) + 1) / 2) * (b - a); // deterministic spread, no Math.random: same scene every visit
function scene(w) {
  if (w.dataset.pm) return; w.dataset.pm = '1'; const n = night(), g = grade(), bgUrl = (w.style.backgroundImage || '').trim();
  w.classList.add('pm'); w.dataset.grade = g;
  const far = document.createElement('div'); far.className = 'pm-layer pm-far'; far.setAttribute('aria-hidden', 'true'); if (bgUrl) far.style.backgroundImage = bgUrl;
  const mid = document.createElement('div'); mid.className = 'pm-layer pm-mid'; mid.setAttribute('aria-hidden', 'true');
  let h = '';
  if (n) { for (let i = 0; i < 14; i++) h += `<i class="pm-star" style="left:${rnd(4, 96, i)}%;top:${rnd(3, 40, i + 7)}%;--s:${rnd(2, 3.6, i + 3).toFixed(1)}px;--d:${rnd(2.4, 5, i).toFixed(1)}s;--dl:${(-rnd(0, 4, i + 5)).toFixed(1)}s"></i>`; for (let i = 0; i < 7; i++) h += `<i class="pm-fly" style="left:${rnd(6, 90, i + 11)}%;top:${rnd(48, 82, i + 2)}%;--d:${rnd(9, 15, i).toFixed(1)}s;--dl:${(-rnd(0, 9, i + 1)).toFixed(1)}s;--dx:${rnd(-26, 26, i + 4).toFixed(0)}px;--dy:${rnd(-22, 10, i + 6).toFixed(0)}px"></i>`; }
  else { h += '<i class="pm-rays"></i>'; for (let i = 0; i < 3; i++) h += `<i class="pm-cloud" style="top:${6 + i * 11}%;--w:${60 + i * 16}px;--d:${70 + i * 28}s;--dl:${-(i * 29)}s"></i>`; }
  for (let i = 0; i < (n ? 3 : 5); i++) h += `<i class="pm-leaf" style="left:${rnd(5, 92, i + 20)}%;--d:${rnd(15, 23, i).toFixed(1)}s;--dl:${(-rnd(0, 18, i + 9)).toFixed(1)}s;--c:${n ? '#7FA37A' : ['#6FB26A', '#E6A83C', '#8FC27A'][i % 3]}"></i>`;
  mid.innerHTML = h;
  const tint = document.createElement('div'); tint.className = 'pm-grade'; tint.setAttribute('aria-hidden', 'true');
  w.prepend(far, mid, tint);
  const fore = document.createElement('div'); fore.className = 'pm-layer pm-fore'; fore.setAttribute('aria-hidden', 'true'); fore.innerHTML = [0, 1].map(i => `<i class="pm-leaf pm-leaf-f" style="left:${i ? 74 : 14}%;--d:${i ? 11 : 13}s;--dl:${i ? -5 : -1}s;--c:${n ? '#8FB08A' : '#7DBB6E'}"></i>`).join(''); w.append(fore);
  new IntersectionObserver(es => w.classList.toggle('pm-off', !es[0].isIntersecting)).observe(w);
}

export function initPremium() {
  initStickers(); light(document.body);
  document.querySelectorAll('.hh-world, .hs-world').forEach(scene);
  new MutationObserver(ms => { for (const m of ms) for (const n of m.addedNodes) { if (n.nodeType !== 1) continue; light(n); if (n.matches?.('.hh-world, .hs-world')) scene(n); else n.querySelectorAll?.('.hh-world, .hs-world').forEach(scene); } }).observe(document.body, { childList: true, subtree: true });
}
initPremium();
