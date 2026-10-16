# Motion audit: Urdu Qaida vs Cookling

Method: Playwright video (390x844, 25 fps = 40 ms/frame) of both apps, each trigger stamped with a one-frame magenta bar so frame 0 of every strip is the exact trigger frame. In-page rAF samplers (about 16 ms) logged computed scale/translate/opacity of the moving element for exact numbers. Cookling = `design/prototype.html` over file://. Urdu Qaida = localhost:5188 with a fresh learner (units 0 + 1 partly seeded), lesson drills for answers, fresh profile for onboarding.

Strips (all in `/home/oye/Documents/free_work/urdu-reading-course/.audit/gauntlet/motion/strips/`, 40 ms/frame unless the label says otherwise; every cell is labelled with ms since trigger):

| Moment | Cookling | Urdu Qaida |
|---|---|---|
| (a) enter | cook_a_enter.png | urdu_a_card_enter.png, urdu_a_lesson_open.png, urdu_a_tabs.png, urdu_a_welcome.png |
| (b) press | cook_b_press.png (+ vid/cook_b_press.json) | urdu_b_press.png, urdu_b_press_hero.png (+ vid/urdu_b_press*.json) |
| (c) correct | cook_c_tick.png (nearest: mise-en-place tick, no quiz in Cookling) | urdu_cd_ok.png (+ vid/urdu_cd_ok.json) |
| (d) wrong | cook_d_locked.png (nearest: locked lesson wiggle) | urdu_cd_no.png (+ vid/urdu_cd_no.json) |
| (e) character | cook_e_idle.png (200 ms/frame) | urdu_e_hero_idle.png (160 ms/frame), urdu_e_coach_idle.png |
| (f) celebrate | cook_f_cel.png (120 ms/frame) | urdu_f_cel.png (120 ms/frame) |
| (g) wake / hatch | cook_g_hatch.png (120 ms/frame) | urdu_g_wake.png (120 ms/frame), urdu_g_wake_fine.png (40 ms/frame) |

Raw videos: `.audit/gauntlet/motion/vid/*.webm`. Driver scripts: scratchpad `mo/rec2.py`, `rec3-6.py`, `strip.py`, `sh.py`.

## What makes Cookling feel the way it does (exact numbers, from prototype.html)

One spring primitive (`Sp`, `springVal`) is used for everything; the whole UI is driven live at the display rate (240 Hz sub-steps), with the creature as a live spring rig, not a baked clip.

- Screen change: `springVal(0,1,140,14.5)`; the incoming screen slides translateX(100% to 0); the outgoing one goes translateX(-26%), scale 0.95, opacity 1 to 0.1 at the same time (zeta 0.61, about 350 ms, one small overshoot). Content then staggers in: `popIn` y=26, scale 0.88, k230 d17, base 260 ms, step 85 ms.
- Press: `Sp(1,380,13)` toward 0.9 on pointerdown, toward 1 on release. Measured: 0.876 at 120 ms (it undershoots the target), release to 1.04 at about 300 ms, settled at about 650 ms. Depth about 12%.
- Checkbox tick: scale 1.25 to 1 with k260 d10 (measured 1.18, 0.91, 1.03, 1.0 over about 600 ms) + draw-on stroke + 7 sparks + creature squash + heart.
- Wrong/blocked (locked lesson): translateX 8 to 0, k300 d9 (measured +3.8, -0.8, -3.2, -1.7, +1.4, then still by about 700 ms).
- Bubbles / "go" buttons: scale 0.5 to 1 at k260 d12, 1.12 to 1 at k300 d10.
- Counters and bars: `countTo` k60 to 120 with `d = 2*sqrt(k)` (critically damped, never wobbles); XP bar k60 to 70, d 15.5 to 16.7; badge scale 0 to 1 plus rotate -10 degrees at k170 d8.
- Character (live rig): breathing sin 0.02 at 2.4 rad/s; random blink every 2 to 5 s (22% double blink); glance every 0.6 to 2.8 s; egg wobble kicks every 1.8 to 3 s; squash on landing `1 - min(.3, impact/1500)`; arms are springs.
- Hatch: anticipation squash to 0.8, three escalating shakes at 120, 270 and 420 ms (shake 5, 9, 14), flash, pop at 580 ms with stretch 1.35 and shell pieces with gravity 1100 and bounce 0.35, burst of 14 sparks, name card springs in 200/13.
- Celebration is choreographed: title popIn at 30 ms, confetti at 120 ms, XP box at 380 ms, count-up and bar fill at 630 ms, badge at 1000 ms, second confetti at 1100 ms, streak at 1300 ms.

## Verdict per moment

### (a) Screen / card entering: PARTIAL. The spring is good, the transition is missing.
Measured Urdu card enter (`spring.js enter`: k230 d15, rise 26, from 0.94): opacity 0 for about 80 ms, scale 0.94 to 1.01, translate 26 px to -4 px (overshoot 15%), settles at about 900 ms. The curve itself is near Cookling's `popIn` (k230 d17); it just has a bit less damping (zeta 0.49 vs 0.56).
What does not match:
- There is NO screen transition. The old content is deleted (`box.innerHTML = ''` in path.js per step, `root.innerHTML = ''` in learner.js per tab) and the new content pops in. Cookling slides the new screen in and parallaxes the old one out. Opening a lesson (urdu_a_lesson_open.png): +0 to +80 ms old screen, +120 to +240 ms nearly empty peach screen with only the button, card appears at +320 ms. That is 200 to 280 ms of nothing. Tab switch (urdu_a_tabs.png): about 120 ms fully blank, then the cards stagger in.
- No stagger inside a card. The lesson card, its title, speaker button and tiles arrive as one block (only the tiles get their own 55 ms stagger).
- The enter starts after a rAF flush + `setTimeout(40 * n)`, so the first block always begins from fully transparent a frame or more late.
Fix: items 1 and 2 below.

### (b) Tapping the primary button: PARTIAL. Right idea, too shallow and not a spring.
`feel.js down()`: WAAPI 1 to 0.94 over 90 ms ease-out; `up()`: a 340 ms keyframed 0.94, 1.045, 0.99, 1. Measured press 0.968 at 45 ms, 0.946 at 96 ms, 0.94 at 135 ms (urdu_b_press*.json). Cookling goes to 0.876 and rebounds to 1.04 (zeta 0.33). On a big 56 px child button a 6% squash is barely visible, and on "Start/Continue" the click replaces the screen, so the release spring is never seen (the element is gone). Fix: item 5.

### (c) Correct answer: MATCHES in energy, too long and stacked. Over-delivers.
Measured tile (urdu_cd_ok.json): 1.0 to 1.19 at 186 ms (+8.7 px lift) to 0.96 at 293 ms to 1.03 at 380 ms to 1.0 at about 560 ms. Cookling's tick: 1.25 to 0.91 to 1.03 to 1.0, 600 ms. So the amplitude and timing are right. The problem is that three drivers write the same properties (CSS `.tile.ok{animation:tileWin .45s}`, `feel.js bounce()` WAAPI scale/translate plus a glow ring, `spring.js pop(t, 1.16, k260 d7)`) plus 10 sparkles, chime, haptic, Marko mood change, say-bubble. spring.js `pop` with d=7 is zeta 0.22: about 4 half-cycles. Looks fine in one tile, but combined it is the busiest moment in the app. Then the next round's tiles arrive (below).

### (d) Wrong answer: MATCHES in spirit, tail too long.
Measured (urdu_cd_no.json): scale 0.94 to 1.04, opacity 0.6, translateX shake +-3 px that is still +-3 px at 420 ms and +-1 px at 700 ms, fully still only by about 1.2 s. `spring.js shake`: k420 d6, zeta 0.15. Plus `.tile.no` CSS `wobble .4s` plus `feel.js wobble`. Cookling's equivalent (k300 d9, zeta 0.26) is still by about 700 ms. Child-safe and soft (no red, amber ring, correct tile highlighted, "Listen again" bubble pops with sayPop), which is good. Fix: item 4.

### (e) Character idle life: DOES NOT MATCH. Biggest difference in feel.
Measured pixel motion energy on the character box over 4 s: Cookling mean 0.87, moving on 62% of frames. Urdu Qaida hero Marko after the calm timer: mean 0.16, moving on 17%, and EXACTLY ZERO motion from about 4 s onward (frame diff 0.02 = video noise). Causes:
- `motion.js CALM_MS = 4000`: after 4 s without input, `rest()` stops the idle loop on its first frame; `html.calm .marko.marko-still>img{animation-play-state:paused}` also stops the CSS breathing. A child who is thinking for 5 s sees a frozen mascot. Cookling never freezes.
- Marko is a pre-baked Lottie (marko_idle.json: 9 s loop authored at 60 fps) played at 15 fps ambient / 24 fps reaction (`marko.js FPS_AMBIENT = 15`). The energy trace alternates about 1.2 / 0.3 per frame (every other frame is a repeat) = visible 15 fps stepping next to 60 Hz spring UI.
- No procedural layer: no random blink/glance, no squash on events (pokeSq CSS keyframes only on the hero poke), no reaction physics. Reaction states (cheer, think, listen) are clip swaps with an outro, 600 ms mood timer.
- Awake, the clip itself is good (hero idle sways, blinks), so the art is fine; the motion system around it is what is missing.
Fix: item 3.

### (f) Celebration / progress fill: PARTIAL.
- Lesson progress bar: `transition: width .3s cubic-bezier(.3,1.2,.5,1)` + glow spark: good and close to Cookling's feel (it overshoots a hair).
- Celebration screen (urdu_f_cel.png): crossfade 0 to 480 ms; at +720 ms the teal screen shows only a title for about 360 ms (dead air), Marko arrives at about +1080 ms, "+1 pearl" chip fades with a 0.3 s cubic-bezier overshoot after a fixed 0.45 s delay for ALL beats at once (`celBeat2`, one delay for stage/chip/goal/text/foot), the "0 pearl on your thread" to "1 pearl" line is a hard text swap at about 1.5 s, no confetti in this capture (white sparkle dots only), no count-up, no bar fill on this screen. Cookling has 6 distinct beats over 1.3 s with counting numbers, bar fill, badge flip and two confetti bursts.
Fix: item 6.

### (g) Onboarding wake vs hatch: DOES NOT MATCH.
Wake (urdu_g_wake_fine.png): tap, then +40 ms sleeping pose, +80 ms already awake and waving: a hard cut, no anticipation, no build-up. Marko pops slightly (disc scales 0.95 to 1.0) and sparkles pulse after, nice, but the text swap ("Marko is fast asleep" to "Assalam-o-alaikum!") is an instant change with no spring. Cookling's hatch has a 580 ms build (squash to 0.8, three escalating shakes, cracks growing) then a 1.35 stretch pop, flying shell pieces, sparks and a springing name card. Urdu Qaida's moment is the emotional first impression of the app and it is the least built-up one. The following colour screen (sun rays + sun fades in, bubble pops) is good.

## Where motion is MISSING (screens that just appear)

Evidence-based (captured): lesson open from Start/Continue (200 to 280 ms blank, no exit); tab switches (120 ms blank, no exit/slide); Continue between lesson cards (old card deleted instantly, new one springs in; the progress header does not move with it); onboarding text swap on wake; "0 to 1 pearl" and similar number changes on the celebration screen.
Code-inferred (not captured): Me/Review stats ("1 of 13", "0 of 0") are static text, no count-up; the unit path pearls and the Me stat cards are not in the BLOCKS selector list in spring.js (`.card, .word, .ucard, .ob-opt, .ob-card-prev, .today-card, .sent-row`), so only generic `.card`s stagger; `.pearl`, `.stat`, `.unit` rows would just appear; sheets/modals use `gate-up` fade+slide only (fine); no exit animation anywhere in the app (the only exits are fades on overlays).

## Where it is too busy for children

- Next-round tiles: spring.js pop from 0.7 at k320 d10 (zeta 0.28) overshoots to 1.12 and takes about 1.2 s to settle (measured 0.7 at 562 ms, 1.12 at 825, 0.97 at 1065, 1.02 at 1250, 1.0 at 1440), AND feel.js `popIn` animates the same tiles from 1.28. Every question, 3 to 6 tiles wobbling for over a second while the child is trying to listen to the next sound.
- Correct moment: five simultaneous things on every right answer (tile bounce, ring, 10 sparkles, chime, Marko mood swap with outro). Fine once, tiring on 10-round drills.
- Wrong moment: tile shake tail 1.2 s + CSS wobble + WAAPI wobble + bubble + Marko flips to `listen`/`think` with an outro every time.
- Ambient village layer on Today (clouds, leaves, rays, fireflies, parallax) plus a gyro-driven specular sheen that follows the pointer on every tile (`premium.js`): lovely but ambient motion competes with the hero Marko, and then everything including Marko stops at 4 s (calm). The balance is inverted: the scenery lives, the friend freezes.

## Ranked changes (implementable)

1. **Real screen/step transitions with an exit.** Add `swap(host, build, dir)` to `mobile/src/spring.js`: keep the old node, append the new one into the same grid cell (`display:grid; grid-area:1/1` on a wrapper), run one `spring(0,1,{k:140,d:14.5})` that sets `translate: ${(1-p)*dir*100}% 0` on the new node and `translate: ${-p*dir*26}% 0; scale: ${1-.05*p}; opacity: ${1-.9*p}` on the old one (Cookling `go()`), remove old at settle. Hook it at the three places that do `innerHTML = ''` then rebuild: `learner.js` `render()/doRender()` (tabs, dir from tab index), `learner.js openLesson` (dir = +1) and the step loop in `path.js` (`box.innerHTML = ''` in each `screens[]` entry: call `swap(box, ...)` instead). For lesson steps use a lighter variant (distance 30%, k200 d17) so it is not a full slide. Skip under `calm()`.
2. **Remove the blank gap (100 to 280 ms).** In `spring.js note()` call `flush()` synchronously (it runs inside a MutationObserver callback already, so no extra `requestAnimationFrame`), start the first block at delay 0 with `from` opacity 0.35 instead of 0, and cut the `40 ms * t` stagger to a progressive `0, 45, 90, 135 ...` capped at 6 blocks. After item 1 the old screen covers the build time, so the gap disappears for free.
3. **Marko never freezes, and gets a live procedural layer.** (a) `motion.js`: make `rest()` in `marko.js` a no-op for the hero and coach Marko (or raise `CALM_MS` to 20000 for Marko only; keep calm for scenery); delete `html.calm .marko.marko-still>img` from `injectStyle()` so the CSS breathe keeps running (it is compositor-only, free). (b) `FPS_AMBIENT` 15 to 24 for the one slot owner only (the single `slot` Marko is already arbitrated, so cost is bounded); keep 15 for off-slot ones. (c) Add `life(el)` in `marko.js` using `spring()` from spring.js on the wrapper `.marko` (transform-origin 50% 100%): breathe `scaleY 1 + 0.02*sin(t*2.4)`, random "glance" every 1.2 to 2.8 s (rotate +-2 deg, translateX +-3 px with `{k:170,d:14}`) and a random squash-blink via a 0.97 scaleY nudge every 2 to 5 s. (d) Event reactions as springs on the wrapper, not clip swaps: correct = hop (translateY -14 px, gravity-like `k=120 d=9`, land squash `scaleY = 1 - min(.3, impact/1500)`, same as Cookling `Creature.update`), wrong = 5 degree tilt away + return `{k:300,d:14}`, tap = squash 0.92 to 1 `{k:260,d:12}`. This is what gives Cookling's creature its life and it costs no extra Lottie frames. (e) Longer term: add a 'blink' + 'glance' marker segment to `design/marko-rig/make_marko.py` so eyes move inside the loop.
4. **One owner for answer feedback, and retune damping to zeta 0.45 to 0.6.** Delete `.tile.ok{animation:tileWin}` (style.css line 226), `.tile.no wobble` (line 78) and `feel.js bounce()` scale/translate and `wobble()` (keep the glow ring and sound). In `spring.js`: correct `pop(t, 1.16, {k:260,d:10})` (matches Cookling's tick: 1.18, 0.91, 1.03, about 600 ms); wrong `shake(t, 8)` with `{k:300,d:14}` (2 visible swings, still by about 450 ms); next-round tiles `pop(n, 0.86, {k:300,d:13})` with 45 ms stagger (drop the 0.7 start and the extra `feel.js popIn`, or keep popIn and drop the CHOICES branch). Net: same energy, 600 ms shorter, no stacked animations.
5. **Press as a real spring.** In `feel.js down()/up()` replace the WAAPI pair with `spring(1, .90, {k:380,d:13}, s => el.style.scale = s)` on down and `spring(cur, 1, {k:380,d:13})` on up (target 0.92 for `.tile`/`.pearl`, 0.90 for `.btn`). Fire the release on pointerup, not click, and delay screen-changing handlers by one frame is NOT needed: because of item 1 the release will be visible while the button slides out. Keep the ripple.
6. **Choreograph the celebration like Cookling.** In the celebrate builder (search `className = 'celebrate'` in path.js/learner.js/stickers.js) replace the single `celBeat2` delay (style.css line 523) with per-element delays: stage/Marko `pop(0.6)` at 0 ms (move Marko's appearance from about +360 ms to 0, removes the 350 ms dead air), title at 90 ms, "+1 pearl" chip scale 0 to 1 with rotate -10 deg at `{k:170,d:8}` at 350 ms, pearl-count line as a count-up (`countTo` helper: `d = 2*sqrt(k)`, k60 to 90), foot at 700 ms. Add one confetti burst (reuse `confetti_burst.json` via `fx()`) at 120 ms. Export `countTo` and `popIn(el, delay, y, s0)` from spring.js (port verbatim from prototype lines 458 to 473).
7. **Build the wake-up.** In `onboarding.js` (around line 75, `ob-sleeper`): on tap run a 480 ms build: squash scaleY 0.92 (anticipation, 120 ms), two escalating tilt-shakes (+-3, +-6 deg at 150 and 300 ms), zzz drift up, then reveal with a stretch pop `spring(1.25,1,{k:240,d:11})` on scaleY/scaleX 0.9 inverse + sparkle burst, THEN swap the title/body text with `pop` (0.9 to 1) instead of a hard text swap. The state change to Lottie 'wave' should start at the pop frame, not at the tap.
8. **Stagger what already has structure.** Extend `BLOCKS` in `spring.js` with `.pearl, .stat, .unit, .necklace .pearl` and stagger them 35 ms apart (cap at 9, existing logic); in lesson cards give `.card > h2`, `.sayRow`, `.choices` a base delay 0 / 60 / 120 ms. Cookling uses base 260 ms/step 85 ms for full screens; for children keep 45 ms steps and total under 400 ms.
9. **Number and bar motion everywhere.** Use `countTo` (item 6) on Today (pearls, minutes, streak), Me stats and the celebration; set the Me/Review bars from 0 with the XP-bar spring (k70 d16.7). Today already has a count-up (round 9b) in learner.js; check it is spring-based (critically damped) and move the others to the same helper.
10. **Calm the tiles for children (budget).** Cap simultaneous springs at 12 (queue the rest), stop the Marko mood swap on every wrong answer (alternate listen/think only on the 2nd wrong in a row; hold `cheer` 900 ms only on streak >= 3), reduce sparkles from 10 to 6 on tiles, and keep the gyro sheen (`premium.js`) only on the hero and the current letter card, not on every `.tile`.

Do not change: prefers-reduced-motion handling (already correct everywhere), the lesson progress-bar transition, the child-safe wrong-answer design (amber, no buzzer), or the single-slot Lottie arbitration. Those are good and are why the app already feels better than most.
