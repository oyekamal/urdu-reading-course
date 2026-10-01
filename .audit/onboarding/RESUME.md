# RESUME: onboarding + "make it attractive like Finch" gauntlet (2026-09-30)

## Done and pushed
- b45ef70 onboarding flow (`mobile/src/onboarding.js`), blind vs Finch: round 1 2-2, round 2 4/4 wins.
- This commit: app visual pass.
  - Unit art: `scripts/pack_images.py` now makes unit art transparent + trimmed; shown bigger (`.art-disc` 132x112).
  - Primary buttons docked at the bottom in lessons (`.lesson` flex layout) and the onboarding demo.
  - LottieFiles animations (downloaded, not made): `mobile/public/lottie/*.json`, credits in `CREDITS.md`, player `mobile/src/fx.js` (lottie-web light; `fx(name,{size,loop})`, `burst()`). Preview page in `.audit/lottie/preview.html`. SW caches them (`lottie/list.json`, VERSION urc-v0.9.0).
  - Full-screen celebration on lesson finish (`path.js` finish → `.celebrate`, gold for unit complete), home scene header (`learner.js` today → `.home-scene`), night-scene empty Review, coral/peach accent, teaser (not grey) locked units, pearls + streak counters (`session.js` pearls()/streak()), onboarding records day-1 attempt so the streak is real.
  - Lessons: patterned warm background, Marko bounces when audio plays (`content.js` play adds `.talk`), correct tile pops.

## Blind critic rounds, in-app look vs Finch (bar = `.audit/onboarding/bar/` 36 frames + store/)
- r3: Finch wins clear (flat utility look). r4: Finch wins SLIGHT. Gaps named: (1) Marko reuses one pose → more poses; (2) home should be a painted scene; (3) lesson screen more alive.
- r5 NOT RUN YET. Gemini poses + scenes GENERATED, checked by eye (all on-model, no fake glyphs) and PACKED (commit after a50c5e9).

## In progress when the session stopped
- Gemini art generation: `design/gen/gen_assets.py poses2` (mascot_trophy/clap/proud/surprised/heart/fire/wave2/letter) and `scenes` (scene_home_morning/evening). Logs `design/gen/gen_poses2.log`, `gen_scenes.log`. Output `design/gen/out/`.
- The code ALREADY references these (mascot('trophy'|'clap'|'proud'|'heart'|'surprised'|'letter'), `img/scene_home_*.webp`). Until they are packed, those images 404 (mascot poses show broken; the scene falls back to the sky colour).

## Next steps
1. (done) art generated + packed.
2. (done).
3. Dev server `cd mobile && npx vite --port 5188`; screenshots: `python3 tools/onb_shots.py 5188 <out>` and the in-app capture snippet (Just me → path → lesson → done → unit done → letter → units → review), then blind strips vs Finch (`36_home_first_view, 33_day_streak_1, 32_day1_greeting, store/iphone_01,03,05`) and a fresh harsh critic subagent (format: WINNER/MARGIN/WHY/TOP 3 GAPS). Loop until ours wins.
4. `npm run build`, sync `reader/` (copy of mobile/dist) + APK (`npm run apk`), bump version, push. Progress page: https://claude.ai/artifact/EhyVf4FbnuKPA2kVKeUjMx (source `.audit/onboarding/progress.html`, images `.audit/onboarding/site/`).

## 2026-10-01: parallel agents launched (Kamal: "go for it, use parallel agents")
- Agent A, Marko rig: design/marko-rig/make_marko.py → mobile/public/lottie/marko_<state>.json (idle talk cheer wave think listen sleep point) + mobile/src/marko.js `marko(state,size)` / `setMarko(el,state)`. NOT wired into screens yet: lead wires it after (replace mascot() calls where it should move).
- Agent B, QA + consistency: drive_all sweep, new mobile/tools/ui_audit.py (tap targets, docked primary, overflow), "Play again" placement, emulator APK check. Fixes in mobile/src (not the marko files).
- After both: wire marko(), gauntlet r5 vs Finch, rebuild reader/ + APK, commit + push.
- 2026-10-01 Agent A DONE: 8 Marko Lottie states (cut-out rig from Gemini parts, ~50 KB each), critic "same character: yes" round 3. API: `import { marko, setMarko } from './marko.js'`. Preview: serve repo root on 5302, /design/marko-rig/preview.html. Known: think/point arms look tube-like; sleep stands (PNG sits). Waiting for QA agent before wiring (QA owns the screen files).
- 2026-10-01 QA pass committed baf22c0; animated Marko wired (next commit). Next: drive_all + ui_audit re-run, gauntlet r5, APK.
- 2026-10-01 r5: Finch clear. r6 (after a5bc7a7): Finch SLIGHT. Critic says our celebrations now beat Finch's. Remaining gaps: (1) home: Marko 2-3x bigger, centred in the scene, one "today" card above the fold, CTA not covering the next card; (2) tab bar: coloured filled icons, playful selected state, 4 tabs for children (ASK Kamal: nav change); (3) Marko peeking on locked units, pearl necklace collectible, fix unit-title wraps. drive_all 0-12 passes (25s wait). Also still to do: rebuild reader/ + APK.
- 2026-10-01 Kamal decided: child track gets 4 tabs (Learn, Review, Read, Me = Progress+More; Units reachable from Learn); adults keep 6.
- Round 7 agents launched: 7a (learner.js/icons.js/main.js/tools: child nav, coloured tab icons, home rebuild with big centred Marko + one today card, units title wraps + peeking Marko); 7b (path.js: locked-card Marko peek, pearl necklace thread + pop, Marko on every lesson kind). Then: lead commits, critic r7, reader/ + APK.
- 2026-10-01 09:10 PAUSED by Kamal (going outside). Round 7a agent stopped mid full-sweep; its changes (child 4-tab nav, coloured tab icons, home rebuild, ui_audit nav fix) are UNVERIFIED and parked on branch `wip/round7a` (pushed), NOT on main. To resume: `git checkout wip/round7a`, run `cd mobile && python3 tools/ui_audit.py 5188 /tmp/claude-1000/qa7` and `PORT=5188 python3 tools/drive_all.py` (child + adult profiles), fix, merge into main, then gauntlet r7 (blind strips vs Finch), update the progress page, rebuild reader/ + APK.
- 2026-10-01 r7 (wip/round7a, ui_audit 0 violations): OURS WINS clear vs Finch. Confirmation round r8 (Finch real in-app frames only) running; full sweep running.
- 2026-10-01 DONE: v0.9.0 on main (merge 55b338b). Beats Finch in blind r7 + r8 (clear, r8 vs Finch's real in-app screens only). ui_audit 0 violations (child + adult), drive_all 0-12 COURSE COMPLETE, emulator verified (Marko shows a still pose instantly, then animates). reader/ PWA rebuilt. Debug APK at mobile/android/app/build/outputs/apk/debug/app-debug.apk. Not done: GitHub release / signed AAB (ask Kamal).

## 2026-10-01 afternoon: ROUND 9 — "more interactive" (Kamal pasted a talk on emotional design; research/18_emotional_design_talk.md)
- Bar = Duolingo's real lesson feel (frame SEQUENCES of correct/wrong/progress/complete/streak/home). Agent captures to `.audit/interact/bar/` + `DUOLINGO_FEEL.md` (gitignored).
- Agents running in parallel (file ownership): 9a `mobile/src/feel.js` (+main.js import, haptics dep, style.css block "round 9a: feel"): tap spring/ripple/tick/haptic everywhere, answer sparkle+chime / gentle boop, lesson-corner Marko coach, combo chip, WebAudio sounds, "Sounds and vibration" switch. 9b `path.js` + `learner.js` (style.css block "round 9b: progress + motion"): progress bar shine, count-ups, daily-goal ring, unit-unlock animation, 220ms transitions, tap-to-poke Marko, periodic wave.
- Child-safe rule: no streak-loss pressure, guilt copy, ads, purchase nudges, harsh buzzers.
- Lead steps after both report: commit each agent's files, run `ui_audit.py` (0 violations) + `drive_all.py` (COURSE COMPLETE), build blind SEQUENCE strips (ours via feel_seq.py/motion_seq.py vs Duolingo bar), fresh critic subagent per round until ours wins, rebuild reader/ + APK (`npm i` then `npx cap sync android` for haptics), bump to 0.10.0, push, update progress page.
- README updated for v0.9.0 (978de52). Emulator: visible window died with the session; Kamal could not see it on his laptop, so test via the web build https://oyekamal.github.io/urdu-reading-course/reader/ or a GitHub-release APK (needs Kamal's go).
- 2026-10-01 round 9 status: Duolingo bar captured (.audit/interact/bar/DUOLINGO_FEEL.md). 9a feel.js DONE (uncommitted: feel.js, main.js, package.json haptics dep, style.css block, tools/feel_seq.py; ui_audit 0). 9b progress+motion and 9c premium (premium.js/stickers.js/memory.js, drills.js tracing) were cut off by the spend limit and RESUMED at ~15:35. Nothing of round 9 is committed yet; tree builds. Next: when both report, commit by file, ui_audit + drive_all, sequence strips vs Duolingo, critic, APK (npm i; npx cap sync android).
- 2026-10-01 round 9 COMMITTED + PUSHED (4a4f274 feel, aeadea5 motion + 'days practised', 8f10155 premium). ui_audit 0, drive_all 0-12 COURSE COMPLETE (drive_all now waits for the two-beat celebration). Blind vs Duolingo real moments: correct-answer WIN, celebration WIN, wrong-answer LOSS (clear), home/premium LOSS (clear).
- Round 10 agents launched: 10a wrong answer (feel.js + answer parts of drills.js: green right tile + check within 150ms, Marko points, bubble hint, no red), 10b tracing UI chips + paper canvas + dotted guide, sticker book as a collection (progress shelf, embossed locked glyphs, foil), pressable depth. Then: commit, ui_audit, drive_all, re-run blind r10 strips (scripts: blind9 builder in this session = PIL strips of feel_seq/premium_seq frames vs .audit/interact/bar), APK (npm i; npx cap sync android), v0.10.0, update progress page + README, push.
