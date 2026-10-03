#!/usr/bin/env python3
"""Open-corpus + open-dictionary evidence for every course word (no invented words).

Sources (all open; downloaded once into ~/.cache/urc_lexicon, see data/SOURCES.md):
  Tatoeba Urdu sentences  (CC-BY 2.0 FR)   https://downloads.tatoeba.org/exports/per_language/urd/urd_sentences.tsv.bz2
  Leipzig Corpora Collection, Urdu Wikipedia 2021 100K word list (CC-BY)   https://wortschatz.uni-leipzig.de/en/download/Urdu
  Wiktionary, Urdu entries via kaikki.org Wiktextract (CC-BY-SA; each hit links to the en.wiktionary page)

  python3 scripts/lexicon.py cand N [--min-tat 1 --min-wiki 15 --top 120]   # candidate words whose letters are all taught by unit N
  python3 scripts/lexicon.py check                                          # evidence for every word of data/units.json -> data/word_evidence.json
Library: from lexicon import Lex; Lex().evidence("کتاب")
"""
import bz2, collections, io, json, os, re, sys, tarfile, unicodedata, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.expanduser("~/.cache/urc_lexicon")
URLS = {
    "tatoeba": "https://downloads.tatoeba.org/exports/per_language/urd/urd_sentences.tsv.bz2",
    "leipzig": "https://downloads.wortschatz-leipzig.de/corpora/urd_wikipedia_2021_100K.tar.gz",
    "kaikki": "https://kaikki.org/dictionary/Urdu/kaikki.org-dictionary-Urdu.jsonl",
}
MK = re.compile("[ً-ٰٟۖ-ۭ]")
NORM = {"ك": "ک", "ي": "ی", "ى": "ی", "ه": "ہ", "ۓ": "ے", "‌": "", "‍": "", "ـ": ""}
PUN = re.compile(r"^[^ء-ۓ]+|[^ء-ۓ]+$")
FOLD = {"آ": "ئ", "أ": "ئ", "ؤ": "ئ", "ء": "ئ"}  # madda / hamza carriers are taught in unit 10 (letter ئ)
NOT_WORD = ("character", "suffix", "prefix", "symbol", "proverb")


def norm(s):
    return MK.sub("", "".join(NORM.get(c, c) for c in s))


def toks(s):
    for t in s.split():
        t = PUN.sub("", t)
        if t and all("؀" <= c <= "ۿ" for c in t) and not re.fullmatch("[۰-۹٠-٩]+", t):
            yield norm(t)


def fetch(name):
    os.makedirs(CACHE, exist_ok=True)
    path = f"{CACHE}/{name}"
    if not os.path.exists(path):
        raw = urllib.request.urlopen(urllib.request.Request(URLS[name.split('.')[0]], headers={"User-Agent": "urc-lexicon/1.0"}), timeout=300).read()
        open(path, "wb").write(raw)
    return path


class Lex:
    def __init__(self):
        L = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))["letters"]
        self.unit = {l["ch"]: l["unit"] for l in L}
        self.unit["ۃ"] = 10
        # Tatoeba
        self.sent = []  # (id, text)
        self.tat = collections.Counter()
        for l in bz2.open(fetch("tatoeba.bz2"), "rt", encoding="utf8"):
            p = l.rstrip("\n").split("\t")
            if len(p) >= 3:
                self.sent.append((p[0], p[2]))
                self.tat.update(toks(p[2]))
        self.tat_n = sum(self.tat.values())
        # Leipzig Wikipedia word list
        self.wiki = collections.Counter()
        with tarfile.open(fetch("leipzig.tgz")) as t:
            m = [x for x in t.getmembers() if x.name.endswith("-words.txt")][0]
            for l in io.TextIOWrapper(t.extractfile(m), encoding="utf8"):
                p = l.rstrip("\n").split("\t")
                if len(p) >= 3:
                    for w in toks(p[1]):
                        self.wiki[w] += int(p[2])
        self.wiki_n = sum(self.wiki.values())
        # Wiktionary (kaikki)
        self.kk = collections.defaultdict(list)
        self.formof = collections.defaultdict(list)
        for l in open(fetch("kaikki.jsonl"), encoding="utf8"):
            r = json.loads(l)
            if r["pos"] in NOT_WORD:
                continue
            self.kk[norm(r["word"])].append(r)
            for f in r.get("forms", []):
                tg = f.get("tags", [])
                if "romanization" in tg or "Hindi" in tg or "table-tags" in tg or "canonical" in tg:
                    continue
                if f["form"] and all("؀" <= c <= "ۿ" for c in f["form"]):
                    self.formof[norm(f["form"])].append(r)

    def unit_of(self, w):
        u = 0
        for c in w:
            c = FOLD.get(c, c)
            if c in self.unit:
                u = max(u, self.unit[c])
            elif c != "ـ":
                return None
        return u

    def score(self, w):
        return self.tat[w] / self.tat_n * 1e6 + self.wiki[w] / self.wiki_n * 1e6

    def wikidata(self, w):
        """Second open dictionary: Wikidata (CC0) item whose Urdu label/alias is exactly w. Cached; polite rate."""
        cp = f"{CACHE}/wikidata.json"
        cache = json.load(open(cp, encoding="utf8")) if os.path.exists(cp) else {}
        if w not in cache:
            import time, urllib.parse
            u = "https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=ur&uselang=en&limit=8&search=" + urllib.parse.quote(w)
            hit = None
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "urc-lexicon/1.0 (educational Urdu reading course)"}), timeout=30))
                for x in r.get("search", []):
                    if norm(x.get("match", {}).get("text", "")) == w and x.get("match", {}).get("language") == "ur":
                        hit = {"qid": x["id"], "label": x.get("label"), "description": x.get("description")}
                        break
            except Exception:
                hit = None
            time.sleep(0.6)
            cache[w] = hit
            os.makedirs(CACHE, exist_ok=True)
            json.dump(cache, open(cp, "w", encoding="utf8"), ensure_ascii=False)
        return cache[w]

    def platts(self, w):
        """Third open source: Platts, A Dictionary of Urdu, Classical Hindi and English (1884, public domain) at dsal.uchicago.edu. Cached; polite rate."""
        cp = f"{CACHE}/platts.json"
        cache = json.load(open(cp, encoding="utf8")) if os.path.exists(cp) else {}
        if w not in cache:
            import time, urllib.parse, html
            url = "https://dsal.uchicago.edu/cgi-bin/app/platts_query.py?searchhws=yes&matchtype=exact&qs=" + urllib.parse.quote(w)
            hit = None
            try:
                raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (urc-lexicon educational Urdu reading course)"}), timeout=40).read().decode("utf8", "replace")
                txt = html.unescape(re.sub(r"<[^>]+>", " ", raw.split("Search for headword", 1)[-1]))
                m = re.search(r"\b1\)\s+(\S+)\s+(\S+)\s*\(\s*p\.\s*\d+\s*\)\s*(.*?)(?=\s\d+\)\s+\S+\s+\S+\s*\(\s*p\.|\Z)", txt, re.S)
                if m:
                    body = re.sub(r"\[[^\]]*\]", "", re.sub(r"\s+", " ", m.group(3)))
                    hit = {"headword": m.group(1), "roman": m.group(2), "text": body[:400], "url": url}
            except Exception:
                hit = None
            time.sleep(0.8)
            cache[w] = hit
            os.makedirs(CACHE, exist_ok=True)
            json.dump(cache, open(cp, "w", encoding="utf8"), ensure_ascii=False)
        return cache[w]

    def lemma_guess(self, w):
        """Regular inflection patterns -> candidate lemma headwords (verb infinitive, adjective -ا, noun plural)."""
        c = []
        for suf in ("تا", "تی", "تے", "نے", "ئیں", "ؤ", "و"):
            if w.endswith(suf) and len(w) > len(suf) + 1:
                c.append(w[: -len(suf)] + "نا")
        if w[-1:] in "اےی" and len(w) >= 2:  # adjective / participle triple: -ا -ے -ی
            c += [w[:-1] + e for e in ("ا", "ے", "ی", "ہ", "نا") if e != w[-1:]]
        if w.endswith("یں") and len(w) > 3:
            c += [w[:-2], w[:-2] + "ی", w[:-2] + "ہ"]
        if w.endswith("وں") and len(w) > 3:
            c += [w[:-2], w[:-2] + "ا", w[:-2] + "ی"]
        if w.endswith("ا") and len(w) > 3:
            c.append(w[:-1] + "نا")  # perfective -ا -> infinitive
        return [x for x in dict.fromkeys(c) if x in self.kk]

    @staticmethod
    def gloss_ok(gloss, texts):
        """Loose gloss check: some 4-letter stem of my English gloss occurs in the dictionary text."""
        if not gloss:
            return True
        g = " ".join(texts).lower()
        stems = [x[:4] for x in re.findall(r"[a-z]{3,}", gloss.lower()) if x not in ("the", "and", "his", "her", "for", "one", "who", "its", "was", "are")]
        return not stems or any(st in g for st in stems)

    def evidence(self, w, gloss=None):
        """Corpus counts + the first open dictionary whose entry agrees with `gloss` (Wiktionary headword, Platts 1884,
        regular inflection of a Wiktionary lemma, Wikidata label). `dict` is None if no dictionary has the word."""
        w = norm(w)
        ev = {"tatoeba": self.tat[w], "wikipedia": self.wiki[w], "dict": None, "gloss_agrees": None}
        cands = []
        rs = self.kk.get(w)
        how = "headword"
        if not rs:
            rs, how = self.formof.get(w), "listed form of"
        if rs:
            r = sorted(rs, key=lambda x: x["pos"] == "name")[0]
            rom = next((f["form"] for f in r.get("forms", []) if "romanization" in f.get("tags", [])), "")
            gl = [s["glosses"][-1] for x in rs[:4] for s in x["senses"] if s.get("glosses")][:8]
            cands.append({"source": "Wiktionary (en)", "url": "https://en.wiktionary.org/wiki/" + urllib.request.quote(r["word"]) + "#Urdu",
                          "match": how, "entry": r["word"], "pos": r["pos"], "roman": rom, "gloss": gl})
        def lemma():
            for lem in self.lemma_guess(w):
                r = self.kk[lem][0]
                yield {"source": "Wiktionary (en), regular inflection of the lemma", "url": "https://en.wiktionary.org/wiki/" + urllib.request.quote(r["word"]) + "#Urdu",
                       "match": "inflection of", "entry": r["word"], "pos": r["pos"], "roman": "", "gloss": [s["glosses"][-1] for x in self.kk[lem][:3] for s in x["senses"] if s.get("glosses")][:6]}
        def platts():
            h = self.platts(w) if getattr(self, "use_platts", True) else None
            if h:
                yield {"source": "Platts 1884 (DSAL, public domain)", "url": h["url"], "match": "headword", "entry": h["headword"], "pos": "", "roman": h["roman"], "gloss": [h["text"]]}
        def wikidata():
            h = self.wikidata(w) if getattr(self, "use_wikidata", True) else None
            if h:
                yield {"source": "Wikidata (CC0)", "url": "https://www.wikidata.org/wiki/" + h["qid"], "match": "ur label", "entry": w, "pos": "noun", "roman": "", "gloss": [h["label"] or "", h["description"] or ""]}
        for gen in (None, platts, lemma, wikidata):
            if gen:
                if any(self.gloss_ok(gloss, c["gloss"]) for c in cands):
                    break
                cands.extend(gen())
        ok = [c for c in cands if self.gloss_ok(gloss, c["gloss"])]
        ev["gloss_agrees"] = bool(ok) if gloss else None
        ev["dict"] = (ok or cands or [None])[0]
        ev["dict_all"] = [c["source"] for c in cands]
        return ev

    def sentences_with(self, toks_ok, maxn=9):
        for sid, s in self.sent:
            t = list(toks(s))
            if 2 <= len(t) <= maxn and all(x in toks_ok for x in t):
                yield sid, s, t

    def candidates(self, n, min_tat=1, min_wiki=15, exclude=()):
        out = []
        for w in set(self.tat) | set(self.wiki):
            if self.unit_of(w) != n or w in exclude:
                continue
            if self.tat[w] < min_tat and self.wiki[w] < min_wiki:
                continue
            ev = self.evidence(w)
            if ev["dict"] and ev["dict"]["pos"] != "name":
                out.append((self.score(w), w, ev))
        return sorted(out, reverse=True)


def short_vowels(rom):
    r = rom.lower()
    for d in ("ai", "au"):
        r = r.replace(d, "A")  # diphthong = one short vowel mark + a letter
    r = re.sub(r"[āīūeo]", "L", r)
    return len(re.findall(r"[aiuA]", r))


def verify(path, lex, existing_bare=()):
    """Check a unit|urdu|roman|gloss|vowelled TSV: decodable by its unit, corpus + dictionary evidence, vowelled == bare + marks."""
    bad = warn = 0
    seen = {}
    rows = []
    for ln, line in enumerate(open(path, encoding="utf8"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = [x.strip() for x in line.split("|")]
        if len(p) < 5:
            print(f"L{ln} FORMAT {line}")
            bad += 1
            continue
        u, ur, rom, gl, vw = int(p[0]), p[1], p[2], p[3], p[4]
        k = norm(ur)
        issues = []
        if ur != k:
            issues.append("urdu has marks/variant letters")
        if k in seen or k in existing_bare:
            issues.append(f"duplicate (also {seen.get(k, 'existing')})")
        seen[k] = u
        du = lex.unit_of(k)
        if du is None:
            issues.append("non-Urdu letter")
        elif du > u:
            issues.append(f"needs unit {du}")
        ev = lex.evidence(k, gl)
        if not ev["dict"]:
            issues.append("NO DICTIONARY ENTRY")
        if ev["tatoeba"] + ev["wikipedia"] < 2:
            issues.append(f"NOT ATTESTED (tat {ev['tatoeba']}, wiki {ev['wikipedia']})")
        if MK.sub("", vw) != ur:
            issues.append("vowelled form differs from bare")
        marks = len(re.findall("[\u064e\u064f\u0650]", vw))
        exp = short_vowels(rom)
        if marks != exp:
            issues.append(f"marks {marks} vs roman short vowels {exp}")
        d = ev["dict"]
        if d and ev["gloss_agrees"] is False:
            issues.append(("GLOSS MISMATCH vs " if d["source"].startswith(("Wikidata", "Platts")) else "gloss? ") + f"mine '{gl}' vs {d['source'][:12]} '{' '.join(d['gloss'])[:60]}'")
        if issues:
            hard = [i for i in issues if i.startswith(("NO DICT", "NOT ATT", "needs", "non-Urdu", "duplicate", "urdu has", "vowelled", "GLOSS MISMATCH"))]
            bad += bool(hard)
            warn += not hard
            print(f"{'FAIL' if hard else 'warn'} u{u} {ur} {rom} | {'; '.join(issues)}")
        rows.append((u, ur, rom, gl, vw, ev))
    print(f"{len(rows)} rows, {bad} failing, {warn} warnings")
    return rows


def main():
    a = sys.argv[1:]
    lex = Lex()
    if a and a[0] == "cand":
        n = int(a[1])
        opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
        U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
        have = {norm(w[0]) for u in U for w in u["words"]}
        for sc, w, ev in lex.candidates(n, opt("--min-tat", 1), opt("--min-wiki", 15))[: opt("--top", 120)]:
            d = ev["dict"]
            print(w, f"{ev['tatoeba']}/{ev['wikipedia']}", d["pos"][:4], "; ".join(d["gloss"])[:40], "|", d["roman"], "*" if w in have else "")
    elif a and a[0] == "top":
        # Tatoeba top-N types with an eligibility flag, for scripts/content_metrics.py (no network needed afterwards)
        lex.use_platts = lex.use_wikidata = False
        NAMES = {"ٹام", "مریم", "جان", "ٹامز", "ٹامس", "ٹوم", "جاپان", "امریکہ", "امریکا", "میکسیکو", "لندن", "باسٹن", "بھارت", "ٹی", "ایم", "ای", "وی", "مین", "ٹینس", "پیانو"}
        top = [w for w, _ in sorted(lex.tat.items(), key=lambda kv: (-kv[1], kv[0]))][: int(a[1]) if len(a) > 1 else 1000]
        out = []
        for w in top:
            ev = lex.evidence(w)
            d = ev["dict"]
            why = "ok"
            if w in NAMES:
                why = "proper name / foreign"
            elif lex.unit_of(w) is None:
                why = "not Urdu letters"
            elif not d:
                why = "no dictionary entry (variant spelling, typo or foreign)"
            elif d["pos"] == "name":
                why = "proper name"
            out.append({"w": w, "n": lex.tat[w], "eligible": why == "ok", "why": why})
        json.dump({"source": "Tatoeba Urdu sentences (CC-BY 2.0 FR); eligible = Urdu letters, has a Wiktionary entry/inflection, not a name", "words": out}, open(f"{ROOT}/data/tatoeba_top1000.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)
        print(len(out), "types,", sum(o["eligible"] for o in out), "eligible")
    elif a and a[0] == "verify":
        U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
        verify(a[1], lex, {norm(w[0]) for u in U for w in u["words"]})
    elif a and a[0] == "check":
        U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
        out, bad = {}, []
        for u in U:
            for w in u["words"]:
                k = norm(w[0])
                ev = lex.evidence(k, w[2])
                d = ev["dict"]
                rec = {"unit": u["n"], "decodable_from_unit": lex.unit_of(k), "roman": w[1], "gloss": w[2], "tatoeba": ev["tatoeba"], "wikipedia": ev["wikipedia"],
                       "dictionary": None if not d else {"source": d["source"], "url": d["url"], "match": d["match"], "entry": d["entry"], "roman": d["roman"], "gloss": [g[:90] for g in d["gloss"][:3]]},
                       "gloss_agrees": ev["gloss_agrees"]}
                if not (ev["tatoeba"] + ev["wikipedia"] >= 2 and d):
                    bad.append((u["n"], w[0], w[1], ev["tatoeba"], ev["wikipedia"], bool(d)))
                out[k] = rec
        json.dump({"_meta": "Evidence per unit word: corpus counts (Tatoeba Urdu sentences; Leipzig Urdu Wikipedia 2021 100K) + the open dictionary entry that agrees with our gloss (Wiktionary via kaikki, Platts 1884 via DSAL, Wikidata). See data/SOURCES.md.", "words": out},
                  open(f"{ROOT}/data/word_evidence.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)
        for b_ in bad:
            print("NO EVIDENCE", *b_)
        disagree = [k for k, r in out.items() if r["gloss_agrees"] is False]
        print(len(out), "words,", len(bad), "without corpus+dictionary evidence,", len(disagree), "where no dictionary text matches our gloss (listed in REVIEW_NEEDED)")
        json.dump(disagree, open("/tmp/urc_gloss_disagree.json", "w", encoding="utf8"), ensure_ascii=False)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
