// Teacher mode: Class · Lesson · Groups · Assess · Reports · Device.
// Design source: ../research/08_teacher_tools.md §3-§5, ../docs/offline-app-plan.html "Teacher mode screens".
// ctx = {db, C, play, openLearner(profileId), lock()} — supplied by the app shell.
import { el, toast, bandFor, BANDS, wordKey, pad2, W } from './content.js';
import { uid } from './db.js';
import { runEgra } from './egra.js';

const TABS = ['Class', 'Lesson', 'Groups', 'Assess', 'Reports', 'Device'];

const GROUP_ACTIVITY = {
  'pre-reader': 'Units 0–1 — hear it / see it: letter-sound exposure, no independent reading expected yet.',
  letters: 'Units 1–5 — tell-apart and join-it drills: build letter recognition and joining.',
  words: 'Units 6–10 — read and dictation drills: decode and spell whole words.',
  sentences: 'Unit 11 — repeated reading of short sentences for fluency.',
  fluent: 'Passages and comprehension questions; push speed and understanding together.',
};

// ---- shared data loader: one learner row = {profile, latest assessment, progress} ----
async function loadRoster(db) {
  const profiles = (await db.all('profiles')).filter(p => p.kind === 'learner');
  const out = [];
  for (const p of profiles) {
    const assessments = (await db.by('assessments', 'profileId', p.id)).sort((a, b) => b.ts - a.ts);
    const progress = await db.get('progress', p.id);
    out.push({ profile: p, latest: assessments[0] || null, progress });
  }
  return out.sort((a, b) => a.profile.name.localeCompare(b.profile.name));
}

// Lowest unit not yet passed by at least half the class, so Lesson opens on the class's real next step.
function pickDefaultUnit(units, progresses) {
  const total = progresses.length || 1;
  for (const u of units) {
    if (u.n === 0) continue;
    const passedCount = progresses.filter(pr => pr && pr.units && pr.units[u.n] && pr.units[u.n].passed).length;
    if (passedCount < total / 2) return u.n;
  }
  return units[units.length - 1].n;
}

// Minimal markdown -> DOM: headings, lists, tables (as preformatted text), image lines stripped.
function renderMarkdown(md) {
  // Minimal renderer for the course lesson files: headings, lists, pipe tables, paragraphs. Strips images,
  // <details> blocks are kept as text, and raw audio paths become a short "audio in app" note.
  const wrap = el('div', '');
  const inline = t => t.replace(/`assets\/audio\/[^`]*`/g, '<span class="muted">(audio: use the play buttons above)</span>').replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/\*([^*]+)\*/g, '<i>$1</i>');
  const lines = md.split('\n'); let ul = null, table = null, ol = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]; const t = line.trim();
    if (/^!\[/.test(t) || /^<\/?details/.test(t) || /^<\/?summary/.test(t)) { if (/^<summary/.test(t)) wrap.appendChild(el('p', 'muted', t.replace(/<[^>]+>/g, ''))); continue; }
    const h = t.match(/^(#{1,3})\s+(.*)/);
    if (h) { ul = ol = table = null; wrap.appendChild(el(`h${Math.min(3, h[1].length + 1)}`, '', inline(h[2]))); continue; }
    if (/^\|.*\|$/.test(t)) {
      if (/^\|\s*-{2,}/.test(t)) continue; // separator row
      const cells = t.slice(1, -1).split('|').map(c => c.trim());
      if (!table) { ul = ol = null; const tw = el('div', 'table'); table = document.createElement('table'); tw.appendChild(table); wrap.appendChild(tw); table._head = true; }
      const tr = document.createElement('tr'); cells.forEach(c => { const cell = el(table._head ? 'th' : 'td', '', inline(c)); if (/[\u0600-\u06FF]/.test(c) && !table._head) cell.classList.add('ur'); tr.appendChild(cell); }); table.appendChild(tr); table._head = false; continue;
    }
    table = null;
    const li = t.match(/^[-*]\s+(.*)/); if (li) { ol = null; if (!ul) { ul = document.createElement('ul'); wrap.appendChild(ul); } ul.appendChild(el('li', '', inline(li[1]))); continue; }
    const oli = t.match(/^\d+\.\s+(.*)/); if (oli) { ul = null; if (!ol) { ol = document.createElement('ol'); wrap.appendChild(ol); } ol.appendChild(el('li', '', inline(oli[1]))); continue; }
    ul = ol = null; if (t) wrap.appendChild(el('p', '', inline(t)));
  }
  return wrap;
}

// Native Filesystem+Share -> Web Share (files) -> download link. Works with no plugins on desktop.
async function shareOrDownload(filename, mime, text) {
  try {
    const { Filesystem, Directory } = await import('@capacitor/filesystem');
    const { Share } = await import('@capacitor/share');
    const written = await Filesystem.writeFile({ path: filename, data: text, directory: Directory.Cache, encoding: 'utf8' });
    await Share.share({ url: written.uri, title: filename });
    return;
  } catch (e) { /* not native, or plugin unavailable — fall through */ }
  try {
    if (navigator.canShare) {
      const file = new File([text], filename, { type: mime });
      if (navigator.canShare({ files: [file] })) { await navigator.share({ files: [file], title: filename }); return; }
    }
  } catch (e) { /* fall through */ }
  try {
    const blob = new Blob([text], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
    toast(`Downloaded ${filename}`);
  } catch (e) { toast(`Export failed: ${e.message}`); }
}

// Class
async function renderClass(body, ctx, state, goto) {
  const { db } = ctx;
  const roster = await loadRoster(db);
  body.innerHTML = '';
  const card = el('div', 'card');
  card.appendChild(el('h2', '', 'Class roster'));
  const tableWrap = el('div', 'table');
  const table = document.createElement('table');
  table.appendChild(el('tr', '', '<th>Name</th><th>Grade</th><th>Band</th><th>Units passed</th><th></th>'));
  roster.forEach(r => {
    const band = r.latest ? bandFor(r.latest.orf.cwpm) : null;
    const passed = r.progress ? Object.values(r.progress.units || {}).filter(u => u.passed).length : 0;
    const tr = document.createElement('tr');
    tr.appendChild(el('td', '', r.profile.name));
    tr.appendChild(el('td', '', String(r.profile.grade || '')));
    const bandTd = el('td', '');
    bandTd.appendChild(el('span', `pill${band ? '' : ' muted'}`, band || 'not assessed'));
    tr.appendChild(bandTd);
    tr.appendChild(el('td', '', String(passed)));
    const actTd = el('td', 'row');
    const openBtn = el('button', 'btn', 'Open'); openBtn.onclick = () => ctx.openLearner(r.profile.id);
    const assessBtn = el('button', 'btn btn-primary', 'Assess'); assessBtn.onclick = () => goto('Assess', r.profile.id);
    const editBtn = el('button', 'btn', 'Edit');
    editBtn.onclick = () => {
      const name = prompt('Name', r.profile.name);
      if (name == null) return;
      const grade = prompt('Grade (1-5)', r.profile.grade || 1);
      if (grade == null) return;
      db.put('profiles', { ...r.profile, name: name.trim() || r.profile.name, grade: Number(grade) || r.profile.grade })
        .then(() => { toast('Updated'); renderClass(body, ctx, state, goto); });
    };
    const delBtn = el('button', 'btn btn-danger', 'Delete');
    delBtn.onclick = () => {
      if (!confirm(`Delete ${r.profile.name}? This cannot be undone.`)) return;
      db.del('profiles', r.profile.id).then(() => { toast('Deleted'); renderClass(body, ctx, state, goto); });
    };
    actTd.appendChild(openBtn); actTd.appendChild(assessBtn); actTd.appendChild(editBtn); actTd.appendChild(delBtn);
    tr.appendChild(actTd);
    table.appendChild(tr);
  });
  tableWrap.appendChild(table);
  card.appendChild(tableWrap);
  if (!roster.length) card.appendChild(el('p', 'muted', 'No children added yet.'));
  body.appendChild(card);
  const addCard = el('div', 'card');
  addCard.appendChild(el('h2', '', 'Add child'));
  const row = el('div', 'row');
  const nameInp = document.createElement('input'); nameInp.placeholder = 'Name';
  const gradeSel = document.createElement('select');
  [1, 2, 3, 4, 5].forEach(g => { const o = document.createElement('option'); o.value = String(g); o.textContent = `Grade ${g}`; gradeSel.appendChild(o); });
  const trackSel = document.createElement('select');
  [['child', 'Child'], ['adult', 'Adult'], ['heritage', 'Speaks Urdu']].forEach(([v, t]) => { const o = document.createElement('option'); o.value = v; o.textContent = t; trackSel.appendChild(o); });
  row.appendChild(nameInp); row.appendChild(gradeSel); row.appendChild(trackSel);
  addCard.appendChild(row);
  const addBtn = el('button', 'btn btn-primary', 'Add child');
  addBtn.onclick = async () => {
    const name = nameInp.value.trim();
    if (!name) { toast('Enter a name'); return; }
    await db.put('profiles', { id: uid(), name, grade: Number(gradeSel.value), track: trackSel.value, kind: 'learner', unit: 0, createdAt: Date.now() });
    toast('Child added');
    renderClass(body, ctx, state, goto);
  };
  addCard.appendChild(addBtn);
  body.appendChild(addCard);
}

// Lesson
async function renderLesson(body, ctx, state, goto) {
  const { db, C, play } = ctx;
  const roster = await loadRoster(db);
  const defaultN = pickDefaultUnit(C.units, roster.map(r => r.progress));
  const n = state.lessonUnit != null ? state.lessonUnit : defaultN;
  state.lessonUnit = n;
  const unit = C.units.find(u => u.n === n) || C.units[1] || C.units[0];
  body.innerHTML = '';
  const head = el('div', 'card');
  head.appendChild(el('h2', '', `Today's lesson — Unit ${unit.n}: ${unit.title}`));
  const sel = document.createElement('select');
  C.units.forEach(u => {
    const o = document.createElement('option'); o.value = String(u.n); o.textContent = `Unit ${u.n} — ${u.title}`;
    if (u.n === n) o.selected = true;
    sel.appendChild(o);
  });
  sel.onchange = () => { state.lessonUnit = Number(sel.value); renderLesson(body, ctx, state, goto); };
  head.appendChild(sel);
  if (unit.hours) { const heavy = unit.hours[0] >= 3; head.appendChild(el('p', 'muted', `Planned time: ${unit.hours[0]} h for children (about ${Math.round(unit.hours[0] * 60 / 40)} lessons of 40 min) · ${unit.hours[1]} h for adults.${heavy ? ' Heavier unit: look-alike letters need extra tell-apart rounds; plan a second lesson before moving on.' : ''}`)); }
  body.appendChild(head);
  const iDo = el('div', 'card');
  iDo.appendChild(el('h2', '', 'I do — 10 min: teacher shows each new letter'));
  const letterRow = el('div', 'row');
  (unit.letters || []).forEach(ch => {
    const L = C.by[ch];
    if (!L) return;
    const box = el('div', 'card');
    box.appendChild(el('div', 'ur big', ch));
    box.appendChild(el('div', 'muted', L.name));
    const br = el('div', 'row');
    const nameBtn = el('button', 'btn', 'Play name'); nameBtn.onclick = () => play(`names/${L.id}`);
    const wordBtn = el('button', 'btn', 'Play word'); wordBtn.onclick = () => play(`words/${L.id}`);
    br.appendChild(nameBtn); br.appendChild(wordBtn);
    box.appendChild(br);
    letterRow.appendChild(box);
  });
  iDo.appendChild(letterRow);
  if (!(unit.letters || []).length) iDo.appendChild(el('p', 'muted', 'No new letters this unit — review previously taught letters instead.'));
  body.appendChild(iDo);
  const weDo = el('div', 'card');
  weDo.appendChild(el('h2', '', 'We do — 15 min: chorus reading of the word list'));
  const wr = el('div', 'row');
  (unit.words || []).forEach((w, i) => {
    const word = W(w);
    const it = el('span', 'item ur big', word.ur);
    it.onclick = () => play(wordKey(unit.n, i));
    wr.appendChild(it);
  });
  const wordsGrid = el('div', 'grid-words'); wordsGrid.appendChild(wr);
  weDo.appendChild(wordsGrid);
  if (!(unit.words || []).length) weDo.appendChild(el('p', 'muted', 'No word list yet for this unit.'));
  body.appendChild(weDo);
  const youDo = el('div', 'card');
  youDo.appendChild(el('h2', '', 'You do — 15 min: rotation'));
  youDo.appendChild(el('p', '', 'Split into small groups (see the Groups tab for current bands). Rotate every 5 minutes:'));
  const ul = document.createElement('ul');
  [
    "\"letters\" band: Tell-apart and Join-it drills in Learner mode, this unit's letters.",
    "\"words\" band: Read and Dictation drills, this unit's word list.",
    '"sentences"/"fluent" band: repeated reading of the unit passage for fluency.',
  ].forEach(t => ul.appendChild(el('li', '', t)));
  youDo.appendChild(ul);
  body.appendChild(youDo);
  const md = await fetch(`data/lessons/unit_${pad2(unit.n)}.md`).then(r => (r.ok ? r.text() : '')).catch(() => '');
  const scriptCard = el('div', 'card');
  scriptCard.appendChild(el('h2', '', 'Full lesson script'));
  scriptCard.appendChild(md ? renderMarkdown(md) : el('p', 'muted', 'No lesson script file found for this unit.'));
  const shareBtn = el('button', 'btn btn-primary', 'Print/share script');
  shareBtn.onclick = async () => {
    if (navigator.share) {
      try { await navigator.share({ title: `Unit ${unit.n} lesson`, text: md || '' }); return; } catch (e) { /* fall through */ }
    }
    try { await navigator.clipboard.writeText(md || ''); toast('Script copied to clipboard'); }
    catch (e) { toast('Could not share or copy'); }
  };
  scriptCard.appendChild(shareBtn);
  body.appendChild(scriptCard);
}

// Groups
async function renderGroups(body, ctx) {
  const roster = await loadRoster(ctx.db);
  body.innerHTML = '';
  const buckets = {}; BANDS.forEach(([name]) => { buckets[name] = []; });
  const unassessed = [];
  roster.forEach(r => {
    if (!r.latest) { unassessed.push(r.profile.name); return; }
    const band = bandFor(r.latest.orf.cwpm);
    (buckets[band] = buckets[band] || []).push(r.profile.name);
  });
  BANDS.forEach(([name]) => {
    const list = buckets[name] || [];
    const card = el('div', 'card');
    card.appendChild(el('h2', '', `${name} (${list.length})`));
    card.appendChild(el('p', 'muted', GROUP_ACTIVITY[name] || ''));
    card.appendChild(el('p', '', list.length ? list.join(', ') : 'No children in this band yet.'));
    body.appendChild(card);
  });
  const na = el('div', 'card');
  na.appendChild(el('h2', '', `Not yet assessed (${unassessed.length})`));
  na.appendChild(el('p', '', unassessed.length ? unassessed.join(', ') : 'Everyone has been assessed.'));
  body.appendChild(na);
}

// Assess
async function renderAssess(body, ctx, state, goto) {
  const { db } = ctx;
  if (state.assessProfileId) {
    const profile = await db.get('profiles', state.assessProfileId);
    if (profile) {
      body.innerHTML = '';
      const wrap = el('div', '');
      body.appendChild(wrap);
      runEgra(wrap, ctx, profile, (rec) => {
        state.assessProfileId = null;
        toast(`Saved: ${profile.name} — band ${rec.band}`);
        renderAssess(body, ctx, state, goto);
      });
      return;
    }
    state.assessProfileId = null;
  }
  const roster = await loadRoster(db);
  body.innerHTML = '';
  const card = el('div', 'card');
  card.appendChild(el('h2', '', 'Assess a child'));
  const tableWrap = el('div', 'table');
  const table = document.createElement('table');
  table.appendChild(el('tr', '', '<th>Name</th><th>Last assessed</th><th></th>'));
  roster.forEach(r => {
    const tr = document.createElement('tr');
    tr.appendChild(el('td', '', r.profile.name));
    tr.appendChild(el('td', '', r.latest ? new Date(r.latest.ts).toLocaleDateString() : 'never'));
    const btn = el('button', 'btn btn-primary', 'Start assessment');
    btn.onclick = () => { state.assessProfileId = r.profile.id; renderAssess(body, ctx, state, goto); };
    const td = el('td', ''); td.appendChild(btn);
    tr.appendChild(td);
    table.appendChild(tr);
  });
  tableWrap.appendChild(table);
  card.appendChild(tableWrap);
  if (!roster.length) card.appendChild(el('p', 'muted', 'Add children in the Class tab first.'));
  body.appendChild(card);
}

// Reports
async function renderReports(body, ctx, state) {
  const { db } = ctx;
  const roster = await loadRoster(db);
  const rows = roster.filter(r => r.latest).map(r => ({
    name: r.profile.name, ts: r.latest.ts, letters: r.latest.letters, nonwords: r.latest.nonwords,
    words: r.latest.words, cwpm: r.latest.orf.cwpm, comp: r.latest.comp, band: r.latest.band,
  }));
  state.reportSort = state.reportSort || { key: 'name', dir: 1 };
  const { key: sortKey, dir } = state.reportSort;
  rows.sort((a, b) => (a[sortKey] > b[sortKey] ? 1 : a[sortKey] < b[sortKey] ? -1 : 0) * dir);
  body.innerHTML = '';
  const card = el('div', 'card');
  card.appendChild(el('h2', '', 'Class report — latest assessment per child'));
  const tableWrap = el('div', 'table');
  const table = document.createElement('table');
  const headers = [['name', 'Name'], ['ts', 'Date'], ['letters', 'Letters'], ['nonwords', 'Nonwords'], ['words', 'Words'], ['cwpm', 'Passage cwpm'], ['comp', 'Comp'], ['band', 'Band']];
  const trh = document.createElement('tr');
  headers.forEach(([k, label]) => {
    const th = document.createElement('th');
    th.textContent = label + (sortKey === k ? (dir > 0 ? ' ▲' : ' ▼') : '');
    th.style.cursor = 'pointer';
    th.onclick = () => { state.reportSort = { key: k, dir: sortKey === k ? -dir : 1 }; renderReports(body, ctx, state); };
    trh.appendChild(th);
  });
  table.appendChild(trh);
  rows.forEach(r => {
    table.appendChild(el('tr', '', `<td>${r.name}</td><td>${new Date(r.ts).toLocaleDateString()}</td><td>${r.letters}</td><td>${r.nonwords}</td><td>${r.words}</td><td>${r.cwpm}</td><td>${r.comp}/5</td><td>${r.band}</td>`));
  });
  tableWrap.appendChild(table);
  card.appendChild(tableWrap);
  if (!rows.length) card.appendChild(el('p', 'muted', 'No assessments yet.'));
  body.appendChild(card);
  const hist = el('div', 'card');
  hist.appendChild(el('h2', '', 'Band histogram'));
  const counts = {}; BANDS.forEach(([n]) => { counts[n] = 0; });
  rows.forEach(r => { counts[r.band] = (counts[r.band] || 0) + 1; });
  const max = Math.max(1, ...Object.values(counts));
  BANDS.forEach(([n]) => {
    const barRow = el('div', 'row');
    barRow.appendChild(el('div', 'muted', n));
    const bar = document.createElement('div');
    bar.style.background = '#4a7'; bar.style.height = '16px';
    bar.style.width = `${Math.round((counts[n] / max) * 200)}px`;
    barRow.appendChild(bar);
    barRow.appendChild(el('span', 'muted', ` ${counts[n]}`));
    hist.appendChild(barRow);
  });
  body.appendChild(hist);
  const exp = el('div', 'card');
  exp.appendChild(el('h2', '', 'Export / import'));
  const row = el('div', 'row');
  const csvBtn = el('button', 'btn', 'Export CSV');
  csvBtn.onclick = () => {
    const csv = [headers.map(h => h[1]).join(',')]
      .concat(rows.map(r => [r.name, new Date(r.ts).toISOString(), r.letters, r.nonwords, r.words, r.cwpm, `${r.comp}/5`, r.band].join(',')))
      .join('\n');
    shareOrDownload('class-report.csv', 'text/csv', csv);
  };
  const jsonBtn = el('button', 'btn', 'Export full backup (JSON)');
  jsonBtn.onclick = async () => {
    const data = await db.exportAll();
    shareOrDownload('urdu-reader-backup.json', 'application/json', JSON.stringify(data, null, 1));
  };
  row.appendChild(csvBtn); row.appendChild(jsonBtn);
  exp.appendChild(row);
  exp.appendChild(el('p', 'muted', 'Import backup:'));
  const fileInp = document.createElement('input'); fileInp.type = 'file'; fileInp.accept = 'application/json';
  fileInp.onchange = async () => {
    const f = fileInp.files[0]; if (!f) return;
    try {
      const text = await f.text();
      const n = await db.importAll(JSON.parse(text));
      toast(`Imported ${n} records`);
      renderReports(body, ctx, state);
    } catch (e) { toast(`Import failed: ${e.message}`); }
  };
  exp.appendChild(fileInp);
  body.appendChild(exp);
  const slips = el('div', 'card');
  slips.appendChild(el('h2', '', 'Parent slip'));
  roster.filter(r => r.latest).forEach(r => {
    const row2 = el('div', 'row');
    row2.appendChild(el('span', '', r.profile.name));
    const btn = el('button', 'btn', 'Share slip');
    btn.onclick = async () => {
      const advice = r.latest.band === 'fluent' ? 'Reading fluently — keep up daily reading at home.'
        : r.latest.band === 'sentences' ? 'Reading full sentences — practise short passages daily.'
        : r.latest.band === 'words' ? 'Reading whole words — practise the unit word list daily.'
        : r.latest.band === 'letters' ? 'Learning letter sounds — 10 minutes of letter practice daily helps most.'
        : 'Still at pre-reading stage — daily read-aloud time with an adult is the best next step.';
      const lvl = r.latest.orf.cwpm > 90 ? 'exceeds the grade-2 standard' : r.latest.orf.cwpm >= 60 ? 'meets the grade-2 standard' : r.latest.orf.cwpm > 0 ? 'below the grade-2 standard (60 words/minute)' : 'not yet reading'; const text = `${r.profile.name} — ${new Date(r.latest.ts).toLocaleDateString()}\nPassage fluency: ${r.latest.orf.cwpm} correct words/minute — ${lvl}\nStage: ${r.latest.band} (pre-reader 0 · letters 1–19 · words 20–39 · sentences 40–59 · fluent 60+)\nComprehension: ${r.latest.comp ?? '-'}/5\n${advice}`;
      if (navigator.share) {
        try { await navigator.share({ title: `${r.profile.name}'s reading update`, text }); return; } catch (e) { /* fall through */ }
      }
      try { await navigator.clipboard.writeText(text); toast('Slip copied to clipboard'); } catch (e) { toast(text); }
    };
    row2.appendChild(btn);
    slips.appendChild(row2);
  });
  if (!roster.filter(r => r.latest).length) slips.appendChild(el('p', 'muted', 'No assessments yet.'));
  body.appendChild(slips);
}

// Device
async function renderDevice(body, ctx) {
  const { db, C } = ctx;
  body.innerHTML = '';
  const pinCard = el('div', 'card');
  pinCard.appendChild(el('h2', '', 'Teacher PIN'));
  const pinInp = document.createElement('input'); pinInp.type = 'tel'; pinInp.maxLength = 6; pinInp.placeholder = 'New PIN (4-6 digits)';
  const saveBtn = el('button', 'btn btn-primary', 'Save PIN');
  saveBtn.onclick = async () => {
    const v = pinInp.value.trim();
    if (!/^\d{4,6}$/.test(v)) { toast('PIN must be 4-6 digits'); return; }
    await db.setting('teacherPin', v);
    toast('PIN updated'); pinInp.value = '';
  };
  pinCard.appendChild(pinInp); pinCard.appendChild(saveBtn);
  body.appendChild(pinCard);
  const storeCard = el('div', 'card');
  storeCard.appendChild(el('h2', '', 'Storage'));
  if (navigator.storage && navigator.storage.estimate) {
    try {
      const est = await navigator.storage.estimate();
      const mb = (n) => (n ? (n / 1048576).toFixed(1) : '0');
      storeCard.appendChild(el('p', '', `Using ${mb(est.usage)} MB of ${mb(est.quota)} MB available.`));
    } catch (e) { storeCard.appendChild(el('p', 'muted', 'Storage estimate unavailable.')); }
  } else {
    storeCard.appendChild(el('p', 'muted', 'Storage estimate not supported on this device.'));
  }
  body.appendChild(storeCard);
  const packCard = el('div', 'card');
  packCard.appendChild(el('h2', '', 'Content pack'));
  packCard.appendChild(el('p', '', C.version || `${(C.letters.letters || []).length} letters · ${(C.units || []).length} units · ${Object.keys(C.audio || {}).length} audio clips`)); packCard.appendChild(el('p', 'muted', 'Two phones with the same pack id have identical content.'));
  body.appendChild(packCard);
  const lockCard = el('div', 'card');
  const lockBtn = el('button', 'btn btn-danger', 'Lock teacher mode');
  lockBtn.onclick = () => ctx.lock();
  lockCard.appendChild(lockBtn);
  body.appendChild(lockCard);
}

// Shell: tab bar + sub-navigation state
const SCREENS = { Class: renderClass, Lesson: renderLesson, Groups: renderGroups, Assess: renderAssess, Reports: renderReports, Device: renderDevice };

export async function renderTeacher(root, ctx) {
  const state = { lessonUnit: null, assessProfileId: null, reportSort: null };
  let active = 'Class';
  const shell = el('div', '');
  const tabBar = el('div', 'tabs');
  const body = el('div', '');
  shell.appendChild(tabBar); shell.appendChild(body);
  root.innerHTML = ''; root.appendChild(shell);
  function goto(tab, profileId) {
    active = tab;
    if (profileId) state.assessProfileId = profileId;
    renderTabs();
    renderBody();
  }
  function renderTabs() {
    tabBar.innerHTML = '';
    TABS.forEach(t => {
      const b = el('div', `tab${t === active ? ' active' : ''}`, t);
      b.onclick = () => goto(t);
      tabBar.appendChild(b);
    });
  }
  async function renderBody() {
    await SCREENS[active](body, ctx, state, goto);
  }
  renderTabs();
  await renderBody();
}
