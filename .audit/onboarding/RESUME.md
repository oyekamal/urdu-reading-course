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
