#!/usr/bin/env python3
"""Write data/REVIEW_NEEDED.md: every judgement call on Urdu spelling, grammar, gloss or vowelling that a native speaker must confirm.

The author of all new content is an AI, so this is deliberately long. Sections 3 to 6 are computed from the data so they cannot go stale;
sections 1, 2, 7 are the author's hand-written calls. Re-run after any content edit:  python3 scripts/make_review_needed.py
"""
import collections, io, json, os, re, sys, tarfile, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lexicon
from lexicon import norm, toks

ROOT = lexicon.ROOT
U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
L = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
E = json.load(open(f"{ROOT}/data/word_evidence.json", encoding="utf8"))["words"]
MN = re.compile("[ً-ٰٟ]")
SHORT = re.compile("[َُِ]")
rows = []  # (section, word, why, source)


def add(section, word, why, source):
    rows.append((section, word, why, source))


# ---- 1 hand-written spelling and grammar calls
CALLS = [
    ("لیے / لئے", "Both spellings are in the course: لیے (unit 2, the current standard in most printing) and لئے (unit 10, the older hamza spelling, 28 uses in Tatoeba). Same for چاہیے (unit 5) vs the hamza spelling چاہئے, not taught. Native check: is it right to teach both, and which first?", "Tatoeba 44 vs 28; Wiktionary لیے"),
    ("کتا / کتّا", "Standard spelling has a shadda (کتّا kuttā); the bare corpus form کتا is what Tatoeba and Wiktionary use. We show کتا with the vowelled form کُتّا. Same for بلی/بلّی, کتے/کتّے.", "Wiktionary کتا; Tatoeba 3"),
    ("گا گے گی (future markers)", "Taught as three words with the gloss 'will'. Wiktionary has no future-marker sense under these spellings (گے = 'gay'), so the dictionary check cannot confirm them; the grammar is standard. Native check: is it better to teach 'ہو گا' as a pair?", "Platts, grammar"),
    ("ہوگا / ہوگی / جیسے / ایسے / چل / رکھ", "Very frequent forms we did NOT add because no dictionary page lists them under that spelling (future written as one word, split future ہو گا is used in sentences instead). A native speaker may prefer the one-word spelling.", "Tatoeba"),
    ("میں (maiṉ) vs میں (meṉ)", "One spelling, two readings (pronoun 'I', postposition 'in'). The romanisation of each sentence distinguishes them (maiṉ / meṉ) but the vowelled form shows مَیں for both. Native check: should the postposition be marked differently?", "course convention"),
    ("ہفتہ / ہفتے", "Glossed 'week, Saturday': ہفتہ is both. ہفتے کو = 'on Saturday' (used in a unit-8 sentence) but ہفتے میں = 'in a week'.", "Wiktionary ہفتہ"),
    ("پیر", "Taught as 'Monday' (unit 7). Wiktionary's first entry is 'foot'; the day-of-week sense (and 'saint') are separate entries. Native check: is Monday the right child-facing sense?", "Wiktionary پیر"),
    ("سو", "'hundred, to sleep' (existing word, two meanings); the sight word سے and سو are unrelated.", "existing word"),
    ("ابو / ابّا / امّی", "Family terms are regional and class-dependent (ابو, ابا, ابّا, ابّو; امی, امّی, اماں). We picked ابو (unit 4), ابّا (unit 10, shadda lesson), امّی (unit 10). Native check.", "Tatoeba, Wiktionary"),
    ("ڈرنا مت / غلطی مت کرنا / اتنا نمک مت لینا", "Negative imperatives with مت + infinitive: grammatical, but a native speaker may prefer مت ڈرو / مت کرو in some registers.", "grammar"),
    ("آؤ، ہم باغ جائیں", "Unit 10: hortative with a subjunctive verb (جائیں); the earlier longer form was replaced. Native check.", "author's judgement"),
    ("تم کیوں تھکے ہو؟", "Unit 6. Grammatical (tired, plural/familiar agreement with تم). Native check on naturalness.", "author's judgement"),
    ("ہمارا ٹیچر بہت اچھا ہے", "Unit 11. 'ٹیچر' is a loanword; 'استاد' is the Urdu word taught in unit 5. Fine in speech; check.", "author's judgement"),
    ("اسکول / سکول", "We use اسکول (Wiktionary); Tatoeba also has the spelling سکول 6 times. Native check.", "Wiktionary"),
    ("Verbless fragments in units 1 to 3", "Before unit 4 no sentence can contain ہے (ہ is taught in unit 4) so units 1 to 3 use noun phrases and imperatives (e.g. نمک کم, کتنا لمبا کمبل). They are real Urdu but not full sentences; a native teacher may want different examples.", "design constraint"),
    ("Passages 1 to 5", "Written with 6 to 14 letters of vocabulary, so they are intentionally flat (a primer, not literature). The unit-1 passage is a list of short phrases.", "design constraint"),
    ("Religious vocabulary", "اللّٰہ قرآن مسجد نماز روزہ اذان عید خدا: kept because the existing course already had اللّٰہ مکّہ صلوٰۃ and they are everyday words for Pakistani children; confirm this is acceptable for every audience (the app is not only for Muslims).", "scope"),
    ("Names", "Hadi, Nadia, Daniyal, Maryam, Sara, Javed, Salman, Shahid, Zainab, Ali, Ahmad, Khalid, Sabir, Tariq, Neelam are unit words with the gloss '(a name)'. Place names: پاکستان لاہور کراچی پشاور ملتان کوئٹہ پنجاب سندھ بلوچستان. Wiktionary lists them as names; check spellings (کوئٹہ vs کوئٹا).", "Wiktionary"),
    ("Dropped for lack of two sources", "Sentence words and foods without a dictionary entry were dropped rather than guessed: قورمہ پکوڑے سموسہ کلاس ہوگا جیسے ایسے.", "scripts/lexicon.py"),
]
for w, why, src in CALLS:
    add("1 · Spelling, grammar and convention calls", w, why, src)

# ---- 2 words with weak or no dictionary evidence
for k, r in E.items():
    n = r["tatoeba"] + r["wikipedia"]
    d = r["dictionary"]
    if not d:
        add("2 · Words kept with a corpus count but no dictionary page", k, f"unit {r['unit']}, gloss '{r['gloss']}': {r['tatoeba']} Tatoeba + {r['wikipedia']} Wikipedia occurrences, no Wiktionary/Platts/Wikidata entry. Real word (old v0.10.0 word or letter example).", "corpora")
    elif n < 2:
        add("2 · Words kept with a corpus count but no dictionary page", k, f"unit {r['unit']}, gloss '{r['gloss']}': dictionary entry exists but only {n} corpus occurrence(s) (100K-sentence corpora). Old v0.10.0 word or letter example; real but rare.", d["url"])

# ---- 3 gloss that no dictionary text matches
dis = [k for k, r in E.items() if r["gloss_agrees"] is False and r["dictionary"]]
for k in dis:
    r = E[k]
    d = r["dictionary"]
    kind = "inflected form: the dictionary glosses the lemma, ours glosses the form" if re.search(r"inflection|to \w+|stem|direct plural|oblique|feminine|participle", " ".join(d["gloss"]), re.I) else "possible homograph or different sense"
    add("3 · English gloss not confirmed by the dictionary text", k, f"unit {r['unit']}: ours '{r['gloss']}' vs {d['source'].split(' (')[0]} '{' ; '.join(d['gloss'])[:70]}' ({kind})", d["url"])

# ---- 4 vowelled forms that differ from Wiktionary's canonical short vowels
lex = lexicon.Lex()
lex.use_platts = lex.use_wikidata = False
mism = []
for u in U:
    for w in u["words"]:
        if len(w) < 4:
            continue
        k = norm(w[0])
        rs = lex.kk.get(k)
        if not rs:
            continue
        can = next((f["form"] for f in rs[0].get("forms", []) if "canonical" in f.get("tags", [])), None)
        if not can or MN.sub("", can) != MN.sub("", w[0]):
            continue
        def shortmarks(txt):
            """(letter index, vowel) for real short vowels. Wiktionary also puts a mark before a long-vowel letter (zer+ی, pesh+و, zabar+ا): ignore those."""
            ch = re.findall(".[\u064b-\u065f\u0670]*", unicodedata.normalize("NFC", txt))
            res = []
            for i, m in enumerate(ch):
                v = SHORT.search(m)
                if not v:
                    continue
                nxt = ch[i + 1][0] if i + 1 < len(ch) else ""
                if (v.group() == "\u0650" and nxt == "ی") or (v.group() == "\u064f" and nxt == "و") or (v.group() == "\u064e" and nxt == "ا"):
                    continue
                res.append((i, v.group()))
            return res
        sa, sb = shortmarks(w[3]), shortmarks(can)
        if sa != sb:
            mism.append((u["n"], w[0], w[3], can))
for n, bare, mine, can in mism:
    add("4 · Vowel marks differ from Wiktionary's canonical form", bare, f"unit {n}: ours {mine} vs Wiktionary {can}. Ours follow the course convention (zabar/zer/pesh on short vowels, jazm sparse, zabar before final ہ); confirm which the learner should see.", "Wiktionary canonical form")

# ---- 5 sentences and passages whose word pairs are rarely seen in real text
bg = set()
with tarfile.open(lexicon.fetch("leipzig.tgz")) as t:
    m = [x for x in t.getmembers() if x.name.endswith("-sentences.txt")][0]
    for line in io.TextIOWrapper(t.extractfile(m), encoding="utf8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            ts = list(toks(p[1]))
            bg.update(zip(ts, ts[1:]))
for sid, s in lex.sent:
    ts = list(toks(s))
    bg.update(zip(ts, ts[1:]))
scored = []
for u in U:
    for i, s in enumerate(u["sentences"]):
        ts = [norm(x) for x in toks(s[0])]
        pairs = list(zip(ts, ts[1:]))
        if pairs:
            scored.append((sum(p in bg for p in pairs) / len(pairs), u["n"], i, s))
scored.sort(key=lambda x: (x[0], x[1]))
low = [x for x in scored if x[0] == 0 and len(x[3][0].split()) >= 3]
for rate, n, i, s in low:
    add("5 · Sentences with no word pair attested in the corpora", s[0], f"unit {n} sentence {i + 1} ('{s[2]}'): none of its adjacent word pairs occurs in Tatoeba or the 100K Wikipedia sentences (many of ours are simple everyday phrasing that corpora of encyclopedic text rarely hold, so this is a prompt to check, not a verdict).", "corpora bigrams")
mean = sum(x[0] for x in scored) / len(scored)

# ---- 6 sensitive or adult-leaning words
SENS = "جان خون عورت بیمار بخار ظلم حادثہ ڈر غم تکلیف بھوک غریب خراب موت تباہ جھوٹ شرارت لڑائی لڑنا چور".split()
bare = {norm(w[0]): (u["n"], w) for u in U for w in u["words"]}
for w in SENS:
    if w in bare:
        add("6 · Words to check for children", w, f"unit {bare[w][0]}, '{bare[w][1][2]}': ordinary everyday word that touches illness, hunger, fighting or loss; confirm it suits the youngest learners.", "author's judgement")

# ---- 7 clips the blind judge never accepted
ovr = json.load(open(f"{ROOT}/data/audio_overrides.json", encoding="utf8"))
for k, v in ovr.items():
    if str(v.get("judge", "")).startswith("unverified") and k.split("/")[0] in ("units", "sentences", "passages"):
        add("7 · Audio clips the Gemini judge rejected after re-rolls (listen)", v["text"], f"{k}: {v['judge'][:110]}", "data/audio_overrides.json")

# ---- write
sections = collections.OrderedDict()
for s, w, why, src in rows:
    sections.setdefault(s, []).append((w, why, src))
out = ["# Needs a native Urdu speaker", "",
       "Everything new in the content-depth pass (≈ 800 words, 189 sentences, 11 passages, 5 test questions, vowelled forms, romanisation, glosses) was written by an AI. "
       "This file lists each judgement call that a native speaker must confirm, with the reason and the source that was checked. "
       "Generated by `scripts/make_review_needed.py` from `data/word_evidence.json`, `data/units.json` and the corpora; sections 1 and 6 are hand-written.", "",
       f"**Total entries: {len(rows)}** (" + ", ".join(f"{k.split(' · ')[0]}: {len(v)}" for k, v in sections.items()) + ").  "
       f"Average share of word pairs in our sentences that occur in real text: {100 * mean:.0f}%.", ""]
n = 0
for s, items in sections.items():
    out += [f"## {s}", "", "| # | Word / text | Why it needs a check | Source |", "|---|---|---|---|"]
    for w, why, src in items:
        n += 1
        out.append(f"| {n} | {w} | {why.replace('|', '/')} | {src} |")
    out.append("")
open(f"{ROOT}/data/REVIEW_NEEDED.md", "w", encoding="utf8").write("\n".join(out))
print("entries", len(rows), {k: len(v) for k, v in sections.items()})
