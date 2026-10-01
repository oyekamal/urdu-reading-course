// round 9c: emotional memory. Marko remembers what the learner actually did and says one kind, specific thing on the home screen.
// Built from real IndexedDB data only (cards, attempts, progress). Rules: warm and specific, never guilt, never mention a missed day
// or a broken streak. A long gap is simply "last time"; the line is chosen deterministically (day number), so it rotates daily
// without randomness. Wire-up (lead): `import { markoLine, loadMemory } from './memory.js'` or use window.__memory.line(profile).
import { db } from './db.js';
import { C } from './content.js';

const DAY = 86400000;
const cap = s => s.length > 70 ? s.slice(0, 67) + '...' : s;

// stats: { hour, lastLetter: {ch,name,nameUr}|null, nextLetter: {...}|null, daysSinceLast: number|null, words, daysPractised, mastered, pearls }
export function markoLine(profile, stats = {}) {
  const name = profile?.name || 'friend', h = stats.hour ?? new Date().getHours(), s = stats;
  const part = h < 5 ? 'night' : h < 12 ? 'morning' : h < 17 ? 'afternoon' : h < 21 ? 'evening' : 'night';
  const pool = [];
  if (s.lastLetter && s.nextLetter) pool.push(`${s.daysSinceLast === 1 ? 'Yesterday' : s.daysSinceLast === 0 ? 'Today' : 'Last time'} we met ${s.lastLetter.ch}, ready for ${s.nextLetter.nameUr}?`);
  if (s.lastLetter && !s.nextLetter) pool.push(`You know ${s.lastLetter.ch} so well, ${name}!`);
  if (s.words > 0) pool.push(`You have read ${s.words} ${s.words === 1 ? 'word' : 'words'}!`);
  if (s.mastered > 0) pool.push(`${s.mastered} ${s.mastered === 1 ? 'letter is' : 'letters are'} yours now. Well done!`);
  if (s.daysPractised > 1) pool.push(`We have practised ${s.daysPractised} days together. I like that!`);
  if (s.pearls > 0) pool.push(`${s.pearls} ${s.pearls === 1 ? 'pearl' : 'pearls'} on your thread, ${name}!`);
  pool.push(part === 'morning' ? `Good morning, ${name}! A fresh day for letters.` : part === 'afternoon' ? `Hello ${name}! A little reading time?` : part === 'evening' ? `Evening, ${name}. A calm lesson before supper?` : `Hi ${name}! Small steps count.`);
  if (!s.lastLetter && !s.words) return cap(`Hi ${name}! Let's find your first letter.`);
  const day = Math.floor(((stats.now ?? Date.now()) - new Date().getTimezoneOffset() * 60000) / DAY);
  return cap(pool[(day + name.length) % pool.length]);
}

export async function loadMemory(profile) {
  const pid = profile.id; const [cards, attempts, prog] = await Promise.all([db.by('cards', 'profileId', pid), db.by('attempts', 'profileId', pid), db.get('progress', pid)]);
  const order = C.units ? C.units.flatMap(u => u.letters).filter(c => C.by[c]) : [];
  const met = cards.filter(c => c.kind === 'letter' && (c.seen > 0 || c.box >= 2)).sort((a, b) => (b.last || 0) - (a.last || 0));
  const info = ch => ch && C.by[ch] ? { ch, name: C.by[ch].name, nameUr: C.by[ch].name_ur } : null;
  const lastLetter = info(met[0]?.item); const nxt = lastLetter ? order[order.indexOf(lastLetter.ch) + 1] : order[0];
  const last = Math.max(0, ...attempts.map(a => a.ts), prog?.lastSession || 0);
  const days = new Set(attempts.map(a => new Date(a.ts).toDateString()));
  const startOf = t => { const d = new Date(t); d.setHours(0, 0, 0, 0); return d.getTime(); };
  return { hour: new Date().getHours(), lastLetter, nextLetter: info(nxt), daysSinceLast: last ? Math.round((startOf(Date.now()) - startOf(last)) / DAY) : null, words: cards.filter(c => c.kind === 'word' && c.seen > 0).length, daysPractised: days.size, mastered: cards.filter(c => c.kind === 'letter' && c.box >= 4).length, pearls: Object.values(prog?.units || {}).reduce((n, u) => n + Object.keys(u.lessons || {}).length, 0) };
}

export async function lineFor(profile) { return markoLine(profile, await loadMemory(profile)); }
window.__memory = { markoLine, loadMemory, line: lineFor };
