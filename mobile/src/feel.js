// feel.js: the "alive on every touch" layer. One delegated module, no per-screen edits:
//   - pointer listeners on document (press squash + spring release, soft ripple, tick sound, haptic tick)
//   - one MutationObserver (answers: .tile .ok / .no, dictation .answer.no, "Correct" toasts, trace "good")
//   - injects a small animated Marko coach into every .lesson header and a combo chip
//   - WebAudio synthesized sounds (no asset files) + @capacitor/haptics (dynamic import, vibrate fallback)
// Child-safe: only delight and encouragement. A wrong answer is a soft boop + a gentle wobble, never a buzzer or red flash.
// Switch: settings.feel === false turns sound + vibration off (motion stays; prefers-reduced-motion removes motion).
import { Capacitor } from '@capacitor/core';
import { marko, setMarko } from './marko.js';
import { C } from './content.js';

let app = null;                                           // ctxBase from main.js: { settings, set }
const on = () => app?.settings?.feel !== false;
const calm = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const root = () => document.getElementById('app');

/* ---------------------------------------------------------------- sound ---- */
let ac = null, master = null;
function unlock() {
  try {
    if (!ac) { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return; ac = new AC(); master = ac.createGain(); master.gain.value = 0.32; master.connect(ac.destination); }
    if (ac.state === 'suspended') ac.resume();
  } catch (e) {}
}
// one soft voice: sine (+ a quiet octave for sparkle), fast attack, exponential decay
function tone(freq, t0, dur, vol, { glide = 0, over = 0 } = {}) {
  const o = ac.createOscillator(), g = ac.createGain(); o.type = 'sine'; o.frequency.setValueAtTime(freq, t0);
  if (glide) o.frequency.exponentialRampToValueAtTime(freq * glide, t0 + dur);
  g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(vol, t0 + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  o.connect(g); g.connect(master); o.start(t0); o.stop(t0 + dur + 0.03);
  if (over) { const o2 = ac.createOscillator(), g2 = ac.createGain(); o2.type = 'triangle'; o2.frequency.setValueAtTime(freq * 2, t0); g2.gain.setValueAtTime(0.0001, t0); g2.gain.exponentialRampToValueAtTime(vol * over, t0 + 0.01); g2.gain.exponentialRampToValueAtTime(0.0001, t0 + dur * 0.7); o2.connect(g2); g2.connect(master); o2.start(t0); o2.stop(t0 + dur); }
}
const PENT = [1046.5, 1174.7, 1318.5, 1568, 1760, 2093];   // C-major pentatonic from C6: bright (Duolingo's chime measures 1.5-2 kHz) and every pair sounds happy
let lastTick = 0;
const sfx = {
  tick() { const n = performance.now(); if (n - lastTick < 45) return; lastTick = n; tone(1250, ac.currentTime, 0.05, 0.05); },
  chime(level = 0) { const t = ac.currentTime, i = Math.min(level, 3); tone(PENT[i], t, 0.16, 0.13, { over: 0.3 }); tone(PENT[i + 2], t + 0.085, 0.26, 0.13, { over: 0.3 }); },   // rising pair, 345 ms, steps up with the combo
  flourish() { const t = ac.currentTime; [0, 2, 4, 5].forEach((k, j) => tone(PENT[k], t + j * 0.075, 0.22, 0.11, { over: 0.3 })); },   // 'high five' arpeggio
  boop() { const t = ac.currentTime; tone(620, t, 0.34, 0.1, { glide: 0.68 }); },   // soft, round, falling 620 -> 420 Hz: 'hmm, listen again', never a buzzer
  pop() { const t = ac.currentTime; tone(880, t, 0.09, 0.07, { glide: 1.5 }); },
};
const hear = (name, a) => { if (!on()) return; try { unlock(); if (ac && ac.state === 'running') sfx[name](a); } catch (e) {} };

/* --------------------------------------------------------------- haptics ---- */
let H = null;
async function haptics() { if (H !== null) return H; try { H = Capacitor.isNativePlatform() ? await import('@capacitor/haptics') : false; } catch (e) { H = false; } return H; }
const coarse = matchMedia('(pointer:coarse)').matches;
function buzz(kind) {
  if (!on()) return;
  try {
    if (Capacitor.isNativePlatform()) {
      haptics().then(m => { if (!m) return; const { Haptics: h, ImpactStyle: s, NotificationType: n } = m;
        if (kind === 'tick') h.impact({ style: s.Light }); else if (kind === 'ok') h.notification({ type: n.Success }); else h.impact({ style: s.Light }); }).catch(() => {});
    } else if (coarse && navigator.vibrate) navigator.vibrate(kind === 'tick' ? 8 : kind === 'ok' ? [14, 40, 14] : 18);
  } catch (e) {}
}

/* ------------------------------------------------------------ tap feedback ---- */
const TAP = '.btn, .tile, .ob-opt, .pearl, .word, .bottom button, .swatch, .ucard, .ob-sw, .ob-word, .ob-glyph, .unitmap button, .tab';
const SPRING = [{ scale: '.94' }, { scale: '1.045', offset: .42 }, { scale: '.99', offset: .72 }, { scale: '1' }];
let pressed = null;
function ripple(el, x, y) {
  const r = el.getBoundingClientRect(); if (r.width < 8) return;
  const box = document.createElement('div'); box.className = 'feel-rip'; box.setAttribute('aria-hidden', 'true');
  Object.assign(box.style, { left: r.left + 'px', top: r.top + 'px', width: r.width + 'px', height: r.height + 'px', borderRadius: getComputedStyle(el).borderRadius });
  if (el.matches('.btn-primary, .cel-go, .ob-cta, .pearl.done, .bottom button.active')) box.classList.add('light');
  const d = Math.hypot(Math.max(x - r.left, r.right - x), Math.max(y - r.top, r.bottom - y)) * 2, i = document.createElement('i');
  Object.assign(i.style, { width: d + 'px', height: d + 'px', left: x - r.left - d / 2 + 'px', top: y - r.top - d / 2 + 'px' });
  box.append(i); document.body.append(box);
  i.animate([{ transform: 'scale(.08)', opacity: .9 }, { transform: 'scale(1)', opacity: .0 }], { duration: 520, easing: 'cubic-bezier(.2,.7,.3,1)', fill: 'forwards' }).onfinish = () => box.remove();
}
function down(e) {
  unlock();
  const el = e.target.closest?.(TAP); if (!el || el.disabled || el.getAttribute('aria-disabled') === 'true') return;
  hear('tick'); buzz('tick');
  if (calm()) { el.classList.add('feel-hot'); pressed = { el, anim: null }; return; }
  const anim = el.animate([{ scale: '1' }, { scale: '.94' }], { duration: 90, easing: 'ease-out', fill: 'forwards' });
  pressed = { el, anim }; ripple(el, e.clientX, e.clientY);
}
function up() {
  if (!pressed) return; const { el, anim } = pressed; pressed = null;
  el.classList.remove('feel-hot');
  if (anim) { anim.cancel(); if (el.isConnected) el.animate(SPRING, { duration: 340, easing: 'ease-out' }); }
}

/* ------------------------------------------------------------ answer effects ---- */
function sparkle(el, n = 10) {
  if (calm() || !el?.isConnected) return;
  const r = el.getBoundingClientRect(), box = document.createElement('div'); box.className = 'feel-spark'; box.setAttribute('aria-hidden', 'true');
  box.style.left = r.left + r.width / 2 + 'px'; box.style.top = r.top + r.height / 2 + 'px';
  const cols = ['var(--gold)', 'var(--accent)', 'var(--coral)', 'var(--gold)', '#fff'];
  for (let k = 0; k < n; k++) {
    const s = document.createElement('i'), a = (k / n) * Math.PI * 2 + Math.random() * .5, d = Math.min(r.width, 120) * .5 + 30 + Math.random() * 34, sz = 10 + Math.random() * 8;
    s.style.cssText = `width:${sz}px;height:${sz}px;background:${cols[k % cols.length]}`;
    box.append(s);
    s.animate([{ transform: 'translate(-50%,-50%) scale(0) rotate(0)', opacity: 1 }, { transform: `translate(calc(-50% + ${Math.cos(a) * d * .75}px),calc(-50% + ${Math.sin(a) * d * .75}px)) scale(1.1) rotate(70deg)`, opacity: 1, offset: .45 },
      { transform: `translate(calc(-50% + ${Math.cos(a) * d}px),calc(-50% + ${Math.sin(a) * d + 8}px)) scale(.2) rotate(140deg)`, opacity: 0 }], { duration: 560 + Math.random() * 160, easing: 'cubic-bezier(.2,.8,.3,1)', fill: 'forwards', delay: k * 12 });
  }
  document.body.append(box); setTimeout(() => box.remove(), 1000);
}
function bounce(el) {
  if (calm() || !el?.isConnected) return;
  el.animate([{ scale: '1', translate: '0 0' }, { scale: '1.2', translate: '0 -9px', offset: .26 }, { scale: '.95', translate: '0 1px', offset: .52 }, { scale: '1.05', translate: '0 -2px', offset: .74 }, { scale: '1', translate: '0 0' }], { duration: 520, easing: 'ease-out' });
  el.animate([{ boxShadow: '0 0 0 0 color-mix(in srgb,var(--good) 55%,transparent)' }, { boxShadow: '0 0 0 16px color-mix(in srgb,var(--good) 0%,transparent)' }], { duration: 620, easing: 'ease-out' });
}
function wobble(el) {
  if (calm() || !el?.isConnected) return;
  el.animate([{ translate: '0 0', rotate: '0deg' }, { translate: '-5px 0', rotate: '-1.6deg', offset: .2 }, { translate: '5px 0', rotate: '1.6deg', offset: .45 }, { translate: '-3px 0', rotate: '-.8deg', offset: .68 }, { translate: '1px 0', offset: .86 }, { translate: '0 0', rotate: '0deg' }], { duration: 440, easing: 'ease-out' });
}

/* ------------------------------------------------------------- Marko coach ---- */
let coach = null, lock = 0, talking = false, idleT = 0, lessonHead = null, combo = 0;
const markos = () => [...document.querySelectorAll('.lesson .marko')].filter(m => m._marko && m.isConnected);
function mood(state, ms) {
  clearTimeout(idleT); lock = performance.now() + ms; markos().forEach(m => setMarko(m, state));
  idleT = setTimeout(() => { lock = 0; markos().forEach(m => setMarko(m, talking && coach && m === coach ? 'talk' : (m.dataset.base || 'idle'))); }, ms);
}
function talk(on_) {
  talking = on_; if (performance.now() < lock) return;
  markos().filter(m => m === coach).forEach(m => setMarko(m, on_ ? 'talk' : 'idle'));
}
// the speech player is private to content.js; wrap play() once and follow the element's own events
const _play = HTMLMediaElement.prototype.play;
const seen = new WeakSet();
const plays = [];                                         // recent speech clips (names/<id>), to point at the right tile after a miss
HTMLMediaElement.prototype.play = function () {
  { const k = (this.src || '').match(/audio\/(names\/[^./]+)\.mp3/); if (k) { plays.push(k[1]); plays.length > 4 && plays.shift(); } }
  if (!seen.has(this)) { seen.add(this); ['playing'].forEach(ev => this.addEventListener(ev, () => talk(true))); ['ended', 'pause', 'error', 'emptied'].forEach(ev => this.addEventListener(ev, () => talk(false))); }
  return _play.apply(this, arguments);
};

function enterLesson(lesson) {
  const head = lesson.firstElementChild; lessonHead = head; combo = 0; talking = false; lock = 0; clearTimeout(idleT); delete lesson.dataset.combo;
  if (!head?.matches('.row')) { coach = null; return; }
  coach = marko('idle', 76, 'feel-coach'); coach.dataset.base = 'idle';
  const wrap = document.createElement('div'); wrap.className = 'feel-coach-wrap'; wrap.append(coach); wrap.setAttribute('aria-hidden', 'true');
  head.insertBefore(wrap, head.children[1] || null);
  // the combo chip rides on the progress bar (zero-height slot, so it never pushes content or covers a button)
  const bar = lesson.querySelector('.progress');
  if (bar) { const host = bar.closest('.pg-wrap'); if (host) host.insertAdjacentHTML('beforeend', '<div class="feel-combo" aria-hidden="true"></div>'); else bar.insertAdjacentHTML('afterend', '<div class="feel-slot" aria-hidden="true"><div class="feel-combo"></div></div>'); }
  syncCoach();
}
// a lesson screen that already has its own big Marko (guide, rules, letter peek) keeps just that one: we drive it instead
function syncCoach() { const w = coach?.parentElement; if (!w) return; const own = document.querySelector('.lesson .guide .marko, .lesson .rules-m, .lesson .blob .marko, .lesson .peek'); w.classList.toggle('away', !!own); }

function chip(n, label) {
  const c = document.querySelector('.feel-combo'); if (!c) return;
  const slot = c.parentElement, bar = document.querySelector('.lesson .progress');
  c.innerHTML = label || (n >= 5 ? '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="currentColor" d="M12 2c1 4 5 5.5 5 11a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-4-1-6 1-10z"/></svg>On fire' : n + ' in a row' + (n >= 3 ? '!' : ''));
  c.classList.toggle('hot', n >= 5);
  if (bar) c.style.top = (bar.getBoundingClientRect().top + bar.offsetHeight / 2 - slot.getBoundingClientRect().top - c.offsetHeight / 2) + 'px';
  c.getAnimations().forEach(a => a.cancel());
  if (calm()) { c.style.opacity = 1; clearTimeout(c._t); c._t = setTimeout(() => c.style.opacity = 0, 1500); return; }
  c.animate([{ transform: 'scale(.3)', opacity: 0 }, { transform: 'scale(1.2)', opacity: 1, offset: .16 }, { transform: 'scale(1)', opacity: 1, offset: .28 }, { transform: 'scale(1)', opacity: 1, offset: .86 }, { transform: 'scale(.9)', opacity: 0 }], { duration: 1700, easing: 'ease-out' });
}

// every 5th correct answer in a row: the coach hops big for a second (never blocks a tap, nothing to dismiss)
function highFive() {
  const w = coach?.parentElement; hear('flourish'); buzz('ok');
  chip(combo, 'High five!');
  if (!w || w.classList.contains('away') || calm()) return;
  w.animate([{ scale: '1', translate: '0 0' }, { scale: '1.45', translate: '-8px 6px', offset: .3 }, { scale: '1.3', translate: '-6px 4px', offset: .7 }, { scale: '1', translate: '0 0' }], { duration: 1200, easing: 'cubic-bezier(.3,1.5,.5,1)' });
  sparkle(w, 12);
}

function right(els, solo) {
  const el = els[0], inLesson = !!document.querySelector('.lesson');
  if (inLesson && solo) combo++; else if (!inLesson) combo = 0;
  hear('chime', inLesson && solo ? combo - 1 : 0); buzz('ok');
  if (solo) { bounce(el); sparkle(el, 10); } else { els.slice(0, 4).forEach(bounce); sparkle(el, 10); }
  if (inLesson) {
    mood('cheer', 1500);
    const les = document.querySelector('.lesson'); if (solo) les.dataset.combo = Math.min(combo, 6);
    if (solo && combo >= 2) setTimeout(() => combo % 5 === 0 ? highFive() : chip(combo), 100);   // label lands ~100 ms after the answer (Duolingo rule 4)
  }
}
let misses = 0;
function wrong(els) {
  const inLesson = !!document.querySelector('.lesson');
  if (inLesson) { combo = 0; delete document.querySelector('.lesson').dataset.combo; }   // quiet reset: no message on a miss
  hear('boop'); buzz('no'); wobble(els[0]);
  if (inLesson) mood(++misses % 2 ? 'listen' : 'think', 1700);
  hintRight(els[0]);
}
// neutral "here is the answer": after a miss on a hear-and-tap drill, softly glow the tile that was the answer (no state change, still tappable)
function hintRight(tile) {
  if (!tile.matches?.('.tile') || calm()) return;
  if (!C?.by) return;
  const tapped = C.by[tile.textContent.trim()]?.id; if (!tapped) return;
  const want = [...plays].reverse().find(k => k.startsWith('names/') && k.slice(6) !== tapped)?.slice(6); if (!want) return;
  setTimeout(() => { const t = [...tile.parentElement?.querySelectorAll('.tile') || []].find(x => C.by[x.textContent.trim()]?.id === want && !x.classList.contains('no')); if (t?.isConnected) t.animate([{ boxShadow: '0 0 0 0 color-mix(in srgb,var(--good) 55%,transparent)' }, { boxShadow: '0 0 0 9px color-mix(in srgb,var(--good) 28%,transparent)', offset: .5 }, { boxShadow: '0 0 0 0 transparent' }], { duration: 1100, iterations: 2, easing: 'ease-in-out' }); }, 800);
}

// next question: the new tiles pop in from large (Duolingo rule 7, ~300 ms)
function popIn(tiles) { if (calm()) return; tiles.forEach((t, i) => t.animate([{ scale: '1.28', opacity: .2 }, { scale: '.97', opacity: 1, offset: .65 }, { scale: '1', opacity: 1 }], { duration: 300, delay: i * 35, easing: 'ease-out', fill: 'backwards' })); }

let lastOk = 0;
function scan(ms) {
  const oks = [], nos = [], soft = [];
  for (const m of ms) {
    const t = m.target;
    if (m.type === 'attributes' && t.nodeType === 1) {
      if (t.closest?.('svg')) continue;
      const was = (m.oldValue || '').split(/\s+/), now = t.classList;
      if (t.matches('.tile')) { if (now.contains('ok') && !was.includes('ok')) oks.push(t); else if (now.contains('no') && !was.includes('no')) nos.push(t); }
      else if (t.matches('.answer') && now.contains('no') && !was.includes('no')) nos.push(t);
    } else if (m.type === 'childList') {
      if (t.id === 'toast' && /^Correct/.test(t.textContent) && performance.now() - lastOk > 250) soft.push(document.querySelector('.answer') || t);
      if (t.matches?.('.score') && t.textContent.includes('✓ good')) soft.push(t);
      if (t.matches?.('.choices') && t.closest('.lesson')) { const ts = [...m.addedNodes].filter(n => n.matches?.('.tile')); if (ts.length > 1) popIn(ts); }
    }
  }
  if (!oks.length && soft.length) oks.push(soft[0]);                                   // toast / trace verdicts only when no tile already said it
  if (oks.length) { lastOk = performance.now(); right(oks, oks.length === 1 && !nos.length); } else if (nos.length) wrong(nos);
  if (oks.length && nos.length) mood(oks.length >= nos.length ? 'cheer' : 'think', 1500);
  const cur = document.querySelector('.lesson');
  if (cur && cur.firstElementChild !== lessonHead) enterLesson(cur); else if (!cur && lessonHead) { lessonHead = null; coach = null; }
  if (cur) syncCoach();
  injectSwitch();
}
/* ---------------------------------------------------------- settings switch ---- */
function injectSwitch() {
  const card = [...document.querySelectorAll('#app .card')].find(c => c.querySelector(':scope > h2')?.textContent === 'Settings' && !c.querySelector('.feel-sw'));
  if (!card) return;
  const l = document.createElement('label'); l.className = 'row feel-sw';
  l.innerHTML = `<input type="checkbox" ${on() ? 'checked' : ''}> Sounds and vibration`;
  l.querySelector('input').onchange = e => { app.set('feel', e.target.checked); if (e.target.checked) { unlock(); setTimeout(() => hear('chime', 0), 50); } };
  card.append(l);
}

export function initFeel(ctx) {
  app = ctx;
  window.__feel = { chime: lvl => hear('chime', lvl), boop: () => hear('boop') }; // for stickers.js / learner.js (silent when the Sounds switch is off)
  document.addEventListener('pointerdown', down, { passive: true, capture: true });
  ['pointerup', 'pointercancel', 'dragstart'].forEach(ev => document.addEventListener(ev, up, { passive: true, capture: true }));
  document.addEventListener('touchend', unlock, { passive: true }); document.addEventListener('keydown', unlock, { passive: true });
  new MutationObserver(scan).observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'], attributeOldValue: true });
}
