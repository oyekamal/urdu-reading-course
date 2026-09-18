// Duolingo-style path: each unit is a row of short lessons. One letter per lesson, then word lessons, then the unit quiz
// that unlocks the next unit. One task per screen, a big Continue button, a visible path of done / current / locked bubbles.
import { db } from './db.js';
import { C, play, W, shuffle, el, toast } from './content.js';
import * as D from './drills.js';
import * as S from './session.js';

export function lessonsFor(u) {
  const L = [];
  if (u.n === 0) { L.push({ id: 'rules', kind: 'rules', title: 'Five rules', icon: '📖' }, { id: 'marks', kind: 'marks', title: 'Vowel marks', icon: '◌ٍ' }, { id: 'done', kind: 'done', title: 'Finish unit', icon: '🏁' }); return L; }
  u.letters.forEach(c => { const l = C.by[c]; if (l) L.push({ id: 'L' + l.id, kind: 'letter', ch: c, title: l.name, icon: c }); });
  if (u.n === 6) L.push({ id: 'aspirates', kind: 'aspirates', title: 'Breath letters', icon: 'ھ' });
  const nw = u.words.length;
  if (u.letters.length && nw) L.push({ id: 'join', kind: 'join', title: 'Join them', icon: '🔗' }, { id: 'blend', kind: 'blend', title: 'Blend', icon: 'بَ' });
  if (nw) { L.push({ id: 'W1', kind: 'words', title: 'Words 1', icon: '🧩', range: [0, Math.ceil(nw / 2)] }, { id: 'W2', kind: 'words', title: 'Words 2', icon: '🧩', range: [Math.ceil(nw / 2), nw] }); }
  if (u.n === 4) L.push({ id: 'nonjoin', kind: 'nonjoin', title: 'The non-joiners', icon: 'ا د ر' });
  if (u.sentences.length) L.push({ id: 'read', kind: 'read', title: 'Read', icon: '📚' });
  if (u.n === 10) L.push({ id: 'marks2', kind: 'marks2', title: 'Hamza, marks, numbers', icon: '۱۲۳' });
  if (u.n === 11) L.push({ id: 'sight', kind: 'sight', title: 'Sight words', icon: '👀' }, { id: 'nastaliq', kind: 'nastaliq', title: 'Nastaliq', icon: 'ن' });
  if (u.n === 12) L.push({ id: 'test', kind: 'test', title: 'Reading test', icon: '⏱' });
  if (nw >= 4) L.push({ id: 'quiz', kind: 'quiz', title: 'Unit check', icon: '🏁' });
  else if (u.n !== 12) L.push({ id: 'done', kind: 'done', title: 'Finish unit', icon: '🏁' });
  return L;
}

export async function lessonState(profileId, u) {
  const p = await S.getProgress(profileId); const done = (p.units[u.n] && p.units[u.n].lessons) || {};
  const ls = lessonsFor(u); const firstOpen = ls.findIndex(l => !done[l.id]);
  return { ls, done, current: firstOpen < 0 ? ls.length : firstOpen, passed: !!p.units[u.n]?.passed };
}
async function markLesson(profileId, u, id) { const p = await S.getProgress(profileId); p.units[u.n] = { ...(p.units[u.n] || {}), lessons: { ...((p.units[u.n] || {}).lessons || {}), [id]: Date.now() } }; await db.put('progress', p); }

// ---- path screen ----
export async function renderPath(main, ctx) {
  const { profile } = ctx; const cur = await S.currentUnit(profile.id); const s = await S.stats(profile.id);
  if (s.due) { const r = el('div', 'card row'); r.style.justifyContent = 'space-between'; r.innerHTML = `<div><b>🔁 Review</b><div class="muted">${s.due} cards due</div></div>`; const b = el('button', 'btn btn-primary', 'Start'); b.onclick = () => ctx.go('review'); r.append(b); main.append(r); }
  for (const u of C.units) {
    if (u.n > cur + 1) break; if (u.n < cur - 1) continue;
    const st = await lessonState(profile.id, u); const locked = u.n > cur;
    const card = el('div', 'card'); card.style.opacity = locked ? .5 : 1;
    card.innerHTML = `<div class="row" style="justify-content:space-between"><div><span class="pill">Unit ${u.n}</span> <b>${u.title}</b><div class="ur" style="font-size:20px;color:var(--muted)">${u.title_ur}</div></div>${st.passed ? '<span class="pill" style="background:var(--good);color:#fff">✓ passed</span>' : locked ? '<span class="muted">🔒 finish unit ' + (u.n - 1) + '</span>' : ''}</div>`;
    const path = el('div', 'pathrow');
    st.ls.forEach((l, i) => { const isDone = !!st.done[l.id], isCur = !locked && i === st.current; const b = el('button', 'bubble' + (isDone ? ' done' : isCur ? ' cur' : ' locked'), `<span class="${/[؀-ۿ]/.test(l.icon) ? 'ur' : ''}">${isDone ? '✓' : l.icon}</span><small>${l.title}</small>`); b.setAttribute('aria-label', `${l.title}${isDone ? ', done' : isCur ? ', up next' : ', locked'}`);
      b.onclick = () => { if (locked) return toast(`Finish unit ${u.n - 1} first`); if (!isDone && !isCur) return toast('Do the lessons in order'); ctx.openLesson(u, i); }; path.append(b); });
    card.append(path); if (!locked && !st.passed && st.current < st.ls.length) { const go = el('button', 'btn btn-primary btn-wide', `${st.done[st.ls[0].id] ? 'Continue' : 'Start'}: ${st.ls[st.current].title}`); go.onclick = () => ctx.openLesson(u, st.current); card.append(go); }
    main.append(card);
  }
  if (cur >= 12) main.append(el('div', 'card center', '<div class="emoji">🎓</div><b>You have finished the course.</b><div class="muted">Keep reading in the Read tab and retest every four weeks.</div>'));
}

// ---- one lesson = a few short screens ----
export async function runLesson(main, ctx, u, idx) {
  const { profile, marks, styleName, dctx } = ctx; const ls = lessonsFor(u); const l = ls[idx]; if (!l) return ctx.go('path');
  main.innerHTML = ''; const head = el('div', 'row'); head.style.justifyContent = 'space-between'; head.innerHTML = `<div><div class="muted">Unit ${u.n} · lesson ${idx + 1} of ${ls.length}</div><h1>${l.title}</h1></div>`; const x = el('button', 'btn', '✕'); x.setAttribute('aria-label', 'Leave lesson'); x.onclick = () => ctx.go('path'); head.append(x); main.append(head);
  const dots = el('div', 'progress', '<i style="width:0"></i>'); main.append(dots); const box = el('div'); main.append(box);
  const screens = buildScreens(l, u, ctx); let i = 0;
  const cont = (label = 'Continue') => { const b = el('button', 'btn btn-primary btn-wide', label); b.style.marginTop = '12px'; b.onclick = next; return b; };
  async function next() { i++; dots.firstChild.style.width = Math.min(100, i / screens.length * 100) + '%'; if (i >= screens.length) return finish(); screens[i](box, cont); window.scrollTo(0, 0); }
  async function finish() { await markLesson(profile.id, u, l.id); if (l.kind === 'letter') await S.ensureCardsFor(profile.id, [l.ch]); if (l.kind === 'done') { await S.markUnit(profile.id, u.n, 10, 10); await S.ensureCards(profile.id, u.n + 1); }
    box.innerHTML = ''; const c = el('div', 'card hero'); c.innerHTML = `<div class="emoji">${profile.track === 'child' ? ['🌟', '🦁', '🎈', '🚀', '🌈', '🐼'][idx % 6] : '✓'}</div><h2>${l.title} done</h2>`; const nxt = ls[idx + 1];
    const b = el('button', 'btn btn-primary btn-wide', nxt ? `Next: ${nxt.title}` : 'Back to path'); b.onclick = () => nxt ? runLesson(main, ctx, u, idx + 1) : ctx.go('path'); const back = el('button', 'btn btn-wide', 'Back to path'); back.onclick = () => ctx.go('path'); c.append(b); if (nxt) c.append(back); box.append(c); }
  screens[0](box, cont);
}

function buildScreens(l, u, ctx) {
  const { profile, marks, styleName, dctx } = ctx; const learned = () => C.units.filter(x => x.n < u.n).flatMap(x => x.letters).concat(u.letters.slice(0, u.letters.indexOf(l.ch) + 1));
  const card = (html) => { const c = el('div', 'card'); c.innerHTML = html; return c; };
  const wordsOf = (range) => u.words.slice(range[0], range[1]);
  switch (l.kind) {
    case 'letter': { const L = C.by[l.ch]; const pool = learned(); const sibs = (L.confusable || []).filter(c => pool.includes(c) && C.by[c]);
      const posWord = (pos) => { const words = C.units.filter(x => x.n <= u.n).flatMap(x => x.words.map(W)); const pick = words.find(w => { const i = w.ur.indexOf(L.ch); if (i < 0) return false; const n = w.ur.length; return pos === 'initial' ? i === 0 && n > 1 : pos === 'medial' ? i > 0 && i < n - 1 : pos === 'final' ? i === n - 1 && n > 1 : true; }); return pick; };
      const hl = (w) => [...w.ur].map(c => c === L.ch ? `<span style="color:var(--accent)">${c}</span>` : c).join('');
      const screens = [
      // 1 sound intro
      (box, cont) => { box.innerHTML = ''; const c = card(`<div class="ur big" style="font-size:130px">${L.ch}</div><h2 class="center">${L.name}</h2><p class="center muted">/${L.ipa}/ · ${L.hint}</p>`); const r = el('div', 'row'); r.style.justifyContent = 'center'; const b1 = el('button', 'btn btn-primary', '🔊 Say it again'); b1.onclick = () => play('names/' + L.id); const b2 = el('button', 'btn', `🔊 ${L.example[1]} · ${L.example[2]}`); b2.onclick = () => play('words/' + L.id); r.append(b1, b2); c.append(r, el('div', 'ur center', hl(W(L.example)))); box.append(c, cont('I heard it')); setTimeout(() => play('names/' + L.id), 300); },
      // 2 tap the sound among look-alikes
      (box, cont) => { box.innerHTML = ''; box.append(el('p', 'muted', sibs.length ? `Listen, then tap. ${L.name} looks like ${sibs.map(c => C.by[c].name).join(', ')}: count the dots.` : 'Listen, then tap the letter you hear.')); box.append(D.tellApart(u, dctx, () => box.append(cont()), { letters: [L.ch], learned: pool, rounds: 5 })); if (pool.length < 2) box.append(cont()); },
      // 3 where it sits in a word: four shapes, each in a real word
      (box, cont) => { box.innerHTML = ''; const c = card(`<h2>Where it sits in a word</h2><p class="muted">${L.joiner ? 'It joins the next letter, so it changes shape.' : 'It never joins the next letter: only two shapes.'}${L.never_initial ? ' No word starts with it.' : ''}</p>`); const forms = D.formsOf(L); forms.forEach(([pos, glyph]) => { if (!glyph) return; const w = posWord(pos); const row = el('div', 'row'); row.style.cssText = 'justify-content:space-between;border-top:1px solid var(--line);padding:8px 0'; row.innerHTML = `<div><small class="muted">${pos}</small><div class="ur" style="font-size:44px">${glyph}</div></div>` + (w ? `<div style="text-align:right"><div class="ur" style="font-size:36px">${hl(w)}</div><small class="muted">${w.rom} · ${w.en}</small></div>` : '<div class="muted">—</div>'); if (w) { const i = C.units.findIndex(x => x.words.some(z => z[0] === w.ur)); const j = C.units[i]?.words.findIndex(z => z[0] === w.ur); if (i >= 0) row.append(D.playBtn(`units/u${String(C.units[i].n).padStart(2, '0')}_${String(j).padStart(2, '0')}`, true)); } c.append(row); }); box.append(c, cont('I see it')); },
      // 4 trace, body first dots last
      ...(profile.track === 'adult' ? [] : [(box, cont) => { box.innerHTML = ''; box.append(el('p', 'muted', `✎ ${D.strokeHint(L)} Start at the green dot. Dots last.`), D.writeIt(u, dctx, styleName, () => {}, [L.ch]), cont('Traced it')); }]),
      // 5 blend with a long vowel (only consonants that can start a word)
      ...(L.role === 'consonant' && !L.never_initial ? [(box, cont) => { box.innerHTML = ''; const syl = [['a', 'ا', 'ā'], ['i', 'ی', 'ī'], ['u', 'و', 'ū']]; const c = card(`<h2>Blend it</h2><p class="muted">${L.name} + a long vowel. Tap what you hear.</p>`); const status = el('div', 'score'), ch = el('div', 'choices'); let round = 0, score = 0, target; function next() { if (round >= 3) { status.textContent = `Done: ${score}/3`; ch.innerHTML = ''; box.append(cont()); return; } round++; target = syl[Math.floor(Math.random() * 3)]; status.textContent = `Round ${round}/3`; ch.innerHTML = ''; shuffle(syl).forEach(sy => { const t = el('button', 'tile ur', L.ch + sy[1]); t.setAttribute('aria-label', L.name + ' ' + sy[2]); t.onclick = () => { const ok = sy === target; dctx.record('blend', L.ch + sy[1], ok, 0); if (ok) { t.classList.add('ok'); score++; setTimeout(next, 450); } else { t.classList.add('no'); play(`syllables/${L.id}_${sy[0]}`); } }; ch.append(t); }); play(`syllables/${L.id}_${target[0]}`); } const again = el('button', 'btn', '🔊 Play again'); again.onclick = () => play(`syllables/${L.id}_${target[0]}`); c.append(status, again, ch); box.append(c); next(); }] : []),
      // 6 mini check: 4 mixed items, 75% to pass
      (box, cont) => { box.innerHTML = ''; const c = card(`<h2>Quick check</h2><p class="muted">Four questions on ${L.name}.</p>`); const status = el('div', 'score'), ch = el('div', 'choices'), q = el('div', ''); let i = 0, score = 0; const items = shuffle([...Array(4).keys()]);
        const ask = () => { if (i >= 4) { const ok = score >= 3; status.textContent = `${score}/4 ${ok ? '✓' : ''}`; ch.innerHTML = ''; box.append(ok ? cont('Finish') : el('p', 'muted', 'Not yet solid. Go through the lesson once more.')); if (!ok) { const r = el('button', 'btn btn-primary btn-wide', 'Do the lesson again'); r.onclick = () => ctx.openLesson(u, lessonsFor(u).findIndex(x => x.id === l.id)); box.append(r); } return; }
          const kind = items[i] % 3; i++; status.textContent = `Question ${i}/4`; ch.innerHTML = ''; const opts = shuffle([L.ch, ...shuffle(pool.filter(c => c !== L.ch)).slice(0, 3)]);
          if (kind === 0) { q.textContent = 'Tap the letter you hear'; play('names/' + L.id); opts.forEach(c => { const t = el('button', 'tile ur', c); t.onclick = () => grade(c === L.ch, t); ch.append(t); }); }
          else if (kind === 1) { q.textContent = `Tap ${L.name}`; opts.forEach(c => { const t = el('button', 'tile ur', c); t.onclick = () => grade(c === L.ch, t); ch.append(t); }); }
          else { const forms = D.formsOf(L).filter(f => f[1]); const f = forms[Math.floor(Math.random() * forms.length)]; q.textContent = `Which is ${L.name} at the ${f[0]} position?`; const wrongs = shuffle(pool.filter(c => c !== L.ch && C.by[c])).slice(0, 3).map(c => D.formsOf(C.by[c]).find(x => x[0] === f[0] && x[1])?.[1]).filter(Boolean); shuffle([f[1], ...wrongs]).forEach(g => { const t = el('button', 'tile ur', g); t.onclick = () => grade(g === f[1], t); ch.append(t); }); } };
        const grade = (ok, t) => { dctx.record('check', L.ch, ok, 0); t.classList.add(ok ? 'ok' : 'no'); if (ok) score++; else toast(`That is not ${L.name}`); setTimeout(ask, 500); };
        c.append(status, q, ch); box.append(c); ask(); },
      ]; return screens; }
    case 'join': return [
      (box, cont) => { box.innerHTML = ''; box.append(card(`<h2>Letters join</h2><p>Each letter you learned in this unit, in all its shapes. Joiners change; <span class="ur">${u.letters.filter(c => C.by[c] && !C.by[c].joiner).join(' ') || '—'}</span> never join forward.</p>`)); u.letters.map(c => C.by[c]).filter(Boolean).forEach(L => { const f = el('div', 'forms'); D.formsOf(L).forEach(([n, g]) => f.insertAdjacentHTML('beforeend', `<div><span class="g ur">${g ?? '—'}</span><small>${n}</small></div>`)); const c = card(`<b>${L.name}</b>`); c.append(f); box.append(c); }); box.append(cont()); },
      (box, cont) => { box.innerHTML = ''; box.append(D.joinIt(u, dctx, marks, () => box.append(cont())) || cont()); },
    ];
    case 'blend': return [(box, cont) => { box.innerHTML = ''; const cons = u.letters.map(c => C.by[c]).filter(L => L && L.role === 'consonant' && !L.never_initial); const c = card('<h2>Blend</h2><p class="muted">A letter plus a vowel makes a sound you can say. Tap what you hear.</p>'); const status = el('div', 'score'), ch = el('div', 'choices'); let round = 0, score = 0, target; const syl = [['a', 'ا'], ['i', 'ی'], ['u', 'و']]; const all = cons.flatMap(L => syl.map(sy => ({ L, sy }))); if (!all.length) { box.append(card('<p>No blends in this unit.</p>'), cont()); return; }
      function next() { if (round >= 6) { status.textContent = `Done: ${score}/6`; ch.innerHTML = ''; box.append(cont()); return; } round++; target = all[Math.floor(Math.random() * all.length)]; status.textContent = `Round ${round}/6`; ch.innerHTML = ''; shuffle([target, ...shuffle(all.filter(x => x !== target)).slice(0, 3)]).forEach(x => { const t = el('button', 'tile ur', x.L.ch + x.sy[1]); t.onclick = () => { const ok = x === target; dctx.record('blend', x.L.ch + x.sy[1], ok, 0); if (ok) { t.classList.add('ok'); score++; setTimeout(next, 450); } else { t.classList.add('no'); play(`syllables/${x.L.id}_${x.sy[0]}`); } }; ch.append(t); }); play(`syllables/${target.L.id}_${target.sy[0]}`); }
      const again = el('button', 'btn', '🔊 Play again'); again.onclick = () => play(`syllables/${target.L.id}_${target.sy[0]}`); c.append(status, again, ch); box.append(c); next(); }];
    case 'words': { const range = l.range; return [
      (box, cont) => { box.innerHTML = ''; const sub = { ...u, words: wordsOf(range), wordOffset: range[0] }; box.append(D.readIt(sub, dctx, marks), cont('Read them')); },
      (box, cont) => { box.innerHTML = ''; const sub = { ...u, words: wordsOf(range), wordOffset: range[0] }; box.append(D.joinIt(sub, dctx, marks, () => box.append(cont())) || cont()); },
      (box, cont) => { box.innerHTML = ''; const sub = { ...u, words: wordsOf(range), wordOffset: range[0] }; const d = D.dictation(sub, dctx, marks, () => box.append(cont())); if (d) box.append(d); else box.append(cont()); },
    ]; }
    case 'read': return [(box, cont) => { box.innerHTML = ''; const sents = D.readIt({ ...u, words: [u.words[0]] }, dctx, marks); if (sents) box.append(sents); if (u.passage) box.append(card(`<h2>Passage</h2><div class="ur" style="font-size:26px;text-align:right">${marks() ? W(u.passage).v : u.passage[0]}</div><p class="muted">${u.passage[2]}</p>`)); box.append(cont('Read it twice')); }];
    case 'quiz': return [(box, cont) => { box.innerHTML = ''; box.append(D.quiz(u, dctx, marks, async (sc, t) => { const passed = await S.markUnit(profile.id, u.n, sc, t); if (passed) { toast(`Unit ${u.n} passed! Unit ${u.n + 1} unlocked`); await S.ensureCards(profile.id, u.n + 1); box.append(cont('Finish')); } else { const again = el('button', 'btn btn-wide', 'Try again'); again.onclick = () => runLesson(box.closest('#app') ? box.parentElement : box, ctx, u, lessonsFor(u).length - 1); box.append(el('p', 'muted', 'You need 8 of 10. Go back to Words 1 and 2, then try again.'), again); } })); }];
    case 'rules': return [
      (box, cont) => { box.innerHTML = ''; box.append(card('<div class="emoji center">👉</div><h2 class="center">Urdu is read right to left</h2><p class="center">The first letter of a word is on the right. <span class="ur" style="font-size:34px">کتاب</span> starts with <span class="ur">ک</span>.</p>'), cont()); },
      (box, cont) => { box.innerHTML = ''; box.append(card('<div class="emoji center">✍️</div><h2 class="center">Letters join like cursive</h2><p class="center">Most letters change shape by position. Ten never join forward:</p><div class="ur center" style="font-size:30px">ا د ڈ ذ ر ڑ ز ژ و ے</div>'), cont()); },
      (box, cont) => { box.innerHTML = ''; box.append(card('<div class="emoji center">👀</div><h2 class="center">Dots decide the letter</h2><div class="ur center" style="font-size:40px">ب پ ت ٹ ث ن ی</div><p class="center">Same body, different dots. Count them, and check above or below.</p>'), cont()); },
      (box, cont) => { box.innerHTML = ''; box.append(card('<div class="emoji center">🔤</div><h2 class="center">Two typefaces, one alphabet</h2><div class="row" style="justify-content:center"><div class="card center" style="margin:0"><div class="ur" style="font-family:var(--naskh)">کتاب</div><small class="muted">Naskh · learning</small></div><div class="card center" style="margin:0"><div class="ur nastaliq">کتاب</div><small class="muted">Nastaliq · print</small></div></div>'), cont('Got it')); },
    ];
    case 'marks': return [(box, cont) => { box.innerHTML = ''; box.append(card(`<h2>Small marks are vowels</h2><p>Same three letters, three words:</p><div class="row" style="justify-content:center"><div class="card center" style="margin:0"><div class="ur" style="font-size:40px">گَل</div>gal · cheek</div><div class="card center" style="margin:0"><div class="ur" style="font-size:40px">گِل</div>gil · clay</div><div class="card center" style="margin:0"><div class="ur" style="font-size:40px">گُل</div>gul · flower</div></div>`), ctx.unit0(), cont('Got it')); }];
    case 'aspirates': return [(box, cont) => { box.innerHTML = ''; box.append(ctx.aspirates(), cont()); }];
    case 'nonjoin': return [(box, cont) => { box.innerHTML = ''; box.append(card('<h2>Guess before you look</h2><p>Build <span class="ur">دور</span> <i>dūr</i> and <span class="ur">ہار</span> <i>hār</i>. Which letters made the next letter start fresh?</p>'), D.joinIt({ ...u, words: u.words.filter(w => ['دور', 'ہار', 'دادا'].includes(w[0])) }, dctx, marks, () => {}), card('<p>The rule: <span class="ur" style="font-size:26px">ا د ڈ ذ ر ڑ ز ژ و ے</span> never join forward. You found it yourself.</p>'), cont()); }];
    case 'marks2': return [(box, cont) => { box.innerHTML = ''; box.append(ctx.izafat(), ctx.punctuation(), cont()); }];
    case 'sight': return [(box, cont) => { box.innerHTML = ''; box.append(ctx.unit11(), ctx.sightDrill(), cont()); }];
    case 'nastaliq': return [(box, cont) => { box.innerHTML = ''; box.append(card('<h2>Switch to Nastaliq</h2><p>Turn off vowel marks and switch the script in More. Re-read the earlier units. If a made-up word still decodes, you are ready.</p>'), cont('Understood')); }];
    case 'test': return [(box, cont) => { box.innerHTML = ''; const b = el('button', 'btn btn-primary btn-wide', 'Open the reading test'); b.onclick = () => ctx.go('test'); box.append(card('<h2>Reading test</h2><p>Five parts, like the teacher\'s assessment. Your speed today, not a certificate.</p>'), b, cont('Later')); }];
    case 'done': return [(box, cont) => { box.innerHTML = ''; box.append(card(`<h2>Unit ${u.n} done</h2><p>Unit ${u.n + 1} starts with <span class="ur">${(C.units[u.n + 1] || {}).letters?.join(' ') || ''}</span>.</p>`), cont('Unlock the next unit')); }];
    default: return [(box, cont) => { box.innerHTML = ''; box.append(cont()); }];
  }
}
