# BAR: content depth for the Urdu Qaida app

Owner's complaint (Kamal): "lots of heavy words are not present in the app." Heavy = longer, harder everyday words: 4 to 6 letters, three syllables, plurals and verb forms, compounds, the harder letters and aspirates, high-frequency school / home / Pakistan words.

Measured with `python3 scripts/content_metrics.py` (baseline = `git show HEAD:data/units.json`, saved in `metrics_before.json`; after = `metrics_after.json`). Sources and licences: `data/SOURCES.md`.

## Baseline (v0.10.0 content)

| Metric | Before |
|---|---|
| Unit words | 220 (214 unique) |
| Words with 4+ letters / 5+ letters | 48.6% / 10.9% (mean 3.47 letters) |
| Words with 3+ syllables (vowel nuclei in the romanisation) / mean syllables | 5.0% / 1.62 |
| Longest word | 6 letters (2 words) |
| Sentences / passages / running words | 33 / 5 / 270 (120 in sentences + 150 in passages) |
| Units with a passage | 5 of 11 (7 to 11); units 1 to 6 have none |
| Reading-test passage | 52 tokens, 17 word types never taught as a unit or sight word, 5 of its sentences also in unit text |
| Tatoeba top-100 / 300 / 500 / 1000 real words taught as a word | 37.9% / 25.7% / 18.8% / 13.7% |
| Same, seen anywhere in course text | 48.4% / 32.6% / 24.0% / 17.4% |
| Share of all Tatoeba running tokens that are taught words | 45.6% (51.7% with text) |
| Sentences using a letter not yet taught | 6 (units 2 to 8); 11 "preview" words with an untaught letter |

## Targets and why

"Real words" in the coverage rows = the Tatoeba top-N types that are spelt with the 39 taught letters, have a Wiktionary entry (or are a regular inflection of one) and are not proper names (`data/tatoeba_top1000.json`, built by `scripts/lexicon.py top`). The raw top-1000 also holds names (ٹام ٹوم), foreign words (امریکہ جاپان) and misspellings (لئیے جائو تمھیں چاہئیے کوئ مئیری): 809 of 1000 are real words. Teaching a misspelling would be a defect, so it is not in the denominator.

| # | Target | Why this number |
|---|---|---|
| T1 | Unit words at least **700** (new at least 480); every unit 1 to 11 at least 40 | 3x the old 220 is "a child can reach real reading"; unit 1 has only 6 letters so its pool is small, later units 4 to 9 have 90 to 140 candidates each |
| T2 | 4+ letter words at least **60%** of unit words (was 48.6%) and 5+ letters at least **25%** (was 10.9%) | The original draft target (35% at 4+) is already beaten by the old list (48.6%), so it would not measure anything. Real text is shorter than a heavy-word list: only 39.6% of Tatoeba tokens and 47.2% of Wikipedia tokens have 4+ letters, 15.1% / 26.7% have 5+. A 60% / 25% list over-represents heavy words on purpose without leaving everyday speech |
| T3 | 3+ syllables at least **12%** of unit words, mean syllables at least 1.8 (was 5.0%, 1.62) | 25% would need a list of long Arabic-origin abstractions; everyday Urdu words (verb forms, plurals, family, food, school words) are mostly 2 syllables, so 12% is the honest ceiling that keeps child vocabulary |
| T4 | Running words at least **1,500** (was 270) in sentences + passages; every unit 1 to 11 has at least 10 sentences and one passage (unit 1 at least 12 words, units 7 to 11 at least 60) | The old path had no text before unit 7; the report asks for 10+ passages of 40 to 120 words |
| T5 | Real top-1000 Tatoeba words **at least 60%** seen in course text (was 17.4%); top-500 at least 80%; top-300 at least 90%; top-100 at least 94% | 60% of the top-1000 is a stretch but reachable once names, foreign words and misspellings are out. Not 100%: the tail of the list is rare forms and abstract words that a child text does not need |
| T6 | Taught words cover at least **80%** of Tatoeba running tokens (was 45.6%) | the number that decides whether a child can read a new sentence |
| T7 | Decodability: 0 undecodable words, 0 sentences or passages with an untaught letter **or an untaught word** (sight words allowed from the unit that teaches their letters), 0 preview words; madda آ ؤ ء count as the unit-10 hamza letter | the report's M9 (6 sentences with untaught letters) and the test passage's 17 never-taught types |
| T8 | Evidence: every word has Tatoeba or Wikipedia attestation (at least 2 occurrences) **and** an open dictionary entry (Wiktionary, Platts 1884, or Wikidata) whose text matches the English gloss; judgement calls go to `data/REVIEW_NEEDED.md` | "no invented words" |
| T9 | Reading test: 50 to 70 tokens (old 52), 0 word types never taught, 0 sentences shared with unit text, comprehension questions rewritten for it | M8 in the validation report; keeps the PRP grade-2 cwpm logic in `egra.js` unchanged |
| T10 | Audio: every new word, sentence and passage has a clip (judge `ok` on at least 90% of new clips, the rest marked `unverified` in `data/audio_overrides.json`); `check_content.py` reports 0 missing keys, 0 orphans, 0 undecodable words | task 4 and 6 |

## Result

Filled in at the end of the run in `ROUNDS.tsv` and the final report.
