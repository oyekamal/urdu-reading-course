# Urdu Qaida gauntlet findings (2026-10-16): pedagogy, QA, motion

Five critics ran once (sonnet, parallel). Full reports sit beside this file. Resume here; work ONE agent at a time (owner is demoing, saving tokens, will say when multi-agent is allowed).

Reports: `pedagogy_reading.md`, `pedagogy_child_ux.md`, `qa_functional.md`, `qa_a11y_edge.md`, `motion.md` (+ `motion/strips`, `motion/vid`).

## STATUS 2026-10-16 (night, 0.13.1 vc 24): also done and shipped: vowel-mark fade (marks.js), ranked letter example words, atomic screen swap + exit overlay, Marko adaptive quality governor, teacher mode QA + roster CSS, axe fixes, theme chip. Final independent QA verdict: ship (.audit/gauntlet/qa_final.md). Open minors: EGRA 60 s timer starts with no Start gate, Learn card says Start after a mid-lesson reload, dark Learn hero grey glow, theme-color on real phone, TalkBack + real-device CPU untested.

## STATUS 2026-10-16 (late): P0 bugs, most P1 pedagogy and P1 motion DONE and shipped as 0.13.0 (vc 23). Still open: vowel-mark fade (units 8-10), letter example word position (needs new audio), screen-exit snapshot (60-120 ms blank between screens), comprehension for non-Read screens, teacher-mode re-test, TalkBack test on a real phone, real-device Marko CPU check (FPS constants in marko.js).

## State of the code before 0.13.0 (kept for history; v0.12.2 c5dbf9a was the previous build)
Done in the working tree, NOT yet shipped or committed:
- Appearance setting (Match my phone / Light / Dark): PostCSS plugin in `mobile/vite.config.js` gives every `@media (prefers-color-scheme:dark)` block a `:root[data-theme=dark]` twin; `main.js apply()` sets `html[data-theme]`; select in Me settings (`learner.js`). Tested in both system modes + persists on reload.
- Wrong quiz answers stay marked and inert (`drills.js stayWrong`, `path.js` quick check/blend/mark, `learner.js` sight words, `onboarding.js`). Quick check no longer auto-advances on a wrong tap and only the first try is graded.
- `mobile/src/spring.js`: Cookling-style spring layer (staggered entrances, pop on correct, shake on wrong, bubbles); progress bars overshoot easing.
Next release should be 0.13.0 (vc 23). Needs: `npx vite build`, `npx cap sync android` BEFORE gradle, bundleRelease with `~/.kamil-harness/keys/urdu-reader.env`, copy AAB to `~/Downloads`.

## Owner's note on the installed app
Images and the new colours were missing on the owner's phone: the phone was on an older Play build. Images shipped in 0.12.0+, colours in 0.11.4+. Version is shown at the bottom of the Me tab.

## Ranked backlog (merge of all five reports)

### P0 correctness bugs (QA functional)
1. Double-tap on a correct tile skips rounds and double-counts (tell-apart `drills.js:45`, blend `path.js` ~193, quick check ~186, mark ~210). Fix: disable all tiles on the first correct tap.
2. Read tab: Start then instant Stop saves "Infinity wpm / new best" (`learner.js` ~153). Fix: minimum seconds guard + clamp, never save impossible wpm.
3. Build the word (`drills.js:76`) wrong tiles un-mark after 400 ms and stay tappable; dictation wrong mark removed after 500 ms (`drills.js:231`). Fix: `stayWrong` + escalate (after 2 misses glow the right tile and play the word).
4. Unit check after Submit: tiles still clickable, can move the green mark onto a wrong answer; 0/10 submit allowed without confirmation (`drills.js:241-243`).
5. Back on the celebration screen opens "leave lesson" over it (`back.js` OVERLAYS lacks `.celebrate`).
6. Teacher PIN: no lockout, plaintext (`main.js:127,136`). Reuse the gate lockout, hash the PIN.
7. Backup restore drops the Appearance setting (`backup.js:38` UI_KEYS has no `theme`). Text size not validated on read (`main.js:47` scale 0 or 50 breaks the UI): whitelist.

### P1 pedagogy (highest learning impact)
1. Words/Read cards show Urdu + picture + romanisation + English at once, so a child can skip decoding (`drills.js:80-93`). Fix: show Urdu only; reveal picture/roman/English on tap (picture as confirmation after the attempt).
2. Unit gate quiz tests Latin-letter matching, not print-to-sound (`drills.js:237`): use audio-only prompt, minimal-pair distractors, per-item feedback.
3. No pseudo-word (non-word) decoding in lessons although EGRA tests it: compose silly words from existing syllable audio.
4. Review is self-graded ("Got it" never shows the answer, `learner.js:138`): reveal first or grade by choice. Review floods (about 420 cards by unit 5): create cards for letters + missed words only, stagger due dates.
5. Failing the 4-question Quick check restarts the whole lesson (`path.js:181`): retry the questions only.
6. First wrong tap reveals the answer (`feel.js wrong()`), hint is English text non-readers cannot use; word drills only say "Not quite".
7. Onboarding is 13 text screens before the first letter, same for a 5-year-old and an adult; no hand-the-phone step.
8. Vowel marks drop off a cliff at unit 11; Read has no comprehension check; ب example word is not initial-position.
9. Three identical speaker icons on one screen; 14px muted instruction text; child-track wrong tile has no non-colour marker; no stopping cue after a lesson.

### P2 accessibility / polish
- Speaker buttons all labelled "Play" (168 on unit 4 page): `drills.js:12` pass `Play ${rom}`.
- Contrast: Me letter grid untaught letters 2.58:1 (`dashboard.js:19`), highlighted letter teal 3.38:1 (`path.js:167`, use `--accent-deep`), locked pearl captions.
- No `color-scheme` set per theme (native controls stay light when forced dark); wrong-theme flash (data-theme set ~300 ms after load).
- Mid-lesson reload restarts the lesson but the sheet says progress is saved: persist the step or change the copy.
- Learner picker cards stack avatar above name (`style.css:84 .card.btn{display:block}`); same-name learners indistinguishable.
- Landscape + XL text leaves 186 of 360 px for the lesson; Learn unit card clips 5 px; locked pearls add 14+ tab stops.

### P1 motion (Cookling gap) — the spring layer itself matches Cookling's numbers; the system around it does not
1. Real screen transitions with exit: add `swap(host, build, dir)` in `spring.js` (spring k140, d14.5), use in `learner.js` tab switch and `path.js` step loop. Today screens are deleted and rebuilt (200-280 ms blank peach).
2. Remove entrance dead time (`flush()` synchronous, first block at 0 ms from opacity .35).
3. Marko freezes after 4 s (calm mode) and plays at 15 fps: exempt Marko from calm in `marko.js`/`motion.js`, 24 fps for the one active Marko, spring breathe/glance/blink, hop + squash reactions on the `.marko` wrapper.
4. One owner for answer feedback (CSS + feel.js WAAPI + spring.js stack on the same tile): correct pop(1.16,k260,d10), wrong shake(8,k300,d14), next tiles from .86 k300 d13.
5. Button press as real spring (to .90, k380 d13) in `feel.js`.
6. Choreograph celebration (six beats; hard cut 0 to 1 pearl now) and the wake-up (anticipation squash, escalating shakes, stretch pop).

## Suggested order (single-agent, demo-friendly)
1. P0 bugs (small, safe), 2. Words/Read cards show Urdu first + reveal, 3. Review reveal-first + card cap, 4. Quick-check retry only, 5. Motion items 1-5, 6. onboarding shortening, 7. a11y polish. Re-test each with Playwright (`mobile/tools/`), screenshots in `.audit/`, then ship 0.13.0.
