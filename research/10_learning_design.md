# Learning-Science Research: Learner Mode Design for an Offline Urdu-Reading App

Research pass date: 2026-09-18. Scope: how to organise practice (spacing, gating, session
design, feedback, decodable-text progression, tracing, progress views, heritage-adult
shortcuts, accessibility, self-administered measurement) for the existing drill set: hear
letter, positional forms, tap-what-you-hear, tile word-building, read vowelled words +
audio, trace on canvas, dictation with letter keyboard, 10-item unit quiz gate, sight
words, Naskh→Nastaliq switch, EGRA-style reading test.

Method: DDG search (`ddg.py`) across 10 topic areas + primary-source PDF reads (Duolingo
Method whitepaper, EDC/Duolingo ABC efficacy report). Citations inline; `UNVERIFIED` marks
anything not confirmed against a primary/authoritative source. No academic-database or
paywalled-journal full-text was read beyond what's linked below — search-result
abstracts/snippets are marked as such where a full paper wasn't opened.

---

## 1. Spaced repetition scheduling

**Feature: adaptive review scheduler over all letter/word items, not a fixed drill order.**

- Three real algorithm families exist: **Leitner** (box-based, coarse, easy to implement
  with plain "move up on correct / move to box 1 on wrong"), **SM-2** (SuperMemo-2, what
  Anki has shipped by default for ~20 years — ease-factor per card, deterministic interval
  multiplication), and **FSRS** (Free Spaced Repetition Scheduler — a 2022+ open-source
  model that fits a memory model with three latent variables, Difficulty/Stability/
  Retrievability (DSR), per learner from review history, and is now considered to
  out-perform SM-2 on retention-per-review). Source: open-spaced-repetition/awesome-fsrs
  (https://github.com/open-spaced-repetition/awesome-fsrs), Expertium's technical writeup
  (https://expertium.github.io/Algorithm.html), Brainscape's comparison
  (https://www.brainscape.com/academy/comparing-spaced-repetition-algorithms/).
- FSRS schedules each review to land at a target retrievability (commonly ~90%), predicting
  a forgetting curve per item per learner rather than a fixed per-box interval; it needs a
  review-history log to fit its weights, which a from-scratch learner (no history) doesn't
  have yet — so a **cold-start fallback to a Leitner-style 3–5 box schedule for the first
  ~1–2 weeks of an item's life, then switching that item onto an FSRS-style model once ≥3–5
  reviews exist**, is the simple/proven combination. FSRS itself ships a documented
  cold-start default-parameter set for exactly this reason (source: gnoseed.com/algorithms/fsrs,
  learnbook.ai/en/blog/how-fsrs-works).
- **Recommendation for this app:** Leitner is simple enough to implement offline with no
  telemetry pipeline and is "good enough" per SuperMemo's own historical framing — the
  incremental gain of SM-2 over Leitner, and FSRS over SM-2, is measured in total-review-count
  efficiency, not pass/fail outcome; for a low-stakes children's app where review load is
  already capped by session length (see §3), simplicity should win unless there's already an
  offline-capable FSRS library to embed (there is: `rs-fsrs` in Rust,
  https://deepwiki.com/open-spaced-repetition/rs-fsrs — fully offline, no telemetry needed,
  runs per-device). UNVERIFIED whether embedding rs-fsrs is worth the complexity at this
  app's scale (tens of letters + few hundred words) vs. Leitner; flag as an open decision,
  not a research gap.
- **Duolingo's own scheduler is NOT SM-2/FSRS** — it's Half-Life Regression (HLR), described
  by Duolingo Research (https://research.duolingo.com/) as modelling a per-item "half-life"
  (days until 50% recall probability) from a large feature set (item, learner history,
  lexeme tags) and re-computing it after every exercise; "Birdbrain" is Duolingo's broader
  ML system that additionally picks exercise *difficulty and order* (not just *when to
  review*), per the Duolingo Method whitepaper (Freeman, Kittredge, Wilson, Pajak 2023,
  https://duolingo-papers.s3.amazonaws.com/reports/duolingo-method-whitepaper.pdf, §2.3
  "Focus on What Matters" / spaced repetition): *"spaced repetition means learners revisit
  new content frequently after they've first learned it, but later on they revisit that
  content less frequently, as long as they're consistently showing they know it... using
  Birdbrain to model learner knowledge, Duolingo is able to optimize when learners need to
  review and when they should do it... which has shown even greater effects on retaining
  learning than a non-personalized review schedule (Lindsey et al., 2014)."* This is
  Duolingo-scale infra (1B+ exercises/day) — not replicable offline, but the *principle*
  (schedule per-item, not per-lesson; personalize interval to individual forgetting rate) is
  exactly what Leitner/FSRS approximate at small scale.
- **Review load a 10-minute daily session tolerates:** no single source gives a hard number
  for "how many spaced-repetition reviews fit in 10 minutes for a 5–8-year-old." Compute an
  app-specific budget instead: each letter-sound review in this app (hear-letter or
  tap-what-you-hear) is a ~3–8 second interaction; at generous overhead (audio playback +
  response + feedback animation), budget **~5–8 seconds/review**, so a 10-minute (600s)
  session split ~50/50 between *new learning* and *review* leaves **~35–60 review slots/day**
  — comfortably covers a growing deck of tens-to-low-hundreds of letters/words if intervals
  are respected (most items won't be due most days). This budget estimate is a first-
  -principles calculation from this research pass, not sourced — mark **UNVERIFIED** as an
  exact figure, but the arithmetic approach (session-seconds ÷ seconds-per-review) is a
  standard capacity-planning method for review apps and should be validated with real timing
  data once drills are instrumented.

## 2. Mastery gating vs. free exploration; interleaving vs. blocking

**Feature: current 10-item, 8/10 unit-quiz gate before the next unit unlocks.**

- Mastery learning (Bloom, 1968) is the named tradition behind "must hit a criterion score
  before advancing," with 80% as the most commonly cited criterion threshold across
  mastery-learning literature (e.g. "a fixed criterion level of achievement, for example,
  80 percent, is chosen" — JSTOR, "Learning as a Function of Time,"
  https://www.jstor.org/stable/27539747; SimpliTrain's applied-research summary,
  https://simplitrain.com/blog/adaptive-learning/, describing a cert track that "holds
  learners at 80 percent demonstrated mastery before advancing"). **8/10 = 80% is therefore
  squarely inside the evidence-backed convention**, not an arbitrary number — keep it.
- Duolingo's Math app documentation (whitepaper §"Learn in a Personalized Way," Duolingo
  Math section) explicitly does **not** gate units sequentially — *"it's not necessary to
  complete all prior skills and units before moving to the next one"* — but *does* gate
  within-unit progress with retry-on-mistake + an end-of-unit "review skill" that mixes
  previous mistakes with unit content in **interleaved practice**, citing Foster, Mueller,
  Was & Dunlosky (2019) *"Why does interleaving improve math learning?"*
  (https://doi.org/10.3758/s13421-019-00918-4) for why mixed/interleaved review beats
  blocked review for later recall. This is a genuinely different model from a strict
  gate-before-next-unit — it trades "can't skip ahead" for "always-available adaptive
  review of everything so far." Given this app already has a hard quiz gate, that's fine
  (defensible under mastery-learning literature) but the **within-unit exercise order should
  still interleave**, not block, especially for confusable letters.
- **Interleaving vs. blocking for confusable letters — this is the single best-evidenced
  design lever in the whole brief.** Multiple independent literatures converge:
  - Bjork & Bjork (2019), "The myth that blocking one's study or practice is best,"
    (https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2020/01/BjorkBjorkEducatinMythChapterPublishedFormSept2019.pdf):
    *"a growing body of research suggests that interleaving, not blocking, enhances the
    learning and transfer of to-be-learned skills and knowledge."* Interleaving works
    specifically because it forces **discriminative contrast** — the learner must
    distinguish item A from item B on every trial instead of pattern-matching "whatever's
    being drilled right now." This is exactly the mechanism confusable-letter drills need
    (e.g. Urdu ب/پ/ت/ث/ٹ or ج/چ — same base shape, different dots/count).
  - A 2025 ScienceDirect study on adaptive interleaved practice
    (https://www.sciencedirect.com/science/article/pii/S1041608025001803) found *"both
    random and adaptive interleaved practice enhance long-term learning... compared to
    blocked practice."*
  - Foster et al. 2019 (cited above, and independently in the Foster/Mueller reference list
    of the Duolingo whitepaper) attribute the benefit specifically to **discriminative
    contrast + distributed practice** — i.e. interleaving is doing two jobs at once
    (spacing *and* discrimination training), which matters for a confusable-letter design:
    don't drill پ in isolation for 5 reps then switch to ت; interleave پ/ت/ٹ/ب items from
    the first rep onward.
  - Reported effect sizes in the wider literature run 25–76% relative improvement on
    delayed tests (secondary/anecdotal source, Facebook post citing "The Effortful
    Educator," https://www.facebook.com/groups/936224677134174/posts/1020637565359551/ —
    **UNVERIFIED**, treat as an approximate/anecdotal range, not a citable number; the
    *direction* of the effect is well-supported by the peer-reviewed sources above, the
    *magnitude* is not independently confirmed here).
  - **Design implication for tap-what-you-hear:** the confusable-letter drill should
    interleave a target letter's distractor set (visually/acoustically similar letters)
    within the same short block, and this set should evolve — a letter that's still shaky
    should keep showing up interleaved with its actual confusers, not drilled alone.
- **Duolingo's adaptive difficulty ("Birdbrain") pattern to borrow:** within a lesson, if a
  learner is doing well the algorithm "selects slightly more challenging exercises"; on a
  mistake, "they receive a hint, and an exercise targeting the same concept is resurfaced at
  the very end of the lesson" (whitepaper §2.3) — i.e. **immediate re-drill at end-of-session,
  not end-of-day**, for anything just missed. This is cheap to implement without ML: track
  wrong answers in-session, requeue them at the tail of the session's item list.

## 3. Session design (length, streaks, rewards)

**Feature: 10-minute daily session as designed; streaks/rewards layer (not yet built,
per the brief's drill list, but implied by the request).**

- **Attention-span-by-age rules of thumb** (multiple parenting/clinical sources, consistent
  with each other): 5–6yo ≈ 12–18 min, 7–8yo ≈ 16–24 min sustained attention
  (cnld.org, https://www.cnld.org/how-long-should-a-childs-attention-span-be/; a commonly
  cited rule-of-thumb is "2–3 minutes per year of age," Brain Balance Centers,
  https://www.brainbalancecenters.com/blog/normal-attention-span-expectations-by-age). A
  **10-minute session sits comfortably inside the sustained-attention window even for a
  5-year-old**, which supports keeping the session short rather than trying to lengthen it
  for "more practice" — the constraint is attention, not content volume.
- **Duolingo ABC's own field-tested guidance (this is a direct, load-bearing comparable):**
  the EDC efficacy study on Duolingo ABC (Lavigne, Kennedy, Lemieux, Salone Maxon, EDC,
  Jan 2022, https://duolingo-papers.s3.amazonaws.com/reports/edc-report-on-duolingo-abc.pdf)
  reports the app developers' own recommended usage pattern: **"one possible usage scenario,
  recommended by Duolingo ABC researchers, was to spend 15–20 minutes 3–4 times a week"**
  (p.7, footnote 4: *"This guidance was based on a recommendation from the app developers as
  a useful guideline for caregivers on how long a typical session might last"*). The study's
  actual minimum-dosage instruction to caregivers was just "at least one hour per week" —
  looser than a strict daily 10-minute rule — and **still produced a statistically
  significant literacy gain** (see below), which is evidence that *consistency over weeks*
  matters more than *hitting an exact daily minute target*. This somewhat undercuts a rigid
  "must do 10 minutes every day" design in favor of "some daily-ish practice, forgiving of
  missed days."
- **Duolingo ABC efficacy numbers (single strongest quantitative source found in this
  pass):** n=105 4–5-year-olds, pre/post PALS-K (validated early-literacy assessment) over
  9 weeks. Total PALS-K score rose from **43.02 → 55.21** (both p<.001 on every subscore:
  rhyme awareness, beginning-sound awareness, lower-case letter recognition, letter-sound
  recognition, spelling, concept-of-word). Dosage mattered: **cumulative hours in-app
  significantly predicted post-test score** (B=0.11, p=.006) even controlling for parent
  education, books-in-home, and kindergarten days; the relationship was **non-linear** —
  high-frequency users (≥16 hrs over 9 weeks, ≈1.8 hrs/week) scored near the *midyear*
  kindergarten benchmark, while low users (≤8 hrs) tracked the *fall* benchmark. Average
  usage was 13.15 hrs over 9 weeks (~1.5 hrs/week, ~13 min/day if daily). **Joint
  parent-child engagement did NOT significantly add to the model** (B=0.06, p=.12) once
  solo app-hours were controlled — i.e. parent co-play didn't measurably boost literacy
  gains beyond child app-time alone, though it likely still matters for younger/pre-reader
  engagement and enjoyment (not measured here). Children's **interest/motivation for
  reading** and **confidence in reading** both rose significantly pre→post (self-report via
  caregiver survey, exploratory/unvalidated confidence measure — EDC flags this
  explicitly as an unvalidated, exploratory instrument).
- **Streaks and rewards — evidence of benefit AND harm, both real:**
  - *Benefit:* Duolingo's own whitepaper cites Silverman & Barasch (2022), "On or Off Track:
    How (Broken) Streaks Affect Consumer Decisions" (https://doi.org/10.1093/jcr/ucac029), for
    streaks being "inherently valuable" and motivating; leaderboards are cited (Landers,
    Bauer & Callan 2017) as *more* effective than "do your best" goals in gamified-learning
    studies.
  - *Harm (independent, non-Duolingo-authored sources — this is the side the whitepaper
    doesn't cover):* a cluster of critical analyses converge on the same mechanism —
    **streaks work via loss aversion / guilt, not intrinsic motivation**, and specifically
    exploit the finding that "losses feel ~2x heavier than gains" (Kahneman & Tversky
    prospect theory, as applied in a Duolingo teardown,
    https://zicozhou10.github.io/behavioral-design-hub/teardowns/duolingo/); The Decision
    Lab's "Streak Creep" analysis (https://thedecisionlab.com/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification)
    frames long streaks as eventually "weaponizing guilt... when the streak itself no longer
    compels" — i.e. the mechanic's *validity as a motivator degrades over time into pure
    anxiety*. Several of these sources are practitioner blogs/critiques rather than
    peer-reviewed studies — **treat the "addiction"/"manipulation" framing as UNVERIFIED
    editorializing**, but the underlying psychological mechanism (loss aversion, negative
    reinforcement via guilt) is a well-established finding independently of Duolingo.
  - **Design implication for a children's reading app specifically:** Duolingo's own
    Literacy app (ABC) deliberately does **NOT** use a formal streak for its youngest users —
    the whitepaper states outright: *"For our youngest learners, in lieu of a formal streak
    the Literacy app provides a daily joke they can react to with an emoji to get them
    excited about building a habit of reading"* (§2.4 "Stay Motivated"). This is a direct,
    load-bearing design precedent: **avoid loss-aversion streak mechanics for young
    children; use a softer daily-return hook (a joke, a new story unlock, a character
    check-in) instead of a break-the-chain-and-lose-everything counter.** For adult
    heritage learners a milder streak/badge system is more defensible (see §8).
- **Bite-sized lesson structure, not big session sizing, is what Duolingo actually
  optimizes:** *"we use 'bite-sized' lessons... a lesson takes no more than a few minutes,
  which means that completing multiple lessons in a row is easily achievable and gives
  learners a higher sense of accomplishment"* (whitepaper §2.4). Applies directly: **design
  the 10-minute session as 2–4 short drill "lessons," each independently completable, rather
  than one continuous 10-minute block** — lets a child stop after 1 lesson on a bad day
  without the session feeling "failed," and lets a motivated child chain several for a
  longer session.

## 4. Feedback design

**Feature: correct/incorrect feedback across all drills, especially tap-what-you-hear and
tracing.**

- **Immediate > delayed, specifically for phonics.** The National Reading Panel's synthesis
  (2000), quoted via a teaching-practice summary: *"systematic phonics instruction coupled
  with direct, immediate corrective feedback produces significantly better reading
  outcomes"* (https://www.varsitytutors.com/practice/subjects/kpeeri/lessons/providing-immediate-feedback,
  citing NRP 2000 — the NRP report itself is in the Duolingo whitepaper's reference list as
  well, confirming it's a real, oft-cited source, not a secondary paraphrase invented by the
  blog). This directly supports immediate (not end-of-drill-batch) feedback on every
  tap/trace/dictation response.
- **Low-confidence-answer feedback retains best.** Butler, Karpicke & Roediger (2008),
  "Correcting a metacognitive error: Feedback increases retention of low-confidence correct
  responses" (cited in Duolingo whitepaper §2.5, doi:10.1037/0278-7393.34.4.918) — feedback
  is *most* valuable exactly where the learner was unsure, which argues for **not
  suppressing feedback on "easy" items** even once a learner seems fluent; a light
  confirmation ping still consolidates it.
- **Error-specific hints, not generic "wrong":** Duolingo's Literacy app design uses
  **"sound effects, color cues, and movement [to] all signal right or wrong answers"**
  rather than a blocking failure state, and provides **hints highlighting the specific
  initial letters** when a child is having trouble finding a target letter in text
  (whitepaper §3.2, "Learn in a Personalized Way": *"we also provide hints to help children
  improve, such as highlighting the initial letters in a text where a child is looking for
  words that start with a target letter"*). For this app's drills: on tap-what-you-hear, an
  error-specific hint (e.g. re-play just the confusable dot-count/position difference) beats
  a generic "wrong" buzzer.
- **Avoid anxiety-inducing feedback design generally** — the whitepaper's "Feel the Delight"
  section (§2.5) is explicit that Duolingo *actively engineers away* harsh failure signals:
  hints for receptive exercises so learners "choose their own level of scaffolding," repeated
  exposure to reduce anxiety through desensitization, and "effort-based praise and
  encouragement" (citing Dweck 2007, "The Perils and Promises of Praise" — the classic
  growth-mindset praise-the-effort-not-the-trait finding). **Concretely for tracing/dictation:
  praise the attempt/stroke ("nice try, watch the direction") rather than a pass/fail
  buzzer, especially pre-mastery.**
- **Handwriting/tracing feedback should be stroke-direction-specific, not just
  shape-match-or-not** — see §6 below for the underlying evidence that motor-sequence
  matters, not just the final shape.

## 5. Decodable text progression & fluency practice

**Feature: read-vowelled-words-with-audio drill; implied progression to sentences/stories.**

- **Urdu-specific decodable-reader precedent exists and is directly relevant:** USAID's
  Pakistan Reading Project (PRP) produced graded Urdu/Sindhi "Reading Level Materials"
  (RLMs) with **daily reading practice built around decodable, level-appropriate text**; a
  World Bank writeup (https://documents1.worldbank.org/curated/en/099010004212217887/pdf/P17425203005530e5087f50fa4754b643d3.pdf)
  cites the program directly: *"Source: Translated from USAID Pakistan Reading Project,
  Grade 1 Urdu Lesson Plans, Week 1, Lesson 6... Practice R-6: Provide adequate time for..."*
  and reports the intervention **"increased reading fluency by 12.6 correct words per
  minute (CWPM), familiar word reading by 11.1 CWPM"** (Scribd-hosted EGRA report,
  https://www.scribd.com/document/785679880/PA00Z7MW — secondary hosting of what appears to
  be a USAID/RTI EGRA impact report; **treat the exact CWPM figures as UNVERIFIED without
  the primary RTI/USAID PDF**, but the program's existence and general approach — decodable,
  leveled Urdu/Sindhi RLMs with daily practice — is corroborated by the independent
  "Gaps analysis early grade reading material in Sindhi and Urdu" slide deck
  (https://www.slideshare.net/slideshow/gaps-analysis-early-grade-reading-material-in-sindhi-and-urdu/102155795),
  which explicitly recommends **"leveled reading and decodable text"** and flags that
  Urdu/Sindhi language should be used for comprehension assessment (i.e. don't test
  comprehension in a second language).
- **Sight words belong alongside phonics, not after it.** Fuchs et al. 2001 and a broader
  synthesis (cited in Duolingo whitepaper §3.2 "Fluency"/"Vocabulary"): *"introducing some
  sight words, especially in an integrated way with decoding instruction, is beneficial for
  young learners"* — Duolingo ABC presents sight words "along with letter-sound lessons
  (e.g. teaching the sight word 'see' just after teaching the letter-sound cue 's')."
  Directly transferable: pair each new Urdu sight word with the letter/sound the child has
  *just* learned, not as a separate late-stage module.
- **General progression pattern (National Reading Panel, foundational skill order, echoed
  in both Duolingo Literacy's curriculum and the USAID PRP materials):** phonemic awareness
  → phonics/decoding → fluency → vocabulary → comprehension, with **decodable sentences
  introduced "as soon as possible" once a few letter-sounds are secure**, not held back
  until the full alphabet is taught (whitepaper §3.2, "Phonics": *"At the early levels...
  children are guided through narrated texts... As soon as possible, they begin to read
  decodable sentences and texts primarily on their own"*). No source in this pass gives an
  exact "N words per unit before first sentence" number for Urdu specifically —
  **UNVERIFIED / open design question**: recommend piloting with a small decodable set (a
  common EGRA-literature convention is ~3–5 known letter-sounds before the first
  fully-decodable sentence) rather than treating any specific count as evidence-backed.
- **Repeated reading reliably improves fluency, with real effect sizes across many recent
  studies:** a 2025 Springer study found repeated-reading gains in correct-words-per-minute
  "generalized to untrained texts, with large effect sizes"
  (https://link.springer.com/article/10.1007/s11145-025-10744-7); a 2025 ILA/Wiley study
  ("Read Like Us") reported **+16.5 CWPM** growth, ending at 110.1 CWPM
  (https://ila.onlinelibrary.wiley.com/doi/full/10.1002/trtr.70024); the Iowa Reading
  Research Center's fluency study reported **+20.91 CWPM** for a "varied practice" repeated-
  reading condition (https://irrc.education.uiowa.edu/sites/irrc.education.uiowa.edu/files/2023-04/irrc_fluency_study_report.pdf).
  Shanahan's practitioner synthesis (https://www.shanahanonliteracy.com/blog/everything-you-wanted-to-know-about-repeated-reading)
  states plainly: *"Repeated reading usually leads to better reading performance. The
  biggest payoffs tend to be with word reading, but it also has been found to improve oral
  [fluency]."* **Design implication: a timed, visible-WPM repeated-reading drill on the
  same short passage (read it 2–3 times, watch your number go up) is one of the
  best-evidenced fluency features available** — more evidence-backed than almost any other
  single mechanic in this brief.

## 6. Handwriting / tracing on a phone

**Feature: trace-letters-on-canvas drill.**

- **Handwriting practice measurably helps letter learning, via neural/motor mechanisms
  distinct from passive viewing.** Duolingo whitepaper cites Santangelo & Graham (2016), "A
  Comprehensive Meta-analysis of Handwriting Instruction," and James (2010/2017) work
  directly for its own trace-the-character drill design: *"physical manipulation of objects
  can also help children learn... we include visual and kinesthetic activities as we
  introduce each letter, such as letter-tracing, that reinforce letter shape recognition and
  help children learn handwriting skills"* (whitepaper §3.2). Independently, Bara, James
  (2004/2010/2017) work is repeatedly cited across sources found here: *"There is growing
  evidence that handwriting training facilitates reading acquisition across cultures (Bara
  et al., 2004; James, 2010)"* (SAGE journal,
  https://journals.sagepub.com/doi/10.1177/1468798417728099); James's fMRI work is
  summarized elsewhere as showing *"experience in handwriting letters improves children's
  neural activation and connectivity in brain areas associated with visual [letter]
  processing"* (ScienceDirect, https://www.sciencedirect.com/science/article/abs/pii/S0167945721000920).
  Shanahan's literacy blog gives the most careful framing:
  https://www.shanahanonliteracy.com/blog/what-about-tracing-and-other-multi-sensory-teaching-approaches-1
  — *"handwriting is important for the early recruitment in letter processing of brain
  regions known to underlie [reading]."*
  **This is solid, converging, multi-source evidence: keep and prioritize the tracing
  drill.**
  Caveat (own conflicting finding surfaced by search, not independently verified here): one
  source paraphrases James & Engelhart as concluding *"free writing has a greater impact on
  brain development than tracing letters"* (UNI ScholarWorks,
  https://scholarworks.uni.edu/cgi/viewcontent.cgi) — i.e. producing a letter freehand from
  memory may beat tracing a fixed guide. **UNVERIFIED relative to tracing specifically**, but
  suggests a natural drill progression: **trace-with-guide first (motor pattern
  acquisition) → free-recall write-from-memory later (stronger encoding)** rather than
  tracing indefinitely.
- **Stroke-order/direction feedback design:** no source in this pass gives Urdu/Nastaliq-
  specific stroke-order guidance (**UNVERIFIED / genuine research gap** — Arabic-script
  stroke order, especially Nastaliq's diagonal baseline, is a distinct problem from Latin
  letter tracing and wasn't covered by the sources found). Recommend: (a) treat this as an
  open item needing either a calligraphy-specialist consult or direct study of existing
  Arabic-script tracing apps' stroke logic, and (b) in the meantime, give **direction-
  specific corrective feedback** (not just "off the line") when a stroke goes the wrong way,
  consistent with the general error-specific-feedback principle in §4.

## 7. Progress visualisation (learner / parent / teacher)

**Feature: not yet built, but implied ("progress" surfaces somewhere).**

- No rigorous *research* (vs. product/UI-gallery) source was found specifically on what to
  show vs. hide to each audience for a children's literacy app — searches returned mostly
  dashboard-template marketing pages (Dribbble, Bold BI, Softr), which are **not
  evidence sources** and are excluded from citation here. **Mark this whole feature area
  UNVERIFIED / needs a dedicated follow-up research pass** (ideally against HCI/ed-tech
  literature on parent-facing learning dashboards specifically, e.g. work on "actionable
  vs. anxiety-inducing" parent dashboards, which this pass did not reach).
- The one directly-relevant, evidence-backed data point available is from the Duolingo ABC
  EDC study: **parent-report interest/motivation and confidence both rose significantly**
  after 9 weeks of app use, and PALS-K subscores are reported against **age-normed
  benchmarks (fall/midyear/spring Kindergarten)** — i.e. the validated approach used in that
  study was to show a **child's score plotted against a normed benchmark band**, not a bare
  percentage or leaderboard rank, which is a defensible, evidence-adjacent design principle
  even though it's not a purpose-built dashboard-design study.

## 8. Heritage / adult learners — fastest path

**Feature: implied for adult learners of Urdu who already speak it but can't read it.**

- Direct literature on "adult heritage-language readers who already know the spoken words"
  and app design for them was **not found in usable form** in this pass — search results
  were dominated by child-heritage-bilingual studies (morphosyntactic prediction, dual
  language learners) rather than adult heritage-*literacy* shortcuts.
  **UNVERIFIED / research gap — flag for a dedicated follow-up search** using terms like
  "heritage language literacy adult L2 script transfer" or targeting SIL/UNESCO adult
  literacy program documentation directly (the SIL "Good Answers to Tough Questions in
  Mother Tongue" PDF found in this pass, https://www.sil.org/sites/default/files/files/sil_2016_good_answers_to_tough_questions_0.pdf,
  touches Urdu decodable-reader design but not adult heritage shortcuts specifically).
- **Reasoned inference (not a cited finding, state as design logic, not evidence):** the
  well-supported general literacy-science model (phonemic awareness → phonics → fluency →
  vocabulary → comprehension) exists specifically because *emergent readers* need
  vocabulary/comprehension scaffolding alongside decoding. An adult heritage speaker already
  has full oral vocabulary and comprehension in Urdu — the *only* missing skill is
  grapheme-to-phoneme mapping (letters → sounds they already know) and orthographic
  conventions (positional forms, vowel marks). A defensible design (mirroring how L2 script
  bridging works for literate adults learning a new script for a language they already
  speak, e.g. Bulgarian→Cyrillic or Serbian Latin→Cyrillic reading bridges) is: **skip
  vocabulary/comprehension drill content entirely for a "I already speak Urdu" adult track,
  and compress straight through letter-shape → positional-form → decoding → fluency**,
  cutting the sight-word/vocabulary/comprehension layers that a child-literacy curriculum
  needs. **This is inference, mark it clearly as such to the product team, not delivered as
  a cited research finding.**
- The one *related*, cited comparator: **onecourse/Duolingo's own English literacy
  products don't have a heritage-adult mode at all** — Duolingo ABC targets ages 3–8, and
  the standard Duolingo Language app teaches vocabulary+grammar from scratch. **No existing
  major product in this space was found to already solve heritage-adult-literacy fast-path
  design** — this may be a genuine product-differentiation opportunity, not just a research
  gap.

## 9. Accessibility

**Feature: implied — dyslexia-friendly settings, colour-blind-safe feedback, audio-only mode.**

- **Arabic-script dyslexia-friendly typography is an active, small research area with
  directly relevant findings:**
  - A UI-design study on Arabic-alphabet learning apps: *"A good font size for dyslexic
    children is 12pt–16pt, other than that the size is too small and too big to be
    implemented"* (ACM DL, https://dl.acm.org/doi/fullHtml/10.1145/3604571.3604584).
  - An Academia.edu paper on Arabic web accessibility for dyslexics recommends
    **increasing letter and word spacing**, and identifies **16–20pt as the preferred text
    size for better [dyslexic] readability**
    (https://www.academia.edu/17420995/Web_Design_for_Dyslexics_Accessibility_of_Arabic_Content).
  - A 2025 Taylor & Francis study on **"Mubassat,"** a purpose-built Arabic dyslexia-
    friendly typeface, evaluates its readability directly
    (https://www.tandfonline.com/doi/full/10.1080/14606925.2026.2656800) — confirms the
    field is young but active; there is **not yet a standard "Arabic OpenDyslexic"
    equivalent** the way there is for Latin script (a 2025 Taylor & Francis piece notes
    *"a lack of dyslexia-friendly typefaces designed specifically for the Arabic script,"*
    https://www.tandfonline.com/doi/full/10.1080/24735132.2025.2489179).
  - **W3C's general (script-agnostic) accessibility baseline still applies and is a hard
    standard, not a suggestion:** WCAG 2.2 Success Criterion 1.4.12, Text Spacing
    (https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html), requires content to
    remain usable with **letter spacing ≥0.12× font size, word spacing ≥0.16× font size,
    line height ≥1.5×, paragraph spacing ≥2× font size** when a user overrides these —
    directly applicable to Urdu/Nastaliq text rendering, where letter-joining behavior makes
    naive letter-spacing overrides risky (Nastaliq's diagonal, connected letterforms may
    break visually if spacing is forced without font/shaping-engine support — **flag as an
    implementation risk, UNVERIFIED how Nastaliq shaping engines handle WCAG-level spacing
    overrides**, worth a direct engineering spike rather than more literature search).
  - **Net recommendation:** since a dedicated dyslexia-friendly Nastaliq/Naskh typeface
    doesn't yet exist as a known off-the-shelf asset, the safest accessibility levers
    confirmed by sources here are: (a) **generous, user-adjustable font size (16–20pt
    baseline for body text)**, (b) **adjustable letter/word spacing within WCAG 1.4.12
    bounds**, (c) **prefer Naskh (more open, less overlapping letterforms) over Nastaliq for
    a dyslexia/accessibility mode**, consistent with the app's existing Naskh→Nastaliq
    switch — Naskh is the more legible starting script generally and this reinforces using
    it as the accessible default.
- **Colour-blind-safe feedback:** no script-specific or app-specific source found this pass;
  general best practice (not independently re-derived here, treat as standard, low-risk
  UI guidance rather than a new finding) is to pair colour feedback (green/red) with a
  redundant non-colour signal (icon, shape, sound) — this app's tap-what-you-hear and
  tracing feedback should never rely on colour alone. **Not independently sourced in this
  pass — standard WCAG guidance (1.4.1, Use of Color), not specifically re-verified here.**
- **Audio-only mode:** no dedicated source found; this is really a product/accessibility
  requirements question more than a learning-science one, and is already implicit in the
  app's design (every drill already has an audio component: hear-letter, audio on vowelled
  words, dictation). **No new evidence found either way — UNVERIFIED / not a research
  gap so much as an engineering scope question** (does the *entire* app tree remain
  navigable and completable with audio + non-visual controls only, e.g. for a blind
  learner). Flag to product as a distinct accessibility audit, not a learning-science
  question.

## 10. Measuring learning in-app without a proctor

**Feature: EGRA-style reading test drill, self-administered.**

- **This exact problem — self-administered EGRA/EGMA without a trained assessor — is an
  active, named research area, not a novel idea.** ImagineWorldwide (an NGO running
  ed-tech literacy programs) publishes a **Self-Administered EGRA/EGMA (SA-EGRA) User
  Guide** (https://www.imagineworldwide.org/wp-content/uploads/SA-EGRMA_UserGuide_Oct24.pdf)
  and a Ghana pilot analysis
  (https://ierc-publicfiles.s3.amazonaws.com/public/resources/Self-Administered+EGRA_Ghana_Additional+Analysis_0.pdf) —
  confirms the concept is real, funded, and studied at pilot scale, though this pass could
  not extract the PDF's full text (large scanned/complex PDF, exceeded readable-page limits;
  **the document's existence and title/scope is confirmed, but specific validity numbers
  from it are UNVERIFIED — recommend a targeted follow-up read of just its findings/
  validity-limitations section**).
  - Search-snippet-level detail (not full-text-confirmed) indicates SA-EGRA covers the same
    core EGRA subtasks as assessor-administered EGRA: **letter identification/recognition,
    decoding (nonword reading), oral reading fluency, listening comprehension** — per the
    Wits University EGRA Toolkit 3.0 overview
    (https://www.wits.ac.za/media/wits-university/faculties-and-schools/humanities/research-entities/unesco-chair/egra-toolkit.pdf),
    which frames EGRA's differentiator as measuring "precursor skills critical to read and
    comprehend text, such as letter identification, decoding, and listening [comprehension]."
  - The **UNESCO/UIS EGRA Toolkit Revision Recommendations**
    (https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/08/WG_GAML_17_UISAID-EGRA-Toolkit-Revision_final.pdf)
    explicitly recommend offering **"a variety of timing considerations — timed and untimed
    scoring, with and without reading stimuli"** and flag **scoring alternatives for
    second-language learners** as an open toolkit-design concern — directly relevant since
    Urdu readers in this app may be L1 or L2 speakers.
- **Tap/response-speed as a fluency proxy (letter-sound fluency without a human listener):**
  no source in this pass directly validated tap-latency as an EGRA-equivalent fluency
  measure (**UNVERIFIED / genuine gap** — this is plausible by analogy to timed
  letter-naming fluency tasks, which *are* a standard, validated EGRA subtask when
  human-scored, but converting "time-to-tap" into a validated fluency score is a
  measurement-design problem this pass didn't find literature on). Recommend treating any
  in-app tap-speed-derived fluency score as a **self-referenced progress indicator** (is
  this child getting faster than their own baseline) rather than claiming it's equivalent to
  a validated EGRA CWPM score — that equivalence would need its own validation study, not
  just implementation.
- **Core validity limitation to state plainly to product/stakeholders:** self-administered,
  unproctored reading/decoding measurement inherently loses two things a trained human
  assessor provides — (a) **correcting for the child not understanding the *task
  instructions*** (a common EGRA administration failure mode with young/first-time test-
  takers, well documented in the broader EGRA methodology literature generally, though not
  quantified in a source read in this pass), and (b) **detecting cheating/guessing patterns**
  (e.g. a child mashing the microphone button or tapping randomly to finish faster). Any
  in-app EGRA-style test should be framed to users/teachers as a **formative, low-stakes
  progress signal**, not a certified assessment-equivalent score — consistent with how the
  Duolingo ABC EDC study itself used a real proctored assessor over video call (PALS-K) for
  its actual validity claims, rather than relying on in-app analytics alone, even though it
  *did* also use in-app engagement analytics as a secondary, non-primary measure (cumulative
  hours, days used) — a useful precedent: **use in-app behavioral data (time-on-task, error
  rate, streaks of correct answers) as a secondary signal, and treat any true fluency/
  accuracy score derived without a proctor as directional, not diagnostic.**

---

## Summary: Learner Mode Spec (feature → citation)

| Feature | Design decision | Primary citation |
|---|---|---|
| Review scheduling | Leitner-style boxes at launch; consider FSRS-style (rs-fsrs) once per-item review history exists | open-spaced-repetition/awesome-fsrs; Duolingo Method whitepaper §2.3 (HLR/Birdbrain principle) |
| Review budget | ~35–60 spaced-review slots/day fits a 10-min session (estimate, not sourced) | Own calculation — UNVERIFIED exact number |
| Unit quiz gate | Keep 8/10 (80%) — matches mastery-learning convention | Bloom mastery learning; JSTOR "Learning as a Function of Time" |
| Cross-unit progression | OK to gate strictly (stricter than Duolingo Math's ungated model) but... | Duolingo Method whitepaper, Duolingo Math §"Learn in a Personalized Way" |
| Within-unit / confusable-letter drills | MUST interleave, never block | Bjork & Bjork 2019; Foster et al. 2019; ScienceDirect 2025 adaptive interleaving |
| End-of-session requeue of missed items | Resurface wrong answers at session end, not next day | Duolingo Method whitepaper §2.3 |
| Session length | 10 min is appropriate/conservative for 5–8yo attention span; structure as 2–4 short "bite-sized" sub-lessons | cnld.org age-attention benchmarks; Duolingo Method whitepaper §2.4 |
| Session frequency vs. exact daily minutes | Prioritize consistency (some practice most days) over rigid daily minute targets | EDC/Duolingo ABC report — "15-20 min 3-4x/week" guidance, min. dosage "1 hr/week" still worked |
| Streaks | Avoid loss-aversion streak counters for children; use a softer daily-return hook (joke/story unlock) | Duolingo Method whitepaper §2.4 (Literacy app's own emoji-joke design); Silverman & Barasch 2022; critical streak-psychology sources |
| Feedback timing | Immediate, every response | NRP 2000 (via Duolingo whitepaper refs) |
| Feedback specificity | Error-specific hints (highlight the differentiator), not generic wrong buzzer; praise effort not correctness pre-mastery | Duolingo Method whitepaper §3.2, §2.5; Dweck 2007 |
| Sight words | Introduce paired with the letter/sound just taught, not as a later separate module | Duolingo Method whitepaper §3.2 "Fluency"/"Vocabulary"; Fuchs et al. 2001 |
| Decodable progression | Move to decodable sentences "as soon as possible" once a few letters are secure; no fixed word-count found — pilot it | Duolingo Method whitepaper §3.2; USAID PRP Urdu RLMs (secondary source) |
| Fluency practice | Timed repeated-reading with visible WPM — one of the best-evidenced single features here | Shanahan synthesis; 2025 Springer, ILA, IRRC studies |
| Tracing | Keep and prioritize; consider trace-with-guide → free-recall-write progression | Duolingo Method whitepaper §3.2; Santangelo & Graham 2016; James 2010/2017 |
| Nastaliq stroke-order feedback | Open gap — needs a dedicated spike, not covered by sources found | UNVERIFIED |
| Progress dashboards | Show score vs. age/level-normed benchmark band, not bare percentage; deeper design research still needed | EDC/Duolingo ABC report (PALS-K benchmark bands); otherwise UNVERIFIED |
| Heritage-adult fast path | Skip vocabulary/comprehension layers; compress to shape→position→decode→fluency (reasoned inference, not directly sourced) | UNVERIFIED / inference — flag clearly to product |
| Accessibility — font/spacing | 16–20pt body text; WCAG 1.4.12 spacing bounds; prefer Naskh over Nastaliq as the accessible default | ACM DL Arabic dyslexia UI study; Academia.edu Arabic dyslexia web design; W3C WCAG 1.4.12 |
| Accessibility — colour | Never colour-only feedback | Standard WCAG 1.4.1 (not independently re-verified this pass) |
| Accessibility — audio-only | Already implicit in drill audio; needs a dedicated accessibility audit, not new learning-science research | UNVERIFIED / scope question |
| Self-administered EGRA-style test | Frame as formative/directional, not certified-equivalent; use in-app behavioral data as secondary signal only | ImagineWorldwide SA-EGRA guide (existence confirmed, detail UNVERIFIED); UNESCO/UIS EGRA Toolkit Revision Recommendations |
| Tap-speed as fluency proxy | Self-referenced progress only, not a validated CWPM-equivalent | UNVERIFIED — no validation source found |

---

## Sources (every URL opened or directly cited)

**Primary sources read in full/substantial part:**
- The Duolingo Method for App-based Teaching and Learning (Freeman, Kittredge, Wilson,
  Pajak; Duolingo Research Report, Jan 2023) —
  https://duolingo-papers.s3.amazonaws.com/reports/duolingo-method-whitepaper.pdf
- Enhancing Literacy Outcomes with Duolingo ABC (Lavigne, Kennedy, Lemieux, Salone Maxon;
  Education Development Center, Jan 2022) —
  https://duolingo-papers.s3.amazonaws.com/reports/edc-report-on-duolingo-abc.pdf

**Secondary sources cited above (search-snippet or partial-page level, listed by section):**
- https://github.com/open-spaced-repetition/awesome-fsrs
- https://expertium.github.io/Algorithm.html
- https://www.brainscape.com/academy/comparing-spaced-repetition-algorithms/
- https://gnoseed.com/algorithms/fsrs
- https://learnbook.ai/en/blog/how-fsrs-works
- https://deepwiki.com/open-spaced-repetition/rs-fsrs/5.1-forgetting-curve
- https://research.duolingo.com/
- https://www.jstor.org/stable/27539747
- https://simplitrain.com/blog/adaptive-learning/
- https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2020/01/BjorkBjorkEducatinMythChapterPublishedFormSept2019.pdf
- https://www.sciencedirect.com/science/article/pii/S1041608025001803
- https://link.springer.com/article/10.3758/s13421-019-00918-4 (Foster et al. 2019, referenced via Duolingo whitepaper bibliography)
- https://www.facebook.com/groups/936224677134174/posts/1020637565359551/ (UNVERIFIED, anecdotal)
- https://www.cnld.org/how-long-should-a-childs-attention-span-be/
- https://www.brainbalancecenters.com/blog/normal-attention-span-expectations-by-age
- https://neurolaunch.com/duolingo-addiction/
- https://satur.app/blog/duolingo-shame-streak-psychology/
- https://thedecisionlab.com/insights/consumer-insights/streak-creep-the-perils-of-too-much-gamification
- https://zicozhou10.github.io/behavioral-design-hub/teardowns/duolingo/
- https://www.varsitytutors.com/practice/subjects/kpeeri/lessons/providing-immediate-feedback
- https://journals.sagepub.com/doi/10.1177/1468798417728099
- https://www.sciencedirect.com/science/article/abs/pii/S0167945721000920
- https://www.shanahanonliteracy.com/blog/what-about-tracing-and-other-multi-sensory-teaching-approaches-1
- https://scholarworks.uni.edu/cgi/viewcontent.cgi (UNI ScholarWorks, James & Engelhart re: free writing vs. tracing — UNVERIFIED claim)
- https://www.shanahanonliteracy.com/blog/everything-you-wanted-to-know-about-repeated-reading
- https://link.springer.com/article/10.1007/s11145-025-10744-7
- https://ila.onlinelibrary.wiley.com/doi/full/10.1002/trtr.70024
- https://irrc.education.uiowa.edu/sites/irrc.education.uiowa.edu/files/2023-04/irrc_fluency_study_report.pdf
- https://www.slideshare.net/slideshow/gaps-analysis-early-grade-reading-material-in-sindhi-and-urdu/102155795
- https://documents1.worldbank.org/curated/en/099010004212217887/pdf/P17425203005530e5087f50fa4754b643d3.pdf
- https://www.scribd.com/document/785679880/PA00Z7MW (UNVERIFIED exact CWPM figures — secondary hosting)
- https://www.sil.org/sites/default/files/files/sil_2016_good_answers_to_tough_questions_0.pdf
- https://dl.acm.org/doi/fullHtml/10.1145/3604571.3604584
- https://www.academia.edu/17420995/Web_Design_for_Dyslexics_Accessibility_of_Arabic_Content
- https://www.tandfonline.com/doi/full/10.1080/14606925.2026.2656800 (Mubassat typeface study)
- https://www.tandfonline.com/doi/full/10.1080/24735132.2025.2489179
- https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html
- https://www.imagineworldwide.org/wp-content/uploads/SA-EGRMA_UserGuide_Oct24.pdf (existence/title confirmed; full-text not extracted — flagged for follow-up)
- https://ierc-publicfiles.s3.amazonaws.com/public/resources/Self-Administered+EGRA_Ghana_Additional+Analysis_0.pdf (title/existence only)
- https://www.wits.ac.za/media/wits-university/faculties-and-schools/humanities/research-entities/unesco-chair/egra-toolkit.pdf
- https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/08/WG_GAML_17_UISAID-EGRA-Toolkit-Revision_final.pdf

**Searched but explicitly excluded as non-evidence (product/marketing galleries, not cited above):**
Dribbble/Behance/Bold BI/Softr dashboard-template listings (§7 progress-visualisation
search) — excluded because they are design-inspiration catalogs, not research.

**Genuine research gaps for a follow-up pass (flagged, not answered here):**
1. Urdu/Nastaliq-specific stroke-order pedagogy and tracing-feedback design.
2. Adult heritage-Urdu-speaker literacy fast-path — direct literature, not inference.
3. Parent/teacher progress-dashboard design research specifically (HCI/ed-tech literature,
   not product galleries).
4. Full-text validity/limitations section of the ImagineWorldwide SA-EGRA guide and Ghana
   pilot analysis.
5. Exact decodable-words-per-unit counts for Urdu specifically (vs. the general "as soon as
   possible" principle found here).
