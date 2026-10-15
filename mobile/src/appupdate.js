// Android app updates: asks Google Play whether a newer version is published and offers it in a small banner (same look as the
// web "update ready" toast in swreg.js). Only on the installed app from Play; sideloaded or web builds get "not available" and stay silent.
// The tap sits behind the grown-up gate like every other external action. Dismissed banners stay away for 3 days.
import { askGrownup } from './gate.js';
import { toast } from './content.js';
const native = (() => { try { return !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()); } catch (e) { return false; } })();
const SNOOZE_KEY = 'urdu-update-snooze', DAY = 864e5; let shown = false, lastCheck = 0;
export const canCheckForUpdate = native;
const snoozed = () => { try { return Date.now() < Number(localStorage.getItem(SNOOZE_KEY) || 0); } catch (e) { return false; } };
const snooze = () => { try { localStorage.setItem(SNOOZE_KEY, String(Date.now() + 3 * DAY)); } catch (e) { /* private mode */ } };
export async function checkForUpdate(manual = false) {
  if (!native || (shown && !manual)) return;
  try {
    const { AppUpdate } = await import('@capawesome/capacitor-app-update'); const info = await AppUpdate.getAppUpdateInfo();
    if (info.updateAvailability !== 2) { if (manual) toast('You have the latest version.'); return; }  // 2 = UPDATE_AVAILABLE
    if (!manual && snoozed()) return;
    banner(AppUpdate, info);
  } catch (e) { if (manual) toast('Could not check right now. Try again later.'); }
}
function banner(AppUpdate, info) {
  if (shown) return; shown = true;
  const t = document.createElement('div'); t.className = 'sw-toast'; t.setAttribute('role', 'status');
  const go = document.createElement('button'); go.type = 'button'; go.className = 'sw-go'; go.textContent = 'New version ready · Update';
  const x = document.createElement('button'); x.type = 'button'; x.className = 'sw-x'; x.setAttribute('aria-label', 'Not now'); x.textContent = '×';
  x.onclick = () => { snooze(); t.remove(); shown = false; };
  go.onclick = async () => {
    if (!await askGrownup({ title: 'Update Urdu Qaida', note: 'This opens Google Play. Grown-ups only, please.' })) return;
    try { if (info.immediateUpdateAllowed) await AppUpdate.performImmediateUpdate(); else await AppUpdate.openAppStore(); }
    catch (e) { try { await AppUpdate.openAppStore(); } catch (e2) { toast('Open Google Play and update Urdu Qaida there.'); } }
  };
  t.append(go, x); document.body.append(t);
}
if (native) {
  setTimeout(() => { lastCheck = Date.now(); checkForUpdate(); }, 8000);  // after the first screen, never competing with it
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && Date.now() - lastCheck > 6 * 3600e3) { lastCheck = Date.now(); checkForUpdate(); } });
}
