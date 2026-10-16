# Urdu Qaida: pedagogy audit (reading instruction)

Judged against: systematic explicit phonics, decodable text, blending, immediate corrective feedback, retrieval and spacing, mastery gating, dual-script handling, fluency and comprehension. Evidence is from reading the code and data, plus screenshots at 412x880 (Words 1 and letter "be").

## 1. What is genuinely strong

- **Decodability is real and machine-checked.** I ran a letters-taught-so-far check over all 1,026 words, ~250 sentences and 11 passages in `data/units.json`. Zero violations, except punctuation and the Urdu digits in unit 10-11. Few apps manage this. The unit order (alif/be/kaf/lam/mim/nun first; non-joiners in unit 4; confusable same-sound letters ص ض ط ظ ذ in unit 9) is sensible.
- **The letter lesson is a proper multi-step flow** (`path.js` case 'letter'): hear it, tell-apart against look-alikes ("count the dots"), the four positional forms each shown in a real word, a judged stroke trace (body first, dots last), a CV blend, then a 4-item check. This covers Urdu joining forms, dots and trace-and-say. Wrong tiles stay marked and the right one is found by retry (`stayWrong`), so feedback is immediate and errorless-ish.
- **Misses feed spaced review, and the app is honest about its limits.** `missCard` sends any in-lesson error back to Leitner box 1. Wrong tap plays the right audio. There is no streak-loss pressure. A placement check and parent report exist. The EGRA harness (`egra.js`) measures letters, nonwords, familiar words, ORF and comprehension.

## 2. Defects, ranked by learning impact

**1. The Words and Read screens let the learner skip decoding.** (`drills.js` readIt lines 80-93; `style.css:937`; screenshot words_1.png)
Every word card shows the Urdu, a picture, the romanization, the English gloss and an audio button at once. Romanization is on by default for the child track (only heritage and the `data-rom="off"` setting hide it). The same applies to sentences: Urdu + rom + English + play, all visible. A 6-year-old reads "kām / work / hammer picture" and never has to decode کام. This is the central skill of the course, and the main drill bypasses it. Pictures here give away meaning *before* the attempt, not after.
Fix (about half a day): in `readIt`, render only the Urdu glyphs. Tap = play audio and reveal picture, rom and English with `.reveal`. Hide `.rom` for the child track, and for everyone inside lesson drills. Reuse the existing `body[data-audioonly]` blur logic but invert it: Urdu clear, supports hidden.

**2. The unit gate does not test reading.** (`drills.js:237-249`)
The prompt is "Which one says **kām** (work)?" plus a picture. That is Latin-letter matching with the answer pictured, not print to sound. The 3 distractors are random words from the unit, so most are visibly different in length, and a learner can pass by length or first letter. There is no audio. The score is only revealed on Submit, so there is no per-item corrective feedback. All 10 items come from the current unit's words, with no earlier letters.
Fix: play word audio only (no rom, no picture, no English). Choose distractors as minimal pairs: edit distance 1, or a swapped confusable (`C.by[c].confusable`), so dots and shape errors are detected. Add 2 items from earlier-unit letters (interleaving) and show right/wrong per item.

**3. No pseudo-word decoding in teaching.** (egra.js:304 vs path.js 'words')
The EGRA test measures nonwords as "the anti-memorization check", but nothing in the lessons trains them. A learner can pass by memorizing 1,026 real words from audio plus pictures. The evidence base (Ehri, Share's self-teaching hypothesis) says nonword decoding is the best indicator of generalizing to unseen words.
Fix: add a "Silly words" step to the Words lessons. Compose 4 CVCV items from the unit's taught letters + ā/ī/ū (`syllables/<L>_<v>.mp3`, 90 files, already exist), reject any in the dictionary (`data/word_evidence.json`), play the concatenated syllables as the reveal. Show Urdu only, then "tap to hear".

**4. Review is self-graded, and "Got it" never shows the answer.** (`learner.js:138-146`)
The card shows the glyph and a "Say it aloud" prompt. "Got it" grades correct with the answer never displayed; only "Not yet" reveals it. A child will always press the big green button. The Leitner boxes then fill with false successes and mastery stats (`lettersMastered`) inflate.
Fix: for letter cards, reuse `tellApart` (hear audio, choose from 4) so the app grades it. For word cards, add a "Show" step: reveal audio, rom and gloss first, then "I was right / not yet".

**5. Review volume will drown the learner.** (`session.js ensureCards` line 12, `dueCards`)
Every word of every passed unit becomes a card, all box 1 and due immediately. By unit 5 that is ~420 word cards plus letters, due at once; the full course is 1,026. The session takes 12 sorted by box and due time, which is effectively arbitrary since they are all identical. At 12 per day a unit's worth takes weeks to churn, and most cards are low-value words. It looks like review but is not targeted at the weak items.
Fix: create cards only for letters, plus words a learner misses (`missCard` already does this) or a sample of 8 per unit. Stagger initial `due` (`now + i*3h`). Cap new cards at ~6 per session. Sort letters and recently-missed first.

**6. The vowel-mark cliff at unit 11.** (`learner.js:20` `marks = ... && unitN <= 10`)
Marks are fully on units 1-10, then fully off from unit 11 (96-word passages unmarked). There is no fade, and nothing teaches how to guess the short vowel of an unmarked word. Best practice (and Rekhta-style graded readers) uses staged removal.
Fix: units 8-10 show marks only on words that are ambiguous without them (or only on words the learner missed before). Add a "peek" tap on unmarked words in unit 11.

**7. The Read lesson has no comprehension, no timing, and the translation is on screen.** (`path.js` case 'read')
It renders sentences with rom + English + play, then the passage with its translation, then a "Read it twice" button. No check at all. The EGRA comprehension questions exist only in the formal test. `fluency()` (timer, WPM) lives in the old `lesson()` flow and is not reached from the path.
Fix: hide English until the learner taps. Add a 3-item "which sentence means X?" check using the existing `en` fields (no new authoring), and wire `fluency(u, box, cb, true)` as a second screen so WPM trends update.

**8. Letters are taught by name only, and the example word is not initial-sound.** (`path.js` letter intro; audio dir has `names/` only; screenshot letter_be.png)
The child track hides the IPA (`profile.track==='child' ? ''`). The child hears "be", never /b/. The example for ب is "اب ab · now", where ب is final. For names like عین, ح, ں this separates name from sound. Duolingo ABC and Khan Kids teach the sound with an initial-position example.
Fix: in the `ex` selection pick a word where the letter is first (`w.ur[0]===L.ch`) when one exists (بابا for ب). Add sound clips (`sounds/<id>.mp3` via the existing `el_audio.py`) and play name then sound then the word.

**9. Mastery gates restart rather than remediate.** (`path.js` check screen and quiz fail)
A failed 3/4 letter check only offers "Do the lesson again" (all 6 screens), with no Continue. A failed unit quiz says "Go back to Words 1 and 2" but just reopens the same quiz. No targeted reteach of the missed items, no soft pass. This blocks motivated and stuck learners alike.
Fix: on fail, build a 3-5 item remedial set from the `attempts` rows of that lesson/unit (missed items), then retest. After 2 fails, offer "Continue anyway", seed the missed items into review, and flag the unit as shaky.

**10. Writing stops at single letters; vocabulary strain in unit 1.**
The trace is judged for letters only (`writeIt`); words are only dictated with tiles. Unit 1 (6 letters, 48 words) includes امکان, ناممکن, املا, مکمل, ممکن and sentences like "نمک کا مالک"; these are decodable but not meaningful to a 5-10-year-old. Only 760 of 1,026 words have pictures.
Fix: trace one joined word per lesson (reuse `judgeTrace` with a per-word reference); in unit 1 prefer high-frequency child words (بابا, نانا, کام, نام, کل, اب) and cut the abstract ones from lesson drills.

## 3. Three quick wins (under 1 day each)

1. **Hide rom, English and picture until tap** in `readIt` and the quiz (defect 1 + the quiz part of 2). About 20 lines of JS/CSS and the biggest decoding gain.
2. **Make Review "Got it" show the answer first** (defect 4): a Show button that reveals audio, rom and gloss before the grade buttons appear.
3. **Pick an initial-position example word** in the letter intro (defect 8), and cap the card flood by staggering `due` and capping new cards per session (defect 5, two-line change in `ensureCards`).
