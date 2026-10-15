// Android hardware/gesture Back. Order: close the open dialog or overlay, then the screen's own "up" handler (learner.js), then any
// visible Back / leave-lesson button, and only on the home screen ask twice before the app closes. Also keeps focused fields above the keyboard.
import { toast } from './content.js';
const native = (() => { try { return !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()); } catch (e) { return false; } })();
const OVERLAYS = 'body > .gate-back, body > .a11y-sheet, body > .pr-ov, body > .stk-ov';
const CLOSERS = '.gate-cancel, .stk-back, .pr-back, [aria-label="Back"], [aria-label="Close"]';
const SCREEN_BACK = '#app button[aria-label="Leave lesson"], #app button[aria-label="Back to path"], #app button[aria-label="Back"], #app .page-back';
let handler = null, lastBack = 0;
export const setBack = fn => { handler = fn; };            // the current screen's "go up one level": returns true when it handled it
export function handleBack() {
  const ov = [...document.querySelectorAll(OVERLAYS)].pop();
  if (ov) { if (ov._cancel) ov._cancel(); else ov.querySelector(CLOSERS)?.click(); return true; }
  if (handler && handler()) return true;
  const b = [...document.querySelectorAll(SCREEN_BACK)].find(x => x.offsetParent !== null);
  if (b) { b.click(); return true; }
  const plain = [...document.querySelectorAll('#app button')].find(x => /^\s*Back\s*$/.test(x.textContent) && x.offsetParent !== null);
  if (plain) { plain.click(); return true; }
  return false;
}
async function onBack() {
  if (handleBack()) return;
  const now = Date.now(); if (now - lastBack < 2000) { try { (await import('@capacitor/app')).App.exitApp(); } catch (e) { /* web */ } return; }
  lastBack = now; toast('Press back again to close the app');
}
if (native) {
  import('@capacitor/app').then(({ App }) => App.addListener('backButton', onBack)).catch(() => {});
  // the keyboard overlays the page on Android's edge-to-edge window: lift the page by its height and keep the focused field in view
  import('@capacitor/keyboard').then(({ Keyboard }) => {
    const set = h => document.documentElement.style.setProperty('--kb', h + 'px');
    Keyboard.addListener('keyboardWillShow', e => { set(e.keyboardHeight || 0); document.body.classList.add('kb-open'); setTimeout(() => document.activeElement?.scrollIntoView?.({ block: 'center', behavior: 'smooth' }), 120); });
    Keyboard.addListener('keyboardWillHide', () => { set(0); document.body.classList.remove('kb-open'); });
  }).catch(() => {});
}
