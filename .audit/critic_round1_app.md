# Critic Round 1 — App Audit (`app/index.html` served at :8765)

Method: Playwright/Chromium, real clicks/keyboard/pointer events, JS state inspection
(via `page.evaluate`, never trusted screenshots alone), console/pageerror capture,
1280×900 desktop + 400×800 mobile viewport. Screenshots in `.audit/shots/`. Compared
against `research/00_quality_bar.md` §C (Duolingo Arabic Letters + "Write Urdu
Alphabets" tracing-app functional spec) and §D (Rekhta Aamozish feature list).

---

## BUGS FOUND (with repro)

### 1. CRITICAL — "Tell it apart" drill permanently softlocks in Unit 8 and Unit 9
**File:** `app/template.html` line 158 (`secTellApart`)
```js
choices.innerHTML=''; shuffle(pool.slice(0,6)).forEach(c=>{...});
```
`target` is chosen from the **full** confusable pool (`pool[Math.floor(Math.random()*pool.length)]`,
line 156), but the six tappable answer buttons are always drawn from `pool.slice(0,6)` —
the first six entries of `pool` **in its original construction order**, never shuffled
before the slice. When a unit's confusable pool has more than 6 letters, any round whose
`target` lands in the excluded tail is unanswerable: the correct tile never appears on
screen, so no click can ever satisfy `c===target`, `next()` never fires (it only fires
from inside the correct-answer branch or the "Play sound" button), and the drill sits
forever at the same "Round N/10" with no skip/timeout.

**Live repro (both confirmed via Playwright, clicking every visible choice each round):**
- Unit 8 ("Sounds from Arabic and Persian"): `pool` = `ف ق ک خ ج چ ح غ ع ہ` (10 letters).
  Choices are always `ف ق ک خ ج چ` (first 6). Round 4 draws `ح`/`غ`/`ع`/`ہ` as target →
  **stuck permanently at "Round 4/10 · score 3"**, confirmed by clicking all 6 visible
  tiles with none turning `.ok` across 7 consecutive attempts.
- Unit 9 ("Same sound, different letter"): `pool` has 9 letters (`ص ض س ط ظ ذ د ڈ ز`),
  choices always the first 6 (`ص ض س ط ظ ذ`) → **stuck at "Round 4/10 · score 3"** the
  same way (`د`/`ڈ`/`ز` never offered).
- Roughly 40% of Unit 8 rounds and 33% of Unit 9 rounds are mathematically unwinnable.
  These are exactly the two units flagged by Alif Baa's own Teacher's Guide as needing
  the *most* time because of heavy letter confusability — the drill breaks precisely
  where the quality bar says it matters most.
- **Fix:** shuffle `pool` once before slicing 6 for the *choice* set, or — better, since
  `target` must always be one of the displayed choices — pick `target` from the already-
  sliced/shuffled 6-item choice set instead of the full pool, e.g. compute the 6 choices
  first (`const opts = shuffle(pool).slice(0,6)`), then set `target = opts[...]`.

### 2. Unit 0 states a wrong letter count for its own dynamically-rendered list
**File:** `app/template.html` lines 228–233 (`secUnit0`)
```js
const nj=L.filter(l=>!l.joiner).map(l=>l.ch).join(' ');
...
<li><b>Letters join like cursive.</b> ... Ten letters never join to the letter
after them: <span class="ur">${nj}</span>. ...</li>
```
`nj` is computed live from the letter data and actually renders **12** characters
(`ا ے و ر د ں ڈ ڑ ز ژ ذ ء` — confirmed via `page.evaluate`), but the surrounding
copy hardcodes "Ten letters." Two real non-joiners — `ر` (re) and `ز` (ze) — are
present in the rendered glyph list but excluded from the stated count. This is the
learner's very first factual claim in the whole course, on the page literally titled
"Five things to know before letter one," and it's wrong on inspection (a learner who
counts along, which the design invites, gets a different number than the text says).
**Fix:** either change "Ten" → "12" (or "these") in the copy, or keep "ten" but define
`nj` from a curated list that matches — the dynamic/hardcoded values must be the same
source of truth.

### 3. No deep-linking / no browser back-forward inside the course
Grepped `app/template.html` for `hashchange`, `location.hash`, `history.pushState` —
zero matches. Current unit lives only in a JS closure variable (`cur`) + `localStorage`
(`store.set('unit',cur)`); confirmed via Playwright that setting `location.hash`
manually does nothing (`render()` is only ever called from nav-button `onclick`).
Reload correctly restores the last-viewed unit from `localStorage`, but there is no
shareable/bookmarkable URL for a specific unit, and pressing the phone/browser back
button does not step back inside the course — it leaves the page entirely.
**Impact:** fails Aamozish's explicitly-advertised "bookmark pages for future
reference" bar outright (§D checklist item 2) — there is nothing to bookmark *to*.

### 4. Mobile unit nav is a blind horizontal-scroll strip
**File:** `app/template.html` line 25:
```css
@media (max-width:760px){nav{... flex-direction:row;overflow-x:auto ...}}
```
At 400×800 viewport, only "0 / 1 / 2" (partially) are visible with **no edge fade,
arrow, or dot indicator** signalling that units 3–12 exist off-screen (see
`.audit/shots/mobile_nav_zoom.png`). A first-time phone user has no visual cue a
13-unit course is longer than 3 items.
**Fix:** `mask-image: linear-gradient(to right, black calc(100% - 24px), transparent)`
on `#nav` at the mobile breakpoint (cheap, no JS), or add a small "3 more →" affordance.

### 5. Tracing drill gives end-state-only pixel coverage — no stroke order/direction check
**File:** `app/template.html` lines 190–196 (`secWrite`). `check.onclick` compares
final canvas pixels against a static gray reference glyph and reports `Coverage N%`.
Verified live: drawing an aimless horizontal squiggle instead of alif's vertical
stroke correctly scored **"Coverage 0%"** (so the overlap metric itself is real, not
a rubber stamp) — but the same algorithm would score **100%** for a correct-shaped
stroke traced bottom-to-top or right-to-left, i.e. backwards from real Urdu
penmanship. There is no start-point marker, no direction arrow, no stroke-count
guide, and no per-stroke feedback — this is exactly the gap the quality bar's
interactive-tracing checklist calls out by name ("shows a directional stroke guide...
and gives per-stroke feedback, not just end-state pass/fail," §C checklist).
**Fix:** at minimum, record the pointer path's start point and general bearing and
penalize scores where the stroke starts from the wrong end (cheap check: compare
`ctx.beginPath` coordinates against a per-letter authored start-point in the data,
rather than only diffing the final raster).

### 6. No ARIA state on nav buttons, canvas, or play buttons
`renderNav()` (line 117) signals "current / done / locked" purely via CSS class
(`done`, `cur`, `locked`) — confirmed via `page.evaluate` that no nav `<button>` ever
gets `aria-current`, `aria-pressed`, or `aria-disabled`. The tracing `<canvas>` has no
`role`/`aria-label` at all (confirmed: `getAttribute('role')` → `null`). Play buttons
only carry `title="Play"`, not `aria-label` (titles aren't reliably announced by all
screen readers, especially on touch). None of this is a hard blocker for a sighted/
mouse user (confirmed `button:focus-visible{outline:3px solid var(--accent)}` at
line 20 *is* correctly implemented and works — verified via real Tab-key traversal),
but a screen-reader user gets zero non-visual signal for which unit is current/locked/
passed, and nothing at all from the tracing exercise.
**Fix:** `aria-current="page"` on the active nav button, `aria-disabled="true"` +
`aria-label="Unit N locked"` on locked ones, `role="img" aria-label="trace the letter
ا"` (updated per selection) on the canvas.

---

## Per-component verdicts (blind comparison vs. §C/§D functional specs)

| Component | Verdict | Biggest remaining gap | Concrete fix |
|---|---|---|---|
| **Letter-intro card** | Ahead of both references on content density (IPA + English sound-alike cue + confusable cross-refs + full positional table with explicit "(none)" for non-existent forms — better than Delacy's "fake 4-form table" pitfall) | No stroke-order diagram lives *on the intro card itself* (Alif Baa: calligrapher video; Delacy: numbered stroke diagrams right there in the letter unit) — it's deferred entirely to the separate Write It section, which itself has no stroke guidance (bug 5) | Add a tiny static numbered-arrow SVG per letter next to the "forms" row in `formsHTML()` (~line 128) |
| **Sound→letter matching ("Tell it apart")** | Meets Duolingo's functional spec (N choices, 1 audio prompt, tap-to-match) when it works, and *does* re-surface earlier letters when they're a `confusable` of a new letter (good — satisfies the "letters recur" checklist item) | (a) Critical: unwinnable rounds in units 8–9 (bug 1); (b) letters with an empty `confusable` array (e.g. `م` mīm) never reappear in this drill again after their own unit passes — recognition-recency isn't tested for ~half the alphabet | Fix bug 1; separately, once every few rounds in later units pull a random letter from *all* `taughtBefore()`, not only the confusable-linked subset |
| **Word-building ("Join it")** | Genuinely correct RTL behavior — verified live: clicking tiles in the word's logical order (`ب ا ب ا` for bābā) builds `target.textContent` by concatenation and the browser renders it right-to-left correctly (`direction:rtl; text-align:right`, confirmed via computed style) | Two identical-looking tiles for a repeated letter (two `ب`, two `ا` for bābā) are visually indistinguishable — no positional hint which is "next" (wrong guesses are free/no-penalty though, so this is friction, not a dead end) | Not worth over-engineering — the current low-stakes retry design is defensible; if changed, use tiny subscript numbers on repeated-glyph tiles |
| **Tracing** | Real (non-fake) pixel-coverage scoring, correctly distinguishes a real trace from a random scribble | No stroke-order/direction check at all (bug 5) — biggest gap vs the "Write Urdu Alphabets" app-bar reference, which shows a directional stroke guide | See bug 5 fix |
| **Dictation** | Fully functional and correctly scored — verified live end-to-end: `Play word` → type via on-screen keys restricted to unit-taught letters (`taughtBefore(u.n) ∪ u.letters`, correctly scoped) → `Check` → score increments → advances to next word after 900ms | None found in this component specifically | — |
| **Assessment ("Check" quiz)** | 10-question MC quiz, 8/10 to pass, writes `progress[u.n].passed` to localStorage and unlocks the next unit — matches the "inline quiz + resumable progress" bar from Aamozish's landing page | Progress is only in `localStorage`, not a real per-unit "Summary" (Alif Baa) or printable answer key (Delacy) — no way to review *which* 2 you missed after submitting, only an aggregate score | Track wrong `qi` indices in `submit.onclick` (line 226) and list them under the score line |
| **Script switching (Naskh↔Nastaliq)** | Verified visually at large size: Nastaliq renders with correct diagonal stacking, dot placement, and final-ye dip below the baseline (`.audit/shots/unit1_nastaliq_novowels.png`); Unit 11's dedicated Naskh→Nastaliq comparison rows (`کتاب`/`کتاب`, `پڑھنا`/`پڑھنا`, etc.) are a genuinely strong feature neither reference book has as an interactive toggle | None found — this is a strength | — |
| **Vowel-mark toggle** | Works correctly — unchecking `#marks` (confirmed via `document.getElementById('marks').checked` and `showMarks()`) strips diacritics from word lists app-wide, consistent with the stated design ("marks stay on until unit 11 on purpose") | None found | — |
| **RTL correctness (general)** | Positional-forms tables read correctly right-to-left (isolated → initial → medial → final, mirroring real word order); non-joiners (`ا د ڈ ذ ر ڑ ز ژ و ے` plus `ں`/`ء`, correctly extended beyond the task's 10-item list — see bug 2) show only isolated+final with explicit "(none)" placeholders, never a faked 4-form table; word-building target renders with correct `direction:rtl` | The *stated* non-joiner count (bug 2) contradicts the actually-correct data | Fix bug 2 |
| **Mobile usability** | No horizontal page overflow anywhere (`scrollWidth - clientWidth === 0` on every unit tested, 0/1/2/6/11/12); settings row (Track/Script/vowel-marks/Reset) reflows cleanly to full-width controls | Unit nav is a blind horizontal-scroll strip with no affordance (bug 4) | See bug 4 fix |
| **Accessibility** | `:focus-visible` outline correctly implemented and verified via real keyboard Tab traversal (3px accent outline, offset 2px) | No ARIA state anywhere (bug 6); tracing canvas has zero accessible fallback | See bug 6 fix |
| **Console/runtime errors** | Zero `pageerror`s across every interaction tested (nav, all 8 unit-1 drills, script/vowel toggles, tracing, mobile) | Two recurring benign `Canvas2D: ...willReadFrequently` perf warnings from `getImageData()` calls in `secWrite` | Pass `{willReadFrequently:true}` to `cv.getContext('2d')` at line 189 |

---

## Prioritised fix list (max 12, most damaging first)

1. **Fix the Unit 8/Unit 9 "Tell it apart" softlock** — `pool.slice(0,6)` vs full-pool
   `target` mismatch, `template.html:158`. Blocks course completion outright. (bug 1)
2. **Correct or dynamically generate the "Ten letters" claim in Unit 0** —
   `template.html:233`, actual rendered count is 12. (bug 2)
3. **Add a stroke-direction/start-point check to the tracing drill**, or at minimum
   stop presenting a pixel-coverage-only score as a proxy for "traced correctly" —
   `template.html:190-196`. (bug 5)
4. **Add ARIA state to nav buttons and the tracing canvas** — `renderNav()` line 117,
   `secWrite()` line 184. (bug 6)
5. **Give the mobile unit-nav a scroll affordance** (edge fade / arrow / dot) —
   `template.html:25`. (bug 4)
6. **Broaden "Tell it apart" recall pool in later units** to include non-confusable
   letters periodically, not only `confusable`-linked ones, so recognition of
   letters like `م` (no confusables) is retested over time, matching the Duolingo
   spec's "letters recur" bar. (`secTellApart`, `template.html:149-163`)
7. **Add per-letter stroke-order guidance to the letter-intro card**, not just the
   separate Write It section — closes the single biggest gap vs Alif Baa/Delacy on
   the intro-card component. (`formsHTML()`, `template.html:128`)
8. **Add deep-linking (URL hash) for the current unit** so a unit can be bookmarked/
   shared, closing the gap against Aamozish's advertised bookmarking feature.
   (no existing routing code to build on — net-new)
9. **Surface which quiz questions were missed after "Check" submission**, not just
   the aggregate score, closer to Alif Baa's per-unit Summary / Delacy's answer key.
   (`secQuiz()`, `template.html:217-227`)
10. **Add `aria-label` to play buttons** in addition to `title` for reliable
    screen-reader announcement. (`playBtn()`, `template.html:116`)
11. **Pass `{willReadFrequently:true}` to the tracing canvas's 2D context** to clear
    the recurring console perf warning. (`template.html:189`)
12. **Remove or use the dead `.pill.warn` CSS rule** (`template.html:74`) — defined,
    styled, contrast-checked at 3.64:1 (would fail WCAG AA if ever shown), but never
    referenced by any JS `classList.add`/template string — harmless but worth a
    cleanup pass since it's a landmine for whoever wires up a future warning state.
