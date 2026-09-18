// Learner mode: Today, Session, Lesson, Review, Read, Test yourself, Progress, Settings.
import { db } from './db.js';
import { C, play, W, shuffle, wordKey, sentKey, el, toast, bandFor } from './content.js';
import * as D from './drills.js';
import * as S from './session.js';

export async function renderLearner(root, ctx) {
  const { profile } = ctx; const st = { tab: 'today' };
  const marks = () => ctx.settings.marks !== false && (st.unitN ?? 0) <= 10;
  const styleName = () => ctx.settings.style || 'naskh';
  const dctx = { record: (drill, item, ok, ms) => S.recordAttempt(profile.id, st.unitN ?? 0, drill, item, ok, ms) };
  await S.ensureCards(profile.id, await S.currentUnit(profile.id));
  root.innerHTML = ''; const main = el('div'); root.append(main);
  const nav = el('div', 'bottom'); root.append(nav);
  const tabs = [['today', '🏠', 'Today'], ['units', '📚', 'Units'], ['review', '🔁', 'Review'], ['read', '📖', 'Read'], ['progress', '📈', 'Progress'], ['more', '⚙️', 'More']];
  tabs.forEach(([k, ic, lab]) => { const b = el('button', k === st.tab ? 'active' : '', `<span>${ic}</span>${lab}`); b.onclick = () => { st.tab = k; render(); }; b.dataset.k = k; nav.append(b); });
  async function render() { [...nav.children].forEach(b => b.classList.toggle('active', b.dataset.k === st.tab)); main.innerHTML = ''; window.scrollTo(0, 0); await ({ today, units, review, read, progress, more, lesson, session, test }[st.tab])(); }

  async function header(title, sub) { const h = el('div', 'row', ''); h.style.justifyContent = 'space-between'; h.innerHTML = `<div><h1>${title}</h1>${sub ? `<div class="muted">${sub}</div>` : ''}</div>`; const who = el('button', 'btn', `${profile.name} ▾`); who.onclick = ctx.switchProfile; h.append(who); main.append(h); }

  async function today() {
    const cur = await S.currentUnit(profile.id); const s = await S.stats(profile.id); const u = C.units[cur];
    await header(greeting(profile), `Unit ${cur} · ${u.title}`);
    const card = el('div', 'card hero'); card.innerHTML = `<div class="ur">${u.title_ur}</div><div class="muted">${s.due} cards to review · ${s.lettersMastered}/${s.letters} letters solid</div>`;
    const go = el('button', 'btn btn-primary btn-wide', s.sessions ? 'Start today\'s 10 minutes' : 'Start your first session'); go.onclick = () => { st.tab = 'session'; render(); }; card.append(go);
    const open = el('button', 'btn btn-wide', `Open unit ${cur} lesson`); open.onclick = () => { st.unitN = cur; st.tab = 'lesson'; render(); }; card.append(open); main.append(card);
    if (s.wpm.length) { const last = s.wpm[s.wpm.length - 1]; main.append(el('div', 'card', `<b>Last reading speed:</b> ${last.wpm} words per minute <span class="pill ${bandFor(last.wpm)}">${bandFor(last.wpm)}</span>`)); }
    if (cur === 0 && !s.sessions) main.append(el('div', 'card', `<h2>Five things before letter one</h2><ol style="padding-left:18px"><li><b>Right to left.</b> The first letter is on the right.</li><li><b>Letters join</b> like cursive and change shape. Ten never join forward: <span class="ur">ا د ڈ ذ ر ڑ ز ژ و ے</span></li><li><b>Dots decide the letter.</b> <span class="ur">ب پ ت ٹ ث ن ی</span> share one body.</li><li><b>Small marks are vowels.</b> We keep them until unit 11.</li><li><b>Two typefaces</b>, Naskh for learning and Nastaliq for print. Switch in More.</li></ol>`));
  }

  // Session: review due cards, then the next lesson step of the current unit, then one read.
  async function session() {
    const cur = await S.currentUnit(profile.id); st.unitN = cur; const sess = await S.startSession(profile.id); const started = Date.now();
    await header('Session', 'Review → lesson → read · about 10 minutes'); const bar = el('div', 'progress', '<i style="width:0"></i>'); main.append(bar);
    const box = el('div'); main.append(box); let step = 0; const steps = [];
    const due = await S.dueCards(profile.id, 12); if (due.length) steps.push(() => reviewCards(due, box, () => next()));
    const u = C.units[cur]; const p = await S.getProgress(profile.id); const done = p.units[cur]?.steps || {};
    if (u.letters.length && !done.hear) steps.push(() => { box.innerHTML = ''; box.append(el('h2', '', 'New letters')); u.letters.map(c => C.by[c]).filter(Boolean).forEach(l => box.append(D.letterCard(l, dctx))); box.append(nextBtn(() => { done.hear = true; next(); })); });
    if (u.letters.length && !done.tell) steps.push(() => { box.innerHTML = ''; box.append(D.tellApart(u, dctx, (sc) => { done.tell = sc >= 7; box.append(nextBtn(next)); })); });
    if (u.words.length && !done.join) steps.push(() => { box.innerHTML = ''; box.append(D.joinIt(u, dctx, marks, () => { done.join = true; box.append(nextBtn(next)); })); });
    if (u.words.length) steps.push(() => { box.innerHTML = ''; box.append(D.readIt(u, dctx, marks)); box.append(nextBtn(next)); });
    if (u.letters.length && !done.write && profile.track !== 'adult') steps.push(() => { box.innerHTML = ''; box.append(D.writeIt(u, dctx, styleName, () => { done.write = true; })); box.append(nextBtn(next)); });
    if (u.words.length && !done.dict) steps.push(() => { box.innerHTML = ''; box.append(D.dictation(u, dctx, marks, (sc) => { done.dict = sc >= 4; box.append(nextBtn(next)); })); });
    if (u.words.length && !p.units[cur]?.passed && done.dict) steps.push(() => { box.innerHTML = ''; box.append(D.quiz(u, dctx, marks, async (sc, t) => { const passed = await S.markUnit(profile.id, cur, sc, t); if (passed) { toast('Unit ' + cur + ' passed!'); await S.ensureCards(profile.id, cur + 1); } box.append(nextBtn(next)); })); });
    if (u.sentences.length) steps.push(() => fluency(u, box, () => next()));
    if (cur === 0) steps.push(() => { box.innerHTML = ''; box.append(el('div', 'card', '<h2>Unit 0 done</h2><p>You know the five rules. Unit 1 starts with <span class="ur">ا ب ک ل م ن</span>.</p>')); S.markUnit(profile.id, 0, 10, 10).then(() => S.ensureCards(profile.id, 1)); box.append(nextBtn(next)); });
    async function next() { const pr = await S.getProgress(profile.id); pr.units[cur] = { ...(pr.units[cur] || {}), steps: done }; await db.put('progress', pr); step++; bar.firstChild.style.width = Math.min(100, step / Math.max(1, steps.length) * 100) + '%'; if (step >= steps.length) return finish(); steps[step](); }
    async function finish() { sess.bites = step; await S.endSession(sess); const mins = Math.round((Date.now() - started) / 60000); box.innerHTML = ''; box.append(el('div', 'card hero', `<div class="emoji">${profile.track === 'child' ? ['🌟', '🦁', '🎈', '🚀', '🌈'][Math.floor(Math.random() * 5)] : '✓'}</div><h2>Session done</h2><div class="muted">${step} bites in ${mins} min</div>`)); const b = el('button', 'btn btn-primary btn-wide', 'Back to Today'); b.onclick = () => { st.tab = 'today'; render(); }; box.append(b); }
    if (!steps.length) return finish(); steps[0]();
  }
  const nextBtn = fn => { const b = el('button', 'btn btn-primary btn-wide', 'Next'); b.onclick = fn; b.style.marginTop = '10px'; return b; };

  function reviewCards(cards, box, onDone) {
    let i = 0, right = 0; box.innerHTML = ''; const head = el('h2', '', `Review · ${cards.length} cards`), card = el('div', 'card center'), ctr = el('div', 'muted'); box.append(head, ctr, card);
    function show() { if (i >= cards.length) { toast(`${right}/${cards.length} remembered`); onDone(); return; } const c = cards[i]; ctr.textContent = `${i + 1} / ${cards.length}`; card.innerHTML = `<div class="ur big">${c.v || c.item}</div>`;
      const sub = el('div', 'muted', c.kind === 'letter' ? 'Say the letter name and sound' : 'Read the word aloud'); const row = el('div', 'row'); row.style.justifyContent = 'center'; const hear = el('button', 'btn', '🔊 Hear it'); hear.onclick = () => play(S.audioKeyFor(c));
      const reveal = el('div', 'muted', ''); const got = el('button', 'btn btn-primary', 'Got it'), miss = el('button', 'btn', 'Not yet');
      got.onclick = async () => { await S.gradeCard(c, true); right++; i++; show(); }; miss.onclick = async () => { await S.gradeCard(c, false); reveal.textContent = c.kind === 'letter' ? `${C.by[c.item].name} — ${C.by[c.item].hint}` : `${c.rom || ''} ${c.en ? '— ' + c.en : ''}`; play(S.audioKeyFor(c)); setTimeout(() => { i++; show(); }, 1400); };
      row.append(hear, miss, got); card.append(sub, row, reveal); }
    show();
  }

  function fluency(u, box, onDone) {
    box.innerHTML = ''; const sents = u.sentences.map(W); const text = sents.map(s => marks() ? s.v : s.ur).join(' '); const words = text.split(' ').length;
    box.append(el('h2', '', 'Read for speed')); const p = el('div', 'card'); p.innerHTML = `<div class="ur" style="font-size:30px;text-align:right">${text}</div><div class="muted">${words} words. Tap Start, read aloud, tap Stop. Read it twice.</div>`;
    const t = el('div', 'timer', '0.0 s'), start = el('button', 'btn btn-primary', 'Start'), stop = el('button', 'btn', 'Stop'), res = el('div', 'score'); let t0, h; stop.disabled = true;
    start.onclick = () => { t0 = Date.now(); start.disabled = true; stop.disabled = false; h = setInterval(() => t.textContent = ((Date.now() - t0) / 1000).toFixed(1) + ' s', 100); };
    stop.onclick = async () => { clearInterval(h); const sec = (Date.now() - t0) / 1000; const wpm = Math.round(words * 60 / sec); res.textContent = `${wpm} words per minute`; await S.addWpm(profile.id, wpm, u.n); start.disabled = false; stop.disabled = true; start.textContent = 'Again'; };
    const row = el('div', 'row'); row.append(start, stop); sents.forEach((s, i) => row.append(D.playBtn(sentKey(u.n, i), true))); p.append(t, row, res); box.append(p, nextBtn(onDone));
  }

  async function units() { await header('Units', 'Tap a unit to open its lesson'); const p = await S.getProgress(profile.id); const cur = await S.currentUnit(profile.id); const g = el('div', 'unitmap'); C.units.forEach(u => { const b = el('button', (p.units[u.n]?.passed ? 'done ' : '') + (u.n === cur ? 'cur ' : '') + (u.n > cur ? 'locked' : ''), `${u.n}`); b.title = u.title; b.onclick = () => { if (u.n > cur && !confirm(`Unit ${cur} is not passed yet. Open unit ${u.n} anyway?`)) return; st.unitN = u.n; st.tab = 'lesson'; render(); }; g.append(b); }); main.append(g); C.units.forEach(u => main.append(el('div', 'muted', `<b>${u.n}</b> ${u.title} — <span class="ur">${u.letters.join(' ')}</span>`))); }

  async function lesson() { const u = C.units[st.unitN ?? 0]; await header(`Unit ${u.n} · ${u.title}`, u.focus); main.append(el('div', 'ur', u.title_ur));
    if (u.letters.length) { main.append(el('h3', '', '1 · Hear and see')); u.letters.map(c => C.by[c]).filter(Boolean).forEach(l => main.append(D.letterCard(l, dctx))); }
    if (u.n === 6) main.append(aspirates()); if (u.n === 0) main.append(unit0()); if (u.n === 11) main.append(unit11());
    if (u.letters.length) { main.append(el('h3', '', '3 · Tell it apart')); main.append(D.tellApart(u, dctx)); }
    [[D.joinIt, '4 · Join it'], [D.readIt, '5 · Read it']].forEach(([f, t]) => { const x = f(u, dctx, marks); if (x) { main.append(el('h3', '', t)); main.append(x); } });
    if (u.letters.length) { main.append(el('h3', '', '6 · Write it')); main.append(D.writeIt(u, dctx, styleName)); }
    const d = D.dictation(u, dctx, marks); if (d) { main.append(el('h3', '', '7 · Dictation')); main.append(d); }
    const q = D.quiz(u, dctx, marks, async (sc, t) => { const passed = await S.markUnit(profile.id, u.n, sc, t); if (passed) { toast('Unit ' + u.n + ' passed!'); await S.ensureCards(profile.id, u.n + 1); } }); if (q) { main.append(el('h3', '', '8 · Check')); main.append(q); }
    if (u.n === 12) main.append(selfTest());
  }
  function aspirates() { const c = el('div', 'card'); c.innerHTML = '<h2>Aspirates and the nasal vowel</h2><p class="muted">Write ھ after a consonant for a puff of breath (بھ پھ کھ گھ). ں nasalises the vowel before it.</p>'; const t = el('div', 'table'); t.innerHTML = `<table>${C.letters.aspirates.map(a => `<tr><td class="ur" style="font-size:26px">${a[0]}</td><td>${a[1]}</td><td class="ur" style="font-size:24px">${a[2]}</td><td>${a[3]} — ${a[4]}</td><td id="asp-${a[1].replace(/[^a-z]/g, '_')}"></td></tr>`).join('')}</table>`; c.append(t); C.letters.aspirates.forEach(a => c.querySelector('#asp-' + a[1].replace(/[^a-z]/g, '_'))?.append(D.playBtn('aspirates/' + [...a[1]].map(ch => /[a-z0-9]/i.test(ch) ? ch : '_').join(''), true))); return c; }
  function unit0() { const c = el('div', 'card'); c.innerHTML = `<h2>Vowel marks</h2><p class="muted">Same three letters, three words: <span class="ur">گَل</span> gal (cheek) · <span class="ur">گِل</span> gil (clay) · <span class="ur">گُل</span> gul (flower).</p><div class="table"><table>${C.letters.diacritics.map(x => `<tr><td class="ur" style="font-size:26px">بـ${x.ch}</td><td>${x.name}</td><td>${x.sound}</td><td class="ur" style="font-size:22px">${x.example[0]}</td><td>${x.example[1]} — ${x.example[2]}</td><td id="d-${x.id}"></td></tr>`).join('')}</table></div><h3>Long vowels</h3><div class="table"><table>${C.letters.long_vowels.map(x => `<tr><td class="ur" style="font-size:24px">${x[0]}</td><td>${x[1]}</td><td class="ur" style="font-size:22px">${x[2].split(' ')[0]}</td><td>${x[2].split(' ').slice(1).join(' ')}</td></tr>`).join('')}</table></div><h3>Numerals</h3><div class="grid-words">${C.letters.numerals.map(x => `<span>${x[0]}<small style="font-size:12px;color:var(--muted)"> ${x[1]}</small></span>`).join('')}</div>`; C.letters.diacritics.forEach(x => c.querySelector('#d-' + x.id).append(D.playBtn('diacritics/' + x.id, true), D.playBtn('diacritics/' + x.id + '_ex', true))); return c; }
  function unit11() { const c = el('div', 'card'); c.innerHTML = '<h2>Sight words</h2><p class="muted">These twenty are a third of any Urdu text.</p>'; const g = el('div', 'words'); C.letters.sight_words.forEach((w, i) => { const d = el('div', 'word', `<div class="ur">${w}</div>`); d.append(D.playBtn('sight/' + String(i).padStart(2, '0'), true)); d.onclick = () => play('sight/' + String(i).padStart(2, '0')); g.append(d); }); c.append(g); c.insertAdjacentHTML('beforeend', `<h3>Naskh → Nastaliq</h3><div class="row">${['کتاب', 'پڑھنا', 'میں گھر میں ہوں'].map(w => `<div class="card" style="margin:0;text-align:center"><div class="ur" style="font-family:var(--naskh)">${w}</div><div class="ur nastaliq">${w}</div></div>`).join('')}</div><h3>Dictionary order</h3><div class="grid-words" style="font-size:26px">${'ا ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ہ ھ ء ی ے'.split(' ').map(x => `<span>${x}</span>`).join('')}</div><p class="muted">Turn vowel marks off in More and re-read earlier units.</p>`); return c; }

  async function review() { await header('Review', 'Cards due today'); const due = await S.dueCards(profile.id, 30); if (!due.length) { main.append(el('div', 'card center', '<div class="emoji">✓</div>Nothing due. Come back tomorrow, or open a unit.')); return; } const box = el('div'); main.append(box); reviewCards(due, box, () => { st.tab = 'today'; render(); }); }

  async function read() { await header('Read', 'Sentences and repeated reading'); const cur = await S.currentUnit(profile.id); C.units.filter(u => u.sentences.length && u.n <= Math.max(cur, 1)).reverse().forEach(u => { const box = el('div'); main.append(el('h3', '', `Unit ${u.n} · ${u.title}`)); main.append(box); fluency(u, box, () => {}); box.lastChild.remove(); }); }

  async function progress() { await header('Progress'); const s = await S.stats(profile.id); const c = el('div', 'card'); const rows = [['Units passed', `${s.unitsPassed} / 13`], ['Letters solid', `${s.lettersMastered} / ${s.letters}`], ['Words solid', `${s.wordsMastered} / ${s.words}`], ['Sessions', s.sessions], ['Cards due', s.due]]; c.innerHTML = rows.map(([k, v]) => `<div class="row" style="justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line)"><span>${k}</span><b>${v}</b></div>`).join(''); main.append(c);
    if (s.wpm.length) { const w = el('div', 'card'); w.innerHTML = '<h2>Reading speed</h2>'; const mx = Math.max(60, ...s.wpm.map(x => x.wpm)); const g = el('div', 'row'); g.style.alignItems = 'flex-end'; g.style.height = '120px'; s.wpm.slice(-20).forEach(x => { const b = el('div', '', ''); b.style.cssText = `width:14px;height:${Math.max(4, x.wpm / mx * 110)}px;background:var(--accent);border-radius:4px`; b.title = `${x.wpm} wpm`; g.append(b); }); w.append(g, el('div', 'muted', `latest ${s.wpm[s.wpm.length - 1].wpm} wpm · 60 meets the grade-2 standard`)); main.append(w); }
    const a = await db.by('assessments', 'profileId', profile.id); if (a.length) { const last = a.sort((x, y) => y.ts - x.ts)[0]; main.append(el('div', 'card', `<h2>Last assessment</h2><div>${new Date(last.ts).toLocaleDateString()} · passage ${last.orf?.cwpm ?? '-'} cwpm · <span class="pill ${last.band}">${last.band}</span></div>`)); } }

  function selfTest() { const c = el('div', 'card'); c.innerHTML = '<h2>Test yourself</h2><p class="muted">Your reading speed today, not a certificate. A teacher-run assessment is the real measure.</p>'; const b = el('button', 'btn btn-primary', 'Start 60-second letter test'); b.onclick = () => { st.tab = 'test'; render(); }; c.append(b); return c; }
  async function test() { await header('Test yourself', 'Say each letter sound; tap the ones you got wrong'); const letters = shuffle(C.letters.letters.concat(C.letters.letters)).slice(0, 60).map(l => l.ch); const g = el('div', 'grid-words'); const wrong = new Set(); letters.forEach((ch, i) => { const s = el('span', 'item ur', ch); s.onclick = () => { wrong.has(i) ? wrong.delete(i) : wrong.add(i); s.classList.toggle('wrong'); }; g.append(s); }); const t = el('div', 'timer', '60'), start = el('button', 'btn btn-primary', 'Start'), res = el('div', 'score'); let t0, h; start.onclick = () => { t0 = Date.now(); start.disabled = true; h = setInterval(() => { const left = 60 - (Date.now() - t0) / 1000; t.textContent = Math.max(0, left).toFixed(0); if (left <= 0) { clearInterval(h); const done = prompt('How many letters did you reach? (count from the right, top row first)', '60'); const n = Math.min(60, parseInt(done) || 0); const score = n - [...wrong].filter(i => i < n).length; res.textContent = `${score} correct letter sounds per minute`; S.recordAttempt(profile.id, 12, 'self-letters', 'clpm', true, score); } }, 250); }; main.append(t, start, g, res); }

  async function more() { await header('More'); const c = el('div', 'card'); c.innerHTML = '<h2>Settings</h2>';
    const track = sel(['child', 'adult', 'heritage'], ['Child (5–10)', 'Adult, new to Urdu', 'Speaks Urdu, can\'t read'], profile.track, async v => { profile.track = v; await db.put('profiles', profile); ctx.apply(); });
    const style = sel(['naskh', 'nastaliq'], ['Naskh (learning)', 'Nastaliq (print)'], ctx.settings.style || 'naskh', v => ctx.set('style', v));
    const marksCb = el('label', 'row', `<input type="checkbox" ${ctx.settings.marks !== false ? 'checked' : ''}> Show vowel marks (until unit 10)`); marksCb.querySelector('input').onchange = e => ctx.set('marks', e.target.checked);
    const size = sel(['1', '1.25', '1.5'], ['Normal text', 'Large', 'Extra large'], String(ctx.settings.scale || '1'), v => ctx.set('scale', v));
    c.append(lab('Track', track), lab('Script', style), lab('Text size', size), marksCb); main.append(c);
    const d = el('div', 'card'); d.innerHTML = '<h2>Data</h2><p class="muted">Everything stays on this phone. Export to keep a backup or move to another phone.</p>'; const ex = el('button', 'btn', 'Export backup (JSON)'); ex.onclick = () => ctx.exportBackup(); const im = el('input'); im.type = 'file'; im.accept = '.json'; im.onchange = async e => { const f = e.target.files[0]; if (!f) return; const n = await db.importAll(JSON.parse(await f.text())); toast(`Imported ${n} records`); }; const reset = el('button', 'btn btn-danger', 'Reset this profile\'s progress'); reset.onclick = async () => { if (!confirm('Delete all progress for ' + profile.name + '?')) return; for (const s of ['cards', 'attempts', 'sessions', 'assessments']) for (const r of await db.by(s, 'profileId', profile.id)) await db.del(s, r.id); await db.del('progress', profile.id); toast('Reset'); st.tab = 'today'; render(); }; d.append(el('div', 'row', ''), ex, lab('Import backup', im), reset); main.append(d);
    const sw = el('button', 'btn btn-wide', 'Switch profile / mode'); sw.onclick = ctx.switchProfile; main.append(sw);
    main.append(el('p', 'muted', 'Urdu Reader · course and evidence at github.com/oyekamal/urdu-reading-course · audio is machine voice (non-commercial licence)')); }
  const sel = (vals, labels, cur, on) => { const s = el('select'); vals.forEach((v, i) => s.append(new Option(labels[i], v, false, v === cur))); s.onchange = () => on(s.value); return s; };
  const lab = (t, node) => { const l = el('label', '', t); l.append(node); return l; };
  render();
}
function greeting(p) { const h = new Date().getHours(); return (h < 12 ? 'Good morning, ' : h < 17 ? 'Good afternoon, ' : 'Good evening, ') + p.name; }
