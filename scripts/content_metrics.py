#!/usr/bin/env python3
"""Content-depth metrics for data/units.json (+ data/letters.json assessment). Read-only.

  python3 scripts/content_metrics.py            # table to stdout
  python3 scripts/content_metrics.py --json out.json [--units old_units.json --letters old_letters.json]

Measures: unit-word count, bare-letter length distribution, syllable estimate (vowel nuclei in the romanisation),
share of words >= 4 letters, running words in sentences + passages, per-unit counts, and coverage of the most
frequent Tatoeba-Urdu words (data/tatoeba_urd_freq.json, CC-BY) by the course vocabulary.

Coverage definitions (top-N = N most frequent corpus word types after stripping punctuation and marks, proper names removed):
  eligible  = top-N types that are real words: spelt only with the taught letters, in Wiktionary, not a proper name
              (data/tatoeba_top1000.json; the rest of the top-1000 are names, foreign words and misspellings such as لئیے جائو تمھیں)
  as_word   = eligible types that are a unit word or sight word                       (taught explicitly)
  seen      = eligible types that are a unit word, sight word, or appear in a sentence / passage (read at least once)
  by_unit   = 'by unit 12': all of the above, since unit 12 is the end of the path; per-unit first-appearance is in 'cum'.
"""
import collections, json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


U = json.load(open(_arg("--units", f"{ROOT}/data/units.json"), encoding="utf8"))["units"]  # --units/--letters let you measure an older revision (git show REV:data/units.json > /tmp/x.json)
LET = json.load(open(_arg("--letters", f"{ROOT}/data/letters.json"), encoding="utf8"))
TAT = json.load(open(f"{ROOT}/data/tatoeba_urd_freq.json", encoding="utf8"))["words"]
TOP = json.load(open(f"{ROOT}/data/tatoeba_top1000.json", encoding="utf8"))["words"] if os.path.exists(f"{ROOT}/data/tatoeba_top1000.json") else None  # scripts/lexicon.py top
LU = {l["ch"]: l["unit"] for l in LET["letters"]}
LU["ۃ"] = 10
FOLD = {"آ": "ا", "أ": "ا", "ؤ": "و", "ء": "ئ"}
MK = re.compile("[ً-ٰٟۖ-ۭ]")
PUN = re.compile(r"^[^ء-ۓ]+|[^ء-ۓ]+$")
NAMES = {"ٹام", "مریم", "جان", "ٹامز", "ٹامس"}  # proper names in the Tatoeba sample (Tom, Mary, John ...)
SKIP_TOK = re.compile(r"^[۰-۹٠-٩]+$")


def bare(s):
    return MK.sub("", s).replace("ـ", "")


def toks(s):
    for t in s.split():
        t = PUN.sub("", t)
        if t and not SKIP_TOK.match(t):
            yield bare(t)


def nletters(w):
    return len([c for c in bare(w) if unicodedata.category(c).startswith("L")])


def syl(rom):
    r = rom.lower().replace("ai", "a").replace("au", "a").replace("ae", "a")
    return max(1, len(re.findall(r"[aāiīuūeo]+", r)))


def unit_of(w):
    u = 0
    for c in w:
        c = FOLD.get(c, c)
        if c in LU:
            u = max(u, LU[c])
        elif c != "ـ":
            return None
    return u


def passage_texts(u):
    p = u.get("passage")
    return [p] if p else []


def main():
    words = [(u["n"], w) for u in U for w in u["words"]]
    uniq = {bare(w[0]) for _, w in words}
    lens = collections.Counter(min(8, nletters(w[0])) for _, w in words)
    heavy = sum(1 for _, w in words if nletters(w[0]) >= 4)
    heavy5 = sum(1 for _, w in words if nletters(w[0]) >= 5)
    syls = [syl(w[1]) for _, w in words]
    run_s = sum(len(list(toks(s[0]))) for u in U for s in u["sentences"])
    run_p = sum(len(list(toks(p[0]))) for u in U for p in passage_texts(u))
    run_types = {t for u in U for s in u["sentences"] for t in toks(s[0])} | {t for u in U for p in passage_texts(u) for t in toks(p[0])}
    asm = LET["assessment"]["passage"]
    asm_tok = list(toks(asm))
    def sents_of(t):
        return {" ".join(toks(x)) for x in re.split("[۔؟!]", t) if x.strip()}
    asm_sents = sents_of(LET["assessment"]["passage"])
    unit_sents = {" ".join(toks(s[0])) for u in U for s in u["sentences"]} | {x for u in U for p in passage_texts(u) for x in sents_of(p[0])}
    taught_text = {bare(w[0]) for _, w in words} | {bare(x) for x in LET["sight_words"]}
    seen = taught_text | run_types

    freq = collections.Counter()
    for w, n in TAT:
        for t in toks(w):
            freq[t] += n
    ranked = [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])) if w not in NAMES]
    cov = {}
    okset = {t["w"] for t in TOP if t["eligible"]} if TOP else None
    order = [t["w"] for t in TOP] if TOP else ranked
    for N in (100, 300, 500, 1000):
        top = order[:N]
        elig = [w for w in top if unit_of(w) is not None and (okset is None or w in okset)]
        a = [w for w in elig if w in taught_text]
        s = [w for w in elig if w in seen]
        cov[N] = {"top": len(top), "eligible": len(elig), "as_word": len(a), "seen": len(s),
                  "as_word_pct": round(100 * len(a) / max(1, len(elig)), 1), "seen_pct": round(100 * len(s) / max(1, len(elig)), 1)}
    tot = sum(freq.values())
    tok_cov = round(100 * sum(c for w, c in freq.items() if w in seen) / tot, 1)
    tok_cov_word = round(100 * sum(c for w, c in freq.items() if w in taught_text) / tot, 1)

    per_unit = []
    cum = set()
    for u in U:
        ws = u["words"]
        sent_tok = sum(len(list(toks(s[0]))) for s in u["sentences"])
        pass_tok = sum(len(list(toks(p[0]))) for p in passage_texts(u))
        cum |= {bare(w[0]) for w in ws}
        top1000 = set(order[:1000])
        elig = {w for w in top1000 if unit_of(w) is not None and (okset is None or w in okset)}
        per_unit.append({"n": u["n"], "words": len(ws), "ge4": sum(1 for w in ws if nletters(w[0]) >= 4),
                         "sentences": len(u["sentences"]), "sentence_tokens": sent_tok, "passage_tokens": pass_tok,
                         "has_passage": bool(u.get("passage")), "cum_top1000_as_word_pct": round(100 * len(cum & elig) / max(1, len(elig)), 1)})
    m = {
        "unit_words": len(words), "unique_words": len(uniq), "share_ge4_pct": round(100 * heavy / max(1, len(words)), 1), "words_ge4": heavy, "words_ge5": heavy5, "share_ge5_pct": round(100 * heavy5 / max(1, len(words)), 1),
        "length_hist": {str(k): lens[k] for k in sorted(lens)}, "mean_letters": round(sum(nletters(w[0]) for _, w in words) / max(1, len(words)), 2),
        "mean_syllables": round(sum(syls) / max(1, len(syls)), 2), "share_syl_ge3_pct": round(100 * sum(1 for s in syls if s >= 3) / max(1, len(syls)), 1),
        "sentences": sum(len(u["sentences"]) for u in U), "running_words_sentences": run_s, "running_words_passages": run_p,
        "running_words_total": run_s + run_p, "running_word_types": len(run_types), "passages": sum(1 for u in U if u.get("passage")),
        "assessment_tokens": len(asm_tok), "assessment_types_not_taught": sorted({t for t in asm_tok if t not in seen}),
        "assessment_types_not_taught_as_word": sorted({t for t in asm_tok if t not in taught_text}),
        "assessment_tokens_in_unit_text": sum(1 for t in asm_tok if t in seen),
        "assessment_sentence_overlap_with_unit_text": len(asm_sents & unit_sents),
        "coverage_top_n": cov, "token_cov_seen_pct": tok_cov, "token_cov_as_word_pct": tok_cov_word, "per_unit": per_unit,
    }
    if "--json" in sys.argv:
        json.dump(m, open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"unit words {m['unit_words']} (unique {m['unique_words']})  >=4 letters {m['words_ge4']} = {m['share_ge4_pct']}%  >=5 letters {m['words_ge5']} = {m['share_ge5_pct']}%  mean letters {m['mean_letters']}  mean syllables {m['mean_syllables']}  >=3 syllables {m['share_syl_ge3_pct']}%")
    print("length histogram (letters):", m["length_hist"])
    print(f"sentences {m['sentences']}  passages {m['passages']}  running words: sentences {run_s} + passages {run_p} = {run_s + run_p}  (types {len(run_types)})")
    print(f"assessment passage: {m['assessment_tokens']} tokens, {m['assessment_tokens_in_unit_text']} appear in unit text, word types never taught as a unit/sight word {len(m['assessment_types_not_taught_as_word'])}, sentences identical to unit text {m['assessment_sentence_overlap_with_unit_text']}")
    for N, c in cov.items():
        print(f"Tatoeba top-{N}: eligible {c['eligible']}  taught as word {c['as_word']} ({c['as_word_pct']}%)  seen in any course text {c['seen']} ({c['seen_pct']}%)")
    print(f"Tatoeba token coverage: taught-as-word {tok_cov_word}%, seen in any text {tok_cov}%")
    print("unit | words | >=4 | sents | sent tok | passage tok | top1000 cum%")
    for p in per_unit:
        print(f"{p['n']:>4} | {p['words']:>5} | {p['ge4']:>3} | {p['sentences']:>5} | {p['sentence_tokens']:>8} | {p['passage_tokens']:>11} | {p['cum_top1000_as_word_pct']}")


if __name__ == "__main__":
    main()
