// Duolingo-style path: each unit is a row of short lessons. One letter per lesson, then word lessons, then the unit quiz
// that unlocks the next unit. One task per screen, a big Continue button, a visible path of done / current / locked bubbles.
import { db } from './db.js';
import { C, play, W, shuffle, el, toast } from './content.js';
import * as D from './drills.js';
import * as S from './session.js';
import { icon, mascot, unitArt, confetti, LESSON_ICON } from './icons.js';
import { fx, burst } from './fx.js';

export function lessonsFor(u) {
  const L = [];
  if (u.n === 0) { L.push({ id: 'rules', kind: 'rules', title: 'Three rules' }, { id: 'done', kind: 'done', title: 'Finish unit' }); return L; }
  u.letters.forEach(c => { const l = C.by[c]; if (l) L.push({ id: 'L' + l.id, kind: 'letter', ch: c, title: l.name, icon: c }); });
  if (u.n === 6) L.push({ id: 'aspirates', kind: 'aspirates', title: 'Breath letters', icon: 'ھ' });
  const nw = u.words.length;
  if (u.n === 1) L.push({ id: 'marks', kind: 'marks', title: 'Vowel marks', icon: 'بَ' });
  if (u.letters.length && nw) L.push({ id: 'join', kind: 'join', title: 'Join them' }, { id: 'blend', kind: 'blend', title: 'Blend', icon: 'با' });
  if (nw) { L.push({ id: 'W1', kind: 'words', title: 'Words 1', range: [0, Math.ceil(nw / 2)] }, { id: 'W2', kind: 'words', title: 'Words 2', range: [Math.ceil(nw / 2), nw] }); }
  if (u.n === 4) L.push({ id: 'nonjoin', kind: 'nonjoin', title: 'The non-joiners', icon: 'ا د ر' });
  if (u.sentences.length) L.push({ id: 'read', kind: 'read', title: 'Read' });
  if (u.n === 10) L.push({ id: 'marks2', kind: 'marks2', title: 'Hamza, marks, numbers', icon: '۱۲۳' });
  if (u.n === 11) L.push({ id: 'sight', kind: 'sight', title: 'Sight words' }, { id: 'nastaliq', kind: 'nastaliq', title: 'Nastaliq', icon: 'ن' });
  if (u.n === 12) L.push({ id: 'test', kind: 'test', title: 'Reading test' });
  if (nw >= 4) L.push({ id: 'quiz', kind: 'quiz', title: 'Unit check' });
  else if (u.n !== 12) L.push({ id: 'done', kind: 'done', title: 'Finish unit' });
  return L;
}

export async function lessonState(profileId, u) {
  const p = await S.getProgress(profileId); const done = (p.units[u.n] && p.units[u.n].lessons) || {};
  const ls = lessonsFor(u); const firstOpen = ls.findIndex(l => !done[l.id]);
  return { ls, done, current: firstOpen < 0 ? ls.length : firstOpen, passed: !!p.units[u.n]?.passed };
}
async function markLesson(profileId, u, id) { const p = await S.getProgress(profileId); p.units[u.n] = { ...(p.units[u.n] || {}), lessons: { ...((p.units[u.n] || {}).lessons || {}), [id]: Date.now() } }; await db.put('progress', p); }

// ---- path screen ----
// round 7b: each unit card is a pearl necklace. Done lessons are pearls on a curved thread, the current one glows gold,
// later ones are empty bead outlines. A pearl earned since the last time this card was seen (sessionStorage) pops onto
// the thread once. Locked units are a teaser: Marko peeks out from behind the unit art.
const seenKey = (pid, n) => `urc-pearls-${pid}-${n}`;
const seenGet = (k) => { try { const v = sessionStorage.getItem(k); return v == null ? null : JSON.parse(v); } catch (e) { return null; } };
const seenSet = (k, v) => { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
// the thread: an SVG line through the pearl centres that sags a little between neighbours; solid up to the last done pearl
function stringThread(path) {
  const draw = () => { if (!path.isConnected) return; const ps = [...path.querySelectorAll('.pearl')]; if (ps.length < 2) return; const W = path.clientWidth, H = path.clientHeight;
    const c = ps.map(p => [p.offsetLeft + p.offsetWidth / 2, p.offsetTop + p.offsetHeight / 2]); const lastDone = ps.map(p => p.classList.contains('done')).lastIndexOf(true);
    const seg = (a, b) => { const [x1, y1] = c[a], [x2, y2] = c[b]; const row = Math.abs(y2 - y1) < 40; const mx = (x1 + x2) / 2, my = Math.max(y1, y2) + (row ? 14 : 0); const out = x1 < W / 2 ? -26 : 26; return row ? `Q${mx} ${my} ${x2} ${y2}` : `C${x1 + out} ${y1 + 30} ${x2 + out} ${y2 - 30} ${x2} ${y2}`; };
    const run = (from, to) => { let d = `M${c[from][0]} ${c[from][1]}`; for (let i = from; i < to; i++) d += seg(i, i + 1); return d; };
    const strung = lastDone >= 0 ? Math.min(lastDone + 1, ps.length - 1) : 0;
    path.querySelector('svg.string')?.remove();
    path.insertAdjacentHTML('afterbegin', `<svg class="string" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" aria-hidden="true"><path class="s-todo" d="${run(0, ps.length - 1)}"/>${lastDone >= 0 ? `<path class="s-done" d="${run(0, strung)}"/>` : ''}</svg>`); };
  requestAnimationFrame(draw); if (typeof ResizeObserver === 'function') new ResizeObserver(() => requestAnimationFrame(draw)).observe(path);
}
export async function renderPath(main, ctx) {
  const { profile } = ctx; const cur = await S.currentUnit(profile.id); const s = await S.stats(profile.id);
  if (s.due) { const r = el('div', 'card row'); r.style.justifyContent = 'space-between'; r.innerHTML = `<div><b>${icon('review')} Review</b><div class="muted">${s.due} cards due</div></div>`; const b = el('button', 'btn', `${icon('review')} Review`); b.onclick = () => ctx.go('review'); r.append(b); main.append(r); }
  for (const u of C.units) {
    if (u.n > cur + 1) break; if (u.n < cur - 1) continue;
    const st = await lessonState(profile.id, u); const locked = u.n > cur;
    const card = el('div', 'card unit' + (u.n === cur ? ' cur' : '')); if (locked) card.classList.add('teaser');
    const doneIds = st.ls.filter(l => st.done[l.id]).map(l => l.id); const n = doneIds.length;
    const status = st.passed ? `<span class="pill" style="background:var(--good);color:#fff">${icon('check')} passed</span>` : locked ? '' : `<span class="u-count">${n} of ${st.ls.length} pearls</span>`;
    card.innerHTML = `<div class="unit-head"><div class="u-text"><span class="pill">Unit ${u.n}</span><b class="u-title">${u.title}</b><div class="ur nastaliq u-ur">${u.title_ur}</div>${status}</div><span class="art-disc">${locked ? mascot('think', 90, 'peek-lock') : ''}${unitArt(u.n)}</span></div>${locked ? `<div class="lock-say">${icon('lock')} Finish unit ${u.n - 1} to open this</div>` : ''}`;
    const path = el('div', 'thread necklace'); const key = seenKey(profile.id, u.n); const seen = seenGet(key); const fresh = seen ? doneIds.filter(id => !seen.includes(id)) : []; seenSet(key, doneIds);
    st.ls.forEach((l, i) => { const isDone = !!st.done[l.id], isCur = !locked && i === st.current; const face = l.icon && /[؀-ۿ]/.test(l.icon) ? `<span class="ur">${l.icon}</span>` : icon(LESSON_ICON[l.kind] || 'star'); const b = el('button', 'pearl' + (isDone ? ' done' : isCur ? ' cur' : ' locked'), `${isDone ? icon('check') : face}<small>${l.title}</small>`); b.setAttribute('aria-label', `${l.title}${isDone ? ', done' : isCur ? ', up next' : ', locked'}`);
      const row = Math.floor(i / 4), col = i % 4; b.style.gridRow = row + 1; b.style.gridColumn = row % 2 ? 4 - col : col + 1; // snake, so the thread drops down the side
      const k = fresh.indexOf(l.id); if (k >= 0) { b.classList.add('pop'); b.style.setProperty('--pd', (0.35 + k * 0.25) + 's'); }
      b.onclick = () => { if (locked) return toast(`Finish unit ${u.n - 1} first`); if (!isDone && !isCur) return toast('Do the lessons in order'); ctx.openLesson(u, i); }; path.append(b); });
    card.append(path); stringThread(path);
    if (!locked && !st.passed && st.current < st.ls.length) { const go = el('button', 'btn btn-primary btn-wide dock', `${st.done[st.ls[0].id] ? 'Continue' : 'Start'}: ${st.ls[st.current].title}`); go.onclick = () => ctx.openLesson(u, st.current); card.append(go); }
    main.append(card);
    if (fresh.length) requestAnimationFrame(() => { const p = path.querySelector('.pearl.pop'); if (p && p.getBoundingClientRect().top > innerHeight - 160) path.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); });
  }
  if (cur >= 12) main.append(el('div', 'card center', mascot('cheer', 150) + '<b>You have finished the course.</b><div class="muted">Keep reading in the Read tab and retest every four weeks.</div>'));
}

// ---- one lesson = a few short screens ----
export async function runLesson(main, ctx, u, idx) {
  const { profile, marks, styleName, dctx } = ctx; const t = document.getElementById('toast'); if (t) t.classList.remove('show'); const ls = lessonsFor(u); const l = ls[idx]; if (!l) return ctx.go('path');
  main.innerHTML = ''; main.className = 'lesson'; const head = el('div', 'row'); head.style.justifyContent = 'space-between'; head.innerHTML = `<div><div class="muted">Unit ${u.n} · lesson ${idx + 1} of ${ls.length}</div><h1>${l.title}</h1></div>`; const x = el('button', 'btn', icon('cross')); x.setAttribute('aria-label', 'Leave lesson'); x.onclick = () => ctx.go('path'); head.append(x); main.append(head);
  const dots = el('div', 'progress', '<i style="width:0"></i>'); main.append(dots); const box = el('div'); main.append(box);
  const screens = buildScreens(l, u, ctx); let i = 0;
  const cont = (label = 'Continue') => { const b = el('button', 'btn btn-primary btn-wide', label); b.style.marginTop = '12px'; b.onclick = next; return b; };
  ctx.say = (key, force) => { if (profile.track === 'child' || force) ctx.later(() => play('ui/' + key), 120); };
  const rep = el('button', 'btn btn-play', icon('speaker')); rep.setAttribute('aria-label', 'Repeat instruction'); rep.onclick = () => { if (ctx.lastSay) play('ui/' + ctx.lastSay); }; head.insertBefore(rep, x); const _say = ctx.say; ctx.say = (k, f) => { ctx.lastSay = k; _say(k, f); };
  ctx.later = (fn, ms) => { const h = setTimeout(fn, ms); (ctx.timers = ctx.timers || []).push(h); return h; };
  async function next() { (ctx.timers || []).forEach(clearTimeout); ctx.timers = []; const tt = document.getElementById('toast'); if (tt) tt.classList.remove('show'); i++; dots.firstChild.style.width = Math.min(100, i / screens.length * 100) + '%'; if (i >= screens.length) return finish(); screens[i](box, cont); window.scrollTo(0, 0); }
  async function finish() { ctx.say(l.kind === 'quiz' || l.kind === 'done' ? 'unit_done' : 'done'); await markLesson(profile.id, u, l.id); if (l.kind === 'letter') await S.ensureCardsFor(profile.id, [l.ch]); if (l.kind === 'done') { await S.markUnit(profile.id, u.n, 10, 10); await S.ensureCards(profile.id, u.n + 1); }
    box.innerHTML = ''; const big = l.kind === 'quiz' || l.kind === 'done'; const nxt = ls[idx + 1]; const total = await S.pearls(profile.id);
    const pose = big ? 'trophy' : ['cheer', 'clap', 'proud', 'heart'][total % 4]; const cel = el('div', 'celebrate' + (big ? ' gold' : ''), `<div class="cel-rays"></div><div class="cel-top"></div><div class="cel-body"><div class="cel-stage">${mascot(pose, 260)}</div><h1>${big ? 'Unit ' + u.n + ' complete!' : l.title + ' done!'}</h1><div class="cel-chip pop">${icon('star')} +1 pearl</div><p>${total} ${total === 1 ? "pearl" : "pearls"} on your thread · lesson ${idx + 1} of ${ls.length}</p></div><div class="cel-foot"></div>`);
    cel.querySelector('.cel-stage').prepend(fx('stars_pop', { size: 130, cls: 'cel-fx' })); cel.prepend(fx('confetti_burst', { size: '100%', loop: true, cls: 'cel-confetti' }));
    const chip = cel.querySelector('.cel-chip'); chip.insertAdjacentHTML('beforeend', [...Array(12)].map((_, k) => `<i class="cel-pearl" style="--a:${k * 30}deg;--d:${(k % 3) * .08 + .5}s"></i>`).join(''));
    if (big) { const fw = () => cel.isConnected && (burst(), setTimeout(fw, 1800)); setTimeout(fw, 1200); }
    const close = () => cel.remove();
    const b = el('button', 'btn btn-primary btn-wide cel-go', nxt ? `Next: ${nxt.title}` : 'Back to path'); b.onclick = () => { close(); nxt ? runLesson(main, ctx, u, idx + 1) : ctx.go('path'); };
    const back = el('button', 'btn cel-back', `${icon('cross')} Path`); back.setAttribute('aria-label', 'Back to path'); back.onclick = () => { close(); ctx.go('path'); };
    cel.querySelector('.cel-foot').append(b); if (nxt) cel.querySelector('.cel-top').append(back); document.body.append(cel); burst();
  }
  screens[0](box, cont);
}

const dock = box => { const a = box.querySelector('.card .act'); if (a) box.append(a); };
// round 7b: Marko opens every lesson kind that had no character: small, one line, and he talks when audio plays
// (class 'peek' is what content.js play() animates). The letter lesson keeps its big Marko beside the letter.
const GUIDE = { join: ['point', 'Letters hold hands. Watch them change!'], blend: ['listen', 'Listen, then tap the sound you hear.'], words: ['read', 'Real words! Tap one to hear it.'], read: ['read', 'Read it out loud. Slow is fine!'], quiz: ['think', 'Show me what you know. You can do it!'], marks: ['listen', 'Tiny marks, big job: they are the vowels.'], nonjoin: ['think', 'Some letters never hold hands. Which ones?'], aspirates: ['listen', 'Put a hand by your mouth. Feel the puff?'], marks2: ['point', 'A few last marks, and numbers too.'], sight: ['read', 'These words you will just know by sight.'], nastaliq: ['point', 'Same letters, fancier writing.'], test: ['think', 'A quick check of your reading speed.'], done: ['cheer', 'A whole unit! Ready for more?'] };
const guide = (pose, line) => el('div', 'guide', `${mascot(pose, 110, 'peek guide-m')}<span class="peek-say guide-say">${line}</span>`);
function buildScreens(l, u, ctx) {
  const s = screensFor(l, u, ctx); const g = GUIDE[l.kind];
  if (g && s[0]) { const first = s[0]; s[0] = (box, cont) => { first(box, cont); box.prepend(guide(...g)); }; }
  return s;
}
function screensFor(l, u, ctx) {
  const { profile, marks, styleName, dctx } = ctx; const learned = () => C.units.filter(x => x.n < u.n).flatMap(x => x.letters).concat(l.ch ? u.letters.slice(0, u.letters.indexOf(l.ch) + 1) : u.letters).filter(c => C.by[c]);
  const VOW = ['ا', 'ی', 'و']; const learnedVowels = () => VOW.filter(v => learned().includes(v));
  const decodable = (w, set) => [...w.ur].every(c => set.includes(c) || 'ءئؤآ\u0640'.includes(c) || /[\u064B-\u0652\u0670]/.test(c));
  const card = (html) => { const c = el('div', 'card'); c.innerHTML = html; return c; };
  const wordsOf = (range) => u.words.slice(range[0], range[1]);
  switch (l.kind) {
    case 'letter': { const L = C.by[l.ch]; const pool = learned(); const sibs = (L.confusable || []).filter(c => pool.includes(c) && C.by[c]);
      const posWord = (pos) => { const set = learned(); const all = C.units.filter(x => x.n <= u.n).flatMap(x => x.words.map(W)); const words = [...all.filter(w => decodable(w, set)), ...all.filter(w => !decodable(w, set))]; const pick = words.find(w => { const n = w.ur.length; const first = w.ur.indexOf(L.ch), last = w.ur.lastIndexOf(L.ch); if (first < 0) return false; if (pos === 'initial') return first === 0 && n > 1; if (pos === 'final') return last === n - 1 && n > 1; if (pos === 'medial') return [...w.ur].some((c, i) => c === L.ch && i > 0 && i < n - 1); return true; }); return pick; };
      const hl = (w) => [...w.ur].map(c => c === L.ch ? `<span style="color:var(--accent)">${c}</span>` : c).join('');
      const screens = [
      // 1 sound intro
      (box, cont) => { box.innerHTML = ''; const c = card(`<div class="blob"><div class="ur big" style="font-size:130px">${L.ch}</div>${mascot('letter', 150, 'peek')}<span class="peek-say">${L.name}!</span></div>`); const b1 = D.sayBtn(() => play('names/' + L.id), 'Say ' + L.name + ' again'); c.append(D.sayRow(b1)); c.insertAdjacentHTML('beforeend', `<h2 class="center">${L.name}</h2>${profile.track === 'child' ? '' : `<p class="center muted">/${L.ipa}/ · ${L.hint}</p>`}`); const ex = (() => { const set = learned(); for (const x of C.units.filter(x => x.n <= u.n)) for (let i = 0; i < x.words.length; i++) { const w = W(x.words[i]); if (w.ur.includes(L.ch) && decodable(w, set)) return { w, key: `units/u${String(x.n).padStart(2, '0')}_${String(i).padStart(2, '0')}` }; } return null; })(); const exRow = el('div', 'ex-row', `<div><div class="ur">${hl(ex ? ex.w : W(L.example))}</div><small class="muted">${ex ? ex.w.rom + ' · ' + ex.w.en : L.example[1] + ' · ' + L.example[2]}</small></div>`); const b2 = D.playBtn(ex ? ex.key : 'words/' + L.id); b2.setAttribute('aria-label', 'Hear the word'); exRow.prepend(b2); c.append(exRow); box.append(c, cont('I heard it')); ctx.say('listen'); ctx.later(() => play('names/' + L.id), profile.track === 'child' ? 1500 : 200); },
      // 2 tap the sound among look-alikes
      ...(pool.length < 2 ? [] : [(box, cont) => { box.innerHTML = ''; ctx.say('tap_heard'); box.append(el('p', 'muted', sibs.length ? `Listen, then tap. ${L.name} looks like ${sibs.map(c => C.by[c].name).join(', ')}: count the dots.` : 'Listen, then tap the letter you hear.')); box.append(D.tellApart(u, dctx, () => box.append(cont()), { letters: [L.ch], learned: pool, rounds: 5 })); }]),
      // 3 where it sits in a word: four shapes, each in a real word
      (box, cont) => { box.innerHTML = ''; ctx.say('look'); const c = card(`<h2>Where it sits in a word</h2><p class="muted">${L.joiner ? 'It joins the next letter, so it changes shape.' : 'It never joins the next letter: only two shapes.'}${L.never_initial ? ' No word starts with it.' : ''}</p>`); const forms = D.formsOf(L); forms.forEach(([pos, glyph]) => { if (!glyph) return; const w = posWord(pos); const row = el('div', 'row'); row.style.cssText = 'justify-content:space-between;border-top:1px solid var(--line);padding:8px 0'; row.innerHTML = `<div><small class="muted">${pos}</small><div class="ur" style="font-size:44px">${glyph}</div></div>` + (w ? `<div style="text-align:right"><div class="ur" style="font-size:36px">${hl(w)}</div><small class="muted">${w.rom} · ${w.en}</small></div>` : '<div class="muted">—</div>'); if (w) { const i = C.units.findIndex(x => x.words.some(z => z[0] === w.ur)); const j = C.units[i]?.words.findIndex(z => z[0] === w.ur); if (i >= 0) row.append(D.playBtn(`units/u${String(C.units[i].n).padStart(2, '0')}_${String(j).padStart(2, '0')}`, true)); } c.append(row); }); box.append(c, cont('I see it')); },
      // 4 trace, body first dots last
      ...(profile.track === 'adult' ? [] : [(box, cont) => { box.innerHTML = ''; ctx.say('trace'); box.append(el('p', 'muted', `${icon('pen')} ${D.strokeHint(L)} Start at the green dot. Dots last.`), D.writeIt(u, dctx, styleName, () => {}, [L.ch]), cont('Traced it')); }]),
      // 5 blend with a long vowel (only consonants that can start a word)
      ...(L.role === 'consonant' && !L.never_initial ? [(box, cont) => { box.innerHTML = ''; ctx.say('blend'); const syl = [['a', 'ا', 'ā'], ['i', 'ی', 'ī'], ['u', 'و', 'ū']].filter(x => learnedVowels().includes(x[1])); if (syl.length < 2) { const c1 = card(`<h2>Blend it</h2><p class="muted">${L.name} with alif says:</p><div class="ur big">${L.ch}ا</div>`); c1.append(D.sayRow(D.sayBtn(() => play(`syllables/${L.id}_a`), 'Hear it'))); box.append(c1, cont()); play(`syllables/${L.id}_a`); return; } const c = card(`<h2>Blend it</h2><p class="muted">${L.name} + a long vowel. Tap what you hear.</p>`); const status = el('div', 'score'), ch = el('div', 'choices'); let round = 0, score = 0, target; function next() { if (round >= 3) { status.textContent = `Done: ${score}/3`; ch.innerHTML = ''; box.append(cont()); return; } round++; target = syl[Math.floor(Math.random() * syl.length)]; status.textContent = `Round ${round}/3`; ch.innerHTML = ''; shuffle(syl).forEach(sy => { const t = el('button', 'tile ur', L.ch + sy[1]); t.setAttribute('aria-label', L.name + ' ' + sy[2]); t.onclick = () => { const ok = sy === target; dctx.record('blend', L.ch + sy[1], ok, 0); if (ok) { t.classList.add('ok'); score++; setTimeout(next, 450); } else { t.classList.add('no'); play(`syllables/${L.id}_${sy[0]}`); } }; ch.append(t); }); play(`syllables/${L.id}_${target[0]}`); } const again = D.sayBtn(() => play(`syllables/${L.id}_${target[0]}`)); c.append(D.sayRow(again, status), ch); box.append(c); next(); }] : []),
      // 6 mini check: 4 mixed items, 75% to pass
      (box, cont) => { box.innerHTML = ''; const pool = learned(); ctx.say('check'); const c = card(`<h2>Quick check</h2><p class="muted">Four questions on ${L.name}.</p>`); const status = el('div', 'score'), ch = el('div', 'choices'), q = el('div', 'q'); const sb = D.sayBtn(() => play('names/' + L.id)); const qrow = D.sayRow(sb, q); let i = 0, score = 0; const items = shuffle([...Array(4).keys()]);
        const ask = () => { if (i >= 4) { const ok = score >= 3; status.textContent = `${score}/4 ${ok ? '✓' : ''}`; ch.innerHTML = ''; box.append(ok ? cont('Finish') : el('div', 'center', mascot('oops', 110) + '<p class="muted">Not yet solid. Go through the lesson once more.</p>')); if (!ok) { const r = el('button', 'btn btn-primary btn-wide', 'Do the lesson again'); r.onclick = () => ctx.openLesson(u, lessonsFor(u).findIndex(x => x.id === l.id)); box.append(r); } return; }
          const kind = pool.length < 2 ? 2 : items[i] % 3; i++; sb.style.display = kind === 0 ? '' : 'none'; status.textContent = `Question ${i}/4`; ch.innerHTML = ''; const opts = shuffle([L.ch, ...shuffle(pool.filter(c => c !== L.ch)).slice(0, 3)]);
          if (kind === 0) { q.textContent = 'Tap the letter you hear'; play('names/' + L.id); opts.forEach(c => { const t = el('button', 'tile ur', c); t.onclick = () => grade(c === L.ch, t); ch.append(t); }); }
          else if (kind === 1) { q.textContent = `Tap ${L.name}`; opts.forEach(c => { const t = el('button', 'tile ur', c); t.onclick = () => grade(c === L.ch, t); ch.append(t); }); }
          else { const forms = D.formsOf(L).filter(f => f[1]); const f = forms[Math.floor(Math.random() * forms.length)]; q.textContent = `Which is ${L.name} at the ${f[0]} position?`; let wrongs = shuffle(pool.filter(c => c !== L.ch && C.by[c])).slice(0, 3).map(c => D.formsOf(C.by[c]).find(x => x[0] === f[0] && x[1])?.[1]).filter(Boolean); if (!wrongs.length) wrongs = D.formsOf(L).filter(x => x[1] && x[1] !== f[1]).map(x => x[1]); shuffle([f[1], ...wrongs]).forEach(g => { const t = el('button', 'tile ur', g); t.onclick = () => grade(g === f[1], t); ch.append(t); }); } };
        const grade = (ok, t) => { dctx.record('check', L.ch, ok, 0); t.classList.add(ok ? 'ok' : 'no'); if (ok) score++; else toast(`That is not ${L.name}`); setTimeout(ask, 500); };
        c.append(status, qrow, ch); box.append(c); ask(); },
      ]; return screens; }
    case 'join': return [
      (box, cont) => { box.innerHTML = ''; box.append(card(`<h2>Letters join</h2><p>Each letter you learned in this unit, in all its shapes. Joiners change; <span class="ur">${u.letters.filter(c => C.by[c] && !C.by[c].joiner).join(' ') || '—'}</span> never join forward.</p>`)); u.letters.map(c => C.by[c]).filter(Boolean).forEach(L => { const f = el('div', 'forms'); D.formsOf(L).filter(([n, g]) => g).forEach(([n, g]) => f.insertAdjacentHTML('beforeend', `<div><span class="g ur">${g}</span><small>${n}</small></div>`)); f.style.gridTemplateColumns = `repeat(${D.formsOf(L).filter(x => x[1]).length}, 1fr)`; const c = card(`<b>${L.name}</b>`); c.append(f); box.append(c); }); box.append(cont()); },
      (box, cont) => { box.innerHTML = ''; box.append(D.joinIt(u, dctx, marks, () => box.append(cont())) || cont()); },
    ];
    case 'blend': return [(box, cont) => { box.innerHTML = ''; ctx.say('blend'); const cons = u.letters.map(c => C.by[c]).filter(L => L && L.role === 'consonant' && !L.never_initial); const c = card('<h2>Blend</h2><p class="muted">A letter plus a vowel makes a sound you can say. Tap what you hear.</p>'); const status = el('div', 'score'), ch = el('div', 'choices'); let round = 0, score = 0, target; const syl = [['a', 'ا'], ['i', 'ی'], ['u', 'و']].filter(x => learnedVowels().includes(x[1])); const all = cons.flatMap(L => syl.map(sy => ({ L, sy }))); if (!all.length) { box.append(card('<p>No blends in this unit.</p>'), cont()); return; }
      function next() { if (round >= 6) { status.textContent = `Done: ${score}/6`; ch.innerHTML = ''; box.append(cont()); return; } round++; target = all[Math.floor(Math.random() * all.length)]; status.textContent = `Round ${round}/6`; ch.innerHTML = ''; shuffle([target, ...shuffle(all.filter(x => x !== target)).slice(0, 3)]).forEach(x => { const t = el('button', 'tile ur', x.L.ch + x.sy[1]); t.onclick = () => { const ok = x === target; dctx.record('blend', x.L.ch + x.sy[1], ok, 0); if (ok) { t.classList.add('ok'); score++; setTimeout(next, 450); } else { t.classList.add('no'); play(`syllables/${x.L.id}_${x.sy[0]}`); } }; ch.append(t); }); play(`syllables/${target.L.id}_${target.sy[0]}`); }
      const again = D.sayBtn(() => play(`syllables/${target.L.id}_${target.sy[0]}`)); c.append(D.sayRow(again, status), ch); box.append(c); next(); }];
    case 'words': { const range = l.range; return [
      (box, cont) => { box.innerHTML = ''; ctx.say('read'); const sub = { ...u, words: wordsOf(range), wordOffset: range[0] }; box.append(D.readIt(sub, dctx, marks), cont('Read them')); },
      (box, cont) => { box.innerHTML = ''; ctx.say('build'); const sub = { ...u, words: wordsOf(range), wordOffset: range[0] }; box.append(D.joinIt(sub, dctx, marks, () => box.append(cont())) || cont()); },
      (box, cont) => { box.innerHTML = ''; ctx.say('write'); const sub = { ...u, words: wordsOf(range), wordOffset: range[0] }; const d = D.dictation(sub, dctx, marks, () => box.append(cont())); if (d) { box.append(d); dock(box); } else box.append(cont()); },
    ]; }
    case 'read': return [(box, cont) => { box.innerHTML = ''; const sents = D.readIt({ ...u, words: [u.words[0]] }, dctx, marks); if (sents) box.append(sents); if (u.passage) box.append(card(`<h2>Passage</h2><div class="ur" style="font-size:26px;text-align:right">${marks() ? W(u.passage).v : u.passage[0]}</div><p class="muted">${u.passage[2]}</p>`)); box.append(cont('Read it twice')); }];
    case 'quiz': return [(box, cont) => { box.innerHTML = ''; ctx.say('check'); box.append(D.quiz(u, dctx, marks, async (sc, t) => { const passed = await S.markUnit(profile.id, u.n, sc, t); if (passed) { toast(`Unit ${u.n} passed! Unit ${u.n + 1} unlocked`); await S.ensureCards(profile.id, u.n + 1); box.append(cont('Finish')); } else { const again = el('button', 'btn btn-primary btn-wide', 'Try again'); again.onclick = () => runLesson(box.closest('#app') ? box.parentElement : box, ctx, u, lessonsFor(u).length - 1); box.append(el('p', 'muted', 'You need 8 of 10. Go back to Words 1 and 2, then try again.'), again); } })); dock(box); }];
    case 'rules': return [
      (box, cont) => { box.innerHTML = ''; box.append(card(mascot('point', 150, 'peek rules-m') + '<h2 class="center">Urdu is read right to left</h2><p class="center">The first letter of a word is on the right. Your finger moves this way:</p><div class="center" style="font-size:44px">⟵</div>'), cont()); },
      (box, cont) => { box.innerHTML = ''; box.append(card(mascot('read', 150, 'peek rules-m') + '<h2 class="center">Letters join like cursive</h2><p class="center">Most letters hold hands with the next one and change shape. A few never do. You will meet each one in its own lesson.</p>'), cont()); },
      (box, cont) => { box.innerHTML = ''; box.append(card(mascot('think', 150, 'peek rules-m') + '<h2 class="center">Dots decide the letter</h2><p class="center">Some letters share one body and differ only by their dots. Count the dots, and check above or below.</p><div class="center" style="font-size:40px">• &nbsp; •• &nbsp; •••</div>'), cont()); },
    ];
    case 'marks': { const pick = (mark) => { for (let i = 0; i < u.words.length; i++) { const w = W(u.words[i]); if (w.v.includes(mark)) return { w, key: `units/u${String(u.n).padStart(2, '0')}_${String(i).padStart(2, '0')}` }; } return null; }; const Z = pick('\u064e'), I = pick('\u0650'), P = pick('\u064f'); const row = (mark, name, sound, ex) => `<div class="card" style="margin:6px 0"><div class="row" style="justify-content:space-between;flex-wrap:nowrap"><div><span class="ur" style="font-size:44px">ب${mark}</span> <b>${name}</b><div class="muted">${sound}</div></div>${ex ? `<div class="row mk-ex" style="flex-wrap:nowrap" data-key="${ex.key}"><div style="text-align:right"><div class="ur" style="font-size:34px">${ex.w.v}</div><small class="muted">${ex.w.rom} · ${ex.w.en}</small></div></div>` : ''}</div></div>`; return [
      (box, cont) => { box.innerHTML = ''; ctx.say('listen'); box.append(card('<h2>Small marks are vowels</h2><p>A letter alone has no vowel. Three small marks give it a short sound. Adult books drop them; we keep them on until unit 11.</p>' + row('\u064e', 'zabar', 'short a, as in "but"', Z) + row('\u0650', 'zer', 'short i, as in "bit"', I) + row('\u064f', 'pesh', 'short u, as in "put"', P))); box.querySelectorAll('.mk-ex').forEach(r => r.append(D.playBtn(r.dataset.key))); box.append(cont('Got it')); },
      (box, cont) => { box.innerHTML = ''; ctx.say('tap_word'); const c = card('<h2>Find the mark</h2><p class="muted">Tap the word you hear. Listen for the short vowel.</p>'); const status = el('div', 'score'), ch = el('div', 'choices'); const items = u.words.map((w, i) => ({ w: W(w), i })).filter(x => /[\u064e\u0650\u064f]/.test(x.w.v)); let round = 0, score = 0, target; function next() { if (round >= 4) { status.textContent = `Done: ${score}/4`; ch.innerHTML = ''; box.append(cont()); return; } round++; target = items[Math.floor(Math.random() * items.length)]; status.textContent = `Round ${round}/4`; ch.innerHTML = ''; shuffle([target, ...shuffle(items.filter(x => x !== target)).slice(0, 2)]).forEach(x => { const t = el('button', 'tile small ur', x.w.v); t.onclick = () => { const ok = x === target; dctx.record('marks', x.w.ur, ok, 0); if (ok) { t.classList.add('ok'); score++; setTimeout(next, 450); } else { t.classList.add('no'); play(`units/u${String(u.n).padStart(2, '0')}_${String(x.i).padStart(2, '0')}`); } }; ch.append(t); }); play(`units/u${String(u.n).padStart(2, '0')}_${String(target.i).padStart(2, '0')}`); } const again = D.sayBtn(() => play(`units/u${String(u.n).padStart(2, '0')}_${String(target.i).padStart(2, '0')}`)); c.append(D.sayRow(again, status), ch); box.append(c); next(); },
    ]; }
    case 'aspirates': return [(box, cont) => { box.innerHTML = ''; box.append(ctx.aspirates(), cont()); }];
    case 'nonjoin': return [(box, cont) => { box.innerHTML = ''; box.append(card('<h2>Guess before you look</h2><p>Build <span class="ur">دور</span> <i>dūr</i> and <span class="ur">ہار</span> <i>hār</i>. Which letters made the next letter start fresh?</p>'), D.joinIt({ ...u, words: u.words.filter(w => ['دور', 'ہار', 'دادا'].includes(w[0])) }, dctx, marks, () => {}), card('<p>The rule: <span class="ur" style="font-size:26px">ا د ڈ ذ ر ڑ ز ژ و ے</span> never join forward. You found it yourself.</p>'), cont()); }];
    case 'marks2': return [(box, cont) => { box.innerHTML = ''; box.append(ctx.izafat(), ctx.punctuation(), cont()); }];
    case 'sight': return [(box, cont) => { box.innerHTML = ''; box.append(ctx.unit11(), ctx.sightDrill(), cont()); }];
    case 'nastaliq': return [(box, cont) => { box.innerHTML = ''; box.append(card('<h2>Two typefaces, one alphabet</h2><div class="row" style="justify-content:center"><div class="card center" style="margin:0"><div class="ur" style="font-family:var(--naskh)">کتاب</div><small class="muted">Naskh · you learned in this</small></div><div class="card center" style="margin:0"><div class="ur nastaliq">کتاب</div><small class="muted">Nastaliq · print and newspapers</small></div></div>'), card('<h2>Switch to Nastaliq</h2><p>Turn off vowel marks and switch the script in More. Re-read the earlier units. If a made-up word still decodes, you are ready.</p>'), cont('Understood')); }];
    case 'test': return [(box, cont) => { box.innerHTML = ''; const b = el('button', 'btn btn-primary btn-wide', 'Open the reading test'); b.onclick = () => ctx.go('test'); const later = cont('Not now'); later.className = 'btn btn-wide'; box.append(card('<h2>Reading test</h2><p>Five parts, like the teacher\'s assessment. Your speed today, not a certificate.</p>'), later, b); }];
    case 'done': return [(box, cont) => { box.innerHTML = ''; box.append(card(`<h2>Unit ${u.n} done</h2><p>${u.n === 0 ? 'Now the first letter.' : `Unit ${u.n + 1} has ${(C.units[u.n + 1] || {}).letters?.length || 0} new letters.`}</p>`), cont('Unlock the next unit')); }];
    default: return [(box, cont) => { box.innerHTML = ''; box.append(cont()); }];
  }
}
