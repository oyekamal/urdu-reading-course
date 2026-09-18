# Teacher Mode Critic — Round 1

Tested live at http://localhost:5179/ with Playwright (chromium, 390x800), source
`mobile/src/teacher.js` + `mobile/src/egra.js`, against `research/08_teacher_tools.md`
§3–5 and `docs/offline-app-plan.html` §3 "Teacher mode screens" / §5 "Every test".
Flow run: My class → PIN 1234 → 3 children (Ali, Sara, Bilal) → full EGRA on Ali
(skip letters/nonwords/words, real passage + comprehension run) → Reports.

Screenshots and raw DOM text in `.audit/` companion run (scratchpad) — key evidence
quoted inline below.

## Findings, one by one

1. **Timer visibility** — Renders at 44px (`.timer{font-size:44px}`), but is a normal
   in-flow block above the grid, not `position:sticky`. On the 100-letter subtask the
   grid is 2628px tall in a 390x800 viewport (measured `.grid-words` bounding box),
   so the timer scrolls off-screen after roughly the second row. A teacher and child
   both looking at the tablet lose the countdown the moment they need to scroll to
   see more letters. **Fails** the "large display" requirement in
   `08_teacher_tools.md` §3.2 step 2.

2. **60s countdown accuracy** — `startTimer()` (egra.js) is `Date.now()`-based, not a
   drifting `setInterval` count; it recomputes `remainingMs` every 200ms tick and
   fires `onDone` exactly when `remainingMs<=0`, then flashes + `beep()`. This is
   correct and matches Tangerine's audible/visual stop. **Passes.**

3. **Stop rule (first 10 wrong ends subtask)** — Implemented in `checkStopRule()`
   (egra.js `runFlashSubtask`): fires only when all of indices 0–9 are marked wrong,
   matching the real EGRA "0 correct in first 10" rule (not a naive "any 10 wrong").
   Verified live: clicking items 0–9 as wrong on the Nonword subtask produced the
   toast `Stop rule: first 10 wrong — subtask ends at 0` and auto-advanced to the
   next subtask. **Passes**, but only implemented for the three flash-card subtasks —
   correctly absent from the passage subtask (matches the "None" stop-rule column
   for Oral Passage Fluency in the research table).

4. **"Last word reached" on the passage** — Implemented (`markMode` toggle +
   click-to-set `lastIdx`, orange outline). Verified: toggling mark mode and tapping
   word index 8 set `attempted=9` and fed it into the cwpm calc. **Passes.**

5. **cwpm formula** — Confirmed by live run: `cwpm = round((attempted - errors) * 60 /
   seconds)`, exactly `(attempted − errors) × 60 / seconds` as specified. Uses actual
   elapsed wall-clock seconds (capped at 60), not a flat "/60", so early finishes via
   "Child finished" are prorated correctly. **Passes.**

6. **Accuracy shown** — Yes, `Passage accuracy: 78%` appeared on the Result screen
   for the live run. **Passes**, but only for the passage subtask — letters/nonwords/
   words show only raw counts with no accuracy or per-subtask pass/fail vs. any
   benchmark, unlike Tangerine's per-subtask scoring.

7. **Benchmark bands — MISMATCH with the app's own plan.** `content.js` defines
   `BANDS = [['pre-reader',0],['letters',1],['words',20],['sentences',40],['fluent',60]]`
   — five app-invented labels keyed purely to passage cwpm. But
   `offline-app-plan.html` §3 item 4 explicitly promises: *"mapped to bands (above 90
   cwpm exceeds, 60 to 90 meets, under 60 below, 0 nonreader)"* — the PRP/ASER
   4-band scheme. The shipped code implements neither PRP's exact bands nor
   documents the substituted scheme anywhere the teacher can see (no explanation on
   the Result, Groups, or Reports screen of what "fluent" or "sentences" means in
   cwpm terms — the teacher only sees `GROUP_ACTIVITY` text on the Groups tab, not on
   Result/Reports). This is a genuine spec-vs-code divergence, not a stylistic
   choice — the design doc names specific PRP-style bands and the code silently
   ships a different taxonomy.

8. **Grade is collected but never used in the benchmark.** `profile.grade` is
   captured on the roster (Class tab) but `bandFor(cwpm)` takes no grade argument —
   a Grade 1 child and a Grade 3 child hit "fluent" at the exact same 60 cwpm, even
   though ASER's own benchmark (§3 "60 cwpm at end of Grade 3"; "45–60 cwpm Grade 2
   threshold") is grade-differentiated. The research and plan doc both name
   grade-specific benchmarks; the code ignores grade entirely.

9. **Saved and visible in Reports/Progress** — Assessment record is `db.put`'ed with
   `profileId`, and both Reports (sortable table + histogram) and Groups (band
   buckets) query it live via `loadRoster()`. Verified: after Save, Reports showed
   Ali's row with correct cwpm/band, and the "Passage cwpm" column header is
   click-sortable (verified toggling `▲`). **Passes.**

10. **Parent slip actionability** — Text is one paragraph: name, date, cwpm number,
    band, and a single fixed-per-band sentence of advice (e.g. "practise the unit
    word list daily"). Functional and plain-language, but generic — no next
    concrete activity (no page/word-list reference), and it repeats the same
    band-label problem from finding 7 (a parent sees "Band: fluent" without any
    anchor to what that means).

11. **Lesson script (40-minute runnable plan)** — Real content is fetched from
    `data/lessons/unit_NN.md` and rendered: I Do (10 min, letter cards + Play
    name/word audio buttons), We Do (15 min, chorus word grid), You Do (15 min,
    written rotation instructions naming which drills each band does). This is a
    genuinely runnable 40-minute script with real timings and talking points.
    **However**, the "Full lesson script" section below it dumps the raw markdown
    through a minimal renderer that treats pipe-table lines as literal
    `<pre>` text — table rows for letter-stroke instructions render as one long
    wall of `| Letter | Name | Sound | ... |` text, and raw asset paths
    (`assets/audio/names/alif.mp3`) leak into what a teacher reads mid-lesson.
    Content is real; presentation of the script's tables is not teacher-usable.

12. **Groups — concrete activity per band** — Yes: `GROUP_ACTIVITY` maps each of the
    5 bands to one concrete instruction (e.g. "words: Read and Dictation drills,
    this unit's word list") and the Groups tab lists which children are in each
    band plus an "Not yet assessed" bucket. **Passes** the TaRL concrete-activity
    requirement, modulo finding 7/8's band-taxonomy problem underneath it.

13. **Class report sort/export** — Sortable by clicking any column header (verified
    live, toggles ascending/descending with ▲/▼). CSV export and full JSON backup
    both work via `shareOrDownload()` (native Share → Web Share → download-link
    fallback chain). **Passes.**

14. **The 100-letter grid on a 390px phone — fails outright.** `renderGrid()` groups
    letters into rows of 10, but every item carries the `.big` class
    (`font-size:72px`), and the outer containers (`.row`, `.grid-words`) are plain
    `display:flex;flex-wrap:wrap`. The intended 10-per-row grouping is invisible —
    at 72px per glyph, roughly 2 letters fit per visual line on a 390px screen, so
    the "row" divs just wrap internally. Measured live: 100 `.item` elements produce
    a 328×2628px block — ~3.3 phone-screens of vertical scroll, under a
    non-sticky 60-second timer (finding 1). This is not "usable one-to-one"; it is
    unusable. Same defect hits the 40-nonword and 50-word subtasks proportionally.
    **Tangerine's own subtask screens page a fixed small set (10) at a time** —
    this app should adopt exactly that instead of dumping the full item list.

## Blind A/B (A = ours, B = Tangerine / Kolibri Coach / PRP guide as described in research)

| Component | Winner | One line |
|---|---|---|
| Assessment flow (timer/stop-rule/scoring mechanics) | **A** | Stop-rule and cwpm math are correctly EGRA-faithful and drift-proof — better engineered than the spec required, undermined only by presentation (findings 1, 14). |
| Class roster | **B** | Tangerine/Kolibri roster is built for one-to-one, add-in-seconds, no-grade-blind scoring; ours collects grade but never uses it (finding 8). |
| Lesson script | **A** | PRP's scripted guides are PDF-only, non-interactive; ours is a real in-app 40-minute script with tappable audio per letter — content wins even though table rendering is broken (finding 11). |
| Grouping (Groups tab) | **B (tie leaning B)** | TaRL's proficiency levels are evidence-validated and grade-aware; ours reinvents a 5-band scheme that contradicts the product's own plan doc (finding 7) and isn't grade-aware (finding 8). |
| Reports | **A** | Sortable, exportable (CSV+JSON), histogram, fully offline with no cloud round-trip — matches or beats Kolibri Coach's dashboard for this use case. |
| Parent communication | **B** | ASER/Tangerine parent slips anchor to a named, explained benchmark; ours shows a band label ("fluent") the parent has no way to interpret without cross-referencing code that isn't shown anywhere in the UI (findings 7, 10). |

**Tally: A 3 — B 3** (one tie scored to B on evidence weight).

## Prioritised fix list (max 10)

1. **Reconcile the band taxonomy with the plan doc** (`content.js` `BANDS`) — either
   implement the PRP 4-band scheme literally promised in
   `docs/offline-app-plan.html` §3 item 4 (0 nonreader / 1–59 below / 60–90 meets /
   >90 exceeds), or rewrite that doc line to match the shipped 5-band scheme and
   surface the cwpm cutoffs on the Result screen so "fluent"/"sentences" aren't
   opaque labels. `bandFor()` in `content.js:22`.
2. **Page the flash-card subtasks 10 at a time**, Tangerine-style, instead of
   rendering all 100/50/40 items in one scrolling flex-wrap block. `renderGrid()` /
   `runFlashSubtask()` in `egra.js`.
3. **Make the timer sticky** (`position:sticky;top:0`) on all four timed subtask
   screens so it stays visible regardless of scroll position. `.timer` in
   `mobile/src/style.css:21`, applied via the `wrap` in `runFlashSubtask()` and
   `runPassageSubtask()` in `egra.js`.
4. **Make bands grade-aware.** Pass `profile.grade` into `bandFor()` (or a new
   `bandForGrade(cwpm, grade)`) and use ASER's grade-specific thresholds (45 cwpm
   Grade 2, 60 cwpm Grade 3) instead of one flat scale for every grade.
   `bandFor` call sites: `egra.js` `renderResult()`, `teacher.js` `renderClass()`
   and `renderGroups()`.
5. **Fix the lesson-script markdown table renderer** so PRP-style pipe tables
   render as an actual table (or a clean letter-by-letter card list) instead of a
   `<pre>`-dumped wall of `| … |` text with raw asset paths visible.
   `renderMarkdown()` in `teacher.js`.
6. **Shrink item font size for high-count subtasks.** Only reduce `.big` to a
   smaller size (e.g. 32–36px) when `items.length > ~15`, so letters/nonwords/words
   actually form a visible grid instead of wrapping to near-single-column.
   `renderGrid()` in `egra.js`.
7. **Show per-subtask accuracy/benchmark, not just raw counts**, for letters,
   nonwords and words — currently only the passage subtask gets an accuracy %.
   `renderResult()` in `egra.js`.
8. **Surface the band cutoffs on the parent slip**, not just the label, so a parent
   without app access can see "60+ cwpm = fluent" rather than an unexplained word.
   Parent-slip builder in `teacher.js` `renderReports()`.
9. **Strip or replace the leaked audio asset paths** in the rendered lesson script
   (e.g. `assets/audio/names/alif.mp3`) with the intended clickable "Play" controls
   the "I do" section already provides above it — the raw-markdown dump duplicates
   and exposes what the structured UI already does better. `renderLesson()` in
   `teacher.js`.
10. **Add a fixed-position "seconds remaining" mini-indicator in the tab bar** as a
    fallback for finding 1/3 — even with the sticky timer fix, a bottom-anchored
    countdown gives a second point of reference on very tall content the way
    Tangerine's minimal single-screen-per-item UI never needed to.
