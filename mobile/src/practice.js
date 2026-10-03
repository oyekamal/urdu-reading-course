// round 11f: Practice sheets. Printable PDFs (A4, black and white is fine) that ship inside the app in public/pdf and are listed by
// public/pdf/index.json (built by scripts/build_pdfs.py from data/letters.json + data/units.json).
//   openPractice(ctx?)  ->  opens the full-screen "Practice sheets" screen. ctx is optional: { onClose }.
//   window.__practice = { open: openPractice }   (the lead wires an entry button in Me/More; this file never touches learner.js)
// Android: the PDF is written to the cache directory with @capacitor/filesystem and handed to the system share sheet
// (@capacitor/share), which offers Open with, Print, Save to Drive and Share. Web / PWA: a plain download link, and the Web Share
// API (or a new tab) for Share / Print. Offline: the files are bundled in the APK; on the web the service worker caches each PDF
// the first time it is opened (nothing is pre-cached). No external links.
import { el, toast } from './content.js';
import { icon, mascot } from './icons.js';

const KIND_ICON = { guide: 'parent', trace: 'pen', lookalike: 'eye', join: 'link', match: 'puzzle', reading: 'read', dictation: 'ear', check: 'check', pack: 'book', starter: 'book', chart: 'script', card: 'marks', flashcards: 'sight', certificate: 'star' };
const kb = n => n >= 1048576 ? (n / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB';
const native = () => { try { return !!window.Capacitor?.isNativePlatform?.(); } catch (e) { return false; } };
const blobs = new Map();
let manifest = null;

async function loadManifest() {
  if (manifest) return manifest;
  const r = await fetch('pdf/index.json'); if (!r.ok) throw new Error('manifest ' + r.status);
  manifest = await r.json(); return manifest;
}

async function getBlob(item) {
  if (blobs.has(item.file)) return blobs.get(item.file);
  let res = null;
  try { res = await fetch(item.file); } catch (e) { /* offline: try any cache the service worker filled earlier */ }
  if (!res || !res.ok) { try { res = await caches.match(item.file, { ignoreSearch: true }); } catch (e) { res = null; } }
  if (!res || !res.ok) throw new Error('not available');
  const b = new Blob([await res.arrayBuffer()], { type: 'application/pdf' });
  blobs.set(item.file, b); return b;
}

const toBase64 = blob => new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(',')[1]); r.onerror = () => no(r.error); r.readAsDataURL(blob); });
const fname = item => item.file.split('/').pop();

async function shareNative(item, dialogTitle) {
  const blob = await getBlob(item);
  const { Filesystem, Directory } = await import('@capacitor/filesystem'); const { Share } = await import('@capacitor/share');
  const r = await Filesystem.writeFile({ path: 'practice/' + fname(item), data: await toBase64(blob), directory: Directory.Cache, recursive: true });
  await Share.share({ title: item.title, url: r.uri, dialogTitle });
}

async function shareWeb(item) {
  if (!navigator.share) { window.open(item.file, '_blank', 'noopener'); return; } // new tab: print from the PDF viewer
  const blob = await getBlob(item); const f = new File([blob], fname(item), { type: 'application/pdf' });
  if (navigator.canShare && !navigator.canShare({ files: [f] })) { const u = URL.createObjectURL(blob); window.open(u, '_blank', 'noopener'); return; }
  await navigator.share({ files: [f], title: item.title });
}

function say(root, msg) { const s = root.querySelector('.pr-status'); if (s) { s.textContent = ''; setTimeout(() => { s.textContent = msg; }, 30); } toast(msg); }

function card(item, primary, root) {
  const c = el('article', 'pr-card' + (primary ? ' pr-main' : ''));
  const id = 'pr-t-' + item.id;
  c.setAttribute('aria-labelledby', id);
  c.innerHTML = `<div class="pr-ic" aria-hidden="true">${icon(KIND_ICON[item.kind] || 'book')}</div>
    <div class="pr-body">
      <h3 class="pr-t" id="${id}"><span class="pr-en"></span><span class="pr-ur ur" lang="ur" dir="rtl"></span></h3>
      <p class="pr-d"></p>
      <p class="pr-m"><span class="pill">${item.pages} page${item.pages === 1 ? '' : 's'}</span><span class="pill">${kb(item.size)}</span><span class="pill">A4</span></p>
      <div class="pr-act"></div>
    </div>`;
  c.querySelector('.pr-en').textContent = item.title; c.querySelector('.pr-ur').textContent = item.title_ur; c.querySelector('.pr-d').textContent = item.desc;
  const act = c.querySelector('.pr-act');
  const open = el('a', 'btn' + (primary ? ' btn-primary' : ''), `${icon('book')}<span>Open / Download</span>`);
  open.href = item.file; open.setAttribute('download', fname(item)); open.setAttribute('aria-label', `Open or download ${item.title}, ${item.pages} pages`);
  open.onclick = async e => {
    if (!native()) { // web / PWA: fetch once (the service worker keeps it for offline), then save from a blob; if that fails, the plain link still works
      e.preventDefault(); open.classList.add('busy');
      try { const b = await getBlob(item); const u = URL.createObjectURL(b); const a = document.createElement('a'); a.href = u; a.download = fname(item); document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000); }
      catch (err) { say(root, navigator.onLine === false ? 'This sheet is not saved on this phone yet. Connect once to get it.' : 'Could not get this sheet. Try again.'); }
      open.classList.remove('busy'); return;
    }
    e.preventDefault(); open.classList.add('busy');
    try { await shareNative(item, 'Open or save this sheet'); } catch (err) { if (!/cancel|dismiss/i.test(String(err?.message || err))) say(root, 'Could not get this sheet. Try again.'); }
    open.classList.remove('busy');
  };
  const share = el('button', 'btn', `${icon('share')}<span>Share / Print</span>`); share.type = 'button'; share.setAttribute('aria-label', `Share or print ${item.title}`);
  share.onclick = async () => {
    share.classList.add('busy'); share.disabled = true;
    try { if (native()) await shareNative(item, 'Share or print this sheet'); else await shareWeb(item); }
    catch (err) { const m = String(err?.name || '') + ' ' + String(err?.message || err); if (!/abort|cancel|dismiss/i.test(m)) say(root, navigator.onLine === false ? 'This sheet is not saved on this phone yet. Connect once to get it.' : 'Could not get this sheet. Try again.'); }
    share.classList.remove('busy'); share.disabled = false;
  };
  act.append(open, share);
  return c;
}

export async function openPractice(ctx = {}) {
  if (document.querySelector('.pr-ov')) return;
  const back = document.activeElement;
  const o = el('div', 'pr-ov'); o.setAttribute('role', 'dialog'); o.setAttribute('aria-modal', 'true'); o.setAttribute('aria-labelledby', 'pr-h');
  o.innerHTML = `<div class="pr-head"><button type="button" class="btn pr-back" aria-label="Back">←</button>
      <div class="pr-hd"><h2 id="pr-h" tabindex="-1">Practice sheets</h2><small>Print them, write on them. They work without internet.</small></div>${mascot('read', 56, 'pr-mk')}</div>
    <details class="pr-tips"><summary>Print tips</summary><ul>
      <li>Use <b>A4</b> paper, portrait. “Actual size” or 100%.</li>
      <li><b>Black and white is fine.</b> Pages use thin grey lines to save ink.</li>
      <li>Give the child a soft pencil. Sit together for 10 minutes.</li>
      <li>Urdu goes right to left. Start on the right side of the page.</li>
      <li>Answer keys are on their own page at the end, for the grown-up.</li></ul></details>
    <div class="pr-tabs" role="tablist" aria-label="Units"></div>
    <div class="pr-scroll" id="pr-panel" role="tabpanel" aria-label="Sheets" tabindex="-1"><p class="muted pr-load">Getting the list…</p></div>
    <p class="pr-status" role="status" aria-live="polite"></p>`;
  document.body.append(o); document.body.classList.add('pr-open');
  // modal: everything behind the screen is inert (no Tab into the app underneath, hidden from screen readers)
  const behind = [...document.body.children].filter(n => n !== o && n.tagName !== 'SCRIPT' && !n.inert);
  behind.forEach(n => { n.inert = true; });
  requestAnimationFrame(() => o.classList.add('in')); o.querySelector('#pr-h').focus({ preventScroll: true });
  const close = () => { behind.forEach(n => { n.inert = false; }); o.classList.remove('in'); o.classList.add('out'); document.removeEventListener('keydown', onKey); setTimeout(() => { o.remove(); if (!document.querySelector('.pr-ov')) document.body.classList.remove('pr-open'); try { back?.focus?.({ preventScroll: true }); } catch (e) {} ctx.onClose?.(); }, 200); };
  const onKey = e => { if (e.key === 'Escape') { e.preventDefault(); close(); } };
  document.addEventListener('keydown', onKey);
  o.querySelector('.pr-back').onclick = close;
  const scroll = o.querySelector('.pr-scroll'), tabs = o.querySelector('.pr-tabs');
  let m;
  try { m = await loadManifest(); } catch (e) {
    scroll.innerHTML = ''; const err = el('div', 'card pr-err', `<h3>The list could not be loaded</h3><p class="muted">${navigator.onLine === false ? 'You are offline and this list is not saved on this phone yet. Connect once, then open Practice again.' : 'Close this screen and open it again. If this keeps happening, update the app.'}</p>`);
    const retry = el('button', 'btn btn-primary', 'Try again'); retry.onclick = () => { close(); setTimeout(() => openPractice(ctx), 260); }; err.append(retry); scroll.append(err); return;
  }
  const groups = [{ key: 'course', label: 'Start', sub: 'Course', items: m.items.filter(i => i.unit == null) }];
  for (const u of m.units) { const items = m.items.filter(i => i.unit === u.n); if (items.length) groups.push({ key: 'u' + u.n, label: String(u.n), sub: 'Unit', title: u.title, title_ur: u.title_ur, items }); }
  const show = k => {
    const g = groups[k]; scroll.innerHTML = ''; scroll.scrollTop = 0;
    scroll.setAttribute('aria-label', g.key === 'course' ? 'Course sheets' : `Unit ${g.label} sheets`);
    [...tabs.children].forEach((b, i) => { b.setAttribute('aria-selected', String(i === k)); b.classList.toggle('on', i === k); b.tabIndex = i === k ? 0 : -1; });
    const head = el('div', 'pr-gh'); head.innerHTML = g.key === 'course' ? '<b>Start here</b><small>Charts, cards and a first-week pack for any learner</small>' : `<b></b><small></small>`;
    if (g.key !== 'course') { head.querySelector('b').textContent = `Unit ${g.label}: ${g.title}`; head.querySelector('small').textContent = `${g.items.length} sheet${g.items.length === 1 ? '' : 's'} · ${g.items[0].level}`; }
    scroll.append(head);
    const lead = g.items.find(i => i.kind === 'starter' || i.kind === 'pack') || g.items[0];
    const order = [...(lead ? [lead] : []), ...g.items.filter(i => i !== lead)];
    const grid = el('div', 'pr-grid'); order.forEach(i => grid.append(card(i, i === lead, o))); scroll.append(grid);
  };
  groups.forEach((g, k) => { const b = el('button', 'btn pr-tab', `<b></b><small></small>`); b.type = 'button'; b.querySelector('b').textContent = g.label; b.querySelector('small').textContent = g.sub; b.setAttribute('role', 'tab'); b.setAttribute('aria-controls', 'pr-panel'); b.setAttribute('aria-label', g.key === 'course' ? 'Start here, course sheets' : `Unit ${g.label}, ${g.title}`); b.onclick = () => show(k);
    b.onkeydown = e => { const d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (d) { const n = (k + d + groups.length) % groups.length; show(n); tabs.children[n].focus(); e.preventDefault(); } };
    tabs.append(b); });
  const start = ctx.unit != null ? groups.findIndex(g => g.key === 'u' + ctx.unit) : 0; show(start > 0 ? start : 0);
}

if (typeof window !== 'undefined') window.__practice = { open: openPractice };
