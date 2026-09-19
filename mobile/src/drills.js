// Drill engines, ported from the course app. Each returns a DOM node and reports results via ctx.record(drill, item, correct, ms).
import { C, play, forms, W, shuffle, wordKey, taughtBefore, STROKE, DOTS, el, toast } from './content.js';
import { icon } from './icons.js';

export const formsOf = l => forms(l);
// Words a learner can spell with letters taught so far (plus hamza forms from unit 10). Preview words stay in Read only.
export const EXTRA10 = ['ء', 'ئ', 'ؤ', 'آ', 'ۃ'];
export const known = unit => new Set([...[...taughtBefore(unit.n), ...unit.letters].filter(c => C.by[c]), '\u0640', ...(unit.n >= 10 ? EXTRA10 : [])]);
export const spellable = (unit, ur) => { const k = known(unit); return [...ur].every(c => k.has(c) || /[\u064B-\u0652\u0670]/.test(c)); };
export const cue = ok => { if (document.body.dataset.track === 'child') setTimeout(() => play(ok ? 'ui/correct' : 'ui/wrong'), ok ? 250 : 900); };
export const strokeHint = l => STROKE[l.family] || 'body first in one stroke, right to left; dots last';
export function playBtn(key, small) { const b = el('button', 'btn btn-play' + (small ? ' small' : ''), '▶'); b.setAttribute('aria-label', 'Play'); b.onclick = e => { e.stopPropagation(); if (!play(key)) toast('No audio for this item'); }; return b; }
const disp = (w, marks) => marks ? w.v : w.ur;
const bare = t => t.replace(/[\u064B-\u0652\u0670\u0640]/g, '');  // letters only: what a tile keyboard can type

export function letterCard(l, ctx) {
  const d = el('div', 'card');
  d.innerHTML = `<div class="row" style="justify-content:space-between"><div><b style="font-size:20px">${l.name}</b> <span class="ur" style="color:var(--muted)">${l.name_ur}</span><div class="muted">/${l.ipa}/</div></div><div class="ur big" style="min-width:110px">${l.ch}</div></div>
  <p style="margin:6px 0">${l.hint}</p>
  <div class="row"><span class="ur" style="font-size:26px">${l.example[0]}</span><span class="rom muted">${l.example[1]}</span><span>— ${l.example[2]}</span></div>
  <div class="muted">${icon('pen')} ${STROKE[l.family] || 'body first in one stroke, right to left; dots last'}</div>
  <div class="muted">${l.joiner ? 'joins forward · 4 forms' : 'does <b>not</b> join forward · 2 forms'}${l.never_initial ? ' · never starts a word' : ''}</div>`;
  const bar = el('div', 'row'); bar.append('name ', playBtn('names/' + l.id, true), ' word ', playBtn('words/' + l.id, true));
  if (l.role === 'consonant' && !l.never_initial) [['a', 'ا'], ['i', 'ی'], ['u', 'و']].forEach(([t, v]) => { const b = el('button', 'btn', `<span class="ur">${l.ch}${v}</span>`); b.onclick = () => play(`syllables/${l.id}_${t}`); bar.append(b); });
  d.append(bar);
  const f = el('div', 'forms'); const have = forms(l).filter(x => x[1]); f.style.gridTemplateColumns = `repeat(${have.length}, 1fr)`; have.forEach(([n, s]) => f.insertAdjacentHTML('beforeend', `<div><span class="g ur">${s}</span><small>${n}</small></div>`)); d.append(f);
  return d;
}

// Tap what you hear: pool of confusable letters + 2 recall letters; target always shown.
export function tellApart(unit, ctx, onDone, opts = {}) {
  const focus = opts.letters || unit.letters; const rounds = opts.rounds || 10;
  const have = new Set([...taughtBefore(unit.n), ...(opts.learned || unit.letters)]);
  let pool = [...new Set(focus.flatMap(c => [c, ...(C.by[c]?.confusable || [])]))].filter(c => have.has(c) && C.by[c]);
  pool = [...pool, ...shuffle([...have].filter(c => C.by[c] && !pool.includes(c))).slice(0, Math.max(0, 4 - pool.length + 2))];
  if (pool.length < 2) { const box = el('div', 'card'); box.innerHTML = '<p class="muted">Nothing to compare yet.</p>'; onDone && onDone(0, 0); return box; }
  const box = el('div', 'card'); box.innerHTML = '<h2>Tap what you hear</h2>';
  const status = el('div', 'score'), choices = el('div', 'choices'), btn = el('button', 'btn btn-primary', 'Play sound'); let round = 0, score = 0, target, t0;
  function next() {
    if (round >= rounds) { status.textContent = `Done: ${score}/${rounds}`; choices.innerHTML = ''; btn.textContent = 'Again'; btn.onclick = () => { round = 0; score = 0; next(); }; onDone && onDone(score, rounds); return; }
    round++; target = opts.letters && Math.random() < 0.6 ? focus[Math.floor(Math.random() * focus.length)] : pool[Math.floor(Math.random() * pool.length)]; status.textContent = `Round ${round}/${rounds} · ${score} right`;
    choices.innerHTML = ''; shuffle([target, ...shuffle(pool.filter(c => c !== target)).slice(0, 5)]).forEach(c => { const t = el('button', 'tile ur', c); t.setAttribute('aria-label', C.by[c].name); t.onclick = () => { const ok = c === target; ctx.record('tell', target, ok, Date.now() - t0); if (ok) { t.classList.add('ok'); t.setAttribute('aria-label', C.by[c].name + ', correct'); score++; toast('Correct: ' + C.by[c].name); cue(true); setTimeout(next, 450); } else { t.classList.add('no'); t.setAttribute('aria-label', C.by[c].name + ', wrong'); toast(hintFor(target, c)); cue(false); play('names/' + C.by[c].id); } }; choices.append(t); });
    t0 = Date.now(); play('names/' + C.by[target].id); btn.textContent = 'Play again'; btn.onclick = () => play('names/' + C.by[target].id);
  }
  btn.onclick = next; box.append(status, btn, choices); shuffle(pool).slice(0, 6).forEach(c => { const t = el('button', 'tile ur', c); t.setAttribute('aria-label', C.by[c].name); t.onclick = next; choices.append(t); }); return box;
}
function hintFor(target, picked) { const dt = DOTS[target] || 0, dp = DOTS[picked] || 0; if (dt !== dp) return `${C.by[target].name} has ${dt} dot${dt === 1 ? '' : 's'}, that one has ${dp}`; return `That is ${C.by[picked].name}. Listen again for ${C.by[target].name}`; }

// Build the word from tiles, right to left.
export function joinIt(unit, ctx, marks, onDone) {
  const words = unit.words.map(W).filter(w => bare(w.ur).length >= 3 && spellable(unit, w.ur)).slice(0, 6); if (!words.length) return null;
  const box = el('div', 'card'); box.innerHTML = '<h2>Build the word</h2><p class="muted">Tap the letters in reading order, right to left.</p>';
  const target = el('div', 'answer ur'), tiles = el('div', 'choices'), info = el('div', 'row'), nextB = el('button', 'btn', 'Next word'); let i = 0, cur = '', done = 0, t0;
  function load() { const w = words[i % words.length]; cur = ''; target.textContent = ''; t0 = Date.now(); info.innerHTML = `Make: <b>${w.rom}</b> — ${w.en} `; info.append(playBtn(wordKey(unit.n, unit.words.findIndex(x => x[0] === w.ur) + (unit.wordOffset || 0)), true));
    tiles.innerHTML = ''; const letters = bare(w.ur); shuffle([...letters]).forEach(c => { const t = el('button', 'tile small ur', c); t.setAttribute('aria-label', C.by[c]?.name || c); t.onclick = () => { if (letters[cur.length] === c) { cur += c; target.textContent = cur; t.disabled = true; t.classList.add('ok'); if (cur === letters) { toast('Correct: ' + w.rom); target.textContent = disp(w, marks()); ctx.record('join', w.ur, true, Date.now() - t0); if (++done >= 3 && onDone) onDone(done, 3); } } else { t.classList.add('no'); setTimeout(() => t.classList.remove('no'), 400); ctx.record('join', w.ur, false, Date.now() - t0); } }; tiles.append(t); }); }
  nextB.onclick = () => { i++; load(); }; load(); box.append(info, target, tiles, nextB); return box;
}

export function readIt(unit, ctx, marks, range) {
  if (!unit.words.length) return null; const [lo, hi] = range || [0, unit.words.length];
  const box = el('div', 'card'); box.innerHTML = `<h2>Read</h2><p class="muted">Read aloud, then tap to listen.</p>`;
  const g = el('div', 'words');
  unit.words.map(W).forEach((w, i) => { if (i < lo || i >= hi) return; const d = el('div', 'word'); const prev = !spellable(unit, w.ur); d.innerHTML = `<div class="ur">${disp(w, marks())}</div><div class="rom">${w.rom}</div><div class="en">${w.en.replace(/\s*\([^)]*preview[^)]*\)/, '')}${prev ? ' <span class="pill">peek ahead</span>' : ''}</div>`; d.append(playBtn(wordKey(unit.n, i + (unit.wordOffset || 0)), true)); d.onclick = () => { play(wordKey(unit.n, i + (unit.wordOffset || 0))); d.classList.add('reveal'); ctx.record('read', w.ur, true, 0); }; g.append(d); });
  box.append(g);
  if (unit.sentences.length && !range) { box.append(el('h3', '', 'Sentences')); unit.sentences.map(W).forEach((w, i) => { const d = el('div', 'row', ''); d.style.cssText = 'padding:8px 0;border-top:1px solid var(--line)'; d.append(playBtn(`sentences/u${String(unit.n).padStart(2, '0')}_${String(i).padStart(2, '0')}`)); d.insertAdjacentHTML('beforeend', `<span class="ur" style="font-size:28px;flex:1;min-width:180px;text-align:right">${disp(w, marks())}</span><span class="rom muted">${w.rom}</span><span class="muted">${w.en}</span>`); box.append(d); }); }
  return box;
}

// Tracing: grey glyph, finger stroke, start-side + coverage + stroke-count feedback.
export function writeIt(unit, ctx, styleName, onDone, letters) {
  const ls = (letters || unit.letters).map(c => C.by[c]).filter(Boolean); if (!ls.length) return null;
  const box = el('div', 'card'); box.innerHTML = '<h2>Trace</h2><p class="muted">Start at the green dot. Body first, dots last.</p>';
  const sel = el('select'), formSel = el('select'), cv = el('canvas', 'trace'), out = el('div', 'score'), clear = el('button', 'btn', 'Clear'), check = el('button', 'btn btn-primary', 'Check');
  ls.forEach(l => sel.append(new Option(l.name + ' ' + l.ch, l.ch))); ['isolated', 'initial', 'medial', 'final'].forEach(f => formSel.append(new Option(f, f)));
  cv.width = 360; cv.height = 300; const ctx2 = cv.getContext('2d', { willReadFrequently: true }); let ref = null, drawing = false, startX = null, glyphBox = null, strokes = 0, good = 0;
  const glyph = () => { const l = C.by[sel.value], f = formSel.value; if (!l.joiner && (f === 'initial' || f === 'medial')) return null; return f === 'isolated' ? l.ch : f === 'initial' ? l.ch + 'ـ' : f === 'medial' ? 'ـ' + l.ch + 'ـ' : 'ـ' + l.ch; };
  function base() { ctx2.clearRect(0, 0, cv.width, cv.height); const g = glyph(); out.textContent = ''; strokes = 0; startX = null; if (!g) { ctx2.fillStyle = '#888'; ctx2.font = '16px sans-serif'; ctx2.textAlign = 'center'; ctx2.fillText('This letter has no such form', 180, 150); ref = null; return; }
    const fam = styleName() === 'nastaliq' ? '"Noto Nastaliq Urdu"' : '"Noto Naskh Arabic"'; ctx2.fillStyle = getComputedStyle(document.body).getPropertyValue('--line'); ctx2.font = `170px ${fam}`; ctx2.textAlign = 'center'; ctx2.textBaseline = 'middle'; ctx2.direction = 'rtl'; ctx2.fillText(g, 180, 150); ref = ctx2.getImageData(0, 0, cv.width, cv.height).data;
    let minx = cv.width, maxx = 0, top = cv.height; for (let i = 3; i < ref.length; i += 4) if (ref[i] > 0) { const x = (i >> 2) % cv.width, y = (i >> 2) / cv.width | 0; if (x < minx) minx = x; if (x > maxx) maxx = x; if (x > maxx - 6 && y < top) top = y; }
    glyphBox = [minx, maxx]; ctx2.fillStyle = getComputedStyle(document.body).getPropertyValue('--accent'); ctx2.beginPath(); ctx2.arc(Math.min(maxx + 10, cv.width - 8), Math.min(top + 20, cv.height - 10), 6, 0, 7); ctx2.fill(); }
  const pos = e => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * cv.width / r.width, (e.clientY - r.top) * cv.height / r.height]; };
  cv.onpointerdown = e => { drawing = true; strokes++; const q = pos(e); if (startX === null) startX = q[0]; ctx2.beginPath(); ctx2.moveTo(...q); cv.setPointerCapture(e.pointerId); };
  cv.onpointermove = e => { if (!drawing) return; ctx2.strokeStyle = getComputedStyle(document.body).getPropertyValue('--accent'); ctx2.lineWidth = 14; ctx2.lineCap = 'round'; ctx2.lineJoin = 'round'; ctx2.lineTo(...pos(e)); ctx2.stroke(); };
  cv.onpointerup = cv.onpointercancel = () => drawing = false;
  check.onclick = () => { if (!ref) return; const now = ctx2.getImageData(0, 0, cv.width, cv.height).data; let g = 0, hit = 0, stray = 0; for (let i = 0; i < ref.length; i += 4) { const isG = ref[i + 3] > 0 && ref[i] > 150; const drawn = Math.abs(now[i] - ref[i]) > 40 || Math.abs(now[i + 1] - ref[i + 1]) > 40 || (now[i + 3] > 0 && ref[i + 3] === 0); if (isG) { g++; if (drawn) hit++; } else if (drawn) stray++; }
    const cov = Math.round(100 * hit / Math.max(1, g)), neat = stray < g * 0.8, rtl = startX === null || !glyphBox || startX > (glyphBox[0] + glyphBox[1]) / 2; const l = C.by[sel.value]; const expect = 1 + (DOTS[l.ch] || 0) + (l.ch === 'گ' || l.ch === 'ک' ? 1 : 0);
    const ok = cov >= 80 && neat && rtl; out.textContent = `Coverage ${cov}% ${ok ? '✓ good' : cov < 80 ? '— keep tracing' : !rtl ? '— start on the right side' : '— stay inside the letter'}${strokes > expect + 1 ? ` · ${strokes} strokes, aim for ${expect}` : ''}`; ctx.record('trace', l.ch, ok, 0); if (ok && ++good >= 1 && onDone) onDone(good, 1); };
  clear.onclick = base; sel.onchange = formSel.onchange = base;
  const side = el('div', 'row'); side.append(sel, formSel, check, clear); box.append(cv, side, out); setTimeout(base, 50); return box;
}

// Dictation with a letter keyboard limited to taught letters.
export function dictation(unit, ctx, marks, onDone) {
  if (unit.words.length < 5) return null;
  const box = el('div', 'card'); box.innerHTML = '<h2>Dictation</h2><p class="muted">Hear a word, spell it with the tiles.</p>';
  const keysAll = [...new Set([...taughtBefore(unit.n), ...unit.letters])].filter(c => C.by[c]);
  const ans = el('div', 'answer ur'), keys = el('div', 'keys'), status = el('div', 'score'), playB = el('button', 'btn btn-primary', 'Play word'), checkB = el('button', 'btn', 'Check'), back = el('button', 'btn', '⌫'), skipB = el('button', 'btn', 'Skip');
  const pickable = unit.words.map((w, i) => ({ w: W(w), i })).filter(x => spellable(unit, x.w.ur)); if (pickable.length < 3) return null;
  let items = shuffle(pickable).slice(0, 5), k = 0, typed = '', score = 0, t0;
  [...keysAll, ...(unit.n >= 10 ? EXTRA10 : [])].forEach(c => { const t = el('button', 'tile ur', c); t.setAttribute('aria-label', C.by[c]?.name || c); t.onclick = () => { typed += c; ans.textContent = typed; }; keys.append(t); });
  back.onclick = () => { typed = [...typed].slice(0, -1).join(''); ans.textContent = typed; };
  const key = () => wordKey(unit.n, items[k].i + (unit.wordOffset || 0));
  function show() { if (k >= items.length) { checkB.disabled = true; skipB.disabled = true; back.disabled = true; status.textContent = `Done: ${score}/5`; playB.textContent = 'Again'; playB.onclick = () => { items = shuffle(pickable).slice(0, 5); k = 0; score = 0; checkB.disabled = false; skipB.disabled = false; back.disabled = false; show(); }; onDone && onDone(score, 5); return; } typed = ''; ans.textContent = ''; t0 = Date.now(); status.textContent = `Word ${k + 1}/5 · ${score} right`; playB.textContent = 'Play word'; playB.onclick = () => play(key()); play(key()); }
  checkB.onclick = () => { if (k >= items.length) return; const w = items[k].w; const ok = typed === bare(w.ur); ctx.record('dictation', w.ur, ok, Date.now() - t0); if (ok) { score++; ans.textContent = disp(w, marks()); toast('Correct — ' + w.rom + ' (' + w.en + ')'); k++; setTimeout(show, 900); } else { ans.classList.add('no'); setTimeout(() => ans.classList.remove('no'), 500); toast(typed.length !== bare(w.ur).length ? `${bare(w.ur).length} letters in this word` : 'Not yet. Listen again.'); } };
  skipB.onclick = () => { if (k >= items.length) return; toast('It was ' + items[k].w.v + ' — ' + items[k].w.rom); ctx.record('dictation', items[k].w.ur, false, 0); k++; setTimeout(show, 900); };
  const bar = el('div', 'row'); bar.append(playB, checkB, back, skipB, status); box.append(bar, ans, keys); show(); return box;
}

// 10-item check; 8 to pass.
export function quiz(unit, ctx, marks, onDone) {
  const qwords = unit.words.map(W).filter(w => spellable(unit, w.ur)); if (qwords.length < 4) return null;
  const box = el('div', 'card'); box.innerHTML = '<h2>Check</h2><p class="muted">Score 8 of 10 to pass this unit.</p>';
  const ol = el('ol'); ol.style.cssText = 'padding-left:18px;display:grid;gap:12px;margin:0'; const qs = shuffle(qwords).slice(0, 10); const picks = {};
  qs.forEach((w, qi) => { const li = el('li', '', `Which one says <b>${w.rom}</b> (${w.en})?`); const ch = el('div', 'choices'); ch.style.justifyContent = 'flex-start'; shuffle([w, ...shuffle(qwords.filter(x => x.ur !== w.ur)).slice(0, 3)]).forEach(o => { const t = el('button', 'tile small ur', disp(o, marks())); t.setAttribute('aria-label', o.rom); t.onclick = () => { [...ch.children].forEach(c => c.classList.remove('ok')); t.classList.add('ok'); picks[qi] = o.ur; }; ch.append(t); }); li.append(ch); ol.append(li); });
  const submit = el('button', 'btn btn-primary btn-wide', 'Submit'), res = el('div', 'score');
  submit.onclick = () => { let sc = 0; qs.forEach((w, qi) => { const ok = picks[qi] === w.ur; if (ok) sc++; ctx.record('quiz', w.ur, ok, 0); [...ol.children[qi].querySelectorAll('.tile')].forEach(t => { const right = t.textContent === disp(w, marks()); t.classList.toggle('ok', right); if (!right && t.classList.contains('ok') === false && picks[qi] && t.textContent === disp(qwords.find(x => x.ur === picks[qi]) || {}, marks())) t.classList.add('no'); }); });
    const missed = qs.filter((w, qi) => picks[qi] !== w.ur).map(w => w.rom).slice(0, 4).join(', '); res.textContent = `Score ${sc}/10 ${sc >= 8 ? '— passed ✓' : '— re-read ' + missed + ', then try again'}`; onDone && onDone(sc, 10); };
  box.append(ol, submit, res); return box;
}
