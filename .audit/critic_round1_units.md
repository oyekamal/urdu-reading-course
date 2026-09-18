# Critic Round 1 — Units 00–12, blind against Alif Baa 3rd ed. / Delacy

Reviewer stance: harsh, blind-comparison per `research/00_quality_bar.md` protocol. Reference sources:
`/tmp/alifbaa3.txt` (real Teacher's Edition preview, Unit 2 ب/ت/ث block + alif section) and
`/tmp/delacy.txt` (real 2003 first-edition full text, Introduction + Unit 1). Where the protocol's
functional-spec-only components (Duolingo matching, tracing-app, Aamozish quizzes) are concerned, I
score against the checklist, not a stripped blind sample, per the protocol's own rule 3.

---

## 1. Letter-introduction page (single new letter, first appearance)

Compared: our `be` card (`assets/images/letters/be_naskh.png` + `assets/images/forms/be_naskh.png`,
driving Unit 1 §1–2) vs. Delacy Unit 1's بـ/کـ/لـ/مـ intro (pronunciation cue → positional-forms
table → writing practice, `/tmp/delacy.txt` lines ~420–520).

**Verdict: A (ours) wins on presentation, B (reference) wins on completeness.**
Our card is genuinely better typeset than the scanned reference — clean color-coded example word,
IPA, plain-English sound-alike cue, all four positional forms laid out in one glance with dot
position visible. Delacy's table is functionally denser but visually a flat monochrome scan grid.
On production quality alone ours is the stronger artifact.

But Delacy's page does one thing ours never does anywhere in the six units read: it shows the
**stroke formation** — numbered, arrowed diagrams for how the pen moves to draw each form ("alif is
written top to bottom... when it follows another letter it is written bottom up"), immediately next
to the positional-forms table, before any reading drill. Ours has no equivalent at any point in the
letter-intro flow; the forms card is a static end-state comparison, not a formation guide.

**Biggest gap:** No stroke-order/writing-direction content exists anywhere in the repo. I searched
`assets/` for anything matching `*trace*` or `*stroke*` — zero files. Unit 1 §6 "Write it" instructs
"Trace each new letter... Use the forms card as the model," but the forms card (`forms/be_naskh.png`,
inspected directly) has no directional arrows, no numbered stroke sequence, no dotted guideline
outline to trace — it is the same static glyph shown in §2. A learner (especially the "children:
required" tracing population the course itself calls out in row 11 of `00_design.md`) has nothing
telling them which direction the pen moves, which is exactly the feature Delacy's page and the
quality bar's own checklist ("directional stroke guide... not just a static shape to copy") require.

**Fix:** Generate a third image variant per letter — `assets/images/strokes/<letter>_naskh.png` —
numbered stroke segments with arrowheads, reusing the same render pipeline as
`scripts/render_cards.py`. Cheapest version: overlay 2–3 arrows per form on the existing glyph
outline; script already has the glyph geometry since it renders the card.

---

## 2. Joining / non-joiner lesson

Compared: `course/unit_00.md` §2 ("Letters join like cursive... ten letters never join") + Unit 1 §4
"Join it" tile-building drill, vs. Delacy's Introduction connector/non-connector passage
(`/tmp/delacy.txt` lines ~181–220).

**Verdict: mixed, leaning B (reference) on explanatory completeness, A (ours) on hands-on practice.**
Delacy's prose actually explains the *mechanism*: connectors join both sides and therefore have
"essentially four forms" that vary by position; non-connectors join only to the preceding character
and therefore reduce to "essentially two forms, an initial and final form" — with the reasoning
spelled out (initial=independent because nothing precedes it forward; final=medial because nothing
follows). Our Unit 0 §2 states the *fact* ("ten letters never join... after one of these the word
restarts") but never explains *why* a non-joiner only has two forms — it's asserted, not derived.
Ours compensates in Unit 1 §4 with an interactive tile-build (بابا, ماما, نام) that lets the learner
*see* a non-joiner's shape freeze mid-word, which Delacy's book — static print — cannot do at all.
That is a real, structural advantage unique to a digital format the quality bar explicitly wants
credited (row 349 protocol, component 2).

**Biggest gap:** the ten-non-joiner list is stated once in Unit 0 and never re-derived or drilled as
a *rule you can apply to a new letter*, only memorized as a fixed list. When unit 4 introduces و ر د,
the text says "does not join forward" for each individually but never asks the learner to predict
this from the rule before revealing it — a missed retrieval-practice opportunity Delacy doesn't offer
either, but the interactive tile format *could* (a "guess before you build" prompt), and currently
doesn't.

**Fix:** In Unit 1 §4 and every subsequent "Join it," ask the learner to predict join/no-join for the
new letter before showing the tile animation, not just watch it happen.

---

## 3. Vowel-marking lesson (short vowels / diacritics)

Compared: `course/unit_00.md` "Vowel marks" table (زبر/زیر/پیش/جزم/تشدید/کھڑا زبر) vs. Delacy's
"Representation of short vowels" (Unit 1, `/tmp/delacy.txt` lines ~470–530).

**Verdict: B (reference) wins.** Delacy's section does the one thing that actually teaches the
*point* of diacritics: it takes a single fixed three-letter skeleton (بک) and shows it three ways —
بَک bak "nonsense," بِک bik "stem of 'to be sold'," بُک buk "book" — proving with a minimal triple
that the mark, not the letters, carries the meaning. Our Unit 0 vowel-marks table gives six
*different* example words, one per mark, each with a different consonant skeleton (بَس, دِل, گُل,
بَسْ, بچّہ, اعلٰی) — a reference table, not a demonstration. A learner can memorize "zabar = short a"
without ever seeing the causal link "same three letters, three different vowels, three different
words," which is the actual cognitive move Alhawary's diacritics research (cited in row 5 of
`00_design.md`) is about.

**Biggest gap:** no minimal-pair/triple demonstration exists anywhere in the vowel-marks section —
the single most load-bearing pedagogical device the reference book uses for this exact lesson is
simply missing.

**Fix:** Add one minimal-triple row to the Unit 0 vowel-marks table using a skeleton already taught
by Unit 1 (e.g. کل: کَل kal "yesterday/tomorrow" / کِل — not real / کُل kul "all" — or pick a skeleton
that yields three genuine words) directly under the six-row table, explicitly framed as "same
letters, different mark, different word."

---

## 4. Drill set (Unit 6, aspirates + Unit 2 dot-cluster, as representative samples)

Compared: our "Tell it apart" / "Join it" / "Read it" / "Dictation" / "Check" sequence vs. Alif Baa's
"Reading and writing practice" (At home/In class labeled, Teacher's Guide description,
`/tmp/alifbaa3.txt`) and Delacy's Roman↔Urdu transliteration drill.

**Verdict: A (ours) wins on drill-type diversity and real-word density, B (reference) wins on one
specific structural label ours lacks entirely.**
Ours genuinely covers more drill types per unit than either reference alone: recognition
(audio-point, §3), production (tile-build, §4), reading (§5), copying/tracing (§6), dictation (§7,
correctly labeled and distinct from copying, matching the quality bar's own checklist item), and a
scored self-quiz (§8). Every item uses real words, never meaningless syllables — also a direct hit
on the quality bar's checklist. Delacy's drill is a single Roman↔Urdu transliteration exercise per
unit; Alif Baa's per-unit drill count is comparable to ours but is explicitly labeled "At home" vs.
"In class" throughout the book — ours has no equivalent label anywhere.

**Biggest gap:** no drill in any unit read is marked self-graded vs. needs-a-human-check. The
quality bar's checklist for Alif Baa is explicit that this is a real fail mode: "the course should
never leave the learner unsure whether a drill is self-graded or needs a human check." Our §7
Dictation ("Play each clip twice. Learner writes the word. Then reveal.") implicitly assumes a
second person exists to play audio and check handwriting, but this is never stated, and §6 Write It
similarly assumes an adult/teacher checks the tracing — for the solo/self-teaching adult use case
(which `00_design.md` explicitly supports — "adults: optional"/"recommended"), there is no guidance
on how a lone learner self-checks handwriting or dictation at all.

**Fix:** Add one line per drill type stating who checks it — e.g., "Dictation: self-check against
the answer key below" vs. "Write it: no answer key possible for handwriting; if learning alone, use
the traced letter as your own reference and move on" — closing the exact gap the quality bar names.

---

## 5. Assessment (Unit 12, EGRA-style test)

Compared against the quality bar's 4-item structural checklist: (a) inline quiz, (b) resumable
progress marker, (c) self-checkable answer key, (d) instructor/external-check point.

**Verdict: B (reference tradition, composite) wins on completeness; ours over-promises on (b).**
Unit 12 clearly hits (a) — every prior unit's §8 Check is an inline, scored quiz — and (d) — the
EGRA test is explicitly "one-to-one," i.e. an external/instructor check point, matching Alif Baa's
instructor-checked-dictation model. It does **not** hit (c): unlike every other unit, Unit 12's test
has no answer key for the nonword list, familiar-word list, or the 5 comprehension questions —
there's nothing here a solo adult learner can self-check against, which is inconsistent with the
course's own stated self-teaching support elsewhere.

**Biggest gap:** "Record results in the app's progress screen or on paper" (Unit 12, final line)
references an "app's progress screen" that is never defined in any of the six units read, and no
progress-tracking mechanism is described anywhere in `00_design.md`'s per-unit lesson shape (§3) —
this is a forward reference to a feature the course text gives the reader no way to locate or
verify exists (`app/` does contain `index.html`, but the markdown course itself never says so or
links to it). A learner following just the units document hits a dead reference at the exact moment
they most need feedback — the capstone assessment.

**Fix:** Either link explicitly to `app/index.html` from Unit 12 (and ideally from `00_design.md`'s
per-unit shape section so the reader knows an app exists at all before unit 12), or strip the "app's
progress screen" line and replace with a plain paper-tracking template if the app isn't meant to be
part of the course deliverable yet.

---

## Factual-error / naturalness check (30+ words checked against my own Urdu knowledge)

Checked every glossed word in Units 1, 2, 4, 6, 11 (≈95 words) plus Unit 0's vowel-mark examples.
Concrete findings:

1. **Unit 4, `ہُوا` glossed "hawā" / "wind" — likely wrong diacritic.** As marked (pesh on ہ, giving
   "hu" + wā), this spells هوا **huā** = "happened/became" (past tense of ہونا, extremely common
   verb form), not **hawā** "wind." "Wind" (hawā) is normally spelled ہَوا with zabar, not pesh, on
   ہ. Either the mark or the gloss is wrong — as printed, the word and its meaning don't match. This
   is the single clearest factual error found; it sits in a "Read it" table the learner is expected
   to sound out and trust literally.
2. **Unit 1, `ماما` glossed "maternal uncle."** In standard Pakistani Urdu, "maternal uncle" is
   ماموں (māmūṉ); ماما more commonly denotes a male nanny/domestic attendant, or is used regionally/
   colloquially for uncle but is not the standard gloss a Pakistani course should lead with. Worth
   double-checking against the Tatoeba source data — if it's driving the letter-frequency word list,
   a wrong gloss here undermines the "real words" claim the design doc makes.
3. **Unit 1, `مان` glossed "accept."** مان as a bare word is closer to "pride/self-respect" (noun) or
   the informal root of ماننا "to believe/accept" — glossing the bare stem as the finite-sounding
   "accept" without the infinitive is a stretch a beginner reading Roman "accept" next to مان will
   not be able to use correctly in a sentence.
4. **Unit 4, `دَر` glossed "door."** Standard everyday word for door is دروازہ (darwāza); در alone is
   mostly literary/Persian-register ("dar" as in "dar-o-diwar"). Not wrong, but not the natural
   beginner-register word a frequency-driven word list should be leading with for "door" — check
   whether the Tatoeba source actually attests در as "door" in running Urdu text or whether this is
   an inference from Persian.
5. **Unit 0, `اعلٰی` for "aʻlā" (khaṛā zabar example).** Standard modern spelling is **اعلیٰ**
   (choṭī ye followed by khaṛā zabar diacritic on the ye) — the form printed, with the diacritic
   apparently on lām before a bare ye, looks like a character-order slip. Needs a direct Unicode
   diff against the canonical spelling before shipping; if this is genuinely wrong it's teaching a
   misspelling of a word the course uses to explain a diacritic most learners will otherwise never
   need this early.

No other errors found in the ~90 remaining words checked — romanization (macrons for length, dots
for retroflexion) and glosses for common words (nām, kām, kitāb, billī, roṭī, ghar, bhāʾī, khānā,
maiṉ, hāṉ, kahāṉ, etc.) are all correct and natural for Pakistani Urdu.

---

## Prioritised fix list (max 10, most damaging first)

1. **Fix or re-diacritize `ہُوا`/"hawā"/"wind" in Unit 4** — a factual error in a core reading table,
   the exact kind of error the vowel-marks system exists to prevent (see Factual-error item 1).
2. **Add stroke-order/writing-direction guidance to every letter card** — currently zero files
   anywhere in `assets/` cover this; Unit 1–11 all instruct tracing against a model that has no
   directional information, contradicting the quality bar's explicit tracing checklist.
3. **Add a minimal-pair/triple demonstration to the Unit 0 vowel-marks section** — the single
   pedagogical device the reference book uses to prove marks carry meaning is entirely absent from
   ours; currently a lookup table, not a lesson.
4. **Verify `ماما`/"maternal uncle" and `دَر`/"door" glosses against the actual Tatoeba source data**
   — both read as non-standard-register choices for a frequency-driven beginner word list; confirm
   they're not silently distorting the "real words, real frequency" claim in `00_design.md` row 2.
5. **Close the Unit 12 "app's progress screen" dead reference** — either link `app/index.html`
   explicitly or remove the reference; as written it points to something the reader of the course
   markdown has no way to discover exists.
6. **Verify `اعلٰی` vs. canonical `اعلیٰ` spelling** in the Unit 0 khaṛā zabar example — possible
   character-order error in a word chosen specifically to teach that diacritic.
7. **Label every drill by who checks it** (self-check / needs a second person / instructor-only) —
   Dictation and Write It currently assume an unstated second person for solo adult learners, the
   exact ambiguity the quality bar's checklist calls out as a real Alif Baa design decision ours
   doesn't match.
8. **Add an answer key to Unit 12's assessment** — the only unit read that breaks the course's own
   self-check-answer-key pattern, at the point (capstone test) where a solo learner needs it most.
9. **Make the non-joiner rule predictive, not just declarative** — ask learners to guess join/no-join
   for a new letter (o ر د in Unit 4, ں in Unit 6) before revealing it, turning the rule from a
   memorized list into an applied skill, closing the gap noted in component 2.
10. **Give Unit 11 a "Tell it apart" pass over confusable sight words** (کہ/کے, تھا/تھی, نے/کے) —
    Unit 11 currently skips straight to §4 Join It with no §1–3 (Hear it/See it/Tell it apart), which
    is defensible since no new letters are introduced, but the sight-word set has real visual
    confusables (تھا vs تھی, کہ vs کے vs کو) that the course's own confusability-first design
    philosophy (row 3, `00_design.md`) says should get contrast drills, and currently don't.
