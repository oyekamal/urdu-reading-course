// round 11b: accessibility layer. One small module, attached from outside the screens (observer-based, like feel.js / premium.js):
//  - a persistent polite live region (and a pre-built #toast) so announcements are not skipped as "first use"
//  - wrong answers are spoken ("Not quite. be is the one with one dot"); the right tile is labelled
//  - Urdu text gets lang="ur" dir="rtl", and its inline px sizes follow the Text size setting (--ur-scale)
//  - the tab bar is a labelled navigation with aria-current on the active tab
//  - overlays (celebration, sticker book, new-sticker, grown-up gate, confirm sheet) are modal dialogs: focus moves in,
//    the page behind is inert, Tab is trapped, focus returns to the opener (or the new screen's heading)
//  - when the focused control is replaced by a new screen, focus goes to that screen's heading instead of <body>
//  - decorative Marko / Lottie / confetti are hidden from screen readers
// Also exports confirmSheet(): the calm "Leave this lesson?" sheet (never window.confirm).

import { C } from './content.js';

const DIALOGS = '.celebrate, .stk-ov, .a11y-sheet, .gate-back';
const DECOR = '.marko, .fx, .cel-rays, .cel-confetti, .cel-pearl, .pg-spark, .hh-shadow, .fx-burst, .stk-rays, .feel-coach-wrap, .confetti, svg.string';
const URDU_CLS = '.ur, .ob-word, .ob-glyph, .stk-ch, .stk-glyph, .u-ur, .ob-joined';
const ARABIC = /[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]/;

/* ----------------------------------------------------------------- live region ---- */
let live = null;
function ensureLive() {
  if (live && live.isConnected) return live;
  live = document.createElement('div'); live.id = 'a11y-live'; live.className = 'sr-only';
  live.setAttribute('role', 'status'); live.setAttribute('aria-live', 'polite'); live.setAttribute('aria-atomic', 'true');
  document.body.append(live); return live;
}
export function announce(msg) {
  const l = ensureLive(); clearTimeout(l._t); l.textContent = '';
  l._t = setTimeout(() => { l.textContent = msg; }, 60);
}
function ensureToast() {   // content.js toast() reuses #toast: having it in the DOM at load makes the very first message announce
  if (document.getElementById('toast')) return;
  const t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; t.setAttribute('role', 'status'); t.setAttribute('aria-live', 'polite'); document.body.append(t);
}

/* -------------------------------------------------------------------- Urdu text ---- */
function scaleInline(e) {
  const s = e.style && e.style.fontSize; if (!s || e.dataset.urpx) return;
  const m = /^([\d.]+)px$/.exec(s); if (!m) return;
  e.dataset.urpx = m[1]; e.style.fontSize = `calc(${m[1]}px * var(--ur-scale,1))`;
}
function markUrdu(root) {
  const list = [];
  if (root.matches?.(URDU_CLS)) list.push(root);
  root.querySelectorAll?.(URDU_CLS).forEach(e => list.push(e));
  for (const e of list) {
    if (!e.hasAttribute('lang')) e.setAttribute('lang', 'ur');
    if (!e.hasAttribute('dir')) e.setAttribute('dir', 'rtl');
    if (e.matches('.ur')) scaleInline(e);
  }
  // Urdu text that is not in an .ur element (labels, bubbles): tag the parent when most of its own text is Arabic script
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let n = 0;
  for (let t = w.nextNode(); t && n < 400; t = w.nextNode(), n++) {
    const v = t.nodeValue; if (!v || !ARABIC.test(v)) continue;
    const p = t.parentElement; if (!p || p.closest('[lang=ur]') || p.closest('script,style')) continue;
    const own = [...p.childNodes].filter(c => c.nodeType === 3).map(c => c.nodeValue).join('').replace(/\s+/g, '');
    const ar = [...own].filter(c => ARABIC.test(c)).length;
    if (own.length && ar / own.length >= .5) p.setAttribute('lang', 'ur');
  }
}
function decorate(root) {
  const hide = e => { if (!e.hasAttribute('aria-hidden')) e.setAttribute('aria-hidden', 'true'); };
  if (root.matches?.(DECOR)) hide(root);
  root.querySelectorAll?.(DECOR).forEach(hide);
}

/* ------------------------------------------------------------- tab bar semantics ---- */
function syncNav(nav) {
  if (!nav) return;
  watchNav(nav);
  if (!nav.hasAttribute('role')) { nav.setAttribute('role', 'navigation'); nav.setAttribute('aria-label', 'Main'); }
  nav.querySelectorAll('button').forEach(b => { if (b.classList.contains('active')) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
}

/* nav height changes with text size: publish it as --nav-h so docked buttons and page padding always clear it */
let navRO = null, navWatched = null;
function measureNav() {
  const nav = document.querySelector('.bottom'), st = document.documentElement.style;
  if (!nav) { st.removeProperty('--nav-h'); return; }
  const cs = getComputedStyle(nav);
  if (cs.position !== 'fixed' || cs.flexDirection === 'column') { st.removeProperty('--nav-h'); return; }
  const pb = parseFloat(cs.paddingBottom) || 0;        // calc(6px + safe-area): keep only the 6px, the safe area is added by the rules that use --nav-h
  st.setProperty('--nav-h', Math.ceil(nav.getBoundingClientRect().height - Math.max(0, pb - 6)) + 'px'); fitAll();
}
function watchNav(nav) {
  if (navWatched === nav) return; navWatched = nav;
  if (!navRO && window.ResizeObserver) { navRO = new ResizeObserver(measureNav); addEventListener('resize', measureNav); addEventListener('orientationchange', measureNav); }
  navRO?.disconnect(); navRO?.observe(nav); measureNav();
}

/* ------------------------------------------------------------ wrong / right answers ---- */
let lastSay = 0, pendingNo = 0;
function sayWrong(node) {
  lastSay = performance.now(); clearTimeout(pendingNo);
  const spoken = (node.textContent || 'Try again').replace(/[\u0600-\u06FF\u200C\u200D]+/g, m => { const k = m.replace(/[\u0640\u200C\u200D]/g, ''); return C.by?.[k]?.name || C.by?.[[...k][0]]?.name || ''; }).replace(/\s{2,}/g, ' ').trim();
  const txt = node.dataset.sr || spoken;   // letter NAMES, never glyphs, for the screen reader
  node.setAttribute('aria-hidden', 'true'); node.removeAttribute('role');   // spoken once through the live region instead
  announce(/^Not quite/i.test(txt) ? txt : 'Not quite. ' + txt);
}
function noteAnswerClasses(t) {
  if (t.matches?.('.tile.feel-answer')) { if (t.dataset.lbl0 === undefined) { const l = t.getAttribute('aria-label') || t.textContent.trim(); t.dataset.lbl0 = l; t.setAttribute('aria-label', l + ', the answer'); } }
  else if (t.dataset?.lbl0 !== undefined && t.matches?.('.tile')) { t.setAttribute('aria-label', t.dataset.lbl0); delete t.dataset.lbl0; }
  if (t.matches?.('.tile.no, .answer.no') && !t.dataset.sayno) {
    t.dataset.sayno = '1';
    const at = performance.now();
    clearTimeout(pendingNo); pendingNo = setTimeout(() => { if (lastSay < at) announce('Not quite. Try again.'); }, 140);
  } else if (t.matches?.('.tile, .answer') && !t.matches('.no')) delete t.dataset.sayno;
}

/* ------------------------------------------------------------------- dialogs ---- */
const stack = [];            // { node, opener }
let lastFocused = null, outside = null;   // outside = last focused element that was not inside an overlay (the opener)
const FOCUSABLE = 'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
const visible = e => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
let idn = 0;
function labelDialog(node) {
  if (node.matches('.gate-back')) return;             // gate.js sets its own role/labels on the inner sheet
  if (!node.hasAttribute('role')) node.setAttribute('role', 'dialog');
  node.setAttribute('aria-modal', 'true');
  if (!node.hasAttribute('aria-label') && !node.hasAttribute('aria-labelledby')) {
    const h = node.querySelector('h1, h2'); if (h) { if (!h.id) h.id = 'a11y-h' + (++idn); node.setAttribute('aria-labelledby', h.id); }
    else node.setAttribute('aria-label', node.matches('.stk-ov') ? 'Sticker book' : 'Dialog');
  }
}
function focusInto(node) {
  if (node.matches('.gate-back')) return;
  const pref = node.querySelector('[data-autofocus]');
  let t = pref;
  if (!t && node.matches('.celebrate')) t = node.querySelector('h1');
  if (!t) t = [...node.querySelectorAll(FOCUSABLE)].find(visible) || node;
  if (t === node || t.matches('h1, h2')) t.setAttribute('tabindex', '-1');
  try { t.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
}
function syncInert() {
  const top = stack[stack.length - 1]?.node;
  for (const c of document.body.children) {
    if (c.tagName === 'SCRIPT' || c.id === 'toast' || c.id === 'a11y-live' || c.matches('.feel-say')) continue;
    if (top && c !== top) { if (!c.inert) { c.inert = true; c.dataset.a11yInert = '1'; } }
    else if (c.dataset.a11yInert) { c.inert = false; delete c.dataset.a11yInert; }
  }
}
function openDialog(node) {
  if (stack.some(s => s.node === node)) return;
  stack.push({ node, opener: outside && outside.isConnected && !outside.closest(DIALOGS) ? outside : null });
  labelDialog(node); syncInert(); [120, 500, 1300].forEach(t => setTimeout(syncScrollable, t));
  requestAnimationFrame(() => { if (stack.some(s => s.node === node) && !node.contains(document.activeElement)) focusInto(node); });
}
function closeDialog(i) {
  const [{ node, opener }] = stack.splice(i, 1); syncInert();
  const ae = document.activeElement;
  if (ae && ae !== document.body && !node.contains(ae) && ae.isConnected) return;     // the app already moved focus somewhere real
  if (stack.length) { const t = stack[stack.length - 1].node; if (!t.contains(document.activeElement)) focusInto(t); return; }
  requestAnimationFrame(() => {
    const cur = document.activeElement; if (cur && cur !== document.body && cur.isConnected) return;
    if (opener && opener.isConnected && visible(opener)) { try { opener.focus({ preventScroll: true }); return; } catch (e) { /* ignore */ } }
    focusScreen();
  });
}
function trapKeys(e) {
  const top = stack[stack.length - 1]; if (!top) return;
  const n = top.node;
  if (e.key === 'Escape' && n.matches('.a11y-sheet')) { e.preventDefault(); e.stopPropagation(); n._cancel?.(); return; }
  if (e.key === 'Escape' && n.matches('.stk-book') && !n.contains(document.activeElement)) { n.querySelector('.stk-back')?.click(); return; }
  if (e.key !== 'Tab' || n.matches('.gate-back')) return;
  const f = [...n.querySelectorAll(FOCUSABLE)].filter(visible); if (!f.length) { e.preventDefault(); return; }
  const a = document.activeElement, first = f[0], last = f[f.length - 1];
  if (!n.contains(a)) { e.preventDefault(); first.focus(); }
  else if (e.shiftKey && (a === first || a.getAttribute('tabindex') === '-1')) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && a === last) { e.preventDefault(); first.focus(); }
}

/* ---------------------------------------------------- focus after a screen change ---- */
function focusScreen() {
  const app = document.getElementById('app'); if (!app || stack.length) return;
  const les = app.querySelector('.lesson');
  const h = (les && (les.querySelector('.t-kids h2') || les.querySelector('h1'))) || app.querySelector('h1') || app.querySelector('h2');
  if (!h) return;
  h.setAttribute('tabindex', '-1'); try { h.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
}
let settle = 0;
function afterRender() {
  clearTimeout(settle);
  settle = setTimeout(() => {
    if (stack.length || !lastFocused || lastFocused.isConnected) return;
    const ae = document.activeElement; if (ae && ae !== document.body) return;
    lastFocused = null; focusScreen();
  }, 160);
}

/* -------------------------------------------------------------- confirm sheet ---- */
let sheetOpen = null;
export function confirmSheet({ title = 'Leave this lesson?', body = 'Your progress here is saved.', yes = 'Leave', no = 'Keep going' } = {}) {
  if (sheetOpen) return sheetOpen;
  const o = document.createElement('div'); o.className = 'a11y-sheet'; o.setAttribute('role', 'dialog'); o.setAttribute('aria-modal', 'true'); o.setAttribute('aria-labelledby', 'a11y-sheet-t'); o.setAttribute('aria-describedby', 'a11y-sheet-d');
  const card = document.createElement('div'); card.className = 'a11y-sheet-card';
  card.innerHTML = '<h2 id="a11y-sheet-t"></h2><p id="a11y-sheet-d" class="muted"></p><div class="a11y-sheet-actions"><button type="button" class="btn btn-primary a11y-stay" data-autofocus></button><button type="button" class="btn a11y-leave"></button></div>';
  card.querySelector('h2').textContent = title; card.querySelector('p').textContent = body;
  card.querySelector('.a11y-stay').textContent = no; card.querySelector('.a11y-leave').textContent = yes;
  o.append(card);
  sheetOpen = new Promise(resolve => {
    const done = v => { if (!o.isConnected) return; o.classList.add('out'); setTimeout(() => o.remove(), 140); sheetOpen = null; resolve(v); };
    o._cancel = () => done(false);
    card.querySelector('.a11y-stay').onclick = () => done(false);
    card.querySelector('.a11y-leave').onclick = () => done(true);
    o.addEventListener('click', e => { if (e.target === o) done(false); });
  });
  document.body.append(o);
  return sheetOpen;
}

/* ------------------------------------------------- lesson: scroll region above a docked primary ---- */
// Lesson screens are built as [content..., primary button] directly inside .t-kids. Wrap the content in one scroll region so the
// primary never overlaps it (small phones, landscape, large text). Re-runs after every render; handlers and refs are untouched
// because nodes are only moved, never rebuilt.
let wrapQ = 0;
function wrapLessons() {
  wrapQ = 0;
  document.querySelectorAll('.lesson > .t-kids, .ob > .ob-demo').forEach(box => {
    const kids = [...box.children]; let sc = kids.find(k => k.classList.contains('les-scroll'));
    const last = kids[kids.length - 1];
    const prim = last && !last.classList.contains('les-scroll') && last.matches('.btn-primary, .dock') ? last : null;
    const body = kids.filter(k => k !== sc && k !== prim);
    if (!body.length) return;
    if (!sc) { sc = document.createElement('div'); sc.className = 'les-scroll'; box.insertBefore(sc, body[0]); }
    body.forEach(k => sc.append(k));
    if (prim && prim !== box.lastElementChild) box.append(prim);
    else if (!prim && sc !== box.lastElementChild) box.append(sc);
  });
  requestAnimationFrame(fitAll); setTimeout(fitAll, 350);
}
let fitRO = null, fitT = 0;
function fitLesson(lesson) {   // publish how tall everything except the scroll area is, so the scroll area gets exactly the room that is left
  const box = lesson.querySelector(':scope > .t-kids, :scope > .ob-demo'); if (!box) return;
  let fixed = 0;
  for (const c of lesson.children) if (c !== box) { const cs = getComputedStyle(c); fixed += c.getBoundingClientRect().height + (parseFloat(cs.marginTop) || 0) + (parseFloat(cs.marginBottom) || 0); }
  const prim = box.lastElementChild;
  if (prim && !prim.classList.contains('les-scroll')) { const cs = getComputedStyle(prim); fixed += prim.getBoundingClientRect().height + (parseFloat(cs.marginTop) || 0) + (parseFloat(cs.marginBottom) || 0); }
  lesson.style.setProperty('--les-fixed', Math.ceil(fixed + 20) + 'px');
  if (window.ResizeObserver) { fitRO = fitRO || new ResizeObserver(() => { clearTimeout(fitT); fitT = setTimeout(fitAll, 60); }); for (const c of lesson.children) if (c !== box && !c._ro) { c._ro = 1; fitRO.observe(c); } if (prim && !prim._ro) { prim._ro = 1; fitRO.observe(prim); } }
}
// a scroll area that really overflows must be reachable and scrollable from the keyboard
function syncScrollable() {
  document.querySelectorAll('.les-scroll, .cel-body').forEach(e => {
    if (e.scrollHeight > e.clientHeight + 1) { if (!e.hasAttribute('tabindex')) { e.setAttribute('tabindex', '0'); e.setAttribute('role', 'region'); e.setAttribute('aria-label', e.matches('.cel-body') ? 'Celebration details' : 'Lesson content'); } }
    else if (e.getAttribute('tabindex') === '0') { e.removeAttribute('tabindex'); e.removeAttribute('role'); e.removeAttribute('aria-label'); }
  });
}
const fitAll = () => { document.querySelectorAll('.lesson, .ob:has(> .ob-demo)').forEach(fitLesson); syncScrollable(); };
const queueWrap = () => { if (!wrapQ) { wrapQ = 1; queueMicrotask(wrapLessons); } };

/* ---------------------------------------------------------------------- init ---- */
function scanNode(n) {
  if (n.nodeType !== 1) return;
  if (n.matches(DIALOGS)) openDialog(n);
  else n.querySelectorAll?.(DIALOGS).forEach(openDialog);
  markUrdu(n); decorate(n);
  if (n.matches('.t-kids, .ob-demo') || n.querySelector?.('.t-kids, .ob-demo')) queueWrap();
  if (n.matches('.ob, .ob *') || n.querySelector?.('.ob')) { const app = document.getElementById('app'); if (app && !app.querySelector('h1, [role=heading][aria-level="1"]')) { const h = app.querySelector('.ob h2'); if (h) { h.setAttribute('role', 'heading'); h.setAttribute('aria-level', '1'); } } }
  if (n.matches('.bottom')) syncNav(n); else n.querySelector?.('.bottom') && syncNav(n.querySelector('.bottom'));
  if (n.matches('.feel-say')) sayWrong(n);
  (n.matches('.swatch') ? [n] : [...(n.querySelectorAll?.('.swatch') || [])]).forEach(b => b.setAttribute('aria-pressed', String(b.classList.contains('on'))));
}
function onMutations(ms) {
  let rendered = false;
  for (const m of ms) {
    if (m.type === 'attributes') {
      const t = m.target; if (t.nodeType !== 1) continue;
      if (t.matches('.bottom button')) syncNav(t.parentElement);
      else if (t.matches('.swatch')) t.setAttribute('aria-pressed', String(t.classList.contains('on')));
      else if (t.matches('.tile, .answer')) noteAnswerClasses(t);
      continue;
    }
    m.addedNodes.forEach(scanNode);
    if (m.type === 'childList' && m.target.nodeType === 1 && m.target.matches?.('.t-kids, .ob-demo')) queueWrap();
    m.removedNodes.forEach(n => {
      if (n.nodeType !== 1) return;
      for (let i = stack.length - 1; i >= 0; i--) if (!stack[i].node.isConnected) closeDialog(i);
    });
    if (m.target.id === 'app' || m.target.closest?.('#app')) rendered = true;
  }
  if (rendered) afterRender();
}
export function initA11y() {
  document.getElementById('app')?.setAttribute('role', 'main');
  ensureLive(); ensureToast(); addEventListener('resize', fitAll); addEventListener('orientationchange', fitAll);
  document.addEventListener('focusin', e => { lastFocused = e.target; if (!e.target.closest?.(DIALOGS)) outside = e.target; }, true);
  document.addEventListener('keydown', trapKeys, true);
  new MutationObserver(onMutations).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  scanNode(document.body);
  window.__a11y = { announce, confirmSheet };
}
initA11y();
