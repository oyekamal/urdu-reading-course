# Urdu Reading Course · اردو پڑھنا سیکھیں

A research-backed course and app that takes anyone, child or adult, Urdu speaker or not, from zero to reading Urdu script. Everything is generated from two data files, so a fix to a letter or a word flows into the cards, the printable lessons and the app.

**Try it now, no install:** the full learner + teacher app runs in the browser and works offline after the first load: https://oyekamal.github.io/urdu-reading-course/reader/ (add it to your home screen). The original single-page course is at https://oyekamal.github.io/urdu-reading-course/app/. Android APK: see Releases.

## What is in the box

| Path | What |
|---|---|
| `app/` | The interactive course: 13 units, drills (tap what you hear, tile word building, tracing, dictation, quiz gate), progress, Naskh/Nastaliq switch, three tracks, EGRA-style reading test. Single HTML file plus `audio.json`. |
| `course/00_design.md` | Every design decision with the evidence behind it, the unit map, hours per unit, the per-letter lesson shape |
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
| `mobile/` | The app source (Capacitor 7 + Vite): learner, parent and teacher modes, offline, one APK |
| `reader/` | Built web version of the same app, served by GitHub Pages as an installable PWA |
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
./scripts/sync_mobile_content.sh     # refresh the mobile bundle, then: cd mobile && npm run build
```

Audio repair loop: flag clips in `app/audio_check.html`, generate alternatives with `scripts/repair_candidates.py flags.txt`, pick in `app/repair_pick.html`, apply with `scripts/apply_picks.py picks.json`. Choices persist in `data/audio_overrides.json`.

Python needs: torch, transformers, soundfile, Pillow (with libraqm), openai-whisper, ffmpeg on PATH.

## Audio, honestly

The voice is machine-generated, locally, with an MMS-VITS Urdu fine-tune chosen by a Whisper-judged bake-off (`research/06_tts_bakeoff.md`). The models drop short-vowel marks, so ambiguous words were re-rendered inside a carrier phrase and cut out using the model's own letter timings; a human listener then picked the best rendering for 95 flagged clips. It is intelligible and good enough for a pilot. For a commercial product, record a native speaker: every successful offline literacy app ships human audio, and the base model's licence is CC BY-NC.

## Recording a human voice

`assets/audio/manifest.json` (built from `data/letters.json` + `data/units.json`) is the source of
truth for every one of the **490 clips** the app plays: 39 letter names, 39 letter example words, 90
syllables, 11 aspirate words, 12 vowel-mark items, 220 unit words, 33 sentences, 20 sight words, 10
numerals, 16 app-voice phrases.

**Voice Studio — record straight into the app, one line at a time:**

```bash
python3 scripts/voice_studio.py        # opens on http://localhost:8420/
```

A local, one-file tool (stdlib + the pipeline `import_recordings.py` already uses — nothing new to
install). Open it in Chrome or Firefox, type your name once, and for each of the 490 lines: press
**space** to record, **space** again to stop, **enter** to save and move to the next unrecorded line.
Every item shows the exact text to read plus a one-line note pulled from `recording/SCRIPT.md`'s own
guidance (read the vowel marks exactly as printed, say letter names the way Pakistani schools do,
numerals as spoken words, everything else in a calm "teacher voice"). Saved clips are converted,
silence-trimmed, peak-normalised and padded exactly like `import_recordings.py` produces them, written
straight to `assets/audio/<kind>/<id>.{wav,mp3}`, and marked `"method": "human"` in
`data/audio_overrides.json` — so this **is** the import step, not a separate one. Progress persists
across sessions (it's the same override file everything else reads); the sidebar shows a running
count per category and a green dot next to every line already recorded, which you can replay or
re-record any time. Run `python3 scripts/build_app.py` afterwards to bake new audio into the app.

Prefer one long take on a phone recorder instead? `recording/SCRIPT.md` still has the read-aloud
script and the "say the number, then the line twice" convention for that path, and `recording/script.csv`
the same rows as a spreadsheet — then:

```bash
# one file per clip, named <kind>__<id>.ext or just <id>.ext where that's unambiguous
python3 scripts/import_recordings.py --folder ~/recordings/session1 \
  --recorded-by "Ayesha Khan" --date 2026-09-18

# or one long take plus a start/end-seconds CSV (see recording/SCRIPT.md's own note on this)
python3 scripts/import_recordings.py --source ~/recordings/full.m4a --cuts recording/cuts.csv \
  --recorded-by "Ayesha Khan" --date 2026-09-18

python3 scripts/build_app.py   # rebuild app/index.html + app/audio.json with the new audio
```

`--dry-run` reports the match/coverage without writing anything. Each import converts to 16 kHz mono,
trims silence, peak-normalises to 0.9 and pads 0.15 s/0.25 s lead/tail — the same shape `gen_audio.py`
already produces — writes `assets/audio/<kind>/<id>.wav` + `.mp3`, and records
`{"method": "human", "recordedBy": ..., "date": ...}` in `data/audio_overrides.json` so `gen_audio.py`
never regenerates (and overwrites) an imported clip. Needs only python3, numpy, soundfile and ffmpeg —
nothing new to install.

**Licence effect:** the CC BY-NC restriction on audio (see below) exists only because the current voice
is a derivative of Meta's MMS-TTS model. A human recording carries no such restriction — once a clip's
`audio_overrides.json` entry says `"method": "human"`, that clip is the speaker's original performance
of CC BY 4.0 course text, and can be licensed the same as the rest of the course (credit the speaker by
name in `LICENSE`/`README.md` once a full pass is recorded).

## Licences

- Code and scripts: MIT (see `LICENSE`).
- Course text, data and images: CC BY 4.0.
- Audio: generated with Meta MMS-TTS derivatives, CC BY-NC 4.0. Non-commercial use only.
- Fonts: SIL Open Font License 1.1. Word frequencies: Tatoeba, CC BY 2.0.

## Design system (v0.6.0)

Researched first (`research/13_ui_reference.md`, `14_pakistani_visual_identity.md`, `15_asset_pipeline.md`), then built, then judged blind
against real Duolingo ABC and Khan Academy Kids store screenshots by a separate critic (`.audit/ui/`, trail in `.audit/decisions.tsv`).

- **Colour:** Multani turquoise `#1E9C8F` (one accent), saffron `#F2A93B` (progress, current pearl), ajrak indigo `#1E2F55` (ink), tile-glaze paper `#F2F7F6`; ralli red only for teacher-side warnings. Dark theme on indigo.
- **Type:** Fredoka (bundled, `mobile/public/fonts/Fredoka.woff2`) for display and buttons, system sans for body, Noto Nastaliq for Urdu headings, Noto Naskh for drills.
- **Signature:** lessons are pearls on a thread (موتیوں جیسی لکھائی). Done pearls fill turquoise, the current one glows saffron, locked ones stay paper. Each unit card wears a short ajrak stripe while current.
- **No emoji.** Icons are inline SVG (`mobile/src/icons.js`). Marko the markhor (Pakistan's national animal, 8 poses; v0.6 used a parrot, dropped as too close to Duolingo) and 13 unit illustrations were generated with Gemini in one flat-vector style (`design/gen/gen_assets.py`, palette-locked prompt + reference image), then packed to WebP by `scripts/pack_images.py` into `mobile/public/img/` (425 KB total, precached by the service worker).

Re-generate art: `cd design/gen && python3 gen_assets.py mascot|units` (needs `GEMINI_API_KEY`), then `python3 scripts/pack_images.py`.
Screenshots for review: `cd mobile && python3 tools/shots.py <vite-port> ../.audit/ui`.

## Android app

Download the latest APK from the [Releases page](https://github.com/oyekamal/urdu-reading-course/releases) and install it (allow "unknown sources" for a debug build). Everything runs offline: no account, no server.

- **Just me / My family**: learner profiles and a Duolingo-style path: one short lesson per letter (hear it, tap it among look-alikes, see where it sits in a word, trace it body-first, blend it with a vowel, 4-question check), then Join, Blend, Words 1, Words 2, Read and a Unit check that unlocks the next unit; Urdu voice instructions and a repeat button on the child track; a Leitner review deck, repeated reading with words per minute, progress, self-check speed test, Naskh/Nastaliq switch, three tracks, backup export and import.
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
