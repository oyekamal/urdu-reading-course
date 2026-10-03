// Restore from a backup file: pick, size-check, parse, validate, import atomically, and say clearly what happened.
// restoreFromFile(file, { onDone }) never throws and never fails silently. pickAndRestore(opts) opens the file chooser.
import { db } from './db.js';
import { toast } from './content.js';
import { confirmSheet } from './a11y.js';
import { MAX_BACKUP_BYTES, BackupError } from './backup.js';
let busy = false;
export async function restoreFromFile(file, { onDone } = {}) {
  if (busy) return false; busy = true;
  try {
    if (!file) { toast('No file was chosen.'); return false; }
    if (file.size > MAX_BACKUP_BYTES) { toast(`That file is too big to be a backup (${Math.round(file.size / 1048576)} MB).`); return false; }
    let text; try { text = await file.text(); } catch (e) { toast('The file could not be read.'); return false; }
    if (text.length > MAX_BACKUP_BYTES) { toast('That file is too big to be a backup.'); return false; }
    let data; try { data = JSON.parse(text); } catch (e) { toast('This file is not a backup: it is not valid JSON.'); return false; }
    // a restore that would replace records already on this phone says so first (names shown as text, never parsed)
    try { const pv = await db.previewImport(data); if (pv.replace > 0) { const names = pv.learners.slice(0, 6).join(', ') + (pv.learners.length > 6 ? ', ...' : ''); if (!await confirmSheet({ title: 'Replace data on this phone?', body: `This backup has ${pv.learners.length} ${pv.learners.length === 1 ? 'learner' : 'learners'}${names ? ' (' + names + ')' : ''}. It adds ${pv.add} new ${pv.add === 1 ? 'record' : 'records'} and replaces ${pv.replace} that are already here with the backup's version.`, yes: 'Replace', no: 'Cancel' })) { toast('Nothing was changed.'); return false; } } }
    catch (e) { toast(e instanceof BackupError ? e.message : 'The backup could not be read. Nothing was changed.'); return false; }
    let n; try { n = await db.importAll(data); } catch (e) { toast(e instanceof BackupError ? e.message : 'The backup could not be restored. Nothing was changed. ' + (e && e.message ? e.message : '')); return false; }
    toast(n ? `Restored ${n} ${n === 1 ? 'record' : 'records'}.` : 'Nothing new to restore: this phone already has everything in that file.');
    try { if (onDone) await onDone(n); } catch (e) { toast('Restored, but this screen could not refresh. Go back and open it again.'); }
    return true;
  } finally { busy = false; }
}
export function pickAndRestore(opts) {
  const inp = document.createElement('input'); inp.type = 'file'; inp.accept = '.json,application/json'; inp.style.display = 'none';
  inp.onchange = () => { const f = inp.files && inp.files[0]; inp.remove(); restoreFromFile(f, opts); };
  document.body.append(inp); inp.click();
}
