# Urdu Reading Course

A research-backed course that takes anyone, child or adult, Urdu speaker or not, from zero to reading Urdu script. Everything here is generated from two data files, so a fix to a letter or a word flows into the cards, the lessons and the app.

## What is in the box

| Path | What |
|---|---|
| `research/` | Six cited research files: quality bar (Alif Baa, Delacy, Duolingo, Aamozish), books, apps, script reference (every letter, codepoint, IPA, joining rule), pedagogy (what the evidence says), open assets and licences, TTS bake-off |
| `course/00_design.md` | Every design decision with the evidence behind it, the 13-unit map, hours per unit |
| `course/unit_00.md … unit_12.md` | Printable lessons: hear, see, tell apart, join, read, write, dictation, check, with answer keys |
| `data/letters.json` | 40 letters + aspirates + diacritics + long vowels + sight words + numerals: the single source of truth |
| `data/units.json` | 13 units, 220 decodable words (bare and vowelled), 33 sentences |
| `data/tatoeba_urd_freq.json` | Letter and word frequencies from 2,851 Tatoeba Urdu sentences (drives the teaching order) |
| `assets/images/` | 616 PNG cards: letter cards, positional-forms cards, look-alike contrast cards, word cards, each in Naskh and Nastaliq |
| `assets/audio/` | 474 clips (wav + mp3): letter names, example words, CV syllables, aspirates, diacritics, every unit word and sentence, sight words, numerals |
| `assets/fonts/` | Noto Nastaliq Urdu and Noto Naskh Arabic (OFL) |
| `app/index.html` + `app/audio.json` | The interactive course: drills, tracing, dictation, quiz gate, progress, Naskh/Nastaliq switch, three tracks |
| `app/audio_check.html` | Listening page to flag any clip that sounds wrong |
| `.audit/` | Decision log and critic reports from the gauntlet loop |

## Run it

```bash
cd app && python3 -m http.server 8765      # then open http://localhost:8765/index.html
```

## Rebuild after editing the data

```bash
python3 scripts/check_decodable.py   # every unit word uses only letters taught so far
python3 scripts/render_cards.py      # PNG cards (PIL + libraqm, both scripts)
python3 scripts/gen_audio.py         # local TTS, sharjeel103/mms-tts-urdu-finetune (bake-off winner), CPU is fine
python3 scripts/verify_audio.py      # Whisper smoke test -> assets/audio/verify.json
python3 scripts/build_course.py      # course/unit_NN.md
python3 scripts/build_app.py         # app/index.html + app/audio.json
```

Python needs: torch, transformers, soundfile, Pillow (with libraqm), openai-whisper, ffmpeg on PATH.

## Licences and honesty

- Fonts: SIL Open Font License. Word/sentence corpus: Tatoeba, CC BY 2.0.
- Audio: generated with an MMS-VITS fine-tune (base model CC BY-NC 4.0; fine-tune licence unstated, treat as the same). Fine for a pilot; for a commercial client, record a native speaker or use a paid Pakistani TTS. See `research/05_open_assets.md`.
- The audio is machine voice. It was smoke-tested for intelligibility, not judged for accent. Use `app/audio_check.html` to flag bad clips.
- Design choices marked *inference* in `course/00_design.md` (Naskh-first, heritage-track speed) are reasoned, not proven.
