// One-tap Appearance switch: phone setting -> Light -> Dark. Lives in the page header and on the learner picker so it is easy to find;
// the Settings card on the Me tab keeps the full dropdown. ctx.set writes the setting and re-applies data-theme (main.js apply()).
import { icon } from './icons.js';
import { toast } from './content.js';
const ORDER = ['', 'light', 'dark'], NAME = { '': 'Match my phone', light: 'Light', dark: 'Dark' }, IC = { '': 'contrast', light: 'sun', dark: 'moon' };
export function themeChip(ctx) {
  const b = document.createElement('button'); b.type = 'button'; b.className = 'btn theme-chip';
  const paint = () => { const t = ctx.settings.theme || ''; b.innerHTML = icon(IC[t]); b.setAttribute('aria-label', `Appearance: ${NAME[t]}. Tap to change.`); b.title = NAME[t]; };
  b.onclick = async () => { const next = ORDER[(ORDER.indexOf(ctx.settings.theme || '') + 1) % 3]; await ctx.set('theme', next); paint(); toast(NAME[next]); };
  paint(); return b;
}
