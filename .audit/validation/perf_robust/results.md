# Urdu Qaida v0.10.0: performance, robustness and safety validation

Date 2026-10-02. Read-only: no app source edited, nothing committed, emulator-5554 untouched.
Build under test: `mobile/` v0.10.0 (`npm run build`, served with `vite preview` on 5301, plain `http.server` on 5302 for SW tests, a throw-away SW update site on 5303). Live PWA https://oyekamal.github.io/urdu-reading-course/reader/ was read-only checked (headers, sw.js, offline walk). Dev server 5188 was used only for the non-destructive `ui_audit.py`.
Chromium 1243 headless, 390x844, DPR 2 (1 for some). Scripts in `scripts/`, raw output in `evidence/`.
Only things reproduced are reported. Items I could not test are listed at the end.

## Findings

### BLOCKER (PWA channel; the Play/APK build is not affected because Capacitor skips the SW)

**B1. PWA never updates: `sw.js` VERSION has not changed since v0.9.0.**
- Evidence: live `reader/sw.js` says `urc-v0.9.0` while `reader/index.html` serves the v0.10.0 bundle (`index-CTkYO871.js`); `git log -- mobile/public/sw.js` last touched it in a50c5e9 (v0.9.0 dev). The SW is cache-first for `index.html`, so a device that installed any earlier build keeps its old `index.html` + old hashed JS forever.
- Repro (`scripts/s4_swupdate.py`, site on 5303): install build A, swap the site to build B (new hashed JS, unchanged sw.js). Reload 3 times and also `registration.update()`: page still reports build A, cache still `urc-v0.9.0`. Same test with VERSION bumped: reload 1 still A, reload 2 and 3 serve B (update arrives one visit late, acceptable).
- Fix: derive VERSION from the build (Vite `define`/plugin writing the content hash into sw.js) so every release changes sw.js; add a "new version, tap to reload" toast on `controllerchange`.

### MAJOR

**M1. The two Lottie Markos eat about half the main thread on an idle Today screen.**
- Evidence (`s10_idle.py`, 1x CPU, 6 s idle on Today): main-thread busy 51 percent of wall time. Pausing CSS animations only: 46 percent. Pausing the Marko Lottie players: 0 percent. With `prefers-reduced-motion`: 0 percent. At 6x CPU (`s2_perf.py`): 23.9 fps, median frame 49.9 ms, 128 of 239 frames over 33 ms, 27 over 50 ms, 22 long tasks (1.3 s total, max 127 ms). At 1x: 58 fps.
- Impact: battery drain and jank on a low-end phone for the screen children see most.
- Fix: lottie-web renders the SVG every rAF at 60 fps; cap to about 20 fps (frame-skip with `setSpeed`/manual `goToAndStop` on a timer), pause the idle Marko after about 5 s (poke to wake) or when offscreen/`document.hidden`, keep one instance on Today.

**M2. Teacher mode does not work offline on first use (lazy chunk not precached).**
- Evidence (`s5_teacher_offline.py`): SW precache builds its list by regex over `index.html` `src/href`, so `assets/teacher-CIxQvURL.js`, `assets/web-*.js` (Capacitor web stubs) and `assets/index-BhFGqPXi.js` style chunks are not cached (7 of 10 hashed assets missing from `s3_cache_pyhttp.json`). Offline, "My class" then PIN then Unlock stays on the "Teacher PIN" screen; request `assets/teacher-CIxQvURL.js` fails. `data/lessons/unit_00..12.md` (13 files) are also not precached; `teacher.js:229` swallows the failure and shares empty text.
- Fix: precache `dist/.vite/manifest.json` entries (or glob `assets/*`) and `data/lessons/*`.

**M3. Stored XSS through the learner name, no CSP.**
- Evidence (`s7_robust.py`, names test): new learner named `<img src=x onerror="window.__xss=1">` then `window.__xss === 1` on the Today screen (name is interpolated into `innerHTML` in `main.js` home list and `learner.js` header; onboarding name screen escapes it correctly). No `<meta http-equiv=Content-Security-Policy>` in `index.html`.
- Impact: low alone (self-inflicted), but backup import (see M4) makes it a hostile-file vector, and in the APK the page has the Capacitor bridge (Filesystem, Share).
- Fix: render names with `textContent`/escape helper everywhere; add a CSP (`default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'`).

**M4. Backup import: silent failures, can overwrite the teacher PIN and device mode, and is undiscoverable on a new phone.**
- Evidence (`s6_data.py`): round trip itself is lossless (30 attempts, 3 cards, progress, profile: 0 missing, 36 records imported).
  - Corrupt file `{not json`: no toast, uncaught error. File `{"profiles":[null,...]}`: `Cannot read properties of null (reading 'id')`, no toast, import aborted half-way (`learner.js` import handler has no try/catch; the teacher.js one does).
  - A settings-only file `{"settings":[{key:'mode',value:'school',updatedAt:<future>},{key:'teacherPin',value:'0000',...}]}` flipped `mode` to `school` and set `teacherPin` to `0000` on the device. `importAll` merges the whole `settings` store, so a file can reset the PIN that guards the roster.
  - Fresh install after wiping the DB shows only onboarding: no restore/import option (`fresh_install_offers_restore: false`). You must create a throw-away learner, open More/Me, then import; afterwards the throw-away profile is still the active one.
- Fix: whitelist importable stores/keys (never `mode`, `teacherPin`, `activeProfile`, `deviceId`, `onb`), validate records, wrap in try/catch with a toast, add "Restore from backup" on the welcome and mode-choice screens.

**M5. "Reset this profile's progress" is reachable by the child with a single native confirm().**
- Evidence: child Me tab lists the button directly under Export (`evidence/s6_me_child.png`, button list in `s6_data.py` output); handler in `learner.js:204` is `if (!confirm(...)) return;` then deletes cards, attempts, sessions, assessments, progress. External links in the same tab are behind the arithmetic gate; this destructive action is not. No undo.
- Fix: put it behind the same grown-ups gate (and offer an automatic export first).

**M6. Database failure modes leave the app hung or bricked with no recovery path.**
- `tx()` in `db.js` handles `oncomplete`/`onerror` only, not `onabort`. Simulated quota abort on writes (`s8b_corrupt.py` (f)): finishing a lesson never shows the celebration, the child sits on the last screen forever (the awaited promise never settles).
- Malformed record (`progress.units = null`) (b): boot stops at "Loading..." permanently; page error `Cannot read properties of null (reading '0')`. Profile record without name (d): header reads "Good afternoon, undefined".
- `indexedDB` unavailable (e): "Loading..." forever, no message (page error `reading 'open'`).
- Dangling `activeProfile` (c) recovers correctly to the profile picker (passed).
- Fix: add `t.onabort`, a global error screen with "Try again / Export / Reset", and sanity-guard `getProgress` (`units ||= {}`).

**M7. Rapid double-tap skips screens (lesson Continue and onboarding CTA).**
- Evidence (`s7_robust.py`, `s8_more.py`): double-click on the lesson "Continue" moved the progress bar 0 to 67 percent (one click is about 33 percent), skipping a rule screen; `next()` only guards the final `finishing` step. Double-click on the onboarding colour-screen CTA saved step `i = 4` instead of 3, skipping the "Who is learning?" question; the name screen then reads "your child's name" with `who` unset, so the profile is silently created as family/child even for an adult. (Lesson completion itself is correctly guarded: pearls and `lessons` stay idempotent.)
- Fix: ignore clicks within about 400 ms of the previous advance (disable the CTA on first click) in `next()` and `go()`.

**M8. First run is heavy for a weak phone, and the SW then pulls 5.8 MB eagerly.**
- Lighthouse mobile preset (`lighthouse_mobile.report.html/json`, simulated Slow 4G + 4x CPU): performance 0.67, FCP 4.8 s, LCP 5.7 s (the `<h1>`), TBT 0 ms, CLS 0; accessibility 1.0, best-practices 1.0. Real CDP throttling (4x CPU, 1.6 Mbps, 150 ms RTT; `s1_first_run.py`): FCP 0.9 s, LCP 2.1 s, CLS 0.003 (0.029 through onboarding), 14 long tasks, max 192 ms.
- Why: the 614 KB `NotoNastaliqUrdu-Regular.ttf` is requested before content with `font-display:block` (welcome hero is Urdu text), followed by a serial waterfall: JS/CSS (0.37 s) then font (0.93 s) then 3 JSON (1.6 s) then Lottie/Fredoka/mascots (2.1 s).
- Bytes to reach the first lesson (transferred): JS 111 KB (349 KB raw, of which lottie_light 381 KB source), CSS 19 KB (84 KB raw), fonts 944 KB (Nastaliq 614 at boot + Naskh about 300 during onboarding), data 18 KB, Lottie 15 files 192 KB, images 30 files 366 KB, audio 6 clips 40 KB: about 1.65 MB.
- SW install precaches about 5.8 MB (audio 2.98 MB, fonts 0.94, img 0.79, lottie 0.61, assets 0.42, data 0.07) the first time the PWA is opened: 550 cache entries in 6.7 s locally, 70 s from GitHub Pages over this network; it competes with first-run rendering, no Wi-Fi/save-data check.
- Fix: `font-display:swap` + preload only the Naskh/Nastaliq actually used on screen (subset the Nastaliq, 614 KB is the whole font); start the SW precache after `load` + idle and skip on `navigator.connection.saveData`/cellular.

### MINOR

- **m1. Slow DOM/listener growth over time (15 min soak, `s2_perf.py 5301 15`).** Switching tabs and opening/leaving lessons in a loop for 15 min: `Memory.getDOMCounters` nodes 752 to 13,022 (about 830 per min), JS listeners 86 to 482 (about 26 per min), JS heap 5.0 to 6.6 MB (about 50 KB per min after forced GC). Live DOM stays 471 elements, Marko count stays 2, 0 canvases, 0 audio elements, timers capped at 9. A heap snapshot after 60 navs (`s9_detached.py`) shows 133 detached nodes: 3 retained copies of the home hero (Marko, parallax layers, counters) held by lottie mask/matte elements and closures. Not a user-visible problem in a 10-minute session; a long session on a low-RAM phone would feel it. Fix: `anim.destroy()` before removing the hero, and drop the node refs in the MutationObserver `reap`.
- **m2. Very long name breaks layout.** 300-character name: `scrollWidth` 8196 px at 390 px viewport (`evidence/s7_name_*.png`). No `maxlength` on the add-learner input. Emoji/ZWJ and RTL names render fine; whitespace-only name is rejected with a toast.
- **m3. WhatsApp button asks the grown-up question twice.** `learner.js:209`: `wa.onclick` prompts, then calls the local `open()` which prompts again (reproduced: two prompts, then one `window.open('https://wa.me/...', '_system')`). Donate asks once.
- **m4. The grown-ups gate is single-digit addition** (a is 3..8, b is 2..8, sums 5..16) using native `prompt()`. A 7 to 10 year old can pass it, which is the target age; Play Families wants a gate a young child cannot pass. Use two-digit multiplication or a hold-and-confirm, and make it a custom dialog.
- **m5. Android flags to decide before Play.** `android:allowBackup="true"` (WebView IndexedDB, including the child's first name, goes into Google Auto Backup although the privacy policy says "on the device only"); `INTERNET` permission is declared but nothing in the app makes network requests (links open via `_system`/intent), so it can go; `file_paths.xml` has `<external-path path=".">` (whole external storage) though the provider is not exported; `minifyEnabled false`; no CSP. Passed: no `usesCleartextTraffic`, `allowMixedContent:false`, no WebView-debug flag in capacitor config (`android:debuggable` appears only in the debug manifest), only the launcher activity and the AndroidX `ProfileInstallReceiver` (permission-protected) are exported.
- **m6. Privacy policy (docs/privacy.html) no longer matches the app.** It says the Help links open "WhatsApp or GitHub" (no GitHub link remains) and says "no in-app purchases" but does not mention the Easypaisa donate card/intent; it says data is "on the device only" (see m5 backup). `deviceorientation` is read for the parallax tilt (`premium.js`), not mentioned.
- **m7. Backup contains the teacher PIN in plain text in school mode** (settings store is exported whole) and goes to the share sheet.
- **m8. Build hygiene.** `npm run build`: warns that three font URLs are unresolved at build time (fine, runtime URLs) and that `content.js` is both statically and dynamically imported (the dynamic import does not split). `dist/` publishes `lottie/preview.html` and `lottie/CREDITS.md` and the SW's `img/list.json`/`lottie/list.json` are not themselves cached. `icon-192.png`/`icon-512.png` are not in the precache list, so the favicon and install icon request fails offline. Lighthouse: unused JS 76 KiB (lottie), unused CSS 18 KiB.
- **m9. Clock moved back hides due cards.** With the device date 3 days (or 400 days) in the past, Review shows "All caught up" until the real time catches up, because `due` is an absolute timestamp. "Days practised" (3) and the 0/10 goal ring are unaffected in all five clock cases tested; moving forward 1.5/3/30 days correctly makes 2/3/3 cards due. Low risk; no fix needed unless kids change dates often.

## Passed checks
- Network: 48 requests across child onboarding + lesson + all tabs + sticker book + teacher mode, all `localhost` (same origin). Zero third-party hosts, no CDN fonts, no analytics (`s11_net.py`, `s1_first_run.json`).
- Console/page errors across onboarding, a lesson and the tabs on the production build: none (only Playwright's SW-blocked warning). `ui_audit.py` full drive (dev 5188): violations 0, no page errors (`evidence/ui_audit.log`).
- Offline with the SW served by a normal static server: reload offline, full onboarding, lesson, Lottie Marko, images, fonts, tabs all work; audio plays from cache (`currentTime` advanced, `readyState 4`) and the three non-ASCII `aspirates/*.mp3` files are cached (my first "uncached" list was a percent-encoding false positive). The same offline walk on the live GitHub Pages site passes. Note: `vite preview` sends `Vary: Origin`, which makes Cache API matches fail for `crossorigin` module/CSS requests offline; GitHub Pages sends `Vary: Accept-Encoding` only, so this is a test-server artifact, not an app bug.
- SW activate deletes old caches; with a bumped VERSION the update lands on the second reload.
- `npm audit --omit=dev`: 0 vulnerabilities. No source maps shipped. Largest source modules: lottie_light 381 KB, learner.js 46, path.js 37, drills.js 27, onboarding.js 25, @capacitor/core 21, feel.js 20.
- Unreferenced assets: none found (all 490 audio files are in `audio_index.json`; img/lottie names are referenced statically or via templates such as `scene_home_${...}` and `marko_${state}`).
- Animation lifecycle: after 60 navigations `.marko` = 2, `.fx` = 0, canvases 0, `audio` elements 0, active timers <= 9, intervals stop when the hero leaves; reduced-motion removes all animation CPU.
- Large data: 1,000 and 10,000 attempts: Progress/More/Today render in 250-710 ms at 4x CPU (0 attempts: 155-714 ms).
- Two children on one device: progress, attempts, cards, sessions, `stickersSeen:<profileId>` are per profile; switching profile mid-lesson wrote nothing to the wrong profile (Amal 1 lesson, Bina none). Device-level `ui` settings are shared by design.
- Kill mid-lesson returns to Today at the same lesson, no orphan session rows; the onboarding saves its step after every screen and resumes.
- Lesson finish is double-tap safe (pearl keyed by lesson id). Export file contains all stores; round trip restored 36/36 records.
- External WhatsApp/Easypaisa links are behind the grown-ups gate (wrong answer: "Ask a grown-up to help", no navigation).

## Play Console declarations this implies
- Data safety: collects none, shares none (no network use found). Declare: data not encrypted in transit is N/A; no deletion mechanism needed (no account) but Reset exists; the user-initiated Export/Share (Share sheet) is not "sharing" under Play's definition. Decide on Auto Backup (m5) before ticking "all data stays on device".
- Families / target audience 5-10 + adults: no ads, no ad SDK, no advertising ID (all verified absent); external links must sit behind a gate a child cannot pass (m4); the donation card in a children's app is policy-sensitive (payments solicited to children) even gated; privacy policy URL required and must be accurate (m6); content rating questionnaire; do not ship the INTERNET permission if unused (m5).

## Not tested / limits
- No physical phone, no Android emulator (kept free for the owner), no Safari/iOS (SW media range requests are known to be fussy there; the SW answers Range with a full 200, which Chromium accepts). Firefox/Safari private mode not run.
- Quota failure was simulated by aborting the write transaction, not by filling the disk. Missing-object-store DB (partial upgrade) only checked at boot (welcome screen loaded; deeper writes untested).
- Review-card "Got it" double-tap and Reset/delete flows were read in code only.
- Lighthouse numbers are the simulated mobile preset on this machine; treat as relative.
