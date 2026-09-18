# Urdu Reading Course — Design and Evidence

**Goal.** Take anyone (age 5 to adult, Urdu speaker or not) from zero to reading unvowelled Nastaliq Urdu at the Pakistani grade-2 "meets standard" level (60+ correct words per minute on a grade-level passage, with comprehension).

**What "research-backed" means here.** Every design choice below names the source it rests on. The full research files are in `research/` (books, apps, script reference, pedagogy, open assets, quality bar). Where the evidence is thin, the choice is marked *inference*, not "research shows".

## 1. Decisions and the evidence behind them

| # | Decision | Evidence | File |
|---|---|---|---|
| 1 | **Synthetic phonics spine**: every unit teaches letter → sound → blend → decodable word → short sentence. No whole-word-first. | USAID Pakistan Reading Project endline: phonics-based Urdu instruction gained +12.6 correct words/min and +18 points on the benchmark vs control (NORC 2020). | `research/04_pedagogy.md` §1 |
| 2 | **Letter order = frequency-first, then shape families, joiners before non-joiners.** Unit 1 is ا ب ک ل م ن: the six letters that make the most real words fastest. | Letter shares from our own Tatoeba-Urdu count (2,851 sentences): ا 11%, ی 10%, ہ 7.5%, ے 6.3%, ک 6.2%, و 5.4%, م 5.1%, ر 5.0%, ن 4.7%, ت 3.9%, ں 3.4%, س 3.3%, ھ 2.7%, ب 2.5%, ل 2.5%. Delacy opens with ب ک ل م for the same "make words on day one" reason. No head-to-head study of letter orders exists for Urdu; this is a reasoned hybrid. | `data/tatoeba_urd_freq.json`, `research/00_quality_bar.md` §B |
| 3 | **Dot-confusable letters taught together with contrast drills** (ب ت ن ی in unit 2; پ ٹ ث in unit 3; ج چ ح خ; د ڈ ذ; ر ڑ ز ژ). Delacy deliberately spreads them apart; Alif Baa groups them. We group, because the error data says confusions do not fade on their own. | Visual-orthographic errors (dots, ligatures) are the largest sub-category of Arabic children's spelling errors and *increase* from grade 1 to grade 2 (Frontiers in Psychology 2020, PMC7497809). | `research/04_pedagogy.md` §2, §6 |
| 4 | **All positional forms in the same lesson as the letter**, and joining drills continue in every later unit. | Same source: ligature/shape errors persist without explicit practice. Alif Baa and Delacy both show the full forms table before any reading. | `research/04_pedagogy.md` §3 |
| 5 | **Short-vowel marks (zabar, zer, pesh) kept on all text through unit 10**; faded in unit 11 only after nonword decoding is demonstrated. | Diacritics improve reading speed, accuracy and comprehension at every tested Arabic-L2 level (Alhawary, Modern Language Journal 2020). | `research/04_pedagogy.md` §4 |
| 6 | **Start in Naskh (Noto Naskh Arabic), switch to Nastaliq (Noto Nastaliq Urdu) in unit 11.** Every card and word is rendered in both so the switch is a side-by-side lesson, not a surprise. *Inference*: no legibility study compares the two for beginners; Nastaliq stacks letters diagonally and moves dots, which raises visual load. Nastaliq is the real target, so it is never skipped. | `research/03_script_reference.md` §5, `research/04_pedagogy.md` §5 |
| 7 | **Ten non-joiners taught as a rule, not ten exceptions**: ا د ڈ ذ ر ڑ ز ژ و ے. | Verified against the Wikipedia letter table (blank initial/medial cells) and the Arabic six. Popular "7 non-connectors" claim is wrong. | `research/03_script_reference.md` §1 |
| 8 | **Aspirates (بھ پھ تھ…) and nūn ghunna get their own early unit (6)** rather than an appendix. | ھ is 2.7% and ں 3.4% of running text; میں ہیں ہاں کہاں are among the 20 most frequent words. | `data/tatoeba_urd_freq.json` |
| 9 | **Same-sound letters (ث ص س / ذ ز ض ظ / ت ط / ہ ح) taught late (units 8–9) as spelling, not as new sounds.** | These are Arabic-loan letters; together they are under 1.5% of running text. Books agree (Delacy units 8–10; Georgetown *Beginning Urdu*). | `research/01_books.md`, `research/03_script_reference.md` §4 |
| 10 | **Small sight-word layer (کا کی کے سے پر کہ اور ہے ہیں نے کو) alongside, not instead of, phonics.** | PRP's own mix: phonics core + supplementary sight-word cards. Also these are the top-20 corpus words. | `research/04_pedagogy.md` §1 |
| 11 | **Handwriting/tracing required for children; optional for adults.** | Handwriting beats typing for letter recognition in young children (Longcamp et al.); adult effect unconfirmed. | `research/04_pedagogy.md` §8 |
| 12 | **Two tracks**: *heritage* (speaks Urdu, can't read) and *non-speaker*. Same letters, different pace and word lists; heritage learners skip meaning drills and move to unit 11 faster. | LESSLA heritage-literacy principles and Hindi-Urdu bridge courses (course-description evidence only, weaker). | `research/04_pedagogy.md` §7 |
| 13 | **Assessment is EGRA-style**: letter-sound fluency, nonword decoding, familiar-word fluency, passage reading + 5 questions. Benchmarks: >90 cwpm exceeds, 60–90 meets, <60 below, 0 nonreader. | PRP/NORC 2020 instrument; RTI EGRA protocol. | `research/04_pedagogy.md` §9 |
| 14 | **Audio on every letter, word and sentence**, generated locally with Meta MMS-TTS Urdu (VITS) and smoke-tested by Whisper round-trip. | Delacy has no audio at all; Alif Baa's companion site is audio-first. Audio is the biggest gap in the book tradition. | `research/00_quality_bar.md`, `research/05_open_assets.md` |
| 15 | **Every drill has an answer key** and is labelled *recognition* / *production* / *dictation*. | Alif Baa's teacher-edition structure (at-home vs in-class, self-graded vs teacher-checked). | `research/00_quality_bar.md` §A |
| 16 | **Two alphabet charts**: the order we teach in, and dictionary order. | Delacy's stated principle; a learner must still be able to use a dictionary. | `research/00_quality_bar.md` §B |

## 2. Course map (13 units)

| Unit | Letters | Hours (child / adult) | New concept |
|---|---|---|---|
| 0 | — | 1 / 0.5 | direction, joining, dots, marks, Naskh vs Nastaliq |
| 1 | ا ب ک ل م ن | 3 / 1.5 | joiners vs alif; zabar zer pesh; first 20 words |
| 2 | ت ی ے | 3 / 1.5 | dot-count cluster ب ت ن ی; ی vs ے |
| 3 | پ ٹ ث | 2.5 / 1 | retroflex ٹ vs dental ت; loan letter ث |
| 4 | و ر د ہ | 3 / 1.5 | the ten non-joiners; ہ as final -a |
| 5 | س ش ج چ گ | 3 / 1.5 | toothed and bowl shapes; ک vs گ |
| 6 | ں ھ | 3 / 1.5 | aspirates, nasal vowels; top-20 words |
| 7 | ڈ ڑ ز ژ | 2.5 / 1 | retroflex ڈ ڑ; ز |
| 8 | ف ق خ غ ع ح | 3 / 1.5 | loan sounds; ع as vowel seat |
| 9 | ص ض ط ظ ذ | 2.5 / 1 | same sound, different letter |
| 10 | ء ۃ + marks + numerals | 2.5 / 1.5 | hamza, tashdīd, jazm, khaṛā zabar, iẕāfat, ۰–۹, punctuation |
| 11 | — | 3 / 2 | sight words, marks removed, Nastaliq switch, dictionary order |
| 12 | — | 1 / 1 | EGRA-style reading test |

Total ≈ 33 hours (child) / 17 hours (adult). Heavier units (2, 6, 8) get more time than lighter ones, matching Alif Baa's practice of budgeting by confusability, not by letter count.

## 3. Per-unit lesson shape

1. **Hear it** — letter name and sound audio, mouth/tongue cue in plain words.
2. **See it** — isolated letter, then the four positional forms (Naskh), then the same in Nastaliq.
3. **Tell it apart** — contrast card with its confusable siblings; "tap what you hear" drill.
4. **Join it** — build three words from letter tiles; watch the shapes change.
5. **Read it** — 20 decodable words with vowel marks, audio per word; 3 sentences.
6. **Write it** — trace the four forms (children: required; adults: optional).
7. **Dictation** — hear 5 words, write them; answer key.
8. **Check** — 10-item self-quiz; must score 8+ to unlock the next unit.

## 4. What this course does not claim

- The Naskh-first order and the heritage-track speed-up are inferences (see rows 6 and 12).
- MMS-TTS audio is machine-generated. It is intelligible (Whisper round-trip in `assets/audio/verify.json`) but it is not a Pakistani voice actor. For a paid client build, record a native speaker or use Uplift AI; see `research/05_open_assets.md` for licences (MMS is CC-BY-NC).
- No stroke-order animation exists yet; tracing uses the glyph outline as a guide. Building true stroke data is listed as a gap in `research/05_open_assets.md`.
