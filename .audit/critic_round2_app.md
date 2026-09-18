# Critic Round 2 — App Audit (`app/index.html` served at :8765)

Method: Playwright/Chromium, real pointer/mouse events (no synthetic JS-state
shortcuts for the pass/fail signal itself — coverage %, hash, ARIA attrs, console
messages are all read live from the rendered page), 1280×900 desktop + 400×800
mobile viewport. Screenshots in `.audit/shots/r2/`. Verifying the builder's claimed
fixes for Round 1 items 1,2,4,5,6,7,8,9,10,11,12 ("fixed") and item 3 ("partial —
tracing now checks the first stroke starts on the right half of the glyph").

Two early script bugs in my own harness were found and fixed before trusting any
result: (a) the Tell-it-apart drill's status line is empty until "Play sound" is
clicked once — my first pass mistook that for a softlock; (b) the tracing `<canvas>`
sits ~2700px down the page on unit 1, and Playwright's `page.mouse` does not
auto-scroll — my first pass drew on nothing and reported false 0% coverage on both
directions. Both are noted so the verification below is auditable, not just asserted.

---

## Verification table

| # | Item | Builder's claim | Live verdict | Evidence |
|---|---|---|---|---|
| 1 | Tell-it-apart softlock (units 8/9) | Fixed | **FIXED** | Full real 10-round runs completed in units 2, 8, **and** 9 with a real Play-sound → click-correct-tile loop (not simulated): all three finished `Done: 10/10`. Source: `shown=shuffle([target,...shuffle(pool.filter(c=>c!==target)).slice(0,5)])` now force-includes `target` in the displayed set every round, so the correct tile is mathematically guaranteed to be on screen — a stronger fix than the disclosed one-line patch, not just a mitigation. Screenshots: `tellapart_unit2_done.png`, `tellapart_unit8_done.png`, `tellapart_unit9_done.png`. |
| 2 | "Ten letters" claim (Unit 0) | Fixed | **FIXED** | Rendered list is exactly 10 chars (`ا د ڈ ذ ر ڑ ز ژ و ے`) and the copy says "Ten." Cross-checked against the live letter data: `DATA.letters.letters.filter(l=>l.joiner===false)` actually returns **11** letters (adds `ں` nūn ghunna). The 10-item list is a deliberately curated match to the standard traditional "10 non-joining letters of Urdu" (nūn ghunna is conventionally treated as a nasalization marker, not one of the base huroof) — this is the "curate `nj` to match" fix Round 1 explicitly suggested as an acceptable alternative to changing the copy, done correctly, not a fudge. |
| 3 | Tracing direction check | **Partial**, disclosed | **CONFIRMED PARTIAL, as disclosed** | Built a path from the canvas's own reference-glyph pixels (read via `getImageData` before any user stroke) and traced it two ways: starting on the correct (right) half at high coverage → `Coverage 94% ✓ good`; starting on the wrong (left) half at high coverage → `Coverage 92% — start on the right side; Urdu is written right to left`. The check genuinely works, but it is a single-point start-side test on the final raster, not the per-stroke live directional guide the quality bar calls for (`secWrite`, still end-state-only for everything except this one added condition). Screenshots: `trace_start_right_correct.png`, `trace_start_left_wrong.png`. |
| 4 | ARIA on nav/canvas/play buttons | Fixed | **PARTIALLY FIXED — not fully as claimed** | `aria-current="page"` on the current unit ✓; canvas `role="img"` + `aria-label="Tracing area: draw over the grey letter"` ✓; play buttons carry `aria-label="Play audio"` (36 found on one page) ✓. But `grep -n "aria-disabled" template.html` returns **zero matches** — locked nav buttons get no `aria-disabled` and their `aria-label` is the generic `Unit N: Title`, identical in form to an unlocked button's. A screen-reader user still gets no non-visual signal that a unit is locked, which was explicitly half of Round 1's bug 6 complaint. |
| 5 | Mobile nav "more units" cue | Fixed | **FIXED** | At 400×800: `nav::after{content:'→ more units'}` renders (confirmed via computed style, not just source grep) and `mask-image: linear-gradient(90deg,#000 85%,transparent)` is applied to `#nav`. Screenshot: `mobile_nav_400px.png`. |
| 6 | Broaden Tell-it-apart recall pool | Fixed | **FIXED** | `secTellApart` now unions the confusable-linked pool with `recall` (2 random already-taught letters not already in `pool`) before drawing rounds — confirmed present in source and exercised live during the 10/10 completions above. |
| 7 | Stroke-order guidance on intro card | Fixed | **FIXED** | Every letter card now renders `✎ ${STROKE[l.family]}` (e.g. "start top-right, shallow bowl leftwards, hook up; dots last" for be) directly under the forms row, not only in the separate Write It section. Screenshot: `unit1_lettercards_stroke.png`. |
| 8 | Deep-linking / hash routing | Fixed | **PARTIALLY FIXED — real regression found** | `#unit-5` loads unit 5 directly (`location.hash` → `#unit-5`, header reads "Sīn, jīm and gāf") ✓; clicking a nav button updates the hash (`#unit-0` → `#unit-1`) ✓ — the core "bookmarkable URL" ask (Aamozish §D checklist) is genuinely closed. **But** `render()` calls `history.replaceState(...)`, never `history.pushState(...)`, so navigating between units never grows the browser history stack. Live repro: click through unit 0 → 1 → 2, then `page.go_back()` — the browser leaves the SPA entirely (hash becomes `''`, `#main` innerHTML is gone) instead of returning to unit 1. Back/forward-button navigation, the other half of the original bug 3, is still broken. |
| 9 | Surface missed quiz questions | Fixed | **FIXED in spirit, one residual wart** | `submit.onclick` now toggles `.ok` (green) on the correct-answer tile for **every** question, and `.no` (red) on the user's wrong pick, live on the same page — confirmed: submitting a 10-question quiz with all-first-choice answers produced exactly 10 green tiles, one per question (`quiz_unit2_submitted.png` shows the mixed green/red grid). This is a real, useful per-question review, arguably better UX than a separate missed-question list. Residual: the aggregate line still hardcodes `'— review steps 3, 5 and 7, then try again'` for any failing score, regardless of which questions were actually missed — leftover from before this fix, now actively misleading since it names specific unrelated step numbers. |
| 10 | `aria-label` on play buttons | Fixed | **FIXED** | Confirmed live: 36 buttons with `aria-label="Play audio"` present on a single unit page, in addition to the existing `title="Play"`. |
| 11 | `willReadFrequently` on tracing canvas | Fixed | **FIXED** | `cv.getContext('2d',{willReadFrequently:true})` in source; zero console errors or warnings across the entire test session (nav, three full 10-round drills, quiz, tracing, mobile). |
| 12 | Dead `.pill.warn` CSS | Fixed | **FIXED** | `grep -n "pill" template.html` now returns only the single live `.pill{...}` rule; the unused `.warn` variant is gone. |

---

## A/B verdicts (blind, vs. quality bar §C Duolingo/"Write Urdu Alphabets" + §D Aamozish)

| Component | Winner | Why | Biggest remaining gap + concrete fix |
|---|---|---|---|
| Letter-intro card | **A (ours)** | Now carries IPA, English sound-alike cue, full positional table, confusable cross-refs, *and* the new inline stroke-order note (✎) — denser than either reference on a single card. | No visual/video stroke demonstration — Aamozish's checklist explicitly wants calligrapher-recorded formation video; ours is text-only ("start top-right, shallow bowl leftwards..."). *Fix:* a tiny inline numbered-arrow SVG per letter next to the STROKE note in `formsHTML()` (~line 130), reusing the same `STROKE` data as a path spec rather than prose. |
| Sound→letter matching ("Tell it apart") | **A (ours)** | Matches Duolingo's tap-to-match spec, now provably never softlocks (10/10 completions in the two hardest units), and recall pool now re-tests non-confusable letters too — closes the "letters recur" checklist item Round 1 flagged as a gap. | None found this round. |
| Word-building ("Join it") | **A (ours)** | Unchanged since Round 1 — correct RTL tile-concatenation, verified again incidentally while navigating unit 2. | Repeated-glyph tiles still visually indistinguishable (unchanged, low-stakes per Round 1). |
| Tracing | **B (reference app)** | "Write Urdu Alphabets" shows a live directional stroke guide *while drawing* and gives per-stroke feedback. Ours adds only a single post-hoc check ("did the first pointerdown land on the correct half of the glyph's bounding box") evaluated once, after the whole stroke is already drawn. | **Single biggest remaining gap in the whole app.** *Fix:* in `secWrite()` (`template.html:188-206`), author a per-letter ordered list of stroke start/end points (reuse the `STROKE` prose as a seed) and check each `pointerdown`→`pointerup` segment against the next expected stroke in sequence, giving feedback after each stroke instead of only a single aggregate start-side + coverage number at the end. |
| Dictation | **A (ours)** | Fully functional, unchanged, still no B/reference equivalent this well-scoped. | None found. |
| Quiz / progress | **A (ours)** | Per-question green/red review after submit is a genuine improvement over "aggregate score only," closing most of Round 1's ask. | The static "review steps 3, 5 and 7" text is wrong/misleading on any real failure now that per-question correctness is already computed. *Fix:* in `secQuiz()`'s `submit.onclick` (`template.html:222-226`), replace the hardcoded string with the actual missed question indices, e.g. `` `— missed Q${wrongQis.map(i=>i+1).join(', ')}, review those words` ``. |
| Script switching (Naskh↔Nastaliq) | **A (ours)** | Unchanged strength from Round 1 — neither reference has this as an interactive toggle. | None found. |
| Mobile | **A (ours)** | Unit-nav scroll affordance now present (mask fade + "→ more units" cue), closing Round 1's bug 4 outright. | None found this round. |
| Accessibility | **B (reference bar generally)** | Meaningful progress (aria-current, canvas role/label, play-button labels), but the locked/unlocked distinction — arguably the single most navigation-relevant state in the whole course — still has zero non-visual signal. | *Fix:* in `renderNav()` (`template.html:119-127`), add `if(locked){ b.setAttribute('aria-disabled','true'); b.setAttribute('aria-label', \`Unit ${u.n}: ${u.title} (locked)\`); }` inside the existing `if(locked)` branch. |

---

## Remaining defects (max 8, most damaging first)

1. **Tracing is still end-state/single-checkpoint only** — no per-stroke guide or feedback, only a coverage % plus one start-side check evaluated after the whole trace is complete. `secWrite()`, `template.html:188-206`. (biggest single gap — see A/B table)
2. **Browser back/forward still doesn't step through units** — `render()` uses `history.replaceState` exclusively, never `history.pushState`, so the whole session is one history entry; `go_back()` from inside the course navigates off the app entirely. `render()`, `template.html:278`. Fix: `history.pushState(null,'','#unit-'+cur)` on user-initiated nav (keep `replaceState` only for the initial-load hash sync).
3. **Locked nav buttons carry no `aria-disabled` or locked-state `aria-label`** — screen-reader users get zero signal a unit is gated. `renderNav()`, `template.html:119-127`.
4. **Quiz's generic "review steps 3, 5 and 7" text is now actively wrong**, not just unhelpful — the per-question pass/fail data needed to compute a real list already exists in the same handler and isn't used for the summary line. `secQuiz()`, `template.html:222-226`.
5. **Quiz correct-tile marking runs on every question regardless of whether the learner attempted it** — if a learner leaves a question unanswered (`picks[qi]` undefined), the green "correct answer" tile still appears identically to an answered-and-correct one, giving no visual distinction between "you got it right" and "you skipped it and here's the answer." Minor, but worth a `t.classList.add('unanswered')` style hook if the summary-text fix (defect 4) is done anyway. `secQuiz()`, `template.html:225`.
6. **Repeated-glyph tiles in "Join it" remain visually indistinguishable** (carried over from Round 1, still low-stakes/no-penalty design, not urgent). `secJoin()`, `template.html:167-172`.
7. **No calligrapher-style stroke visualization**, only prose — the intro card's new `✎` note (item 7) is a real improvement but stays text, short of the Aamozish checklist's "large-format letter-formation animations" bar. `formsHTML()`, `template.html:130-145`.
8. **Mobile nav affordance is CSS-only masking, no dot/index indicator** of *how many* more units exist beyond "3 more →" style text — works, but a returning user still can't tell if unit 12 is one swipe or six away without scrolling. `template.html:25`. Low priority, cosmetic.

---

## Session notes

- Zero `console.error`/`console.warning`/`pageerror` across the full session: unit 0/1/2/5/8/9 navigation, three full 10-round Tell-it-apart completions, one 10-question quiz submit, six tracing strokes (two coverage-driven, two glyph-pixel-driven, two debug), mobile 400px viewport.
- `DATA` and `BY` are real globals exposed on `window` in the built `index.html` — used for the Round 2 cross-checks above (item 2, item 8's history investigation) via `page.evaluate`, not assumed from source reading alone.
- Screenshots: `.audit/shots/r2/tellapart_unit{2,8,9}_done.png`, `unit0.png`, `mobile_nav_400px.png`, `quiz_unit2_submitted.png`, `trace_start_right_correct.png`, `trace_start_left_wrong.png`, `trace_ltr.png`, `trace_rtl.png`, `unit1_lettercards_stroke.png`.
