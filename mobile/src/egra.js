// EGRA-style one-to-one reading assessment (Tangerine-style), teacher administered.
// Five subtasks in order: letter sounds -> nonwords -> familiar words -> passage -> comprehension.
// Design source: ../research/08_teacher_tools.md §3, ../docs/offline-app-plan.html "Teacher mode screens" #4.
//
// Assumption: ctx passed in mirrors teacher.js's ctx ({db, C, ...}); no audio is played during
// the assessment itself (teacher reads/administers it live), so only db/content/C are needed —
// this module falls back to importing db/content directly so it also works stand-alone.
import { C as C_, el, toast, shuffle, W, PRP, BAND_HELP, COMP_MIN, overallBand, overallLevel } from './content.js';
import { db as db_, uid } from './db.js';

const PER_MIN = 60; // seconds per timed subtask
const MIN_PASSAGE_S = 15; // a passage read in less than this is an accidental tap, never a score
const MAX_CWPM = 200;       // no child reads faster than this; anything above is a timing slip and is capped

// ---- honest timer: Date.now-based countdown, immune to setInterval drift ----
function startTimer(seconds, onTick, onDone) {
  const start = Date.now();
  const durMs = seconds * 1000;
  let stopped = false;
  let h;
  function tick() {
    if (stopped) return;
    const elapsedMs = Date.now() - start;
    const remainingMs = Math.max(0, durMs - elapsedMs);
    onTick(Math.ceil(remainingMs / 1000), elapsedMs / 1000);
    if (remainingMs <= 0) { stopped = true; onDone(elapsedMs / 1000); return; }
    h = setTimeout(tick, 200);
  }
  tick();
  return () => { stopped = true; clearTimeout(h); };
}

function beep() {
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    const actx = new Ctx();
    const o = actx.createOscillator(), g = actx.createGain();
    o.type = 'square'; o.frequency.value = 880;
    o.connect(g); g.connect(actx.destination);
    g.gain.setValueAtTime(0.25, actx.currentTime);
    o.start();
    o.stop(actx.currentTime + 0.35);
    o.onended = () => actx.close().catch(() => {});
  } catch (e) { /* no audio backend available — visual flash still fires */ }
}

function flash(node) {
  const prev = node.style.background;
  node.style.background = '#ffe0e0';
  setTimeout(() => { node.style.background = prev; }, 450);
}

function fillTo(arr, n) {
  const out = [];
  while (out.length < n) out.push(...arr);
  return out.slice(0, n);
}

function scriptClass(nastaliq) { return nastaliq ? 'ur nastaliq' : 'ur'; }

function renderGrid(items, cls, perRow) {
  // Tangerine-style paging: 10 items per page, big and tappable; Prev/Next under the grid.
  const grid = el('div', 'grid-words'); grid.style.cssText = 'font-size:34px;justify-content:center;min-height:120px';
  const pager = el('div', 'row'); pager.style.justifyContent = 'center';
  const prev = el('button', 'btn', '‹ Prev'), info = el('span', 'muted', ''), next = el('button', 'btn', 'Next ›');
  let page = 0; const pages = Math.ceil(items.length / perRow);
  function draw() { grid.innerHTML = ''; items.slice(page * perRow, (page + 1) * perRow).forEach((txt, j) => { const it = el('span', `item ${cls}`, txt); it.dataset.i = String(page * perRow + j); if (grid._wrong && grid._wrong.has(page * perRow + j)) it.classList.add('wrong'); grid.appendChild(it); }); info.textContent = `${page + 1} / ${pages}`; prev.disabled = page === 0; next.disabled = page >= pages - 1; }
  prev.onclick = () => { if (page > 0) { page--; draw(); } }; next.onclick = () => { if (page < pages - 1) { page++; draw(); } };
  pager.append(prev, info, next); draw();
  const box = el('div'); box.append(grid, pager); box.grid = grid; box.reached = () => (page + 1) * perRow; return box;
}

// ---- shared flash-card subtask runner: letter sounds / nonwords / familiar words ----
function runFlashSubtask(root, opts) {
  const { title, items, cls, onScore, onSkip } = opts;
  const wrong = new Set();
  let finished = false, touched = false;
  const wrap = el('div', 'card');
  wrap.appendChild(el('h2', '', title));
  const timerEl = el('div', 'timer big', String(PER_MIN)); timerEl.style.cssText = 'position:sticky;top:0;background:var(--card);z-index:2;padding:4px 0';
  wrap.appendChild(timerEl);
  const gridBox = renderGrid(items, cls, 10); const grid = gridBox.grid; grid._wrong = wrong;
  grid.addEventListener('click', (ev) => {
    const t = ev.target.closest('.item');
    if (!t || finished) return;
    const i = Number(t.dataset.i); touched = true;
    if (wrong.has(i)) { wrong.delete(i); t.classList.remove('wrong'); }
    else { wrong.add(i); t.classList.add('wrong'); }
    checkStopRule();
  });
  gridBox.addEventListener('click', ev => { if (ev.target.closest('button')) touched = true; });
  wrap.appendChild(gridBox); wrap.appendChild(el('p', 'muted', 'Tap a letter the child gets wrong. Use Next as the child reads on; the last page shown counts as items attempted.'));
  const row = el('div', 'row');
  const skipBtn = el('button', 'btn', 'Skip');
  skipBtn.onclick = () => { if (finished) return; finished = true; stop(); onSkip(); };
  row.appendChild(skipBtn);
  wrap.appendChild(row);
  root.innerHTML = ''; root.appendChild(wrap);

  function checkStopRule() {
    if (finished || items.length < 10) return;
    for (let k = 0; k < 10; k++) if (!wrong.has(k)) return; // not all wrong yet
    finished = true; stop();
    flash(wrap); beep();
    toast('Stop rule: first 10 wrong — subtask ends at 0');
    onScore(0);
  }

  const stop = startTimer(PER_MIN, (secLeft) => { timerEl.textContent = String(secLeft); }, () => {
    if (finished) return;
    finished = true;
    flash(wrap); beep();
    const finishAt = (attempted) => { finished = true; const score = Math.max(0, attempted - [...wrong].filter(i => i < attempted).length); onScore(score, attempted); };
    if (touched) { finishAt(Math.min(items.length, gridBox.reached())); return; }
    // nothing was tapped and no page was turned: nobody said how far the child got, so ask instead of crediting a whole page
    finished = false; const ask = el('div', 'row'); const num = el('input'); num.type = 'number'; num.min = 0; num.max = items.length; num.value = ''; num.setAttribute('aria-label', 'How many items did the child read?'); num.style.width = '90px';
    const go = el('button', 'btn btn-primary', 'Score it'); go.onclick = () => { const n = Math.max(0, Math.min(items.length, parseInt(num.value, 10))); if (Number.isNaN(n)) { toast('Type how many the child read'); return; } ask.remove(); finishAt(n); };
    ask.append(el('span', '', 'Time is up. How many did the child read?'), num, go); wrap.appendChild(ask);
  });
}

// ---- passage subtask: tappable words, error marking, "last word reached", "child finished" ----
// The score needs to know how far the child got. It is never assumed: when time runs out (or the teacher says the child stopped early)
// the teacher taps the last word reached first; "Child finished" asks whether the whole passage was read; a Finish before MIN_PASSAGE_S is ignored.
function runPassageSubtask(root, opts) {
  const { text, cls, onScore, onSkip } = opts;
  const words = text.split(/\s+/).filter(Boolean);
  const wrong = new Set();
  let lastIdx = null;
  let markMode = false;
  let finished = false;
  let awaiting = false; // true once the score is waiting for the "last word reached" tap
  const start = Date.now();

  const wrap = el('div', 'card');
  wrap.appendChild(el('h2', '', 'Passage — oral reading fluency (60s)'));
  const timerEl = el('div', 'timer big', String(PER_MIN)); timerEl.style.cssText = 'position:sticky;top:0;background:var(--card);z-index:2;padding:4px 0';
  wrap.appendChild(timerEl);
  const note = el('p', 'muted', 'Tap words the child gets wrong. Tap "Mark last word reached", then the word, if the child stops before the end.'); note.setAttribute('role', 'status');
  const p = el('div', 'grid-words');
  const row1 = el('div', 'row');
  words.forEach((w, i) => {
    const sp = el('span', `item ${cls}`, w);
    sp.dataset.i = String(i);
    row1.appendChild(sp);
  });
  p.appendChild(row1);
  wrap.appendChild(p);
  wrap.appendChild(note);

  p.addEventListener('click', (ev) => {
    const sp = ev.target.closest('.item');
    if (!sp || finished) return;
    const i = Number(sp.dataset.i);
    if (markMode) {
      lastIdx = i;
      p.querySelectorAll('.item').forEach(e => { e.style.outline = ''; });
      sp.style.outline = '3px solid orange';
      markMode = false; markBtn.classList.remove('btn-primary');
      if (awaiting) { finBtn.disabled = false; note.textContent = `Last word reached: word ${i + 1}. Tap Score it.`; }
      return;
    }
    if (wrong.has(i)) { wrong.delete(i); sp.classList.remove('wrong'); }
    else { wrong.add(i); sp.classList.add('wrong'); }
  });

  const row = el('div', 'row');
  const markBtn = el('button', 'btn', 'Mark last word reached');
  markBtn.onclick = () => { markMode = awaiting ? true : !markMode; markBtn.classList.toggle('btn-primary', markMode); };
  const finBtn = el('button', 'btn btn-primary', 'Child finished');
  const ask = el('div', 'row'); ask.style.display = 'none';
  const yesBtn = el('button', 'btn btn-primary', 'Read to the end'), noBtn = el('button', 'btn', 'Stopped early: tap last word');
  ask.append(el('span', '', 'Did the child read the whole passage?'), yesBtn, noBtn);
  const noneBtn = el('button', 'btn', 'Read no words'); noneBtn.style.display = 'none';
  finBtn.onclick = () => {
    if (finished) return;
    if (awaiting) { if (lastIdx != null) finish(true); return; }
    const sec = (Date.now() - start) / 1000;
    if (sec < MIN_PASSAGE_S) { note.textContent = `Only ${Math.floor(sec)} s so far: too short to score. The timer is still running.`; toast('Too short to score yet'); return; }
    if (lastIdx != null) { finish(false); return; }
    ask.style.display = ''; finBtn.disabled = true;
  };
  yesBtn.onclick = () => { ask.style.display = 'none'; finBtn.disabled = false; lastIdx = words.length - 1; finish(false); };
  noBtn.onclick = () => { ask.style.display = 'none'; finBtn.disabled = false; markMode = true; markBtn.classList.add('btn-primary'); note.textContent = 'Tap the last word the child reached, then tap Child finished.'; };
  noneBtn.onclick = () => { if (finished) return; lastIdx = -1; finish(true); };
  const skipBtn = el('button', 'btn', 'Skip');
  skipBtn.onclick = () => { if (finished) return; finished = true; stop(); onSkip(); };
  row.appendChild(markBtn); row.appendChild(finBtn); row.appendChild(noneBtn); row.appendChild(skipBtn);
  wrap.appendChild(row); wrap.appendChild(ask);
  root.innerHTML = ''; root.appendChild(wrap);

  const stop = startTimer(PER_MIN, (secLeft) => { timerEl.textContent = String(secLeft); }, () => {
    if (finished) return;
    flash(wrap); beep();
    if (lastIdx != null) { finish(true); return; }
    // time is up and nobody said how far the child got: do not guess, ask
    awaiting = true; markMode = true; markBtn.classList.add('btn-primary'); ask.style.display = 'none'; finBtn.disabled = true; finBtn.textContent = 'Score it'; noneBtn.style.display = '';
    note.textContent = 'Time is up. Tap the last word the child reached (or "Read no words"), then tap Score it.';
  });

  function finish(timedOut) {
    if (finished) return;
    finished = true; stop();
    const seconds = timedOut ? PER_MIN : Math.max(MIN_PASSAGE_S, Math.min(PER_MIN, (Date.now() - start) / 1000));
    const attempted = Math.max(0, Math.min(words.length, lastIdx + 1));
    let errors = 0;
    wrong.forEach(i => { if (i < attempted) errors++; });
    const raw = Math.max(0, Math.round((attempted - errors) * 60 / seconds)), cwpm = Math.min(MAX_CWPM, raw);
    const acc = attempted ? Math.round(((attempted - errors) / attempted) * 100) : 0;
    onScore({ cwpm, acc, seconds: Math.round(seconds), errors, attempted, capped: raw > MAX_CWPM });
  }
}

// ---- comprehension: 5 questions, teacher marks correct/incorrect, answer key shown small ----
function runComprehensionSubtask(root, opts) {
  const { questions, answers, cls, onScore, onSkip } = opts;
  let i = 0, correct = 0;
  const wrap = el('div', 'card');
  root.innerHTML = ''; root.appendChild(wrap);
  renderQ();
  function renderQ() {
    if (i >= questions.length) { onScore(correct); return; }
    wrap.innerHTML = '';
    wrap.appendChild(el('h2', '', `Comprehension — question ${i + 1} of ${questions.length}`));
    wrap.appendChild(el('p', `${cls} big`, questions[i]));
    wrap.appendChild(el('p', `muted ${cls}`, answers[i] || ''));
    const row = el('div', 'row');
    const okBtn = el('button', 'btn btn-primary', 'Correct');
    okBtn.onclick = () => { correct++; i++; renderQ(); };
    const noBtn = el('button', 'btn btn-danger', 'Incorrect');
    noBtn.onclick = () => { i++; renderQ(); };
    const skipBtn = el('button', 'btn', 'Skip');
    skipBtn.onclick = onSkip;
    row.appendChild(okBtn); row.appendChild(noBtn); row.appendChild(skipBtn);
    wrap.appendChild(row);
  }
}

// ---- result screen ----
function renderResult(root, db, profile, state, onDone) {
  const band = state.orfDone ? overallBand(state.orf.cwpm, state.comp, state.compDone) : 'not tested'; const level = state.orfDone ? overallLevel(state.orf.cwpm, state.comp, state.compDone) : 'passage not tested: no standard result';
  const acc = (s, a) => a ? ` (${Math.round(100 * s / a)}% of ${a} attempted)` : '';
  const wrap = el('div', 'card');
  { const h2 = el('h2', ''); h2.textContent = `Result — ${profile.name}`; wrap.appendChild(h2); }
  const rows = [
    ['Letter sounds (clpm)', `${state.letters}${acc(state.letters, state.lettersAttempted)}`],
    ['Nonwords (cnwpm)', `${state.nonwords}${acc(state.nonwords, state.nonwordsAttempted)}`],
    ['Familiar words (cwpm)', `${state.words}${acc(state.words, state.wordsAttempted)}`],
    ['Passage fluency (cwpm)', state.orfDone ? state.orf.cwpm + (state.orf.capped ? ' (capped: check the timing)' : '') : 'not tested'],
    ['Passage accuracy', state.orfDone ? `${state.orf.acc}%` : '-'],
    ['Comprehension', state.compDone ? `${state.comp}/5${state.comp >= COMP_MIN ? '' : ' (4 of 5 needed)'}` : 'not tested'],
    ['Fluency alone vs grade-2 standard', state.orfDone ? PRP(state.orf.cwpm) : 'not tested'],
    ['Overall (reading + understanding)', level],
    ['Learning band', band],
  ];
  const tableWrap = el('div', 'table');
  const table = el('table');
  rows.forEach(([k, v]) => table.appendChild(el('tr', '', `<td>${k}</td><td>${v}</td>`)));
  tableWrap.appendChild(table);
  wrap.appendChild(tableWrap); wrap.appendChild(el('p', 'muted', BAND_HELP));
  if (state.orfDone && band === 'pre-reader') {
    wrap.appendChild(el('p', 'muted', 'Non-reader / pre-reader band — flag for immediate small-group support (see Groups tab).'));
  }
  const btnRow = el('div', 'row');
  const saveBtn = el('button', 'btn btn-primary', 'Save assessment');
  saveBtn.onclick = async () => {
    saveBtn.disabled = true;
    const rec = {
      id: uid(), profileId: profile.id, ts: Date.now(),
      letters: state.letters, nonwords: state.nonwords, words: state.words,
      orf: state.orf, orfDone: !!state.orfDone, comp: state.comp, compDone: !!state.compDone, band, level, by: 'teacher',
    };
    try { await db.put('assessments', rec); } catch (e) { saveBtn.disabled = false; toast('That did not save. Please tap Save again.'); return; }
    toast('Assessment saved');
    onDone(rec);
  };
  btnRow.appendChild(saveBtn);
  wrap.appendChild(btnRow);
  root.innerHTML = ''; root.appendChild(wrap);
}

/**
 * Run the full EGRA-style assessment for one child.
 * @param {HTMLElement} root - container to render each subtask screen into
 * @param {object} ctx - {db, C, play} — falls back to direct db.js/content.js imports if absent
 * @param {object} profile - the learner profile being assessed ({id, name, ...})
 * @param {function} onDone - called with the saved assessment record when the teacher saves
 */
export function runEgra(root, ctx, profile, onDone) {
  const db = (ctx && ctx.db) || db_;
  const Cc = (ctx && ctx.C) || C_;
  const state = { letters: 0, nonwords: 0, words: 0, orf: { cwpm: 0, acc: 0, seconds: 0, errors: 0 }, comp: 0, compDone: false, orfDone: false };

  db.setting('style').catch(() => 'naskh').then((style) => {
    const cls = scriptClass(style === 'nastaliq');
    const steps = [
      () => runFlashSubtask(root, {
        title: 'Subtask 1 — Letter sounds (60s)',
        items: fillTo(shuffle(Cc.letters.letters.map(l => l.ch)), 100),
        cls, onScore: (n, a) => { state.letters = n; state.lettersAttempted = a; advance(); }, onSkip: advance,
      }),
      () => runFlashSubtask(root, {
        title: 'Subtask 2 — Nonword decoding (60s)',
        items: fillTo(shuffle(Cc.letters.assessment.nonwords || []), 40),
        cls, onScore: (n, a) => { state.nonwords = n; state.nonwordsAttempted = a; advance(); }, onSkip: advance,
      }),
      () => runFlashSubtask(root, {
        title: 'Subtask 3 — Familiar words (60s)',
        items: fillTo(shuffle(Cc.units.flatMap(u => u.words || []).map(w => W(w).ur)), 50),
        cls, onScore: (n, a) => { state.words = n; state.wordsAttempted = a; advance(); }, onSkip: advance,
      }),
      () => runPassageSubtask(root, {
        text: Cc.letters.assessment.passage || '',
        cls, onScore: (orf) => { state.orf = orf; state.orfDone = true; advance(); }, onSkip: advance,
      }),
      () => runComprehensionSubtask(root, {
        questions: Cc.letters.assessment.questions || [],
        answers: Cc.letters.assessment.answers || [],
        cls, onScore: (n) => { state.comp = n; state.compDone = true; advance(); }, onSkip: advance,
      }),
    ];
    let idx = 0;
    function advance() {
      idx++;
      if (idx >= steps.length) { renderResult(root, db, profile, state, onDone); return; }
      steps[idx]();
    }
    steps[0]();
  });
}
