// Leitner spaced review + the 10-minute session engine.
import { db, uid } from './db.js';
import { C, W } from './content.js';
const DAY = 86400000, BOXES = [0, 1, 2, 4, 8, 16]; // box n -> days until due

export async function ensureCards(profileId, unitN) {
  // cards exist only for units the learner has actually reached: a locked unit (tampered state, preview) never creates review cards
  unitN = Math.min(unitN, await currentUnit(profileId));
  // every letter and word taught up to unitN has a card; new cards are due now
  const have = new Set((await db.by('cards', 'profileId', profileId)).map(c => c.item));
  const items = [];
  C.units.filter(u => u.n < unitN).forEach(u => { u.letters.forEach(c => C.by[c] && items.push({ item: c, kind: 'letter' })); u.words.forEach(w => items.push({ item: w[0], kind: 'word', v: w[3] || w[0], rom: w[1], en: w[2], unit: u.n, idx: u.words.indexOf(w) })); });
  if (unitN >= 6) C.letters.sight_words.forEach((w, i) => items.push({ item: w, kind: 'sight', idx: i }));
  for (const it of items) if (!have.has(it.item)) await db.put('cards', { id: profileId + ':' + it.item, profileId, ...it, box: 1, due: Date.now(), seen: 0 });
}
export async function ensureCardsFor(profileId, letters) { const have = new Set((await db.by('cards', 'profileId', profileId)).map(c => c.item)); for (const c of letters) if (C.by[c] && !have.has(c)) await db.put('cards', { id: profileId + ':' + c, profileId, item: c, kind: 'letter', box: 1, due: Date.now() + DAY, seen: 0 }); }
export async function dueCards(profileId, limit = 12) {
  const now = Date.now(); const all = await db.by('cards', 'profileId', profileId);
  return all.filter(c => c.due <= now && (c.kind !== 'letter' || C.by[c.item])).sort((a, b) => a.box - b.box || a.due - b.due).slice(0, limit);
}
export async function gradeCard(card, correct) {
  const box = correct ? Math.min(card.box + 1, BOXES.length - 1) : 1;
  await db.put('cards', { ...card, box, seen: card.seen + 1, due: Date.now() + BOXES[box] * DAY, last: Date.now(), lastOk: correct });
}
export function audioKeyFor(card) {
  if (card.kind === 'letter') return 'names/' + C.by[card.item].id;
  if (card.kind === 'sight') return 'sight/' + String(card.idx).padStart(2, '0');
  return `units/u${String(card.unit).padStart(2, '0')}_${String(card.idx).padStart(2, '0')}`;
}
// A malformed or half-written progress record is repaired here, never allowed to crash a screen.
const isO = v => v && typeof v === 'object' && !Array.isArray(v);
export function normProgress(p, profileId) {
  const o = isO(p) ? p : {}; const units = {};
  if (isO(o.units)) for (const [k, v] of Object.entries(o.units)) { if (!/^\d{1,2}$/.test(k)) continue; const u = isO(v) ? { ...v } : {}; if (!isO(u.lessons)) delete u.lessons; if (!isO(u.steps)) delete u.steps; units[k] = u; }
  return { ...o, id: profileId, units, wpm: Array.isArray(o.wpm) ? o.wpm.filter(x => isO(x) && Number.isFinite(x.wpm)) : [], sessions: Number.isFinite(o.sessions) ? o.sessions : 0 };
}
export async function getProgress(profileId) { return normProgress(await db.get('progress', profileId), profileId); }
export async function markUnit(profileId, n, score, total) {
  // only the learner's current unit (or one already passed) can be marked: a locked unit can never be passed by a screen, a URL or edited state
  if (!Number.isInteger(n) || n < 0 || n > await currentUnit(profileId)) return false;
  const p = await getProgress(profileId); const passed = score >= Math.ceil(total * 0.8) || p.units[n]?.passed; p.units[n] = { ...(p.units[n] || {}), passed, score, total, at: Date.now() }; await db.put('progress', p); return passed;
}
export async function currentUnit(profileId) { const p = await getProgress(profileId); let n = 0; while (p.units[n]?.passed && n < 12) n++; return n; }
export async function startSession(profileId) { const s = { id: uid(), profileId, startedAt: Date.now(), bites: [], correct: 0, total: 0 }; await db.put('sessions', s); return s; }
export async function endSession(s) { s.endedAt = Date.now(); await db.put('sessions', s); const p = await getProgress(s.profileId); p.sessions = (p.sessions || 0) + 1; p.lastSession = Date.now(); await db.put('progress', p); }
// In-lesson mistakes feed the spaced repetition: a drill item answered wrong goes back to box 1 and is due within a day (never later than it
// already was), so it comes back in Review. Cards that do not exist yet are created. gradeCard (the self-graded Review path) is unchanged.
const DRILL_ITEM = { tell: 1, join: 1, quiz: 1, dictation: 1, read: 1, blend: 1, check: 1, marks: 1, sight: 1 };
function cardFor(item) {
  if (!item || !C.units) return null;
  if (C.by[item]) return { item, kind: 'letter' };
  for (const u of C.units) { const i = u.words.findIndex(w => w[0] === item); if (i >= 0) { const w = u.words[i]; return { item, kind: 'word', v: w[3] || w[0], rom: w[1], en: w[2], unit: u.n, idx: i }; } }
  const si = (C.letters.sight_words || []).indexOf(item); if (si >= 0) return { item, kind: 'sight', idx: si };
  return null;
}
export async function missCard(profileId, drill, item) {
  if (!DRILL_ITEM[drill]) return null;
  if (typeof item !== 'string' || !item) return null; let key = item; if (drill === 'blend') key = [...item][0];                 // a missed blend 'بی' sends the LETTER back
  const found = cardFor(key); if (!found) return null; const id = profileId + ':' + found.item; const old = await db.get('cards', id); const soon = Date.now() + BOXES[1] * DAY;
  const card = old ? { ...old, box: 1, due: Math.min(old.due, soon), lastOk: false, lastMiss: Date.now() } : { id, profileId, ...found, box: 1, due: soon, seen: 0, lastOk: false, lastMiss: Date.now() };
  await db.put('cards', card); return card;
}
export async function recordAttempt(profileId, unit, drill, item, correct, ms) { if (unit > await currentUnit(profileId)) return; /* a locked unit records nothing */ await db.put('attempts', { id: uid(), profileId, unit, drill, item, correct, ms, ts: Date.now() }); if (!correct) { try { await missCard(profileId, drill, item); } catch (e) { /* a failed card write never breaks a lesson */ } } }
export async function stats(profileId) {
  const cards = await db.by('cards', 'profileId', profileId); const p = await getProgress(profileId);
  return { letters: cards.filter(c => c.kind === 'letter').length, lettersMastered: cards.filter(c => c.kind === 'letter' && c.box >= 4).length, words: cards.filter(c => c.kind === 'word').length, wordsMastered: cards.filter(c => c.kind === 'word' && c.box >= 4).length, due: cards.filter(c => c.due <= Date.now()).length, unitsPassed: Object.values(p.units).filter(u => u.passed).length, sessions: p.sessions || 0, wpm: p.wpm || [] };
}
export async function pearls(profileId) { const p = await getProgress(profileId); return Object.values(p.units || {}).reduce((n, u) => n + Object.keys(u.lessons || {}).length, 0); }
// days practised in total: it only ever goes up, a missed day costs nothing (children's app: no streak-loss pressure)
export async function streak(profileId) { return new Set((await db.by('attempts', 'profileId', profileId)).map(a => new Date(a.ts).toDateString())).size; }
export async function addWpm(profileId, wpm, unit) { unit = Math.min(unit, await currentUnit(profileId)); /* a locked unit's passage is logged against the current unit */ const p = await getProgress(profileId); p.wpm = [...(p.wpm || []), { ts: Date.now(), wpm, unit }].slice(-50); await db.put('progress', p); }
