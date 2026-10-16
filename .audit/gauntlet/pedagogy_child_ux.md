# Urdu Qaida: child and parent UX review (first 3 sessions)

Method: ran the real app at http://localhost:5188/ in Playwright (412x880): full first-run onboarding for the child and adult tracks, then seeded learners driven through letter lesson 2, vowel marks, join, words, home, Me and settings. I tapped wrong answers on purpose in each drill. Screens are in /tmp/claude-1000/ux/ (kid_*.png, L_*.png, B*.png, W_00.png, M_05.png, h*.png). Compared against .audit/wordimg/bar (Khan Kids, Duolingo ABC), research/12_child_ux.md (feedback rules, 3-5 min blocks, 3-5 choices) and 18_emotional_design_talk.md.

## Strengths

1. **A wrong answer is never wiped and never shamed.** In tap drills the wrong tile stays visible, faded amber, no longer tappable (`stayWrong`, style.css:77/614). Marko answers with a soft "boop", wobbles, and leans toward the right tile. Red X and buzzers are gone in the child track. "Streak" is days practised and only goes up (session.js:70), so a missed day costs nothing. This matches 12_child_ux.md and the "do not copy" list in 18.
2. **Audio-first scaffolding exists.** Every lesson header has a "Repeat instruction" button (path.js:127) and every item has a big speaker. The hint on a miss is built from the glyph on screen ("Count the dots: ب has one", "Look where the dot sits") and the right sound is replayed. First run reaches a real letter lesson, with one idea per screen and a 6-segment progress bar.
3. **Accessibility settings are unusually complete.** Me > Settings has text size (3), letter spacing (up to "dyslexia-friendly"), audio-first mode, light/dark/system, Naskh/Nastaliq, vowel marks, romanisation and a sounds switch. prefers-reduced-motion is honoured (marko.js, motion.js, feel.js `calm()`). Tab buttons are 58px, path nodes 64px, tiles about 108px, all above the 44-60px rule.

## Defects, ranked by impact on learning and motivation

### 1. Build-the-word is a dead end with no escalation (drills.js:76, joinIt)
- Repro: seed units 0-1 up to "Join them" or "Words 1", get "Make: kām — work", tap a wrong first tile again and again. I did 14 wrong taps in a row.
- Result: the tile flashes for 400 ms then un-marks (`setTimeout(() => t.classList.remove('no'), 400)`). The bubble says "Not quite. Listen again and try another one." There is nothing to listen to here. No hint, no reveal, no auto-help, ever. Every miss is logged as `join` false, which pollutes review. The bubble also sits on top of "Next word", the only exit.
- Fix: keep a per-word `misses` counter in joinIt. At 2 misses add `feel-answer` to the correct next tile and `play(wordKey(...))`. At 3 place the letter for the child (mark it ok, record once). Stop `ctx.record(false)` after the first miss per word. In feel.js `lineFor`, add a branch for `.tile.small` inside `.answer`'s card: "Start from the right: this letter first". Let `bubble()` return below the tiles only if it will not cover `.btn` (the `below` test already exists; add `nextB` height).

### 2. Failing the Quick check throws the child back to the start of a 7-step lesson (path.js:181)
- Repro: Unit 1 lesson 2 (be), get 2 of 4 in the Quick check. The screen shows a stale question, "2/4", "Not yet solid. Go through the lesson once more." and one button, "Do the lesson again", which runs `ctx.openLesson` from step 0 (hear, 5 tap rounds, forms, trace, blend, check).
- Result: this is a punishing loop for a 5-year-old. The check is 4 questions with 2-4 options each, so a fair guess passes about a third of the time and a fail wastes about 8 screens. No pearl is given, and the text is English only.
- Fix: replace the single button with a primary "Try the questions again" (reruns `ask` with fresh items; `i = 0; score = 0`) and a secondary "Hear it again" that replays only the letter card. Show `${score}/4` as 4 pips, not "2/4" under a stale question. Award a half-pearl or keep lesson progress on a retry pass. Change "Not yet solid" to "Almost! Let's try those again".

### 3. Onboarding is 13 text screens before the first letter, the same for a 5-year-old as for an adult (onboarding.js)
- Repro: open without `?skiponb`, choose "My child". Screens: welcome, wake Marko, hello, colour, who, name, why, speak Urdu, read any letters, what's hard (a long multi-select, two states), good news, minutes per day, "making path", then the first lesson. About 8 are questions about the learner answered by the parent. The child is left waiting with no "hand the phone to Zara" handoff.
- On "What has made reading Urdu hard?" the options fade in one by one and the sixth and seventh sit under the docked Continue button (kid_09.png). The Marko bubble clips at the right edge mid-animation.
- Adult track is the same flow, so an adult sees a mascot to wake and a "lucky colour" before any value.
- Fix: keep welcome, name and who. Move why, speak, hard and minutes into a single skippable "Tell Marko more" card after the first win (the first lesson already runs at about 2 minutes). Default minutes=5, speak=unknown. Add a handoff screen for the child track: big Marko, "Pass the phone to Zara", with a speaker saying it. For the multi-select, drop the stagger and give the list `padding-bottom` equal to the docked button height.

### 4. Read screens hand over the answer before the child tries to decode (drills.js:82 readIt, content.js wimg)
- Repro: Unit 1 "Words 1". Each card shows the Urdu word, a picture, roman "kām" and English "work" at once, plus a speaker (W_00.png). The only check is "tap to hear it", and `ctx.record('read', w.ur, true, 0)` is always true. So the child can pass by looking at the picture or the roman, and nothing proves decoding.
- The pictures themselves help concrete nouns (kām: carpenter, nām: person with badge). They are weaker or misleading for abstract words: بالکل "absolutely" is a thumbs-up, ناکام is a red X, مکمل is a tick, and کمال "perfection" shows a medal while کامل "perfect" shows a trophy. These are near-synonyms with near-identical art. کم، اب، کل، ملک have no picture, and the set mixes four styles (tw-/om-/mb-/art-). Khan Kids and Duolingo ABC pair a picture with a word only after the learner acts.
- Fix: in readIt, for child track render `.wimg`, `.rom`, `.en` hidden (or `visibility:hidden`) and reveal them in the existing `d.classList.add('reveal')` tap handler, so the order is: read, tap, hear, see. Keep the picture on the Build screen, where it is the prompt. Drop pictures for non-concrete or near-synonym entries in data/word_img.json (bilkul, nakam, mukammal, kamal, kamil, man, bilkul). Make the Read stage count real: add a "Did you read it before tapping?" two-button self-check or log `ms` before the reveal.

### 5. The first wrong tap gives away the answer, and the help is English text only (feel.js:`wrong()`, `lineFor`)
- Repro: lesson 2 "Tap what you hear". The first wrong tap adds `feel-answer` to the right tile (a green tick) and plays its sound within 90 ms, plus the bubble "Count the dots: ب has one" for 4.2 s (L_11x.png, w0_b.png). With 2 to 4 tiles, one wrong tap reveals the answer, so the next tap is a copy, not recall. In the Quick check, which is a mastery gate, the same reveal applies.
- A 5-year-old cannot read the bubble. `a11y.js` speaks it only for screen readers.
- Word drills ("Find the mark", 3 near-identical words) get the generic "Not quite. Listen again and try another one." and no reveal at all, so the child can brute-force and learns nothing about which vowel mark differed.
- Fix: track `misses` per `.choices` node. First miss: wobble, replay the sound, no reveal and no bubble. Second miss: reveal plus bubble, as now. Add a tiny icon beside the line (dot count drawn as dots, an ear for "listen again") so non-readers get it. For word choices, build the line from the first differing character or mark ("Look at the little mark on top").

### 6. Three speaker buttons on one screen, two of them unlabelled to a child (path.js:127, drills.js `sayBtn`)
- Repro: any lesson card (L_00.png): header speaker (Repeat instruction), big speaker (say the letter), small speaker (play the word). Same icon, different meanings, no text labels. The instruction text is also 14px muted (`.muted`) for 5-year-olds: "Tap the letters in reading order, right to left."
- Fix: give the header instruction button a different glyph, such as a speech-bubble with an ear, or put the mascot bubble itself in charge of replay (tap Marko to hear it again). Autoplay the instruction once per drill type per profile and only then stay silent. Raise `.lesson .muted` to 17-18px in the child track and drop the duplicated sentence when audio plays it.

### 7. Reward moment has no stopping point (path.js:132-143, learner.js)
- Repro: finish a lesson (M_05.png). Marko cheers, "+1 pearl", and the only large button is "Next: Join them". The daily goal ring appears on Home but the lesson celebration never says "that is enough for today", even when `goalHit` is true. A unit-1 path is 15 steps, and letter lessons are 7+ screens, longer than the 3-5 minute block in 12_child_ux.md.
- The pearl is a flat +1 regardless of accuracy, so effort and mastery look the same.
- Fix: when `goalHit` (or the third lesson of a session), make the primary button "All done for today" (to Path) and demote "One more" to a text link. Add a small "stars for today" row: 1 pearl as now, plus up to 2 bonus sparkles for 4/4 first-try, so accuracy is visible without any loss message.

### 8. Wrong state relies on colour and opacity only in the child track, and fades the glyph (style.css:77, 428-429, 614)
- The child-track rules remove the ✗ (`::after{content:''}`) and rely on a faint amber border plus `opacity:.6` on the whole tile. The wrong letter (w0_c.png) becomes a grey-blue ghost, the letter being studied. For low-vision or colour-blind children there is no non-colour marker, and the faded glyph is below 3:1 on the tinted card.
- Fix: for `body[data-track="child"] .tile.no` use `opacity:.85`, a dashed border and a small "tap another" icon in a corner (`::after` with an SVG data URI) instead of an empty string. Keep it non-red.

### 9. Pictures and decoding screens have no accessible text (content.js:31)
- `wimg()` renders `alt=""` for every picture, so screen-reader users get the word only by reading the Urdu glyphs and the roman line. The picture is also the sole cue in "Build the word" for sighted children. Fix: `alt` equal to `w.en` when the picture is the prompt (joinIt `info`), keep `alt=""` on Read cards where the English line is also shown.

## Three quick wins (each under an hour)

1. **joinIt escalation (defect 1):** add `misses` and a `feel-answer` on the next correct tile after 2 misses, plus audio replay. About 10 lines in drills.js:76.
2. **Quick-check retry (defect 2):** change the fail branch in path.js:181 to re-run only the 4 questions with "Try the questions again" as the primary button.
3. **Read cards hide roman, English and picture until tapped on the child track (defect 4):** one CSS rule (`body[data-track="child"] .word:not(.reveal) :is(.rom,.en,.wimg){visibility:hidden}`) because the `reveal` class is already added in the tap handler.
