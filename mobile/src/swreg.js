// Service worker registration + "update ready" toast (round 11p). A module (not inline) so the production CSP can say script-src 'self'.
// Capacitor (the Android app) serves its own files, so it skips the worker; the dev server never registers one (and clears any old one).
//   - registered after the page has loaded and gone idle, so the precache download never competes with the first screen
//   - when a newer build installs, a small non-blocking toast offers "Update ready, tap to refresh"; tapping activates it and reloads once
//   - once the first lesson finishes (the .celebrate screen) and the browser is idle, the worker is asked to warm the audio cache in the background
//   - checks for a newer build whenever the app comes back to the foreground (at most every 20 minutes)
// NOT `!window.Capacitor`: @capacitor/core defines that global on the plain web too once the bundle has run (the old inline script ran before it)
const native = (() => { try { return !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()); } catch (e) { return false; } })();
const sw = navigator.serviceWorker;
if (sw && !native) {
  if (import.meta.env?.DEV) sw.getRegistrations().then(rs => rs.forEach(r => r.unregister())).catch(() => {});
  else start();
}

function start() {
  let wantReload = false, shown = false, lastCheck = Date.now(), regRef = null;
  const hadController = !!sw.controller;
  let reloaded = false;
  const idle = fn => (window.requestIdleCallback ? requestIdleCallback(fn, { timeout: 4000 }) : setTimeout(fn, 1500));
  const whenLoaded = fn => (document.readyState === 'complete' ? fn() : addEventListener('load', fn, { once: true }));

  function toast(worker) {
    if (shown) return; shown = true;
    const t = document.createElement('div'); t.className = 'sw-toast'; t.setAttribute('role', 'status');
    const go = document.createElement('button'); go.type = 'button'; go.className = 'sw-go'; go.textContent = 'Update ready, tap to refresh';
    const x = document.createElement('button'); x.type = 'button'; x.className = 'sw-x'; x.setAttribute('aria-label', 'Not now'); x.textContent = '×';
    go.onclick = () => {
      wantReload = true; go.disabled = true; go.textContent = 'Updating…';
      const w = (regRef && regRef.waiting) || worker;   // the NEWEST waiting worker (a later deploy replaces the one the toast was made for)
      if (w && w.state !== 'redundant' && w.state !== 'activated') w.postMessage({ type: 'SKIP_WAITING' });
      else location.reload();                           // already active: just load it
      // belt and braces: if the page is still here after a moment (message lost, worker replaced), ask again, then load whatever is current
      setTimeout(() => { const n = regRef && regRef.waiting; if (n) n.postMessage({ type: 'SKIP_WAITING' }); }, 2500);
      setTimeout(() => { if (!reloaded) { reloaded = true; location.reload(); } }, 6000);
    };
    x.onclick = () => { t.remove(); shown = false; };
    t.append(go, x); document.body.append(t);
  }

  function watch(reg) {
    regRef = reg;
    const onInstalled = w => w.addEventListener('statechange', () => { if (w.state === 'installed' && sw.controller) setTimeout(() => { if (reg.waiting === w) toast(w); }, 300); });   // a self-activating worker (first install / legacy upgrade) never shows it
    if (reg.waiting && sw.controller) toast(reg.waiting);
    if (reg.installing) onInstalled(reg.installing);
    reg.addEventListener('updatefound', () => reg.installing && onInstalled(reg.installing));
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && Date.now() - lastCheck > 20 * 60 * 1000) { lastCheck = Date.now(); reg.update().catch(() => {}); }
    });
    // background warm-up of the audio cache after the first finished lesson
    const mo = new MutationObserver(() => {
      if (!document.querySelector('body > .celebrate')) return; mo.disconnect();
      idle(() => { const w = reg.active || sw.controller; w && w.postMessage({ type: 'WARM' }); });
    });
    mo.observe(document.body, { childList: true });
    window.__swReg = reg;
  }

  // a new worker took over because the user asked for it: load the new build once (never on the very first claim)
  // (also in a second tab that the new worker claimed: its shell is the old build, so it must reload too; never on a first-install claim)
  sw.addEventListener('controllerchange', () => { if ((wantReload || hadController) && !reloaded) { reloaded = true; location.reload(); } });

  whenLoaded(() => idle(() => {
    const saver = navigator.connection && navigator.connection.saveData;
    if (saver && !sw.controller) return;   // data saver on and nothing installed yet: stay online-only rather than pull ~2 MB
    sw.register('./sw.js').then(watch).catch(() => {});
  }));
}
