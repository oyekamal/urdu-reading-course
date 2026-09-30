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
