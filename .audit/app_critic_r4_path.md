# App Critic Round 4 — Duolingo-style Learner Path (Unit 0 + Unit 1)

**Scope:** `mobile/src/path.js` (+ `drills.js`, `learner.js`), web build at `http://localhost:5179/`.
**Method:** Playwright (python sync, chromium 390×800), audio interception via
`HTMLMediaElement.prototype.play` monkeypatch mapped through
`mobile/public/data/audio_index.json`, tile clicks via `page.evaluate('e=>e.click()', handle)`
to avoid the fixed bottom nav intercepting taps. Created a child-track learner ("Zoya"),
completed Unit 0 (3 lessons) and Unit 1 completely (6 letter lessons, Join, Blend, Words 1,
Words 2, Read, Unit check — 12 lessons total), confirmed Unit 2 unlocked. Script:
`/tmp/.../scratchpad/audit_run.py` (ephemeral, not part of the repo). Screenshots referenced
below are in the harness scratchpad, not committed to this repo.

Bar: research/00_quality_bar.md §C (Duolingo Arabic Letters + a real tracing app) and §D
(Aamozish), plus research/11_letter_lesson_flow.md's own synthesized recommendation and
research/12_child_ux.md's child-UX checklist.

---

## Run result

Full walkthrough succeeded on the second corrected pass: Unit 0 (Five rules → Vowel marks →
Finish unit) then Unit 1's all 12 lessons (alif, be, kāf, lām, mīm, nūn, Join them, Blend,
Words 1, Words 2, Read, Unit check). Unit check quiz scored 10/10 and Unit 2 ("Dots and the
two ye") visibly unlocked in the path (screenshot `03_unit1_done.png`: Unit 1 card shows
"✓ passed" on all 12 bubbles, Unit 2 card renders its letter bubbles instead of the
"🔒 finish unit 1" lock text).

---

## 1–10: Per-component A/B judgment

Reference bar = Duolingo Arabic "Letters" (interactive pattern) + Noorani Qaida's staged
progression + Alif Baa's per-letter-forms model, as documented in research/00 §C/D and
research/11.

| # | Component | Verdict | Why |
|---|---|---|---|
| 1 | Path screen clarity (6yo) | **A (ours)** | Mirrors Duolingo's actual 2022 path redesign closely (linear bubble row, done/current/locked states, single big CTA, pill for passed units) — the exact pattern research/11 Part 2 documents as *the* model for children. Icons + short labels, ≤5 choices visible per screen. Deduction: every label is English text (see §12). |
| 2 | Per-letter lesson sequence | **A (ours)** | Implements research/11 §2's own synthesized 7-step recommendation almost verbatim (sound intro → tap-the-sound → position-in-word → trace → blend → quick check). Neither Duolingo (exact sequence unconfirmed, UNVERIFIED per research/11) nor Qaida (defers positional forms/vowels to separate whole-alphabet lessons) matches this coherence. |
| 3 | "Where it sits in a word" screen | **A (ours)** | Real word per position, highlighted target letter, audio per row — matches Alif Baa's "all forms up front" approach (ref A in quality bar). Minor deduction: position labels ("isolated/initial/medial/final") and the explanatory sentence are English-only. |
| 4 | Tracing screen | **Mixed, slight edge to reference** | Has a start dot + "body first, dots last" guidance (partial match to Alif Baa's arrows), but it's a single freehand pass with **no animated stroke-path demo** (research/12's explicit ask) and, more importantly, the trace-check result **never gates progress** — `path.js`'s screen 4 appends `cont('Traced it')` unconditionally alongside the drill (`mobile/src/path.js:81`), so a child can tap Continue without tracing anything at all. Neither Duolingo (no handwriting feature at all, per quality-bar §C) nor our tracing screen has the "dots → guided → independent" 3-stage scaffold research/12 recommends. |
| 5 | Blend screen | **A (ours)** | Audio-first, retry-until-correct, matches Duolingo's confirmed "match sound to shape" exercise type. Well executed both at letter-level (3 rounds) and unit-level (6 rounds). |
| 6 | Quick check + 75% gate | **Mixed** | Gate logic itself (≥3/4, loop back to the lesson if not) is correctly wired and verified live. But **for the very first letter taught in the whole course (alif), the check is trivial** — see Bug #2: with only one letter "known" so far, all three question kinds render with a single, un-missable tile. Every subsequent letter (pool≥2) works as intended. |
| 7 | Join/Blend unit lessons | **A (ours)** | Deliberately scoped to only the unit's own letters (not all 29 at once, unlike Qaida) — verified working correctly at full-unit scope with no indexing issues. |
| 8 | Word lessons (Words 1/2) | **Mixed** | Read → build-from-tiles → dictate progression matches Alif Baa's documented exercise variety (quality-bar doc A: "letter connection, reading, dictation, sound discrimination"). But **Words 2 plays the wrong audio for every word** — Bug #3, a real regression a listening child would notice even if they can't articulate why. |
| 9 | Unit check gate | **A (ours)** | Matches Duolingo's checkpoint concept and Qaida's mastery-gating norm; verified live end-to-end (10/10 → Unit 2 unlocked). |
| 10 | Feedback on wrong answers | **A (ours), by design; partially undermined in execution** | `body[data-track="child"]` CSS (`mobile/src/style.css:56-57`) removes the red ✗ glyph, swaps the wrong-answer color from `--bad` (red) to `--warn` (amber), and adds a `wobble` shake animation — this is a precise, deliberate implementation of research/12's "no red X, soft bounce" rule, better than anything confirmed for Duolingo or Qaida in the quality bar docs. Execution flaw: Bug #4 (stale toast bleed-through) can visually collide the feedback toast with the next screen's primary CTA button. |

**Tally (items 1–10):** 6 clear wins for ours (1, 2, 3, 5, 7, 9), 4 mixed/partial (4, 6, 8, 10 —
all still net-positive for ours on design intent, each marred by one concrete, fixable bug),
**0 clear wins for the reference bar.**

---

## 11. Lesson length (timed)

Bot-driven (near-instant clicking, ~150–500ms waits) completion times, `timings.json`:

| Lesson | Bot time |
|---|---|
| Five rules (4 screens) | 2.1s |
| Vowel marks | 0.9s |
| Finish unit | 1.5s |
| alif (6 screens, no blend — vowel-carrier) | 10.2s |
| be / kāf / lām / mīm / nūn (7 screens incl. blend) | ~13.1s each |
| Join them | 4.5s |
| Blend (unit) | 5.9s |
| Words 1 | 8.5s |
| Words 2 | 8.2s |
| Read | 0.9s |
| Unit check (10-question quiz) | 2.8s |

These are **not** representative of a real child's pace (the bot skips think-time and only
half-listens to audio). Extrapolating with research/11's own "~20–30s/screen" assumption and
audio-clip durations (~1.5–2.5s each, several plays per screen):

- **Single letter lesson (6–7 screens):** roughly 2.5–4 minutes for a real child — **within**
  the 3–5 min target, consistent with research/11 §2's own length check ("7 screens × 20–30s
  ≈ 3–4 min").
- **Join them / Blend (unit-level):** roughly 1.5–3 minutes each — within target.
- **Words 1 / Words 2:** each bundles read (10 words) + build-3-words + dictate-5-words in one
  path node. Realistically 3–6 minutes per node — **at or over** the 3–5 min "one small lesson"
  framing the app's own subtitle promises.
- **Unit check (10 MC questions, each requiring reading a romanization + English gloss and
  discriminating among up to 4 visually similar words):** realistically 3–5+ minutes by
  itself — this single path node is likely the **longest** "lesson" in the whole unit, which
  cuts against the "one small lesson at a time" pitch shown directly under the child's name on
  the Learn tab.

**Finding:** most individual letter lessons hit the 3–5 min target well; the two Words nodes
and the Unit check node are the ones most likely to run long for a real 5–7-year-old.

---

## 12. What a child cannot do without reading English

The app has **zero narrated/audio instructions** — confirmed by inspecting
`mobile/public/data/audio_index.json` (474 clips across 9 prefixes:
`names, words, syllables, units, sentences, sight, diacritics, aspirates, numerals` — no
`instructions`/`ui` category exists). Every instruction, label, and prompt below is
English-only text with no voice-over, contradicting research/12's own rule #5 ("Voice
guidance for pre-literate children ages 3-6: replace written instructions with
character-driven narration").

A pre-literate or non-English-reading child cannot, without an adult reading for them:

- **Path/Today screen:** "Good [morning/evening], {name}", "Unit N · {title} · one small
  lesson at a time", every lesson-bubble label ("Five rules", "Vowel marks", "Finish unit",
  every letter's Latin transliteration name like "alif"/"be"/"kāf", "Join them", "Blend",
  "Words 1", "Words 2", "Read", "Unit check"), the "Start: X" / "Continue: X" button, the
  "🔒 finish unit N" lock message, bottom-nav labels ("Learn", "Units", "Review", "Read",
  "Progress", "More").
- **Sound intro screen:** the letter's name, its IPA string, a full English hint sentence
  (e.g. "'a' in father when long; a silent seat for short vowels…"), "Say it again", the
  romanized example word + English gloss, "I heard it".
- **Tap-the-sound screen:** "Listen, then tap the letter you hear.", "Tap what you hear",
  "Play sound"/"Play again", "Continue".
- **Where-it-sits-in-a-word screen:** the explanatory sentence ("It never joins the next
  letter…"), position labels ("isolated/initial/medial/final"), "I see it".
- **Trace screen:** the stroke-hint sentence (shown twice, once above the card and once
  inside it), "Start at the green dot. Body first, dots last.", form/letter dropdown labels,
  "Check", "Clear", "Traced it".
- **Blend screens (letter- and unit-level):** the instruction sentence, "Play again",
  "Continue".
- **Quick check:** "Four questions on X.", "Question N/4", all three question prompts
  ("Tap the letter you hear", "Tap {name}", "Which is {name} at the {position} position?"),
  "Not yet solid. Go through the lesson once more.", "Do the lesson again", "Finish".
- **Join them / Build the word:** "Tap the letters in reading order, right to left.",
  "Make: {rom} — {en}", "Next word".
- **Words 1/2 Read screen:** "Read aloud, then tap to listen."
- **Dictation:** "Hear a word, spell it with the tiles.", "Play word", "Check", "Skip",
  "Word N/5 · X right", toast hints ("N letters in this word", "Not yet. Listen again.").
- **Read lesson:** "Read it twice", the passage's English translation caption.
- **Unit check:** "Score 8 of 10 to pass this unit.", every question ("Which one says {rom}
  ({en})?"), "Submit", the result line ("re-read …, then try again" / "passed ✓").
- **Lesson finisher:** "{title} done", "Next: {title}" / "Back to path".

Net effect: a **pre-reading child cannot navigate the path, start a lesson, or understand what
any given screen is asking them to do without an adult (or older sibling) reading every label
aloud** — the actual Urdu *content* (letters, words, sentences) is fully voiced, but the app's
own UI chrome and pedagogy is not, which is a real gap against research/12 in a course whose
target learner is, per the task itself, a 6-year-old.

---

## Bugs found (with repro + file:line)

### Bug 1 — [HIGH] "Back to path" / ✕ reopens the FIRST lesson of the unit instead of the path screen

**Repro:**
1. Open the Learn tab → tap "Five rules" (Unit 0's first lesson bubble).
2. Tap Continue through the lesson; tap "Next: Vowel marks" (the in-lesson auto-advance
   button).
3. Finish "Vowel marks", tap "Next: Finish unit"; finish "Finish unit", tap **"Back to path"**
   (or, equivalently, tap the ✕ "leave lesson" button at any point after the first lesson).

**Actual:** "Five rules" (lesson 1 of the unit) reopens from scratch, not the path screen.
**Expected:** the Unit path screen.

Reproduced twice independently in this run — once at the Unit 0→1 boundary
(`before_back_Finish unit.png` / `after_back_Finish unit.png`) and once after Unit 1's Unit
check quiz (`before_back_Unit check.png` / `after_back_Unit check.png`).

**Root cause:** `openLesson` (`mobile/src/learner.js:20`) sets `st.lessonU`/`st.lessonI` and
calls `runLesson` directly, but it is only ever invoked from a path-screen bubble tap. Once
inside a lesson, `next()`/`finish()` (`mobile/src/path.js:58` and `:61`) advance to subsequent
lessons by calling `runLesson(main, ctx, u, idx+1)` **directly**, bypassing `openLesson` — so
`st.lessonU`/`st.lessonI` are never updated past the very first lesson opened. When "Back to
path" or ✕ later calls `ctx.go('path')` (`mobile/src/learner.js:21`), the `path()` render
function checks `if (st.lessonU)` first and — finding it still set to the original
lesson — **re-runs that stale lesson** instead of showing the path. Tapping the bottom-nav
"Learn" tab does NOT hit this bug (it routes through `today()`, which doesn't consult
`st.lessonU`), so that was used as the workaround to keep this audit moving.

**Suggested fix:** clear `st.lessonU`/`st.lessonI` (or update them) every time `runLesson`
advances to a new lesson, not just on the initial `openLesson` call — or simplest, have the
"Back to path"/✕ handlers explicitly clear `st.lessonU = null` before calling `ctx.go('path')`.

### Bug 2 — [MEDIUM] Quick check is trivial (single un-missable tile) for the very first letter taught

**Repro:** Learn tab → Unit 1 → "alif" (the first letter lesson in the whole course) →
complete through to the "Quick check" screen.

**Actual:** every question (`Which is alif at the isolated position?`, `Tap alif`, `Tap the
letter you hear`) renders with **exactly one answer tile** — see `screen_quick_check.png`.

**Expected:** at least 2–4 plausible options per question, as happens for every subsequent
letter.

**Root cause:** `mobile/src/path.js:87` (kind 0/1) and `:90` (kind 2, "which position") build
distractors from `pool.filter(c => c !== L.ch)`. For the first letter of the app, `pool`
(computed by `learned()` at `path.js:66`) contains only that one letter, so the distractor
list is empty and `shuffle([L.ch, ...[]])` / `shuffle([f[1], ...[]])` yields a 1-tile question.
Contrast with `drills.js:28-29`'s `tellApart`, which has an explicit fallback
(`if (pool.length < 2) pool = [...new Set([...focus, ...shuffle(C.letters.letters...).slice(0,3)])]`)
for exactly this situation — `path.js`'s quick-check code has no equivalent floor.

**Suggested fix:** port the same minimum-pool-size fallback from `drills.js:28-29` into the
three quick-check branches in `path.js`.

### Bug 3 — [MEDIUM] "Words 2" (and any range-sliced word lesson) plays the WRONG audio for every word

**Repro:** Learn tab → Unit 1 → "Words 2" → tap the play (▶) button on any word, or listen
during the Dictation drill's auto-played "Play word".

**Actual:** the audio played is for a **different, earlier word** in the unit (e.g. the 11th
word's play button plays the 1st word's clip).

**Root cause:** `mobile/src/path.js:68,101-105` (`wordsOf(range)` / `case 'words'`) builds a
`sub` object whose `words` array is `u.words.slice(range[0], range[1])` — re-indexed from 0.
`drills.js`'s `readIt` (`:56`), `joinIt` (`:47`), and `dictation` (`:94`) all compute the audio
key as `wordKey(unit.n, i)` using that **local, post-slice index**, but the actual recorded
clips in `audio_index.json` (`units/u01_00` … `units/u01_19`) are indexed by the word's
**global** position in the full 20-word unit list. For "Words 1" (range `[0,10]`) the local
and global indices happen to coincide, masking the bug; for "Words 2" (range `[10,20]`) they
diverge for every single word. Confirmed by inspecting `audio_index.json`'s `units/u01_*` keys
(20 entries, `u01_00`…`u01_19`) against `path.js`'s slicing logic.

**Suggested fix:** carry the original global index through `wordsOf()` (e.g. map to
`{w, globalIndex}` pairs instead of a plain re-sliced array) and have `readIt`/`joinIt`/
`dictation` use the global index for `wordKey`, not the local loop index.

### Bug 4 — [LOW] Stale toast can visually overlap the next screen's primary button

**Observed:** `screen_trace.png` shows a toast reading "Correct: to'e" (the Urdu letter ٹ,
not taught until much later in the course) rendered directly on top of the "Traced it"
Continue button, on the **alif** lesson's trace screen; the same stale toast also appears on
`screen_quick_check.png`, a different screen entirely.

**Root cause:** `content.js`'s `toast()` reuses a single shared `#toast` DOM element with a
fixed 1800ms auto-hide timer (`content.js` line ~18) that is never explicitly cancelled or
hidden on lesson-screen transitions (`path.js`'s `next()` clears `box.innerHTML` but does not
touch the toast element, which lives outside `box` at `document.body` level). Under fast
sequential interaction (a plausible pattern for an impulsive child tapping quickly) a toast
fired just before a screen transition can still be mid-fade when the next screen renders,
visually colliding with its CTA button.

**Suggested fix:** call a `hideToast()`/clear the timeout in `path.js`'s screen-transition
code (`next()`), or move the toast's `z-index` stacking / position so it never overlaps the
fixed bottom action button.

### Design gap (not a functional bug) — touch targets not uniformly upsized for child track

`mobile/src/style.css:55` bumps `.tile` to 68px min-width/height for
`body[data-track="child"]`, correctly landing in research/12's 60–80px recommendation for
ages 3–6. But `.btn`/`.btn-wide` (`style.css:13,15` — Continue, Play sound/word, Check, Next
word) and `.btn-play` (`:16`, 44×44px) get **no equivalent child-track boost** and remain at
the generic 44px minimum, below the same research/12 threshold. Every primary CTA button a
child taps to advance the lesson is smaller than the letter/answer tiles they just tapped.

---

## Prioritised fixes (max 10)

1. **[HIGH]** Fix stale `st.lessonU`/`st.lessonI` so "Back to path" and ✕ always return to the
   path screen, not the first lesson of the unit (Bug 1 — `learner.js:20-21`, `path.js:58,61`).
2. **[MEDIUM]** Add a minimum-distractor-pool fallback to Quick check's three question
   builders so the very first letter isn't a trivial 1-tile question (Bug 2 — `path.js:87,90`).
3. **[MEDIUM]** Fix the word audio-index bug for range-sliced word lessons ("Words 2" and any
   future non-zero-offset range) so play buttons and dictation audio match the displayed word
   (Bug 3 — `path.js:68,101-105`, `drills.js:47,56,94`).
4. **[LOW]** Clear/cancel the shared toast on lesson-screen transitions so it can't overlap the
   next screen's CTA button (Bug 4 — `content.js` toast(), `path.js` next()).
5. **[MEDIUM]** Add narrated audio for the app's own instructions/prompts (or at minimum the
   most-repeated ones: "Tap what you hear", "Listen, then tap the letter you hear", "Which one
   says…", lesson-bubble titles) — the single biggest gap against research/12's own rule #5 for
   a pre-literate 6-year-old target user (§12 above).
6. **[LOW]** Bump `.btn`/`.btn-wide`/`.btn-play` to the same 60–80px child-track floor already
   applied to `.tile` (`style.css:55` vs `:13,15,16`) so every primary CTA is as easy to hit as
   the answer tiles.
7. **[LOW]** Make the trace screen's outcome actually mean something — either gate Continue on
   a minimum trace-check pass (with generous retries), or explicitly relabel the button so it's
   clear tracing is optional practice, not a checked step (`path.js:81` currently appends
   `cont()` unconditionally alongside the drill).
8. **[LOW]** Split "Words 1"/"Words 2" (which bundle read + build-3-words + dictate-5-words in
   one path node) and the 10-question "Unit check" into shorter sub-nodes, or trim their item
   counts — both are likely to run past the app's own "one small lesson" 3–5 min framing for a
   real child (§11 above).
9. **[LOW]** Add an animated stroke-path demo before the freehand trace (currently only a
   static start-dot + text hint), closing the gap against Alif Baa's "arrows shown every time"
   standard cited in the quality bar.
10. **[LOW]** Consider a lightweight "child-safe" romanization-first quiz variant for Unit
    check, since reading `{rom} ({en})` prompts in Latin script/English before picking an Urdu
    word arguably works against the app's own "read Urdu, not English" goal for its youngest,
    non-literate-in-English users.
