# Urdu Writing System — Script Reference

Compiled 2026-09-18 for the Urdu reading course. Every fact below is either cited to a source
opened during this research pass or marked **UNVERIFIED**. Primary source for the letter table,
codepoints, IPA, digraphs, vowel chart, diacritics, and iẓāfat is the English Wikipedia article
"Urdu alphabet" (raw wikitext pulled and checked directly against its cited tables, not a
paraphrase) — see Sources.

---

## 1. Full Letter Inventory

Standard teaching order (as used in Pakistani schools), 38 core letters + hamza + the
tāʼ marbūṭah variant sometimes counted as a 39th/40th letter. Romanization column gives the
Pakistan-common form (matches the ALA-LC style used in the task prompt) except where noted.

Legend: **J** = joiner (has medial + initial forms, connects to the next letter) · **NJ** =
non-joiner (only isolated + final forms; still receives a connection from the letter before it,
but never connects forward to the next letter, so text keeps flowing after it as a new
unconnected unit).

| # | Letter | Codepoint | Name (Urdu script) | Name (romanized) | IPA | English approx. | J/NJ | Shape family | Example word (word-initial) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ا | U+0627 | الف | alif | /ɑː/, /ʔ/, or silent (vowel carrier) | "a" in "father" (as ā) | NJ | alif-family | اردو *urdū* — "Urdu" |
| 2 | ب | U+0628 | بے | be | /b/ | "b" in "bat" | J | be-family | بچہ *bachcha* — "child" |
| 3 | پ | U+067E | پے | pe | /p/ | "p" in "pat" | J | be-family | پانی *pānī* — "water" |
| 4 | ت | U+062A | تے | te | /t̪/ (dental) | "t" in Spanish "tú" (soft) | J | be-family | تین *tīn* — "three" |
| 5 | ٹ | U+0679 | ٹے | ṭe | /ʈ/ (retroflex) | "t" in English "tap" (hard) | J | be-family | ٹوپی *ṭopī* — "cap" |
| 6 | ث | U+062B | ثے | s̱e (Arabic loan-only) | /s/ | "s" in "sun" | J | be-family | ثواب *s̱awāb* — "reward" (Arabic loanword) |
| 7 | ج | U+062C | جیم | jīm | /d͡ʒ/ | "j" in "jam" | J | jīm-family | جوتا *jūtā* — "shoe" |
| 8 | چ | U+0686 | چے | che | /t͡ʃ/ | "ch" in "chair" | J | jīm-family | چائے *chāʾe* — "tea" |
| 9 | ح | U+062D | بڑی حے / حائے حطی / حائے مہملہ | baṛī ḥe | /ɦ/ | breathy "h" (Arabic loan-only, no English equiv.) | J | jīm-family | حال *ḥāl* — "condition" |
| 10 | خ | U+062E | خے | k͟he | /x/ | "ch" in Scottish "loch" | J | jīm-family | خط *k͟hat̤* — "letter" |
| 11 | د | U+062F | دال | dāl | /d̪/ (dental) | "d" in Spanish "dado" | NJ | dāl-family | دن *din* — "day" |
| 12 | ڈ | U+0688 | ڈال | ḍāl | /ɖ/ (retroflex) | "d" in English "dad" | NJ | dāl-family | ڈاک *ḍāk* — "mail" |
| 13 | ذ | U+0630 | ذال | ẕāl (Arabic loan-only) | /z/ | "z" in "zoo" | NJ | dāl-family | ذائقہ *ẕāʾiqa* — "taste" |
| 14 | ر | U+0631 | رے | re | /r/ | tapped "r" | NJ | re-family | روٹی *roṭī* — "bread" |
| 15 | ڑ | U+0691 | ڑے | ṛe | /ɽ/ (retroflex flap) | flapped "d"/"r" (Urdu-Hindi specific, no English equiv.); **never begins a word** | NJ | re-family | (no word-initial example — see §1 note) |
| 16 | ز | U+0632 | زے | ze | /z/ | "z" in "zoo" | NJ | re-family | زبان *zabān* — "tongue/language" |
| 17 | ژ | U+0698 | ژے | zhe (Persian loan-only) | /ʒ/ | "s" in "pleasure" | NJ | re-family | ژالہ *zhāla* — "hailstone" |
| 18 | س | U+0633 | سین | sīn | /s/ | "s" in "sun" | J | sīn-family | سکول *skūl* — "school" |
| 19 | ش | U+0634 | شین | shīn | /ʃ/ | "sh" in "shop" | J | sīn-family | شکریہ *shukriya* — "thank you" |
| 20 | ص | U+0635 | صاد | ṣwād (Arabic loan-only) | /s/ | "s" in "sun" (emphatic in Arabic, plain /s/ in Urdu) | J | sīn-family | صبر *ṣabr* — "patience" |
| 21 | ض | U+0636 | ضاد | ẓwād (Arabic loan-only) | /z/ | "z" in "zoo" | J | sīn-family | ضرور *ẓarūr* — "certainly" |
| 22 | ط | U+0637 | طوے | t̤oʼe (Arabic loan-only) | /t̪/ | "t" — dental, merges with ت in Urdu speech | J | sīn-family | طالب *t̤ālib* — "seeker/student" |
| 23 | ظ | U+0638 | ظوے | z̤oʼe (Arabic loan-only) | /z/ | "z" in "zoo" | J | sīn-family | ظاہر *z̤āhir* — "apparent" |
| 24 | ع | U+0639 | عین | ʻain (Arabic loan-only) | /ɑː/, /oː/, /eː/, /ʔ/, /ʕ/, or silent | acts as vowel-carrier; sounds like surrounding vowel | J | ʻain-family | عمر *ʻumr* — "age" |
| 25 | غ | U+063A | غین | g͟hain (Arabic loan-only) | /ɣ/ | French "r" (uvular fricative) | J | ʻain-family | غریب *g͟harīb* — "poor" |
| 26 | ف | U+0641 | فے | fe | /f/ | "f" in "fat" | J | fe-family | فرش *farsh* — "floor" |
| 27 | ق | U+0642 | قاف | qāf (Arabic loan-only) | /q/ | uvular "k", further back than ک | J | fe-family | قلم *qalam* — "pen" |
| 28 | ک | U+06A9 | کاف | kāf | /k/ | "k" in "kite" | J | kāf-family | کتاب *kitāb* — "book" |
| 29 | گ | U+06AF | گاف | gāf | /ɡ/ | "g" in "go" | J | kāf-family | گھر *ghar* — "house" |
| 30 | ل | U+0644 | لام | lām | /l/ | "l" in "log" | J | lām-family | لڑکا *laṛkā* — "boy" |
| 31 | م | U+0645 | میم | mīm | /m/ | "m" in "mat" | J | mīm-family | ماں *māṉ* — "mother" |
| 32 | ن | U+0646 | نون | nūn | /n/, /ɲ/, /ɳ/, /ŋ/ (assimilates to following consonant) | "n" in "net" | J | nūn-family | نام *nām* — "name" |
| 33 | ں | U+06BA (word-final) / ٘ U+0658 (mid-word diacritic, usually omitted) | نون غنّہ | nūn g͟hunna | nasalization /◌̃/ | nasal vowel marker (French "-in" nasal); **never begins a word** | NJ | nūn-family | (no word-initial example — nasalizer only) |
| 34 | و | U+0648 | واؤ | wāʾo | /ʋ/ (consonant "v"); /uː/, /ʊ/, /oː/, /ɔː/ (vowel carrier) | "w"/"v" or long "oo"/"o" | NJ | wāʾo-family | وقت *waqt* — "time" |
| 35 | ہ | U+06C1 | ہے / گول ہے (gol he) / چھوٹی ہے (choṭī he) | (gol/choṭī) he | /ɦ/ initial/medial; /ɑː/ or /eː/ word-final (vowel carrier) | "h" in "hat"; word-final often silent-ish "-a"/"-e" | J | he-family | ہاتھی *hāthī* — "elephant" |
| 36 | ھ | U+06BE | دو چشمی ہے | do-chashmī he | /ʰ/ or /ʱ/ (aspiration marker only) | breath-release after the preceding consonant; **never begins a word alone** — only appears as the 2nd half of the aspirated digraphs (§below) | J | he-family | (only in digraphs, e.g. بھاری *bhārī* — "heavy") |
| 37 | ی | U+06CC | یے / چھوٹی یے (choṭī ye) | choṭī ye | /j/ (consonant "y"); /iː/ (long vowel); /ɑː/ (rare) | "y" in "yes" or long "ee" | J | ye-family | یار *yār* — "friend" |
| 38 | ے | U+06D2 | بڑی یے | baṛī ye | /eː/, /ɛː/ (vowel only, never a consonant) | long "ay"/"e" as in "day"; **never begins a word** | NJ | ye-family | (no word-initial example — vowel-only, word-final/medial) |
| — | ئ | U+0626 | ہمزہ (on choṭī ye) | hamza (ye-carrier) | /ʔ/ or silent | glottal stop / vowel-cluster break | J | hamza-family | ئل — appears mid-word, e.g. مسئلہ *masʾala* — "issue/problem" |
| — | ء | U+0621 | ہمزہ | hamza (bare) | /ʔ/ or silent | glottal stop | NJ | hamza-family | (rare word-initial; mostly medial/final, e.g. قرآن *qurʾān*) |
| — | ۃ / ة | U+06C3 / U+0629 | تاء مربوطہ | tāʼ marbūṭah (sometimes counted the 40th letter; Arabic loan-only, rare) | /-a(t)/ or replaced by گول ہے | "-ah" ending in Arabic loanwords | NJ | tā-family | زکوٰۃ *zakāt* — "almsgiving" |

**Source for the whole table above:** Wikipedia, "Urdu alphabet" §Letter names and phonemes
(cites Delacy 2003 for letter names, ALA-LC/Library of Congress romanization, and Hunterian
romanization). Codepoints verified against the article's inline Unicode/wiktionary links, cross
checked against the Unicode Arabic block chart (unicode.org/charts/PDF/U0600.pdf).

**Non-joiners, confirmed list (10 letters, not 7):** the article's own table shows blank
medial/initial-form cells for exactly these 10 letters — الف alif, دال dāl, ڈال ḍāl, ذال ẕāl,
رے re, ڑے ṛe, زے ze, ژے zhe, واؤ wāʾo, بڑی یے baṛī ye. This matches Arabic's own 6 non-joiners
(alif, dāl, ẕāl, re, ze, wāʾo — confirmed independently via Busuu/Kalimah Center Arabic-alphabet
guides) plus Urdu's 4 additions (ḍāl, ṛe, zhe, baṛī ye). **Correction to the task brief:** the
commonly cited "7 non-connectors" undercounts by 3 — the accurate figure from the Wikipedia
letter table is 10. (A Rekhta Learning Facebook post claims "nine non-connectors" — flagged
**UNVERIFIED**, not corroborated by any primary source opened in this research pass; the
Wikipedia table's own cell structure is the authoritative count used above.)

**Words that never begin with:** ں (nūn ghunna), ھ (do-chashmī he), ڑ (ṛe), ے (baṛī ye) — this
is a *separate* rule from joining behaviour (word-position restriction, not
connects-to-next-letter behaviour). Directly quoted from the Wikipedia article's footnote
(marked `citation needed` in the source itself, so treat as well-established teaching
convention rather than an independently sourced fact): "No Urdu word begins with ں, ھ, ڑ, or ے."

### Aspirated digraphs (بھ, پھ, تھ, ٹھ, جھ, چھ, دھ, ڈھ, رھ, ڑھ, کھ, گھ, لھ, مھ, نھ)

All formed by writing دو چشمی ہے (do-chashmī he, U+06BE) immediately after the base consonant.
Table below is the exact digraph list from Wikipedia §Digraphs (sourced to the ALA-LC
romanization standard):

| Digraph | Romanization | IPA | Example |
|---|---|---|---|
| بھ | bh | [bʱ] | بھاری *bhārī* — heavy |
| پھ | ph | [pʰ] | پھول *phūl* — flower |
| تھ | th | [t̪ʰ] | تھیلا *thailā* — bag |
| ٹھ | ṭh | [ʈʰ] | ٹھنڈا *ṭhanḍā* — cold |
| جھ | jh | [d͡ʒʱ] | جھاڑی *jhāṛī* — bush |
| چھ | chh | [t͡ʃʰ] | چھتری *chhatrī* — umbrella |
| دھ | dh | [d̪ʱ] | دھوبی *dhobī* — washerman |
| ڈھ | ḍh | [ɖʱ] | ڈھول *ḍhol* — drum |
| رھ | rh | [ɾʱ] | تیرھواں *tērhwāṉ* — thirteenth |
| ڑھ | ṛh | [ɽʱ] | اڑھائی *aṛhāʾī* — two and a half |
| کھ | kh | [kʰ] | کھانسی *khānsī* — cough |
| گھ | gh | [ɡʱ] | گھوڑا *ghoṛā* — horse |
| لھ | lh | [lʱ] | دولھا *dūlhā* — groom |
| مھ | mh | [mʱ] | تمھیں *tumheṉ* — to you |
| نھ | nh | [nʱ] | ننھا *nanhā* — tiny |

Note: دو چشمی ہے (U+06BE) is visually near-identical to the Arabic ه (U+0647, hāʾ) in medial
position in many fonts — a real search/encoding gotcha documented on the Wikipedia page (the
University of Chicago Hindustani dictionary example, where the two encodings produce different
search results for what looks like the same word).

---

## 2. Positional Forms — Isolated / Initial / Medial / Final

Standard Perso-Arabic cursive shaping: each *joiner* letter has up to 4 contextual glyphs; the
Nastaliq style used for Urdu print goes further, sometimes rendering more than the "standard"
3–4 forms because of its diagonal, stacked letter shapes (source: Wikipedia §Nastaliq, citing a
Columbia University positional chart).

- **Isolated** — the letter standing alone, connected on neither side (dictionary/naming form).
- **Initial** — connects forward only (word- or syllable-initial, joiner letters only).
- **Medial** — connects on both sides (joiner letters only).
- **Final** — connects backward only (receives a connection from the previous letter).
- **Non-joiners** have only isolated + final forms (2 forms total) — confirmed list of 10 in §1.
  Example: دال (dāl) — isolated د, final ـد, no medial/initial glyphs exist.

**How Unicode handles this:** Arabic-script text in Unicode is stored as *logical order*, one
codepoint per letter (e.g. plain U+062F for dāl in all contexts) — **not** one codepoint per
positional form for ordinary text. The correct positional glyph is chosen automatically by the
font's shaping engine (OpenType `init`/`medi`/`fina`/`isol` GSUB features) based on
neighboring characters, the same mechanism used for Arabic. This is why a font (Nastaliq or
Naskh) must be installed for the shapes to render correctly — the Wikipedia native-name markup
literally warns about this ("this displays in a Nastaliq/Naskh font if installed").

- **To force/display an isolated form in digital text** (e.g. in a table showing "the letter by
  itself"), the two portable tricks are:
  - **ZWJ (U+200A? — correction: Zero Width Joiner is U+200D)** placed adjacent to a letter can
    force a joined *presentation* form to render even without a real neighboring letter, useful
    for showing initial/medial shapes of a letter in isolation (i.e. writing X+ZWJ to coax the
    shaper into rendering X's initial form). This is the general Unicode mechanism for Arabic
    script and applies to Urdu the same way — general Unicode Arabic-shaping knowledge, not
    quoted verbatim from a specific Urdu source in this pass, so treat the ZWJ/ZWNJ mechanic
    itself as **UNVERIFIED against an Urdu-specific source** (it is standard Unicode behaviour,
    documented for Arabic script broadly, but this research pass did not open the Unicode
    Standard's own ZWJ/ZWNJ shaping section for Arabic to quote it directly).
  - **ZWNJ (U+200C, Zero Width Non-Joiner)** placed between two letters that would otherwise
    ligate/connect forces them to render in their *non-connecting* forms (isolated/final shapes)
    even though they are still logically adjacent letters — used in real Urdu digital text to
    stop unwanted ligatures (e.g. in some keyboard layouts for typing).
  - Alternative for a course/reference document: use the Unicode Arabic Presentation Forms-A/B
    blocks (U+FB50–FDFF, U+FE70–FEFF), which *do* encode explicit per-position glyphs (isolated/
    initial/medial/final) as separate legacy codepoints. These exist for font-compatibility and
    round-tripping with legacy 8-bit Arabic encodings — **not** meant for authoring new text, but
    they are exactly what a course table generator could use to force each individual form to
    display without relying on a shaping engine. (Wikipedia infobox cites these blocks: U+0600–
    06FF, U+0750–077F, U+FB50–FDFF, U+FE70–FEFF as the four Unicode ranges relevant to Urdu.)

- **Letters with only 2 forms** (isolated + final only) = the 10 non-joiners listed in §1.
- **Letters with all 4 forms** = every joiner letter in §1 (28 of the 38 core letters).
- **ی (choṭī ye) vs ے (baṛī ye)** are visually merged in *medial* position in many renderings —
  Wikipedia's dedicated ye table shows both letters sharing the identical medial (ـیـ) and
  initial (یـ) glyphs; they are only visually distinguishable in the **final** position (ی → ـی
  vs ے → ـے) and **baṛī ye never has an initial form** (it never starts a word, §1).
- **ہ (gol he) vs ھ (do-chashmī he)** likewise look different in isolated/initial position but
  their **medial forms are visually identical** (ـہـ vs ـھـ render the same in many fonts) —
  Wikipedia's dedicated he table documents this via a `colspan` merge on the medial-form cell.

---

## 3. Vowel System

Urdu is an **abjad-with-matres-lectionis**: the base script encodes consonants + long vowels;
short vowels are optional diacritics that are *omitted in virtually all adult/native-level
running text* (newspapers, novels, signage) and supplied only in children's primers, the Qur'an,
dictionaries, and beginner learning material. This is the single most important pedagogical fact
for a reading course: **a fluent reader is disambiguating short vowels from context and root
patterns, not from marks on the page** — Wikipedia states this directly ("short vowel diacritics
... are often omitted").

### Short vowels (diacritics on the preceding consonant, or on a placeholder ا/ع/ء at word start)

| Diacritic (Urdu name) | Arabic name | Mark | Codepoint | Sound | Example |
|---|---|---|---|---|---|
| زبر zabar | fatḥah | ◌َ (small diagonal stroke above) | U+064E | /ə/ ("a" as in "cup") | اَب *ab* — "now" |
| زیر zer | kasrah | ◌ِ (small diagonal stroke below) | U+0650 | /ɪ/ ("i" as in "sit") | اِسم *ism* — "noun" |
| پیش pesh | ḍammah | ◌ُ (small loop above) | U+064F | /ʊ/ ("u" as in "put") | اُردو *urdū* — "Urdu" |
| الٹا پیش ulta pesh | — | (inverted pesh) | (part of the same diacritic family; distinct from plain pesh) | /oː/ ("o" as in "go") | جاگو *jāgō* |

### Long vowels (consonant letters as matres lectionis — carry the vowel, are not separately marked)

| Long vowel | Carrier letter(s) | IPA | Example |
|---|---|---|---|
| ā | ا alif (plain, mid/final word) / آ alif-madd (word-initial) | /aː/ | آپ *āp* — "you" (formal); بھاگنا *bhāgnā* — "to run" |
| ī | ی choṭī ye | /iː/ | کتاب*ی* — adjectival ī ending |
| ū | و wāʾo (with pesh) | /uː/ | خوشبو *khushbū* — "fragrance" |
| e | ے baṛī ye | /eː/ | میز *mez* — "table" |
| ai | ے baṛī ye (with zabar before it) | /ɛː/ | ہے *hai* — "is" |
| o | و wāʾo | /oː/ | جاگو *jāgō* — "wake up" |
| au | و wāʾo (with zabar before it) | /ɔː/ | اور *aur* — "and" |

Full 10-vowel chart (Wikipedia §Vowels states "The Urdu language has ten vowels and ten
nasalized vowels" and gives an explicit table of a/ā/i/ī/e/ai/u/ū/o/au with their final/
medial/initial written forms):

```
a   /ə/   →  اَ (initial, zabar on alif)             — no distinct final form (short, word-final vowels don't exist in Urdu)
ā   /aː/  →  آ (initial, alif-madd) / ـَا (medial) / ـَا،ـَی،ـَہ (final — several spellings)
i   /ɪ/   →  اِ (initial, zer on alif)                — no final form
ī   /iː/  →  اِیـ (initial) / ـِیـ (medial) / ـِی (final)
e   /eː/  →  ایـ (initial) / ـیـ (medial) / ـے (final)
ai  /ɛː/  →  اَیـ (initial) / ـَیـ (medial) / ـَے (final)
u   /ʊ/   →  اُ (initial, pesh on alif)               — no final form
ū   /uː/  →  اُو (initial) / ـُو (medial+final)
o   /oː/  →  او (initial) / ـو (medial+final)
au  /ɔː/  →  اَو (initial) / ـَو (medial+final)
```

### Alif — vowel-carrier rules
- Word-initial, plain alif can represent *any* short vowel (a/i/u) depending on the diacritic it
  carries — but that diacritic is usually omitted in real text, so a learner must recognize
  اب/اسم/اردو (ab/ism/urdū) by vocabulary knowledge, not by the (absent) mark.
- Word-initial **long ā** specifically requires **آ (alif with madda above, U+0622)** — this
  distinction (plain ا vs آ) is one of the few vowel markings Urdu *keeps* even in unvocalized
  adult text, because the two are not visually or grammatically interchangeable. Example:
  آزادی *āzādī* "freedom" (mid-word plain alif in the same word: bhāgnā spelled with plain ا).

### Wāʾo — vowel/consonant dual role + the "silent wāʾo" trap
- و renders /ʋ/ (consonant "v"/"w"), or the vowels ū/u/o/au.
- **Silent wāʾo**: only after خ (k͟he), و can be unpronounced entirely — a Persian-loanword
  quirk. Example: خواب *k͟hāb* "dream" (و is silent) vs خود *k͟hud* "myself" (و = /ʊ/, "u").
  This is a specific, source-confirmed gotcha (Wikipedia §Wāʾo, citing Grierson's "Urdu Language
  Management").

### Ye — choṭī ye vs baṛī ye
- چھوٹی یے (choṭī ye, ی): consonant /j/ ("y") and long vowel /iː/ ("ī"); can begin a word.
- بڑی یے (baṛī ye, ے): vowel-only, /eː/ or /ɛː/ ("e"/"ai"); **cannot begin a word**; visually
  distinguishable from choṭī ye only in word-final position.

### The two hes — گول ہے (gol/choṭī he) vs دو چشمی ہے (do-chashmī he)
- گول ہے (ہ, U+06C1): the /ɦ/ consonant ("h") anywhere in a word; **also** word-finally renders
  the long vowel /ɑː/ ("ā") or /eː/ ("e") — i.e. a huge number of Urdu words ending visually in
  ہ are pronounced with a final "-a" or "-e" vowel sound, not literally "h". This is the fact
  behind the task brief's "ہ word-final as 'a' sound" — confirmed directly by Wikipedia's
  §"The 2 hes" section.
- دو چشمی ہے (ھ, U+06BE): pure aspiration marker /ʰ/ or /ʱ/, only used as the second element of
  the aspirated digraphs in §1 — never stands alone as a word sound.
- **Encoding trap**: ہ (U+06C1, Urdu gol he) is visually distinct from Arabic/Persian ه (U+0647)
  in isolated/initial forms but the two can render identically in some fonts/medial positions —
  documented Unicode confusable-glyph table on the Wikipedia page.

### Nasalization — نون غنّہ (nūn g͟hunna)
- Marks vowel nasalization, written **after** the non-nasal vowel form of a word.
  Example: ہَے *hai* "is" → ہَیں *haiṉ* "are/is" (respectful/plural), the ں added at the end.
- Word-final form: ں (U+06BA). Mid-word form: written identically to regular ن (nūn) but
  distinguished by a diacritic called *maghnoona* / *ulta jazm* — a superscript V above the
  letter (ن٘, diacritic U+0658) — in practice **usually omitted** in running text (per Wikipedia
  §Diacritics: "only maghnoona is used commonly in dictionaries" among the rare special
  diacritics, implying it's not default running-text practice).
- **Never begins a word** (§1).

### Other diacritics

| Name (Urdu/Persian) | Arabic name | Mark | Function |
|---|---|---|---|
| جزم jazm | sukūn | ◌ْ | marks the *absence* of a vowel — consonant cluster indicator |
| تشدید tashdīd | shaddah | ◌ّ | gemination (doubled consonant) — **never used to spell doubled consonants in verbs**, which are written out as two separate letters instead |
| کھڑی زبر khaṛī zabar | dagger alif | ◌ٰ | marks a long ā that is written without a full alif letter — found in some common Arabic loanwords |
| دو زبر do zabar | fatḥatan / tanwīn | ◌ً | an "-an" ending, found in Arabic loanwords (adverbial forms like فوراً *fauran*, "immediately") |

Rare/dictionary-only diacritics (per Wikipedia §Diacritics, sourced to a CRULP/CLE paper
"Proposal of Inclusion of Certain Characters in Unicode"): *kasrah-e-majhool*,
*fatḥah-e-majhool*, *ḍammah-e-majhool*, *alif-e-wāvī*, and others — essentially never seen
outside advanced dictionaries; not worth teaching to reading-course beginners.

**Pedagogical implication of diacritic omission**: because zabar/zer/pesh/jazm/tashdīd are
almost always left out of adult Urdu text, a reading course must teach vowel disambiguation
primarily through (a) whole-word recognition / sight vocabulary, (b) common root/pattern
recognition (especially for Arabic-loan morphological patterns), and (c) the *few* markings that
Urdu writers do reliably keep even in unvocalized text: alif-madd (آ), hamza on baṛī ye/gol he/
wāʾo, and the general presence of long-vowel letters (ا/و/ی/ے) themselves, which are never
optional the way short-vowel diacritics are.

### Hamza — the four forms and their (mostly silent) rules
- ء bare hamza (U+0621), ئ hamza-on-choṭī-ye (U+0626), ؤ hamza-on-wāʾo (U+0624), ۓ hamza-on-baṛī-
  ye (U+06D3), ۂ hamza-on-gol-he (U+06C2 or ہ+U+0654 combining hamza-above) — full inventory
  confirmed in Wikipedia's "Additional characters and variations" table.
- **In Urdu, hamza is silent in all its forms except when used as *hamzah-e-izafat*** (the iẓāfat
  connector, see below) — direct quote from Wikipedia §Alphabet footnote.
- Its main job is marking a **vowel cluster / hiatus** (two vowel sounds in sequence that must
  not merge/glide), not representing an independent consonant sound the way it does in Arabic.
- **Nastaliq legibility gotcha**: hamza in Nastaliq fonts closely resembles the two dots used in
  ت (te) and ق (qāf), unlike in Arabic/Geometric fonts where it looks more like a "2" — a
  handwriting/font-reading trap worth flagging for learners moving from Naskh-trained material
  to Nastaliq-trained material (Wikipedia §Hamza in Nastaliq).

### Iẓāfat (اضافت) — the Persian-borrowed "of" connector
Not a native Urdu vowel rule but relevant to reading real text: a short "-e-" sound links two
nouns (X-e-Y = "Y's X" / "X of Y"), written as:
- زیر (zer, ِ) under the final letter, if the first word ends in a consonant or ع (usually
  omitted in writing) — e.g. شیرِ پنجاب *sher-e-Panjāb* "the lion of Punjab"
- hamza above the final letter if the first word ends in choṭī he یا ye — ۂ/ئ/ۓ — e.g. ملکۂ
  دنیا *malikā-e-dunyā* "the queen of the world"
- a special baṛī-ye-with-hamza form (ئے) if the first word ends in a long vowel (ا or و) — e.g.
  روئے زمین *rū-e-zamīn* "the surface of the Earth"

---

## 4. Letters That Share a Sound

Pakistani Urdu speech has collapsed several historically-distinct Arabic phonemes into single
Urdu sounds — pure spelling/etymology distinctions today, not pronunciation distinctions. All
four groups below are confirmed by the per-letter IPA values already tabulated in §1 (each
letter listed shares the exact same IPA symbol in the Wikipedia letter table):

| Shared sound | Letters | Arabic-loan-only? |
|---|---|---|
| /z/ ("z") | ز (ze, native/Persian) · ذ (ẕāl) · ض (ẓwād) · ظ (z̤oʼe) | ذ ض ظ = Arabic-loan-only; ز is native/general |
| /s/ ("s") | س (sīn, native/general) · ث (s̱e) · ص (ṣwād) | ث ص = Arabic-loan-only; س is native/general |
| /t̪/ ("t", dental) | ت (te, native/general) · ط (t̤oʼe) | ط = Arabic-loan-only; ت is native/general (note: ٹ ṭe is a *separate*, retroflex sound, not part of this merger) |
| /ɦ/ ("h") | ہ (gol he, native/general) · ح (baṛī ḥe) | ح = Arabic-loan-only; ہ is native/general |

Practical reading-course implication: a learner cannot recover which of ز/ذ/ض/ظ (or س/ث/ص, or
ت/ط, or ہ/ح) a word uses purely from the sound — spelling must be memorized per word, same as
English homophone spelling (e.g. "to/too/two"). This is one of the biggest phonics-teaching
traps in Urdu and should be called out explicitly and early in the course.

### Letter frequency in running Urdu text
Sources searched during this pass (CRULP — Center for Research in Urdu Language Processing —
and CLE — Center for Language Engineering, Lahore) publish Urdu corpora (e.g. the "CLE Urdu
Digest Corpus", ~50 target words / word-sense corpus) and n-gram/keyboard-layout research, but
this research pass did **not** locate a specific, openly published letter-frequency ranking
table (i.e. "which Urdu letters are most common in running text, in order") from CRULP/CLE that
could be directly cited with numbers. **Mark this UNVERIFIED / not found** — a course wanting
letter-frequency-driven lesson ordering should either (a) generate this directly from a large
Urdu text corpus (e.g. CLE's own corpora, linked at cle.org.pk/software/ling_resources.htm) using
a simple character-count script, or (b) follow the standard pedagogical letter-introduction order
used in Pakistani primers (which is *not* frequency-ordered — it follows the traditional
alphabet/shape-family order used in §1), rather than relying on an unconfirmed frequency claim.

---

## 5. Nastaliq vs Naskh

- **Naskh**: the standard Arabic print style (horizontal baseline, roughly uniform letter
  height, used for nearly all Arabic-language print and most non-Urdu Perso-Arabic languages).
- **Nastaʿlīq**: "a Persian mixture of the Naskh and Ta'liq scripts" (direct quote, Wikipedia
  §Nastaliq) — more cursive/flowing than Naskh, became the preferred style after the Muslim
  conquest of the Indian subcontinent, and remains the dominant print style for Urdu in Pakistan
  and among Urdu writers elsewhere, even though Arabic itself is normally set in Naskh.
- **Structural differences** (from Wikipedia + general Perso-Arabic typography knowledge in this
  pass — the "more than three general forms for many letters" claim is directly sourced; the
  finer visual mechanics below are standard typographic knowledge about Nastaliq, not each
  individually re-verified against a dedicated typography paper in this pass, so treat the
  specific mechanics list as **lightly-sourced / typographically well-known rather than
  freshly cited**):
  - Diagonal, stepped baseline — words cascade down-and-right rather than sitting on one flat
    line, unlike Naskh's horizontal baseline.
  - Heavier reliance on vertical stacking of letters within a word/ligature (more forms than
    Naskh's simple isolated/initial/medial/final set, per the Columbia University positional
    chart Wikipedia cites).
  - Kashida (letter-elongation, ـــ) is used far more sparingly/differently in Nastaliq than in
    Naskh justification — Nastaliq typically relies on vertical stacking rather than horizontal
    stretching to fill a line, which is *why* Nastaliq is notoriously hard to digitally typeset
    (this is why InPage/dedicated Nastaliq rendering engines existed for years before Unicode
    Nastaliq shaping matured — general industry knowledge, not individually re-cited here).
  - Dot placement is generally similar to Naskh (differentiating letters within the same shape
    family, e.g. ب vs پ vs ت vs ث by dot count/position — see the "shape family" column in §1),
    though Nastaliq's cursive slant means dots sit at different relative positions than in Naskh.
- **Why Pakistani print uses Nastaliq**: cultural/historical continuity from Persian court
  writing traditions carried into South Asian Urdu print culture — the *Daily Jang* newspaper
  was the first Urdu paper typeset digitally in Nastaliq by computer (Wikipedia §Software),
  underscoring how central Nastaliq has been to Urdu's print identity specifically (versus
  Arabic's Naskh-first print culture).

### Free Nastaliq fonts

| Font | License | Notes |
|---|---|---|
| **Noto Nastaliq Urdu** | SIL Open Font License (OFL) | Google/Noto Project; free for personal, educational, and commercial use, no restrictions (confirmed via multiple independent font-distribution sites in this pass: serbyte.net, urdu-nigaar.com, fontmeme.com — all state OFL) |
| **Jameel Noori Nastaleeq** | "Free of charge for Urdu lovers" / free for commercial + personal use, no restrictions (per urdulabs.com and the wahibhaq/urdu-font-comparator-app FONT_LICENSES.md on GitHub) | Extremely widely used in Pakistani desktop publishing/InPage workflows |
| **Mehr Nastaliq Web** | Creative Commons license — "remix, tweak, and build upon our work even for commercial purposes, as long as you credit us" (i.e. CC-BY-style attribution required) — per mehrtype.com's own product page | Web-optimized, from Rekhta's type foundry |
| **Alvi Nastaleeq** | Free download widely distributed (urdulabs.com, urdufonts.com); **exact license terms not independently confirmed in this pass** — mark **UNVERIFIED** pending a direct license-text check on the designer's/Alvi Technologies' own site | Designed by Amjad Hussain Alvi, wide/sans-serif-flavoured Nastaliq |

---

## 6. Numerals and Punctuation

### Numerals — Extended Arabic-Indic digits (U+06F0–U+06F9)

| Digit | ۰ | ۱ | ۲ | ۳ | ۴ | ۵ | ۶ | ۷ | ۸ | ۹ |
|---|---|---|---|---|---|---|---|---|---|---|
| Value | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| Codepoint | U+06F0 | U+06F1 | U+06F2 | U+06F3 | U+06F4 | U+06F5 | U+06F6 | U+06F7 | U+06F8 | U+06F9 |

Source: r12a.io Urdu orthography notes (Unicode script-notes project) + Unicode Arabic block
chart. Note: Urdu/Persian digit *shapes* differ from the plain Arabic-Indic digits (U+0660–0669)
used in most Arabic-speaking countries — specifically the glyphs for 4, 5, 6, and 7 differ in
shape between the Arabic set and the Persian/Urdu "extended" set, per r12a.io.

### Punctuation

| Mark | Character | Codepoint | Function |
|---|---|---|---|
| Comma | ، | U+060C | phrase separator (note: mirrored orientation vs Latin comma, for RTL text) |
| Semicolon | ؛ | U+061B | clause separator |
| Full stop / sentence-final | ۔ | U+06D4 | Urdu-specific full stop (distinct from the ASCII period, which Urdu text also uses in some contexts per r12a.io — "Urdu uses a mixture of ASCII and Arabic punctuation") |
| Question mark | ؟ | U+061F | mirrored question mark for RTL text |
| Percent sign | ٪ | U+066A | Arabic percent sign |
| Date/fraction separator | ؍ | U+060D | Arabic date separator |
| Colon | : | U+003A (ASCII) | Urdu uses the plain ASCII colon, not an Arabic-specific form (per r12a.io) |

Source: r12a.io Urdu orthography script notes (r12a.github.io/scripts/arab/ur.html), cross-
checked against the Unicode Arabic block chart's own punctuation section (unicode.org/charts/
PDF/U0600.pdf).

---

## Sources (all opened directly during this research pass)

1. Wikipedia, "Urdu alphabet" — https://en.wikipedia.org/wiki/Urdu_alphabet — raw wikitext
   pulled via `action=raw` and read directly (not just the rendered-page summary) for the full
   letter table, digraph table, vowel chart, diacritics section, iẓāfat section, Nastaliq
   section, and the "additional characters and variations" (hamza forms, tāʼ marbūṭah) table.
   Primary source for essentially all codepoints, IPA values, and romanizations in this document.
2. Omniglot, "Urdu" — https://www.omniglot.com/writing/urdu.htm — confirmed Nastaliq-as-default-
   style and that nūn g͟hunna appears only word-finally; page is largely image-based so did not
   yield a separate letter table.
3. r12a.io Urdu script notes — https://r12a.github.io/scripts/arab/ur.html — numerals table,
   punctuation table (comma/semicolon/colon/full-stop/question-mark with codepoints), and the
   ASCII-vs-Arabic punctuation mixing note.
4. DuckDuckGo search results (via `.claude/hooks/ddg.py`, not individually fetched as full
   pages) used to locate and corroborate: Arabic's 6 non-joining letters (Busuu "Arabic
   Alphabet" page, Kalimah Center "Arabic Alphabet In English" page — both list alif/dal/dhal/
   ra/zay/waw as the 6 Arabic non-connectors, used here to cross-check the Urdu 10-letter
   non-joiner list derived from the Wikipedia table structure); font license claims for Noto
   Nastaliq Urdu (serbyte.net, urdu-nigaar.com, fontmeme.com), Jameel Noori Nastaleeq (urdulabs.
   com, and the FONT_LICENSES.md file in github.com/wahibhaq/urdu-font-comparator-app), Mehr
   Nastaliq Web (mehrtype.com product page), and Alvi Nastaleeq (urdulabs.com, urdufonts.com —
   license terms not independently confirmed, flagged UNVERIFIED above).
5. CLE (Center for Language Engineering, Lahore) — https://www.cle.org.pk/software/
   ling_resources.htm — located as the likely home of Urdu corpora, but no specific published
   letter-frequency ranking was found in this pass; flagged UNVERIFIED in §4.

### Explicitly UNVERIFIED items in this document
- "Nine non-connectors" (Rekhta Learning Facebook claim) — contradicts the 10-letter list
  derived directly from the Wikipedia letter table's own form-column structure; not used as the
  answer, kept only as a flagged discrepancy.
- ZWJ/ZWNJ Urdu-specific shaping mechanics — described from general Unicode Arabic-script
  shaping knowledge, not from a freshly-opened Urdu-specific or Unicode-Standard source in this
  pass.
- Fine visual mechanics of Nastaliq vs Naskh (kashida behaviour, stacking specifics) — general
  typographic knowledge, lightly sourced rather than freshly cited to a dedicated typography
  paper.
- Alvi Nastaleeq's exact license terms.
- CLE/CRULP Urdu letter-frequency data — not located; needs either direct corpus analysis or a
  more targeted search of CRULP's published papers (e.g. cle.org.pk/clt09/download/Papers/) than
  this pass performed.
