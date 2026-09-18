# Urdu Reading Course · اردو پڑھنا سیکھیں

A research-backed course and app that takes anyone, child or adult, Urdu speaker or not, from zero to reading Urdu script. Everything is generated from two data files, so a fix to a letter or a word flows into the cards, the printable lessons and the app.

**Try the app:** open `app/index.html` (or the GitHub Pages link in the repo description). It runs offline once loaded, with audio for every letter, word and sentence.

## What is in the box

| Path | What |
|---|---|
| `app/` | The interactive course: 13 units, drills (tap what you hear, tile word building, tracing, dictation, quiz gate), progress, Naskh/Nastaliq switch, three tracks, EGRA-style reading test. Single HTML file plus `audio.json`. |
| `course/00_design.md` | Every design decision with the evidence behind it, the unit map, hours per unit |
| `course/unit_00.md … unit_12.md` | Printable lessons with answer keys and pen-movement guidance |
| `data/letters.json` | 39 letters, aspirates, vowel marks, long vowels, sight words, numerals, assessment passage: the single source of truth |
| `data/units.json` | 13 units, 220 decodable words (bare and vowelled), 33 sentences |
| `data/tatoeba_urd_freq.json` | Letter and word frequencies from 2,851 Tatoeba Urdu sentences; drives the teaching order |
| `data/audio_overrides.json` | Per-clip rendering choices made by a human listener |
| `assets/images/` | 616 PNG cards (letters, positional forms, look-alike contrasts, vowelled words) in Naskh and Nastaliq |
| `assets/audio/` | 474 clips (mp3): letter names, example words, CV syllables, aspirates, vowel marks, every unit word and sentence, sight words, numerals |
| `assets/fonts/` | Noto Nastaliq Urdu and Noto Naskh Arabic (SIL OFL) |
| `research/` | Eleven cited research files: quality bar, books, apps, script reference, pedagogy, open assets, TTS bake-off, offline literacy apps, teacher tools, tech stack, learning design |
| `docs/offline-app-plan.html` | Product and architecture plan for the offline Android app (learner, teacher, parent modes) |
| `mobile/` | The Android app (Capacitor 7 + Vite): learner, parent and teacher modes, offline, one APK |
| `scripts/` | The build pipeline (below) |
| `.audit/` | Decision log and the gauntlet-loop critic reports, kept for transparency |

## How the course is designed

- **Synthetic phonics spine.** Letter, sound, blend, decodable word, sentence. The USAID Pakistan Reading Project endline showed phonics-based Urdu instruction gaining 12.6 correct words per minute over control.
- **Letter order by frequency, then shape family.** Unit 1 is ا ب ک ل م ن, the letters that make the most real words fastest, from our own corpus count.
- **Look-alike letters taught together** (ب ت ن ی; پ ٹ ث; ج چ ح خ; د ڈ ذ; ر ڑ ز ژ) with contrast drills, because the error data says dot confusions do not fade on their own.
- **Ten non-joiners as a rule**, not exceptions: ا د ڈ ذ ر ڑ ز ژ و ے. The popular "seven" is wrong.
- **Vowel marks kept until unit 11**, then faded once nonwords decode.
- **Naskh first, Nastaliq in unit 11**, both always available. This one is an inference, and is labelled as such.
- **EGRA-style assessment** with the Pakistani grade-2 benchmarks: over 90 cwpm exceeds, 60 to 90 meets, under 60 below.

Full reasoning with citations: `course/00_design.md`.

## Rebuild after editing the data

```bash
python3 scripts/check_decodable.py   # every unit word uses only letters taught so far
python3 scripts/render_cards.py      # PNG cards (Pillow with libraqm), both scripts
python3 scripts/gen_audio.py         # local TTS (sharjeel103/mms-tts-urdu-finetune), CPU is fine
python3 scripts/verify_audio.py      # Whisper smoke test on concatenated chunks
python3 scripts/build_course.py      # course/unit_NN.md
python3 scripts/build_app.py         # app/index.html + app/audio.json
```

Audio repair loop: flag clips in `app/audio_check.html`, generate alternatives with `scripts/repair_candidates.py flags.txt`, pick in `app/repair_pick.html`, apply with `scripts/apply_picks.py picks.json`. Choices persist in `data/audio_overrides.json`.

Python needs: torch, transformers, soundfile, Pillow (with libraqm), openai-whisper, ffmpeg on PATH.

## Audio, honestly

The voice is machine-generated, locally, with an MMS-VITS Urdu fine-tune chosen by a Whisper-judged bake-off (`research/06_tts_bakeoff.md`). The models drop short-vowel marks, so ambiguous words were re-rendered inside a carrier phrase and cut out using the model's own letter timings; a human listener then picked the best rendering for 95 flagged clips. It is intelligible and good enough for a pilot. For a commercial product, record a native speaker: every successful offline literacy app ships human audio, and the base model's licence is CC BY-NC.

## Licences

- Code and scripts: MIT (see `LICENSE`).
- Course text, data and images: CC BY 4.0.
- Audio: generated with Meta MMS-TTS derivatives, CC BY-NC 4.0. Non-commercial use only.
- Fonts: SIL Open Font License 1.1. Word frequencies: Tatoeba, CC BY 2.0.

## Android app

Download the latest APK from the [Releases page](https://github.com/oyekamal/urdu-reading-course/releases) and install it (allow "unknown sources" for a debug build). Everything runs offline: no account, no server.

- **Just me / My family**: learner profiles, a 10-minute daily session (spaced review, then the next lesson step, then a timed read), the eight lesson steps per unit, a Leitner review deck, repeated reading with words per minute, progress, self-check speed test, Naskh/Nastaliq switch, three tracks, backup export and import.
- **My class**: teacher PIN, roster, a 40-minute lesson script per unit (I do, we do, you do), reading-level groups, the EGRA assessment (five subtasks with timers, stop rules, auto-scoring, bands), class reports with CSV and JSON export, parent slips.

Build it yourself:

```bash
cd mobile && npm install
npm run build && npx cap sync android
cd android && JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 ./gradlew assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```

Design and evidence: `docs/offline-app-plan.html`. Minimum Android 6 (API 23).

## Credits

Built by Kamil (Muhammad Kamal's agent) in September 2026, with three rounds of adversarial review against Georgetown's *Alif Baa*, Delacy's *Beginner's Urdu Script*, Duolingo's Arabic letters course and Rekhta's Aamozish. Evidence sources are listed at the end of each research file.
