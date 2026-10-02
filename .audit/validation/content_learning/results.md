# Content + learning-logic validation: Urdu Qaida app (v0.10.0 dev build, port 5188)

Read-only test. No app source edited, nothing committed, emulator untouched. Every number below was produced by a script in this folder (names in brackets). Where a check could not be made to work it is said so.

Coverage of the live drive (`drive_audit2.py`): a fresh child profile driven through every lesson of units 0-12 to "COURSE COMPLETE" with zero page errors. All 13 lesson kinds were exercised (letter, marks, join, blend, words, read, quiz, nonjoin, aspirates, marks2, sight, nastaliq, test). 691 choice screens recorded, 224 deliberate wrong taps with the on-screen hint captured, 110 unit-check questions inspected.

## 1. Prioritised findings

Severity: blocker = a learner cannot progress or is taught something false at scale; major = wrong/misleading for a real child, or an assessment you cannot trust; minor = polish/data hygiene.

No blocker found. The content pack is complete and the course can be finished end to end.

### Major

| # | Finding | Evidence (reproduced) | Fix |
|---|---|---|---|
| M1 | **3 of 11 aspirate play buttons are silent, and their table cells collide.** `learner.js aspirates()` builds the audio key by replacing every non `[a-z0-9]` character with `_`; the clips are named `aspirates/ṭh`, `ḍh`, `ṛh`. All three request `aspirates/_h`; the cell ids also collide (`#asp-_h`), so all three buttons land in the ṭh row. | `ui_checks.json`: row ṭh has 3 buttons, rows ḍh and ṛh have 0; clicking the three gives toast "No audio for this item". `check_content.json: aspirates_keys_requested_by_learner_js_missing_from_index`. The path lesson "Breath letters" is the only place these three are heard. | Key by index (`aspirates/${a[1]}` with the real ASCII ids) and give each row a unique id. |
| M2 | **Unit-9 Blend lesson asks "tap what you hear" with up to three identical-sounding options** (ض ظ ذ are all /z/). | Live run: target `ظو`, options `['صی','ظو','ضو','ظی']`, `ظو` and `ضو` both say "zū" (analyze_drills.json). Static pool analysis: 23.5% of rounds in this lesson contain two or more same-sound options (`sim_logic.json`). Names-based drills are unaffected (names differ). | Never put two letters of one sound class in one round, or ask the letter-name instead. |
| M3 | **Tracing is validated by pixel coverage only; direction and order are not checked, and the one direction rule gives false rejections.** | `trace_test.json`, alif: top-to-bottom, bottom-to-top and 10 random dashes all give "Coverage 92% good" (the dashes add only a note "10 strokes, aim for 1"). A perfectly straight alif drawn on the centre line, or 3 px left of it, is rejected "start on the right side" (a vertical stroke has no meaningful right/left start). For ب a pixel-exact raster fill with a 14 px brush was rejected as "stay inside", so I could not show order insensitivity for dotted letters; no claim made there. `STROKE` is text only, no animated stroke order. | Compare against a centre-line path with start point and direction; drop the right-side rule for vertical letters; show an animated arrow first. |
| M4 | **Wrong-answer hint states false dot counts.** The `DOTS` table counts ٹ ڈ ڑ as "1 dot" (they carry a small ط, no dot), ئ as 1 (hamza), and ی as 2 although the tile shows the isolated ی which has none in Urdu style. | 75 "Count the dots: X has N" hints were shown in the run; 24 (32%) were wrong against the font's own glyph decomposition: ی x7, ٹ x10, ڈ/ڑ x5, ئ x2 (`dots_truth.json`, `analyze_drills.json`). The other 33 letters in the table (ث 3, ق 2, ش 3, ژ 3, ب 1 ...) match the font. | Make DOTS a per-form table, give ٹ ڈ ڑ a "small ط" hint, drop the hint for ئ. |
| M5 | **Placement check cannot certify a unit.** Each stage draws 6 targets with replacement; pass is 5/6; it tests letter names only, never a word. | Probability some letter of a unit is never asked: unit 1 98.5%, unit 8 98.4%, unit 5 88%, unit 9 89% (`sim_logic.json`). A learner who does not know one letter of unit 1 still passes that stage 80% of the time. Live: knows 1-4 -> "Start at unit 5", units 0-4 marked passed with 0 lessons done, 96 review cards created; unit 1 asked 4 of its 6 letters (`ui_checks.json`). Knows all letters -> 61 questions, "Start at unit 11". Positive: knowing nothing stops at unit 1 after 6 questions; a pure guesser clears unit 1 0.07% of the time. | Sample without replacement so every letter is asked, require all or 90%, add 3-4 word-reading items per stage. |
| M6 | **Locked units can be opened from the Units tab; passing the check there floods Review with never-learned cards.** | Child profile: Units -> unit 5 -> one `confirm()` ("Unit 0 is not passed yet. Open unit 5 anyway?") -> full static lesson page with the check. Passing it marks unit 5 passed with 0 lessons done and `ensureCards` then created 138 due cards (letters and words of units 1-5) while Learn still shows Unit 0 "Start: Three rules" (`ui_checks.json`). `currentUnit` stays at 0 and later jumps to 6 once units 0-4 are done (gating test below). A 5-year-old taps OK. | No confirm path for the child track; `ensureCards` only for units passed in sequence. |
| M7 | **EGRA passage score assumes the whole passage was read unless the teacher taps "Mark last word reached".** No lower bound on elapsed time; comprehension ignored in the level. | Real `egra.js`, driven with a fake clock (`logic_browser.json`): child reads 12 words in 60 s and teacher marks word 12 -> 12 cwpm (correct). Same child, teacher forgets the mark -> **52 cwpm, band "sentences"**. Finish pressed at 36 s with nothing marked -> 86 cwpm, "meets standard". Formula copy: 0.2 s accidental Finish -> 3120 cwpm. Comprehension 0/5 still shows "meets standard"; the design goal states "60+ cwpm with comprehension". The flash subtasks credit whole pages of 10 (`attempted = (page+1)*10`). | Default attempted to words reached by timer; clamp seconds >= 10; require comp >= 4/5 for "meets". |
| M8 | **The reading test is contaminated by practice text.** | 4 of the 8 sentences of the assessment passage are verbatim in the unit-11 practice passage; 48 of its 52 tokens occur elsewhere in course text (`check_content.json: assessment_passage_overlap`, coverage script). A learner who finishes the course has seen the test. | Keep 2-3 unseen parallel passages out of the lesson text. |
| M9 | **Sentences break the "nothing appears that has not been taught" rule.** `check_decodable.py` only checks word lists. | 6 sentences contain untaught letters: `بلی کالی ہے` (ہ, unit 2, declared "sight word"), `میں ٹوپی لے` (ں و, declared preview), but undeclared: `ہم دور ہیں` (ں, unit 4), `شیر جنگل میں ہے` (ں, unit 5), `وہ کمرہ بڑا ہے` (ڑ, declared preview), `بھائی کھانا کھاتا ہے` (ئ, unit 6) (check_content.txt B1). Passages in units 7-9 and 11 are unvowelled although the design keeps marks through unit 10; only unit 10's passage has marks. | Extend the checker to sentences and passages; reword or declare. |
| M10 | **Language errors in sample text** (my own Urdu reading, please confirm with a native speaker). | `میں ٹوپی لے` (unit 3) is not grammatical Urdu ("I cap take"). `تین کتاب` (unit 2) should be `تین کتابیں`. `تکیا` (unit 2) is non-standard for `تکیہ`. Romanisation uses the same `ẕ` for ذ and ض (ذمہ ẕimma, ضد ẕid). Glosses `کمال "wonder"` and `مان "accept"` are loose. | Native-speaker review of the 33 sentences and 220 glosses before release. |
| M11 | **No read-aloud feedback and the speed metric rewards skipping.** | `grep` finds no `SpeechRecognition`, `getUserMedia` or `MediaRecorder` in `mobile/src`. "Read for speed" computes `words*60/seconds` from Start/Stop taps with no error count: tapping Stop after 1 s gives a "new personal best". Review is self-graded ("Got it"). | Even a crude check (record plus whisper-tiny on device, or parent taps wrong words as in EGRA mode) closes the loop. |
| M12 | **In-lesson mistakes never reach spaced repetition; there is no adaptivity.** | `gradeCard` is called from exactly one place, the self-graded Review screen (`grep gradeCard`). A letter missed 5 times in "tap what you hear" is not scheduled. `attempts` feed only the dashboard "Needs work" list, which is not wired back into the path. A failed letter check replays the same lesson. | Call `gradeCard(false)` on in-lesson misses and queue the missed items in the next lesson. |
| M13 | **Passages have no audio and the child gets no comprehension question anywhere.** | `audio_index.json` has no passage key (units 7-11 passages and the assessment passage); the Read tab shows an English gloss only. Comprehension questions exist only in the teacher EGRA and the self-test (self-marked). | Record the 6 passages; add 2 picture/tap questions per passage. |
| M14 | **Content volume is thin for the claimed end point.** | 220 words (214 unique), 33 sentences, 5 passages (23-40 words). Total running text a learner reads in the whole path: **272 words**. The final assessment passage is 52 words; only 63% of its tokens are taught words; 17 word types (inflected verbs like رہتا چلتا جاتے دیکھتے پیتے, ایک, ساتھ, پاس, واپس) are never taught as words. Words per unit are a flat 20 for every unit 1-11 regardless of letters introduced (2 letters in unit 6, 6 in unit 8). | Add 10+ decodable passages of 40-120 words, one per unit from unit 5, and a fluency lane that repeats known text. |

### Minor

| # | Finding | Evidence | Fix |
|---|---|---|---|
| m1 | "Tap what you hear" opens with six unlabelled live-looking tiles; the first tap only starts round 1 (not graded, no audio before it). | `tell_first_tap.json`: status empty, 6 tiles; first tap -> "Round 1/10", 0 attempts recorded, audio only after the tap. Same function in the path lesson. | Call `next()` on mount. |
| m2 | First letter (alif) quick check has two options per question and passes at 3/4. | 37 two-option screens in the run, all unit 1; options `ا` vs `ـا` (the same letter with a connector stroke). P(guess pass) = 31%. | Add look-alike distractors from the pool or skip the check for lesson 1. |
| m3 | Letter ۃ is listed as taught in unit 10 but has no record in letters.json (no lesson, card, audio, tracing). | `unit_letters_missing_from_letters_json: ['ۃ']`. | Add the record or remove it from the unit list. |
| m4 | 28 (letter, position) pairs show "—" instead of a real example in "Where it sits in a word"; ئ has no initial example (never starts a word in the shipped words although flagged not never_initial). | `letter_positions_without_example_word_in_lesson`. | Add words or hide the row. |
| m5 | 13 audio clips never played: numerals/0-9 (the numerals table has no play buttons) and ui/next. | check_content.txt. | Wire or drop. |
| m6 | 6 words appear in two units (کے نے دودھ مچھلی ہیں ٹھنڈا); 18 of 20 sight words equal a unit word, so their Leitner sight card overwrites the word card (same id `profile:item`), losing rom/en in the reveal. 11 preview-word glosses carry raw text like "(و comes in unit 4, preview)" which the Review reveal shows verbatim. | logic_browser.json (255 cards at unit 12 = 39 letters + 198 words + 18 sight); check_content.json. | Namespace card ids by kind. |
| m7 | Dictation: 45 of 208 eligible words contain a letter with a same-sound twin already taught (س/ث, ز/ذ/ض/ظ, ت/ط, ہ/ح): the ear cannot decide the spelling, and the only feedback is "Not yet. Listen again." | dictation_static.py. | Say which letter is wrong or limit dictation to unambiguous words. |
| m8 | Nastaliq tatweel forms look degraded: initial/medial forms in the sheet are small stubs. | forms_nastaliq_1.png (letters rendered with U+0640 as the app builds them). | Use ZWJ for Nastaliq. |
| m9 | A few audio clips are long or odd for one word (2.2-2.95 s vs ~1.2 s): syllables/swad_u, zal_u, units/u10_13, u10_15, u11_07 (ہے 2.2 s). Whisper-small (noisy on one-syllable clips) could not decode: u06_03, u09_11, u09_16, u10_07, u10_19, u03_08, u03_11. These are listening candidates, not confirmed defects. | whisper_verify.json, check_content.json. | Have a native speaker listen to these ~12. |
| m10 | Unit check prompts by romanisation and plays no audio. | Not cheatable by length: a zero-Urdu bot using only word length passes 0.0-3.5% (guess = 0.04%) (`sim_logic.json`). It does reward the roman. | Add an audio-prompted variant. |

## 2. Checks that passed

| Area | Result |
|---|---|
| Audio | 490/490 index entries have a file on disk; 490 expected keys (names 39, words 39, syllables 90, units 220, sentences 33, sight 20, aspirates 11, diacritics 12, numerals 10, ui 16) all present; 0 orphan files; 0 tiny or unplayable clips (ffprobe); manifest text equals the unit/letter text for every clip; all 90 syllable clips are CV with the right vowel letter; 0 ui keys used in code but missing. |
| Decodability | All 200 words in units 1-10 and all 20 in unit 11 decodable from letters of the same or earlier unit in the bare form; 11 exceptions are declared "preview" words. All vowelled forms contain exactly the bare letters (0 mismatches). |
| Glosses | 0 blank, 0 duplicate romanisation within a unit, 0 where English equals roman; 4 same-English pairs (thin: پتلی/پتلا, prayer: دعا/صلوٰۃ, of: کا/کی/کے, was: تھا/تھی) which are legitimate gender/number pairs. |
| Letter flags | The 10 non-joiners match the data. HarfBuzz on Noto Naskh agrees with the joiner flag for all 39 letters (ں is a joiner in the font but deliberately flagged non-joiner, which matches Urdu usage). No never_initial letter starts any shipped word. |
| Rendering | 39 letters x 4 forms in Naskh and Nastaliq: 0 .notdef glyphs, also for every character used in word/sentence/passage text (tofu 0). Sheets: forms_*.png. |
| Drills | 419 audio-driven choice screens: the correct tile is present exactly once, no duplicate tiles, `data-right` equals the clip played in every case. 163 quick-check questions: the target is present exactly once (7 flagged by my harness were mis-parses; the letter is on screen once). 110 unit-check questions: correct word exactly once, 0 duplicates. |
| Dictation | 15/15 correct spellings accepted, 15/15 near-misses (swapped letters) rejected, units 1, 5, 10; every spellable word can be typed on the tile keyboard (208/208). |
| Gating | Unit check passes at exactly 8/10 (7 fails, 8 passes), pass is sticky, a failed check offers "Try again" with a new question set, `currentUnit` never advances past an unpassed unit. |
| Leitner | Boxes 2,4,8,16,16 days after correct answers; a wrong answer from box 5 returns to box 1 due in 1 day; due list ordered box then due date; 40 mixed grades left 49/49 cards; `ensureCards` is idempotent; every card resolves to an audio clip (0 unresolved at unit 12). |
| Days practised | 5 attempts over 3 calendar days (including a 23:59 / 00:01 pair) -> 3. |
| EGRA | Correct when the teacher marks the last word (12 cwpm); stop rule after 10 wrong ends the subtask at 0; PRP band thresholds read from code as 60 meets / >90 exceeds (not separately driven); results save. |
| Whisper round trip (small, CPU, noisy) | words 39 mean 0.88, units 220 mean 0.88 (166 >= 0.8), sentences 33 mean 0.96, sight 20 mean 0.94; 33/33 sentences >= 0.8. |

## 3. Learning-design gap analysis

Evidence base: `course/00_design.md`, research 05 and 11, and the code. Impact is for a 5-10 year old's reading progress; effort is solo-developer.

| Capability | Status | Detail | Impact | Effort |
|---|---|---|---|---|
| Letter-sound mapping | Partial | Every "sound" clip is the letter NAME (names/alif ...). No isolated phoneme, so synthetic phonics happens only at consonant+long-vowel syllables. | High | Medium (record 39 phoneme clips) |
| Blending | Has | CV syllables (3 long vowels) then CVC words via build-the-word. M2 breaks it for unit 9. No short-vowel (zabar/zer/pesh) blending drill after unit 1, no onset-rime. | High | Low-Med |
| Phonemic awareness | Missing | No rhyme, first/last-sound, or segmenting tasks without print. | Med-High for non-readers | Medium |
| Word reading / decoding | Has | 20 words per unit with audio, build, dictation. | High | - |
| Fluency with timing | Partial | Self-timed Start/Stop, no accuracy, no repeated-reading loop with targets; EGRA is teacher-only. | High | Medium |
| Read-aloud feedback / speech recognition | Missing | No microphone code at all (M11). | Very high | High (on-device ASR for Urdu is weak; a parent-taps-wrong-words mode is cheap) |
| Comprehension | Missing for the child | Only teacher EGRA / self-test; passages carry an English gloss, not questions (M13). | High from unit 7 | Low-Med |
| Vocabulary | Partial | English gloss and audio per word; no pictures, no in-sentence use, glosses unchecked by a native speaker (M10). | Med | Medium |
| Handwriting / stroke order | Partial | Tracing with a start dot and text hint; coverage only (M3). No stroke data; the design admits this. | Med (age 5-7 high) | High |
| Spaced repetition | Partial | Correct Leitner math, but self-graded and unfed by lessons (M12). | High | Low |
| Adaptive difficulty | Missing | Linear path, one fixed placement; weakness data is only displayed. | High | Medium |
| Sight words | Late | 20 high-frequency words are first drilled in unit 11 although کا ہے ہیں appear from unit 1-2 sentences. | Med | Low |
| Positional forms and dots | Has (strong) | Per-letter forms, confusable pools and dot hints, with M4 errors. | High | - |
| Assessment | Has, untrustworthy as built | EGRA structure is right; M5, M7, M8 weaken it. | High | Low-Med |
| Child-language instructions | Partial | 16 recorded Urdu prompts and an English UI; no Urdu UI strings, no Urdu on buttons, nothing for pre-readers beyond the 16 clips. | Med-High | Medium |
| Voice quality | Machine voice | ElevenLabs "Sara" for all 490 clips; no human recording; a handful of clips are long or unclear (m9). A native speaker pass is cheap. | Med | Low (listening) / Med (recording) |
| Parent guidance | Thin | A five-bullet card before letter one and a shareable text report. The report says "ask X to read the words aloud to you", which a parent who cannot read Urdu cannot check. No answer key, no audio for the parent, no "what to do when stuck". | High (parent is the feedback loop) | Low |
| Teacher mode depth | Good for assessment, thin for teaching | Roster, EGRA, class report, band histogram, parent slip, printable 3-part lesson script, CSV. No per-letter error report across a class, no grouping suggestions despite the "see Groups tab" text in egra.js. | Med | Medium |

Does the 13-unit path reach "read a simple paragraph"? To a point: a learner decodes every letter, 214 words and 272 running words, and meets one 40-word passage in unit 11. The test passage is 52 words, includes 17 untaught word types (inflected verbs), and 4 of its 8 sentences are already in unit 11. The evidence supports "can decode isolated words and short sentences with audio support"; it does not support "60 cwpm on unseen grade-2 text". Reaching that needs far more connected, decodable text and a read-aloud check.

## 4. Files
- `check_content.py` -> `check_content.json`, `check_content.txt` (static integrity: audio, decodability, glosses, flags, shaping, eligibility)
- `render_sheet.py` -> `forms_naskh_{1,2}.png`, `forms_nastaliq_{1,2}.png`
- `dots_truth.py` -> `dots_truth.json`
- `drive_audit2.py` -> `drive_audit_raw.json`, `drive_audit2.log`; `analyze_drills.py` -> `analyze_drills.json`
- `logic_browser.py` -> `logic_browser.json` (Leitner, gating, EGRA with fake clock)
- `ui_checks.py` -> `ui_checks.json` (placement, gating bypass, aspirates)
- `trace_test.py` -> `trace_test.json`; `tell_first_tap.py`; `dictation_test.py`; `dictation_static.py`; `days_test.py`
- `sim_logic.py` -> `sim_logic.json`; `whisper_verify.py` -> `whisper_verify.json`, `whisper_summary.json`

Limits: Whisper-small is unreliable on one-syllable clips, so only gross mismatches are flagged for a human listen. Urdu grammar and gloss judgements (M10) are mine and need a native check. The learner self-test screen (`learner.js test()`) was read but not driven; it has the same "whole passage counted" assumption as M7.
