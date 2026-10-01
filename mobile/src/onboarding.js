// First-run onboarding (app-onboarding-questionnaire skill, benchmarked against Finch). Marko asks a few questions, the
// learner reads a first real word (بابا, from ا + ب alone), gets a shareable card, then lands on the path.
// Answers are saved after every step (db setting 'onb') so a closed app resumes where it stopped.
import { db } from './db.js';
import { C, play, el } from './content.js';
import { icon, mascot, confetti } from './icons.js';
import { fx, burst } from './fx.js';

const T = (who, me, child) => who === 'me' ? me : child;

export async function runOnboarding(root, { finish, teacherSetup }) {
  const st = (await db.setting('onb')) || { i: 0, a: {} }; const a = st.a;
  const save = () => db.setting('onb', { i: st.i, a });
  const nm = () => a.name || (a.who === 'me' ? 'you' : 'your child');
  const flow = [welcome, wake, colour, who, name, goal, speak, reads, pains, solution, minutes, processing, demo, value, streak, commit, plan];
  const Q0 = 3, Q1 = 10; // screens that show the progress bar (who … minutes)
  let timers = [];
  const later = (fn, ms) => timers.push(setTimeout(fn, ms));

  function show() {
    timers.forEach(clearTimeout); timers = []; root.innerHTML = ''; window.scrollTo(0, 0);
    const scr = el('div', 'ob'); root.append(scr);
    if (st.i >= Q0 && st.i <= Q1) {
      const top = el('div', 'ob-top'); const back = el('button', 'ob-back', icon('back')); back.setAttribute('aria-label', 'Back'); back.onclick = () => go(-1);
      top.append(back, el('div', 'ob-bar', `<i style="width:${Math.round((st.i - Q0 + 1) / (Q1 - Q0 + 1) * 100)}%"></i>`)); scr.append(top);
    }
    flow[st.i](scr);
  }
  function go(d = 1) { st.i = Math.max(0, Math.min(flow.length - 1, st.i + d)); if (flow[st.i] === name && a.who === 'class' && d > 0) return teacherSetup(); save(); show(); }
  // Marko says a line, speech-bubble style, first person (Finch's pet talks to you; ours is your teacher)
  const say = (pose, html, size = 120) => el('div', 'ob-say', `<span class="ob-m" style="--c:${a.colour || 'var(--gold)'}">${mascot(pose, size)}</span><div class="ob-bubble">${html}</div>`);
  // Marko answers every choice: swap pose + bubble line, then move on (Finch's pet talks back; a silent form does not)
  const react = (scr, pose, html) => { const s = scr.querySelector('.ob-say'); if (!s) return; s.querySelector('.ob-m').innerHTML = mascot(pose, s.querySelector('.mascot').width); s.classList.remove('bump'); void s.offsetWidth; s.classList.add('bump'); s.querySelector('.ob-bubble').innerHTML = html; };
  const cta = (label, fn, disabled) => { const b = el('button', 'btn btn-primary btn-wide ob-cta', label); b.disabled = !!disabled; b.onclick = fn; return b; };
  const foot = (scr, ...btns) => { const f = el('div', 'ob-foot'); f.append(...btns); scr.append(f); return f; };

  // one-tap options; single-select advances on tap (Finch pattern), multi-select toggles
  function options(scr, key, list, { multi = false, reply } = {}) {
    const box = el('div', 'ob-opts'); const cur = () => a[key] || (multi ? [] : null);
    let next;
    list.forEach(([v, ic, label, sub]) => {
      const b = el('button', 'ob-opt', `<span class="ob-ic">${icon(ic)}</span><span><b>${label}</b>${sub ? `<small>${sub}</small>` : ''}</span>${multi ? `<span class="ob-tick">${icon('check')}</span>` : ''}`);
      b.setAttribute('aria-pressed', multi ? cur().includes(v) : cur() === v);
      b.onclick = () => {
        if (multi) { const s = new Set(cur()); s.has(v) ? s.delete(v) : s.add(v); a[key] = [...s]; b.setAttribute('aria-pressed', s.has(v)); next.disabled = !s.size; save(); return; }
        a[key] = v; [...box.children].forEach(x => { x.setAttribute('aria-pressed', x === b); x.disabled = true; }); save(); const r = reply && reply(v); if (r) { react(scr, r[0], r[1]); play('ui/correct'); } later(() => go(1), r ? 1300 : 260);
      };
      box.append(b);
    });
    scr.append(box);
    if (multi) { next = cta('Continue', () => go(1), !cur().length); foot(scr, next); }
  }

  function welcome(scr) {
    scr.classList.add('ob-welcome');
    scr.append(el('div', 'ob-hero', `<div class="ob-sun fx-stage">${mascot('hello', 190)}</div><div class="ur nastaliq ob-kicker">اردو پڑھنا سیکھیں</div><h1>Read Urdu in ten minutes a day</h1><p class="muted">Hi, I'm Marko. I'll teach you the letters one at a time, and you'll read a real word in the next two minutes.</p>`));
    scr.querySelector('.ob-sun').prepend(fx('sparkles_loop', { size: 250, loop: true, cls: 'fx-over', speed: .6 }));
    foot(scr, el('p', 'muted center ob-small', 'Free, no account, works offline'), cta("Let's begin", () => { play('ui/welcome'); go(1); }));
  }
  function wake(scr) {
    scr.classList.add('ob-center');
    const m = el('button', 'ob-sleeper', mascot('sleep', 210)); m.prepend(fx('sleeping_zzz', { size: 90, loop: true, cls: 'fx-zz' })); m.setAttribute('aria-label', 'Wake Marko up');
    const cap = el('h2', 'center', 'Marko is fast asleep'); const sub = el('p', 'muted center', 'Tap him to wake him up.');
    m.onclick = () => { m.disabled = true; m.innerHTML = mascot('hello', 210); m.prepend(fx('sparkles_loop', { size: 240, cls: 'fx-over' })); m.classList.add('awake'); play('ui/welcome'); cap.textContent = 'Assalam-o-alaikum!'; sub.innerHTML = "Thanks for waking me. I'm <b>Marko</b>, and I teach reading."; later(() => go(1), 2200); };
    scr.append(m, cap, sub);
  }
  function colour(scr) {
    scr.classList.add('ob-center');
    const cols = [['#1E9C8F', 'turquoise'], ['#F2A93B', 'saffron'], ['#C74A3B', 'ajrak red'], ['#2E3A8C', 'indigo'], ['#5FA55A', 'green'], ['#D97AA6', 'pink']];
    a.colour = a.colour || cols[1][0]; save();
    const halo = el('div', 'ob-halo', mascot('point', 170)); halo.style.setProperty('--c', a.colour);
    const bub = el('div', 'ob-bubble', '<b>Pick my lucky colour!</b> It will be on your badge too.');
    const row = el('div', 'ob-swatches'); cols.forEach(([c, n]) => { const b = el('button', 'ob-sw'); b.style.background = c; b.setAttribute('aria-label', n); b.setAttribute('aria-pressed', a.colour === c);
      b.onclick = () => { a.colour = c; save(); halo.style.setProperty('--c', c); halo.classList.remove('bump'); void halo.offsetWidth; halo.classList.add('bump'); [...row.children].forEach(x => x.setAttribute('aria-pressed', x === b)); bub.innerHTML = `<b>Ooh, ${n}!</b> My favourite. Now it's ours.`; next.disabled = false; }; row.append(b); });
    const next = cta('This one', () => go(1));
    scr.append(halo, bub, row); foot(scr, next);
  }
  function who(scr) {
    scr.append(say('point', 'First things first. <b>Who is learning to read?</b>'));
    options(scr, 'who', [['me', 'user', 'Me', 'I want to read Urdu myself'], ['child', 'parent', 'My child', 'Ages 5 to 10, I will sit with them'], ['children', 'family', 'My children', 'Two or three learners on this phone'], ['class', 'school', 'My class', 'Teacher mode: roster, scripts, reading test']], { reply: v => ({ me: ['cheer', 'A grown-up reader! We are going to be <b>great friends</b>.'], child: ['cheer', 'Hooray, a <b>young reader</b>! I love teaching children.'], children: ['cheer', 'A whole family of readers! Let\'s start with <b>one</b>.'], class: ['cheer', 'A teacher! Let\'s set up <b>your class</b>.'] }[v]) });
  }
  function name(scr) {
    scr.append(say('hello', T(a.who, "I'm Marko. <b>What's your name?</b>", "I'm Marko. <b>What's your child's name?</b>"), 150));
    const inp = el('input', 'ob-name'); inp.id = 'ob-name'; inp.placeholder = T(a.who, 'Your name', "Child's name"); inp.value = a.name || ''; inp.maxLength = 24; inp.autocomplete = 'off'; inp.setAttribute('aria-label', inp.placeholder);
    const hi = el('div', 'ob-hi'); const next = cta('Continue', () => { a.name = inp.value.trim(); save(); go(1); }, !inp.value.trim());
    let greeted = false; const upd = () => { const v = inp.value.trim(); next.disabled = !v; hi.innerHTML = v ? `<span class="ob-badge" style="background:${a.colour || 'var(--accent)'}">${esc([...v][0].toUpperCase())}</span><span>${esc(v)}'s reading badge</span>` : ''; const line = v => `<b>${esc(v)}!</b> What a lovely name. Soon ${T(a.who, "you'll", esc(v) + ' will')} read it in Urdu.`; if (v && !greeted) { greeted = true; react(scr, 'cheer', line(v)); } else if (v) scr.querySelector('.ob-bubble').innerHTML = line(v); };
    inp.oninput = upd; inp.onkeydown = e => { if (e.key === 'Enter' && inp.value.trim()) next.click(); };
    scr.append(inp, hi); foot(scr, next); upd(); later(() => inp.focus(), 250);
  }
  function goal(scr) {
    scr.append(say('think', T(a.who, `<b>Why do you want to read Urdu, ${esc(a.name)}?</b>`, `<b>Why should ${esc(a.name)} learn to read Urdu?</b>`)));
    options(scr, 'goal', a.who === 'me'
      ? [['family', 'family', 'Read messages from family', 'WhatsApp, cards, notes from elders'], ['books', 'book', 'Read books and poetry', 'Stories, Ghalib, the news'], ['kids', 'parent', 'Help my children with Urdu', 'Stay one step ahead of them'], ['roots', 'sparkle', 'Reconnect with my roots', 'I speak it, I want to read it'], ['class', 'school', 'Pass an Urdu class or exam', ''], ['curious', 'eye', 'Just curious', 'The script is beautiful']]
      : [['school', 'school', 'Keep up in Urdu class', 'Homework, class readers'], ['family', 'family', 'Read with grandparents', 'Stories and messages at home'], ['start', 'flag', 'A head start before school', ''], ['abroad', 'sparkle', 'Keep our language alive', 'We live outside Pakistan'], ['stories', 'book', 'Enjoy Urdu stories', '']], { reply: v => ['cheer', GOAL_REPLY[v] || 'Lovely. <b>I can help with that.</b>'] });
  }
  function speak(scr) {
    scr.append(say('listen', T(a.who, '<b>How much Urdu do you speak?</b>', `<b>Does ${esc(a.name)} speak Urdu?</b>`)));
    options(scr, 'speak', [['fluent', 'ear', T(a.who, 'I speak it well', 'Yes, at home every day'), 'Reading is the missing part'], ['some', 'ear', T(a.who, 'I understand some', 'Understands, speaks a little'), ''], ['none', 'eye', T(a.who, "I'm new to Urdu", 'Not yet'), "I'll say what every word means"]], { reply: v => v === 'none' ? ['listen', 'No problem. I\'ll tell you <b>what every word means</b>.'] : ['cheer', 'Brilliant. Speaking is the hard part, <b>reading will come fast</b>.'] });
  }
  function reads(scr) {
    scr.append(say('read', T(a.who, '<b>Can you read any Urdu letters yet?</b>', `<b>Can ${esc(a.name)} read any Urdu letters yet?</b>`)));
    options(scr, 'reads', [['none', 'eye', 'Not a single one', 'Perfect, we start at alif'], ['few', 'puzzle', 'A few letters', 'A quick check after this skips what you know'], ['slow', 'book', 'Short words, slowly', 'A quick check finds your unit']], { reply: v => v === 'none' ? ['cheer', 'Everyone starts there. <b>We begin with alif</b>.'] : ['think', 'Nice! After this I\'ll give a <b>2-minute check</b> so we skip what you know.'] });
  }
  function pains(scr) {
    scr.append(say('think', `<b>What has made reading Urdu hard?</b><br><span class="muted">Pick all that sound familiar.</span>`));
    options(scr, 'pains', PAINS.map(([v, ic, label]) => [v, ic, label]), { multi: true });
  }
  function solution(scr) {
    const mine = (a.pains || []).map(v => PAINS.find(p => p[0] === v)).filter(Boolean).slice(0, 4);
    scr.append(say('surprised', `Good news, ${esc(a.name)}. <b>I built this for exactly that.</b>`, 96));
    const list = el('div', 'ob-fixes'); mine.forEach(([, ic, label, fix]) => list.append(el('div', 'ob-fix', `<span class="ob-ic">${icon(ic)}</span><div><small>${label}</small><b>${fix}</b></div>`))); scr.append(list);
    scr.append(el('p', 'ob-proof', `${icon('star')} The same letter-sound method raised Urdu reading by <b>12.6 words a minute</b> over normal classes in the USAID Pakistan Reading Project.`));
    foot(scr, cta('Show me', () => go(1)));
  }
  function minutes(scr) {
    scr.append(say('point', T(a.who, '<b>How much time can you give me a day?</b>', `<b>How long will ${esc(a.name)} practise a day?</b>`)));
    options(scr, 'minutes', [[5, 'blend', '5 minutes · gentle', 'One letter a day, unit 1 in about 2 weeks'], [10, 'timer', '10 minutes · steady', 'Most learners pick this, unit 1 in about a week'], [15, 'flag', '15 minutes · keen', 'Reading short sentences in about a month']], { reply: v => ['cheer', `${v} minutes it is. <b>That's about one cup of chai.</b>`] });
  }
  function processing(scr) {
    scr.classList.add('ob-center');
    const lines = [(a.pains || []).includes('dots') ? 'Grouping the look-alike letters' : `Picking ${T(a.who, 'your', a.name + "'s")} first letters: ا ب ک ل م ن`, `Setting a ${a.minutes || 10}-minute day`, a.speak === 'none' ? 'Adding the meaning of every word' : 'Leaving out English you already know', 'Getting Marko\'s voice ready'];
    const ms = 3000; const ring = el('div', 'ob-ring', `<span class="ob-m" style="--c:${a.colour || 'var(--gold)'}">${mascot('think', 130)}</span>`); ring.style.setProperty('--ms', ms + 'ms');
    const list = el('ul', 'ob-steps', lines.map(t => `<li>${icon('check')}<span>${t}</span></li>`).join(''));
    ring.append(fx('loading_dots', { size: 60, loop: true, cls: 'fx-ringtop' })); scr.append(ring, el('h2', 'center', `Making ${T(a.who, 'your', esc(a.name) + "'s")} path`), list);
    requestAnimationFrame(() => ring.classList.add('go'));
    [...list.children].forEach((li, i) => later(() => li.classList.add('done'), (i + 1) * ms / (lines.length + .5))); later(() => go(1), ms + 500);
  }

  // The demo: two letters, one blend, one word. Nothing on screen the learner has not just met.
  function demo(scr) {
    const steps = [meetA, meetB, tap, blend, word, check]; let k = 0;
    const stage = el('div', 'ob-demo'); const pips = el('div', 'ob-pips', steps.map(() => '<i></i>').join('')); scr.append(el('div', 'muted center ob-small', 'Your first lesson'), pips, stage);
    const step = () => { [...pips.children].forEach((p, i) => p.classList.toggle('on', i <= k)); stage.innerHTML = ''; steps[k](); };
    const nxt = (label = 'Next') => { const b = cta(label, () => { k++; k < steps.length ? step() : go(1); }); stage.append(b); return b; };
    const hear = (key, label) => { const b = el('button', 'btn btn-play btn-say', icon('speaker')); b.setAttribute('aria-label', label); b.onclick = () => play(key); return b; };
    function meetA() { stage.append(say('listen', `This is <b>alif</b>. It says <b>aa</b>, like in <i>father</i>.`, 84), el('button', 'ob-glyph ur', 'ا')); stage.lastChild.onclick = () => play('names/alif'); stage.lastChild.setAttribute('aria-label', 'Hear alif'); stage.append(hear('names/alif', 'Hear it again')); later(() => play('names/alif'), 400); nxt(); }
    function meetB() { stage.append(say('point', `This is <b>be</b>. It says <b>b</b>. See the <b>one dot</b> underneath?`, 84), el('button', 'ob-glyph ur', 'ب')); stage.lastChild.onclick = () => play('names/be'); stage.lastChild.setAttribute('aria-label', 'Hear be'); stage.append(hear('names/be', 'Hear it again')); later(() => play('names/be'), 400); nxt(); }
    function tap() {
      const order = ['ب', 'ا', 'ب']; let r = 0; const q = say('listen', '<b>Listen, then tap the letter you hear.</b>', 84); const row = el('div', 'choices ob-choices'); const again = hear('', 'Play again'); stage.append(q, again, row);
      const round = () => { const t = order[r]; const key = t === 'ا' ? 'names/alif' : 'names/be'; again.onclick = () => play(key); row.innerHTML = '';
        ['ا', 'ب'].forEach(c => { const b = el('button', 'tile ur', c); b.onclick = () => { if (c !== t) { b.classList.add('no'); play('ui/wrong'); later(() => b.classList.remove('no'), 500); return; } b.classList.add('ok'); play('ui/correct'); r++; later(() => r < order.length ? round() : (row.innerHTML = '', q.querySelector('.ob-bubble').innerHTML = '<b>Three out of three.</b> Your ears already know them.', nxt()), 650); }; row.append(b); }); later(() => play(key), 300); };
      round();
    }
    function blend() {
      stage.append(say('think', 'Put <b>be</b> before <b>alif</b> and they join into one sound. Urdu reads <b>right to left</b>.', 84));
      const j = el('div', 'ob-join', '<span class="ur ob-l">ا</span><span class="ur ob-r">ب</span><span class="ur ob-joined">با</span>'); stage.append(j);
      const b = cta(`${icon('blend')} Join them`); stage.append(b);
      b.onclick = () => { j.classList.add('go'); b.remove(); later(() => { play('syllables/be_a'); stage.append(el('div', 'say-row', '<p class="ob-say-line">b + aa = <b>baa</b></p>')); stage.lastChild.prepend(hear('syllables/be_a', 'Hear baa')); nxt('Now a whole word'); }, 700); };
    }
    function word() {
      const baba = C.units[1].words.findIndex(w => w[0] === 'بابا'); const key = `units/u01_${String(baba).padStart(2, '0')}`;
      stage.append(say('point', '<b>baa</b> twice. Say it out loud, then tap to check.', 84));
      const w = el('button', 'ob-word ur', 'بابا'); w.setAttribute('aria-label', 'Read the word, then tap to hear it'); stage.append(w);
      w.onclick = () => { if (w.classList.contains('read')) return play(key); w.classList.add('read'); play(key); stage.append(el('div', 'ob-meaning', '<b>baba</b> · dad'), confettiEl()); later(() => nxt('Check me'), 900); };
    }
    function check() {
      const baba = C.units[1].words.findIndex(w => w[0] === 'بابا'); const key = `units/u01_${String(baba).padStart(2, '0')}`;
      const q = say('listen', '<b>Last one.</b> Which one says <b>baba</b>?', 84); const row = el('div', 'choices ob-choices'); const again = hear(key, 'Play again'); stage.append(q, again, row);
      ['با', 'بابا'].sort(() => Math.random() - .5).forEach(c => { const b = el('button', 'tile ur', c); b.onclick = () => { if (c !== 'بابا') { b.classList.add('no'); play('syllables/be_a'); react(stage, 'think', 'That one is just <b>baa</b>. Look for <b>baa</b> twice.'); later(() => b.classList.remove('no'), 600); return; } row.querySelectorAll('.tile').forEach(x => x.disabled = true); b.classList.add('ok'); play('ui/correct'); a.firstWord = Date.now(); save(); react(stage, 'cheer', '<b>You read it. Really read it.</b>'); stage.append(fx('success_check', { size: 110 })); burst(); later(() => nxt('See what you did'), 900); }; row.append(b); });
      later(() => play(key), 300);
    }
    step();
  }
  const confettiEl = () => { const d = el('div', 'ob-confetti', confetti(22)); return d; };

  function value(scr) {
    scr.classList.add('ob-center'); scr.append(fx('hearts_or_balloons', { size: '100%', loop: true, cls: 'fx-bg' }));
    scr.append(el('div', 'ob-hero', `${mascot('heart', 150)}<h1>${T(a.who, 'You', esc(a.name))} just read Urdu</h1><div class="ob-card-prev"><div class="ur" style="font-size:64px;line-height:1.6">بابا</div><div class="muted">baba · dad · ${T(a.who, 'your', 'a')} first word</div></div><p class="muted">Two letters, one word, under two minutes. ${T(a.who, 'Show someone who will be proud of you.', 'Send it to the family, they will want to hear about this.')}</p>`));
    const sh = el('button', 'btn btn-gold btn-wide', `${icon('share')} Share ${T(a.who, 'my', esc(a.name) + "'s")} first word`); sh.onclick = () => shareCard(a).catch(() => {});
    foot(scr, sh, cta('Continue', () => go(1)));
  }
  function streak(scr) {
    scr.classList.add('ob-center', 'ob-blue'); const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']; const today = (new Date().getDay() + 6) % 7;
    burst(); scr.append(el('div', 'ob-hero', `<span class="ob-hop">${mascot('proud', 110)}</span><div class="ob-flame"><span class="ob-big-n pop">1</span></div><div class="ob-streak-l">day streak</div><div class="ob-week">${days.map((d, i) => `<span class="${i === today ? 'on' : i < today ? 'past' : ''}"><i>${i === today ? icon('check') : ''}</i>${d}</span>`).join('')}</div><p>Day 1 counts, because ${T(a.who, 'you', esc(a.name))} read <span class="ur">بابا</span> today. Read a little tomorrow and it becomes two.</p>`));
    scr.querySelector('.ob-flame').prepend(fx('streak_flame', { size: 170, loop: true }));
    foot(scr, cta("Let's keep it going", () => go(1)));
  }
  function commit(scr) {
    scr.append(say('hello', T(a.who, '<b>How many days in a row will you read with me?</b>', `<b>How many days in a row will ${esc(a.name)} read with me?</b>`), 120));
    options(scr, 'days', [[3, 'blend', '3 days', 'A good first try'], [7, 'star', '7 days', 'A whole week, the first six letters'], [14, 'flag', '14 days', 'Two weeks, unit 1 done'], [30, 'sparkle', '30 days', 'Reading short sentences']], { reply: v => ['cheer', v >= 14 ? `${v} days! <b>Now that's a reader.</b>` : `${v} days. <b>I'll be waiting every morning.</b>`] });
  }
  function plan(scr) {
    const u1 = C.units[1];
    scr.append(say('hello', `${T(a.who, 'Here is your plan', 'Here is ' + esc(a.name) + "'s plan")}. <b>I'll be there every day.</b>`, 110));
    const c = el('div', 'ob-plan', `<div><small>First unit</small><b>${u1.title}</b><span class="ur">${u1.letters.join(' ')}</span></div><div><small>Every day</small><b>${a.minutes || 10} minutes, ${a.days || 7} days in a row</b><span class="muted">one short lesson, then a quick review</span></div><div><small>${a.reads && a.reads !== 'none' ? 'Before we start' : 'Up next'}</small><b>${a.reads && a.reads !== 'none' ? 'A 2-minute letter check' : 'Three quick rules, then alif'}</b><span class="muted">${a.reads && a.reads !== 'none' ? 'so you skip what you know' : 'about five minutes'}</span></div>`);
    scr.append(c);
    if (a.who === 'children') scr.append(el('p', 'muted center ob-small', 'Add your other children from the "Who is learning?" screen.'));
    foot(scr, cta(a.reads && a.reads !== 'none' ? 'Start the letter check' : 'Start my first lesson', async () => { await db.setting('onb', null); finish(a); }));
  }
  show();
}

const PAINS = [
  ['dots', 'eye', 'The letters look alike', 'Look-alikes are taught side by side, and you count the dots'],
  ['shapes', 'link', 'Letters change shape when they join', 'Every letter shown in all its shapes, in real words'],
  ['rtl', 'back', 'Right to left feels backwards', 'Rule one, day one, and it sticks'],
  ['check', 'speaker', 'No one to check me', 'Every letter, word and sentence is spoken aloud'],
  ['boring', 'star', 'Old qaida books are boring', 'Real words from lesson one, like بابا and نام'],
  ['time', 'timer', 'No time for long lessons', 'Lessons take about five minutes'],
  ['ads', 'lock', 'Apps full of ads, or they need internet', 'No ads, no account, works offline'],
];
const GOAL_REPLY = { family: 'Messages from family, <b>in their own script</b>. Lovely.', books: 'Ghalib is waiting. <b>We will get there.</b>', kids: 'A parent who reads with them. <b>Best thing for a child.</b>', roots: 'Your language, now <b>on paper too</b>.', class: 'We will be <b>ready for that exam</b>.', curious: 'It <b>is</b> beautiful. Wait until you see it join up.', school: 'We will make Urdu class <b>the easy one</b>.', start: 'A head start is <b>a gift</b>.', abroad: 'Far from home, <b>still reading Urdu</b>.', stories: 'Stories are <b>the best reason</b> to read.' };
const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// 1080x1350 share card drawn on canvas, then the Android share sheet (Capacitor) or Web Share, else a download.
export async function shareCard(a) {
  await Promise.all(['700 64px "Noto Naskh Arabic"', '700 40px Fredoka', '40px "Noto Nastaliq Urdu"'].map(f => document.fonts.load(f).catch(() => {})));
  const W = 1080, H = 1350, cv = Object.assign(document.createElement('canvas'), { width: W, height: H }), g = cv.getContext('2d');
  g.fillStyle = '#F2F7F6'; g.fillRect(0, 0, W, H);
  const stripe = ['#1E9C8F', '#F2A93B', '#C74A3B', '#1E2F55']; for (let x = 0; x < W; x += 56) { g.fillStyle = stripe[(x / 56) % 4]; g.fillRect(x, 0, 56, 18); g.fillRect(x, H - 18, 56, 18); }
  g.fillStyle = '#fff'; round(g, 90, 300, W - 180, 560, 48); g.fill(); g.strokeStyle = '#D5E3E1'; g.lineWidth = 4; g.stroke();
  const img = await new Promise(r => { const i = new Image(); i.onload = () => r(i); i.onerror = () => r(null); i.src = './img/mascot_cheer.webp'; }); if (img) g.drawImage(img, W - 330, 150, 250, 250);
  g.textAlign = 'center'; g.fillStyle = '#1E2F55'; g.font = '700 58px Fredoka, sans-serif'; g.fillText(a.who === 'me' ? 'I read my first Urdu word' : `${a.name} read a first Urdu word`, W / 2, 230);
  g.direction = 'rtl'; g.fillStyle = '#157A70'; g.font = '700 260px "Noto Naskh Arabic", serif'; g.fillText('بابا', W / 2, 700); g.direction = 'ltr';
  g.fillStyle = '#5A6B84'; g.font = '600 48px Fredoka, sans-serif'; g.fillText('baba · dad', W / 2, 800);
  g.fillStyle = '#1E2F55'; g.font = '600 40px Fredoka, sans-serif'; g.fillText(new Date().toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric' }), W / 2, 980);
  g.fillStyle = '#157A70'; g.font = '44px "Noto Nastaliq Urdu", serif'; g.fillText('اردو پڑھنا سیکھیں', W / 2, 1110);
  g.fillStyle = '#5A6B84'; g.font = '600 36px Fredoka, sans-serif'; g.fillText('Urdu Qaida · free, offline, 10 minutes a day', W / 2, 1230);
  const b64 = cv.toDataURL('image/png').split(',')[1]; const name = 'first-urdu-word.png'; const text = a.who === 'me' ? 'I just read my first Urdu word: بابا (baba, dad)' : `${a.name} just read a first Urdu word: بابا (baba, dad)`;
  try { const { Filesystem, Directory } = await import('@capacitor/filesystem'); const { Share } = await import('@capacitor/share'); if (!window.Capacitor?.isNativePlatform?.()) throw 0; const r = await Filesystem.writeFile({ path: name, data: b64, directory: Directory.Cache }); await Share.share({ title: 'First Urdu word', text, url: r.uri }); return; } catch (e) {}
  const blob = await (await fetch('data:image/png;base64,' + b64)).blob(); const f = new File([blob], name, { type: 'image/png' });
  try { if (navigator.canShare?.({ files: [f] })) { await navigator.share({ files: [f], text }); return; } } catch (e) { if (e?.name === 'AbortError') return; }
  const l = document.createElement('a'); l.href = URL.createObjectURL(blob); l.download = name; l.click();
}
function round(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
