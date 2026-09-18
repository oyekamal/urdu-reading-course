# Urdu Reading Course — App QA Pass R1

**Target:** web build at `http://localhost:5179/` (Capacitor source under `mobile/src/*.js`), tested with
Playwright (sync, Chromium, 390x800 primary / 360x740 for overflow), hostile-tester harness:
`page.on('dialog', accept)`, console/pageerror capture, `HTMLMediaElement.prototype.src` hooked to
verify real audio playback (not just UI state) and to identify exactly which letter/word was quizzed.

**Screenshots:** `.audit/shots/app_r1/*.png` (61 files, numbered by test phase).

**Important environment note:** the app's source files (`learner.js`, `main.js`) were **actively being
edited on disk by another process during this QA pass** (confirmed via file-change diffs mid-session —
line counts grew from 113→147 in `learner.js`, new features like the placement check, parent report,
and romanisation/audio-first toggles appeared between test runs). Vite's dev server does full-reloads on
change for a non-HMR-aware app like this one, which caused a few one-off "unrecognised session step"
/ stray "Back to Today not found" flakes in early runs — those were retested and are **not** listed as
bugs below. Every bug below was reproduced at least twice against the code current at the time of
this report, with a `file:line` cite from the version in the repo *now*.

---

## P0/P1 bugs

### P1 — Session flow drops the unit quiz on the very first pass; a unit can never be completed in one sitting via the primary "Start session" flow
**File:** `mobile/src/learner.js:46`
```js
if (u.words.length && !p.units[cur]?.passed && done.dict) steps.push(() => { ... quiz ... });
```
`steps` (the whole session step list) is built **synchronously, once, at the top of `session()`**
(`learner.js:37-49`), before any drill has actually run. `done` is read from previously-saved progress
(`learner.js:39`), so on the *first* session in which a learner reaches Dictation, `done.dict` is still
`false` at the moment this `if` is evaluated — even though Dictation is later completed successfully in
that same session. The quiz step is therefore silently omitted from `steps`, and the session goes
straight from Dictation to the sentence-fluency step and "Session done", skipping the unit's pass/fail
check entirely.

**Repro (deterministic, reproduced 3× across separate runs with a fresh child profile):**
1. Family mode → add a child → complete the Unit 0 intro session (marks Unit 0 passed automatically).
2. Start Unit 1 session → New letters → Tell-apart (10/10) → Build the word (3/3) → Read → Trace →
   Dictation (5/5, verified via captured audio keys that the exact target word was spelled correctly
   each time) → session jumps directly to "Read for speed" → "Session done". **No quiz is shown.**
3. `Units` tab shows unit 1 still `cur` (not `done`), unit 2 still `locked`.
4. Tap **Start today's session** again for the same unit (now `done.dict` is `true` from the saved
   `progress.units[1].steps` written by step 1's `next()`) → this time the quiz **does** appear, scores
   10/10, unit 1 is marked `done`, unit 2 unlocks (`cur`).

**Impact:** the app markets "Session … about 10 minutes" as a complete, self-contained daily loop, but a
learner using only the "Start session" button can never actually pass a unit on the session where they
finish Dictation — they must return a second time. This will read as a broken/buggy app to most users
("I did everything and it didn't count"), even though the workaround (Lesson tab, where the quiz call
at `learner.js` "8 · Check" is unconditional) exists but is not the primary promoted flow. Classified P1
(blocks the intended flow, not a full progression block — a second session or the Lesson tab
recovers it) rather than P0.

**Fix hint:** evaluate the quiz gate lazily, e.g. re-check `!p.units[cur]?.passed && done.dict` inside
`next()` right before deciding whether to advance past the dictation step (dynamically push the quiz
step onto `steps` when `done.dict` flips `true`), instead of baking the decision into the array at
session start.

---

### P2 — Opening a child from the teacher Class tab, then using the learner's own profile-switch button, drops the teacher back to the locked home screen (loses Teacher-mode context)
**Files:** `mobile/src/main.js` (`ctxBase.switchProfile: () => home()`, and `teacher()`'s
`openLearner: async id => learner(await db.get('profiles', id))`), `mobile/src/teacher.js:118`
(`openBtn.onclick = () => ctx.openLearner(r.profile.id)`).

**Repro:**
1. School mode → unlock Teacher → Class tab → tap **Open** on a child's row → lands correctly in that
   child's learner UI (Today/Units/etc.).
2. Tap the profile switcher (`<name> ▾`) in the learner header to go back.
3. **Expected:** return to the Teacher tab bar (Class/Lesson/Groups/Assess/Reports/Device) where the
   teacher was.
   **Actual:** lands on the plain, PIN-locked "Class — tap your name to start" screen (screenshot
   `55_after_back_from_learner.png`). The teacher must re-enter the PIN to get back to Assess/Reports/etc.

**Why:** `learner(p)` always wires `switchProfile` to `main.js`'s module-level `home()`, which has no
memory of "I was opened from inside Teacher mode." This matters for the product's own intended
in-classroom workflow (teacher watches a child work, then returns to keep assessing/reporting).

---

### P2 — School mode cannot add adult/heritage-track learners through its own UI
**File:** `mobile/src/main.js:44` (`if (mode !== 'school' || !profiles.length) { …+Add a learner… }`)
and `mobile/src/teacher.js` `renderClass`'s "Add child" form (hardcodes `track: 'child'`).

Once a school-mode device has ≥1 profile, the home screen's "+ Add a learner" button (the only UI that
lets a user pick a track) disappears entirely (`mode !== 'school' || !profiles.length` is `false`), and
the Teacher Class tab's own "Add child" form has no track selector at all — it always creates
`track: 'child'`. There is **no way**, short of a raw backup-JSON edit, to have an adult or
heritage-speaker learner profile inside school mode. This may be an intentional product decision (a
"class" is assumed to be children), but it directly conflicts with the QA brief's expectation of testing
all three tracks inside one flow, and is worth an explicit product decision rather than a silent gap.

---

## P3 (polish)

- **Touch targets under 40×40px at 360px width** (lesson screen, `.btn` syllable buttons e.g. `با`/`لا`/`نا`
  measured 38×52, and `.btn-play.small` measured 32×44). CSS: `mobile/src/style.css:16`
  (`.btn-play{width:44px;height:44px}` is overridden implicitly by `.small` variants having no explicit
  width, and the syllable buttons in `drills.js` (`letterCard`) are plain `.btn` with no min-width, so
  they shrink below the 44px CSS `min-height` floor in the *width* dimension on narrow screens).
  See `bug_overflow_*` — no, see the a11y screenshot pass; not screenshotted individually, but
  reproducible via `document.querySelectorAll('button,.tile,.item,.btn-play')` bounding-rect check at
  360px viewport.

---

## What passed cleanly (no bugs found)

- **First launch / 3 modes / device-type switch:** all three mode cards (Personal/Family/School) work,
  teacher PIN setup validates 4–6 digits correctly (rejects "12" with a toast), "Change device type"
  round-trips back to `chooseMode()` and keeps profiles/progress.
- **3 learners, 3 tracks (family mode):** child/adult/heritage all created and switchable.
  `document.body.dataset.track` set correctly for both heritage and adult.
  Heritage: `.rom` (romanisation) computed `display: none` confirmed via `getComputedStyle`.
  Adult: no "Trace" step observed in the session flow (code-level: `learner.js:44` gates `writeIt` on
  `profile.track !== 'adult'`) — note the Lesson tab still always shows tracing for every track by
  design (separate reference material vs. the daily drill loop), which is consistent, not a bug.
- **Full Unit 0 + Unit 1 session run:** Tell-apart 10/10 (verified via captured `names/<id>.mp3` audio
  keys matched to the correct tile every round), Word Builder 3/3 words built letter-by-tile in correct
  RTL order (verified via the on-screen "Make: **rom**" prompt matched against `units.json`), Dictation
  5/5 words spelled correctly (verified via captured `units/uNN_ii.mp3` audio keys resolved back to the
  exact word, typed with the keyboard tiles, matched target `ur` exactly), Quiz 10/10 (tile text matched
  against the vowelled `v` field shown in Read, i.e. `اَب` not `اب`). Unit 1 ends up `done` and Unit 2
  `cur` (unlocked) — *after* the second session, see the P1 bug above.
- **Review deck grading:** due cards render, "Got it"/"Not yet" both gradeable, Leitner box updates via
  `S.gradeCard`, UI advances correctly through a mixed grading pass.
- **Read tab timer:** Start advances a live `.timer` (`X.X s`), Stop computes and displays a `wpm` figure
  and a "new personal best" / "best N" comparison; Progress tab immediately shows a "Reading speed" card
  with the same figure and the correct band threshold text.
- **More tab:** Script → Nastaliq updates `body.dataset.style` live; Text size → Large updates
  `--ur-scale` CSS var live; "Show vowel marks" checkbox toggle persists `settings.marks = false` to the
  `ui` setting record; **Export backup** triggers a real file download (verified: valid JSON with
  `profiles`/`progress`/`cards`/etc.); **Import** of that same file shows "Imported N records" and the
  app keeps working afterward (no crash, Today tab renders normally); **Reset profile's progress**
  correctly clears `cards`/`attempts`/`sessions`/`assessments`/`progress` and the learner is dropped back
  to Unit 0.
- **School mode, full teacher loop:** wrong PIN → "Wrong PIN" toast, correct PIN → unlocks Class tab;
  Add child appears in roster immediately; Lesson tab renders "I do"/"We do"/"You do" sections with
  working "Play name" audio buttons (verified via audio hook); Assess → all 5 EGRA subtasks (letter
  sounds, nonwords, familiar words — each tap-wrong-then-Skip; passage — mark-last-word-reached +
  Child-finished; comprehension — 5 questions Correct/Incorrect) → Save → toast
  "Saved: Ayesha — band fluent"; Reports tab shows the new row with the right band; **CSV export**
  triggers a real download; **Parent slip** produces the expected share/clipboard text; Groups tab lists
  the child under the correct band; Device tab PIN change works (old PIN correctly rejected after
  change, new PIN correctly unlocks), and Lock teacher mode correctly re-locks to the PIN gate.
- **Reload mid-session persistence:** reloading the page mid-flow correctly restores `activeProfile`,
  routes straight back into that learner's Today tab, and all progress (`units[0].passed`, etc.)
  survives the reload untouched.
- **Offline mode:** after `context.set_offline(True)` (set only *after* first load, per the test brief),
  bundled audio still resolves and plays (`audio/names/alif.mp3` captured via the real `<audio>` element
  `src`), and tab navigation (Units → lesson → Progress) continues to work with zero errors.
- **Accessibility basics:** default browser focus ring is visible on Tab (no CSS suppresses `outline`
  anywhere in `style.css`); `.ur` elements compute `direction: rtl` correctly everywhere checked.
- **360px viewport:** `document.documentElement.scrollWidth <= innerWidth` held true (no horizontal
  overflow) on every screen checked: chooseMode, Today (unit 0), Units map, Unit-1 Lesson, Read tab,
  Progress tab, More tab, and an in-progress Session screen.
- **Console/page errors:** zero JS `console.error`/`console.warning`/`pageerror` events were captured
  across the entire test matrix (all contexts, all flows).

---

## Screens/paths not fully exercised, and why

- **Placement check** (`learner.js`'s `placement()`) and **Parent report** (`parentReport()`) — these
  appeared partway through this QA pass as the source file was being actively edited live (see the
  environment note above) and were outside the original test brief's 11 numbered items, so they were
  observed but not driven end-to-end. Worth a follow-up pass once the file stabilizes.
  New "Show romanisation" and "Audio-first mode" checkboxes on the More tab (also new mid-session) were
  likewise seen but not individually verified.
- **Actual finger-tracing gesture in the "Trace" drill** — the session flow's `nextBtn` is appended
  immediately alongside the Trace canvas regardless of tracing success (`learner.js:44`), so it was
  possible (and, per the test brief, acceptable) to advance without performing a real pointer-drag
  stroke. The canvas coverage/neatness/stroke-count scoring logic in `drills.js` (`writeIt`) was
  therefore not exercised with a genuine gesture in this pass.
- **Nonword/familiar-word EGRA subtask scoring nuance** (tapping specific wrong items to test the
  "first 10 wrong = stop rule at 0" logic in `egra.js`'s `runFlashSubtask`) — only the Skip path was
  exercised for subtasks 2 and 3, per the brief's "skip where allowed."
- **Pill color-contrast measurement** — colors were read via `getComputedStyle` on one Progress-tab pill
  but a full WCAG contrast-ratio calculation was not performed (no obvious visual contrast problem was
  observed in screenshots, e.g. `35_progress_tab.png`, `69_reports_tab.png`).

---

## Prioritised fix list (max 15)

1. **`learner.js:46`** — Make the Unit quiz step gate lazy (check `done.dict` at the point of deciding
   the next step, not when `steps` is built), so a learner can pass a unit in the same session they
   finish Dictation. (P1 — highest priority; breaks the app's core promoted loop.)
2. **`main.js` `learner()` / `teacher()`'s `openLearner`** — give the learner ctx passed from
   Teacher-Open a `switchProfile` that returns to `renderTeacher(...)` (or at least skips the PIN
   re-entry) instead of unconditionally calling `home()`. (P2)
3. **`teacher.js` `renderClass` "Add child" form** — add a track selector (child/adult/heritage) to match
   what family/personal mode offers, or explicitly document that school-mode learners are
   children-only. (P2 — product decision needed either way.)
4. **`drills.js` `letterCard`'s syllable buttons and `.btn-play.small`** — bump width to ≥44px (or ≥40px)
   at narrow viewports to meet common touch-target guidance. (P3)
5. Consider surfacing to the user, in the Session UI itself, when a step is deferred to "next session"
   (e.g. after Dictation, show "Come back for today's check tomorrow" instead of silently skipping to
   fluency) — this would turn the P1 bug's *symptom* into an intentional-feeling design even before the
   root cause is fixed, and is worth doing regardless.
6. Once the in-flight edits (placement check, parent report, romanisation/audio-first settings) settle,
   run a focused follow-up QA pass specifically on those three new surfaces — they were not covered by
   this report.
7. Add an automated smoke check (script or CI job) that runs a session to unit-1-quiz-pass headlessly on
   every commit — this exact bug (quiz never appearing on the first pass) would have been caught
   immediately by a script identical in spirit to the one used for this QA pass.
