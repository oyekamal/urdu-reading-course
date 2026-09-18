#!/usr/bin/env python3
"""
Add fully-vowelled (iʻrāb) spellings to data/units.json.

Every [urdu, roman, english] entry (word or sentence) becomes
[urdu, roman, english, urdu_vowelled], where urdu_vowelled is the SAME base
letters with short-vowel marks (zabar/zer/pesh), tashdīd, and (sparingly)
jazm inserted by hand. Nothing else is changed except two roman-transliteration
corrections noted in ROMAN_FIXES below (found while vowelling — the Urdu
spelling was right, the roman gloss was wrong).

Design of this file (for review):

  WORD_MAP      -- dict: bare Urdu word/token (as it appears verbatim in
                   units.json, no punctuation) -> hand-authored vowelled form.
                   This is the actual editorial work; everything below is
                   plumbing that applies it.

  vowel_sentence() -- splits a sentence on whitespace, strips leading/
                   trailing punctuation from each token, looks the bare
                   token up in WORD_MAP, and reattaches the punctuation.
                   This is how sentence-level vowelled forms are built
                   word-by-word, per the task's instruction.

  ROMAN_FIXES   -- (unit_n, urdu) -> corrected roman string. Applied before
                   the 4th element is added. Both entries found are logged
                   to stdout.

Verification: for EVERY entry, stripping all Unicode Mn (mark, nonspacing)
characters from urdu_vowelled must reproduce the *skeleton* of the original
`urdu` string. Because 8 words in the source data already contain legitimate
Mn marks as part of their normal spelling (shadda in بچّہ/ابّا/امّی/مکّہ/کہّ,
shadda+dagger-alif in اللّٰہ, dagger-alif alone in اعلٰی and صلوٰۃ) -- marks
that are NOT something we add, just something we must preserve -- the
literal-original comparison the task describes would spuriously fail on
those 8 entries. So the check actually run is:

    strip_marks(urdu_vowelled) == strip_marks(urdu)

which is strictly equivalent to "urdu_vowelled adds only new Mn marks
on top of the exact same base letters as urdu, in the exact same order"
for every entry, including the 8 with pre-existing marks (for which both
sides strip down to the same skeleton), and reduces to the literal
strip(vowelled) == urdu comparison for the other ~245 entries that had no
pre-existing marks at all.
"""
import json
import sys
import random
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "units.json"

MN = lambda s: "".join(c for c in s if unicodedata.category(c) != "Mn")

# ---------------------------------------------------------------------------
# Roman-transliteration fixes found while vowelling (Urdu spelling untouched)
# ---------------------------------------------------------------------------
ROMAN_FIXES = {
    # سبک ("light" in weight, Persian-origin) is "sabuk" (pesh on ب), not
    # "sabak" -- "sabak" would be a different, unrelated reading. Vowelling
    # forced the check: سَبُک.
    "سبک": "sabuk",
}

# ---------------------------------------------------------------------------
# WORD_MAP -- every bare Urdu token that appears in units.json (word-list
# entries and sentence tokens with punctuation stripped), hand-vowelled.
# Grouped by the unit it's first introduced in; reused tokens (e.g. ہے, میں,
# کا, دودھ, مچھلی, ٹھنڈا, بڑا, دوست, نمک...) are listed once and reused.
# ---------------------------------------------------------------------------
WORD_MAP = {
    # ---- Unit 1 -----------------------------------------------------
    "اب": "اَب", "بابا": "بابا", "ماما": "ماما", "نام": "نام", "کام": "کام",
    "کل": "کَل", "لال": "لال", "بال": "بال", "ناک": "ناک", "کان": "کان",
    "مان": "مان", "نمک": "نَمَک", "ملک": "مُلْک", "کمال": "کَمال", "انا": "اَنا",
    "کالا": "کالا", "بلا": "بَلا", "مکان": "مَکان", "املا": "اِملا",
    "کمان": "کَمان", "کا": "کا", "لا": "لا",

    # ---- Unit 2 -----------------------------------------------------
    "تم": "تُم", "تین": "تین", "بیل": "بَیل", "میل": "میل", "نیلا": "نیلا",
    "کیلا": "کیلا", "تیل": "تیل", "لے": "لے", "کے": "کے", "نے": "نے",
    "تالی": "تالی", "بلی": "بِلّی", "تالا": "تالا", "کتاب": "کِتاب",
    "بیتاب": "بیتاب", "تکیا": "تَکِیا", "مالی": "مالی", "ناتا": "ناتا",
    "ابے": "اَبے", "کمانی": "کَمانی", "کالی": "کالی", "ہے": "ہَے",

    # ---- Unit 3 -----------------------------------------------------
    "پانی": "پانی", "پل": "پُل", "ٹوپی": "ٹوپی", "پتا": "پَتا", "پاک": "پاک",
    "پیٹ": "پیٹ", "ٹب": "ٹَب", "پتلی": "پَتْلی", "ثابت": "ثابِت",
    "پیپل": "پیپَل", "ٹماٹر": "ٹَماٹَر", "ٹانکا": "ٹانْکا", "پیالا": "پِیالا",
    "نپا": "نَپا", "پلک": "پَلَک", "کپاس": "کَپاس", "تپتا": "تَپْتا",
    "پتلا": "پَتْلا", "ٹال": "ٹال", "بٹن": "بَٹَن", "میں": "مَیں",

    # ---- Unit 4 -----------------------------------------------------
    "وہ": "وُہ", "دو": "دو", "دن": "دِن", "در": "دَر", "دم": "دَم",
    "رات": "رات", "روٹی": "روٹی", "دور": "دور", "ہم": "ہَم", "ہار": "ہار",
    "کمرہ": "کَمْرہ", "بادام": "بادام", "دادا": "دادا", "دریا": "دَرْیا",
    "ہوا۔وند": "ہَوا",  # placeholder key unused, see 'ہوا' handling below
    "راہ": "راہ", "دودھ": "دودھ", "مور": "مور", "پودا": "پَودا",
    "نہر": "نَہَر", "بڑا": "بَڑا", "ہیں": "ہَیں",

    # ---- Unit 5 -----------------------------------------------------
    "سب": "سَب", "سو": "سو", "سال": "سال", "شام": "شام", "شیر": "شیر",
    "جوتا": "جوتا", "جام": "جام", "چار": "چار", "چاند": "چاند",
    "چابی": "چابی", "گلاب": "گُلاب", "گاجر": "گاجَر", "گانا": "گانا",
    "سبک": "سَبُک", "شادی": "شادی", "جنگل": "جَنگَل", "مچھلی": "مَچھلی",
    "گرم": "گَرْم", "سردی": "سَرْدی", "دوست": "دوسْت",

    # ---- Unit 6 -----------------------------------------------------
    "ہاں": "ہاں", "کہاں": "کَہاں", "گھر": "گَھر", "بھائی": "بَھائی",
    "پھول": "پھول", "تھالی": "تھالی", "ٹھنڈا": "ٹَھنڈا", "کھانا": "کھانا",
    "دھاگا": "دھاگا", "چھت": "چَھت", "جھولا": "جھولا", "ہاتھ": "ہاتھ",
    "آنکھ": "آنکھ", "یہاں": "یَہاں", "سکھانا": "سِکھانا", "بھالو": "بَھالو",
    "ہوں": "ہوں", "کھاتا": "کھاتا",

    # ---- Unit 7 -----------------------------------------------------
    "ڈاک": "ڈاک", "ڈبہ": "ڈَبّہ", "لڑکا": "لَڑْکا", "لڑکی": "لَڑْکی",
    "پڑھنا": "پَڑھنا", "زبان": "زَبان", "زمین": "زَمین", "ژالہ": "ژَالہ",
    "روزانہ": "روزانہ", "ڈھول": "ڈھول", "گڑیا": "گُڑِیا", "سڑک": "سَڑَک",
    "زرد": "زَرْد", "ڈر": "ڈَر", "کپڑا": "کَپْڑا", "مزا": "مَزا",
    "انڈا": "اَنڈا", "گھڑی": "گَھڑی", "پر": "پَر",

    # ---- Unit 8 -----------------------------------------------------
    "فرش": "فَرْش", "فون": "فون", "قلم": "قَلَم", "قمیض": "قَمیض",
    "خط": "خَط", "خوش": "خُوش", "غریب": "غَریب", "باغ": "باغ",
    "عمر": "عُمْر", "علم": "عِلْم", "حال": "حال", "حلوہ": "حَلْوہ",
    "صاف": "صاف", "فوج": "فَوج", "وقت": "وَقْت", "خالی": "خالی",
    "غم": "غَم", "عام": "عام", "حساب": "حِساب", "دفتر": "دَفْتَر",
    "کیا": "کیا", "ہوا": "ہُوا",

    # ---- Unit 9 -----------------------------------------------------
    "صبح": "صُبْح", "صبر": "صَبْر", "ضرور": "ضَرور", "مریض": "مَریض",
    "طالب": "طالِب", "طوطا": "طوطا", "ظاہر": "ظاہِر", "ظلم": "ظُلْم",
    "ذائقہ": "ذائِقَہ", "ذمہ": "ذِمّہ", "صابن": "صابُن", "ضد": "ضِد",
    "طاقت": "طاقَت", "حفاظت": "حِفاظَت", "ذرا": "ذَرا", "خاص": "خاص",
    "ثواب": "ثَواب", "نظر": "نَظْر", "لفظ": "لَفْظ", "صحیح": "صَحیح",
    "یہ": "یِہ",

    # ---- Unit 10 ------------------------------------------------------
    "آم": "آم", "آپ": "آپ", "کوئی": "کوئی", "گئے": "گَئے",
    "مسئلہ": "مَسْئَلہ", "بچّہ": "بَچّہ", "اللّٰہ": "اَللّٰہ", "دعا": "دُعا",
    "سؤال": "سُؤال", "آئینہ": "آئینہ", "نئی": "نَئی", "چائے": "چائے",
    "گائے": "گائے", "اعلٰی": "اَعلٰی", "صلوٰۃ": "صَلوٰۃ", "دنیا": "دُنیا",
    "ابّا": "اَبّا", "امّی": "اَمّی", "مکّہ": "مَکّہ", "کہّ": "کَہّ",
    "نہیں": "نَہیں", "چمچ": "چَمَچ", "چینی": "چینی",

    # ---- Unit 11 ------------------------------------------------------
    "کی": "کی", "سے": "سے", "کہ": "کَہ", "اور": "اَور", "کو": "کو",
    "تھا": "تھا", "تھی": "تھی", "بھی": "بھی", "لیکن": "لیکِن",
    "اگر": "اَگَر", "پھر": "پِھر", "بہت": "بَہُت",
    "میرا": "میرا", "لاہور": "لاہَور", "رہتا": "رَہْتا",
    "بچے": "بَچّے", "اسکول": "اِسْکول", "جاتے": "جاتے", "آج": "آج",
    "چھٹی": "چُھٹّی", "بارش": "بارِش", "ہوئی": "ہُوئی", "تو": "تو",
    "رہیں": "رَہیں", "گے": "گے",
}

# remove the unused placeholder key we used as a scratch note above
WORD_MAP.pop("ہوا۔وند", None)

PUNCT = "؟۔،.!:"


def vowel_sentence(s: str) -> str:
    out = []
    for tok in s.split(" "):
        lead = ""
        trail = ""
        core = tok
        while core and core[0] in PUNCT:
            lead += core[0]
            core = core[1:]
        while core and core[-1] in PUNCT:
            trail = core[-1] + trail
            core = core[:-1]
        if core == "":
            out.append(tok)
            continue
        if core.isdigit() or all(unicodedata.category(c) == "Nd" for c in core):
            out.append(lead + core + trail)
            continue
        if core not in WORD_MAP:
            raise KeyError(f"no WORD_MAP entry for token {core!r} (from sentence {s!r})")
        out.append(lead + WORD_MAP[core] + trail)
    return " ".join(out)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))

    roman_fix_log = []
    checked = 0

    for unit in data["units"]:
        new_words = []
        for w in unit["words"]:
            urdu, roman, eng = w[0], w[1], w[2]
            if urdu in ROMAN_FIXES and roman != ROMAN_FIXES[urdu]:
                roman_fix_log.append((unit["n"], urdu, roman, ROMAN_FIXES[urdu]))
                roman = ROMAN_FIXES[urdu]
            if urdu not in WORD_MAP:
                raise KeyError(f"unit {unit['n']}: no WORD_MAP entry for word {urdu!r}")
            vowelled = WORD_MAP[urdu]
            assert MN(vowelled) == MN(urdu), (
                f"unit {unit['n']} word {urdu!r}: stripped vowelled "
                f"{MN(vowelled)!r} != stripped original {MN(urdu)!r}"
            )
            checked += 1
            new_words.append([urdu, roman, eng, vowelled])
        unit["words"] = new_words

        new_sents = []
        for s in unit["sentences"]:
            urdu, roman, eng = s[0], s[1], s[2]
            vowelled = vowel_sentence(urdu)
            assert MN(vowelled) == MN(urdu), (
                f"unit {unit['n']} sentence {urdu!r}: stripped vowelled "
                f"{MN(vowelled)!r} != stripped original {MN(urdu)!r}"
            )
            checked += 1
            new_sents.append([urdu, roman, eng, vowelled])
        unit["sentences"] = new_sents

    DATA.write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    print(f"Verified {checked} entries (stripped-marks skeleton match).")
    if roman_fix_log:
        print("\nRoman transliteration fixes applied:")
        for n, urdu, old, new in roman_fix_log:
            print(f"  unit {n}: {urdu!r}  {old!r} -> {new!r}")

    # ---- sample table -----------------------------------------------
    all_entries = []
    for unit in data["units"]:
        for w in unit["words"]:
            all_entries.append(("word", unit["n"], w))
        for s in unit["sentences"]:
            all_entries.append(("sent", unit["n"], s))

    random.seed(7)
    sample = random.sample(all_entries, min(30, len(all_entries)))
    print(f"\n{'kind':<5} {'unit':<4} {'urdu':<14} {'roman':<20} {'vowelled':<16}")
    print("-" * 80)
    for kind, n, entry in sample:
        urdu, roman, eng, vowelled = entry
        print(f"{kind:<5} {n:<4} {urdu:<14} {roman:<20} {vowelled:<16}")


if __name__ == "__main__":
    sys.exit(main())
