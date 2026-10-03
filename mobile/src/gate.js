// Grown-up gate: an in-app bottom sheet. A two-digit number is spelled out in Urdu and English words; the adult types it
// as digits. A child who is still learning to read Urdu cannot do it. 3 wrong tries = 30 s calm lockout (no punishing timers).
// askGrownup(opts?) -> Promise<boolean>. opts: { title, note }. Also on window.__gate.
const UR = {
  10: 'دس', 11: 'گیارہ', 12: 'بارہ', 13: 'تیرہ', 14: 'چودہ', 15: 'پندرہ', 16: 'سولہ', 17: 'سترہ', 18: 'اٹھارہ', 19: 'انیس',
  20: 'بیس', 21: 'اکیس', 22: 'بائیس', 23: 'تیئس', 24: 'چوبیس', 25: 'پچیس', 26: 'چھبیس', 27: 'ستائیس', 28: 'اٹھائیس', 29: 'انتیس',
  30: 'تیس', 31: 'اکتیس', 32: 'بتیس', 33: 'تینتیس', 34: 'چونتیس', 35: 'پینتیس', 36: 'چھتیس', 37: 'سینتیس', 38: 'اڑتیس', 39: 'انتالیس',
  40: 'چالیس', 41: 'اکتالیس', 42: 'بیالیس', 43: 'تینتالیس', 44: 'چوالیس', 45: 'پینتالیس', 46: 'چھیالیس', 47: 'سینتالیس', 48: 'اڑتالیس', 49: 'انچاس',
  50: 'پچاس', 51: 'اکیاون', 52: 'باون', 53: 'ترپن', 54: 'چون', 55: 'پچپن', 56: 'چھپن', 57: 'ستاون', 58: 'اٹھاون', 59: 'انسٹھ',
  60: 'ساٹھ', 61: 'اکسٹھ', 62: 'باسٹھ', 63: 'ترسٹھ', 64: 'چونسٹھ', 65: 'پینسٹھ', 66: 'چھیاسٹھ', 67: 'سڑسٹھ', 68: 'اڑسٹھ', 69: 'انہتر',
  70: 'ستر', 71: 'اکہتر', 72: 'بہتر', 73: 'تہتر', 74: 'چوہتر', 75: 'پچھتر', 76: 'چھہتر', 77: 'ستتر', 78: 'اٹھہتر', 79: 'اناسی',
  80: 'اسی', 81: 'اکیاسی', 82: 'بیاسی', 83: 'تراسی', 84: 'چوراسی', 85: 'پچاسی', 86: 'چھیاسی', 87: 'ستاسی', 88: 'اٹھاسی', 89: 'نواسی',
  90: 'نوے', 91: 'اکانوے', 92: 'بانوے', 93: 'ترانوے', 94: 'چورانوے', 95: 'پچانوے', 96: 'چھیانوے', 97: 'ستانوے', 98: 'اٹھانوے', 99: 'ننانوے',
};
const ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'];
const TEENS = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'];
const TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'];
const en = n => n < 10 ? ONES[n] : n < 20 ? TEENS[n - 10] : TENS[Math.floor(n / 10)] + (n % 10 ? '-' + ONES[n % 10] : '');
const LOCK_MS = 30000, MAX_TRIES = 3, LOCK_KEY = 'urdu-gate-lock', TRY_KEY = 'urdu-gate-tries';

const pick = () => { let n; do { n = 13 + Math.floor(Math.random() * 86); } while (n % 10 === 0); return n; };
const digits = s => String(s).replace(/[۰-۹]/g, c => String(c.charCodeAt(0) - 0x06F0)).replace(/[٠-٩]/g, c => String(c.charCodeAt(0) - 0x0660)).replace(/\s+/g, '');
const readLock = () => { try { return Number(localStorage.getItem(LOCK_KEY)) || 0; } catch (e) { return mem.lock; } };
const writeLock = t => { mem.lock = t; try { localStorage.setItem(LOCK_KEY, String(t)); } catch (e) { /* private mode */ } };
const mem = { lock: 0, open: null, tries: 0 };
// the wrong-try counter survives closing the sheet and reloading the app, so a child cannot brute-force by restarting
const readTries = () => { try { return Number(localStorage.getItem(TRY_KEY)) || 0; } catch (e) { return mem.tries; } };
const writeTries = n => { mem.tries = n; try { localStorage.setItem(TRY_KEY, String(n)); } catch (e) { /* private mode */ } };

export function askGrownup(opts = {}) {
  if (mem.open) return Promise.resolve(false); // a second request while a gate is open is refused, never approved by the first answer
  const prev = document.activeElement;
  const root = document.createElement('div'); root.className = 'gate-back';
  const sheet = document.createElement('div'); sheet.className = 'gate-sheet'; sheet.setAttribute('role', 'dialog'); sheet.setAttribute('aria-modal', 'true'); sheet.setAttribute('aria-labelledby', 'gate-title'); sheet.setAttribute('aria-describedby', 'gate-desc');
  sheet.innerHTML = `<h2 id="gate-title"></h2><p id="gate-desc" class="muted"></p>
    <div class="gate-num" aria-live="polite"><div class="gate-ur" lang="ur" dir="rtl"></div><div class="gate-en" lang="en"></div></div>
    <label class="gate-label" for="gate-input">Type this number with digits</label>
    <input id="gate-input" class="gate-input" type="text" inputmode="numeric" pattern="[0-9]*" autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="4" enterkeyhint="done">
    <p class="gate-msg muted" role="status" aria-live="polite"></p>
    <div class="gate-actions"><button type="button" class="btn gate-cancel">Close</button><button type="button" class="btn btn-primary gate-ok">Continue</button></div>`;
  root.append(sheet); document.body.append(root);
  const $ = s => sheet.querySelector(s);
  $('#gate-title').textContent = opts.title || 'For grown-ups';
  $('#gate-desc').textContent = opts.note || 'This part is for parents and teachers. Please read the number and type it.';
  const input = $('#gate-input'), msg = $('.gate-msg'), ok = $('.gate-ok'), cancel = $('.gate-cancel');
  let n = pick(), tick = null, done = false, resolve;
  const show = () => { $('.gate-ur').textContent = UR[n]; $('.gate-en').textContent = en(n); input.value = ''; };
  const locked = () => readLock() - Date.now() > 0;
  const paintLock = () => {
    const left = Math.ceil((readLock() - Date.now()) / 1000);
    if (left > 0) { input.disabled = true; ok.disabled = true; msg.textContent = `Let us pause for a moment. You can try again in ${left} seconds.`; }
    else { clearInterval(tick); tick = null; input.disabled = false; ok.disabled = false; writeTries(0); n = pick(); show(); msg.textContent = 'Ready when you are.'; try { input.focus(); } catch (e) { /* ignore */ } }
  };
  const finish = v => {
    if (done) return; done = true; clearInterval(tick); document.removeEventListener('keydown', onKey, true);
    root.classList.add('out'); setTimeout(() => root.remove(), 120); mem.open = null;
    try { document.body.classList.remove('gate-open'); if (prev && prev.focus) prev.focus(); } catch (e) { /* ignore */ }
    resolve(v);
  };
  const submit = () => {
    if (locked()) return paintLock();
    if (digits(input.value) === String(n)) return finish(true);
    writeTries(readTries() + 1);
    if (readTries() >= MAX_TRIES) { writeLock(Date.now() + LOCK_MS); tick = setInterval(paintLock, 500); return paintLock(); }
    msg.textContent = 'That is not it. No problem, here is a new number.'; n = pick(); show(); input.focus();
  };
  const onKey = e => {
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); finish(false); return; }
    if (e.key === 'Tab') {
      const f = [...sheet.querySelectorAll('input,button')].filter(x => !x.disabled); if (!f.length) { e.preventDefault(); return; }
      const first = f[0], last = f[f.length - 1], a = document.activeElement;
      if (!sheet.contains(a)) { e.preventDefault(); first.focus(); }
      else if (e.shiftKey && a === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && a === last) { e.preventDefault(); first.focus(); }
    }
  };
  input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); submit(); } });
  input.addEventListener('input', () => { input.value = digits(input.value).replace(/\D/g, '').slice(0, 4); });
  ok.addEventListener('click', submit); cancel.addEventListener('click', () => finish(false));
  root.addEventListener('click', e => { if (e.target === root) finish(false); });
  document.addEventListener('keydown', onKey, true);
  document.body.classList.add('gate-open');
  show();
  if (locked()) { tick = setInterval(paintLock, 500); paintLock(); } else msg.textContent = '';
  setTimeout(() => { try { (input.disabled ? cancel : input).focus(); } catch (e) { /* ignore */ } }, 30);
  mem.open = new Promise(r => { resolve = r; });
  return mem.open;
}
if (typeof window !== 'undefined') window.__gate = { askGrownup };
