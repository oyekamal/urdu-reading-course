# Content-completeness audit — mobile app vs. course, round 1

**Auditor stance:** harsh critic, gauntlet-loop round 1. Bar = the course (`course/00_design.md`, `course/unit_00–12.md`), the web reference app (`app/template.html`), the promised feature/test inventory (`docs/offline-app-plan.html` §2, §3, §5), and the content pack (`data/letters.json`, `data/units.json`).

**Method note (important):** the mobile source files are being actively edited during this audit — `mobile/src/{content.js,learner.js,egra.js,teacher.js}` all grew between an initial `cat` pass and a follow-up `Read`/Playwright pass (e.g. `learner.js` went 113→141 lines, `egra.js`'s subtask UI changed from a flat grid to Tangerine-style paging). All verdicts below are from the **final Read + live Playwright verification** against `http://localhost:5179/`, not the first-pass reads — several early "ABSENT" findings (placement test, parent report, unit-4 "guess", unit-11 sight-word tell-apart) turned out to be false negatives from a stale read and are corrected here.

---

## Checklist

### Letters, forms, script

| Item | Verdict | Evidence |
|---|---|---|
| 39 letters, name/sound/hint/positional forms | PRESENT | `data/letters.json`; `mobile/src/drills.js:8-19` `letterCard()`; confirmed unit 1/6 screenshots |
| Confusable-letter contrast + "tap what you hear" | PRESENT | `mobile/src/drills.js:24-38` `tellApart()`, pool includes `l.confusable` + prior-taught letters (interleaving per `00_design.md` row 3) |
| Naskh rendering (all units) | PRESENT | live CSS font var `--urdu-naskh`, `body[data-style]` |
| Nastaliq switch + side-by-side Naskh→Nastaliq comparison (unit 11) | PRESENT | `mobile/src/learner.js:103` `unit11()`; confirmed screenshot (`u11_end.png`) |
| Stroke guidance (✎ pen-movement hints) | PRESENT (compressed) | `STROKE` object in `content.js:19`, shown as one muted line per letter card (`drills.js:12`); the course's longer per-letter ✎ prose only survives verbatim in the **teacher print script** (`data/lessons/unit_NN.md`, rendered via `teacher.js:216-229`), not in the learner card |
| Ten non-joiners taught as a rule (unit 4) | PRESENT | `course/unit_04.md`; app: "Guess before you look" discovery card, `learner.js:88`, confirmed screenshot |
| Aspirates (11 pairs) | PRESENT | `data/letters.json.aspirates`; `learner.js:96` `aspirates()`, confirmed screenshot |
| Nūn ghunna | PRESENT | unit 6 letter card + course text; no separate drill beyond tell-apart, matches course |
| Diacritics: zabar/zer/pesh/jazm/tashdīd/khaṛā zabar | PRESENT | `data/letters.json.diacritics` (6 entries); `learner.js:97` `unit0()` |
| Long vowels (9) | PRESENT | `data/letters.json.long_vowels`; `unit0()` |
| Numerals ۰–۹ | PRESENT | `data/letters.json.numerals`; `unit0()` |
| **Punctuation ۔ ، ؟ ؛** | **ABSENT from UI** | Data exists (`data/letters.json.punctuation`, 4 marks) but no `mobile/src/*.js` file references it — not in `unit0()`, not in any unit-10 rendering, not in the web app either (`grep punctuation app/template.html` → nothing). Promised in `course/unit_10.md` focus line and `00_design.md` row 10. |
| **Iẕāfat** | **ABSENT everywhere** | Promised in `course/unit_10.md` focus line and `00_design.md` row 10, but has zero entries in `data/letters.json`, no word/example anywhere in the repo. This is a course-content gap the app faithfully inherited, not an app-only regression. |
| Dictionary order (2nd alphabet chart) | PRESENT | `learner.js:103`; also in `app/template.html:secUnit11` |
| Unified "course order" A–Z / Letter Library reference screen | **REDUCED** | `docs/offline-app-plan.html` §2 promises a "Letter Library" as a home for the full letter set; the app only exposes letters per-unit (Units tab list, `learner.js:84`) or via Review-deck cards — no single all-letters reference view |

### Words, sentences, passages, sight words

| Item | Verdict | Evidence |
|---|---|---|
| Decodable words w/ audio (220, per unit) | PRESENT | `data/units.json` `words[]`; `drills.js` `readIt/dictation/quiz` |
| Sentences w/ audio (33, 3/unit) | PRESENT | `data/units.json` `sentences[]`; `drills.js:readIt` |
| Decodable passages, units 7–11 | PRESENT | `data/units.json` has a `passage` field on units 7,8,9,10,11 (grep confirms 5 passages, not just unit 12); rendered with a live wpm timer via `learner.js:107-109` `read()` + `fluency(u, box, cb, usePassage)`. *(Note: `docs/offline-app-plan.html` §9 describes "decodable passages for units 7–11" as future Phase-3 work — the plan document is stale; the passages already exist and are already wired into the app.)* |
| Sight words (20) | PRESENT | `data/letters.json.sight_words`; `learner.js:103` |
| "Tell the sight words apart" drill (unit 11) | PRESENT | `learner.js:98-102` `sightDrill()`, called from `lesson()` at `:88`; confirmed via Playwright text match (`'Tell the sight words apart'` count=1). Note: this is a **separate function** from the generic `tellApart()`, which is never invoked for unit 11 because `u.letters` is empty there — a first-pass code read that only grepped for "Tell it apart" will wrongly conclude this drill is missing. |
| Repeated reading w/ live wpm | PRESENT | `learner.js:75-82` `fluency()` |
| "Personal best" wpm highlighted | **REDUCED** | `progress()` (`learner.js:111-113`) shows a bar-chart history + latest value, never an explicit best-record label as `docs/offline-app-plan.html`'s "Read" screen description promises |

### Drills, tests, answer keys

| Item | Verdict | Evidence |
|---|---|---|
| Tile word builder (Join it) | PRESENT | `drills.js:41-48` |
| Tracer w/ start-dot, coverage %, stroke-count, RTL check | PRESENT | `drills.js:51-64`; ported near-identically into `app/template.html:secWrite` |
| Dictation w/ scoped letter keyboard | PRESENT | `drills.js:67-77` |
| 10-item unit check, 8/10 to pass | PRESENT | `drills.js:80-88` |
| Drill taxonomy labels (recognition/production/dictation, from course headers) | **REDUCED** | Course markdown tags every section (`· recognition · self-check with audio` etc., see `course/unit_04.md` §3–7); the app UI drops these labels — a teacher can't tell from the screen alone which steps are self-gradable vs which need a helper |
| Placement test (first launch) | PRESENT | `learner.js:54-60` `placement()`; confirmed screenshot ("Take the placement check") |
| Learner self-administered EGRA-style test (5 parts, cwpm, band, comprehension + answer key) | PRESENT | `learner.js:115-126` `selfTest()/test()`; confirmed screenshot showing comprehension + `<details>` answer key |
| Teacher-run EGRA assessment: timers, stop-rule, paging, cwpm/accuracy, PRP band, comprehension w/ answer key shown to teacher | PRESENT — **richer than the course spec** | `mobile/src/egra.js` full file; confirmed live via Playwright (letter-sounds page 1/10, passage subtask, comprehension subtask all rendered with real timers) |
| Answer keys for dictation/unit-check | PRESENT (functional equivalent) | App scores automatically and reveals the correct spelling/word on a miss (`drills.js` dictation/quiz `onclick` handlers) rather than reproducing the static `<details>` key from the .md — a legitimate design substitution, not a gap |
| Per-unit "hours" pacing (child vs adult, `00_design.md` §2 table) | **ABSENT** | Never surfaced to teacher or learner; the teacher's I-do/We-do/You-do script (`teacher.js:172-215`) is a fixed 40 minutes regardless of a unit's design-doc weight (e.g. units 2/6/8 are called out as needing more time) |

### Teacher / parent / device layer (offline-app-plan §3–§6)

| Item | Verdict | Evidence |
|---|---|---|
| Class roster, PIN, instant child switching | PRESENT | `main.js` teacher setup + gate; `teacher.js` Class tab; confirmed screenshot |
| Scripted lesson (I do / we do / you do) + full print script | PRESENT | `teacher.js:172-229`; script pulled live from `data/lessons/unit_NN.md`; confirmed screenshot |
| Groups by band + suggested activity | PRESENT | `teacher.js:232-255` |
| Reports: sortable table, band histogram, CSV/JSON export, parent slip | PRESENT | `teacher.js:298-400` |
| Parent report (single-learner mode) | PRESENT | `learner.js:61-62` `parentReport()`; confirmed screenshot |
| Backup/restore (export/import JSON, cross-phone merge by id) | PRESENT | `main.js:exportBackup`, `db.js:importAll`, `learner.js`/`teacher.js` Reports import |
| Content pack version/manifest w/ per-file hashes | **REDUCED** | `docs/offline-app-plan.html` §6 promises a versioned manifest with hashes; Device tab (`teacher.js:430-433`) only shows raw counts (`N letters · N units · N audio clips`), no version string or hash — two phones can't be confirmed to be on the same content pack |
| Storage estimate / persistence request | PRESENT (estimate only) | `teacher.js:418-429` shows `navigator.storage.estimate()`; no explicit `navigator.storage.persist()` call found in any `mobile/src/*.js` — **REDUCED**, the plan's "request persistent storage after first full download" (`offline-app-plan.html` §6) isn't implemented |

### Accessibility / settings (`offline-app-plan.html` §4 "Learner mode rules")

| Item | Verdict | Evidence |
|---|---|---|
| Track (child/adult/heritage) | PRESENT | `learner.js:129` |
| Script (Naskh/Nastaliq) | PRESENT | `learner.js:130` |
| Vowel marks on/off | PRESENT | `learner.js:131` |
| Text size (3 steps) | PRESENT | `learner.js:132` |
| Letter spacing adjustment | **ABSENT** | Plan promises "text 16–20pt, adjustable letter spacing" — only text size exists, no spacing control |
| Audio-only mode | **ABSENT** | Not in `more()` settings at all |
| Romanisation on/off toggle | **ABSENT** | Plan explicitly lists this as a setting; romanization (`w.rom`) is unconditionally rendered everywhere (`drills.js` readIt/joinIt/dictation) — an adult learner wanting to test themselves without the Roman crutch has no way to hide it |
| Colour-safe (non-colour-only) correct/incorrect feedback | **REDUCED** | `.tile.ok`/`.tile.no` (`mobile/src/style.css:25`) differ only by border/background colour via `color-mix`, no icon/shape redundancy — a WCAG 1.4.1 concern the plan's own accessibility row flags |

---

## Blind A/B: mobile lesson experience vs. `app/template.html`, per step

Walked units 1, 4, 6, 11, 12 in both. The two apps share the *same* drill engine code lineage (`mobile/src/drills.js` is a near-verbatim port of the functions inlined in `app/template.html`'s `<script>`), so per-step mechanics are close to identical:

| Step | Verdict | Note |
|---|---|---|
| 1 Hear it | Tie | Same audio buttons, same letter-card layout |
| 2 See it | Tie | Same `forms()` grid |
| 3 Tell it apart | **Mobile wins** | Web's `secTellApart` is gated by `u.letters.length` and never runs for unit 11 (no letters); web has no equivalent of `sightDrill()`, so a web-app learner gets **no interactive tell-apart practice at all for the 20 sight words** — the single confusable-word skill the course calls out by name (`course/unit_11.md` "Tell the sight words apart"). |
| 4 Join it | Tie | |
| 5 Read it | **Mobile wins, clearly** | Web has no dedicated Read tab, no repeated-reading wpm timer, and no decodable-passage practice at all — `secRead` in `template.html` only lists words + sentences inline, once, with no timer. Mobile's `fluency()` + Read tab deliver the course's explicitly evidence-flagged fluency feature (`00_design.md` row: "one of the best-evidenced fluency features, 16–21 cwpm gains") that the web app never implements. |
| 6 Write it | Tie | Canvas tracer logic is essentially copy-pasted between the two |
| 7 Dictation | Tie | |
| 8 Check | Tie | |
| Reading test (unit 12) | **Mobile wins** | Web's `secTest()` never renders the comprehension **answer key** (`A.answers` is imported but never referenced in `template.html`) — a teacher/parent using the web app has no way to check comprehension answers without the source .md open. Mobile's self-test (`learner.js:126`) shows the answer key in a `<details>`. |

**Overall winner: the mobile app, decisively.** It is a strict superset of `app/template.html`'s content and mechanics, plus the entire teacher/parent/placement/spaced-repetition layer the web app never had (profiles, PIN-gated class roster, Leitner review deck, 10-minute session engine, placement test, parent report, teacher EGRA with real timers and CSV export). The web app is best understood as the single-file reference prototype the drills were ported from, not a competing product — `docs/offline-app-plan.html` and the mobile code comments say this explicitly ("Ported as-is from the current template").

**Single biggest gap, mobile app vs. course + plan:** punctuation (۔ ، ؟ ؛) is fully specified in the data file and named twice in the course text (unit 10 focus line, `00_design.md` row 10) but is never taught, drilled, or even displayed anywhere in either app — a learner can finish all 13 units and never see a full stop or question mark explained.

---

## Prioritised fix list (max 12)

1. **Teach punctuation (۔ ، ؟ ؛).** Data already exists (`data/letters.json.punctuation`); add a small table + example sentences to unit 10's `unit0()`-style block in `learner.js`, matching the pattern already used for numerals/long vowels.
2. **Resolve or drop the iẕāfat promise.** Either add real content (letter/example/word) to `data/letters.json` and unit 10, or remove "iẕāfat" from `course/unit_10.md`'s focus line and `00_design.md` row 10 so the course stops promising a concept it never teaches.
3. **Add a romanisation on/off toggle** in `more()` settings — currently `w.rom` is unconditionally shown everywhere, defeating the adult "read without a crutch" self-test the design doc calls for.
4. **Add an audio-only mode** setting, per `offline-app-plan.html` §4's accessibility row (WCAG 1.4.12) — currently absent from `more()`.
5. **Add a "Letter Library" / full A–Z reference screen** — currently letters are only reachable per-unit or via due review cards; the plan explicitly promises this as a home-screen destination.
6. **Show a content-pack version/hash** on the teacher Device tab (`teacher.js` `renderDevice`), not just raw counts — needed so a teacher can confirm two classroom phones are on the same content pack, per `offline-app-plan.html` §6.
7. **Call `navigator.storage.persist()`** after first full content download (plan §6 explicitly calls this out as "a real risk, not theoretical" on a full 16GB phone) — currently only `estimate()` is used.
8. **Surface drill-type labels** (recognition/production/dictation) somewhere in the lesson UI, so a teacher glancing at the screen (not the .md source) can tell which steps are self-gradable.
9. **Highlight a "personal best" wpm** distinctly in `progress()`, not just the latest value in a bar-chart history.
10. **Add non-colour-only correct/incorrect feedback** (icon or shape, not just border/background colour) to `.tile.ok`/`.tile.no` in `style.css`, per the plan's own colour-safe-feedback rule.
11. **Surface per-unit pacing (hours, child vs adult)** from `00_design.md` §2 somewhere in the teacher Lesson tab, since the current I-do/We-do/You-do script is a flat 40 minutes regardless of a unit's documented weight.
12. **Fix `docs/offline-app-plan.html` §9's stale claim** that decodable passages for units 7–11 are future Phase-3 work — they already exist in `data/units.json` and are already wired into the Read tab; the plan document should be updated so it stops under-selling shipped work (and so a future auditor doesn't waste a pass re-litigating something already done).
