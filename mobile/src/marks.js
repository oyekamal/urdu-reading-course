// Vowel-mark scaffold fading. Units 1-7: marks always on. Units 8-10: a word's marks are hidden once the learner has read it correctly
// twice in a row (join / dictation / quiz / sight / check answers, or a Review card at box 3+) and has not peeked since. Unit 11+: off.
// The Settings checkbox is the manual override: true shows marks everywhere, false hides them everywhere, unset = the automatic fade.
import { db } from './db.js';
import { C } from './content.js';

const COUNT = new Set(['join', 'dictation', 'quiz', 'sight', 'check']);   // answers that prove the learner read the word
const NEED = 2;                                                           // clean reads in a row before the marks fade
const F = new Map();                                                      // item -> { n: clean reads since the last miss/peek, peek: ts of the last peek }
let LISTED = null;   // word -> the (first) unit that teaches it
const listed = () => LISTED || (LISTED = new Map(C.units.flatMap(u => u.words.map(w => [w[0], u.n])).reverse()));
const sight = () => new Set(C.letters?.sight_words || []);
const rec = item => { let r = F.get(item); if (!r) F.set(item, r = { n: 0, peek: 0 }); return r; };

export async function loadFluency(profileId) {
  F.clear();
  const at = (await db.by('attempts', 'profileId', profileId)).sort((a, b) => a.ts - b.ts);
  for (const a of at) { const r = rec(a.item); if (a.drill === 'peek') { r.n = 0; r.peek = a.ts; } else if (COUNT.has(a.drill)) { if (a.correct) r.n++; else r.n = 0; } }
  for (const c of await db.by('cards', 'profileId', profileId)) if (c.kind !== 'letter') { const r = rec(c.item); if (c.box >= 3 && c.lastOk !== false && (c.last || 0) > r.peek) r.n = Math.max(r.n, NEED); }
}
export function note(drill, item, ok) { const r = rec(item); if (drill === 'peek') { r.n = 0; r.peek = Date.now(); } else if (COUNT.has(drill)) r.n = ok ? r.n + 1 : 0; }
export function noteCard(item, ok) { const r = rec(item); r.n = ok ? r.n + 1 : 0; }   // self-graded Review card

export const mode = ctx => ctx.settings.marks === true ? 'on' : ctx.settings.marks === false ? 'off' : 'auto';
export const fading = (ctx, unitN) => mode(ctx) === 'auto' && unitN >= 8 && unitN <= 10;
// the plain boolean (Words lesson, letters, anything that is not a faded drill)
export const marksOn = (ctx, unitN) => { const m = mode(ctx); return m === 'on' || (m === 'auto' && unitN <= 10); };
// Not teaching targets, so unmarked from unit 8: words no unit lists, and sight words that a later unit teaches (ہے، کا، پر show up in unit 8 sentences but are drilled as a set).
const fluent = (item, unitN) => { const u = listed().get(item); if (u === undefined) return true; if (u > unitN && sight().has(item)) return true; return (F.get(item)?.n || 0) >= NEED; };
export function marksFor(ctx, unitN, item) { const m = mode(ctx); if (m !== 'auto') return m === 'on'; if (unitN <= 7) return true; if (unitN > 10) return false; return !fluent(item, unitN); }
// text of a word or a whole sentence {ur, v}: marked per token
export function textFor(ctx, unitN, w) {
  const m = mode(ctx); if (m !== 'auto') return m === 'on' ? w.v : w.ur; if (unitN <= 7) return w.v; if (unitN > 10) return w.ur;
  const u = w.ur.split(' '), v = w.v.split(' '); if (u.length !== v.length) return u.every(t => fluent(t, unitN)) ? w.ur : w.v;
  return u.map((t, i) => fluent(t, unitN) ? t : v[i]).join(' ');
}
// items whose marks are hidden right now (only those that actually carry marks)
export function hiddenItems(ctx, unitN, w) {
  if (!fading(ctx, unitN)) return [];
  const u = w.ur.split(' '), v = w.v.split(' '); if (u.length !== v.length) return textFor(ctx, unitN, w) === w.v ? [] : u.filter(t => listed().has(t));
  return u.filter((t, i) => fluent(t, unitN) && v[i] !== t);
}

// Tag a text node so peek can swap its marks in. Call after the node's text is set from textFor().
export function tag(node, w, hidden) { if (hidden.length) { node.dataset.mv = w.v; node.dataset.mu = node.textContent; node.dataset.mi = hidden.join('|'); } return node; }
// A "Show marks" chip on the box plus tap-on-the-word: marks show for 3 s, each peek is recorded and resets the word's fade counter.
export function peekWrap(box, marks) {
  if (!marks || !marks.fade || !marks.fade()) return box;
  const btn = document.createElement('button'); btn.type = 'button'; btn.className = 'btn btn-chip peek-btn'; btn.textContent = 'Show marks'; btn.setAttribute('aria-label', 'Show the vowel marks for 3 seconds'); btn.style.display = 'none';
  const hid = () => [...box.querySelectorAll('[data-mv]')];
  const peek = els => { if (!els.length) return; els.forEach(e => { e.textContent = e.dataset.mv; e.classList.add('peeking'); (e.dataset.mi || '').split('|').filter(Boolean).forEach(i => marks.peeked(i)); delete e.dataset.mp; }); setTimeout(() => els.forEach(e => { if (e.dataset.mu !== undefined && e.classList.contains('peeking')) { e.textContent = e.dataset.mu; e.classList.remove('peeking'); } }), 3000); };
  btn.onclick = e => { e.stopPropagation(); peek(hid().filter(x => !x.classList.contains('peeking'))); };
  box.addEventListener('click', e => { const t = e.target.closest && e.target.closest('[data-mv]'); if (t && !t.closest('button') && !t.closest('.word') && !t.classList.contains('peeking')) peek([t]); });
  const sync = () => { btn.style.display = hid().length ? '' : 'none'; };
  box.prepend(btn); new MutationObserver(sync).observe(box, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-mv'] }); sync();
  return box;
}
