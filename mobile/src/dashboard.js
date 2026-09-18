// Progress dashboard shared by the learner's Progress tab and the teacher's per-child detail.
// Letter mastery grid (Leitner box), drill accuracy over 14 days, weakest items, 28-day activity, speed history, assessments.
import { db } from './db.js';
import { C, el, bandFor, PRP } from './content.js';
import * as S from './session.js';

const DAY = 86400000;
export async function renderDashboard(profileId, opts = {}) {
  const wrap = el('div');
  const [cards, attempts, p, assessments, sessions] = await Promise.all([db.by('cards', 'profileId', profileId), db.by('attempts', 'profileId', profileId), S.getProgress(profileId), db.by('assessments', 'profileId', profileId), db.by('sessions', 'profileId', profileId)]);
  const s = await S.stats(profileId);
  // summary row
  const sum = el('div', 'card'); sum.innerHTML = [['Units passed', `${s.unitsPassed} / 13`], ['Letters solid', `${s.lettersMastered} / ${s.letters}`], ['Words solid', `${s.wordsMastered} / ${s.words}`], ['Sessions', s.sessions], ['Cards due', s.due]].map(([k, v]) => `<div class="row" style="justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line)"><span>${k}</span><b>${v}</b></div>`).join(''); wrap.append(sum);
  // letter mastery grid
  const byItem = Object.fromEntries(cards.map(c => [c.item, c]));
  const grid = el('div', 'card'); grid.innerHTML = '<h2>Letters</h2><p class="muted">Grey not yet taught · red new or missed · amber learning · green solid (remembered 3+ times spaced)</p>';
  const g = el('div', 'choices'); g.style.justifyContent = 'flex-start';
  C.letters.letters.forEach(l => { const c = byItem[l.ch]; const box = c ? c.box : 0; const t = el('span', 'tile small ur', l.ch); t.style.cssText = `min-width:44px;padding:4px 8px;cursor:default;border-color:${!c ? 'var(--line)' : box <= 1 ? 'var(--bad)' : box < 4 ? 'var(--warn)' : 'var(--good)'};opacity:${c ? 1 : .45}`; t.title = `${l.name}${c ? ` · box ${box} · seen ${c.seen}` : ' · not yet taught'}`; t.setAttribute('aria-label', t.title); g.append(t); });
  grid.append(g); wrap.append(grid);
  // drill accuracy, last 14 days
  const recent = attempts.filter(a => a.ts > Date.now() - 14 * DAY); const drills = ['tell', 'join', 'read', 'trace', 'dictation', 'quiz', 'sight'];
  const acc = el('div', 'card'); acc.innerHTML = '<h2>Drill accuracy · last 14 days</h2>';
  const rows = drills.map(d => { const xs = recent.filter(a => a.drill === d); return [d, xs.length, xs.filter(a => a.correct).length]; }).filter(r => r[1]);
  acc.innerHTML += rows.length ? `<div class="table"><table><tr><th>Drill</th><th>Tries</th><th>Right</th><th></th></tr>${rows.map(([d, n, r]) => `<tr><td>${{ tell: 'Tell apart', join: 'Build word', read: 'Read', trace: 'Trace', dictation: 'Dictation', quiz: 'Check', sight: 'Sight words' }[d] || d}</td><td>${n}</td><td>${Math.round(100 * r / n)}%</td><td style="min-width:90px"><div class="progress"><i style="width:${Math.round(100 * r / n)}%"></i></div></td></tr>`).join('')}</table></div>` : '<p class="muted">No drills in the last two weeks.</p>';
  wrap.append(acc);
  // weakest items
  const miss = {}; attempts.filter(a => !a.correct && a.ts > Date.now() - 28 * DAY).forEach(a => { miss[a.item] = (miss[a.item] || 0) + 1; });
  const weak = Object.entries(miss).sort((a, b) => b[1] - a[1]).slice(0, 8);
  if (weak.length) { const w = el('div', 'card'); w.innerHTML = '<h2>Needs work</h2><p class="muted">Most-missed items in the last four weeks. Tap to hear.</p>'; const row = el('div', 'choices'); row.style.justifyContent = 'flex-start'; weak.forEach(([item, n]) => { const t = el('button', 'tile small ur', item); t.title = `${n} misses`; t.setAttribute('aria-label', `${item}, ${n} misses`); t.onclick = () => { const c = byItem[item]; if (c) import('./content.js').then(m => m.play(S.audioKeyFor(c))); }; const tag = el('span', 'pill', String(n)); tag.style.cssText = 'position:relative;left:-10px;top:-8px'; row.append(t, tag); }); w.append(row); wrap.append(w); }
  // activity, last 28 days
  const act = el('div', 'card'); act.innerHTML = '<h2>Activity · last 4 weeks</h2>'; const cal = el('div', 'row'); cal.style.gap = '4px'; const days = [...Array(28).keys()].map(i => { const d0 = new Date(); d0.setHours(0, 0, 0, 0); return d0.getTime() - (27 - i) * DAY; });
  const perDay = days.map(d => sessions.filter(x => x.startedAt >= d && x.startedAt < d + DAY).length);
  perDay.forEach((n, i) => { const dot = el('span', '', ''); dot.style.cssText = `width:18px;height:18px;border-radius:4px;background:${n ? 'var(--accent)' : 'var(--line)'};opacity:${n ? Math.min(1, .5 + n * .25) : 1}`; dot.title = `${new Date(days[i]).toLocaleDateString()}: ${n} session${n === 1 ? '' : 's'}`; cal.append(dot); });
  act.append(cal, el('p', 'muted', `${perDay.filter(Boolean).length} active days of 28`)); wrap.append(act);
  // speed
  if (s.wpm.length) { const w = el('div', 'card'); w.innerHTML = '<h2>Reading speed</h2>'; const mx = Math.max(60, ...s.wpm.map(x => x.wpm)); const best = Math.max(...s.wpm.map(x => x.wpm)); const gg = el('div', 'row'); gg.style.alignItems = 'flex-end'; gg.style.height = '120px'; s.wpm.slice(-20).forEach(x => { const b = el('div', '', ''); b.style.cssText = `width:14px;height:${Math.max(4, x.wpm / mx * 110)}px;background:${x.wpm === best ? 'var(--good)' : 'var(--accent)'};border-radius:4px`; b.title = `${x.wpm} wpm`; gg.append(b); }); const line = el('div', '', ''); line.style.cssText = `border-top:1px dashed var(--muted);margin-top:-${Math.round(60 / mx * 110)}px;position:relative;pointer-events:none`; w.append(gg, el('div', 'muted', `latest ${s.wpm[s.wpm.length - 1].wpm} wpm · best ${best} · 60 meets the grade-2 standard (${PRP(s.wpm[s.wpm.length - 1].wpm)})`)); wrap.append(w); }
  // assessments
  if (assessments.length) { const a = el('div', 'card'); a.innerHTML = '<h2>Assessments</h2>'; const t = el('div', 'table'); t.innerHTML = `<table><tr><th>Date</th><th>By</th><th>Letters</th><th>Nonwords</th><th>Words</th><th>Passage</th><th>Comp.</th><th>Level</th></tr>${assessments.sort((x, y) => y.ts - x.ts).slice(0, 6).map(x => `<tr><td>${new Date(x.ts).toLocaleDateString()}</td><td>${x.by}</td><td>${x.letters ?? '-'}</td><td>${x.nonwords ?? '-'}</td><td>${x.words ?? '-'}</td><td>${x.orf?.cwpm ?? '-'}</td><td>${x.comp ?? '-'}</td><td><span class="pill ${x.band}">${x.band}</span></td></tr>`).join('')}</table>`; a.append(t); wrap.append(a); }
  return wrap;
}
