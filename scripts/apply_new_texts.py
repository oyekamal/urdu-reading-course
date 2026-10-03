#!/usr/bin/env python3
"""Turn data/new_texts.tsv (hand-written sentences and passages) into units.json `sentences` / `passage`.

  python3 scripts/apply_new_texts.py [--check]      # --check validates and prints, writes nothing

Input lines:   S|unit|urdu|english          one sentence of that unit's Read lesson
               P|unit|urdu|english          the unit's passage (sentences separated by ۔ ؟ !)
               T|-|urdu|english             the final reading test passage
               Q|-|urdu question|answer     its comprehension questions (in order) (goes to letters.json assessment, unit text must not contain it)
An Urdu token may end in * to pick the alternate reading (see ALT: میں* = meṉ 'in', ہوا* = huā 'was').

Hard rules (all enforced here):
  * every token is a word taught in this unit or an earlier one (data/units.json), or a sight word whose letters are already taught
  * therefore every letter is taught, bare and vowelled
  * romanisation and vowelled text are assembled from the word list, so they cannot drift from it
  * no sentence repeats inside the unit text; a T passage shares no sentence with unit text
"""
import json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lexicon
from lexicon import norm

ROOT = lexicon.ROOT
PUNCT = {"۔": ".", "؟": "?", "،": ",", ":": ":", "!": "!", ".": "."}
ALT = {"میں*": ("meṉ", "مَیں"), "ہوا*": ("huā", "ہُوا"), "کل*": ("kal", "کَل")}
# sight words that are not (or not yet) unit words: roman, vowelled
SIGHT_EXTRA = {"یہ": ("yeh", "یَہ"), "اس": ("is", "اِس"), "وہ": ("woh", "وُہ"), "میں": ("maiṉ", "مَیں"), "کہ": ("keh", "کِہ")}
HAMZA_UNIT = 10


def load():
    U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))
    L = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
    return U, L


def vocab(U, L, lex):
    """token -> (unit, roman, vowelled). Sight words count from the unit that teaches their letters."""
    V = {}
    for u in U["units"]:
        for w in u["words"]:
            V.setdefault(norm(w[0]), (u["n"], w[1], w[3] if len(w) > 3 else w[0]))
    for sw in L["sight_words"]:
        k = norm(sw)
        du = lex.unit_of(k)
        if k not in V or V[k][0] > du:
            r = SIGHT_EXTRA.get(k)
            if r is None and k in V:
                r = V[k][1:]
            if r is None:
                raise SystemExit(f"sight word {sw} has no roman/vowelled")
            V[k] = (du, r[0], r[1])
    return V


def render(text, unit, V, errs):
    """-> (urdu, roman, vowelled) for a text; appends problems to errs."""
    ur, rom, vow = [], [], []
    for raw in text.split():
        m = re.match(r"^([^۔؟،:!.]+?)(\*?)([۔؟،:!.]*)$", raw)
        if not m:
            errs.append(f"cannot parse token {raw!r}")
            continue
        tok, star, punc = m.groups()
        k = norm(tok)
        if re.fullmatch("[۰-۹]+", tok):
            ur.append(tok + punc); rom.append(tok + "".join(PUNCT[c] for c in punc)); vow.append(tok + punc)
            continue
        hit = V.get(k)
        if hit is None:
            errs.append(f"u{unit}: '{tok}' is not a taught word")
            continue
        if hit[0] > unit:
            errs.append(f"u{unit}: '{tok}' is taught in unit {hit[0]}")
        r, v = (ALT[tok + "*"] if star else hit[1:])
        ur.append(tok + punc)
        rom.append(r + "".join(PUNCT[c] for c in punc))
        vow.append(v + punc)
    return " ".join(ur), " ".join(rom), " ".join(vow)


def main():
    check = "--check" in sys.argv
    U, L = load()
    lex = lexicon.Lex()
    lex.use_wikidata = lex.use_platts = False
    V = vocab(U, L, lex)
    byn = {u["n"]: u for u in U["units"]}
    sents = {n: [] for n in byn}
    pas = {}
    test = None
    quests = []
    errs = []
    seen = set()
    for ln, line in enumerate(open(f"{ROOT}/data/new_texts.tsv", encoding="utf8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        p = [x.strip() for x in line.split("|")]
        kind, unit, text, en = p[0], p[1], p[2], p[3]
        if kind == "Q":
            q = render(text, 12, V, errs)
            quests.append((q[0], en))
            continue
        if kind == "T":
            r = render(text, 12, V, errs)
            test = [r[0], r[1], en, r[2]]
            continue
        n = int(unit)
        r = render(text, n, V, errs)
        key = " ".join(norm(t) for t in re.split(r"\s+", r[0].replace("۔", "").replace("؟", "")))
        if kind == "S":
            if key in seen:
                errs.append(f"duplicate sentence u{n}: {text}")
            seen.add(key)
            sents[n].append([r[0], r[1], en, r[2]])
        elif kind == "P":
            pas[n] = [r[0], r[1], en, r[2]]
    # test passage must not share a sentence with unit text
    if test:
        usents = {s for n in byn for x in [*sents[n], *( [pas[n]] if n in pas else [])] for s in re.split("[۔؟!]", x[0]) if s.strip()}
        for s in re.split("[۔؟!]", test[0]):
            if s.strip() and s.strip() in usents:
                errs.append(f"test passage sentence also in unit text: {s.strip()}")
    for n in sorted(byn):
        if n in range(1, 12) and (len(sents[n]) < 8 or n not in pas):
            errs.append(f"unit {n}: {len(sents[n])} sentences, passage {'yes' if n in pas else 'MISSING'}")
    for e in errs:
        print("ERR", e)
    tok = lambda t: len(t.split())
    print("sentences", sum(len(v) for v in sents.values()), "tokens", sum(tok(s[0]) for v in sents.values() for s in v), "| passages", len(pas), "tokens", sum(tok(p[0]) for p in pas.values()),
          "| test tokens", tok(test[0]) if test else 0, "| errors", len(errs))
    if check or errs:
        sys.exit(1 if errs else 0)
    U["_meta"] = ("Course units. `words` are decodable using only letters taught up to and including that unit (scripts/check_decodable.py); each word is "
                  "[urdu, roman, english, urdu_vowelled]. `sentences` are the unit's Read-lesson sentences, `passage` its short passage, same 4-field shape; both are built "
                  "from words taught in this or an earlier unit (sight words from the unit that teaches their letters) by scripts/apply_new_texts.py. "
                  "Word evidence (corpus counts + open dictionary entry) is in data/word_evidence.json, sources in data/SOURCES.md.")
    for n, u in byn.items():
        if n in range(1, 12):
            u["sentences"] = sents[n]
            u["passage"] = pas[n]
    if test:
        L["assessment"]["passage"] = test[0]
        L["assessment"]["passage_roman"] = test[1]
        L["assessment"]["passage_en"] = test[2]
        if quests:
            L["assessment"]["questions"] = [q for q, _ in quests]
            L["assessment"]["answers"] = [a for _, a in quests]
    json.dump(U, open(f"{ROOT}/data/units.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    json.dump(L, open(f"{ROOT}/data/letters.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("written")


if __name__ == "__main__":
    main()
