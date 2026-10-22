// Marko stories: 15 picture stories for beginners (img/mstory/stories.json, pictures img/mstory/, narration audio/mstory/, PDF per story in pdf/).
// A grid of covers; tap one to read it page by page (picture, vowelled Urdu, tap to hear, meaning on request); the last page offers the PDF to save or print.
import { el, play, toast } from './content.js';
import { icon } from './icons.js';
import { savePdf } from './practice.js';

let data = null, pdfs = null;
const load = async () => { if (!data) data = await fetch('img/mstory/stories.json').then(r => r.json()); return data; };
const pdfFor = async n => { try { if (!pdfs) pdfs = (await fetch('pdf/index.json').then(r => r.json())).items; } catch (e) { return null; } return pdfs.find(x => x.id === 'story_' + String(n).padStart(2, '0')); };
const img = (f, cls) => `<img class="${cls}" src="./img/mstory/${f}" alt="" decoding="async" loading="lazy">`;
const aud = (n, i) => `mstory/s${String(n).padStart(2, '0')}_p${i + 1}`;

// ctx: { st, render, header, cur } — st.storyN is the open story (null = the grid), st.storyP the page
export async function renderStories(main, ctx) {
  const { st, render } = ctx; const S = await load();
  if (st.storyN == null) {
    await ctx.header('Marko stories', 'Tap a story to read it. Marko is in every picture.');
    const g = el('div', 'mst-grid');
    S.forEach(s => { const b = el('button', 'mst-card' + (s.unit > ctx.cur ? ' later' : ''), `${img(s.cover, 'mst-cover')}<span class="mst-t ur">${s.title_ur}</span><span class="mst-e">${s.title_en}</span><span class="pill mst-u">Unit ${s.unit}</span>`);
      b.setAttribute('aria-label', `${s.title_en}, unit ${s.unit}`); b.onclick = () => { st.storyN = s.n; st.storyP = 0; render(); }; g.append(b); });
    main.append(g); return;
  }
  const s = S.find(x => x.n === st.storyN); if (!s) { st.storyN = null; return render(); }
  const last = s.pages.length, p = Math.min(Math.max(st.storyP || 0, 0), last);   // page `last` = the end page
  await ctx.header(s.title_en, `Unit ${s.unit} · page ${Math.min(p + 1, last)} of ${last}`);
  const card = el('div', 'card mst-page');
  if (p < last) {
    const pg = s.pages[p]; let shown = false;
    const say = el('button', 'btn btn-primary btn-wide mst-say', `${icon('speaker')} Hear it`); say.onclick = () => play(aud(s.n, p));
    const meaning = el('div', 'muted mst-mean'); meaning.hidden = true; meaning.innerHTML = `<div>${pg.r}</div><b>${pg.e}</b>`;
    const sb = el('button', 'btn btn-chip btn-center', 'Show meaning'); sb.onclick = () => { shown = !shown; meaning.hidden = !shown; sb.textContent = shown ? 'Hide meaning' : 'Show meaning'; };
    card.innerHTML = img(pg.img, 'mst-pic') + `<div class="ur big mst-ur" lang="ur" dir="rtl">${pg.v}</div>`; card.append(say, sb, meaning);
    setTimeout(() => { if (card.isConnected) play(aud(s.n, p)); }, 350);
  } else {
    card.classList.add('mst-end'); card.innerHTML = `${img(s.cover, 'mst-pic')}<h2>The End</h2><p class="muted">${s.moral_en || ''}</p>`;
    if (s.talk_en?.length) card.insertAdjacentHTML('beforeend', `<h3>Talk about it</h3><ul class="mst-talk">${s.talk_en.map(q => `<li>${q}</li>`).join('')}</ul>`);
    const dl = el('button', 'btn btn-primary btn-wide', 'Download the PDF'); dl.onclick = async () => { const it = await pdfFor(s.n); if (it) savePdf(it); else toast('PDF not available.'); }; card.append(dl);
  }
  main.append(card);
  const nav = el('div', 'mst-nav'), prev = el('button', 'btn', 'Back'), next = el('button', 'btn btn-primary', p < last ? (p === last - 1 ? 'Finish' : 'Next') : 'All stories');
  prev.onclick = () => { if (p > 0) { st.storyP = p - 1; } else st.storyN = null; render(); };
  next.onclick = () => { if (p < last) st.storyP = p + 1; else st.storyN = null; render(); };
  nav.append(prev, next); main.append(nav);
}
