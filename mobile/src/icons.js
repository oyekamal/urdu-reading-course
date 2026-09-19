// Inline SVG icon set: 2px rounded strokes, 24-unit grid, currentColor. No emoji anywhere in the app.
const P = (d, extra = '') => `<svg viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}${extra}</svg>`;
export const I = {
  home: P('<path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z"/>'),
  units: P('<rect x="3" y="4" width="7" height="7" rx="2"/><rect x="14" y="4" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>'),
  review: P('<path d="M4 12a8 8 0 0 1 13.7-5.7L20 8"/><path d="M20 4v4h-4"/><path d="M20 12a8 8 0 0 1-13.7 5.7L4 16"/><path d="M4 20v-4h4"/>'),
  read: P('<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H12v16H6.5A2.5 2.5 0 0 0 4 21z"/><path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H12v16h5.5A2.5 2.5 0 0 1 20 21z"/>'),
  progress: P('<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/>'),
  more: P('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'),
  play: P('<path d="M7 5v14l11-7z" fill="currentColor" stroke="none"/>'),
  speaker: P('<path d="M4 10v4h3l4 4V6L7 10z" fill="currentColor" stroke="none"/><path d="M15 9a4 4 0 0 1 0 6"/><path d="M18 6a8 8 0 0 1 0 12"/>'),
  ear: P('<path d="M6 9a6 6 0 0 1 12 0c0 3-2 4-3 6s-1 4-4 4"/><path d="M10 9a2 2 0 0 1 4 0c0 2-2 2-2 4"/>'),
  eye: P('<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'),
  pen: P('<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>'),
  blend: P('<circle cx="9" cy="12" r="5"/><circle cx="15" cy="12" r="5"/>'),
  link: P('<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>'),
  puzzle: P('<path d="M4 8h4a2 2 0 1 1 4 0h4v4a2 2 0 1 0 0 4v4h-4a2 2 0 1 1-4 0H4v-4a2 2 0 1 1 0-4z"/>'),
  book: P('<path d="M4 4h12a3 3 0 0 1 3 3v13H7a3 3 0 0 0-3 3z"/><path d="M4 4v16"/><path d="M8 8h7M8 12h7"/>'),
  flag: P('<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>'),
  timer: P('<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2"/><path d="M9 2h6"/>'),
  check: P('<path d="M5 12l5 5L20 7"/>'),
  cross: P('<path d="M6 6l12 12M18 6 6 18"/>'),
  lock: P('<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>'),
  star: P('<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" fill="currentColor" stroke="none"/>'),
  marks: P('<path d="M6 16h12"/><path d="M11 8h2"/><path d="M12 5v1"/><path d="M8 20h8"/>'),
  door: P('<path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16"/><path d="M3 21h18"/><circle cx="14.5" cy="12" r="1" fill="currentColor"/>'),
  numbers: P('<path d="M4 8h3v8"/><path d="M11 9a2 2 0 1 1 4 0c0 2-4 3-4 5h4"/><path d="M18 8h3l-2 3a2 2 0 1 1-1.5 3.5"/>'),
  sight: P('<path d="M3 12c2.7-4 5.7-6 9-6s6.3 2 9 6c-2.7 4-5.7 6-9 6s-6.3-2-9-6z"/><path d="M9.5 12a2.5 2.5 0 1 0 5 0 2.5 2.5 0 1 0-5 0"/><path d="M12 3v2M12 19v2"/>'),
  script: P('<path d="M20 6c-4 0-6 3-9 3S6 6 4 6"/><path d="M20 12c-4 0-6 3-9 3s-5-3-7-3"/><path d="M20 18c-4 0-6 3-9 3s-5-3-7-3"/>'),
  class: P('<circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M2 20a6 6 0 0 1 12 0"/><path d="M12 20a6 6 0 0 1 10 0"/>'),
  back: P('<path d="M15 6l-6 6 6 6"/>'),
  next: P('<path d="M9 6l6 6-6 6"/>'),
  repeat: P('<path d="M4 10a8 8 0 0 1 13.7-5.7L20 6"/><path d="M20 2v4h-4"/><path d="M20 14a8 8 0 0 1-13.7 5.7L4 18"/><path d="M4 22v-4h4"/>'),
  share: P('<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.6M8.2 13.2l7.6 4.6"/>'),
  user: P('<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>'),
  family: P('<circle cx="8" cy="7" r="3"/><circle cx="16" cy="9" r="2.5"/><path d="M2 20a6 6 0 0 1 12 0"/><path d="M13 20a5 5 0 0 1 9 0"/>'),
  school: P('<path d="M3 21V10l9-6 9 6v11"/><path d="M9 21v-6h6v6"/><path d="M3 21h18"/>'),
  plus: P('<path d="M12 5v14M5 12h14"/>'),
  parent: P('<path d="M4 20V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12"/><path d="M8 11h8M8 15h5"/>'),
  sparkle: P('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>'),
};
export const icon = (name, cls = '') => `<span class="ic ${cls}">${I[name] || I.star}</span>`;
export const LESSON_ICON = { rules: 'door', marks: 'marks', done: 'flag', letter: null, aspirates: 'ear', join: 'link', blend: 'blend', words: 'puzzle', nonjoin: 'link', read: 'book', marks2: 'numbers', sight: 'sight', nastaliq: 'script', test: 'timer', quiz: 'flag' };
// Toto the parrot. poses: hello listen think cheer oops sleep read point
export const mascot = (pose, size = 120, cls = '') => `<img class="mascot ${cls}" src="./img/mascot_${pose}.webp" width="${size}" height="${size}" alt="" style="width:${size}px;height:${size}px">`;
export const unitArt = (n) => `<img class="unit-art" src="./img/unit_${String(n).padStart(2, '0')}.webp" alt="" loading="lazy">`;
// profile avatars: a colour disc with the initial (older profiles stored an emoji; those fall back to a colour by name)
export const AVATARS = ['#1E9C8F', '#F2A93B', '#C74A3B', '#2E3A8C', '#5FA55A', '#8B6F47', '#D97AA6', '#4A90D9'];
export const avatar = (p, size = 48) => { const c = /^#/.test(p.avatar || '') ? p.avatar : AVATARS[[...(p.name || '')].reduce((a, ch) => a + ch.charCodeAt(0), 0) % AVATARS.length]; return `<span class="avatar" style="background:${c};width:${size}px;height:${size}px;font-size:${size * .46}px">${[...(p.name || '?')][0].toUpperCase()}</span>`; };
export const confetti = (n = 18) => `<div class="confetti">${[...Array(n)].map((_, i) => `<i style="left:${Math.round(5 + i * 90 / n + Math.random() * 4)}%;background:${['#1E9C8F', '#F2A93B', '#C74A3B', '#2E3A8C', '#5FA55A'][i % 5]};animation-delay:${(Math.random() * .5).toFixed(2)}s;animation-duration:${(1.3 + Math.random() * .8).toFixed(2)}s"></i>`).join('')}</div>`;
