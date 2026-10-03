// Local database: IndexedDB, one store per record type. No server. Every record carries an id, profileId
// (where relevant) and updatedAt so exports from several phones can be merged by id.
import { validateBackup, BACKUP_FORMAT, BACKUP_VERSION } from './backup.js';
import { cleanName } from './safe.js';
const DB_NAME = 'urdu-reader', VERSION = 1;
const STORES = {
  settings: { keyPath: 'key' },                 // device-level: mode, teacherPin, activeProfile, style, marks
  profiles: { keyPath: 'id' },                  // {id, name, track: child|adult|heritage, grade, createdAt, unit, avatar}
  attempts: { keyPath: 'id', indexes: ['profileId', 'ts'] },      // every drill answer {id, profileId, unit, drill, item, correct, ms, ts}
  cards: { keyPath: 'id', indexes: ['profileId', 'due'] },        // Leitner {id: profileId+':'+item, profileId, item, kind, box, due, seen}
  sessions: { keyPath: 'id', indexes: ['profileId'] },            // {id, profileId, startedAt, endedAt, bites, reviewDone, correct, total}
  progress: { keyPath: 'id' },                  // {id: profileId, units: {n:{passed, score, at}}, wpm: [{ts, wpm, unit}]}
  assessments: { keyPath: 'id', indexes: ['profileId', 'ts'] },   // EGRA {id, profileId, ts, letters, nonwords, words, orf:{cwpm, acc}, comp, band, by}
};
let dbp;
export const DB_TIMEOUT = 8000; // no promise in this file may wait longer than this (a stuck open, a wedged transaction)
const withTimeout = (p, ms, what) => new Promise((res, rej) => { const t = setTimeout(() => rej(new Error(what + ' timed out')), ms); p.then(v => { clearTimeout(t); res(v); }, e => { clearTimeout(t); rej(e); }); });
function createMissing(d) {
  for (const [name, def] of Object.entries(STORES)) {
    if (!d.objectStoreNames.contains(name)) {
      const st = d.createObjectStore(name, { keyPath: def.keyPath });
      (def.indexes || []).forEach(ix => st.createIndex(ix, ix));
    }
  }
}
// indexes left out of an old or damaged database are added too
function createMissingIndexes(t) { for (const [name, def] of Object.entries(STORES)) { if (!t.objectStoreNames.contains(name)) continue; const st = t.objectStore(name); (def.indexes || []).forEach(ix => { if (!st.indexNames.contains(ix)) st.createIndex(ix, ix); }); } }
function openAt(version) {
  return new Promise((res, rej) => {
    let r; try { r = version ? indexedDB.open(DB_NAME, version) : indexedDB.open(DB_NAME); } catch (e) { return rej(e); }
    r.onupgradeneeded = () => { createMissing(r.result); if (r.transaction) createMissingIndexes(r.transaction); };
    r.onblocked = () => rej(new Error('The database is open in another tab. Close the other tab and try again.'));
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error || new Error('Could not open the database'));
  });
}
export function open() {
  if (dbp) return dbp;
  dbp = (async () => {
    if (typeof indexedDB === 'undefined' || !indexedDB) throw new Error('This browser does not allow the app to save data (storage unavailable).');
    let d; try { d = await withTimeout(openAt(VERSION), DB_TIMEOUT, 'Opening the database'); } catch (e) { if (e && e.name === 'VersionError') d = await withTimeout(openAt(), DB_TIMEOUT, 'Opening the database'); else throw e; } // a newer/odd version left by another build: open whatever is there
    // a database left half-made (a store missing) is repaired by a version bump that only adds what is missing
    const missingIx = () => Object.entries(STORES).some(([n, def]) => d.objectStoreNames.contains(n) && (def.indexes || []).some(ix => !d.transaction(n).objectStore(n).indexNames.contains(ix)));
    if (Object.keys(STORES).some(n => !d.objectStoreNames.contains(n)) || missingIx()) { const v = d.version + 1; d.close(); d = await withTimeout(openAt(v), DB_TIMEOUT, 'Repairing the database'); }
    d.onversionchange = () => { try { d.close(); } catch (e) { /* ignore */ } dbp = null; };
    d.onclose = () => { dbp = null; };
    return d;
  })();
  dbp.catch(() => { dbp = null; }); // a failed open can be retried ("Try again")
  return dbp;
}
const isRec = r => r && typeof r === 'object' && !Array.isArray(r);
// Anything read back from the database is untrusted (old versions, hand-edited, imported): records are made safe on the way out.
// Markup characters are stripped from every string of every learner-data record (defence in depth: screens also escape), profiles get a
// safe name/track/colour, and an assessment always has the shape the teacher screens expect.
const TRACKS = ['child', 'adult', 'heritage'];
const STRIP = /[<>"`]/g;
const scrub = (v, d = 0) => typeof v === 'string' ? v.replace(STRIP, '') : d < 5 && Array.isArray(v) ? v.map(x => scrub(x, d + 1)) : d < 5 && isRec(v) ? Object.fromEntries(Object.entries(v).map(([k, x]) => [k.replace(STRIP, ''), scrub(x, d + 1)])) : v;
const fix = (store, r) => {
  if (!isRec(r) || store === 'settings') return r;
  const o = scrub(r);
  if (store === 'profiles') return { ...o, name: cleanName(o.name) || 'Learner', track: TRACKS.includes(o.track) ? o.track : 'child', grade: typeof o.grade === 'number' && Number.isFinite(o.grade) ? o.grade : /^[\w .-]{0,6}$/.test(String(o.grade ?? '')) ? String(o.grade ?? '') : '', avatar: /^#[0-9a-fA-F]{3,8}$/.test(o.avatar || '') ? o.avatar : undefined };
  if (store === 'assessments') return { ...o, orf: isRec(o.orf) ? o.orf : { cwpm: 0 }, band: typeof o.band === 'string' ? o.band : '' };
  return o;
};
function tx(store, mode, fn) {
  return withTimeout(open().then(d => new Promise((res, rej) => {
    let t, out;
    try { t = d.transaction(store, mode); out = fn(t.objectStore(store)); } catch (e) { return rej(e); }
    t.oncomplete = () => res(out instanceof IDBRequest ? out.result : out);
    t.onerror = () => rej(t.error || new Error('Database write failed'));
    t.onabort = () => rej(t.error || new Error('Database write was cancelled (storage may be full)'));
  })), DB_TIMEOUT, 'Saving');
}
export const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
export const db = {
  get: (store, key) => tx(store, 'readonly', s => s.get(key)).then(r => fix(store, r)),
  put: (store, val) => tx(store, 'readwrite', s => s.put({ ...val, updatedAt: Date.now() })),
  del: (store, key) => tx(store, 'readwrite', s => s.delete(key)),
  all: (store) => tx(store, 'readonly', s => s.getAll()).then(a => (a || []).filter(isRec).map(r => fix(store, r))),
  by: (store, index, value) => tx(store, 'readonly', s => s.index(index).getAll(value)).then(a => (a || []).filter(isRec).map(r => fix(store, r))),
  setting: async (key, val) => val === undefined ? (await db.get('settings', key))?.value : db.put('settings', { key, value: val }),
  async exportAll() {
    const out = { format: BACKUP_FORMAT, version: BACKUP_VERSION, exportedAt: new Date().toISOString(), device: await db.setting('deviceId') };
    for (const s of Object.keys(STORES)) out[s] = await db.all(s);
    out.settings = out.settings.filter(r => r.key === 'ui' || /^stickersSeen:/.test(r.key)); // the teacher PIN, mode and device id never leave the phone in a backup
    return out;
  },
  // best effort for the recovery screen: every store on its own, so one broken store does not hide the rest
  async exportSalvage() {
    const out = { format: BACKUP_FORMAT, version: BACKUP_VERSION, exportedAt: new Date().toISOString(), salvaged: true };
    for (const s of Object.keys(STORES)) { try { out[s] = await db.all(s); } catch (e) { out[s] = []; } }
    out.settings = out.settings.filter(r => r.key === 'ui' || /^stickersSeen:/.test(r.key));
    return out;
  },
  // What an import would do, without writing: learner names, how many records are new and how many would replace a record already on this phone.
  async previewImport(data) {
    const { clean } = validateBackup(data); let add = 0, replace = 0;
    for (const s of Object.keys(clean)) { if (!clean[s].length) continue; const kp = STORES[s].keyPath; const have = new Map((await db.all(s)).map(r => [r[kp], r.updatedAt || 0])); for (const rec of clean[s]) { if (!have.has(rec[kp])) add++; else if ((rec.updatedAt || 0) > have.get(rec[kp])) replace++; } }
    return { learners: clean.profiles.map(p => p.name), add, replace };
  },
  // Validates the whole file first (backup.js), then merges it in ONE transaction across every store: all or nothing.
  async importAll(data) {
    const { clean } = validateBackup(data); // throws BackupError with a plain-language message
    const stores = Object.keys(clean).filter(k => clean[k].length); if (!stores.length) return 0;
    const d = await open();
    return new Promise((res, rej) => {
      let n = 0, t; try { t = d.transaction(stores, 'readwrite'); } catch (e) { return rej(e); }
      const timer = setTimeout(() => { try { t.abort(); } catch (e) { /* ignore */ } rej(new Error('Importing took too long, so it was cancelled and nothing was changed')); }, 120000); // abort for real: a timeout never leaves a half-applied import
      for (const s of stores) {
        const os = t.objectStore(s), kp = STORES[s].keyPath;
        for (const rec of clean[s]) { const g = os.get(rec[kp]); g.onsuccess = () => { const cur = g.result; if (!cur || (rec.updatedAt || 0) > (cur.updatedAt || 0)) { n++; os.put(rec); } }; }
      }
      t.oncomplete = () => { clearTimeout(timer); res(n); }; t.onerror = () => { clearTimeout(timer); rej(t.error || new Error('Import failed')); }; t.onabort = () => { clearTimeout(timer); rej(t.error || new Error('Import was cancelled; nothing was changed')); };
    });
  },
  // Delete one learner and everything that belongs to them (teacher mode Delete): no orphaned attempts, cards, progress or sticker list
  async deleteProfile(id) {
    for (const s of ['cards', 'attempts', 'sessions', 'assessments']) for (const r of await db.by(s, 'profileId', id)) await db.del(s, r.id);
    await db.del('progress', id); await db.del('settings', 'stickersSeen:' + id); await db.del('profiles', id);
  },
  // "Start fresh": delete the whole database (behind the grown-up gate in the recovery screen)
  async wipe() {
    try { const d = await dbp; d && d.close(); } catch (e) { /* ignore */ } dbp = null;
    await withTimeout(new Promise((res, rej) => { const r = indexedDB.deleteDatabase(DB_NAME); r.onsuccess = () => res(); r.onerror = () => rej(r.error); r.onblocked = () => res(); }), DB_TIMEOUT, 'Clearing the database');
  },
};
export async function ensureDevice() {
  if (!(await db.setting('deviceId'))) await db.setting('deviceId', uid());
}
