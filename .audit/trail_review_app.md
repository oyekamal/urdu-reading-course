# Trail Audit — App-Building Phase (android, app-plan, app-gauntlet, v0.3, deliver)

Skeptical re-read of `.audit/decisions.tsv` rows from `10:02:41Z` onward (local +0500, so
`10:02:41Z` = `15:02:41` local — every row's timestamp lines up with a same-second-ish git
commit, see mapping below). Prior rows (up to the `08:48` deliver/artifact-publish row) were
already audited in `.audit/trail_review.md` and are not re-litigated here.

Method: opened every named evidence file, re-ran `scripts/check_decodable.py` live, counted
`mobile/public/audio/**/*.mp3` and IndexedDB store definitions directly from source, queried
`gh release list`/`gh release view --json assets` for real APK sizes and dates, checked
`~/.kamil-harness/keys/` for keystore/env/AAB presence (names only, contents untouched), and
cross-referenced `git log` timestamps against every row.

## Timestamp sanity check

Every row in this range has a git commit within seconds of its local-time equivalent
(UTC row ts + 5h = commit time). This is strong, independent corroboration that the trail
was written contemporaneously with the work, not reconstructed after the fact:

| Row ts (UTC) | Local (+5h) | Commit | Commit time |
|---|---|---|---|
| 10:02:41 | 15:02:41 | `774f1c4` offline app plan | 15:02:41 |
| 11:02:30 | 16:02:30 | `ce4ab87`/`72759cd` README+assets+mobile scaffold | 16:00:57/16:01:08 |
| 11:23:19 | 16:23:19 | `7c87309`/`cad4a10` Android v0.1 | 16:13:39/16:23:00 |
| 11:29:55 | 16:29:55 | `4c3ed27` parity gaps | 16:29:55 (exact) |
| 11:33:23 | 16:33:23 | `5385c89` teacher r1 fixes | 16:33:23 (exact) |
| 11:39:46 | 16:39:46 | `9327c50` content r1 fixes | 16:39:46 (exact) |
| 11:55:17 | 16:55:17 | `9971bda` QA r1 fixes | 16:55:17 (exact) |
| 12:22:41 | 17:22:41 | `ade4fe1` v0.2.0 | 17:22:29 |
| 13:46:56 | 18:46:56 | `2bd82db`/`66357ff` v0.3.0 + recording kit | 18:44:50/18:45:30 |
| 14:06:11 | 19:06:11 | `111d7bd` v0.3.1 | 19:06:01 (exact) |

## Row-by-row resolution

All rows in this slice **resolve** — every hard number checked reproduces exactly:

| Row | Claim | Verdict |
|---|---|---|
| app-plan 10:02:41 | `docs/offline-app-plan.html` + `research/07-10` | **Resolves.** File exists (190 lines), all four research files (`07_offline_apps.md`…`10_learning_design.md`) present. |
| deliver 11:02:30 (github) | Public repo, MIT code / CC BY content / CC BY-NC audio, Pages hosting `app/` | **Resolves exactly.** `gh repo view` confirms public; README lines 100–103 state the exact same three licences; `gh api .../pages` confirms Pages built from `main:/`. |
| android 11:02:30 | Capacitor 7 + Vite, appId `com.oyekamal.urdureader`, IndexedDB 7 stores | **Resolves exactly.** `mobile/capacitor.config.json` and `build.gradle` both show the appId; `mobile/src/db.js` `STORES` object has exactly 7 keys (settings, profiles, attempts, cards, sessions, progress, assessments). |
| android 11:23:19 (APK v0.1.0) | "7.4 MB", shipped, GitHub release | **Resolves exactly.** `gh release view v0.1.0 --json assets` → `urdu-reader-v0.1.0-debug.apk` = 7,402,417 bytes = 7.4 MB decimal. Release title honestly says "(debug APK)". |
| android 11:23:19 (teacher.js/egra.js) | Sonnet subagent, contract-first, zero integration fixes | **Partially resolves.** Files exist and are substantial (479 + 298 lines) and land in the commit at the claimed time. The "zero fixes needed" and "which subagent wrote it" parts are not independently checkable from the repo (no per-subagent attribution artifact) — plausible but not provable. |
| app-gauntlet 11:29:55 | 5-part self test, cwpm, placement, parent report, unit-11 sight drill, unit-4 guess card, passages 7–11 verified | **Resolves.** `check_decodable.py` run live → `0 violations, 11 declared previews`, matching the pattern already verified for the course phase. `4c3ed27` diff matches the description. |
| app-gauntlet 11:33:23 (teacher r1) | "A 3 B 3" | **Resolves exactly.** `.audit/app_critic_r1_teacher.md:129`: `**Tally: A 3 — B 3**`. |
| app-gauntlet 11:39:46 (content r1) | "12 remaining items" | **Resolves exactly.** `.audit/app_critic_r1_content.md` lists items 1–12 verbatim matching the row's parenthetical list. |
| app-gauntlet 11:55:17 (QA r1) | "0 console errors", 1 P1 (repro'd 3x), 2 P2, 1 P3 | **Resolves exactly.** `.audit/app_critic_r1_qa.md:158` states zero console errors; P1 explicitly "reproduced 3× across separate runs" (line 36); exactly one P1, two P2, and a P3 section are present. |
| app-gauntlet 12:22:41 (round 2) | "18/19 FIXED, 1 PARTIAL", "no regressions", "A wins/ties 11/13" | **Resolves exactly.** `.audit/app_critic_r2.md:40`: "18 of 19 claims fully verified FIXED... 1... PARTIAL"; line 63: "No regressions found anywhere"; line 137: "wins or ties 11 of 13 components". |
| v0.3 13:46:56 | dashboard.js, PWA at `reader/`, recording kit, keystore generated, PKCS12 gotcha, signed APK+AAB, AAB archived | **Mostly resolves; one sub-claim unverifiable (see Attention #1).** `mobile/src/dashboard.js` exists (6.4 KB, real logic, not a stub). `reader/` is a real built PWA (manifest, sw.js, icons). `recording/` kit (`66357ff`) has `SCRIPT.md` (563 lines), `script.csv` (475 rows), `import_recordings.py` (302 lines). `~/.kamil-harness/keys/urdu-reader.env` and `urdu-reader-upload.keystore` both exist (checked presence/mtime only). `~/.kamil-harness/keys/releases/` holds `urdu-reader-0.3.0-vc3.aab` (6.0 MB) and `urdu-reader-0.3.1-vc4.aab` (6.0 MB). **The PKCS12 "key password must equal store password, first build failed on that" detail has no independent evidence anywhere** — no failed-build log, no error text saved to `.audit/`, nothing in README/mobile docs. It's plausible (a real, well-known `apksigner`/`keytool` PKCS12 constraint) but currently rests on the row's own prose alone. |
| app-gauntlet 14:06:11 (round 3) | "7/8 FIXED, A wins/ties 13/13", released v0.3.1 signed | **Resolves exactly.** `.audit/app_critic_r3.md:39` summary: "7 of 8 claims fully verified FIXED... 1... PARTIAL"; line 41: "wins or ties on all 13 of the 13 components". `gh release view v0.3.1` confirms signed APK, published 14:06:11Z (exact match to the row timestamp). |

**Bottom line: every row resolves against its cited evidence.** This is a marked improvement
over the earlier course-phase rows (two of which failed to resolve — see `trail_review.md`).
One sub-claim (PKCS12 password gotcha) has no evidence pointer at all and should be treated as
an unverified anecdote, not a fabrication — it's a small, specific, technically-accurate detail
that has no obvious motive to invent, but "no obvious motive" is not the same as "resolved."

## Unlogged decisions found

1. **Debug-signed APKs were published as public GitHub releases for v0.1.0 and v0.2.0** before
   any signed release existed (v0.3.0 is the first properly signed build). This is disclosed
   honestly in the release titles ("debug APK") but the *decision* to publish debug-cert builds
   publicly before a signing pipeline existed is not logged as a decision anywhere in the TSV —
   it's just implicit in the row-by-row shipped/released language.
2. **Board task #61 ("Urdu Reader v1: human voice recording, pilot in 2 classrooms, Play Store
   signing") was opened at 11:23:19** (same second as the Android v0.1.0 release) but the TSV
   has no row logging that a new board task was created — `multi-project.md` rule 1 calls for
   logging non-trivial new work before touching code; this is administrative, not fabrication,
   but the trail is silent on it. Task #61 is also still `todo` in the board despite the
   recording kit (`66357ff`) and Play Store signing config (v0.3 keystore/AAB) both already
   being substantially done — the board status hasn't been updated to reflect that partial
   progress, mirroring (on a smaller scale) the task-status-drift the prior audit flagged for
   task #60 (which has since correctly moved to `done`).
3. **`72759cd` ("lockfile", a 2,213-line `mobile/package-lock.json` addition) has no TSV row**
   — trivial and expected (npm install byproduct of the same commit group), not concerning, but
   worth noting for completeness since the earlier audit flagged similar single-commit gaps.
4. **The emulator screenshots cited as evidence for row 11:23:19 ("scratchpad emu*.png") live in
   an ephemeral session scratchpad, not the repo** — same class of problem as the `/tmp` PDF
   sources flagged in the earlier course-phase audit. They cannot be re-opened today to confirm
   the "AudioFocus + 1.56 s track logged" detail; only the release artifact and code paths are
   independently checkable.

## Attention (most important first)

1. **PKCS12 keystore-password mistake has zero evidence trail.** The v0.3 row's most
   operationally interesting detail ("key pw must equal store pw, first build failed on that")
   is asserted with no log, no error text, no commit message reference — nothing to check it
   against. It's a real, well-known Java keystore constraint, so it reads as plausible, but
   under a "prove it" standard it does not resolve. If this repo is ever handed to someone else
   to build/sign, they'll hit this same wall with no documented fix path — worth writing the
   actual error text into `mobile/README.md`'s signing section now, while it's still fresh.
2. **Debug-signed APKs (v0.1.0, v0.2.0) were public GitHub releases before any release-signing
   pipeline existed.** Disclosed honestly in the release title, but never logged as a deliberate
   risk trade-off. Debug-signed builds use the well-known Android debug key — fine for an
   internal pilot test, but anyone installing v0.1.0/v0.2.0 from the public repo today is
   running a debug-signed binary without being told what that means beyond the release title.
3. **Content-critic round 1 explicitly caught itself testing a dev server whose source was
   changing under it mid-audit** (`app_critic_r1_content.md:5` — `learner.js` grew 113→141
   lines and `egra.js`'s UI changed between the critic's first read and its final Playwright
   pass, producing several false "ABSENT" findings later corrected). The critic caught and
   self-corrected this one time, but nothing in the TSV or the other critic reports states
   whether the same hazard (editing live while a critic tests) was controlled for in rounds 2
   and 3 — worth explicitly confirming there was no overlap in the later rounds too, since a
   critic silently missing a still-moving target is a much worse failure mode than one that
   catches and discloses it.
4. **Board task #61 status hasn't kept pace with real progress** (recording kit built, Play
   signing done, still shows `todo`) — low stakes, but exactly the kind of small drift that
   compounds; a 30-second `task status 61 in_progress` would close the gap.
5. **APK size claims are decimal-MB (7.4 MB = 7,402,417 bytes), not binary MiB** — correct as
   stated, but worth flagging only because a casual reader might assume MiB and think a release
   note undersold the size by ~0.3 MB. Not an error, just a unit-convention note for future rows.
6. **"Zero-hosting-needed" framing for Capacitor (row 11:02:30 android)** is true for the
   installed app, but the same day's course also ships a hosted PWA at `/reader` and hosted
   GitHub Pages app at `/app` — three parallel delivery surfaces (native APK, PWA, static web
   app) now exist with no single row stating which one is the "real" pilot artifact Kamal should
   point a classroom at. Not a trail-fidelity problem, but a coordination risk worth a follow-up
   decision.
7. **QA round 1's "0 console errors" claim is scoped to the flows the script drove** (full
   unit 0+1 session, tab navigation) — true as stated, but the phrase reads as a blanket
   guarantee. Rounds 2 and 3 repeat similar zero-error claims for their own tested flows; none
   of the three rounds claims exhaustive coverage of every screen/state combination, which is
   reasonable but worth remembering before citing "0 console errors" as a general app-health
   metric outside this repo.
8. **Emulator evidence (screenshots, AudioFocus log) for the Android v0.1.0 row lives only in a
   now-gone session scratchpad.** Same pattern flagged in the prior course-phase audit for
   `/tmp`-sourced evidence — worth adopting a habit of copying key verification artifacts into
   `.audit/` (as was correctly done for the Whisper logs after that earlier finding) rather than
   leaving them in ephemeral scratch directories.
