// Local database: IndexedDB, one store per record type. No server. Every record carries an id, profileId
// (where relevant) and updatedAt so exports from several phones can be merged by id.
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
function open() {
  if (dbp) return dbp;
  dbp = new Promise((res, rej) => {
    const r = indexedDB.open(DB_NAME, VERSION);
    r.onupgradeneeded = () => {
      const d = r.result;
      for (const [name, def] of Object.entries(STORES)) {
        if (!d.objectStoreNames.contains(name)) {
          const s = d.createObjectStore(name, { keyPath: def.keyPath });
          (def.indexes || []).forEach(ix => s.createIndex(ix, ix));
        }
      }
    };
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  });
  return dbp;
}
function tx(store, mode, fn) {
  return open().then(d => new Promise((res, rej) => {
    const t = d.transaction(store, mode); const s = t.objectStore(store); const out = fn(s);
    t.oncomplete = () => res(out instanceof IDBRequest ? out.result : out); t.onerror = () => rej(t.error);
  }));
}
export const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
export const db = {
  get: (store, key) => tx(store, 'readonly', s => s.get(key)),
  put: (store, val) => tx(store, 'readwrite', s => s.put({ ...val, updatedAt: Date.now() })),
  del: (store, key) => tx(store, 'readwrite', s => s.delete(key)),
  all: (store) => tx(store, 'readonly', s => s.getAll()),
  by: (store, index, value) => tx(store, 'readonly', s => s.index(index).getAll(value)),
  setting: async (key, val) => val === undefined ? (await db.get('settings', key))?.value : db.put('settings', { key, value: val }),
  async exportAll() {
    const out = { exportedAt: new Date().toISOString(), device: await db.setting('deviceId') };
    for (const s of Object.keys(STORES)) out[s] = await db.all(s);
    return out;
  },
  async importAll(data) {
    let n = 0;
    for (const s of Object.keys(STORES)) for (const rec of (data[s] || [])) {
      const cur = await db.get(s, rec[STORES[s].keyPath]);
      if (!cur || (rec.updatedAt || 0) > (cur.updatedAt || 0)) { await tx(s, 'readwrite', st => st.put(rec)); n++; }
    }
    return n;
  },
};
export async function ensureDevice() {
  if (!(await db.setting('deviceId'))) await db.setting('deviceId', uid());
}
