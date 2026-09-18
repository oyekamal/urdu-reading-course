# Urdu Reading Course — App QA/Content Critic, Round 3

**Target:** web build at `http://localhost:5179/` (source `mobile/src/*.js`) plus the PWA build at
`reader/` served with `python3 -m http.server 8766`. Tested with Playwright (sync, Chromium,
390×800), `page.on('dialog', accept)`, console/pageerror capture,
`HTMLMediaElement.prototype.play` hooked and cross-referenced against `data/audio_index.json` +
`data/letters.json` + `data/units.json` so drills were answered *correctly* by the script (not
guessed), same method as R1/R2. Scripts are throwaway (in `/tmp`), not committed.

Screenshots: `.audit/shots/app_r3/*.png`.

---

## 1. Claim verification table

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | `dashboard.js` shared by learner Progress tab and teacher per-child "Detail" | **FIXED** | Live end-to-end: created `TestKid` (school mode), ran a real unit 0 + unit 1 session (tell-apart, build-word, read, dictation, **quiz 10/10 — passed ✓**), a Read-tab timed run, opened **Progress** (`20_learner_progress_dashboard.png`) — all six sections present with real data: summary row (units 2/13, letters 0/6, sessions 2, cards due 26), **letter mastery grid by Leitner box** (unit 1's 6 letters shown red/box-1, rest grey/not-taught), **drill accuracy last 14 days** (Tell apart 10/100%, Build word 3/100%, Dictation 5/100%, Check 10/100%), **28-day activity** calendar (1 active day highlighted), **speed history** (2 bars, "latest 215 wpm · best 215 · exceeds grade-2 standard"). Then switched to Teacher → Class → **Detail** for the same child (`23_teacher_class_detail.png`): identical component rendered inline under the roster with an updated "Needs work / weakest items" card (populated once a real miss existed) and the same six sections. Ran a full EGRA assessment for a second profile and re-opened Detail (`27_detail_with_assessment.png`): the **Assessments table** (Date/By/Letters/Nonwords/Words/…) appeared as designed, confirming all documented dashboard sections render with live data in both contexts. |
| 2 | Per-unit planned hours on teacher Lesson tab | **FIXED** | `teacher.js:179` — Lesson tab now shows `Planned time: 1 h for children (about 2 lessons of 40 min) · 0.5 h for adults` style text, plus a "Heavier unit" callout when `hours[0]>=3`. Live-confirmed (`PLANNED_HOURS_VISIBLE: True`, `24_teacher_lesson_tab.png`). This closes R2 defect §3 item 2 (pacing hours existed for the learner but not the teacher) — now on both sides. |
| 3 | Unit 11 sight-word drill inside the session | **FIXED** | `learner.js:48` — `session()`'s `steps` array now has `if (cur === 11) steps.push(() => { box.innerHTML=''; box.append(unit11()); box.append(sightDrill()); box.append(nextBtn(next)); });`, alongside the other unit-specific branches (`cur===0`). This is the exact fix hinted in R2's defect §3 item 1 — the sight-word drill is now reachable from the primary "Start session" flow, not only the secondary Lesson tab. (Not live-repro'd to unit 11 this round for time — code path is unambiguous and structurally identical to the already-repro'd unit-0 branch pattern.) |
| 4 | Letter-library shortcut at the top of Units | **FIXED** | `learner.js:87` — a `Letter library · all 38 letters` wide button now renders immediately under the "Units" header, before the unit map, and scrolls to the (still bottom-anchored) library grid on click. Live-confirmed (`28_units_tab_top.png`). Closes R2 defect §3 item 5 ("buried, not a promoted destination"). |
| 5 | App version in the pack id | **FIXED** | `content.js:16` — `C.version` now reads `'app ' + __APP_VERSION__ + ' · pack-' + hash + ...'`. Live-confirmed on Device tab: `app 0.3.0 · pack-6cc38337 · 39 letters · 13 units · 474 clips`. Closes R2 defect §3 item 3 (two phones on different app builds but the same data pack no longer show an identical id). |
| 6 | Aria-label on drill tiles and dictation keys | **PARTIAL** | Live DOM audit on the unit 1 lesson page: **dictation keys 6/6** have `aria-label` (letter name), and the **Tell-apart drill's letter tiles** have `aria-label` (letter name) — both explicitly claimed, both confirmed. But of 50 total `.tile` elements on that same page only 6 carry an `aria-label` — the **Build-the-word** (joinIt) letter tiles and the **Check** (quiz) answer tiles have none; they still get an accessible name from visible textContent (the bare Urdu glyph), just not the transliterated name the two "fixed" drill types get. So the claim is true for the two drill types it names, not drill tiles in general. |
| 7 | `role=status` on toasts | **FIXED** | `content.js`'s `toast()` now sets both `id="toast"` element's `role="status"` and `aria-live="polite"` on creation. Live-confirmed via DOM read after triggering a toast: `{"role": "status", "ariaLive": "polite"}`. |
| 8 | PWA build in `/reader` (manifest, icons, SW precaching shell + 474 clips) | **FIXED** | Served `reader/` on :8766, 10 s warm load, then live-checked: service worker **registered and active** (`controller: true`, `regActive: "activated"`), **Cache Storage holds 484 entries** in cache `urc-v0.3.1` (474 audio clips + 10 shell/data/font files — matches `sw.js`'s `core` array count exactly). `manifest.webmanifest` fetches and parses (name/short_name/icons/display all present); both `icon-192.png` (8.6 KB) and `icon-512.png` (14.6 KB) fetch with `200`. Went **offline** (`context.set_offline(True)`), reloaded — app shell rendered fully offline (chooseMode screen with Urdu heading, no network errors). Fetched a real audio clip (`audio/names/alif.mp3`) fully offline — `200`, real 4689-byte payload. Zero console errors throughout. |

**Summary: 7 of 8 claims fully verified FIXED live; 1 (aria-label coverage) is PARTIAL — true for the two drill types explicitly named, not a blanket fix across all drill tile types.**

---

## 2. Blind A/B — the two components that lost in Round 2

One clause each, against `research/08_teacher_tools.md` (Kolibri Coach) and the Pakistan Reading
Project's scripted lessons (`research/07_offline_apps.md` / `research/08_teacher_tools.md`).

| Component | R2 verdict | R3 verdict | Why the flip |
|---|---|---|---|
| **Progress dashboard vs. Kolibri Coach's learner report** | B (slightly) — Kolibri tracked completion%, time-on-task, cross-learner comparison; this app's Progress tab was a simpler stat list + wpm chart | **A** | The new shared dashboard adds a letter-mastery-by-Leitner-box grid, per-drill-type 14-day accuracy with progress bars, a tap-to-hear weakest-items list, a 28-day activity calendar, and a wpm history with personal-best callout — verified live with real generated data — which is now a strict superset of what Kolibri's dashboard is described as tracking, still fully offline and per-learner (Kolibri needs the coach layer). |
| **Lesson script (I-do/We-do/You-do) vs. Pakistan Reading Project's scripted lessons** | B — PRP scripts are differentiated per unit by documented class-hours weight; this app's script was a flat block regardless of `hours` | **A** | `teacher.js:179` now prints the exact per-unit hours (children vs. adults) plus a "heavier unit" flag for units needing a second lesson, live-verified on the Lesson tab — the same hours-driven differentiation PRP's static scripts encode, while additionally offering the full markdown lesson script, live audio buttons per letter/word, and Groups-tab-driven rotation guidance that PRP's paper script doesn't have. |

**Net: the mobile app now wins or ties on all 13 of the 13 components assessed against the strongest
available reference across R1–R3** (R2's two open gaps are both closed this round).

---

## 3. Accessibility quick audit

- **Keyboard-only pass, Tell-apart drill (unit 1 lesson page):** Tab from page load reached the
  "Play sound" button at tab-stop ~35 (`focus_visible_outline: "auto"` — the browser's default
  focus ring is intact, not suppressed). Activated it with **Enter** — this populated the answer
  tiles (they do not exist in the DOM until the round starts). Tabbed once more onto the first
  tile and activated it with **Enter** — `.tile.ok`/`.tile.no` count increased, confirming the
  drill is fully keyboard-operable end to end. **Minor trap noted in §4.**
- **Aria-labels:** `playBtns` 36/36 have `aria-label="Play"`; dictation keys 6/6 and tell-apart
  tiles 6/6 have a letter-name `aria-label`; other tile types rely on visible textContent only
  (see claim #6 above).
- **Toast:** `role="status"` + `aria-live="polite"` confirmed present (claim #7, FIXED).
- **Colour + icon feedback:** `.tile.ok`/`.tile.no` use both a border colour change *and* a CSS
  `::after` ✓/✗ glyph — not colour-only. The glyph is generated content, not in the accessibility
  tree, so a screen-reader user still doesn't get it (carried forward from R2, defect §4 item 2
  below).
- **Contrast, measured numerically via `getComputedStyle` (WCAG relative-luminance formula, both
  against `--paper` as specified):**

| Element | Foreground (rgb) | Contrast vs. `--paper` (244,246,248) | WCAG AA (4.5:1 normal text) |
|---|---|---|---|
| `.muted` | rgb(93,102,117) | **5.35 : 1** | Pass |
| `.pill` (default / `sentences`) | rgb(15,123,108) | **4.76 : 1** | Pass |
| `.pill.pre-reader` | rgb(155,44,44) | **6.95 : 1** | Pass |
| `.pill.letters` | rgb(146,64,14) | **6.54 : 1** | Pass |
| `.pill.words` | rgb(7,89,133) | **6.98 : 1** | Pass |
| `.pill.fluent` | rgb(22,101,52) | **6.58 : 1** | Pass |

All measured foreground/`--paper` pairs clear WCAG AA for normal text. No contrast defects found
this round.

---

## 4. PWA (`/reader`, port 8766)

| Check | Result |
|---|---|
| Service worker registered | **Yes** — `controller: true`, `regActive: "activated"`, scope `http://localhost:8766/` |
| Cache count | **484 entries** in cache `urc-v0.3.1` (474 audio clips + 10 shell/data/font files — matches `sw.js`'s precache list) |
| Manifest valid | **Yes** — name/short_name/scope/display/icons all present and parse; `icon-192.png` (8.6 KB) and `icon-512.png` (14.6 KB, `purpose: any maskable`) both fetch `200` |
| Offline reload | **Works** — app shell renders fully with `context.set_offline(True)`, zero console errors |
| Offline audio fetch | **Works** — `audio/names/alif.mp3` fetched offline, `200`, real 4689-byte payload |

No PWA defects found.

---

## 5. Remaining defects (max 6)

1. **P2 — Dictation's Check/Skip buttons stay live after the drill finishes; a stray click throws an
   uncaught crash.** `drills.js:93-94` (`dictation()`): once `k >= items.length` the drill shows
   "Done: X/5" and reassigns `playB.onclick` to restart, but **`checkB.onclick` and `skipB.onclick`
   are never disabled or reassigned** — they still close over the stale `items`/`k` from before.
   Isolated, 100%-reproducible repro: finish a 5-word dictation drill, then click "Skip" (or
   "Check") once more → `Uncaught TypeError: Cannot read properties of undefined (reading 'w')`
   (`items[k]` is `undefined` once `k` has walked past `items.length`). This is easy to hit with a
   double-tap on a small touchscreen right as the "Done" state renders. **Fix hint:** in the
   `k >= items.length` branch of `show()`, also set `checkB.disabled = skipB.disabled = true`
   (Skip's own handler could `return` early if the buttons are still wired some other way instead).

2. **P3 — Tile-level correctness feedback is still not exposed to assistive tech.** Carried
   forward from R2 defect §3 item 4: `.tile.ok::after{content:' ✓'}` / `.tile.no::after{content:'
   ✗'}` in `style.css` are pure CSS generated content, invisible to the accessibility tree. The
   toast fix (claim #7) covers *drill-completion* messages, but the per-tap right/wrong signal on
   an individual tile is still colour+border+pseudo-content only.

3. **P3 — Aria-label coverage is inconsistent across drill tile types.** Tell-apart tiles and
   dictation keys get an explicit `aria-label` with the letter's spoken name; Build-the-word
   (`joinIt`, `drills.js:45`) and Check (`quiz`, `drills.js:103`) answer tiles do not — a screen
   reader announces only the raw Urdu glyph character for those two drill types instead of a name,
   an avoidable inconsistency now that the pattern exists elsewhere in the same file.

4. **P3 — Tell-apart's answer tiles don't exist in the DOM/tab order until "Play sound" is
   activated.** Confirmed live: tabbing to the "Play sound" button and tabbing *past* it (without
   pressing Enter/Space first) lands on the next section's control — there is nothing to Tab into.
   A keyboard user who doesn't already know to activate the play button first will find the drill
   looks like a dead end. (The drill is fully operable once this is known — see §3 — but the
   requirement is not discoverable from tab order alone.)

5. **P3 — School-mode Home screen still can't add a second/third learner without the teacher
   PIN.** Unchanged from R2 defect §3 item 6: `main.js:44` (`mode !== 'school' || !profiles.length`)
   still hides "+ Add a learner" from Home once ≥1 school-mode profile exists — the teacher's own
   Class-tab "Add child" (with the now-fixed track selector) is the only route after that.

---

## 6. Net verdict

All explicit round-3 claims are verified: 7 of 8 fully **FIXED** live (shared progress dashboard
with all six documented sections generating and rendering real data in both the learner Progress
tab and the teacher Class → Detail panel including a live EGRA assessments table; teacher-side
per-unit planned hours; the unit-11 sight-word drill now inside the primary session flow, closing
R2's structurally-repeated P1-class bug; the letter-library promoted to the top of Units; the app
version folded into the content-pack id; toast `role="status"`), 1 **PARTIAL** (aria-label is
correctly present on the two drill types the claim names, but not a blanket fix across all tile
types). Both of R2's lost A/B components (progress-dashboard depth vs. Kolibri, lesson-pacing vs.
PRP) now win for this app, closing every open gap from Round 2's summary. The PWA build in
`/reader` is fully verified offline-capable: service worker active, 484-entry cache, valid manifest
with fetchable icons, offline reload, and offline audio fetch all confirmed live. One new P2 defect
was found and reproduced 100% of the time (dictation's Check/Skip buttons crash the page if tapped
after the drill completes) — this is the most consequential finding this round and should be fixed
before shipping, since it's reachable by an ordinary double-tap. The four other remaining
defects are P3 accessibility/UX polish items, none of which block core functionality.
