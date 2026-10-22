// One "new version" popup for both the Android Play update and the web service-worker update. Reuses the gate's backdrop/sheet look.
// updateDialog({ note, action }) -> { close, busy(text) }. `action` runs on Update; Later just closes (caller snoozes via onLater).
export function updateDialog({ note, action, onLater }) {
  const back = document.createElement('div'); back.className = 'gate-back upd-back';
  const sheet = document.createElement('div'); sheet.className = 'gate-sheet upd-sheet'; sheet.setAttribute('role', 'dialog'); sheet.setAttribute('aria-modal', 'true'); sheet.setAttribute('aria-label', 'Update available');
  sheet.innerHTML = '<div class="upd-ic" aria-hidden="true">⬆</div><h2>A new version is ready</h2><p class="muted"></p><button type="button" class="btn btn-primary btn-wide upd-go">Update now</button><button type="button" class="btn btn-chip btn-center upd-later">Later</button>';
  sheet.querySelector('p').textContent = note || 'New lessons and fixes are waiting.';
  back.append(sheet); document.body.append(back);
  const go = sheet.querySelector('.upd-go'), later = sheet.querySelector('.upd-later');
  const close = () => back.remove();
  later.onclick = () => { close(); onLater && onLater(); };
  go.onclick = () => { go.disabled = true; go.textContent = 'Updating…'; Promise.resolve(action()).catch(() => {}).finally(() => { go.disabled = false; go.textContent = 'Update now'; }); };
  go.focus();
  return { close };
}
