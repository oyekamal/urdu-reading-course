// App shell: first-launch mode choice, profiles, teacher PIN, settings, routing between learner and teacher modes.
import { db, uid, ensureDevice } from './db.js';
import { loadContent, el, toast } from './content.js';
import { renderLearner } from './learner.js';
import { icon, mascot, avatar, AVATARS } from './icons.js';
import { runOnboarding } from './onboarding.js';
import { marko } from './marko.js';
import { initFeel } from './feel.js';
import { askGrownup } from './gate.js';
import { esc, cleanName, NAME_MAX, once } from './safe.js';
import { pickAndRestore } from './restore.js';
import './swreg.js'; // round 11a: service worker registration as a module (no inline script, so the CSP can say script-src 'self')
import './a11y.js'; // round 11b: live region, lang=ur, modal dialogs + focus, tab-bar semantics (observer-based)
import './premium.js'; // round 9c: stickers, light-catching, scene depth, memory (observer-based, no screen edits)

// Every static Marko pose that has an animated state is upgraded in place to the Lottie Marko (marko.js).
// ponytail: one observer instead of touching ~40 mascot() call sites; special poses (trophy, clap, heart…) stay static.
const ANIM = { hello: 'wave', listen: 'listen', think: 'think', cheer: 'cheer', sleep: 'sleep', point: 'point', letter: 'point', read: 'idle', wave2: 'wave' };
function upgradeMarko(scope) {
  (scope.matches?.('img.mascot') ? [scope] : scope.querySelectorAll?.('img.mascot') || []).forEach(img => {
    const st = ANIM[(img.getAttribute('src') || '').match(/mascot_(\w+)\.webp/)?.[1]]; if (!st) return;
    const m = marko(st, img.width || 120, img.className); m.width = img.width || 120; m.dataset.base = st === 'wave' || st === 'cheer' ? 'idle' : st; img.replaceWith(m);
  });
}
// Lottie players keep ticking after their element leaves the DOM (every re-render left looping Markos and fx behind, and a
// long session slowed to a crawl). Destroy the player once a removed node is really gone (not just moved).
function reap(n) {
  if (n.nodeType !== 1) return; const list = [n, ...n.querySelectorAll('.marko, .fx')];
  setTimeout(() => list.forEach(e => { if (e.isConnected) return; if (e._marko) { e._marko.token++; e._marko.anim?.destroy(); e._marko.anim = null; } if (e._anim) { e._anim.destroy(); e._anim = null; } }), 0);
}
new MutationObserver(ms => ms.forEach(m => { m.addedNodes.forEach(n => n.nodeType === 1 && upgradeMarko(n)); m.removedNodes.forEach(reap); })).observe(document.body, { childList: true, subtree: true });

const root = document.getElementById('app');
let settings = {};
const ctxBase = {
  get settings() { return settings; },
  async set(k, v) { settings[k] = v; await db.setting('ui', settings); apply(); },
  apply,
  switchProfile: () => home(),
  exportBackup,
  recover: e => showRecovery(e),
};
initFeel(ctxBase); // tap/answer feel layer (sound, haptics, Marko coach, combo chip): delegated, no per-screen hooks
function apply() { document.body.dataset.style = settings.style || 'naskh'; document.documentElement.style.setProperty('--ur-scale', settings.scale || '1'); document.documentElement.style.setProperty('--ur-spacing', (settings.spacing || '0') + 'em'); document.body.dataset.rom = settings.rom === false ? 'off' : 'on'; document.body.dataset.audioonly = settings.audioOnly ? 'on' : 'off'; }

let booted = false, finishing = false;
async function boot() {
  finishing = false;
  const dog = setTimeout(() => { if (!booted) showRecovery(new Error('The app took too long to open its saved data.')); }, 12000); // never "Loading…" forever
  try {
    await ensureDevice(); await loadContent(); try { navigator.storage?.persist?.(); } catch (e) {} settings = (await db.setting('ui')) || {}; if (typeof settings !== 'object' || Array.isArray(settings)) settings = {}; apply();
    let mode = await db.setting('mode'); if (!['personal', 'family', 'school'].includes(mode)) mode = null; /* a garbage value is treated as not chosen yet */ if (!mode) { if ((await db.all('profiles')).length || location.search.includes('skiponb')) await chooseMode(); else onboard(); booted = true; return; } // ponytail: ?skiponb keeps the old test drivers working
    const active = await db.setting('activeProfile'); if (typeof active === 'string' && active && mode !== 'school') { const p = await db.get('profiles', active); if (p) { await learner(p); booted = true; return; } }
    await home(); booted = true;
  } catch (e) { showRecovery(e); } finally { clearTimeout(dog); }
}
// Calm recovery screen: shown when the saved data cannot be opened or a screen cannot load it. Needs no database to render.
function showRecovery(err) {
  booted = true; console.error('recovery:', err);
  root.innerHTML = ''; const c = el('div', 'card center recovery'); c.setAttribute('role', 'alert');
  c.innerHTML = `<h1>We could not open your saved progress</h1><p class="muted">Nothing has been deleted. This can happen when the phone is very low on space or the app was closed while saving.</p><p class="muted rec-why"></p>`;
  c.querySelector('.rec-why').textContent = String((err && err.message) || err || '').slice(0, 200);
  const again = el('button', 'btn btn-primary btn-wide', 'Try again'); again.onclick = once(() => { booted = false; boot(); });
  const exp = el('button', 'btn btn-wide', 'Export what can be saved'); exp.onclick = once(async () => { if (!await askGrownup({ title: 'Export what can be saved', note: 'A backup file holds every learner on this phone. Grown-ups only, please.' })) return; try { await shareBackup(await db.exportSalvage()); } catch (e) { toast('Export did not work: ' + ((e && e.message) || e)); } });
  const fresh = el('button', 'btn btn-danger btn-wide', 'Start fresh'); fresh.onclick = once(async () => { if (!await askGrownup({ title: 'Start fresh?', note: 'This deletes every learner and all progress on this phone. It cannot be undone. Grown-ups only.' })) return; try { await db.wipe(); } catch (e) { return toast('Could not clear the data: ' + ((e && e.message) || e)); } location.reload(); });
  c.append(again, exp, fresh); root.append(c);
}
// a database or storage error that nobody caught: say so calmly instead of leaving a frozen screen
window.addEventListener('unhandledrejection', e => { const m = String((e.reason && e.reason.message) || e.reason || ''); if (/database|storage|saving|timed out|transaction|quota|idb|aborted|not found/i.test(m)) { try { toast('That did not save. Please try again.'); } catch (x) {} } });

// First launch: the questionnaire onboarding creates the device mode and the first learner.
function onboard() {
  runOnboarding(root, {
    teacherSetup: async () => { await db.setting('onb', null); await db.setting('mode', 'school'); setupTeacher(); },
    restore: () => pickAndRestore({ onDone: afterRestore }),
    finish: async a => {
      if (finishing) return; finishing = true; // one tap, one learner
      try {
      await db.setting('mode', a.who === 'me' ? 'personal' : 'family');
      const track = a.who === 'me' ? (a.speak === 'none' ? 'adult' : 'heritage') : 'child';
      const p = { id: uid(), kind: 'learner', name: cleanName(a.name, 24) || 'Learner', track, grade: '', avatar: a.colour || AVATARS[0], createdAt: Date.now(), goal: a.goal, speaks: a.speak, pains: a.pains || [], minutes: a.minutes || 10, days: a.days || 7 };
      await db.put('profiles', p); if (a.firstWord) await db.put('attempts', { id: uid(), profileId: p.id, unit: 1, drill: 'onboarding', item: 'بابا', correct: true, ms: 0, ts: Date.now() }); // day 1 of the streak is real
      learner(p, undefined, a.reads && a.reads !== 'none');
      } catch (e) { finishing = false; toast('That did not save. Please tap again.'); throw e; }
    },
  });
}

async function chooseMode() {
  const has = (await db.all('profiles')).length; root.innerHTML = ''; const h = el('div', 'hero'); h.innerHTML = `${mascot('hello', 150)}<div class="ur">اردو پڑھنا سیکھیں</div><h1>Urdu Qaida</h1><p class="muted">Works fully offline. Who is this device for?</p>`; root.append(h);
  [['personal', 'user', 'Just me', 'One learner, child or adult', 'var(--accent)'], ['family', 'family', 'My family', 'A parent with one to three children', 'var(--gold-deep)'], ['school', 'school', 'My class', 'A teacher with a roster, lesson scripts and the reading assessment', 'var(--ink)']].forEach(([m, ic, t, d, col]) => {
    const c = el('button', 'card btn', `<div class="row" style="flex-wrap:nowrap"><span class="mode-ic" style="color:${col};background:color-mix(in srgb,${col} 14%,var(--card))">${icon(ic)}</span><div style="text-align:left"><b style="font-size:18px">${t}</b><div class="muted">${d}</div></div></div>`); c.style.width = '100%'; c.style.textAlign = 'left';
    c.onclick = once(async () => { await db.setting('mode', m); if (m === 'school') return setupTeacher(); home(); }); root.append(c);
  });
  // a new phone: restore a backup made on another one (no data here yet, so no gate; with data present the grown-up gate applies)
  const rs = el('button', 'btn btn-wide restore-btn', 'Restore from a backup'); rs.style.marginTop = '12px'; rs.onclick = async () => { if (has && !await askGrownup({ title: 'Restore a backup', note: 'Restoring adds the learners from a backup file. Grown-ups only, please.' })) return; pickAndRestore({ onDone: afterRestore }); }; root.append(rs);
}
// after a restore on a device with no mode yet: pick a sensible mode and open the learners (mode, PIN and other security settings never come from a file)
async function afterRestore() { const ps = (await db.all('profiles')).filter(p => p.kind !== 'teacher'); if (!(await db.setting('mode')) && ps.length) { await db.setting('onb', null); await db.setting('mode', ps.length > 1 ? 'family' : 'personal'); } if (ps.length === 1 && (await db.setting('mode')) === 'personal') return learner(ps[0]); return (await db.setting('mode')) ? home() : chooseMode(); }

async function setupTeacher() {
  root.innerHTML = ''; root.append(el('h1', '', 'Teacher setup')); const c = el('div', 'card'); c.innerHTML = '<p class="muted">Set a PIN. Children tap their name; the PIN protects the roster, assessments and reports.</p>';
  const name = el('input'); name.placeholder = 'Your name'; name.maxLength = NAME_MAX; const pin = el('input'); pin.type = 'password'; pin.inputMode = 'numeric'; pin.placeholder = '4-digit PIN'; pin.maxLength = 6;
  const ok = el('button', 'btn btn-primary btn-wide', 'Save'); ok.onclick = async () => { if (!/^\d{4,6}$/.test(pin.value)) return toast('PIN must be 4 to 6 digits'); await db.setting('teacherPin', pin.value); await db.setting('teacherName', cleanName(name.value) || 'Teacher'); home(); };
  c.append(lab('Name', name), lab('PIN', pin), ok); root.append(c);
}

async function home() {
  const mode = await db.setting('mode'); const profiles = (await db.all('profiles')).filter(p => p.kind !== 'teacher');
  root.innerHTML = ''; const h = el('div', 'row'); h.style.justifyContent = 'space-between'; h.innerHTML = `<div><h1>${mode === 'school' ? 'Class' : 'Who is learning?'}</h1><div class="muted">${mode === 'school' ? 'Tap your name to start' : 'Tap a name, or add one'}</div></div>`; root.append(h);
  const list = el('div', 'list'); profiles.sort((a, b) => a.name.localeCompare(b.name)).forEach(p => { const c = el('button', 'card btn', `${avatar(p)}<div style="flex:1;text-align:left"><b style="font-size:18px;overflow-wrap:anywhere">${esc(p.name)}</b><div class="muted">${esc(p.track)}${p.grade ? ' · grade ' + esc(p.grade) : ''}</div></div>`); c.style.width = '100%'; c.onclick = () => learner(p); list.append(c); });
  root.append(list);
  if (mode !== 'school' || !profiles.length) { const add = el('button', 'btn btn-wide', '+ Add a learner'); add.onclick = () => addProfile(); root.append(add); }
  if (mode === 'school') { const t = el('button', 'btn btn-primary btn-wide', `${icon('lock')} Teacher`); t.onclick = () => teacherGate(); root.append(t); }
  const ch = el('button', 'btn', 'Change device type'); ch.style.marginTop = '20px'; ch.onclick = async () => { if (await askGrownup({ title: 'Change device type', note: 'Profiles and progress are kept. Grown-ups only, please.' })) { await db.setting('mode', null); chooseMode(); } }; root.append(ch);
}

async function addProfile(onDone) {
  root.innerHTML = ''; root.append(el('h1', '', 'New learner')); const c = el('div', 'card'); const name = el('input'); name.placeholder = 'Name'; name.maxLength = NAME_MAX; name.autocomplete = 'off';
  const track = el('select'); [['child', 'Child (5–10)'], ['adult', 'Adult, new to Urdu'], ['heritage', 'Speaks Urdu, can\'t read']].forEach(([v, t]) => track.append(new Option(t, v)));
  const grade = el('select'); ['', '1', '2', '3', '4', '5'].forEach(g => grade.append(new Option(g ? 'Grade ' + g : 'No grade', g)));
  const av = el('div', 'row'); let avatar = AVATARS[0]; AVATARS.forEach((e, i) => { const b = el('button', 'swatch' + (i ? '' : ' on')); b.style.background = e; b.setAttribute('aria-label', 'colour ' + (i + 1)); b.onclick = () => { avatar = e; [...av.children].forEach(x => x.classList.remove('on')); b.classList.add('on'); }; av.append(b); });
  const ok = el('button', 'btn btn-primary btn-wide', 'Start'); ok.onclick = once(async () => { const nm = cleanName(name.value); if (!nm) return toast('Type a name'); const p = { id: uid(), kind: 'learner', name: nm, track: ['child', 'adult', 'heritage'].includes(track.value) ? track.value : 'child', grade: grade.value, avatar, createdAt: Date.now() }; try { await db.put('profiles', p); } catch (e) { return toast('Could not save. Please try again.'); } onDone ? onDone(p) : learner(p); }, 700);
  const back = el('button', 'btn', 'Back'); back.onclick = home; c.append(lab('Name', name), lab('Track', track), lab('Grade', grade), lab('Colour', av), ok, back); root.append(c);
}

async function learner(p, backTo, autoPlacement) { await db.setting('activeProfile', p.id); document.body.dataset.track = p.track; return renderLearner(root, { ...ctxBase, profile: p, mode: await db.setting('mode'), switchProfile: backTo || home, autoPlacement }); }

async function teacherGate() {
  const pin = await db.setting('teacherPin'); if (!pin) return setupTeacher();
  root.innerHTML = ''; const c = el('div', 'card center'); c.innerHTML = '<h2>Teacher PIN</h2>'; const inp = el('input'); inp.type = 'password'; inp.inputMode = 'numeric'; inp.style.fontSize = '24px'; inp.style.textAlign = 'center';
  const ok = el('button', 'btn btn-primary btn-wide', 'Unlock'); ok.onclick = () => inp.value === pin ? teacher() : toast('Wrong PIN'); inp.onkeydown = e => { if (e.key === 'Enter') ok.click(); }; const back = el('button', 'btn', 'Back'); back.onclick = home; c.append(inp, ok, back); root.append(c); inp.focus();
}
async function teacher() {
  const { renderTeacher } = await import('./teacher.js');
  await db.setting('activeProfile', null);
  const { C, play } = await import('./content.js');
  renderTeacher(root, { db, C, play, settings, recover: e => showRecovery(e), openLearner: async id => learner(await db.get('profiles', id), teacher), lock: home, exportBackup, addProfile: () => addProfile(() => teacher()) });
}

async function exportBackup() {
  if (!await askGrownup({ title: 'Export a backup', note: 'A backup file holds every learner on this phone. Grown-ups only, please.' })) return;
  await shareBackup(await db.exportAll());
}
async function shareBackup(data) {
  const text = JSON.stringify(data); const name = `urdu-reader-backup-${new Date().toISOString().slice(0, 10)}.json`;
  try { const { Filesystem, Directory, Encoding } = await import('@capacitor/filesystem'); const { Share } = await import('@capacitor/share'); const r = await Filesystem.writeFile({ path: name, data: text, directory: Directory.Cache, encoding: Encoding.UTF8 }); await Share.share({ title: name, url: r.uri }); return; } catch (e) { /* not on device or plugin missing */ }
  try { const f = new File([text], name, { type: 'application/json' }); if (navigator.canShare && navigator.canShare({ files: [f] })) { await navigator.share({ files: [f], title: name }); return; } } catch (e) {}
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' })); a.download = name; a.click(); toast('Backup downloaded');
}
const lab = (t, node) => { const l = el('label', '', t); l.append(node); return l; };
// a screen that cannot load its data shows the recovery screen instead of freezing
const guard = fn => async (...a) => { try { return await fn(...a); } catch (e) { showRecovery(e); } };
home = guard(home); learner = guard(learner); teacherGate = guard(teacherGate);
boot();
