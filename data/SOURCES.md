# Sources for the word, sentence and passage lists

Nothing here is copied from a textbook, a commercial worksheet or a published reader. Every Urdu sentence and passage in `data/units.json` and every comprehension question in `data/letters.json` was written for this course on 2026-10-03 (by an AI, from the course's own word list; see `data/REVIEW_NEEDED.md` for what a native speaker must still confirm). Words were chosen from open corpora and checked against open dictionaries; the evidence for each word is in `data/word_evidence.json`.

| Source | What we took | Licence | Where |
|---|---|---|---|
| Tatoeba, Urdu sentences (2,851 sentences, export of 2026-10-03) | token counts only (`data/tatoeba_urd_freq.json`, `data/tatoeba_top1000.json`); no sentence text is stored or shown | CC BY 2.0 FR, contributors credited at tatoeba.org | https://downloads.tatoeba.org/exports/per_language/urd/urd_sentences.tsv.bz2 |
| Leipzig Corpora Collection, Urdu Wikipedia 2021, 100K sentences (1.7M tokens) | word frequencies (a second, independent corpus) | CC BY 4.0 (text is Wikipedia, CC BY-SA); D. Goldhahn, T. Eckart, U. Quasthoff, LREC 2012 | https://wortschatz.uni-leipzig.de/en/download/Urdu |
| Wiktionary (English) Urdu entries, as extracted by Wiktextract | spelling, part of speech, English gloss, romanisation per headword or listed inflection; the page URL is stored per word | CC BY-SA 4.0 (Wiktionary contributors); snippets kept short | https://kaikki.org/dictionary/Urdu/ and the en.wiktionary.org page named in each record |
| J. T. Platts, *A Dictionary of Urdu, Classical Hindi, and English* (1884), digitised by DSAL, University of Chicago | second dictionary where Wiktionary lacks the word or its entry is a different word | public domain | https://dsal.uchicago.edu/dictionaries/platts/ |
| Wikidata | last resort for loan nouns (the item whose Urdu label equals the word) | CC0 | https://www.wikidata.org |

## How a word got in (`scripts/lexicon.py`)

1. It is spelt only with letters taught in its unit or earlier (madda آ, ؤ and ء count as the unit-10 hamza letter).
2. It occurs at least twice in Tatoeba plus Urdu Wikipedia combined (two independent corpora).
3. An open dictionary entry (Wiktionary headword or listed inflection, Platts, or a Wiktionary lemma of which it is a regular inflection) exists **and its English text agrees with our gloss** (loose 4-letter stem match; the check is a screen, not a proof, and the disagreements are listed in `data/REVIEW_NEEDED.md`). Wikidata alone must match the gloss to count.
4. Romanisation and vowelled form are ours (the course's scheme: ā ī ū, ṉ for ں, one symbol per Perso-Arabic letter: ث s̱, ص ṣ, ض ẓ, ط t̤, ظ z̤, ذ ẕ, ح ḥ, خ k͟h, غ g͟h, ع ʻ).
5. Placement: the later of the unit asked for and the first unit that decodes it; inside a unit, most frequent corpus words first.

Words that fail 2 or 3 were not added. Twenty old words from v0.10.0 failed them and were handled one by one (dropped when the spelling was non-standard or unattested: نپا تپتا ٹانکا تکیا کمانی پیالا ٹب سؤال; kept and flagged when they are real words that are only rare in a 100K-sentence corpus: see REVIEW_NEEDED).

## Re-running

```
python3 scripts/lexicon.py cand 6 --top 120     # candidate words whose letters are all taught by unit 6
python3 scripts/lexicon.py verify data/new_words.tsv
python3 scripts/apply_new_words.py && python3 scripts/apply_new_texts.py
python3 scripts/lexicon.py check                # writes data/word_evidence.json
python3 scripts/lexicon.py top 1000             # writes data/tatoeba_top1000.json
python3 scripts/content_metrics.py
```
Downloads are cached in `~/.cache/urc_lexicon`; Platts and Wikidata are queried once per word at about one request per second.
