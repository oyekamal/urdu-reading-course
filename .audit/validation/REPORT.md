# Urdu Qaida v0.10.0: validation report, "what are we missing"

Date: 2026-10-02. Four read-only test passes, each with its own `results.md` (evidence, repro, one-line fix):
`a11y_devices/` (accessibility and device shapes), `perf_robust/` (performance, offline, robustness, privacy), `content_learning/` (content integrity and learning logic), `competitive/` (feature gaps vs similar apps).

**Mobbin:** the official MCP (`https://api.mobbin.com/mcp`) is registered at user scope but not signed in, so the competitive pass used public sources only (store listings, review sites, a 2025 study of deceptive design in kids' apps, Google Play Families policy). Re-run it with real Mobbin screens after signing in (`/mcp`, choose mobbin, Authenticate; paid plan).

**Not tested:** a physical phone (TalkBack, real Android back gesture, soft-keyboard PIN entry), iOS Safari, real disk-quota exhaustion. Urdu grammar and gloss judgements below are an AI's and need a native speaker.

## What passed
- All 490 audio keys exist as files; 0 orphans, 0 unplayable clips; every unit word decodable (bare and vowelled) from letters taught by then.
- No missing glyphs in Naskh or Nastaliq; joiner flags agree with the shaping engine.
- Full drive of units 0 to 12 completes with no page errors; 419 audio-driven choice screens had the target exactly once; 110 unit-check questions clean; dictation accepted 15/15 correct spellings and rejected 15/15 near-misses.
- Leitner intervals and demotion correct; "days practised" counts correctly; unit check passes at exactly 8/10 and stays passed.
- Zero third-party hosts in 48 requests; `npm audit` 0 vulnerabilities; two children on one device stay isolated; 10,000 attempts render fast; offline onboarding, lessons and audio work; export then import is lossless (36/36 records).
- Reduced motion removes all animation; dark mode and Urdu rendering (Naskh, Nastaliq, scale 1.5) show no breakage; no sideways overflow at any viewport; nearly all tap targets at least 44 px.

## P0: fix now (small, and they are bugs, security issues or wrong teaching)
| # | Finding | Evidence | Fix |
|---|---|---|---|
| 1 | A learner name runs as code (HTML in a name executes on Today); no CSP. A hostile backup file can use the same route. | perf_robust | Render names with `textContent`/escape everywhere; add a CSP meta tag. |
| 2 | Backup import is unsafe and hard to find: corrupt files fail silently, a file can overwrite `teacherPin` and `mode` (PIN set to 0000 in the test); a fresh install has no restore option. | perf_robust, competitive | Validate and whitelist keys on import, show errors, add "Restore" to the first screen and Me. |
| 3 | The web (PWA) version never updates: live `sw.js` says `urc-v0.9.0` while serving the v0.10.0 bundle. Android APK unaffected. | perf_robust | Bump the SW version, derive it from the build. |
| 4 | Two keyboard handlers return `false` for every other key: teacher PIN field rejects hardware-keyboard typing; sticker book cannot be tabbed or activated. | a11y (stickers.js:65, main.js:100) | Handle the key, do not return the comparison. |
| 5 | 24 of the 75 "Count the dots" hints are false (ٹ ڈ ڑ counted as one dot, ئ as one, ی shown with two dots when the tile has none). We teach children wrong facts. | content_learning | Fix the DOTS table and derive hints from the displayed glyph. |
| 6 | Three of 11 "Breath letters" play buttons are silent (ṭh, ḍh, ṛh): the audio key replaces every non-ASCII character with `_`; table ids collide too. | content_learning | Use explicit ids per aspirate. |
| 7 | A child can wipe their own progress (Reset on the Me tab, single confirm). The parent gate is single-digit addition and guards only the WhatsApp link. | perf_robust, competitive | One spelled-out-number gate sheet for Reset, backup/restore, report, links, settings. |
| 8 | Double-tap skips screens; double-tapping the onboarding button skipped "Who is learning?" and created an adult as a child profile. | perf_robust | Lock buttons after first activation (debounce in `go`/`next`). |
| 9 | Database failures hang the app ("Loading…" forever, frozen lesson finish). | perf_robust | try/catch around boot and writes, show a recover/retry screen. |
| 10 | Locked units open from the Units tab after one `confirm()`, can be passed, and add 138 never-learned review cards while Learn still shows Unit 0. | content_learning | Block locked units (or open only as read-only preview). |
| 11 | The celebration "Next" button is off-screen and unreachable at 320x568, in landscape and at 200% text. | a11y | Make the overlay scrollable or dock the button inside the viewport. |
| 12 | EGRA scoring traps: forgetting "Mark last word reached" turns 12 words in 60 s into 52 cwpm; an accidental Finish gives about 3120 cwpm; comprehension 0/5 still says "meets standard". | content_learning | Require the mark, clamp, and gate the band on comprehension. |

## P1: major quality
- **Marko drains the phone:** two Lottie instances use about 50% of the main thread on an idle Today; 24 fps at 6x slowdown. Pause when hidden/offscreen, one instance, lower frame rate, or the canvas renderer.
- **Teacher mode fails offline on first use** (SW precaches from `index.html` only; misses `teacher-*.js`, chunks, lesson markdown).
- **First load is heavy:** 614 KB Nastaliq font before content; SW pulls about 5.8 MB eagerly (Lighthouse performance 0.67 simulated, LCP 5.7 s). Lazy-load Nastaliq and audio.
- **Large text:** the "Extra large" Urdu setting does nothing on most screens (fixed px sizes win); 130% and 200% text break Today's Start button, bubbles, unit titles and play buttons.
- **Landscape phone is nearly unusable** in drills (about 100 px of height left). Lock to portrait or add a landscape layout.
- **Screen readers:** wrong answers are silent (correct ones announce); Urdu text lacks `lang="ur"`; the celebration is not a dialog; focus is lost after Continue; the active tab is not exposed.
- **Contrast fails:** onboarding step text 2.0:1, celebration chip 2.7:1, dark-mode active nav 4.3:1, unit pill 2.3:1, gold focus ring 1.85:1.
- **Kid ergonomics:** the leave-lesson ✕ sits 8 px from the speaker button and exits without confirmation; "Next word" touches tiles; colour swatches are 40 px.
- **Placement is weak:** draws 6 targets with replacement (some letter never asked in 98% of attempts for units 1 and 8), tests letter names only, a learner missing one letter still passes about 80% of the time.
- **Unit-9 blend:** ض ظ ذ all sound /z/; about 23% of rounds contain two or more identical-sounding options.
- **Content errors for a native speaker to confirm:** six sentences use letters not yet taught; `میں ٹوپی لے` ungrammatical; `تین کتاب` should be `تین کتابیں`; `تکیا` vs `تکیہ`; ذ and ض share the romanisation `ẕ`.
- **Test contamination:** 4 of 8 reading-test sentences also appear in the unit-11 practice passage; the 52-word test passage contains 17 never-taught word types.
- **Tracing checks pixel coverage only:** alif drawn bottom-to-top or ten random dashes both pass; a straight alif on the centre line is rejected.
- **Housekeeping:** `allowBackup` on, INTERNET permission unused, privacy policy out of date (mentions GitHub, omits the donate card); home screen leaks about 50 KB/min; a 300-character name overflows the page; WhatsApp asks the gate twice; Android back gesture likely exits the app.

## P2: missing features (what similar apps have and we do not)
Ranked by impact on a 5 to 10 year old and their parent against effort; evidence in `competitive/results.md`.
1. Illustrated decodable stories with audio and comprehension questions (Duolingo ABC, Khan Kids and the top Urdu competitor have them; our whole path has 272 running words).
2. Opt-in parent-set reminders (local notification addressed to the parent, no guilt copy).
3. Read-aloud / speaking practice with feedback; stroke-order-aware tracing; mistakes in lessons feeding spaced repetition.
4. A human (or consented cloned) voice; a calm "welcome back" screen.
5. Family dashboard (the rich one exists only in teacher mode) and co-play prompts for parents who cannot read Urdu.
6. Urdu/English interface toggle with RTL handling.
7. Tablet layout; home-screen widget.
8. A no-fail "letter pop" free-play toy; Marko accessories for the sticker collection.
9. Real-device TalkBack pass; Play Data safety and Families declarations.

## Where we beat the market (do not over-correct)
Real Urdu script teaching with Naskh and Nastaliq; fully offline with no ads; teacher mode with the EGRA reading test; child-safe motivation design (no lives, no loss streaks); audio quality; the Marko feel.

## Suggested order
1. P0 in one pass (12 small fixes), re-run `ui_audit.py` and `drive_all.py`, ship v0.10.1.
2. P1 in parallel agents by file (performance, large text/landscape, a11y, content corrections with a native speaker).
3. P2 as separate projects after Kamal picks priorities.
4. Sign in to Mobbin and re-run the competitive pass with real screens.
