// Content pack: letters, units, audio index, lesson scripts. Loaded once, offline from the bundle.
export const C = { letters: null, units: null, audio: null, by: {}, ready: null };
const player = new Audio();
export function play(key) { const src = C.audio[key]; if (!src) return false; player.src = src; player.play().catch(() => {}); return true; }
export const TATWEEL = 'ـ';
export const forms = l => [['isolated', l.ch], ['initial', l.joiner ? l.ch + TATWEEL : null], ['medial', l.joiner ? TATWEEL + l.ch + TATWEEL : null], ['final', TATWEEL + l.ch]];
export const W = w => ({ ur: w[0], rom: w[1], en: w[2], v: w[3] || w[0] });
export const shuffle = a => a.map(x => [Math.random(), x]).sort((p, q) => p[0] - q[0]).map(x => x[1]);
export const pad2 = n => String(n).padStart(2, '0');
export const wordKey = (unit, i) => `units/u${pad2(unit)}_${pad2(i)}`;
export const sentKey = (unit, i) => `sentences/u${pad2(unit)}_${pad2(i)}`;
export function taughtBefore(n) { return new Set(C.units.filter(u => u.n < n).flatMap(u => u.letters)); }
export function loadContent() {
  if (C.ready) return C.ready;
  C.ready = Promise.all([fetch('data/letters.json').then(r => r.json()), fetch('data/units.json').then(r => r.json()), fetch('data/audio_index.json').then(r => r.json())])
    .then(([L, U, A]) => { C.letters = L; C.units = U.units; C.audio = A; L.letters.forEach(l => C.by[l.ch] = l); const str = JSON.stringify(L) + JSON.stringify(U) + Object.keys(A).length; let h = 0; for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0; C.version = 'pack-' + h.toString(16) + ' · ' + L.letters.length + ' letters · ' + U.units.length + ' units · ' + Object.keys(A).length + ' clips'; return C; });
  return C.ready;
}
export const STROKE = { alif: 'one stroke, top to bottom', be: 'start top-right, shallow bowl leftwards, hook up; dots last', jim: 'small head stroke leftwards, then the round bowl below; dot last', dal: 'top down and out to the left in one angled stroke', re: 'top down and sweep left below the line', sin: 'three teeth right to left, then the bowl', toe: 'loop first, then the tall stroke on its right', ain: 'small c at the top, then the bowl', fe: 'small loop, then the bowl leftwards', kaf: 'base stroke first, right to left, then the sloping cap on top', lam: 'tall stroke down, curve into the bowl', mim: 'small loop, tail down-left', nun: 'deep round bowl; dot last', wao: 'small loop, short tail', he: 'small loop with a short tail (ھ: two bowls open at top)', ye: 'bowl that swings back under itself (ے: long flat sweep)', hamza: 'small hook, written last' };
export const DOTS = { 'ب': 1, 'پ': 3, 'ت': 2, 'ٹ': 1, 'ث': 3, 'ج': 1, 'چ': 3, 'خ': 1, 'ذ': 1, 'ڈ': 1, 'ڑ': 1, 'ز': 1, 'ژ': 3, 'ش': 3, 'ض': 1, 'ظ': 1, 'غ': 1, 'ف': 1, 'ق': 2, 'ن': 1, 'ی': 2, 'ئ': 1 };
export const BANDS = [['pre-reader', 0], ['letters', 1], ['words', 20], ['sentences', 40], ['fluent', 60]];
export const PRP = cwpm => cwpm > 90 ? 'exceeds grade-2 standard' : cwpm >= 60 ? 'meets standard' : cwpm > 0 ? 'below standard' : 'nonreader';
export const BAND_HELP = 'Bands by passage speed: pre-reader 0 · letters 1–19 · words 20–39 · sentences 40–59 · fluent 60+ cwpm. Grade-2 standard (USAID PRP): 60 cwpm meets, 90+ exceeds.';
export function bandFor(cwpm) { let b = BANDS[0][0]; for (const [name, min] of BANDS) if (cwpm >= min) b = name; return b; }
export const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
export const toast = m => { const t = document.getElementById('toast') || Object.assign(document.body.appendChild(document.createElement('div')), { id: 'toast', className: 'toast' }); t.textContent = m; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 1800); };
