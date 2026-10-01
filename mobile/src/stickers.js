// round 9c: the letter sticker book. Every letter mastered (Leitner box >= 4) earns a collectible sticker: the letter on a glossy,
// die-cut tile in a palette colour with a tiny Marko pose. Fully deterministic (colour and pose come from the letter's index): no
// randomness, no scarcity, nothing to lose. Three pieces, all attached from outside the screens that own the DOM:
//  - a "Sticker book" button injected under the Me card (observer on .me-card)
//  - the Sticker Book overlay (earned stickers + soft outlines with the letter's name for the rest)
//  - a one-time "new sticker" reveal, queued and shown only when the Learn tab (.home-hero) is on screen, never over a lesson
import { db } from './db.js';
import { C, el } from './content.js';

const COLOURS = ['#1E9C8F', '#D9831F', '#E0583C', '#4F5FD0', '#3E9A5E', '#C2528C', '#2E86C1', '#7A52B8'];
const POSES = ['trophy', 'clap', 'proud', 'heart', 'surprised', 'fire'];
const seenKey = pid => 'stickersSeen:' + pid;
const order = () => (C.letters?.letters || []).map(l => l.ch);

export function stickerTile(l, idx, cls = '') {
  const t = el('div', 'stk ' + cls, `<span class="stk-gloss"></span><span class="stk-ch ur">${l.ch}</span><span class="stk-name">${l.name}</span><img class="stk-m" alt="" src="./img/mascot_${POSES[(idx * 5 + 2) % POSES.length]}.webp" loading="lazy">`);
  t.style.setProperty('--sc', COLOURS[idx % COLOURS.length]); t.style.setProperty('--tilt', ((idx % 5) - 2) * 1.2 + 'deg'); t.setAttribute('aria-label', `Sticker: ${l.name}`);
  return t;
}

async function pid() { return db.setting('activeProfile'); }
async function mastered(profileId) { const cards = await db.by('cards', 'profileId', profileId); return cards.filter(c => c.kind === 'letter' && c.box >= 4).sort((a, b) => (a.last || 0) - (b.last || 0)).map(c => c.item).filter(ch => C.by[ch]); }
async function seenOf(profileId) { return await db.setting(seenKey(profileId)); }
const saveSeen = (profileId, arr) => db.setting(seenKey(profileId), [...new Set(arr)]);
const soundOk = () => { try { window.__feel?.chime?.(2); } catch (e) {} };

let busy = false;
function overlay(cls, label) { const o = el('div', 'stk-ov ' + cls); o.setAttribute('role', 'dialog'); o.setAttribute('aria-label', label); document.body.append(o); document.body.classList.add('stk-open'); requestAnimationFrame(() => o.classList.add('in')); return o; }
function close(o, after) { o.classList.remove('in'); o.classList.add('out'); setTimeout(() => { o.remove(); if (!document.querySelector('.stk-ov')) document.body.classList.remove('stk-open'); after?.(); }, 220); }

export async function openBook() {
  if (document.querySelector('.stk-book')) return; const p = await pid(); if (!p) return; const got = new Set(await mastered(p)); const all = order();
  const o = overlay('stk-book', 'Sticker book');
  const done = all.filter(ch => got.has(ch)).length;
  o.innerHTML = `<div class="stk-head"><button class="btn stk-back" aria-label="Back">←</button><div><h2>My stickers</h2><small>${done} of ${all.length} letters</small></div></div><div class="stk-scroll"></div>`;
  const sc = o.querySelector('.stk-scroll');
  if (!done) sc.append(el('div', 'stk-empty', `<img src="./img/mascot_heart.webp" alt="" width="120" height="120"><p><b>Your first sticker is waiting.</b><br>Learn a letter well and it lands here.</p>`));
  const grid = el('div', 'stk-grid'); all.forEach((ch, i) => { const l = C.by[ch]; if (!l) return; if (got.has(ch)) { const t = stickerTile(l, i, 'got'); t.style.animationDelay = Math.min(i, 14) * 30 + 'ms'; grid.append(t); } else grid.append(el('div', 'stk ghost', `<span class="stk-name">${l.name}</span>`)); });
  sc.append(grid);
  const b = o.querySelector('.stk-back'); b.onclick = () => close(o); o.onkeydown = e => e.key === 'Escape' && close(o); b.focus({ preventScroll: true });
}

async function reveal(ch, rest, profileId) {
  const idx = order().indexOf(ch), l = C.by[ch]; busy = true;
  const o = overlay('stk-reveal', 'New sticker');
  o.innerHTML = `<div class="stk-rays"></div><div class="stk-stage"><h2 class="stk-title">New sticker!</h2><div class="stk-flip"><div class="stk-back-face"><span>?</span></div></div><p class="stk-line"><b>${l.name}</b> is yours.<br><small>You know this letter well now.</small></p><img class="stk-pal" src="./img/mascot_clap.webp" alt="" width="110" height="110"></div><div class="stk-foot"><button class="btn stk-cta">${rest.length ? 'Next sticker' : 'Add to my book'}</button></div>`;
  const flip = o.querySelector('.stk-flip'); const tile = stickerTile(l, idx, 'xl'); flip.append(tile);
  setTimeout(() => { flip.classList.add('go'); flip.insertAdjacentHTML('beforeend', [...Array(14)].map((_, k) => `<i class="stk-sp" style="--a:${k * 25.7}deg;--d:${70 + (k % 4) * 18}px;--dl:${(k % 3) * 40}ms"></i>`).join('')); soundOk(); }, 380);
  await saveSeen(profileId, [...(await seenOf(profileId) || []), ch]);
  const cta = o.querySelector('.stk-cta'); cta.onclick = () => close(o, () => { busy = false; if (rest.length) reveal(rest[0], rest.slice(1), profileId); });
}

// Called when the Learn tab is on screen. Silent catch-up on first run (we never dump 20 reveals on someone): only the newest 3 reveal.
async function checkNew() {
  if (busy || document.querySelector('.stk-ov, .lesson, .celebrate') || !document.querySelector('.home-hero')) return;
  const p = await pid(); if (!p || !C.by || !C.letters) return; const now = await mastered(p); if (!now.length) { if (await seenOf(p) == null) await saveSeen(p, []); return; }
  let seen = await seenOf(p); if (seen == null) { seen = now.slice(0, Math.max(0, now.length - 3)); await saveSeen(p, seen); }
  const fresh = now.filter(ch => !seen.includes(ch)); if (!fresh.length) return;
  if (busy || document.querySelector('.stk-ov, .lesson, .celebrate') || !document.querySelector('.home-hero')) return;
  setTimeout(() => { if (!busy && document.querySelector('.home-hero') && !document.querySelector('.lesson, .celebrate')) reveal(fresh[0], fresh.slice(1), p); }, 700);
}

async function injectEntry(card) {
  if (card.dataset.stk) return; card.dataset.stk = '1'; const p = await pid(); if (!p || !C.letters) return; const got = (await mastered(p)).length, total = order().length;
  const b = el('button', 'card stk-entry', `<span class="stk-mini">${[0, 1, 2].map(i => `<i style="--sc:${COLOURS[(i * 3 + 1) % 8]};--r:${(i - 1) * 9}deg"></i>`).join('')}</span><span><b>Sticker book</b><small class="muted">${got ? `${got} of ${total} letters collected` : 'Your letter stickers live here'}</small></span><span class="stk-go">›</span>`);
  b.onclick = () => openBook(); card.after(b);
}

export function initStickers() {
  let q = 0; const scan = () => { q = 0; const c = document.querySelector('.me-card:not([data-stk])'); if (c) injectEntry(c); checkNew(); };
  new MutationObserver(ms => { if (q) return; for (const m of ms) for (const n of m.addedNodes) if (n.nodeType === 1 && (n.matches?.('.me-card,.home-hero') || n.querySelector?.('.me-card,.home-hero'))) { q = requestAnimationFrame(scan); return; } }).observe(document.body, { childList: true, subtree: true });
  window.__stickers = { openBook, checkNew, mastered: async () => mastered(await pid()) };
}
