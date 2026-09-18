# Critic Round 2 — Units 00–12, blind against Alif Baa 3rd ed. / Delacy

Method: re-read `data/letters.json`, `data/units.json`, `scripts/build_course.py`, regenerated
`course/unit_*.md` with `python3 scripts/build_course.py` (zero diff against committed files —
the course markdown is current with the data), diffed against Round 1's two reports, checked all
220 `units.json` words + 39 `letters.json` entries + 6 diacritics + long-vowel rows by codepoint
and by Urdu-register/naturalness, and did a fresh blind A/B against `/tmp/alifbaa3.txt` and
`/tmp/delacy.txt`. Files were not edited.

---

## 1. Fix-verification table

| # | Claimed fix | File:line / location | Verdict | Notes |
|---|---|---|---|---|
| 1 | ہُوا→ہَوا (wind) | `data/units.json` unit 4, word `["ہوا","hawā","wind","ہَوا"]` | **FIXED** | ہَوا = ہ+zabar+و+ا = *hawā* "wind". Correct now; matches gloss. `course/unit_04.md` §5 regenerated identically. |
| 2 | اعلٰی→اعلیٰ | `data/letters.json` → `diacritics[khari_zabar].example` = `["اعلیٰ","aʻlā","high"]` | **FIXED** | Verified codepoint order: ا‑ع‑ل‑ی‑ٰ (U+0627,0639,0644,06CC,0670) — canonical spelling, khaṛā zabar correctly sits on ی, not ل. Also propagated into `units.json` unit 10 (`["اعلیٰ","aʻlā","high","اَعلیٰ"]`). |
| 3 | Hamza entry now ئ U+0626 with کوئی | `data/letters.json` → `letters[hamza]` | **FIXED** | `ch`="ئ", `cp`="U+0626", `example`=`["کوئی","koʾī","someone / any"]` — کوئی now genuinely contains the letter (ک‑و‑ئ‑ی). `tatoeba_pct`=0.9 matches the recomputed ئ frequency from Round 1's factcheck (item 1). |
| 4 | Long-vowel ū row (drop دو) | `data/letters.json` → `long_vowels[3]` | **FIXED** | Now `["و","ū","جوتا jūtā"]` only; دو removed. جوتا also appears correctly in unit 5's own word list (`jūtā`, "shoe"), so the example is doubly verified as an actual /uː/ word in the course. |
| 5 | Weak words replaced: ابے انا بلا ٹال ماما در کہّ | `data/units.json`, all 12 units | **FIXED** | Scripted search for all 7 strings across every unit's word list: zero hits. Replacements match Round 1's own suggestions almost verbatim: انا→نانا "maternal grandfather" (unit 1), بلا→مالا "garland" (unit 1), ابے→تالاب "pond" (unit 2), ٹال→ٹِکَٹ "ticket" (unit 3), کہّ→ removed from unit 10's list (no longer present, unit 10 has 20 clean words), ماما→ removed/renamed (امام "prayer leader" now used with correct register), در→ removed from unit 4 (no "door" word present). All replacement spellings verified correct by codepoint (اِمام, نانا, مالا, تالاب, ٹِکَٹ all decode to their stated romanisation). |
| 6 | Drill labels (recognition/production, self-check vs helper) | `scripts/build_course.py` `unit_md()`, every `## N · <name>` heading | **FIXED** | All six generic drill headings now carry a label: §3 Tell it apart *recognition · self-check with audio*, §4 Join it *production · self-check against the answer shown*, §5 Read it *reading aloud · self-check with audio, or a helper listens*, §6 Write it *production · needs a helper or the app tracer to check*, §7 Dictation *production · self-check with the key below*, §8 Check *recognition · self-check*. Confirmed present verbatim in every regenerated `course/unit_01.md`…`unit_11.md`. Closes Round 1 fix-list item 7 exactly. |
| 7 | Stroke-direction guidance per letter family in "Write it" | `scripts/build_course.py` `STROKE` dict (17 families + default) + §6 block | **PARTIAL** | Content now exists (previously zero — Round 1's headline finding). But two problems remain: (a) it is placed in **§6 Write it, after §5 Read it** — the exact ordering Alif Baa's own checklist forbids ("writing-practice with stroke guidelines... **before** any reading-comprehension drill"); Delacy's reference page puts stroke diagrams next to the forms table, before reading. (b) it is **text-only** — a one-line prose bullet per letter family, not the numbered/arrowed diagram Round 1's own "Fix" suggested (a visual overlay reusing `render_cards.py`'s glyph geometry). See fact-check §3 below for a specific accuracy concern on the ک (kāf) entry. |
| 8 | Unit 0 minimal triple گَل گِل گُل | `scripts/build_course.py` `special_units()[0]`, "### Same skeleton, three words" | **FIXED** | Present, closely mirrors Delacy's بَک/بِک/بُک device: same three letters گ ل (+mark), three real words (gal "cheek", gil "clay", gul "flower"), explicit "cover the marks" framing. Sits above the existing 6-row reference table, so the course now has both the demonstration *and* the lookup table — arguably ahead of Delacy, which only has the demonstration. |
| 9 | Unit 4 "guess before you look" | `scripts/build_course.py` `special_units()[4]` | **FIXED** | Present: "Cover the forms cards... write دور and ہار from tiles first. Which letters made the next letter start fresh?... You have just discovered it rather than been told it." Matches Round 1 fix-list item 9. Note: this predictive framing was **only added to unit 4's special block**, not generalised to every subsequent "Join it" section as Round 1's fix note literally requested ("every subsequent Join it") — units 5–11's §4 still reveal the built word directly with no predict-first step. Scope of the actual claim ("unit 4 guess before you look") is met; the wider ask is not. |
| 10 | Unit 11 sight-word tell-apart | `course/unit_11.md` "## Tell the sight words apart" | **FIXED** | Present: تھا/تھی, کہ/کے/کو, ہے/ہیں, میں/مَیں. All four are genuine minimal pairs/sets (میں *meṉ* "in" vs مَیں *maiṉ* "I" is a real, correctly-marked contrast). Minor: it's a prose instruction ("Drill them like unit 2") rather than an instantiated drill block with its own audio-file list like §3 in numbered units — adequate but less concrete than the pattern it points to. |
| 11 | Unit 12 comprehension answer key | `course/unit_12.md`, `<details><summary>Answer key — comprehension...</summary>` | **PARTIAL — see new defect below** | An answer key was added (5 numbered answers: Lahore / garden walk / flowers and trees / his sister / tea). But it answers a **passage that does not exist anywhere in the markdown course** — see §2/Assessment below and Prioritised Defects #1. The literal claim ("unit 12 comprehension answer key exists") is true; the underlying Round 1 complaint ("dead reference the reader can't resolve") is not actually resolved for a reader of the course text. |

**Score: 9 fully FIXED, 2 PARTIAL (stroke-guidance placement/medium, Unit 12 answer key grounding).**

---

## 2. Fresh blind A/B

### Letter-introduction page
Compared: `course/unit_01.md` §1–2 (be card) + new §6 stroke line, vs. Delacy Unit 1's
بـ/کـ/لـ/مـ page (`/tmp/delacy.txt` ~420–520).

**Verdict: B (reference) still wins, gap narrowed but not closed.** Round 1's flat "zero stroke
content anywhere" finding is gone — every letter now gets a one-line stroke description. But
Delacy's actual structural advantage was never about the *existence* of stroke content, it was
about **sequencing**: pronunciation cue → forms table → stroke diagram → *then* reading drills.
Ours now runs Hear it → See it (forms) → Tell it apart → Join it → **Read it** → **Write it
(stroke guidance)** — the stroke guidance sits four sections and one full reading drill *after*
the forms table, i.e. exactly the ordering Alif Baa's own checklist item flags as wrong ("...
before any reading-comprehension drill using that letter"). It is also prose, not a diagram — no
arrows, no numbered segments, no dotted trace outline — so a visual/kinesthetic learner still has
nothing to look at, only something to read. Biggest remaining gap: **move (or duplicate) the
stroke line into §2 See It, next to the forms card, and turn at least the highest-frequency
letters into an actual arrowed image**, not just reorder text.

### Joining lesson
Compared: `special_units()[4]` "Guess before you look" vs. Delacy's connector/non-connector prose
(`/tmp/delacy.txt` ~181–220).

**Verdict: A (ours) now wins outright.** Round 1 called this "mixed" because ours had the
interactive tile-build but no predictive/retrieval-practice moment. That gap is closed for unit 4
specifically, and it's a genuinely stronger pedagogical move than Delacy's prose-only explanation
— the learner builds two real words from tiles, is asked to notice the join-break themselves, and
only then gets the rule stated. The remaining asymmetry (units 5–11 don't carry the same predict-
first framing) is a real but much smaller gap than Round 1's.

### Vowel-marking lesson
Compared: `special_units()[0]` "Same skeleton, three words" vs. Delacy's بَک/بِک/بُک triple.

**Verdict: A (ours) now wins.** The minimal-triple device that was "the single most load-bearing
pedagogical device... simply missing" in Round 1 is now present and correctly executed (real
words, shared skeleton, explicit "cover the marks" framing). Ours additionally keeps the 6-example
reference table Delacy doesn't have, so the unit now does both jobs Delacy's page does separately
across two different points in its book.

### Drill set
Compared: unit 6/2 drill sequence (labels now attached) vs. Alif Baa's "At home"/"In class" +
self-graded/teacher-checked labeling philosophy.

**Verdict: A (ours) now wins outright.** The one structural gap Round 1 found (real drill-type
diversity but no self-check/needs-a-human labeling) is closed cleanly and consistently across
every unit's every drill heading. Combined with the drill-type diversity and real-word density
Round 1 already credited A with, there's no remaining dimension where B leads here.

### Assessment (Unit 12)
Compared against the same 4-item checklist as Round 1: (a) inline quiz, (b) resumable progress
marker, (c) self-checkable answer key, (d) instructor/external-check point.

**Verdict: B (reference tradition, composite) still wins — and this area has a new, sharper
problem, not just a leftover one.** (a) and (d) still hold as in Round 1. (c) is now *nominally*
satisfied — Unit 12 has an answer key — but tracing where the answers come from breaks the course:
Unit 12 says "read **the unit 11 passage** aloud," yet `course/unit_11.md` contains no passage —
only a sight-word table and three unrelated one-line sentences (about Kamal's name/school/rain).
The actual ~60-word passage ("میرا نام کمال ہے۔ میں لاہور میں رہتا ہوں...") that the new answer
key (Lahore / garden / flowers and trees / sister / tea) genuinely answers lives **only** inside
`app/template.html` as a JavaScript string, never surfaced in any `course/*.md` file and never
linked to from either unit 11 or unit 12's markdown, or from `course/00_design.md`. A reader
following the markdown course — which is the primary deliverable per Round 1's own framing — now
hits a *worse* version of the original dead reference: previously the vague phrase "app's progress
screen" at least signaled "go find an app"; now a specific, plausible-looking answer key cites
concrete facts (a named city, a sister, tea) that the reader has never been shown a source for,
which reads as either a hallucinated answer key or an undisclosed forward reference — neither is
acceptable at the capstone assessment.

---

## 3. Fact-check — all 220 words + STROKE dict

**Words:** every `units.json` word across all 12 units checked for (a) codepoint self-consistency
(vowelled column strips to the base spelling, allowing tashdīd/khaṛā-zabar/madd which are always
written even "unvowelled" — scripted, 0 real mismatches after accounting for that convention),
(b) spelling correctness, (c) romanisation-to-vowelling match, (d) gloss accuracy/register/
naturalness for a beginner reader. Full pass, not spot-check.

**Result: no new spelling/vowelling errors found among the 220 words** (the 7 Round 1 flagged
words are gone and their replacements are all independently verified correct). Two pre-existing,
lower-severity issues survive from Round 1 that were **not** on the claimed-fix list, so are not
mis-scored above, but are worth carrying into this round's defect list:

- **`مان` glossed "accept" (unit 1)** — still present, still the weaker of the two readings (مان
  bare is closer to "pride/self-respect" or the imperative "accept!", not a clean infinitive-free
  noun gloss). Round 1 item 3, never claimed fixed, still live.
- **`letters.json` `be`.example gloss "father" vs. `units.json` unit 1's own gloss "dad" for the
  same word بابا** — minor but real: the same word gets two different English glosses depending
  on which data file renders it, which a learner comparing the §1 Hear it audio caption against
  the §5 Read it table could notice as inconsistent.

**New decodability gap, not previously flagged as a specific instance (structural issue is Round 1
factcheck item 5, medium confidence, never claimed fixed):**
- `آنکھ` "eye" (unit 6) and `ذائقہ` "taste" (unit 9) both use letters (آ alif-madd, ئ hamza-on-ye)
  that are not formally taught until unit 10 (per unit 10's own `focus` field: "ئ ؤ آ") and have
  **no `letters.json` entry at all** — yet neither word carries a "(… preview)" gloss tag the way
  `ٹوپی`(unit 3, و-preview) or `بھائی`(unit 6, ئ-preview, correctly tagged!) do. `بھائی` in the
  *same unit* (6) correctly flags its ئ as a preview — so the convention is known and used
  correctly elsewhere, making `آنکھ`'s silence more likely an oversight than a design choice.
  `scripts/check_decodable.py` will never catch this: it hardcodes
  `ALWAYS = set("ءئؤآأـ") | {diacritics}` — i.e. it unconditionally exempts hamza-forms and
  alif-madd from the taught-letters check regardless of whether `letters.json` actually has an
  entry for them, which is why `python3 scripts/check_decodable.py` reports **"0 violations"**
  even though the underlying gap (no آ/ؤ/ۃ rows in `letters.json`) is real and verified. This
  gives false confidence — the checker was built in a way that can't detect the exact class of
  bug it exists to catch.

**STROKE dict (`scripts/build_course.py`), spot-checked against real Naskh calligraphy practice:**
- **د (dāl) — "start at the top, come down and out to the left in one angled stroke; never joins
  forward."** Correct. Dāl is universally taught as a single diagonal stroke, and the course's own
  `research/03_script_reference.md` independently confirms dāl as a confirmed non-joiner. No issue.
- **ک (kāf) — "the sloping cap stroke first from top-left down to the right, then the base going
  left; گ adds a second cap stroke."** **Likely wrong stroke order, flag for verification.**
  Standard practice (and the course's own stated general rule, repeated in every unit: "each
  letter body is drawn in one stroke where possible; dots and small marks are added last") draws
  the main body first and adds the small diagonal "flag"/cap accent on top *last*, the same way
  dots are added last — the cap stroke is cosmetically closer to a dot/mark than to the letter
  body. Describing it as drawn *first* both contradicts common calligraphic teaching order and is
  internally inconsistent with this very document's own "marks last" rule stated two paragraphs
  above it in every generated unit file. This is exactly the kind of claim the task brief asked to
  be checked ("is ک really drawn cap-first?") and it does not hold up — recommend verifying against
  an actual calligrapher or a sourced stroke-order reference before shipping, not shipping on
  inference the way this line currently is.
- **ط/ظ (toe family) — "draw the loop first (like ص), then the tall stroke rising from its right;
  dot after for ظ."** Directionally plausible but **unverified** — no primary source in this
  repo's `research/` covers stroke order at all (confirmed: `grep -i "stroke" research/*.md`
  returns nothing), so this line and the rest of the `STROKE` dict rest entirely on the model's
  own inference, same as کاف above. Lower confidence than the کاف flag only because it's less
  directly contradicted by the document's own stated rule, not because it's confirmed correct.
- Remaining 14 families (alif, be, jim, re, sin, ain, fe, lam, mim, nun, wao, he, ye, hamza, +
  default) read as accurate, standard descriptions of Naskh letterforms and match their letters'
  known shapes (e.g. `ھ`'s "two connected bowls open at the top" literally matches its name
  do-chashmi/"two-eyed" he). No further issues found.
- **Coverage check:** all 17 `family` values used in `letters.json` have a matching `STROKE` key
  (scripted) — no letter silently falls through to the generic `default` string.

---

## Prioritised remaining defects (max 10, most damaging first)

1. **Unit 12's comprehension answer key answers a passage that doesn't exist in the markdown
   course.** `course/unit_11.md` has no ~60-word passage; the real one is buried as a JS string in
   `app/template.html` with zero link from any `course/*.md` file. A markdown-only reader hits a
   worse dead-reference than Round 1 found: specific, ungrounded answers (Lahore/garden/sister/tea)
   with no visible source. Fix: either paste the actual passage into `course/unit_11.md` §5/§9, or
   add an explicit `[Read the full passage in the app](../app/index.html)` link from both unit 11
   and unit 12, and from `course/00_design.md`'s per-unit shape section per Round 1's original ask.

2. **Stroke-direction guidance is sequenced after the reading drill, not before it.** §6 Write It
   (which now carries the stroke text) comes after §5 Read It in every unit; Alif Baa's own
   checklist explicitly requires stroke guidance before reading-comprehension drills. Fix: move the
   "How the pen moves" block (or a short version of it) into §2 See It, next to the forms card.

3. **کاف (ک) stroke-order claim ("cap stroke first") likely contradicts standard calligraphic
   practice and this document's own "marks/dots last" rule.** Verify against a real source before
   shipping; currently the STROKE dict's entire content is unsourced model inference (confirmed:
   no `research/*.md` file mentions stroke order at all).

4. **`scripts/check_decodable.py` hardcodes an unconditional exemption for ء ئ ؤ آ أ**
   (`ALWAYS = set("ءئؤآأـ")`), so it will report "0 violations" forever regardless of whether
   `letters.json` actually has entries for آ/ؤ — which it doesn't. This gives false confidence in
   the pipeline's own gate. Either add real `letters.json` rows for آ, ؤ (and `ۃ`, referenced in
   unit 10's `letters` field but also absent from `letters.json`), or make the checker's exemption
   conditional on a "these are deliberately ungated" comment plus a manual audit note, not silent.

5. **`آنکھ` (unit 6, "eye") and `ذائقہ` (unit 9, "taste") use آ/ئ without the "(… preview)" tag**
   that the very same units use correctly elsewhere (`بھائی` in unit 6 tags its ئ correctly). Add
   the preview tag to both, consistent with the convention already in use.

6. **Stroke guidance is text-only, not a diagram.** Round 1's own "Fix" note asked for a rendered
   overlay (arrows/numbered segments on the existing glyph, reusing `render_cards.py`'s geometry);
   what shipped is one prose sentence per letter family. Still closes some of the gap but not the
   visual/kinesthetic half of it.

7. **"Guess before you look" predictive framing exists only in unit 4, not generalised to unit 6's
   ں/ھ or the rest of the course's "Join it" sections**, despite Round 1's fix note explicitly
   asking for "every subsequent Join it." Low cost to extend given the pattern is now proven out.

8. **`مان` glossed "accept" (unit 1) is still the weaker of two possible readings** — بare مان is
   closer to "pride/self-respect" or an imperative; carried over from Round 1, never claimed fixed,
   still live.

9. **Cross-file gloss inconsistency: `letters.json`'s `be` entry glosses بابا as "father," while
   `units.json` unit 1 glosses the same word as "dad."** Minor, but a learner cross-referencing the
   §1 Hear it audio caption against the §5 Read it table will see two different English words for
   one Urdu word.

10. **Unit 11's "Tell the sight words apart" section is a prose instruction ("Drill them like unit
    2"), not an instantiated drill block with its own listed audio files**, unlike every numbered
    unit's §3. Functionally adequate but a step down in concreteness from the pattern it's copying.
