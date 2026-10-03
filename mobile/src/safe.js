// Round 11a: safety helpers shared by every screen. No imports, so any module can use them.
// esc(): escape anything user-typed (learner names, notes, goals, imported text) before it goes into an HTML template.
// cleanName(): what a name input may hold. cleanText(): same for longer free text. once()/tapLock(): one activation per action.
const MAP = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;' };
export const esc = s => String(s ?? '').replace(/[&<>"'`]/g, c => MAP[c]);
export const NAME_MAX = 40, TEXT_MAX = 300;
// control characters, bidi overrides and angle brackets never belong in a name; whitespace is collapsed; length counts characters, not bytes
const BAD = /[\u0000-\u001f\u007f-\u009f‪-‮⁦-⁩<>]/g;
const clip = (s, n) => { const a = Array.from(s); return a.length > n ? a.slice(0, n).join('') : s; };
const ZW = /[\u00ad\u200b\u200e\u200f\u2060-\u2064\ufeff\u034f\u061c\u180e]/g; // invisible characters (ZWNJ/ZWJ stay: Urdu words and emoji need them)
export const cleanName = (s, max = NAME_MAX) => { let r = String(s ?? '').replace(BAD, '').replace(ZW, '').replace(/\s+/g, ' ').trim().replace(/(\p{M}{3})\p{M}+/gu, '$1'); if (!/[\p{L}\p{N}\p{Emoji_Presentation}]/u.test(r)) return ''; return clip(r, max); };
export const cleanText = (s, max = TEXT_MAX) => clip(String(s ?? '').replace(BAD, ' ').trim(), max);
// A spreadsheet treats a cell starting with = + - @ as a formula: neutralise it in CSV exports.
export const csvCell = v => { let s = String(v ?? ''); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
// tapLock: a short global lock for screen-changing actions. A double tap lands on the NEW screen's button (the old one is gone),
// so the lock is time-based and shared: returns true when the caller may proceed.
let until = 0, start = 0;
// A burst of taps is one tap: while the lock is held, further taps extend it (at most 800 ms in total), so a triple tap at 100-300 ms gaps
// moves exactly one step, while a deliberate second tap 350 ms or more after the last one works normally.
let inClick = false; // true only while a real (or scripted) click is being dispatched: a lock taken by a timer must not swallow the user's next tap
export const tapLock = (ms = 350) => { const n = Date.now(); if (n < until) { until = Math.min(n + ms, start + 800); return false; } if (inClick) { start = n; until = n + ms; } return true; };
export const tapFree = () => { until = 0; start = 0; };
// The old screen's button is gone after a step, so the next tap of a burst lands on whatever is underneath (the new screen's button, the tab bar).
// While the lock is held every button-like tap is swallowed before it reaches any handler (the grown-up gate and text fields are exempt).
if (typeof document !== 'undefined') document.addEventListener('click', e => {
  inClick = true; setTimeout(() => { inClick = false; }, 0);
  const n = Date.now(); if (n >= until) return; const t = e.target; if (!t || !t.closest || t.closest('.gate-back, input, select, textarea, label')) return;
  if (t.closest('button, a, [role=button], .tile, .ob-opt, .ucard, .card')) { e.stopPropagation(); e.preventDefault(); until = Math.min(n + 350, start + 800); }
}, true);
// once(fn): the first call runs; further calls are ignored until fn has settled plus a short cool-down.
export function once(fn, ms = 350) {
  let busy = false;
  return function (...a) {
    if (busy) return;
    busy = true; const free = () => setTimeout(() => { busy = false; }, ms);
    try { const r = fn.apply(this, a); if (r && typeof r.then === 'function') r.then(free, free); else free(); return r; } catch (e) { busy = false; throw e; }
  };
}
// a button that can only be activated once per render: disables itself, then runs fn
export function onceBtn(btn, fn) { btn.onclick = e => { if (btn.disabled || btn.dataset.used) return; btn.dataset.used = '1'; try { const r = fn(e); if (r && r.then) r.catch(() => { delete btn.dataset.used; }); } catch (err) { delete btn.dataset.used; throw err; } }; return btn; }
