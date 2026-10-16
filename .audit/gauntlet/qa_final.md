# Urdu Qaida final QA (integrated state, 2026-10-16)

Playwright chromium, dev :5188 (untouched) plus a production build served from /tmp/qa/dist on :5199 (outside the repo) for the service worker and offline checks. No repo file edited. Console errors, pageerrors and HTTP >= 400 / failed requests captured in every session: zero (except the expected ERR_INTERNET_DISCONNECTED when I went offline on the dev server, which has no precache; the prod build was clean offline).

## RELEASE VERDICT: SHIP (no blockers, no majors; the minors below can follow in a point release)

## Bugs

### Blocker
None found.

### Major
None found.

### Minor
1. Word cards cannot be revealed by keyboard or TalkBack. Repro: Words 1 lesson, Tab through the page; `.words .word` is a `div` with tabIndex -1 and no role or label, so focus lands only on the Play buttons. Expected: the card is focusable (role=button, Enter/Space) and reveals picture, romanisation and meaning. Actual: only a pointer tap reveals (synthetic `.click()` on the child does not, a real tap on the card does). File: src/drills.js:98 (`d.onclick`). Fix: `d.tabIndex=0; d.setAttribute('role','button'); d.onkeydown = Enter/Space -> d.click()`, and have the Play button also add `.reveal`.
2. `<meta name=theme-color>` stays `#1E9C8F` in light, dark and system modes. Repro: tap `.theme-chip` and read the meta content. Expected: dark colour in dark (status bar and PWA chrome). File: src/main.js `apply()`. Fix: set the meta from the resolved theme.
3. 320x568 with Extra large text: the Build-the-word card shows the picture, and the letter tiles start at y=554, under the tab bar (they are reachable by scrolling, but nothing hints at that). Repro: seed unit 1, Words 1, Read them, Settings > Extra large. File: src/style.css (`.wimg` in the Build screen) / a11y.js fitLesson. Fix: cap the Build picture at about 90px height when innerHeight < 640.
4. Dark Learn hero on 820/1280: a grey radial glow blob sits behind the Start card button, and the drifting clouds overlay the tree as grey patches (412 dark too). Cosmetic. File: `.pm-cloud` / hero glow in src/style.css. Fix: lower the cloud opacity or blend-mode in dark.
5. Header subtitle sits about 8px above the first card on the learner picker ("Tap a name, or add one") and on Class home. Fix: add margin-bottom about 12px to that subtitle.
6. After mid-lesson resume the Learn card still says "Start: <lesson>" (it does resume at the saved step: a reload on Unit 9 lesson 1, step 1 reopened at "Tap what you hear"). Fix: label "Continue:" when `resume:<profile>` exists.
7. Tap-what-you-hear: tiles are live before the round starts, and the first tap only starts the round (no score, no audio before it). Known from the earlier QA. Fix: disable the tiles until the sound has played or the Play button is tapped.
8. Read tab: "Show meaning" wraps onto its own row under Start/Stop at 412 (not clipped). Cosmetic.
9. Adult and heritage tracks still show the child Marko scene and "Let's earn your first pearl" bubble and mascot in lessons. Intentional or not is a product call; the layout is fine.

## Verified clean
- Layout at 412x880, 820x900, 1280x800, 360x640, 320x568, light and dark (plus reduced-motion at 412 dark): Learn, Review, Read, Me, learner picker, mode chooser and Class home. No horizontal scroll (the only overflow is clipped scenery layers `.pm-*`), no clipped headers, `.theme-chip` and the learner chip correctly placed.
- Theme chip cycles system -> light -> dark -> system. Settings dropdown has the same three options. localStorage cache works: after a reload the theme is correct at DOMContentLoaded, so no theme flash in any of the three states.
- Child journey from first run through unit 3 (`drive_all.py START_UNIT=1 SWEEP_SECS=420`): units 0-3 completed, errors: [].
- Read-first word cards: only Urdu shown until tapped, then picture, romanisation and meaning. Pictures load (no 404s) and look fine in dark and light at 412 and 320.
- Wrong answers stay marked (`no` class); the right tile is flagged after repeated misses; triple-tap on the correct tile advances exactly one round (double-tap lock works).
- Review tab: Check button first, then "I was right / wrong"; counter advances.
- Resume-mid-lesson: setting `resume:<id>` saved and applied after reload.
- Units 8-10: "Show vowel marks" control present in Settings.
- Android Back (`handleBack`): closes the sticker book, practice sheets and gate overlays; in a lesson it opens the leave sheet; Review/Read/Me -> Learn; on Learn it returns false, so the app does the press-twice-to-exit toast.
- Backup export (behind the grown-up gate) -> reset (gated; progress went from 1 of 13 to 0 of 13) -> restore from the file via the mode chooser: progress came back. The grown-up gate solver worked.
- Teacher PIN stored as `h1:<salt>:<hash>`, not plaintext.
- Offline (prod build, SW controlled): reload offline, all four tabs and a lesson work, zero failed requests.
- Rapid tab taps (60 random) and rapid CTA taps, with and without reduced motion: no leftover `[data-exit]` or `[inert]` nodes, no duplicate screens, no errors.
- Text size Large and Extra large at 412: no overflow on any tab.
- Multiple learners (long name wraps cleanly at 320).

## Not covered
- The stopping cue after 3 lessons, the comprehension question after Read, the Quick check retry, vowel-mark fade rendering and the WPM guard were not individually driven (only exercised indirectly by drive_all). Real device audio, haptics and the Capacitor back/keyboard path were not testable in a browser.
