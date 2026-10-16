# Urdu Qaida functional QA (Playwright, chromium 412x880 @2x unless noted)

Date 2026-10-16. Dev server :5188 (untouched). A production build was also made to /tmp (outside the repo) and served on :5199 to test the service worker and offline. No repo file was edited. Driver scripts: /tmp/claude-1000/qa/*.py.
Console errors / pageerrors / HTTP>=400 were captured in every session: **zero** in all runs.

## BUGS

### 1. [major] Double-tapping the correct tile skips rounds and double-counts score (tell-apart, blend, quick check)
Repro: Learn > start any letter lesson with 2+ learned letters (e.g. unit 1 "be"). On "Tap what you hear" tap any tile to start, then double-tap the correct tile (also real `dblclick`).
Expected: one answer, one round. Actual: status jumps "Round 1/5 · 0 right" -> "Round 3/5 · 2 right". The same on the Blend lesson ("Round 1/6" -> "Round 3/6") and the letter "Quick check" (triple tap: Question 1/4 -> 4/4, three questions never asked, so the 3-of-4 pass gate is easy to fall through/skip).
Cause: the `ok` branch never sets `dataset.stay`/disables the tile, and `setTimeout(next, 450|600)` fires once per click. `tapLock` only guards Continue buttons.
Files: src/drills.js:45 (tellApart ok branch), src/path.js:178 (letter-lesson blend) and src/path.js:195 (blend lesson `t.onclick`), src/path.js:211 (`grade` in quick check).
Fix: on a correct tap do `t.dataset.stay='1'` and disable all tiles in `choices` (or `if (answered) return; answered = true;`) before scheduling `next`.

### 2. [major] Read tab: Start then Stop immediately saves "Infinity"/absurd words-per-minute as a personal best
Repro: Read tab > "Read for speed" card > Start, Stop straight away (or after <1 s).
Expected: "too quick to count" guard (the Test screen has one at <15 s). Actual: "Infinity words per minute · new personal best!"; after another run Today shows "Last reading speed: 840000 words per minute fluent", Me/Progress shows "latest 840000 wpm · best 840000" and the best is poisoned permanently (it is persisted via S.addWpm).
File: src/learner.js:153 (`stop.onclick` in `fluency`, `Math.round(words*60/sec)` with sec ~ 0).
Fix: `if (sec < 5) { res.textContent='Too quick to count. Read the whole text.'; start.disabled=false; stop.disabled=true; return; }` and clamp wpm to <= 250 before `addWpm`.

### 3. [major] "Build the word" wrong tiles un-mark after 400 ms and stay tappable (violates "wrong stays marked")
Repro: lesson "Join them" (or any Words N lesson, 2nd step, or Unit page "Join it"). Tap a wrong letter tile: it turns `.no` and 400 ms later reverts to a plain tile. Verified: after 700 ms the wrong tiles show class `tile small ur` again. Each tap also records another failed attempt.
File: src/drills.js:76 (`t.classList.add('no'); setTimeout(() => t.classList.remove('no'), 400)`).
Fix: replace with `stayWrong(t)` (already exported at drills.js:256); a correct tile already gets disabled.

### 4. [major] Dictation: wrong answer mark disappears after 500 ms
Repro: Words lesson step 3 (Dictation): tap one key, press Check. `.answer` gets `no` then it is removed 500 ms later (confirmed); the wrong typed text stays on screen with no mark, only a toast that vanishes.
File: src/drills.js:231 (`ans.classList.add('no') ... setTimeout(() => ans.classList.remove('no'), 500)`).
Fix: keep `no` until the next key/erase (remove it in the key `onclick` and in `back.onclick`), not on a timer.

### 5. [major] Unit check (quiz): after Submit the tiles are still tappable and rewrite the result
Repro: unit 1 last lesson "Unit check": Submit with nothing selected (score 0/10, correct answers shown green). Tap any wrong tile in question 1: the green `ok` jumps from the correct word to the wrong one (class list before `[.., ok, ..]` after `[ok at the tapped wrong tile]`). The review of what was right/wrong is now false, and on a pass screen the same can be done.
File: src/drills.js:241-243 (tile `onclick` is not disabled by `submit.onclick`).
Fix: in `submit.onclick` do `ol.querySelectorAll('.tile').forEach(t => { t.disabled = true; })` (or guard `if (submit.dataset.used) return;` at the top of the tile handler). Also consider requiring all 10 answered (currently 0/10 can be submitted by accident, no confirmation).

### 6. [major] Teacher PIN has no lockout and is stored/compared in clear text
Repro: Class screen > Teacher > enter wrong PIN repeatedly: "Wrong PIN" toast every time, no delay, no cap (children can brute-force 4 digits in minutes; the grown-up gate elsewhere has a 3-try/30 s lockout). The PIN is saved as the plain string in IndexedDB setting `teacherPin`.
File: src/main.js:136 (`ok.onclick = () => inp.value === pin ? teacher() : toast('Wrong PIN')`), src/main.js:127 (`db.setting('teacherPin', pin.value)`).
Fix: reuse the gate's try/lockout counter (gate.js `readTries/writeLock`) for PIN entry; store a salted SHA-256 (crypto.subtle) instead of the raw PIN.

### 7. [minor] Learner picker cards stack avatar above the name (huge cards, 3 learners fill the screen)
Repro: Who is learning? with 2+ learners (any theme). Avatar sits on its own line above the name; each card ~145 px tall. Cause: `.card.btn{display:block}` overrides the intended flex row (computed display `block`).
File: src/style.css:84 and src/main.js `home()` (card built as `card btn` with avatar + div).
Fix: wrap the avatar+text in `<div class="row" style="flex-wrap:nowrap">` as `chooseMode()` does, or add `.list .card.btn{display:flex;align-items:center;gap:12px}`.
Related minor: two learners with the same name and the same track (e.g. "Ali"/child twice) are indistinguishable in the picker (only track and grade shown); there is also no delete-learner outside teacher mode.

### 8. [minor] Appearance "Dark/Light" does not flip native controls, and there is a light flash at startup
Repro A: OS light + Appearance Dark: `getComputedStyle(documentElement).colorScheme` is `normal`; native `<select>` popup, scrollbars, checkboxes and the Android keyboard stay light. No `color-scheme` is set anywhere.
Repro B: OS light + saved Dark: `data-theme` is applied by `apply()` only after IndexedDB opens (measured 308 ms after navigation), so the cream light page paints first, then flips (reverse for Light under OS dark). `<meta name=theme-color>` is a fixed #1E9C8F in every mode.
Files: src/main.js:47 (`apply`), index.html:6.
Fix: add `:root[data-theme=dark]{color-scheme:dark}` / `:root[data-theme=light]{color-scheme:light}` in style.css (or in the postcss plugin in vite.config.js); mirror the choice to `localStorage` and set `data-theme` from a tiny first-script before first paint; update the theme-color meta in `apply()`.

### 9. [minor] First tap on the "Tap what you hear" screen silently starts the game
Repro: letter lesson step 2: the screen shows 6 pre-rendered tiles with no instruction to start; tapping any of them (child's natural action) only starts round 1 and discards the tap; the speaker button also starts the game instead of playing.
File: src/drills.js:50 (dummy tiles `t.onclick = next`) .
Fix: call `next()` immediately in `tellApart` when used inside a lesson (opts.letters present), keep the tap-to-start only for the Unit page.

### 10. [minor] Letter-lesson "Blend it" (2+ vowels learned) wrong tile is not disabled
Repro: any letter lesson in unit 2+ with the `Blend it` step: wrong tile gets `.no` but stays tappable, and each tap records another failed attempt (other blend drills use stayWrong).
File: src/path.js:178 (`else { t.classList.add('no'); }`). Fix: `D.stayWrong(t)`.

### 11. [minor] Spring layer: tiles settle slowly, and the pop uses a tight 0.002 tolerance
Observed on the 40-tile Unit check at 360x640: tiles still at scale 0.74-1.11 at 1.0 s, 0.99-1.02 at 2.0 s, clean at 3 s. Cards in teacher tabs are still at scale 0.9988 / translate 0.5 px at 0.9 s. Nothing is stuck (no opacity 0, no leftover scale/translate after 3 s, none after 40 rapid tab switches, none with prefers-reduced-motion), but the staggered `55 ms * c++` delay makes the last quiz tile start ~2 s late. Under 4x CPU throttle: Me tab frame gap 300 ms, Today 183 ms (mostly Lottie/dashboard, but entrances add to it).
File: src/spring.js:44 (CHOICES branch), spring.js:7 (settle threshold).
Fix: cap stagger at ~8 tiles (`Math.min(c++, 7) * 40`), loosen the settle test to `|x-to|<0.004 && |v|<0.05`.

### 12. [minor] Shake/pop fire only once per element
`__shook` / `__won` flags are never reset, so a joinIt tile that is wrong twice shakes only the first time (spring.js:56-57). Fix: clear the flag when the class is removed (`!t.matches('.tile.no') -> t.__shook = false`).

### 13. [minor] Misc
- Onboarding: Back from the name reply screen ("Zara! What a lovely name") returns to the reply, not to the name input; Back is otherwise correct at every step and resume after reload works (src/onboarding.js).
- Teacher tabs are `<div class="tab">` with no role/tabindex/aria-selected (not keyboard or TalkBack reachable); at 360 px "Reports"/"Device" are off-screen (the row scrolls, no cue). Teacher "Lesson" screen select is 358 px wide at 360 viewport.
- Review card copy says "then check" but there is no check/reveal button (only Not yet / Got it).
- Read tab "Start" interval is never cleared on leaving the tab (`setInterval` in `fluency`, src/learner.js:152).
- `prompt()`/`confirm()` are used in Test yourself and teacher Delete (src/learner.js test(), src/teacher.js:135); unreliable in some Android WebViews.
- Offline (prod build, SW): app shell, lessons and units 0-1 audio work offline; audio for later units (u02+) returned a network error ~11 s after install because it is lazy-warmed in the background. A learner who installs and goes offline immediately has silent units 2+.
- Placement check: a wrong answer marks the tile and ends the check after 700 ms (design: "one miss ends"), but this is an auto-advance on a wrong answer, contrary to the rule applied elsewhere.
- Backup file `settings` store carries the `ui` setting (theme/text size) into restores: restoring on another phone overrides its Appearance (intended? flag only).

## TESTED AND CLEAN
- Appearance select (Match my phone / Light / Dark) with color_scheme light AND dark: correct palette each time on Me, learner picker, onboarding (theme=light under OS dark gives cream onboarding), lessons, words, review; persists across reload; unset returns to OS. Postcss `:root[data-theme]` twins also present in the production build (46 data-theme rules in dist index.html).
- First-run onboarding: welcome > wake > colour > who > name > goal > speak > reads > pains > solution > minutes > processing > demo > value > streak > commit > plan, both "My child" and "Me" paths via tools/onb_shots.py: no errors. Back works at every step back to the welcome; reload mid-flow resumes at the same step; empty and whitespace name disables Continue; 200-char name capped to 24; emoji, Arabic and RTL-override names accepted/sanitised; `<b>` stripped.
- Child lesson flow unit 0 and unit 1 (letters, where-it-sits, trace screen, quick check, join, blend, words read/build/dictation, unit check): pass (10/10 passes, celebrate screen, next unit unlocks, Unit 2 "open" banner), fail (0/10 shows missed words, Try again returns a fresh 10-question check), retry pass. Tell-apart, marks, sight, blend wrong answers stay marked and disabled and do not advance.
- Triple-tap on Continue advances one step only (tapLock); reload mid-lesson returns to Today with progress kept; rapid-fire 40 tab switches leave one screen, correct active tab, no duplicates, no stuck styles (also with reduced motion).
- Review tab: 30 due cards, rapid triple tap on "Got it" grades one card. Read tab: passage + 24 sentence rows, speaker buttons highlight only the playing row (`.is-playing`).
- Me tab: text size, script, letter spacing, audio-first persist across reload; backup export (valid JSON, 55 records), reset (grown-up gate with spelled number, 3 wrong = 30 s lockout), restore (merge, "Restored 55 records"), corrupt JSON rejected with plain message; sticker book and practice sheets open; leave-lesson sheet.
- Multiple learners: add, switch, same names, 60-char emoji/RTL name wraps without overflow, child/adult/heritage tab sets correct (4 vs 6 tabs); adult and heritage screens (Units, Review, Read, Progress, More) render with no errors.
- Teacher mode: PIN setup validation (<4 digits rejected, non-digits still typeable), wrong PIN rejected, roster, Lesson/Groups/Assess/Reports/Device tabs, full 5-part assessment with Skip to the result screen.
- Viewports 360x640, 320x568 (text size Extra large + Widest spacing + dark), 880x412 landscape: no horizontal document scroll on Today/Review/Read/Me/lesson; nothing off-screen apart from the teacher tab row noted above.
- Word pictures: all 5 images on the Words screen load (naturalWidth > 0), no 4xx in network, alt="" (decorative, text is beside them), no overlap between picture/text/speaker in light and dark, layout shift 0.012 over 500 ms.
- Offline (prod build + service worker): reload offline renders Today, opens a lesson; shell assets and unit 0-1 audio served from cache; no uncaught errors; audio `error` event clears the `is-playing` highlight.
- Spring layer: no element left at opacity 0 or with stray scale/translate after settling (checked every tab, lessons, teacher tabs, restore flow); reduced-motion makes the layer a no-op with fully visible content.
