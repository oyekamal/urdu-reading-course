# Urdu Qaida QA / a11y / edge audit

Scope: Playwright (chromium) against the live dev server http://localhost:5188/ (working tree was dirty and being edited by others during the run: main.js, path.js, style.css, vite.config.js). Child profile seeded to unit 4. Matrix: 360x640 and 412x880, each light / dark by OS, plus Appearance forced both ways (OS light + data-theme=dark, OS dark + data-theme=light), plus 320x568, text size Extra large (1.5) and landscape 640x360 / 800x360 XL. Harness scripts live in the session scratchpad (h.py, audit.js, walk.py, layout.py, back*.py, data*.py, perf*.py); no repo files were edited.
`tools/ui_audit.py` was not re-run (known stale check).

Severity: H = users lose work or get wrong behaviour, M = real a11y / data issue, L = polish or hand-edit-only.

---

## Defects

### D1 [H] Android Back on the celebration screen opens "Leave this lesson?" on top of it, and Leave leaves the celebration stuck on the home screen
- File: `src/back.js:5` (`OVERLAYS` has no `.celebrate`; `a11y.js:14` treats `.celebrate` as a modal dialog).
- Repro: seed unit 4, finish the "Blend" lesson (celebration shows "Blend done!"), call `(await import('/src/back.js')).handleBack()`.
- Expected: Back dismisses the celebration and returns to the path (same as its "Path" button, aria-label "Back to path").
- Actual: `handleBack()` finds no overlay, falls through to `[aria-label="Leave lesson"]` on the inert lesson behind the celebration and opens the confirm sheet on top (`body` children: `celebrate, a11y-sheet`). Choosing Leave navigates Learn but `.celebrate` stays in the DOM on top of it (`ov: ['celebrate']`, heading behind = "Good morning, Zara"). The user can then only escape with the celebration buttons; two more Backs hit the "press again to close the app" path with the celebration still showing. Lesson was already saved (progress verified), so no data loss, but the screen is wrong and confusing.
- Fix: one line, add `body > .celebrate` to `OVERLAYS` and `.cel-back` to `CLOSERS`.

### D2 [M] Every speaker button in word lists is named just "Play" (screen reader users cannot tell which word)
- File: `src/drills.js:12` `playBtn()` hard-codes `aria-label="Play"`. Used by `readIt` (drills.js:84, word cards), sentence rows (learner.js:154), letter card (drills.js:26).
- Repro: Units tab, open Unit 4 (or 5) page as child or adult; count `button[aria-label="Play"]`.
- Measured: 168 identical "Play" buttons on unit 4 (153 on unit 5); 13 per Words lesson "Read" step. Also `drills.js:41/224` say "Play sound"/"Play word" (generic but singular, ok).
- Expected: "Play meri", "Play name of be", "Play sentence 3".
- Fix: `playBtn(key, small, label='Play')`, pass `` `Play ${w.rom}` `` at the call sites (rom/name is already at hand in each).

### D3 [M] Mid-lesson reload / process kill drops the learner back to the start of the lesson while the exit sheet promises "Your progress here is saved."
- Files: `src/a11y.js:193` and `src/path.js:120` (copy); no step persistence in `path.js` `runLesson` (only `markLesson` at finish).
- Repro: open Words 1 (unit 4), advance to "Build the word", reload the page. Lands on Learn home; the lesson restarts at step 1 (per-answer attempts are saved, the position is not). Android: OS kills the app in the background, same result.
- Expected: copy matches reality, or resume at the step.
- Fix: change body to "Finished lessons are saved. Leaving now starts this one again." or persist `{unit, lessonId, i}` in sessionStorage/settings and resume.

### D4 [M] Urdu Text size / spacing stored values are not validated at read time (invisible Urdu text for a bad value)
- File: `src/main.js:47` `apply()` writes `settings.scale || '1'` straight to `--ur-scale` (same for spacing). `backup.js:38` validates imports, but a value already in IndexedDB is trusted.
- Repro: `db.put('settings',{key:'ui',value:{scale:'0'}})`, reload. Measured `.ur` computed font-size: scale "0" gives 0px (every letter invisible), "abc" gives broken scaling (24/16px), "50" gives 850px. `ui` = string/array/null and garbage `mode` / `activeProfile` / `deviceId` / `teacherPin` were all handled cleanly (no crash, no recovery screen needed).
- Fix: `const sc = ['1','1.25','1.5'].includes(String(settings.scale)) ? String(settings.scale) : '1'` (same whitelist for spacing and `style`).

### D5 [M] Appearance (theme) is lost on backup / restore  (from code reading, not executed)
- File: `src/backup.js:38` `UI_KEYS` has no `theme`; `shape()` drops unknown keys; `db.importAll` replaces the whole `ui` record when the backup copy is newer, so restoring resets Appearance to "Match my phone" (and the export already contains `theme`, so the file looks complete).
- Fix: add `theme: oneOf('', 'light', 'dark')` to `UI_KEYS`.

### D6 [L] Contrast failures (all measured with composited colour, bg-image cases excluded or pixel-sampled)
| Where | Ratio | Need | File |
|---|---|---|---|
| Me tab letter grid, letters "not yet taught", 34px glyph, opacity .45, light mode (dark mode passes) | 2.58:1 | 3:1 | `dashboard.js:19` (opacity .45) |
| Lesson word card, highlighted letter `color:var(--accent)` (#1E9C8F) on white, 16px/600, light mode | 3.38:1 | 4.5:1 | `path.js:167` (use `var(--accent-deep)`) |
| Locked path pearls' captions, 11px at 0.7 alpha, light 2.8 to 2.9:1, dark 4.16:1; "ا د ر" caption 1.7:1 / 2.2:1 | below 4.5 | n/a if treated as disabled, but 11px | `style.css:69,88` |
| Read tab disabled "Stop" button text, light 2.93:1, dark 4.38:1 | disabled, exempt | | |
- Fix: dashboard opacity .45 to .62 (or keep full opacity and use a dashed border for "not taught"); `path.js:167` accent to accent-deep; bump locked captions to 12px and 0.85 alpha.

### D7 [L] Native controls do not follow the forced Appearance  (from code reading, not rendered)
- No `color-scheme` anywhere (`index.html`, `style.css`). With OS dark + Appearance Light (or vice versa) the select popup, checkbox, scrollbar and keyboard stay in the OS scheme.
- Fix: `:root[data-theme=dark]{color-scheme:dark}` and `:root[data-theme=light]{color-scheme:light}` (and `color-scheme: light dark` on bare `:root`).

### D8 [L] Landscape + Extra large: lesson content area is only 186px of 360px; letter card is cut to a third
- Repro: 640x360, Text size Extra large, open any letter lesson (shot `shots/land_lesson.png`). `.les-scroll` clientHeight 186 / scrollHeight 561 (scrollable, focusable region, so reachable, but heavy).
- Fix: in landscape short viewports hide `.lesson .muted` sub-header and shrink the progress bar / header, or put the docked primary beside the content.

### D9 [L] `.card.unit` on Learn clips 5px at the bottom at every viewport (scrollHeight 485 / clientHeight 480 at 360x640)
- Same at 320 to 412 and landscape; cosmetic (overflow hidden on the unit card). Check `style.css` `.card.unit` overflow vs padding.

### D10 [L] Transient hint bubble covers the question text in the 360x640 quick check
- "Listen again: this is wāʾo" bubble sits over "For the letter you hear" (shot `shots/walkfail_360_Lwao.png`). Clears with the bubble timeout; low impact.

### D11 [L] Keyboard / SR polish
- Learn lists every locked pearl as a focusable button (14+ tab stops before the nav bar). Suggest `tabindex=-1` on locked ones past the next lesson, or a skip link. Locked ones are labelled "…, locked" so they are understandable.
- Me tab checkboxes: the `<input>` itself measures 13x48; the surrounding `label.row` is the real target (fine), but the 13px native box is small for the child track.
- The "Round 1/5 · 0 right" `.score` line is not a live region (answers themselves are announced).
- `db.js` `fix()` for profiles runs `cleanName(o.name)` on non-strings: a hand-edited `name: {a:1}` renders "Good morning, [object Object]". Hand-edit only; coerce with `typeof === 'string'`.

---

## Verified clean (no defect found)

Tap targets
- All buttons/links/selects >= 44x44 on Learn, Review, Read, Me, Units, onboarding (welcome to name/goal), letter / join / blend / words / non-joiner / read / quiz lesson steps, gate, confirm sheet, sticker book, at 360x640 light and 412x880 dark. Only exception: the 13px checkbox input noted in D11 (its label row is 48px).
- Child-track tiles and speaker buttons reach the larger child sizes (no `child-tile<64` hits in the steps walked).

Contrast
- Light, dark, OS-dark + forced-light and OS-light + forced-dark render identical results on every screen walked (the manual `data-theme` twins from the vite postcss plugin work; same failures in both routes, nothing extra from forcing).
- No failures on onboarding screens, home hero, path pearls (unlocked), word cards, quiz, gate dialog, confirm sheet in any theme. Celebration (white on teal gradient) pixel-sampled: sub-line 4.67 to 4.72:1, heading 3.54:1 (large), both pass.

Keyboard / screen reader
- Visible 3px focus ring on every stop, in both themes.
- Confirm sheet: focus lands on "Keep going", Tab / Shift+Tab cycle only inside the sheet, Esc closes it, background is `inert`.
- Icon-only buttons in lessons are named ("Repeat instruction", "Leave lesson", "Say wāʾo again", "Hear the word", "Switch learner", "Tap Marko to say hi"). Letter tiles carry letter names ("be", "wāʾo"), not glyphs. Zero unlabeled buttons or fields found on any screen walked.
- Answers: wrong tap announces "Not quite. This is wāʾo, no dots!" via `#a11y-live`; correct tap announces "Correct: wāʾo" via the polite toast.
- Single `h1`, `main`, nav landmarks labelled; `.les-scroll` becomes a focusable "Lesson content" region only when it overflows.

Layout
- No horizontal page scroll or element overflow on Learn, Review, Read, Me, Units or lesson steps at 320x568, 360x640, 412x880, each also with Text size Extra large (1.5), and landscape 640x360 / 800x360 XL. Docked primary stays above the nav (portrait) and the nav becomes a left rail in landscape (primary top 284, bottom 332 of 360).

Android Back (`handleBack()` via `import('/src/back.js')`)
- Home (Learn): returns false, so the "Press back again" toast / exit path runs.
- Review / Read / Me tabs and Units sub-screen: each returns true and lands on Learn.
- Mid-lesson: first Back opens the leave sheet, second Back closes it, third reopens; no stacking, no trap, progress untouched.
- Grown-up gate and Sticker book: Back closes each (`.gate-cancel`, `.stk-back`).
- Onboarding: welcome returns false (exit prompt), later steps step backwards, name text preserved is not tested.
- Only defect: D1 (celebration).

Data safety
- Triple-click on "I heard it" advanced exactly one step (progress 0% to 20%); `tapLock` works.
- Finished lesson wrote one pearl, attempts recorded once; no double pearls.
- IndexedDB `put` throwing QuotaExceededError mid-lesson: toast "That did not save. Please try again." appears, lesson stays on screen (the 4 `pageerror`s in that run came from my stub throwing synchronously, not from the app).
- `indexedDB.open` throwing at boot: recovery screen appears with Try again / Export what can be saved / Start fresh (all 56px tall).
- Corrupt `ui` (string / array / null), `mode` (number / object), `activeProfile` (object / unknown id), `deviceId`, `teacherPin`, `progress` (string, array units, string lessons): app boots, no recovery screen needed, no console error. (Only the D4 scale values and the D11 name-object case misbehave.)

Performance
- Largest per-lesson Words list is 13 words (lessons are chunked ~12-13); the only 100+ word screen is the Units page for a unit (unit 4: 141 words, 168 play buttons, 2,240 DOM nodes, 31,467px tall; unit 5: 125 words, 2,125 nodes). Scroll under load: p95 16.7ms, max 66ms, 0 long tasks, heap 12MB.
- 5-minute scripted session (tabs + letter/join/words/blend lessons, ~12 cycles): JS heap 8.8MB to 11.4MB and back to 10.7MB, DOM nodes oscillating 689 / 323 with no growth, Lottie SVG count 56/11 with no growth, `body` children steady at 5. No leak, no console errors.
- spring.js: with motion enabled, 3 rounds of rapid tab switching (14 switches at 35 to 115ms) then 3.5s settle: zero elements left with inline opacity<1, scale or translate (only the intentional `opacity:.45` letter-grid spans). A one-off mid-animation reading (`scale 1.0068`) at the end of a scripted run was not stuck on re-check.

## Not covered
- Real device TalkBack / Android keyboard behaviour (kb-open lift), real storage-full conditions (stubbed), audio playback, the teacher mode screens, adult 6-tab bar contrast.
- D5 and D7 are from reading code, not from a rendered repro.
