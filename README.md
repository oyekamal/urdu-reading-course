# Urdu Reading Course · اردو پڑھنا سیکھیں

A research-backed course and app that takes anyone, child or adult, Urdu speaker or not, from zero to reading Urdu script. Everything is generated from two data files, so a fix to a letter or a word flows into the cards, the printable lessons and the app.

**Try it now, no install:** the full learner + teacher app runs in the browser and works offline after the first load: https://oyekamal.github.io/urdu-reading-course/reader/ (add it to your home screen). The original single-page course is at https://oyekamal.github.io/urdu-reading-course/app/. Android APK: see Releases. Current version: **v0.10.0** (adds the interactivity pass on top of the v0.9.0 onboarding, animated Marko and look; see [Onboarding, Marko and the look](#onboarding-marko-and-the-look-v090) and [Interactivity and emotional design](#interactivity-and-emotional-design-v0100)).

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
| `mobile/` | The app source (Capacitor 7 + Vite): first-run onboarding, learner, parent and teacher modes, animated Marko, offline, one APK |
| `design/` | `gen/` Gemini art pipeline (Marko poses, unit art, village scenes); `marko-rig/` the Lottie cut-out rig that animates Marko |
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

Since v0.8.0 every one of the 490 clips is **ElevenLabs** (`eleven_v3`, voice "Sara", Urdu), replacing the local MMS-VITS voice (`research/06_tts_bakeoff.md`, still used by `gen_audio.py`). How it was chosen and checked, with a blind Gemini listener as the critic and native-teacher recordings from Rekhta Aamozish as the bar (evaluation only, never shipped):

- **Correctness:** Gemini picks which of the 39 letter names it hears. Sara 36/38, the real teacher 36/38, the old MMS voice 21/36.
- **New vs old, blind A/B on every clip:** the new voice won 378/489 in round 1. The rest were re-rolled with the judge in the loop, and the handful that were genuinely wrong (a wrong word, a short vowel) were re-rolled until they passed.
- **Against the real teacher:** the new voice still loses on warmth, 9/39 on letter names. Slowing the audio, changing the cut and trying other voices did not close that gap. A human recording (below) or a cloned consenting teacher's voice is what beats it.

Short items (letter names, syllables, short words) are spoken inside a carrier phrase, «یہ ہے... X۔», and the target is cut on silence: `eleven_v3` returns empty timestamps for Urdu, and a bare letter name comes out garbled. Clips ship as 22.05 kHz mono mp3; in a blind test the critic could not tell them from 44.1 kHz (18/39), and they are half the size.

```bash
python3 scripts/el_audio.py build --judge                  # (re)generate everything not recorded by a human
python3 scripts/el_audio.py audition <voice_id> names/jim  # try a voice on a few clips, into assets/audio/_el/
python3 scripts/listen_judge.py identify clip.mp3          # blind "which letter is this?"
python3 scripts/listen_judge.py ab "جیم" a.mp3 b.mp3       # blind A/B, prints winner + biggest gap
```

Keys go in the repo `.env` (gitignored): `ELEVENLABS_API_KEY`, `GEMINI_API_KEY`. Voices live in `data/voices.json`. Per-clip provenance (`method`, `voice`, `frame`) is in `data/audio_overrides.json`, and human recordings are never overwritten.

## Recording a human voice

`assets/audio/manifest.json` (built from `data/letters.json` + `data/units.json`) is the source of
truth for every one of the **490 clips** the app plays: 39 letter names, 39 letter example words, 90
syllables, 11 aspirate words, 12 vowel-mark items, 220 unit words, 33 sentences, 20 sight words, 10
numerals, 16 app-voice phrases.

**Voice Studio: generate with ElevenLabs or record your own voice, one line at a time:**

```bash
python3 scripts/voice_studio.py        # opens on http://localhost:8420/
```

Each line has an ElevenLabs row: pick a voice, **Generate** (`g`), **Re-roll** (`r`), play the take, and **Keep take** (`k`) to put it into the app. **+ Voice** adds a voice by pasting its ElevenLabs ID or by searching the ElevenLabs library ("urdu") and pressing Add. A badge on each line shows where its current audio came from: your voice, ElevenLabs or MMS.

Recording is a local, one-file tool (stdlib + the pipeline `import_recordings.py` already uses — nothing new to
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
- **No emoji.** Icons are inline SVG (`mobile/src/icons.js`). Marko the markhor (Pakistan's national animal, 16 static poses, animated since v0.9; v0.6 used a parrot, dropped as too close to Duolingo) and 13 unit illustrations were generated with Gemini in one flat-vector style (`design/gen/gen_assets.py`, palette-locked prompt + reference image), then packed to WebP by `scripts/pack_images.py` into `mobile/public/img/` (425 KB total, precached by the service worker).

Re-generate art: `cd design/gen && python3 gen_assets.py mascot|units` (needs `GEMINI_API_KEY`), then `python3 scripts/pack_images.py`.
Screenshots for review: `cd mobile && python3 tools/shots.py <vite-port> ../.audit/ui`.

## Onboarding, Marko and the look (v0.9.0)

Built with the [app-onboarding-questionnaire](https://github.com/adamlyttleapps/claude-skill-app-onboarding-questionnaire) skill and gauntlet-looped (builder plus a separate harsh critic, blind side-by-side) against **Finch: Self-Care Pet**, a loved consumer app whose pet is born from your answers. Result: the onboarding beat Finch in all four segments, and the in-app look beat Finch's real in-app screens in two blind rounds in a row (rounds 7 and 8). The trail, with every round's verdict, screenshots and the bar, is in `.audit/onboarding/` (start at `RESUME.md`).

**First run (`mobile/src/onboarding.js`, 17 screens):** Marko is asleep and you wake him, pick his lucky colour (it becomes the learner's badge), then answer who is learning, the name, why Urdu, how much Urdu they speak, whether they read any letters, and what has made it hard. Marko replies to every answer. The plan screen mirrors the answers back, a ring loader names them while it "builds the path", then a real mini lesson: hear and tap ا and ب, join them into با, read **بابا** and pick it from با by ear. The learner earns a shareable first-word card, a day-1 streak (earned by reading, never guilt) and a days-in-a-row promise. "My class" goes to teacher setup; "I can read some letters" goes to the placement check. Answers resume if the app is closed mid-way.

**Marko (`mobile/src/marko.js`, `design/marko-rig/`):** 8 animated states (idle with breathing and blinking, talk, cheer, wave, think, listen, sleep, point), each about 50 KB of Lottie JSON built as a cut-out rig from Gemini-drawn head, body and arm parts with vector eyes and mouth. Static Marko images anywhere in the UI are upgraded in place; he talks whenever audio plays and shows a still pose instantly while the animation loads. Preview: serve the repo root and open `design/marko-rig/preview.html`.

**Look and feel:** full-screen celebrations (sunburst, confetti, pearls bursting out, a trophy and fireworks for a finished unit), a painted village home with Marko in it, a pearl necklace that gains a pearl after every lesson, locked units with Marko peeking out, a night-time Review, four tabs for children (Learn, Review, Read, Me) and six for adults, one big bottom-docked primary button on every screen, one standard round speaker button for every "play again". Free animations (confetti, stars, tick, flame, trophy, sparkles, hearts, sun, sleeping Z's) are downloaded from LottieFiles, whose terms put free animations under the Lottie Simple License (not verified page by page); titles, authors and URLs are in `mobile/public/lottie/CREDITS.md`, and `mobile/src/fx.js` plays them.

**QA tools:** `mobile/tools/ui_audit.py <port> <outdir>` walks about 60 screens at 390x844 and checks tap-target sizes, overflow, a docked primary action, content under fixed bars and contrast (0 violations on child and adult profiles); `mobile/tools/drive_all.py` plays units 0 to 12 end to end; `mobile/tools/onb_shots.py` screenshots the onboarding. Run the dev server with `cd mobile && npx vite --port 5188`.

Re-generate Marko art: `cd design/gen && python3 gen_assets.py mascot|poses2|scenes|units` (needs `GEMINI_API_KEY`), then `python3 scripts/pack_images.py`. Rebuild his animations: `python3 design/marko-rig/make_marko.py`.

## Interactivity and emotional design (v0.10.0)

Brief: a talk on emotional design ([`research/18_emotional_design_talk.md`](research/18_emotional_design_talk.md)) argues that products win on how they feel (Duolingo's animated mascot and feedback loops, Phantom's polish as trust, Revolut's tactile, light-catching details). We gauntlet-looped it against **Duolingo's real lesson moments** (frame sequences captured from public recordings, notes in `.audit/interact/bar/DUOLINGO_FEEL.md`, gitignored because of size). Final blind result, four comparisons, ours won all four clearly: correct answer, wrong answer, lesson-complete celebration, home and premium details. Round-by-round trail and screenshots: `.audit/onboarding/RESUME.md` and `.audit/onboarding/progress.html`.

**Feel (`mobile/src/feel.js`):** every tap gets an instant press spring, ripple, tick and haptic. A right answer hops, rings and sparkles, plays a rising chime and Marko cheers; "N in a row" chips pop and the progress bar warms from gold to orange. A wrong answer is kind and instantly recoverable: the right tile turns green with a check, the tapped one softens with an amber outline and a small wobble (never red), a bubble says what to look for ("Count the dots: ب has one"), and Marko reacts. Sounds are synthesised in WebAudio (no files); haptics use `@capacitor/haptics`; a "Sounds and vibration" switch lives in Me.

**Motion (`path.js`, `learner.js`):** lesson progress bar with a sparkling head, count-ups for pearls, minutes and days, a daily-goal ring that celebrates when reached and says nothing when missed, a two-beat lesson-complete reveal, a unit-unlock animation, tap-to-poke Marko on the home screen, quick screen transitions.

**Premium (`premium.js`, `stickers.js`, `memory.js`, `drills.js`):** glowing-ink tracing on a paper canvas with a dotted guide, start dot and arrow; a sticker book (one deterministic sticker per mastered letter, embossed locked slots, foil, progress shelf, tabs per unit) with a flip reveal; light-catching pearls and tiles that follow the pointer or device tilt; a parallax village with drifting clouds by day and fireflies after dark; Marko lines built from real progress ("Yesterday we met ب").

**Child-safe rules (deliberate):** no hearts or lives, no leaderboards, no streak-loss pressure (the counter is "days practised" and only ever goes up), no guilt copy, no ads or purchase nudges, no red failure states, no random loot.

**More QA tools:** `mobile/tools/feel_seq.py`, `motion_seq.py`, `premium_seq.py` and `finish_seq.py` record timed frame sequences; `ui_audit.py` (0 violations) and `drive_all.py` (units 0 to 12, waits for the two-beat celebration) as before. Android: after `npm install` run `npx cap sync android` so the haptics plugin is linked.

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
