#!/usr/bin/env python3
"""Build course/unit_NN.md lesson files from data/letters.json + data/units.json.
Each unit follows the 8-step lesson shape in course/00_design.md and embeds the rendered cards and audio."""
import json, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f"{ROOT}/data/letters.json", encoding="utf8"))
U = json.load(open(f"{ROOT}/data/units.json", encoding="utf8"))["units"]
L = {l["ch"]: l for l in D["letters"]}
random.seed(7)


def w4(w):  # tolerate 3- or 4-element word rows
    return (w + [w[0]])[:4]


def unit_md(u, taught_before):
    n = u["n"]; style = "nastaliq" if n >= 11 else "naskh"
    out = [f"# Unit {n} — {u['title']}  ·  {u['title_ur']}\n", f"**Focus:** {u['focus']}\n"]
    letters = [L[c] for c in u["letters"] if c in L]
    if letters:
        out.append("## 1 · Hear it\n")
        out.append("| Letter | Name | Sound | Say it like… | Audio |\n|---|---|---|---|---|")
        for l in letters:
            out.append(f"| {l['ch']} | {l['name']} ({l['name_ur']}) | /{l['ipa']}/ | {l['hint']} | `assets/audio/names/{l['id']}.mp3` · `assets/audio/words/{l['id']}.mp3` ({l['example'][0]} {l['example'][1]} — {l['example'][2]}) |")
        out.append("\n## 2 · See it\n")
        for l in letters:
            j = "joins forward (4 forms)" if l["joiner"] else "does **not** join forward (2 forms: isolated, final)"
            ni = " No Urdu word begins with it." if l["never_initial"] else ""
            out.append(f"**{l['ch']} {l['name']}** — {j}.{ni}\n\n![{l['name']} card](../assets/images/letters/{l['id']}_{style}.png)\n![{l['name']} forms](../assets/images/forms/{l['id']}_{style}.png)\n")
        out.append("## 3 · Tell it apart\n")
        seen = set()
        for l in letters:
            sib = [c for c in l["confusable"] if c in taught_before | set(u["letters"])]
            if sib and l["ch"] not in seen:
                grp = [l["ch"]] + sib
                seen.update(grp)
                out.append(f"- {l['ch']} vs {' '.join(sib)} — same body, different dots or marks. Drill: play `names/` audio for each, learner points at the right one. 10 rounds, shuffled.")
        if not seen:
            out.append("- No new look-alikes this unit. Re-run the unit 2 dot drill (ب ت ن ی) as a warm-up.")
    words = [w4(w) for w in u["words"]]
    if words:
        joinable = [w for w in words if len(w[0]) >= 3][:3]
        out.append("\n## 4 · Join it\n")
        out.append("Build each word from letter tiles, right to left. Watch which letters change shape and which refuse to join.\n")
        for w in joinable:
            tiles = " + ".join(w[0])
            out.append(f"- {tiles}  →  **{w[3]}**  ({w[1]}, {w[2]})")
        out.append("\n## 5 · Read it\n")
        out.append("Vowel marks are shown. Read aloud, then play the audio and compare.\n")
        out.append("| Word | Say | Means | Audio |\n|---|---|---|---|")
        for i, w in enumerate(words):
            out.append(f"| {w[3]} | {w[1]} | {w[2]} | `assets/audio/units/u{n:02d}_{i:02d}.mp3` |")
        if u["sentences"]:
            out.append("\n**Sentences**\n")
            for i, s in enumerate(u["sentences"]):
                s = w4(s)
                out.append(f"- {s[3]}  —  *{s[1]}*  —  {s[2]}  · `assets/audio/sentences/u{n:02d}_{i:02d}.mp3`")
        out.append("\n## 6 · Write it\n")
        out.append("Trace each new letter in all its forms three times (children: required; adults: recommended). Use the forms card as the model. Then write these words from the list without looking: " + ", ".join(w[3] for w in words[:5]) + ".\n")
        dict_words = random.sample(words, min(5, len(words)))
        out.append("## 7 · Dictation\n")
        out.append("Play each clip twice. Learner writes the word. Then reveal.\n")
        for i, w in enumerate(dict_words, 1):
            idx = words.index(w)
            out.append(f"{i}. `assets/audio/units/u{n:02d}_{idx:02d}.mp3`")
        out.append("\n<details><summary>Answer key</summary>\n\n" + "\n".join(f"{i}. {w[3]} ({w[1]})" for i, w in enumerate(dict_words, 1)) + "\n\n</details>\n")
        out.append("## 8 · Check (score 8/10 to move on)\n")
        quiz = random.sample(words, min(10, len(words)))
        for i, w in enumerate(quiz, 1):
            others = random.sample([x for x in words if x is not w], min(3, len(words) - 1))
            opts = sorted([w] + others, key=lambda x: random.random())
            out.append(f"{i}. Which one says **{w[1]}** ({w[2]})?   " + "   ".join(f"({chr(97+k)}) {o[3]}" for k, o in enumerate(opts)))
        out.append("\n<details><summary>Answer key</summary>\n\n" + "\n".join(f"{i}. {w[3]}" for i, w in enumerate(quiz, 1)) + "\n\n</details>\n")
    return "\n".join(out)


def special_units():
    asp = "\n".join(f"| {a[0]} | {a[1]} | {a[2]} | {a[3]} | {a[4]} | `assets/audio/aspirates/{''.join(c if c.isalnum() else '_' for c in a[1])}.mp3` |" for a in D["aspirates"])
    dia = "\n".join(f"| {d['ch']} | {d['name']} ({d['name_ur']}) | {d['sound']} | {d['position']} | {d['example'][0]} {d['example'][1]} — {d['example'][2]} |" for d in D["diacritics"])
    lv = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in D["long_vowels"])
    num = "  ".join(f"{a}={b}" for a, b in D["numerals"])
    nj = " ".join(l["ch"] for l in D["letters"] if not l["joiner"])
    return {
        0: f"""
## The five things to know before letter one

1. **Urdu is read right to left.** The first letter of a word is on the right. Numbers are still written left to right.
2. **Letters join like cursive.** Most letters change shape depending on where they sit: alone, first, middle, last. Ten letters never join to the letter after them: **{nj}**. After one of these the word "restarts".
3. **Dots decide the letter.** ب پ ت ٹ ث ن ی all share one body; the dots (and the small ط-mark) tell them apart. Count dots, and check above vs below.
4. **Small marks are vowels.** Short a / i / u are written as small marks above or below the letter: zabar ( َ ), zer ( ِ ), pesh ( ُ ). Adult books drop them; this course keeps them until unit 11.
5. **Two typefaces, one alphabet.** Printed Urdu uses *Nastaliq* (letters slope and stack). Screens and Arabic use *Naskh* (letters sit on a line). We learn shapes in Naskh, then switch to Nastaliq in unit 11.

### Vowel marks
| Mark | Name | Sound | Where | Example |
|---|---|---|---|---|
{dia}

### Long vowels (written with letters)
| Letter | Sound | Example |
|---|---|---|
{lv}

### Numerals
{num}
""",
        6: f"""
## Aspirates — one letter, one puff of breath
Write دو چشمی ہے (ھ) after a consonant to add a breath. English speakers already do this ("p" in *pin* has it, "p" in *spin* does not).

| Pair | Say | Word | Roman | Means | Audio |
|---|---|---|---|---|---|
{asp}

## Nūn ghunna — the nasal vowel
ں at the end of a word (or ن in the middle) nasalises the vowel before it, like French *bon*. Compare: ہاں hāṉ (yes) vs ہا. میں maiṉ, ہیں haiṉ, کہاں kahāṉ, یہاں yahāṉ are among the twenty most common words in Urdu.
""",
        11: f"""
## Sight words
These twenty words are 30–40% of any Urdu text. Learn them as whole shapes; audio in `assets/audio/sight/`.

{' · '.join(D['sight_words'])}

## Marks come off
Read the unit 1–10 word lists again in `assets/images/words/*_nastaliq.png` — now without vowel marks. Rule: if you can already decode a made-up word (nonword) without marks, you are ready; if not, stay on marked text one more week.

## Naskh → Nastaliq
Every card exists in both styles (`*_naskh.png` and `*_nastaliq.png`). Put them side by side. What moves: letters stack diagonally from upper-right to lower-left; dots slide along the stroke; the final ی and ے drop below the line. What never changes: the letter identity, the order, the dots' count.

## Dictionary order
Course order was chosen for speed. Dictionaries use this order:
ا ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ہ ھ ء ی ے
""",
        12: """
## Reading test (EGRA-style, 10 minutes, one-to-one)
Timing is per subtask, 60 seconds each unless stated. Stop a subtask after 10 consecutive errors.

1. **Letter sounds** — 100 letters in random order (`assets/images/letters/*_nastaliq.png`). Score: correct letter-sounds per minute.
2. **Nonwords** — 50 made-up words (e.g. نَبَل، تیمو، کُدار). Score: correct per minute. This is the anti-memorisation check.
3. **Familiar words** — 50 words from units 1–11 in Nastaliq, no marks. Score: correct per minute.
4. **Passage** — read the unit 11 passage aloud (about 60 words). Score: correct words per minute (cwpm).
5. **Comprehension** — 5 questions on the passage, asked orally.

| cwpm | Level |
|---|---|
| > 90 | exceeds grade-2 standard |
| 60–90 | meets standard |
| 1–59 | below standard: repeat units flagged by subtasks 1–3 |
| 0 | nonreader: restart at unit 1 |

Record results in the app's progress screen or on paper. Retest after four weeks.
""",
    }


def main():
    os.makedirs(f"{ROOT}/course", exist_ok=True)
    sp = special_units()
    taught = set()
    for u in U:
        md = unit_md(u, taught)
        if u["n"] in sp:
            md += "\n" + sp[u["n"]]
        open(f"{ROOT}/course/unit_{u['n']:02d}.md", "w", encoding="utf8").write(md)
        taught |= set(u["letters"])
    print(f"wrote {len(U)} unit files")


if __name__ == "__main__":
    main()
