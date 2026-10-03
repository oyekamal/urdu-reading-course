import { setMarko } from './marko.js';
// Content pack: letters, units, audio index, lesson scripts. Loaded once, offline from the bundle.
export const C = { letters: null, units: null, audio: null, by: {}, ready: null };
let player = new Audio(); let queue = []; let watchdog = null;
function attach(p) { p.addEventListener('ended', drain); p.addEventListener('error', drain); return p; }
function drain() { const n = queue.shift(); if (n) { player.src = n; player.play().catch(() => {}); } }
attach(player);
function rebuild() { try { player.pause(); player.removeAttribute('src'); player.load(); } catch (e) {} player = attach(new Audio()); queue = []; }
// One shared player. Instruction clips (ui/*) wait behind whatever is playing (at most one queued); content clips
// interrupt so a tap always answers immediately. If a play does not start within 1.5 s the element is rebuilt and
// retried once: Android WebViews occasionally leave a media element wedged after a focus loss or a background/resume.
export function play(key, _retry) {
  const src = C.audio[key]; if (!src) return false;
  const busy = !player.paused && !player.ended && player.currentTime > 0;
  if (key.startsWith('ui/') && busy) { queue = [src]; return true; }
  if (!key.startsWith('ui/')) queue = [];
  document.querySelectorAll('.mascot.peek, .ob-m .mascot, .fx-stage .mascot').forEach(m => { if (m._marko) { setMarko(m, 'talk'); clearTimeout(m._talk); m._talk = setTimeout(() => setMarko(m, m.dataset.base || 'idle'), 1800); } else { m.classList.remove('talk'); void m.offsetWidth; m.classList.add('talk'); } }); // Marko talks whenever something is said
  player.src = src; const p = player.play(); if (p && p.catch) p.catch(() => {});
  clearTimeout(watchdog); watchdog = setTimeout(() => { if (player.src === src && (player.paused || player.currentTime === 0) && !player.ended) { if (!_retry) { rebuild(); play(key, true); } } }, 1500);
  return true;
}
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && player.error) rebuild(); });
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
    .then(([L, U, A]) => { C.letters = L; C.units = U.units; C.audio = A; L.letters.forEach(l => C.by[l.ch] = l); const str = JSON.stringify(L) + JSON.stringify(U) + Object.keys(A).length; let h = 0; for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0; C.version = 'app ' + (typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : 'dev') + ' · pack-' + h.toString(16) + ' · ' + L.letters.length + ' letters · ' + U.units.length + ' units · ' + Object.keys(A).length + ' clips'; return C; });
  return C.ready;
}
export const STROKE = { alif: 'one stroke, top to bottom', be: 'start top-right, shallow bowl leftwards, hook up; dots last', jim: 'small head stroke leftwards, then the round bowl below; dot last', dal: 'top down and out to the left in one angled stroke', re: 'top down and sweep left below the line', sin: 'three teeth right to left, then the bowl', toe: 'loop first, then the tall stroke on its right', ain: 'small c at the top, then the bowl', fe: 'small loop, then the bowl leftwards', kaf: 'base stroke first, right to left, then the sloping cap on top', lam: 'tall stroke down, curve into the bowl', mim: 'small loop, tail down-left', nun: 'deep round bowl; dot last', wao: 'small loop, short tail', he: 'small loop with a short tail (ھ: two bowls open at top)', ye: 'bowl that swings back under itself (ے: long flat sweep)', hamza: 'small hook, written last' };
// Dots as DRAWN on the glyph, per position (Urdu Naskh/Nastaliq): [count, 'above'|'below'], or a small mark that is not a dot:
// 'tah' (the little ط on ٹ ڈ ڑ) and 'hamza' (ئ). ی has no dots alone or at the end of a word, two below when it joins forward.
const DOT_BASE = { 'ب': [1, 'below'], 'پ': [3, 'below'], 'ت': [2, 'above'], 'ٹ': 'tah', 'ث': [3, 'above'], 'ج': [1, 'below'], 'چ': [3, 'below'], 'خ': [1, 'above'], 'ذ': [1, 'above'], 'ڈ': 'tah', 'ڑ': 'tah', 'ز': [1, 'above'], 'ژ': [3, 'above'], 'ش': [3, 'above'], 'ض': [1, 'above'], 'ظ': [1, 'above'], 'غ': [1, 'above'], 'ف': [1, 'above'], 'ق': [2, 'above'], 'ن': [1, 'above'], 'ئ': 'hamza' };
const DOT_JOINED = { 'ی': [2, 'below'], 'ں': [1, 'above'] };
export function dotInfo(ch, form = 'isolated') {
  const b = ((form === 'initial' || form === 'medial') && DOT_JOINED[ch]) || DOT_BASE[ch];
  if (!b) return { n: 0, pos: '', mark: null }; if (typeof b === 'string') return { n: 0, pos: '', mark: b }; return { n: b[0], pos: b[1], mark: null };
}
export const DOTS = { 'ب': 1, 'پ': 3, 'ت': 2, 'ث': 3, 'ج': 1, 'چ': 3, 'خ': 1, 'ذ': 1, 'ز': 1, 'ژ': 3, 'ش': 3, 'ض': 1, 'ظ': 1, 'غ': 1, 'ف': 1, 'ق': 2, 'ن': 1 };  // true dots on the isolated glyph (no tah, no hamza)
// which letter and which position does a tile show? 'ـبـ' -> {ch:'ب', form:'medial'}; null if it is not exactly one letter
export function glyphForm(text) { const t = (text || '').trim(), lead = t.startsWith(TATWEEL), trail = t.length > 1 && t.endsWith(TATWEEL), ch = t.split(TATWEEL).join(''); if ([...ch].length !== 1) return null; return { ch, form: lead && trail ? 'medial' : lead ? 'final' : trail ? 'initial' : 'isolated' }; }
// consonants that sound the same in Urdu: two of them never go in one tap-what-you-hear round (the clips are the same sound)
const SAME_SOUND = { 'ث': 'س', 'ص': 'س', 'ذ': 'ز', 'ض': 'ز', 'ظ': 'ز', 'ط': 'ت', 'ح': 'ہ', 'ع': 'ا' };
export const soundOf = c => SAME_SOUND[c] || c;
// assessment level that counts reading AND understanding: 60+ cwpm only 'meets' with comprehension at 4 of 5 or better
export const COMP_MIN = 4;
export function overallLevel(cwpm, comp, compDone = true) { const base = PRP(cwpm); if (cwpm < 60) return base; if (!compDone) return 'fluent, comprehension not tested: not yet a standard result'; return comp >= COMP_MIN ? base : 'below standard: reads fast, understands too little'; }
export function overallBand(cwpm, comp, compDone = true) { const b = bandFor(cwpm); return b === 'fluent' && !(compDone && comp >= COMP_MIN) ? 'sentences' : b; }
export const BANDS = [['pre-reader', 0], ['letters', 1], ['words', 20], ['sentences', 40], ['fluent', 60]];
export const PRP = cwpm => cwpm > 90 ? 'exceeds grade-2 standard' : cwpm >= 60 ? 'meets standard' : cwpm > 0 ? 'below standard' : 'nonreader';
export const BAND_HELP = 'Bands by passage speed: pre-reader 0 · letters 1–19 · words 20–39 · sentences 40–59 · fluent 60+ cwpm. Grade-2 standard (USAID PRP): 60 cwpm meets, 90+ exceeds.';
export function bandFor(cwpm) { let b = BANDS[0][0]; for (const [name, min] of BANDS) if (cwpm >= min) b = name; return b; }
export const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
export const toast = m => { const t = document.getElementById('toast') || Object.assign(document.body.appendChild(document.createElement('div')), { id: 'toast', className: 'toast', role: 'status' }); t.setAttribute('aria-live', 'polite'); t.textContent = m; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 1800); };

// comprehension as text for a saved assessment: a part that was not tested is never shown as 0/5
export const compText = a => a && a.compDone === false ? 'not tested' : (a && a.comp != null ? a.comp + '/5' : '-');
// level/band of a SAVED assessment: new records carry them; old ones are worked out the same way (comprehension counted, band from cwpm)
export const recBand = a => a.orfDone === false ? 'not tested' : overallBand(a.orf?.cwpm ?? 0, a.comp ?? 0, a.compDone !== false && a.comp != null);   // always recomputed: a legacy 'fluent' with weak comprehension is not fluent
export const recLevel = a => a.orfDone === false ? 'passage not tested: no standard result' : overallLevel(a.orf?.cwpm ?? 0, a.comp ?? 0, a.compDone !== false && a.comp != null);
