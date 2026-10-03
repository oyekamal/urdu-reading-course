// Drill engines, ported from the course app. Each returns a DOM node and reports results via ctx.record(drill, item, correct, ms).
import { C, play, forms, W, shuffle, wordKey, taughtBefore, STROKE, dotInfo, soundOf, el, toast } from './content.js';
import { icon } from './icons.js';

export const formsOf = l => forms(l);
// Words a learner can spell with letters taught so far (plus hamza forms from unit 10). Preview words stay in Read only.
export const EXTRA10 = ['ء', 'ئ', 'ؤ', 'آ', 'ۃ'];
export const known = unit => new Set([...[...taughtBefore(unit.n), ...unit.letters].filter(c => C.by[c]), '\u0640', ...(unit.n >= 10 ? EXTRA10 : [])]);
export const spellable = (unit, ur) => { const k = known(unit); return [...ur].every(c => k.has(c) || /[\u064B-\u0652\u0670]/.test(c)); };
export const cue = ok => { if (document.body.dataset.track === 'child') setTimeout(() => play(ok ? 'ui/correct' : 'ui/wrong'), ok ? 250 : 900); };
export const strokeHint = l => STROKE[l.family] || 'body first in one stroke, right to left; dots last';
export function playBtn(key, small) { const b = el('button', 'btn btn-play' + (small ? ' small' : ''), icon('speaker')); b.setAttribute('aria-label', 'Play'); b.onclick = e => { e.stopPropagation(); if (!play(key)) toast('No audio for this item'); }; return b; }
// THE audio control: one big round speaker button, placed directly above the tiles it asks about (or next to the item it says).
export function sayBtn(fn, label = 'Play again') { const b = el('button', 'btn btn-play btn-say', icon('speaker')); b.setAttribute('aria-label', label); b.onclick = e => { e.stopPropagation(); fn(); }; return b; }
export const sayRow = (...kids) => { const r = el('div', 'say-row'); r.append(...kids.filter(Boolean)); return r; };
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
  const status = el('div', 'score'), choices = el('div', 'choices'); let round = 0, score = 0, target, t0; const btn = sayBtn(() => next(), 'Play sound'); const again = el('button', 'btn btn-chip', 'Again'); again.style.display = 'none'; again.onclick = () => { round = 0; score = 0; again.style.display = 'none'; btn.style.display = ''; next(); };
  function next() {
    if (round >= rounds) { status.textContent = `Done: ${score}/${rounds}`; choices.innerHTML = ''; btn.style.display = 'none'; again.style.display = ''; onDone && onDone(score, rounds); return; }
    round++; target = opts.letters && Math.random() < 0.6 ? focus[Math.floor(Math.random() * focus.length)] : pool[Math.floor(Math.random() * pool.length)]; status.textContent = `Round ${round}/${rounds} · ${score} right`;
    choices.innerHTML = ''; shuffle([target, ...shuffle(pool.filter(c => c !== target)).slice(0, 5)]).forEach(c => { const t = el('button', 'tile ur', c); t.setAttribute('aria-label', C.by[c].name); if (c === target) t.dataset.right = 'names/' + C.by[c].id; t.onclick = () => { const ok = c === target; ctx.record('tell', target, ok, Date.now() - t0); if (ok) { t.classList.add('ok'); t.setAttribute('aria-label', C.by[c].name + ', correct'); score++; toast('Correct: ' + C.by[c].name); cue(true); setTimeout(next, 450); } else { t.classList.add('no'); t.setAttribute('aria-label', C.by[c].name + ', wrong'); cue(false); }   /* the kind hint + replaying the right sound live in feel.js (answer help) */ }; choices.append(t); });
    t0 = Date.now(); play('names/' + C.by[target].id); btn.setAttribute('aria-label', 'Play again'); btn.onclick = e => { e.stopPropagation(); play('names/' + C.by[target].id); };
  }
  box.append(sayRow(btn, status, again), choices); shuffle(pool).slice(0, 6).forEach(c => { const t = el('button', 'tile ur', c); t.setAttribute('aria-label', C.by[c].name); t.onclick = next; choices.append(t); }); return box;
}

// Tap-what-you-hear options for a consonant+vowel blend (unit blends, any similar drill): `all` = [{ L, sy }], target one of them.
// ض ظ ذ say the same /z/, ث س ص the same /s/, ت ط, ح ہ, ع ا likewise: a round never shows two options that sound alike
// (distractors with the target's sound are dropped, and so are repeats of one sound among the distractors).
export function blendOptions(all, target, n = 4) {
  const snd = x => soundOf(x.L.ch) + x.sy[0]; const out = [];
  for (const x of shuffle(all.filter(y => y !== target))) { if (out.length >= n - 1) break; if (snd(x) !== snd(target) && !out.some(o => snd(o) === snd(x))) out.push(x); }
  return shuffle([target, ...out]);
}
// Placement stage for one unit: EVERY letter of the unit once (drawn without replacement, six tiles each) plus one word to read.
// The learner passes the stage only with every item right, so a learner who misses one letter passes ~1 time in 6 (the guess).
export function placementItems(unit, pool, marks = () => false) {
  const items = shuffle(unit.letters.filter(c => C.by[c])).map(c => ({ kind: 'letter', target: c, audio: 'names/' + C.by[c].id, options: shuffle([c, ...shuffle(pool.filter(x => x !== c)).slice(0, 5)]).map(x => ({ text: x, label: C.by[x].name, right: x === c })) }));
  const ws = unit.words.map((w, i) => ({ w: W(w), i })).filter(x => spellable(unit, x.w.ur)); if (ws.length < 2) return items;
  const t = ws[Math.floor(Math.random() * ws.length)], len = x => bare(x.w.ur).length;
  const ds = shuffle(ws.filter(x => x !== t && x.w.ur !== t.w.ur)).sort((a, b) => Math.abs(len(a) - len(t)) - Math.abs(len(b) - len(t))).slice(0, 3);
  items.push({ kind: 'word', target: t.w.ur, audio: wordKey(unit.n, t.i + (unit.wordOffset || 0)), options: shuffle([t, ...ds]).map(x => ({ text: marks() ? x.w.v : x.w.ur, label: x.w.rom, right: x === t })) });
  return items;
}

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

// round 9c: glowing ink. The visible stroke lives on an overlay canvas (cv itself stays the static glyph and a hidden logic
// canvas keeps the old hard 14px stroke, so the coverage check is unchanged). Finger positions are low-pass smoothed and drawn as
// quadratic curves through midpoints (calligraphy, no corners); width thins with finger speed. Glow = layered uniform-alpha passes
// (no shadowBlur, cheap). Sparkles trail the fingertip, a ring pops when a stroke ends, a gold band sweeps the finished letter.
function inkPad(cv) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches, dpr = Math.min(2, window.devicePixelRatio || 1), W = 360, H = 300;
  cv.width = W * dpr; cv.height = H * dpr; const g = cv.getContext('2d');
  const sh = document.createElement('canvas'); sh.width = W; sh.height = H; const sc = sh.getContext('2d'); let mask = null;
  let strokes = [], cur = null, parts = [], pops = [], shim = 0, raf = 0, tip = null;
  const path = (c, p) => { c.beginPath(); c.moveTo(p[0].x, p[0].y); for (let i = 1; i < p.length - 1; i++) c.quadraticCurveTo(p[i].x, p[i].y, (p[i].x + p[i + 1].x) / 2, (p[i].y + p[i + 1].y) / 2); const l = p[p.length - 1]; c.lineTo(l.x, l.y); };
  const star = (c, x, y, r) => { c.beginPath(); c.moveTo(x, y - r); c.quadraticCurveTo(x, y, x + r, y); c.quadraticCurveTo(x, y, x, y + r); c.quadraticCurveTo(x, y, x - r, y); c.quadraticCurveTo(x, y, x, y - r); c.fill(); };
  function spark(x, y, n, spread, up) { if (reduce) return; for (let i = 0; i < n && parts.length < 30; i++) { const a = Math.random() * 6.283, s = Math.random() * spread; parts.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - up, r: 3 + Math.random() * 4, t: 0, life: 520 + Math.random() * 380, c: i % 3 === 0 ? '#fff' : i % 3 === 1 ? '#F2A93B' : '#5EE0D0' }); } }
  function draw(now) {
    g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H); g.lineCap = g.lineJoin = 'round';
    for (const s of strokes.concat(cur ? [cur] : [])) { const p = s.pts; if (!p.length) continue;
      if (p.length < 2) { g.fillStyle = 'rgba(242,169,59,.25)'; g.beginPath(); g.arc(p[0].x, p[0].y, 17, 0, 7); g.fill(); g.fillStyle = '#17A79A'; g.beginPath(); g.arc(p[0].x, p[0].y, 8, 0, 7); g.fill(); continue; }
      path(g, p); for (const [w, c] of [[38, 'rgba(242,169,59,.15)'], [29, 'rgba(242,169,59,.22)'], [22, 'rgba(94,224,208,.32)']]) { g.lineWidth = w; g.strokeStyle = c; g.stroke(); }
      g.strokeStyle = '#17A79A'; for (let i = 1; i < p.length; i++) { const a = i > 1 ? { x: (p[i - 1].x + p[i].x) / 2, y: (p[i - 1].y + p[i].y) / 2 } : p[0], b = i < p.length - 1 ? { x: (p[i].x + p[i + 1].x) / 2, y: (p[i].y + p[i + 1].y) / 2 } : p[i]; g.lineWidth = p[i].w; g.beginPath(); g.moveTo(a.x, a.y); g.quadraticCurveTo(p[i].x, p[i].y, b.x, b.y); g.stroke(); }
      path(g, p); g.lineWidth = 3.2; g.strokeStyle = 'rgba(214,255,250,.7)'; g.stroke(); }
    if (shim && mask) { const k = (now - shim) / 950; if (k >= 1) shim = 0; else { sc.globalCompositeOperation = 'source-over'; sc.clearRect(0, 0, W, H); const x = -90 + k * (W + 180), gr = sc.createLinearGradient(x - 95, 0, x + 95, 110); gr.addColorStop(0, 'rgba(255,240,190,0)'); gr.addColorStop(.5, 'rgba(255,252,235,1)'); gr.addColorStop(1, 'rgba(255,240,190,0)'); sc.fillStyle = gr; sc.fillRect(0, 0, W, H); sc.globalCompositeOperation = 'destination-in'; sc.drawImage(mask, 0, 0); g.drawImage(sh, 0, 0, W, H); } }
    for (const q of pops) { const k = (now - q.t0) / 300; if (k < 1) { g.strokeStyle = `rgba(242,169,59,${.65 * (1 - k)})`; g.lineWidth = 3 * (1 - k) + 1; g.beginPath(); g.arc(q.x, q.y, 8 + 22 * (1 - Math.pow(1 - k, 3)), 0, 7); g.stroke(); } }
    pops = pops.filter(q => now - q.t0 < 300);
    for (const q of parts) { q.t += 16; q.x += q.vx; q.y += q.vy; q.vy += .02; q.vx *= .97; const k = q.t / q.life; g.globalAlpha = Math.max(0, 1 - k); g.fillStyle = q.c; star(g, q.x, q.y, q.r * (1 - k * .5)); } g.globalAlpha = 1; parts = parts.filter(q => q.t < q.life);
    if (tip && !reduce) { const r = 13 + Math.sin(now / 140) * 2; const gr = g.createRadialGradient(tip.x, tip.y, 0, tip.x, tip.y, r + 8); gr.addColorStop(0, 'rgba(255,255,255,.95)'); gr.addColorStop(.35, 'rgba(255,214,120,.7)'); gr.addColorStop(1, 'rgba(242,169,59,0)'); g.fillStyle = gr; g.beginPath(); g.arc(tip.x, tip.y, r + 8, 0, 7); g.fill(); }
  }
  const loop = now => { draw(now); raf = (parts.length || pops.length || shim || tip) ? requestAnimationFrame(loop) : 0; };
  const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };
  return {
    reset(m) { strokes = []; cur = null; parts = []; pops = []; shim = 0; tip = null; mask = null; if (m) { mask = document.createElement('canvas'); mask.width = W; mask.height = H; mask.getContext('2d').putImageData(new ImageData(new Uint8ClampedArray(m), W, H), 0, 0); } draw(performance.now()); },
    down(x, y) { cur = { pts: [{ x, y, w: 15 }], sx: x, sy: y, vw: 15, n: 0 }; tip = { x, y }; spark(x, y, 3, 1.2, .3); kick(); },
    move(x, y, dt) { if (!cur) return; const p = cur.pts[cur.pts.length - 1]; cur.sx += (x - cur.sx) * .42; cur.sy += (y - cur.sy) * .42; const d = Math.hypot(cur.sx - p.x, cur.sy - p.y); if (d < 1.6) return; cur.vw += (Math.max(9, Math.min(19, 20 - (d / Math.max(4, dt)) * 5)) - cur.vw) * .25; cur.pts.push({ x: cur.sx, y: cur.sy, w: cur.vw }); tip = { x: cur.sx, y: cur.sy }; if (++cur.n % 2 === 0) spark(cur.sx, cur.sy, 1, 1.1, .35); kick(); },
    up() { if (!cur) return; const l = cur.pts[cur.pts.length - 1]; strokes.push(cur); cur = null; tip = null; if (!reduce) { pops.push({ x: l.x, y: l.y, t0: performance.now() }); spark(l.x, l.y, 7, 2.2, .4); } kick(); draw(performance.now()); },
    shimmer() { if (reduce || !mask) return; shim = performance.now(); kick(); },
  };
}

// ---- tracing judge (round 11d): direction + order on top of coverage. Pure function, tested with synthetic strokes. ----
// strokes: [[ [x,y], ... ], ...] in canvas px; ref: RGBA of the grey glyph (alpha > 40 = ink); start: [x,y] of the green dot.
// Lenient on purpose (a six-year-old's finger): the start must be NEAR the dot, the one-stroke letters (alif, dal, re family, alone) must head
// the hinted way and get most of the way to the end, body before dots, a few lifts are fine, a smooth line is not needed but a scribble or a
// pile of dashes is not a letter. Every reply is kind: it says what to do, never "wrong".
const SINGLE = new Set(['alif', 'dal', 're']);
function resample(pts, step = 8) {
  if (pts.length < 2) return pts.slice(); const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const total = cum[cum.length - 1]; if (total < step) return [pts[0], pts[pts.length - 1]]; const out = []; let j = 1;
  for (let d = 0; d <= total; d += step) { while (j < cum.length - 1 && cum[j] < d) j++; const t = cum[j] === cum[j - 1] ? 0 : (d - cum[j - 1]) / (cum[j] - cum[j - 1]); out.push([pts[j - 1][0] + (pts[j][0] - pts[j - 1][0]) * t, pts[j - 1][1] + (pts[j][1] - pts[j - 1][1]) * t]); }
  const l = pts[pts.length - 1]; if (Math.hypot(out[out.length - 1][0] - l[0], out[out.length - 1][1] - l[1]) > 1) out.push(l); return out;
}
function smooth(pts, w = 3) { return pts.map((p, i) => { if (i === 0 || i === pts.length - 1) return p; let x = 0, y = 0, n = 0; for (let k = Math.max(0, i - w); k <= Math.min(pts.length - 1, i + w); k++) { x += pts[k][0]; y += pts[k][1]; n++; } return [x / n, y / n]; }); }
const plen = p => { let L = 0; for (let i = 1; i < p.length; i++) L += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); return L; };
function turning(p) { let T = 0, prev = null; for (let i = 2; i < p.length; i++) { const a = Math.atan2(p[i][1] - p[i - 2][1], p[i][0] - p[i - 2][0]); if (prev !== null) { let d = Math.abs(a - prev); if (d > Math.PI) d = 2 * Math.PI - d; T += d; } prev = a; } return T; }
// the biggest connected blob of the glyph (the body, not its dots) and its pixel farthest from the start dot (= where a one-stroke letter ends)
function bodyEnd(ref, W, H, start) {
  const n = W * H, lab = new Int32Array(n), sizes = [0]; let id = 0; const st = [];
  for (let i = 0; i < n; i++) { if (ref[i * 4 + 3] <= 40 || lab[i]) continue; id++; let size = 0; st.push(i); lab[i] = id;
    while (st.length) { const q = st.pop(); size++; const x = q % W, y = (q / W) | 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const nx = x + dx, ny = y + dy; if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue; const k = ny * W + nx; if (!lab[k] && ref[k * 4 + 3] > 40) { lab[k] = id; st.push(k); } } }
    sizes[id] = size; }
  let bestId = 1; for (let k = 1; k <= id; k++) if (sizes[k] > sizes[bestId]) bestId = k;
  let far = null, fd = -1; const body = [], marks = []; for (let i = 0; i < n; i += 3) { if (!lab[i]) continue; const x = i % W, y = (i / W) | 0; if (lab[i] === bestId) { body.push([x, y]); const d = (x - start[0]) ** 2 + (y - start[1]) ** 2; if (d > fd) { fd = d; far = [x, y]; } } else marks.push([x, y]); }
  return { far, body, marks };
}
// a stroke belongs to the body unless its centre sits nearer to a dot/tah/hamza than to the body (position, not length: a squiggled dot or a lifted body piece both work)
const nearest = (pts, c) => { let d = 1e9; for (const p of pts) { const e = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2; if (e < d) d = e; } return d; };
export function judgeTrace({ strokes, ref, W = 360, H = 300, start, ch, form = 'isolated' }) {
  const L = C.by[ch]; if (!L || !ref || !start) return { ok: true, msg: '' };
  const raw = strokes.filter(s => s.length); if (!raw.length) return { ok: false, msg: 'Trace the letter with your finger' };
  let minx = W, maxx = 0, top = H, bot = 0; for (let i = 3; i < ref.length; i += 4) if (ref[i] > 40) { const x = (i >> 2) % W, y = (i >> 2) / W | 0; if (x < minx) minx = x; if (x > maxx) maxx = x; if (y < top) top = y; if (y > bot) bot = y; }
  const gw = maxx - minx, gh = bot - top, di = dotInfo(ch, form), marks = di.n + (di.mark ? 1 : 0) + (ch === 'گ' || ch === 'ک' ? 1 : 0);
  const sm = raw.map(s => smooth(resample(s))), len = sm.map(plen);
  const m = { strokes: raw.length, marks, len: len.map(Math.round) };
  // a pile of dashes, or a scribble, is not a letter
  if (raw.length > 1 + marks + 3 || sm.some(p => turning(p) > 14)) return { ok: false, msg: 'Try one smooth line, from the green dot', m };
  let be = null, es = start; if (SINGLE.has(L.family)) { be = bodyEnd(ref, W, H, start); let bd = 1e18; for (const q of be.body) { const d = (q[0] - start[0]) ** 2 + (q[1] - start[1]) ** 2; if (d < bd) { bd = d; es = q; } } }   // single-stroke letters start on the BODY: the green dot may sit on a tah/dot above it
  const s0 = raw[0][0], near = Math.hypot(s0[0] - es[0], s0[1] - es[1]) <= (SINGLE.has(L.family) ? 80 : 95) || (!SINGLE.has(L.family) && s0[0] >= minx + gw * 0.5);
  if (!near) return { ok: false, msg: 'Start at the green dot', m };
  // body before dots: a first stroke that is only a dot, when a real stroke follows
  const mx = Math.max(...len); if (marks && raw.length > 1 && len[0] < mx * 0.25 && mx > 40) return { ok: false, msg: 'Body first, then the dots', m };
  if (SINGLE.has(L.family) && form === 'isolated') {
    // the body is every stroke that is not a little dot-sized one, in order (a child may lift once or twice); together they must start at the
    // dot end, never go backwards, and get most of the way to the far end of the letter
    let end = es, fd = -1; for (const q of be.body) { const d = (q[0] - es[0]) ** 2 + (q[1] - es[1]) ** 2; if (d > fd) { fd = d; end = q; } }
    const vx = end[0] - es[0], vy = end[1] - es[1], vv = vx * vx + vy * vy || 1, proj = p => ((p[0] - es[0]) * vx + (p[1] - es[1]) * vy) / vv;
    const isBody = (p, i) => { if (!be.marks.length) return true; const c = raw[i].reduce((a, q) => [a[0] + q[0] / raw[i].length, a[1] + q[1] / raw[i].length], [0, 0]); return nearest(be.body, c) <= nearest(be.marks, c); };
    const main = sm.filter(isBody); if (!main.length) return { ok: false, msg: 'Start at the green dot and follow the arrow', m };
    const a = proj(main[0][0]); let hi = a, back = false; for (const q of main) { if (proj(q[0]) < hi - 0.3) back = true; for (const pt of q) hi = Math.max(hi, proj(pt)); }
    const z = proj(main[main.length - 1][main[main.length - 1].length - 1]); m.proj = [+a.toFixed(2), +hi.toFixed(2), +z.toFixed(2)];
    if (a > 0.45 || back || hi < 0.6) return { ok: false, msg: a > 0.45 || back ? 'Start at the green dot and follow the arrow' : 'Keep going to the end of the letter', m };
  }
  return { ok: true, msg: '', m };
}

// Tracing: grey glyph, finger stroke, start-side + coverage + stroke-count feedback.
export function writeIt(unit, ctx, styleName, onDone, letters) {
  const ls = (letters || unit.letters).map(c => C.by[c]).filter(Boolean); if (!ls.length) return null;
  const box = el('div', 'card'); box.innerHTML = '<h2>Trace</h2><p class="muted">Start at the green dot. Body first, dots last.</p>';
  const sel = { value: ls[0].ch, onchange: null }, formSel = { value: 'isolated', onchange: null }, cv = el('canvas', 'trace'), out = el('div', 'score trace-out'), clear = el('button', 'btn trace-clear', `${icon('repeat')}<span>Clear</span>`), check = el('button', 'btn btn-check', `${icon('check')}<span>Check</span>`);
  out.setAttribute('aria-live', 'polite');
  cv.width = 360; cv.height = 300; const ctx2 = cv.getContext('2d', { willReadFrequently: true }); const lg = document.createElement('canvas'); lg.width = 360; lg.height = 300; const lc = lg.getContext('2d', { willReadFrequently: true }), inkCv = el('canvas', 'trace-ink'), wrap = el('div', 'trace-wrap'), pad = inkPad(inkCv); wrap.append(cv, inkCv); let tPrev = 0; let ref = null, drawing = false, startX = null, glyphBox = null, strokes = 0, good = 0, sp = [], curS = null, startPt = null;
  const gl = (l, f) => { if (!l.joiner && (f === 'initial' || f === 'medial')) return null; return f === 'isolated' ? l.ch : f === 'initial' ? l.ch + 'ـ' : f === 'medial' ? 'ـ' + l.ch + 'ـ' : 'ـ' + l.ch; };
  const glyph = () => gl(C.by[sel.value], formSel.value);
  const startDot = el('i', 'trace-start'), arrow = el('i', 'trace-arrow', '<svg viewBox="0 0 40 24" aria-hidden="true"><path d="M36 12H6M15 4 5 12l10 8" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'); startDot.setAttribute('aria-hidden', 'true'); arrow.setAttribute('aria-hidden', 'true');
  // paper look: after the logic copy (lc) is taken, the visible canvas is repainted as a faint filled glyph with a dotted outline (logic untouched)
  function dressed(g, fam, dot) { ctx2.clearRect(0, 0, cv.width, cv.height); ctx2.direction = 'rtl'; ctx2.textAlign = 'center'; ctx2.textBaseline = 'middle'; ctx2.font = `170px ${fam}`; const acc = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#1E9C8F'; ctx2.fillStyle = acc; ctx2.globalAlpha = .1; ctx2.fillText(g, 180, 150); ctx2.globalAlpha = .75; ctx2.strokeStyle = acc; ctx2.lineWidth = 3; ctx2.lineCap = 'round'; ctx2.lineJoin = 'round'; ctx2.setLineDash([.1, 8]); ctx2.strokeText(g, 180, 150); ctx2.setLineDash([]); ctx2.globalAlpha = 1;
    const hint = strokeHint(C.by[sel.value]), down = /top to bottom|top down(?!.*left)/.test(hint), dl = !down && /top down|sweep left/.test(hint) && /down/.test(hint); const x = dot[0] / 360 * 100, y = dot[1] / 300 * 100; startDot.style.cssText = `left:${x}%;top:${y}%`; arrow.style.cssText = `left:${down ? x : Math.max(8, x - 17)}%;top:${down ? Math.min(92, y + 17) : y}%`; arrow.dataset.dir = down ? 'down' : dl ? 'downleft' : 'left'; wrap.dataset.on = '1'; }
  function base() { wrap.classList.remove('inked'); ctx2.clearRect(0, 0, cv.width, cv.height); const g = glyph(); out.textContent = ''; out.className = 'score trace-out'; strokes = 0; startX = null; sp = []; curS = null; if (!g) { ctx2.fillStyle = '#888'; ctx2.font = '16px sans-serif'; ctx2.textAlign = 'center'; ctx2.fillText('This letter has no such form', 180, 150); ref = null; delete wrap.dataset.on; lc.clearRect(0, 0, 360, 300); lc.drawImage(cv, 0, 0); pad.reset(null); return; }
    const fam = styleName() === 'nastaliq' ? '"Noto Nastaliq Urdu"' : '"Noto Naskh Arabic"'; ctx2.fillStyle = getComputedStyle(document.body).getPropertyValue('--line'); ctx2.font = `170px ${fam}`; ctx2.textAlign = 'center'; ctx2.textBaseline = 'middle'; ctx2.direction = 'rtl'; ctx2.fillText(g, 180, 150); ref = ctx2.getImageData(0, 0, cv.width, cv.height).data;
    let minx = cv.width, maxx = 0, top = cv.height; for (let i = 3; i < ref.length; i += 4) if (ref[i] > 0) { const x = (i >> 2) % cv.width, y = (i >> 2) / cv.width | 0; if (x < minx) minx = x; if (x > maxx) maxx = x; if (x > maxx - 6 && y < top) top = y; }
    startPt = [Math.min(maxx + 10, cv.width - 8), Math.min(top + 20, cv.height - 10)]; glyphBox = [minx, maxx]; ctx2.fillStyle = getComputedStyle(document.body).getPropertyValue('--accent'); ctx2.beginPath(); ctx2.arc(Math.min(maxx + 10, cv.width - 8), Math.min(top + 20, cv.height - 10), 6, 0, 7); ctx2.fill(); lc.clearRect(0, 0, 360, 300); lc.drawImage(cv, 0, 0); pad.reset(ref); dressed(g, fam, [Math.min(maxx + 10, cv.width - 8), Math.min(top + 20, cv.height - 10)]); }
  const pos = e => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * cv.width / r.width, (e.clientY - r.top) * cv.height / r.height]; };
  cv.onpointerdown = e => { wrap.classList.add('inked'); drawing = true; strokes++; const q = pos(e); curS = [q]; sp.push(curS); if (startX === null) startX = q[0]; lc.beginPath(); lc.moveTo(...q); cv.setPointerCapture(e.pointerId); tPrev = e.timeStamp; pad.down(...q); };
  cv.onpointermove = e => { if (!drawing) return; lc.strokeStyle = getComputedStyle(document.body).getPropertyValue('--accent'); lc.lineWidth = styleName() === 'nastaliq' ? 28 : 20; lc.lineCap = 'round'; lc.lineJoin = 'round'; for (const ev of (e.getCoalescedEvents?.() || [e])) { const q = pos(ev); if (curS) curS.push(q); lc.lineTo(...q); lc.stroke(); pad.move(q[0], q[1], Math.max(1, ev.timeStamp - tPrev)); tPrev = ev.timeStamp; } };
  cv.onpointerup = cv.onpointercancel = () => { if (drawing) { pad.up(); if (curS && curS.length === 1) { lc.fillStyle = getComputedStyle(document.body).getPropertyValue('--accent'); lc.beginPath(); lc.arc(curS[0][0], curS[0][1], 22, 0, 7); lc.fill(); } } drawing = false; };   /* a tap is a dot: it must count on the logic canvas like a drawn stroke */
  check.onclick = () => { if (!ref) return; const now = lc.getImageData(0, 0, cv.width, cv.height).data; let g = 0, hit = 0, stray = 0; for (let i = 0; i < ref.length; i += 4) { const isG = ref[i + 3] > 0 && ref[i] > 150; const drawn = Math.abs(now[i] - ref[i]) > 40 || Math.abs(now[i + 1] - ref[i + 1]) > 40 || (now[i + 3] > 0 && ref[i + 3] === 0); if (isG) { g++; if (drawn) hit++; } else if (drawn) stray++; }
    const di0 = dotInfo(C.by[sel.value].ch, formSel.value); const cov = Math.round(100 * hit / Math.max(1, g)), neat = stray < g * 0.8 + (1500 + 700 * (di0.n + (di0.mark ? 1 : 0))) * (styleName() === 'nastaliq' ? 2 : 1);   /* +1500: a thin letter (alif) must forgive a wobbly finger; scribbles and dashes are caught by judgeTrace */ const l = C.by[sel.value]; const di = dotInfo(l.ch, formSel.value); const expect = 1 + di.n + (di.mark ? 1 : 0) + (l.ch === 'گ' || l.ch === 'ک' ? 1 : 0);
    // direction and order (judgeTrace) only matter once the letter is covered: low coverage keeps the old "keep tracing"
    const v = cov >= 80 && neat ? judgeTrace({ strokes: sp, ref, start: startPt, ch: l.ch, form: formSel.value }) : { ok: false, msg: '' };
    const ok = cov >= 80 && neat && v.ok; out.textContent = `Coverage ${cov}% ${ok ? '✓ good' : cov < 80 ? '— keep tracing' : !neat ? '— stay inside the letter' : '— ' + v.msg}${ok && strokes > expect + 1 ? ` · ${strokes} strokes, aim for ${expect}` : ''}`; out.className = 'score trace-out ' + (ok ? 'ok' : 'try'); ctx.record('trace', l.ch, ok, 0); if (ok) pad.shimmer(); if (ok && ++good >= 1 && onDone) onDone(good, 1); };
  wrap.append(startDot, arrow); clear.onclick = base; sel.onchange = formSel.onchange = base; box.classList.add('trace-card');
  // chips instead of native selects (same state objects: sel.value / formSel.value). One letter given (lesson flow) = no pickers, the card is just the pad.
  const FORMS = [['isolated', 'Alone'], ['initial', 'Start'], ['medial', 'Middle'], ['final', 'End']], pick = el('div', 'trace-pick');
  const letterRow = el('div', 'trace-letters'), posRow = el('div', 'trace-pos'); letterRow.setAttribute('role', 'group'); letterRow.setAttribute('aria-label', 'Letter'); posRow.setAttribute('role', 'group'); posRow.setAttribute('aria-label', 'Position in the word');
  const lchips = ls.map(l => { const b = el('button', 'btn btn-chip tchip', `<span class="ur">${l.ch}</span><small>${l.name}</small>`); b.setAttribute('aria-label', l.name); b.onclick = () => { sel.value = l.ch; sync(); sel.onchange(); }; letterRow.append(b); return b; });
  const pchips = FORMS.map(([f, label]) => { const b = el('button', 'btn btn-chip tchip pchip'); b.setAttribute('aria-label', f); b.onclick = () => { formSel.value = f; sync(); formSel.onchange(); }; posRow.append(b); return b; });
  function sync() { const cur = C.by[sel.value]; lchips.forEach((b, i) => { const on = ls[i].ch === sel.value; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); }); pchips.forEach((b, i) => { const f = FORMS[i][0], g = gl(cur, f), on = f === formSel.value; b.classList.toggle('on', on); b.classList.toggle('na', !g); b.setAttribute('aria-pressed', on); b.innerHTML = `<span class="ur">${g || '–'}</span><small>${FORMS[i][1]}</small>`; }); }
  sync(); if (ls.length > 1) pick.append(letterRow); if (!letters || letters.length !== 1) pick.append(posRow); else box.classList.add('trace-solo');
  const acts = el('div', 'trace-actions'); acts.append(clear, check);
  box.append(...(pick.children.length ? [pick] : []), wrap, acts, out); setTimeout(base, 50); return box;
}

// Dictation with a letter keyboard limited to taught letters.
export function dictation(unit, ctx, marks, onDone) {
  if (unit.words.length < 5) return null;
  const box = el('div', 'card'); box.innerHTML = '<h2>Dictation</h2><p class="muted">Hear a word, spell it with the tiles.</p>';
  const keysAll = [...new Set([...taughtBefore(unit.n), ...unit.letters])].filter(c => C.by[c]);
  const ans = el('div', 'answer ur'), keys = el('div', 'keys'), status = el('div', 'score'), playB = sayBtn(() => {}, 'Play word'), checkB = el('button', 'btn btn-primary btn-wide act', 'Check'), back = el('button', 'btn', '⌫'), skipB = el('button', 'btn', 'Skip'), againB = el('button', 'btn btn-chip', 'Again'); back.setAttribute('aria-label', 'Erase'); againB.style.display = 'none';
  const pickable = unit.words.map((w, i) => ({ w: W(w), i })).filter(x => spellable(unit, x.w.ur)); if (pickable.length < 3) return null;
  let items = shuffle(pickable).slice(0, 5), k = 0, typed = '', score = 0, t0;
  [...keysAll, ...(unit.n >= 10 ? EXTRA10 : [])].forEach(c => { const t = el('button', 'tile ur', c); t.setAttribute('aria-label', C.by[c]?.name || c); t.onclick = () => { typed += c; ans.textContent = typed; }; keys.append(t); });
  back.onclick = () => { typed = [...typed].slice(0, -1).join(''); ans.textContent = typed; };
  const key = () => wordKey(unit.n, items[k].i + (unit.wordOffset || 0));
  function show() { if (k >= items.length) { checkB.disabled = true; skipB.disabled = true; back.disabled = true; status.textContent = `Done: ${score}/5`; playB.style.display = 'none'; againB.style.display = ''; checkB.style.display = 'none'; againB.onclick = () => { items = shuffle(pickable).slice(0, 5); k = 0; score = 0; checkB.disabled = false; skipB.disabled = false; back.disabled = false; playB.style.display = ''; againB.style.display = 'none'; checkB.style.display = ''; show(); }; onDone && onDone(score, 5); return; } typed = ''; ans.textContent = ''; t0 = Date.now(); status.textContent = `Word ${k + 1}/5 · ${score} right`; playB.onclick = e => { e.stopPropagation(); play(key()); }; play(key()); }
  checkB.onclick = () => { if (k >= items.length || checkB.dataset.wait) return; const w = items[k].w; const ok = typed === bare(w.ur); ctx.record('dictation', w.ur, ok, Date.now() - t0); if (ok) { score++; ans.textContent = disp(w, marks()); toast('Correct — ' + w.rom + ' (' + w.en + ')'); k++; checkB.dataset.wait = '1'; skipB.dataset.wait = '1'; setTimeout(() => { delete checkB.dataset.wait; delete skipB.dataset.wait; show(); }, 900); } else { ans.classList.add('no'); checkB.dataset.wait = '1'; setTimeout(() => { ans.classList.remove('no'); delete checkB.dataset.wait; }, 500); toast(typed.length !== bare(w.ur).length ? `${bare(w.ur).length} letters in this word` : 'Not yet. Listen again.'); } };
  skipB.onclick = () => { if (k >= items.length || skipB.dataset.wait) return; toast('It was ' + items[k].w.v + ' — ' + items[k].w.rom); ctx.record('dictation', items[k].w.ur, false, 0); k++; checkB.dataset.wait = '1'; skipB.dataset.wait = '1'; setTimeout(() => { delete checkB.dataset.wait; delete skipB.dataset.wait; show(); }, 900); };
  const bar = el('div', 'row'); bar.append(back, skipB); box.append(sayRow(playB, status, againB), ans, keys, bar, checkB); show(); return box;
}

// 10-item check; 8 to pass.
export function quiz(unit, ctx, marks, onDone) {
  const qwords = unit.words.map(W).filter(w => spellable(unit, w.ur)); if (qwords.length < 4) return null;
  const box = el('div', 'card'); box.innerHTML = '<h2>Check</h2><p class="muted">Score 8 of 10 to pass this unit.</p>';
  const ol = el('ol'); ol.style.cssText = 'padding-left:18px;display:grid;gap:12px;margin:0'; const qs = shuffle(qwords).slice(0, 10); const picks = {};
  qs.forEach((w, qi) => { const li = el('li', '', `Which one says <b>${w.rom}</b> (${w.en})?`); const ch = el('div', 'choices'); ch.style.justifyContent = 'flex-start'; shuffle([w, ...shuffle(qwords.filter(x => x.ur !== w.ur)).slice(0, 3)]).forEach(o => { const t = el('button', 'tile small ur', disp(o, marks())); t.setAttribute('aria-label', o.rom); t.onclick = () => { [...ch.children].forEach(c => c.classList.remove('ok')); t.classList.add('ok'); picks[qi] = o.ur; }; ch.append(t); }); li.append(ch); ol.append(li); });
  const submit = el('button', 'btn btn-primary btn-wide act', 'Submit'), res = el('div', 'score');
  submit.onclick = () => { if (submit.dataset.used) return; submit.dataset.used = '1'; let sc = 0; qs.forEach((w, qi) => { const ok = picks[qi] === w.ur; if (ok) sc++; ctx.record('quiz', w.ur, ok, 0); [...ol.children[qi].querySelectorAll('.tile')].forEach(t => { const right = t.textContent === disp(w, marks()); t.classList.toggle('ok', right); if (!right && t.classList.contains('ok') === false && picks[qi] && t.textContent === disp(qwords.find(x => x.ur === picks[qi]) || {}, marks())) t.classList.add('no'); }); });
    const missed = qs.filter((w, qi) => picks[qi] !== w.ur).map(w => w.rom).slice(0, 4).join(', '); res.textContent = `Score ${sc}/10 ${sc >= 8 ? '— passed ✓' : '— re-read ' + missed + ', then try again'}`; submit.remove(); res.scrollIntoView({ block: 'center' }); const done = () => Promise.resolve(onDone && onDone(sc, 10)).catch(() => { const r = el('button', 'btn btn-primary btn-wide', 'Try saving again'); r.onclick = () => { r.remove(); done(); }; box.append(el('p', 'muted', 'Your score did not save yet. Nothing is lost.'), r); }); done(); };
  box.append(ol, res, submit); return box;
}
