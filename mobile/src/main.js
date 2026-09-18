// App shell: first-launch mode choice, profiles, teacher PIN, settings, routing between learner and teacher modes.
import { db, uid, ensureDevice } from './db.js';
import { loadContent, el, toast } from './content.js';
import { renderLearner } from './learner.js';

const root = document.getElementById('app');
let settings = {};
const ctxBase = {
  get settings() { return settings; },
  async set(k, v) { settings[k] = v; await db.setting('ui', settings); apply(); },
  apply,
  switchProfile: () => home(),
  exportBackup,
};
function apply() { document.body.dataset.style = settings.style || 'naskh'; document.documentElement.style.setProperty('--ur-scale', settings.scale || '1'); }

async function boot() {
  await ensureDevice(); await loadContent(); settings = (await db.setting('ui')) || {}; apply();
  const mode = await db.setting('mode'); if (!mode) return chooseMode();
  const active = await db.setting('activeProfile'); if (active && mode !== 'school') { const p = await db.get('profiles', active); if (p) return learner(p); }
  home();
}

function chooseMode() {
  root.innerHTML = ''; const h = el('div', 'hero'); h.innerHTML = `<div class="ur" style="font-size:44px">اردو پڑھنا سیکھیں</div><h1>Urdu Reader</h1><p class="muted">Works fully offline. Who is this device for?</p>`; root.append(h);
  [['personal', '🙋', 'Just me', 'One learner, child or adult'], ['family', '👨‍👩‍👧', 'My family', 'A parent with one to three children'], ['school', '🏫', 'My class', 'A teacher with a roster, lesson scripts and the reading assessment']].forEach(([m, ic, t, d]) => {
    const c = el('button', 'card btn', `<div class="row"><span class="emoji">${ic}</span><div style="text-align:left"><b style="font-size:18px">${t}</b><div class="muted">${d}</div></div></div>`); c.style.width = '100%'; c.style.textAlign = 'left';
    c.onclick = async () => { await db.setting('mode', m); if (m === 'school') return setupTeacher(); home(); }; root.append(c);
  });
}

async function setupTeacher() {
  root.innerHTML = ''; root.append(el('h1', '', 'Teacher setup')); const c = el('div', 'card'); c.innerHTML = '<p class="muted">Set a PIN. Children tap their name; the PIN protects the roster, assessments and reports.</p>';
  const name = el('input'); name.placeholder = 'Your name'; const pin = el('input'); pin.type = 'password'; pin.inputMode = 'numeric'; pin.placeholder = '4-digit PIN'; pin.maxLength = 6;
  const ok = el('button', 'btn btn-primary btn-wide', 'Save'); ok.onclick = async () => { if (!/^\d{4,6}$/.test(pin.value)) return toast('PIN must be 4 to 6 digits'); await db.setting('teacherPin', pin.value); await db.setting('teacherName', name.value || 'Teacher'); home(); };
  c.append(lab('Name', name), lab('PIN', pin), ok); root.append(c);
}

async function home() {
  const mode = await db.setting('mode'); const profiles = (await db.all('profiles')).filter(p => p.kind !== 'teacher');
  root.innerHTML = ''; const h = el('div', 'row'); h.style.justifyContent = 'space-between'; h.innerHTML = `<div><h1>${mode === 'school' ? 'Class' : 'Who is learning?'}</h1><div class="muted">${mode === 'school' ? 'Tap your name to start' : 'Tap a name, or add one'}</div></div>`; root.append(h);
  const list = el('div', 'list'); profiles.sort((a, b) => a.name.localeCompare(b.name)).forEach(p => { const c = el('button', 'card btn', `<span class="emoji">${p.avatar || '🙂'}</span><div style="flex:1;text-align:left"><b style="font-size:18px">${p.name}</b><div class="muted">${p.track}${p.grade ? ' · grade ' + p.grade : ''}</div></div>`); c.style.width = '100%'; c.onclick = () => learner(p); list.append(c); });
  root.append(list);
  if (mode !== 'school' || !profiles.length) { const add = el('button', 'btn btn-wide', '+ Add a learner'); add.onclick = () => addProfile(); root.append(add); }
  if (mode === 'school') { const t = el('button', 'btn btn-primary btn-wide', '🔒 Teacher'); t.onclick = () => teacherGate(); root.append(t); }
  const ch = el('button', 'btn', 'Change device type'); ch.style.marginTop = '20px'; ch.onclick = async () => { if (confirm('Change device type? Profiles and progress are kept.')) { await db.setting('mode', null); chooseMode(); } }; root.append(ch);
}

async function addProfile(onDone) {
  root.innerHTML = ''; root.append(el('h1', '', 'New learner')); const c = el('div', 'card'); const name = el('input'); name.placeholder = 'Name';
  const track = el('select'); [['child', 'Child (5–10)'], ['adult', 'Adult, new to Urdu'], ['heritage', 'Speaks Urdu, can\'t read']].forEach(([v, t]) => track.append(new Option(t, v)));
  const grade = el('select'); ['', '1', '2', '3', '4', '5'].forEach(g => grade.append(new Option(g ? 'Grade ' + g : 'No grade', g)));
  const av = el('div', 'row'); let avatar = '🙂'; ['🙂', '🦁', '🐯', '🐼', '🦋', '🌸', '⭐', '🚀', '🎈', '📚'].forEach(e => { const b = el('button', 'btn', e); b.onclick = () => { avatar = e; [...av.children].forEach(x => x.classList.remove('btn-primary')); b.classList.add('btn-primary'); }; av.append(b); });
  const ok = el('button', 'btn btn-primary btn-wide', 'Start'); ok.onclick = async () => { if (!name.value.trim()) return toast('Type a name'); const p = { id: uid(), kind: 'learner', name: name.value.trim(), track: track.value, grade: grade.value, avatar, createdAt: Date.now() }; await db.put('profiles', p); onDone ? onDone(p) : learner(p); };
  const back = el('button', 'btn', 'Back'); back.onclick = home; c.append(lab('Name', name), lab('Track', track), lab('Grade', grade), lab('Picture', av), ok, back); root.append(c);
}

async function learner(p) { await db.setting('activeProfile', p.id); document.body.dataset.track = p.track; renderLearner(root, { ...ctxBase, profile: p }); }

async function teacherGate() {
  const pin = await db.setting('teacherPin'); if (!pin) return setupTeacher();
  root.innerHTML = ''; const c = el('div', 'card center'); c.innerHTML = '<h2>Teacher PIN</h2>'; const inp = el('input'); inp.type = 'password'; inp.inputMode = 'numeric'; inp.style.fontSize = '24px'; inp.style.textAlign = 'center';
  const ok = el('button', 'btn btn-primary btn-wide', 'Unlock'); ok.onclick = () => inp.value === pin ? teacher() : toast('Wrong PIN'); inp.onkeydown = e => e.key === 'Enter' && ok.click(); const back = el('button', 'btn', 'Back'); back.onclick = home; c.append(inp, ok, back); root.append(c); inp.focus();
}
async function teacher() {
  const { renderTeacher } = await import('./teacher.js');
  await db.setting('activeProfile', null);
  const { C, play } = await import('./content.js');
  renderTeacher(root, { db, C, play, settings, openLearner: async id => learner(await db.get('profiles', id)), lock: home, exportBackup, addProfile: () => addProfile(() => teacher()) });
}

async function exportBackup() {
  const data = await db.exportAll(); const text = JSON.stringify(data); const name = `urdu-reader-backup-${new Date().toISOString().slice(0, 10)}.json`;
  try { const { Filesystem, Directory, Encoding } = await import('@capacitor/filesystem'); const { Share } = await import('@capacitor/share'); const r = await Filesystem.writeFile({ path: name, data: text, directory: Directory.Cache, encoding: Encoding.UTF8 }); await Share.share({ title: name, url: r.uri }); return; } catch (e) { /* not on device or plugin missing */ }
  try { const f = new File([text], name, { type: 'application/json' }); if (navigator.canShare && navigator.canShare({ files: [f] })) { await navigator.share({ files: [f], title: name }); return; } } catch (e) {}
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' })); a.download = name; a.click(); toast('Backup downloaded');
}
const lab = (t, node) => { const l = el('label', '', t); l.append(node); return l; };
boot();
