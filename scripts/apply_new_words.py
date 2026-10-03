#!/usr/bin/env python3
"""Merge data/new_words.tsv into data/units.json (idempotent) and clean the old word lists.

  python3 scripts/apply_new_words.py [--dry]

Rules (course/00_design.md + .audit/improve/e_content/BAR.md):
  * a word lives in exactly ONE unit: the later of (unit asked for, first unit whose letters decode it); a row in new_words.tsv overrides the old placement
  * no 'preview' words: a word whose letters are not all taught yet moves to the first unit that decodes it
  * madda آ / ؤ / ء count as the unit-10 hamza letter (taught there), so those words start in unit 10
  * inside a unit words are ordered by corpus frequency (Tatoeba + Wikipedia per million): common first, heavy last
  * ض romanised ẓ, ذ romanised ẕ (they were both ẕ)
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lexicon
from lexicon import norm

ROOT = lexicon.ROOT
DRY = "--dry" in sys.argv
# old words dropped: no dictionary entry and no attestation, or a non-standard spelling (replaced by a standard one in new_words.tsv)
DROP = {"نپا", "تپتا", "ٹانکا", "تکیا", "ٹب", "سؤال", "کمانی", "پیالا", "کلاس", "سن", "قورمہ", "پکوڑے", "سموسہ", "لئے", "پتا"}
GLOSS_FIX = {"پتلی": "thin (fem)", "گئے": "went (plural)", "سو": "hundred, to sleep", "ابّا": "dad (abba)", "امّی": "mum (ammī)", "کالا": "black", "پانی": "water", "آب": "water (poetic)", "پیالا": "cup", "سبک": "light (not heavy)", "کہاں": "where?", "مزا": "fun", "فلم": "movie, film", "کمال": "perfection, skill", "مان": "pride, honour", "املا": "spelling", "کل": "tomorrow, yesterday", "سو": "hundred, to sleep"}


ROMAN_EXPLICIT = {  # words whose roman missed a Perso-Arabic letter token; the scheme is in data/letters.json (name field)
    "مثال": "mis̱āl", "اکثر": "aks̱ar", "طرح": "t̤araḥ", "صرف": "ṣirf", "طرف": "t̤araf", "غلط": "g͟halat̤", "غلطی": "g͟halat̤ī", "خط": "k͟hat̤",
    "خطرہ": "k͟hat̤ra", "اضافہ": "iẓāfa", "حوصلہ": "ḥauṣla", "مذاق": "maẕāq", "ثابت": "s̱ābit",
}


def fix_roman(ur, rom):
    if norm(ur) == "سو":
        return "sau, so"
    if norm(ur) == "ننھا":
        return "nanhā"
    """One symbol per Perso-Arabic letter: ث s̱  ص ṣ  ض ẓ  ط t̤  ظ z̤  ذ ẕ  ح ḥ  خ k͟h  غ g͟h (ṭ is only ٹ, ẓ only ض)."""
    k = norm(ur)
    if k in ROMAN_EXPLICIT:
        return ROMAN_EXPLICIT[k]
    if "ض" in ur and "ذ" not in ur:
        rom = rom.replace("ẕ", "ẓ")
    if "ظ" in ur and "ض" not in ur:
        rom = rom.replace("ẓ", "z̤")
    if "ط" in ur and "ٹ" not in ur:
        rom = rom.replace("ṭ", "t̤")
    if "خ" in ur and "کھ" not in ur and "k͟h" not in rom:
        rom = rom.replace("kh", "k͟h")
    return rom


def main():
    P = f"{ROOT}/data/units.json"
    J = json.load(open(P, encoding="utf8"))
    U = {u["n"]: u for u in J["units"]}
    lex = lexicon.Lex()
    lex.use_wikidata = lex.use_platts = False
    pool = {}  # bare -> (unit, [urdu, rom, gloss, vowelled])

    def add(unit, w, override=False):
        k = norm(w[0])
        du = lex.unit_of(k)
        if du is None:
            raise SystemExit(f"non-Urdu letters in {w}")
        u = max(unit, du)
        w = [w[0], fix_roman(w[0], w[1]), re.sub(r"\s*\([^)]*preview\)", "", w[2]).strip(), w[3] if len(w) > 3 else w[0]]
        if k in GLOSS_FIX and unit != 99:
            w[2] = GLOSS_FIX[k]
        if k in pool and pool[k][0] <= u and not override:
            return
        pool[k] = (u, w)

    for n, u in U.items():
        for w in u["words"]:
            if norm(w[0]) not in DROP:
                add(n, w)
    for line in open(f"{ROOT}/data/new_words.tsv", encoding="utf8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = [x.strip() for x in line.split("|")]
        add(int(p[0]), [p[1], p[2], p[3], p[4]], override=True)  # the TSV is authoritative: it can also move an older word later
    by = {n: [] for n in U}
    for k, (u, w) in pool.items():
        by[u].append((lex.score(k), w[0], w))
    sight = set(json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))["sight_words"])
    for n, rows in by.items():
        # sight words first inside unit 11 (they are the point of that unit); everything else by corpus frequency
        rows.sort(key=lambda r: (0 if (n == 11 and r[1] in sight) else 1, -r[0], r[1]))
        U[n]["words"] = [w for _, _, w in rows]
    print({n: len(u["words"]) for n, u in U.items()}, "total", sum(len(u["words"]) for u in U.values()))
    if not DRY:
        json.dump(J, open(P, "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print("wrote", P)


if __name__ == "__main__":
    main()
