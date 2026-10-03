// Backup file validation (pure, no imports from the app). A backup is untrusted input: it may be corrupt, huge, hand-edited or hostile.
// validateBackup(data) returns { clean, notes } or throws BackupError. Only whitelisted stores and fields survive; security
// settings (teacherPin, mode, activeProfile, deviceId, onb) can never come from a file.
import { cleanName, cleanText } from './safe.js';
export const BACKUP_FORMAT = 'urdu-qaida-backup', BACKUP_VERSION = 1;
export const MAX_BACKUP_BYTES = 64 * 1024 * 1024;
export class BackupError extends Error { constructor(m) { super(m); this.name = 'BackupError'; } }
const LIMITS = { profiles: 200, attempts: 250000, cards: 250000, sessions: 50000, progress: 200, assessments: 5000, settings: 400 };
const NOW = () => Date.now();
const SAFE_KEY = /^[A-Za-z0-9_:.-]{1,80}$/, BAD_KEY = /^(__proto__|constructor|prototype)$/;
const fail = m => { throw new BackupError(m); };
const isObj = v => v && typeof v === 'object' && !Array.isArray(v);
// ---- field checkers: each returns the cleaned value or undefined (= drop the field). `req` fields that come back undefined reject the record.
const str = (max, { clean = false } = {}) => v => typeof v === 'string' ? (clean ? cleanText(v, max) : (v.length <= max ? v.replace(/[\u0000-\u001f\u007f<>]/g, '') : undefined)) : undefined;
const name = v => typeof v === 'string' ? (cleanName(v) || 'Learner') : undefined;
const id = v => typeof v === 'string' && /^[A-Za-z0-9_:.\-؀-ۿ]{1,120}$/.test(v) ? v : undefined;
const num = (lo = -1e15, hi = 1e15) => v => typeof v === 'number' && Number.isFinite(v) && v >= lo && v <= hi ? v : undefined;
const int = (lo, hi) => v => Number.isInteger(v) && v >= lo && v <= hi ? v : undefined;
const bool = v => typeof v === 'boolean' ? v : undefined;
const oneOf = (...a) => v => a.includes(v) ? v : undefined;
const colour = v => typeof v === 'string' && /^#[0-9a-fA-F]{3,8}$/.test(v) ? v : undefined;
const ts = num(0, 4.1e12);
const strArr = (n, max) => v => Array.isArray(v) ? v.slice(0, n).filter(x => typeof x === 'string').map(x => cleanText(x, max)) : undefined;
const dict = (valueFn, maxKeys = 200, keyRx = SAFE_KEY) => v => { if (!isObj(v)) return undefined; const out = {}; let k = 0; for (const key of Object.keys(v)) { if (BAD_KEY.test(key) || !keyRx.test(key)) continue; if (++k > maxKeys) break; const x = valueFn(v[key]); if (x !== undefined) out[key] = x; } return out; };
const shape = fields => v => { if (!isObj(v)) return undefined; const out = {}; for (const [k, fn] of Object.entries(fields)) if (k in v) { const x = fn(v[k]); if (x !== undefined) out[k] = x; } return out; };
const unitRec = shape({ passed: bool, score: num(0, 1000), total: num(0, 1000), at: ts, steps: dict(bool, 40), lessons: dict(v => isObj(v) ? shape({ at: ts, score: num(0, 1000) })(v) : (v === true ? true : (typeof v === 'number' ? num()(v) : undefined)), 80) });
const wpmRec = v => isObj(v) ? shape({ ts, wpm: num(0, 1000), unit: int(0, 12) })(v) : undefined;
const orf = shape({ cwpm: num(0, 1000), acc: num(0, 100), seconds: num(0, 36000), errors: num(0, 1000), attempted: num(0, 5000), capped: bool });
// ---- store schemas: [required fields..., field checkers]
const SCHEMA = {
  profiles: { key: 'id', req: ['id', 'name'], f: { id, name, kind: v => v === 'learner' ? v : undefined, track: oneOf('child', 'adult', 'heritage'), grade: v => typeof v === 'number' ? int(0, 12)(v) : str(3)(v), createdAt: ts, unit: int(0, 12), avatar: colour, goal: str(80, { clean: true }), speaks: str(24), pains: strArr(8, 40), minutes: num(0, 600), days: num(0, 7), updatedAt: ts } },
  attempts: { key: 'id', req: ['id', 'profileId', 'ts'], f: { id, profileId: id, unit: int(0, 12), drill: str(32), item: str(80), correct: bool, ms: num(0, 3.6e6), ts, updatedAt: ts } },
  cards: { key: 'id', req: ['id', 'profileId', 'item'], f: { id, profileId: id, item: str(80), kind: oneOf('letter', 'word', 'sight'), v: str(80), rom: str(80), en: str(120), unit: int(0, 12), idx: int(0, 500), box: int(0, 5), due: ts, seen: int(0, 1e6), last: ts, lastOk: bool, lastMiss: ts, updatedAt: ts } },
  sessions: { key: 'id', req: ['id', 'profileId'], f: { id, profileId: id, startedAt: ts, endedAt: ts, bites: v => Array.isArray(v) ? v.length : num(0, 1000)(v), reviewDone: num(0, 1000), correct: num(0, 1000), total: num(0, 1000), updatedAt: ts } },
  progress: { key: 'id', req: ['id'], f: { id, units: dict(unitRec, 40, /^\d{1,2}$/), wpm: v => Array.isArray(v) ? v.slice(-50).map(wpmRec).filter(Boolean) : undefined, sessions: int(0, 1e6), lastSession: ts, updatedAt: ts } },
  assessments: { key: 'id', req: ['id', 'profileId', 'ts'], f: { id, profileId: id, ts, letters: num(0, 1000), nonwords: num(0, 1000), words: num(0, 1000), orf, orfDone: bool, comp: num(0, 10), compDone: bool, band: str(60), level: str(120), by: name, updatedAt: ts } },
};
const UI_KEYS = { style: oneOf('naskh', 'nastaliq'), marks: bool, scale: oneOf('1', '1.25', '1.5', 1, 1.25, 1.5), rom: bool, audioOnly: bool, spacing: oneOf('0', '0.05', '0.12', 0, 0.05, 0.12), sounds: bool, haptics: bool };
// settings: only display preferences and the sticker-seen lists are importable. Everything else (mode, teacherPin, activeProfile, deviceId, onb, teacherName) is device security state.
function cleanSetting(rec) {
  if (!isObj(rec) || typeof rec.key !== 'string') return null;
  if (rec.key === 'ui') { const v = shape(UI_KEYS)(rec.value); return v ? { key: 'ui', value: v, updatedAt: ts(rec.updatedAt) } : null; }
  if (/^stickersSeen:[A-Za-z0-9_-]{1,60}$/.test(rec.key) && Array.isArray(rec.value)) return { key: rec.key, value: rec.value.slice(0, 80).filter(x => typeof x === 'string' && x.length <= 12).map(x => x), updatedAt: ts(rec.updatedAt) };
  return null;
}
export function validateBackup(data) {
  if (!isObj(data)) fail('This file is not a Urdu Qaida backup (it does not hold a data object).');
  if (data.format !== undefined && data.format !== BACKUP_FORMAT) fail('This file is not a Urdu Qaida backup (wrong format marker).');
  if (data.version !== undefined && (!Number.isInteger(data.version) || data.version < 1 || data.version > BACKUP_VERSION)) fail('This backup was made by a newer version of the app. Update the app and try again.');
  const known = Object.keys(SCHEMA).concat('settings');
  if (data.format === undefined && !(typeof data.exportedAt === 'string' && known.some(k => Array.isArray(data[k])))) fail('This file is not a Urdu Qaida backup.');
  const clean = {}, notes = { dropped: 0, cleaned: 0 }; let total = 0;
  for (const s of known) {
    const arr = data[s]; if (arr === undefined) { clean[s] = []; continue; }
    if (!Array.isArray(arr)) fail(`The backup is damaged: "${s}" should be a list.`);
    if (arr.length > LIMITS[s]) fail(`The backup is too large: ${arr.length} ${s} (the most this app accepts is ${LIMITS[s]}).`);
    total += arr.length; if (total > 700000) fail('The backup is too large.');
    const out = clean[s] = [], seen = new Set();
    arr.forEach((rec, i) => {
      if (s === 'settings') { const c = cleanSetting(rec); if (c) { if (c.updatedAt === undefined || c.updatedAt > NOW()) c.updatedAt = NOW(); out.push(c); } else notes.dropped++; return; }
      if (!isObj(rec)) fail(`The backup is damaged: ${s} entry ${i + 1} is not a record.`);
      const sc = SCHEMA[s], r = {};
      for (const [k, fn] of Object.entries(sc.f)) if (k in rec) { const x = fn(rec[k]); if (x !== undefined) r[k] = x; else if (sc.req.includes(k)) fail(`The backup is damaged: ${s} entry ${i + 1} has an invalid "${k}".`); }
      for (const k of sc.req) if (r[k] === undefined) fail(`The backup is damaged: ${s} entry ${i + 1} is missing "${k}".`);
      if (s === 'profiles' && typeof rec.name === 'string' && rec.name !== r.name) notes.cleaned++;
      if (s === 'profiles') r.kind = 'learner'; // a file can only add learners, never a teacher record
      if (r.updatedAt === undefined) r.updatedAt = 0; else if (r.updatedAt > NOW()) r.updatedAt = NOW(); // a forged future stamp never counts as newer than now
      if (seen.has(r[sc.key])) return; seen.add(r[sc.key]); out.push(r);
    });
  }
  return { clean, notes };
}
