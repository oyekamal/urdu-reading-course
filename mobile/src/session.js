// Leitner spaced review + the 10-minute session engine.
import { db, uid } from './db.js';
import { C, W } from './content.js';
const DAY = 86400000, BOXES = [0, 1, 2, 4, 8, 16]; // box n -> days until due

export async function ensureCards(profileId, unitN) {
  // every letter and word taught up to unitN has a card; new cards are due now
  const have = new Set((await db.by('cards', 'profileId', profileId)).map(c => c.item));
  const items = [];
  C.units.filter(u => u.n < unitN).forEach(u => { u.letters.forEach(c => C.by[c] && items.push({ item: c, kind: 'letter' })); u.words.forEach(w => items.push({ item: w[0], kind: 'word', v: w[3] || w[0], rom: w[1], en: w[2], unit: u.n, idx: u.words.indexOf(w) })); });
  if (unitN >= 6) C.letters.sight_words.forEach((w, i) => items.push({ item: w, kind: 'sight', idx: i }));
  for (const it of items) if (!have.has(it.item)) await db.put('cards', { id: profileId + ':' + it.item, profileId, ...it, box: 1, due: Date.now(), seen: 0 });
}
export async function dueCards(profileId, limit = 12) {
  const now = Date.now(); const all = await db.by('cards', 'profileId', profileId);
  return all.filter(c => c.due <= now).sort((a, b) => a.box - b.box || a.due - b.due).slice(0, limit);
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
export async function getProgress(profileId) { return (await db.get('progress', profileId)) || { id: profileId, units: {}, wpm: [], sessions: 0 }; }
export async function markUnit(profileId, n, score, total) {
  const p = await getProgress(profileId); const passed = score >= Math.ceil(total * 0.8) || p.units[n]?.passed; p.units[n] = { passed, score, total, at: Date.now() }; await db.put('progress', p); return passed;
}
export async function currentUnit(profileId) { const p = await getProgress(profileId); let n = 0; while (p.units[n]?.passed && n < 12) n++; return n; }
export async function startSession(profileId) { const s = { id: uid(), profileId, startedAt: Date.now(), bites: [], correct: 0, total: 0 }; await db.put('sessions', s); return s; }
export async function endSession(s) { s.endedAt = Date.now(); await db.put('sessions', s); const p = await getProgress(s.profileId); p.sessions = (p.sessions || 0) + 1; p.lastSession = Date.now(); await db.put('progress', p); }
export async function recordAttempt(profileId, unit, drill, item, correct, ms) { await db.put('attempts', { id: uid(), profileId, unit, drill, item, correct, ms, ts: Date.now() }); }
export async function stats(profileId) {
  const cards = await db.by('cards', 'profileId', profileId); const p = await getProgress(profileId);
  return { letters: cards.filter(c => c.kind === 'letter').length, lettersMastered: cards.filter(c => c.kind === 'letter' && c.box >= 4).length, words: cards.filter(c => c.kind === 'word').length, wordsMastered: cards.filter(c => c.kind === 'word' && c.box >= 4).length, due: cards.filter(c => c.due <= Date.now()).length, unitsPassed: Object.values(p.units).filter(u => u.passed).length, sessions: p.sessions || 0, wpm: p.wpm || [] };
}
export async function addWpm(profileId, wpm, unit) { const p = await getProgress(profileId); p.wpm = [...(p.wpm || []), { ts: Date.now(), wpm, unit }].slice(-50); await db.put('progress', p); }
