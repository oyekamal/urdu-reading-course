# Competitive / UX gap analysis: what is the Urdu Qaida app missing?

Date: 2026-10-02. Research only: no app source edited, nothing committed.

## 0. Method and honesty notes (read first)

- **Mobbin tools were NOT available in this session.** ToolSearch for "mobbin" returned nothing (no `mcp__mobbin__*` tools; the Mobbin MCP was registered at user scope but needs the browser OAuth step via `/mcp` and a restart of the session). So there are **no Mobbin screen ids or images** in this report and nothing was saved to `.audit/validation/competitive/mobbin/`. Re-run this report's Section 5 (the Mobbin shopping list) once Mobbin is authenticated.
- Fallback used: public web sources only (store listings, official help pages, review sites, a 2025 academic paper on deceptive design in kids' apps, Google Play policy pages). I did not open the apps themselves. Where a competitor cell says "?" I found no evidence either way. Competitor claims are "reported by source X", not hands-on tested.
- "Our app" cells come from reading the repo (`mobile/src/*.js`, `style.css`, `AndroidManifest.xml`, `package.json`, `store/*`, README, `.audit/onboarding/RESUME.md`, `.audit/interact/bar/DUOLINGO_FEEL.md`, `research/02`, `research/17`). Each is grep-checked; evidence is in the "Repo evidence" list at the end of Section 2.
- Source quality: Common Sense Education stopped publishing reviews in Jan 2026, so I could not use its ratings. The arXiv paper covers 20 apps rated 4+, so treat the percentages as indicative.

## 1. Competitor set and what each is best at

| App | Why in the set | Evidence |
|---|---|---|
| Duolingo ABC | Closest functional comparator (ages 3-8 reading, free, no ads, offline). Map of buildings, interactive stories, parent-gated settings, practice reminders, per-child progress, optional hearts, speaking toggle. | [mwm.ai listing](https://mwm.ai/apps/learn-to-read-duolingo-abc/1440502568), [screensdesign showcase](https://screensdesign.com/showcase/learn-to-read-duolingo-abc), [Common Sense privacy eval](https://privacy.commonsense.org/evaluation/Duolingo-ABC---Learn-to-Read) |
| Khan Academy Kids | Best free all-rounder: library of books/videos, Kodi companion, collectibles (hats, bugs), multiple profiles, parent section with content limits, offline "Kodi's Suitcase". | [help: offline](https://khankids.zendesk.com/hc/en-us/articles/360029139531-Learn-on-the-go-with-offline-content-in-Khan-Academy-Kids), [screenwise guide](https://screenwiseapp.com/guides/khan-academy-kids) |
| Lingokids | Parent area with weekly progress report, goals, content filter by year of birth, 4 profiles. Subscription. Reviews note the gate is easy for a 7-year-old and progress reporting was buggy for some. | [techpoint review](https://techpoint.africa/guide/lingokids-tested-review/), [App Store reviews](https://apps.apple.com/us/app/lingokids-games-shows/id1002043426?see-all=reviews) |
| Endless Alphabet / Endless Reader (Originator) | "No high scores, failures, limits or stress"; word-as-toy delight; sight-word levels 1-3; parent info area gated by typing written-out numbers. One-time purchase. | [Common Sense Media](https://www.commonsensemedia.org/app-reviews/endless-reader), [screenwise](https://screenwiseapp.com/guides/endless-alphabet-app) |
| Reading Eggs | Placement test (20 questions), maps with revision quiz and auto-generated report, family dashboard (90 days), milestone emails to parents. Dashboard is browser-only. | [Reading Eggs parents guide](https://readingeggs.com/articles/getting-started-guide-parents/), [support: placement](https://support.readingeggs.com/support/solutions/articles/237436-how-can-i-reset-the-placement-test-or-adjust-level-) |
| Starfall | Nonprofit, ad-free, 20 years of trust; no verified detail on parent/reminder features. | [brighterly roundup](https://brighterly.com/blog/best-reading-apps-for-kids/) |
| Epic! | Library with recommendations; parental toggle to turn videos off. | same roundup |
| Finch (habit reference, adult) | Habit loop without punishment: pet never dies, streaks never punish, home-screen widget, morning check-ins. We already beat it on onboarding and in-app look (RESUME.md r7/r8). | [Deconstructor of Fun](https://www.deconstructoroffun.com/blog/x0hd2ssr80y5n7gv0w967pg7hwd7tl), [selfpause](https://www.selfpause.com/resources/finch) |
| Basic Urdu Qaida for Kids (Little Tree House) | Best Urdu competitor: 100K+ installs, 4.39 (568), stock photography of objects, 5-icon home, stories ("کہانی"), games. | `research/17_aso.md` live Play pull, 2026-09-19 |
| Kids Urdu Qaida / Write Me / LEARN URDU group | Rest of the Urdu long tail: ad-supported, free-form tracing, shallow, dated UI. Alif Bay Pay Go: crashes, 2.3-2.9 stars on mirrors. | `research/17_aso.md`, `research/02_apps_tools.md`, [apkpure listing](https://apkpure.com/alif-bay-pay-go-urdu-learn/com.Fair5ive.AlifBayPayGo) |
| Duolingo (main app), cautionary | Streak widget/notifications drive retention (reported next-day retention 12% to 55%) but draw criticism for guilt and streak anxiety in children. | [Digia UX breakdown](https://www.digia.tech/post/duolingo-habit-forming-reminders-retention-architecture/), [screenwise streak guide](https://screenwiseapp.com/guides/duolingo-streaks-and-anxiety-in-kids) |

## 2. Feature / UX matrix

Legend: **Y** = reported/present, **P** = partial, **N** = absent, **?** = no evidence found. "OURS" column is verified in the repo.

### 2a. Learning experience

| Area | OURS | Duolingo ABC | Khan Kids | Lingokids | Endless Alph/Reader | Reading Eggs | Starfall | Epic | Finch | Little Tree House (Urdu) |
|---|---|---|---|---|---|---|---|---|---|---|
| Onboarding | **Y** (17-screen, Marko wake-up, plan screen) | Y (11 steps; parent sets level; child's first task is writing own name) | Y | Y | N/light | Y (placement) | ? | ? | Y (hatch pet) | N |
| Placement / skip-ahead | **Y** (`autoPlacement` in main.js/learner.js) | Y (parent picks level) | Y | ? | Y (levels 1-3) | Y (20-q test) | ? | ? | n/a | N |
| Progression path | **Y** (pearls on thread, 13 units, gated unit check) | Y (building map) | Y (guided path) | Y | N (free play) | Y (maps) | P | N | n/a | N (menu) |
| Lesson variety | **P** (9 drill types: hear, tell-apart, join, read, write/trace, dictation, quiz, tiles, sight words; no songs, no speed games, no free-play toy) | Y (stories, tracing, speaking) | Y (books, songs, videos, art) | Y (games, shows, songs) | Y (word-as-toy) | Y (games, books) | Y | Y | n/a | Y (5 mini-games) |
| Stories / books to read | **N** (33 sentences and passages in the Read tab; no illustrated stories) | Y (interactive stories, unlock as reward) | Y (library) | Y | Y | Y | Y | Y | n/a | Y (کہانی) |
| Speaking / pronunciation | **N** (no mic code) | Y (optional, parent can disable) | P | ? | N | Y | N | N | n/a | N |
| Content depth | **Y** (39 letters, 220 words, 33 sentences, 13 units, 490 audio clips) | Y (700+ lessons, English) | Y | Y | Y | Y | Y | Y | n/a | P |

### 2b. Feedback, rewards, mascot

| Area | OURS | Duolingo ABC | Khan Kids | Lingokids | Endless | Reading Eggs | Finch | Little Tree House |
|---|---|---|---|---|---|---|---|---|
| Instant feedback | **Y** (spring, chime, haptic, kind wrong-answer with green reveal) | Y (sparkling coin) | Y | Y | Y (no fail state) | Y | Y | P |
| Rewards / collection | **Y** (sticker book, pearl necklace, trophies) but **P** for personalisation (no dress-up / spend) | P (unlocked books) | Y (hats, bugs, toys) | Y | P | Y (eggs, golden eggs) | Y (items) | N |
| Mascot | **Y** (Marko, 8 Lottie states) | Y | Y (Kodi) | Y | Y (monsters) | Y | Y | P |
| Streak design | **Y** safe ("days practised" only goes up) | P (hearts optional) | N | ? | N | ? | Y (no loss) | N |

### 2c. Parent, safety, reach

| Area | OURS | Duolingo ABC | Khan Kids | Lingokids | Endless | Reading Eggs | Finch | Little Tree House |
|---|---|---|---|---|---|---|---|---|
| Parent area / report | **P** (plain-text "Parent report" shared to WhatsApp; family profiles; full dashboard only in teacher mode) | Y (reports, level, activities, hearts toggle) | Y (parent section, content limits) | Y (weekly report, goals) | P (info area) | Y (90-day dashboard, milestone emails; browser only) | n/a | N |
| Parent gate quality | **P** (`prompt()` with a + b where a,b are 2..8; any 6-year-old who can add can pass; used for WhatsApp link only; settings are not gated) | Y (type number words) | Y | P (easy math) | Y (written-out numbers) | ? | n/a | ? |
| Reminders / notifications | **N** (no LocalNotifications plugin; Haptics only) | Y (parent sets practice reminder) | ? | Y | N | Y (emails) | Y | N |
| Home-screen widget | **N** (no AppWidget in `android/app/src`) | ? | ? | ? | N | N | Y | N |
| Offline | **Y** (100%, PWA + APK) | Y | P (Suitcase only) | P | Y | N (online) | P | P/Y |
| Profiles | **Y** (family up to 3, teacher roster) | Y | Y | Y (4) | N | Y (4) | n/a | N |
| Backup / sync | **P** (manual JSON export via share sheet; **no import/restore code found**; no cloud) | Y (account) | Y (account) | Y | N | Y | Y | N |
| Accessibility | **P** (text size, letter spacing, audio-first, romanisation, reduced-motion, dark mode, 44px target audit; no TalkBack audit on record) | ? | ? | ? | ? | ? | P | N |
| Settings (sound, font, script) | **Y** (sounds+vibration switch, text size, Naskh/Nastaliq, romanisation, audio-first) | Y | Y | Y | P | Y | Y | N |
| UI language toggle (Urdu/English) | **N** (English UI with Urdu headings/voice; no `uiLang`; no `lang=`/`dir=rtl` attributes found) | Y (multi-locale) | Y | Y | Y | Y | Y | P (Urdu menu) |
| Tablets | **P** (single column capped at 688-720 px; store has 7" and 10" screenshots but no two-pane layout) | Y | Y | Y | Y | Y | ? | ? |
| Monetisation fairness | **Y** (free, no ads, no IAP) | Y | Y | N (subscription) | P (one-time) | N (subscription) | N | N (ads) |
| Safety / Families policy | **P** (no data collected; mixed 5-18+ audience declared; WhatsApp is gated) | Y | Y | Y | Y | Y | n/a | N/? |

### Repo evidence for the OURS column (what I actually checked)

- Parent gate: `mobile/src/learner.js` has `prompt(\`For grown-ups: what is ${a} + ${b}?\`)` with `a,b = 2 + floor(random*7)`; it guards only the WhatsApp feedback link (`open(url,'_system')`). Teacher PIN in `main.js` guards the roster.
- Reminders/notifications: `grep -i notification|remind` hits only Haptics `NotificationType` in `feel.js`. `package.json` deps: android, cli, core, filesystem, haptics, share, lottie-web. No local-notifications or push plugin.
- Widget: `find android/app/src -iname "*widget*"` returns nothing; AndroidManifest has one activity and a FileProvider only.
- UI language: no `uiLang`, no `lang=` or `dir="rtl"` strings in `mobile/src`; Settings has Text size, Naskh/Nastaliq, romanisation, audio-first, Sounds and vibration.
- Backup: `exportBackup` in `main.js` writes JSON to Cache and opens the share sheet. No `restore`/`importBackup` function in `main.js`, `learner.js`, `teacher.js`. `android:allowBackup="true"` is set, but WebView storage restore is unverified.
- Placement: `autoPlacement` path exists (`main.js learner(p, backTo, autoPlacement)`, `learner.js` calls placement on first open at unit 0).
- Tablets: `style.css` max-widths 688/720 px, no `min-width` media breakpoints, only `prefers-color-scheme` and `prefers-reduced-motion` media queries.
- Lessons: `drills.js` exports playBtn, sayBtn, letterCard, tellApart, joinIt, readIt, writeIt, dictation, quiz; `path.js` kinds: letter, join, blend, words, read, quiz, sight, marks, aspirates, rules, nastaliq, test, done.
- Speech input: no `SpeechRecognition`/`getUserMedia` anywhere.

## 3. Top 15 gaps, ranked by (impact on retention and learning for 5-10s and parents) / effort

Score = my judgement of impact (1-10) divided by effort (S=1, M=2, L=4), rounded. Child-safety rule applied to everything: no streak-loss pressure, no ads, no guilt copy, no sad-character return nudges.

### 1. Stronger parent gate, applied to every grown-up surface (S, score 9)
- **Best apps:** Duolingo ABC and Endless Alphabet make the parent type numbers spelled out as words ([screensdesign](https://screensdesign.com/showcase/learn-to-read-duolingo-abc), [Common Sense Media](https://www.commonsensemedia.org/app-reviews/endless-reader)). Lingokids' plain math gate is criticised as easy for over-7s ([techpoint](https://techpoint.africa/guide/lingokids-tested-review/)). Google Play Families expects age-appropriate protection for mixed audiences ([Families policy](https://support.google.com/googleplay/android-developer/answer/9893335?hl=en)).
- **Today:** a + b with a,b in 2..8 via `window.prompt`, only on the WhatsApp link. Settings, backup export, delete-profile and parent report are not gated (profile deletion is in teacher mode behind PIN).
- **Design:** one `parentGate()` helper: show a number written in words in both English and Urdu (e.g. "type seventeen"), rendered in a proper in-app sheet (not `prompt()`, which looks like a browser dialog and cannot be localised or read aloud), rotate the number and keep it out of the DOM text as digits. Apply it to Settings, Parent report, export/share, external links, and Me-tab profile management. Child never needs it for lessons.
- **Effort:** S. **Caveat:** keep it a deterrent, not security; never block a child inside a lesson.

### 2. Backup restore + family-friendly "move to a new phone" (S-M, score 8)
- **Best apps:** account-based apps restore automatically (Duolingo ABC, Khan Kids, Reading Eggs).
- **Today:** export JSON via share sheet, no import. A lost phone loses weeks of a child's sticker book, which is the opposite of the "never lose progress" promise in our store listing ("Export a backup whenever you like").
- **Design:** add "Restore from backup" (file picker via `@capacitor/filesystem`/input type file; PWA uses plain file input) behind the parent gate; validate version + profile ids; offer "merge" vs "replace"; after export show a calm card "Saved. Keep this file in WhatsApp/Drive". Test that Android Auto Backup actually restores IndexedDB (currently unverified).
- **Effort:** S-M. **Caveat:** backup JSON contains child names; say so on the share sheet.

### 3. Opt-in, parent-set practice reminder with child-safe copy (M, score 7)
- **Best apps:** Duolingo ABC lets the parent set a practice reminder ([Common Sense privacy eval](https://privacy.commonsense.org/evaluation/Duolingo-ABC---Learn-to-Read), search synthesis); Reading Eggs emails milestones. Reminder-style nudges are the main retention lever across the set, but research flags "emotionally loaded notifications that urged users to return" as a manipulation pattern ([arXiv 2512.17819](https://arxiv.org/html/2512.17819v1), 65% of 20 kid apps showed emotional/sensory manipulation).
- **Today:** none. A child who does not open the app daily has no pull back; for a diaspora parent this is the main reason a paid-free app dies after week 2.
- **Design:** `@capacitor/local-notifications`. Off by default; in Parent area (gated) "Remind me to practise together at [time], [days]". Notification is addressed to the *parent* ("Marko has 5 minutes of reading ready for Ayesha") and never mentions streaks, loss, or sadness. One reminder max per day, auto-stops after 3 ignored ones, Android 13 permission asked in parent context only. No push server, all local, so the "no data collected" claim stays true.
- **Effort:** M. **Caveat:** Families policy: no notifications aimed at pressuring a child; keep copy parent-directed and neutral.

### 4. Illustrated decodable stories (a "Read" shelf that unlocks as books) (L, score 6)
- **Best apps:** Duolingo ABC unlocks books as lesson rewards and has interactive stories ([screensdesign](https://screensdesign.com/showcase/learn-to-read-duolingo-abc)); Khan Kids has a library; Little Tree House has a کہانی icon ([research/17](../../../research/17_aso.md)). Stories are where letter learning turns into "I can read".
- **Today:** the Read tab has sentences/passages only; no pictures, no page-turn, no "I finished a book" moment. Biggest content-depth gap against both Duolingo ABC and the top Urdu competitor.
- **Design:** 10-12 six-to-eight-page books built *only* from letters/words taught up to that unit (the app already computes `decodable()` in `path.js`); one sentence per page, tap a word to hear it, Marko reacts, finishing a book adds a sticker and a shelf cover. Reuse the Gemini pipeline (`design/gen`) for page art; text from `data/units.json` sentences extended. Unlock book N with unit N.
- **Effort:** L (content + art). **Caveat:** keep texts culturally neutral, check every illustration for fake glyphs (an issue already hit once).

### 5. Urdu / English interface switch with RTL (M, score 6)
- **Best apps:** all mainstream apps localise UI; the Urdu competitor uses Urdu menu labels (حروف تہجی، کہانی).
- **Today:** English UI strings with Urdu voice prompts on the child track; no `lang`/`dir` handling. A child of 5-6 in Pakistan cannot read "Review", "Read", "Me" labels; parents of Urdu-medium families are shut out of the Settings/Parent report.
- **Design:** a string table `ui.en` / `ui.ur` (start with tab labels, buttons, onboarding, parent area; the 16 app-voice phrases already exist in audio), `document.documentElement.lang/dir` toggled, icons mirrored where directional, picked in onboarding ("زبان / Language") and Settings. Child track defaults to Urdu labels plus icons; adult track follows device locale.
- **Effort:** M. **Caveat:** RTL layout needs a full `ui_audit.py` sweep; do not machine-translate parent report text without a native review.

### 6. In-app family dashboard (not only a text share) (M, score 6)
- **Best apps:** Reading Eggs family dashboard with 90-day view and milestone emails ([Reading Eggs](https://readingeggs.com/articles/getting-started-guide-parents/)); Lingokids weekly report; Duolingo ABC detailed reports.
- **Today:** "Parent report for X" is a `<pre>` text block with a WhatsApp share. `dashboard.js` has rich charts (accuracy 14 days, weakest items, 28-day activity) but it is teacher-mode only.
- **Design:** reuse `dashboard.js` for one family child behind the parent gate: "This week" card (days practised, minutes, new letters, weakest 3 with play buttons), 28-day calendar of dots (no red, no empty-day shame), "Practise together" suggestions, and the share-as-image button (a rendered card, nicer on WhatsApp than text). Lingokids' reviews show a broken report is worse than none, so empty state must say "Report appears after the first lesson".
- **Effort:** M. **Caveat:** no ranking between siblings.

### 7. Home-screen widget showing Marko and today's tiny goal (M, score 5)
- **Best apps:** Finch and Duolingo widgets; reported as effective as push, with no notification permission ([Digia](https://www.digia.tech/post/duolingo-habit-forming-reminders-retention-architecture/), [Deconstructor of Fun](https://www.deconstructoroffun.com/blog/x0hd2ssr80y5n7gv0w967pg7hwd7tl)).
- **Today:** none.
- **Design:** one 2x2 Android AppWidget: Marko pose (idle/waving), "Today: 1 lesson" ring, tap opens the current lesson. State read from a small SharedPreferences file written by the app after each lesson (needs a small Capacitor plugin). Marko never looks sad when the goal is not met; widget shows a neutral "Marko is ready" on missed days.
- **Effort:** M (native Kotlin). **Caveat:** widget reveals the child's name on the lock screen; make showing the name opt-in.

### 8. Tablet two-pane layout (S-M, score 5)
- **Best apps:** Khan Kids, Lingokids, Reading Eggs run on tablets; our target households share a tablet. We upload 7" and 10" screenshots (`store/tablet7_en`, `tablet10_en`) but the UI is a centred 720px column.
- **Design:** at >= 840 px width: path on the left (pearl thread), lesson stage on the right; larger tap targets and Marko; landscape lesson layout. Pure CSS grid plus one breakpoint, then a `ui_audit.py` run at 800x1280 and 1280x800.
- **Effort:** S-M. **Caveat:** none.

### 9. One more game-like lesson form: a fast, no-fail "letter pop" toy (M, score 5)
- **Best apps:** Endless Alphabet (word-as-toy, "no high scores, failures, limits or stress"), Little Tree House (5 mini-games: fishing for letters, balloons, drag, match) ([research/02](../../../research/02_apps_tools.md)).
- **Today:** nine drill types, all question-and-answer. The memory note "Find the Fun First" applies: nothing is a toy a child plays for the joy of it.
- **Design:** "Pop it": letters float up as bubbles/balloons, Marko says a sound, child pops the matching letter. No timer, no lives, no score; wrong pops wobble and release a hint. Accessible from the Review tab and as a 90-second "bonus" after a lesson. Content from letters already mastered (Leitner deck).
- **Effort:** M. **Caveat:** no flashing or loud pops; honour the Sounds switch and reduced motion.

### 10. Voice and speaking practice (optional, parent-enabled) (L, score 3)
- **Best apps:** Duolingo ABC has speaking exercises with a parent toggle ([listing](https://mwm.ai/apps/learn-to-read-duolingo-abc/1440502568)).
- **Today:** none; the child listens and taps but never says a sound back.
- **Design:** "Say it with Marko": record 2 seconds, play both voices back (no ASR scoring at first; self-compare avoids false negatives on young voices and Urdu ASR weakness). Mic permission only after parent opts in; audio never leaves the device.
- **Effort:** L (permissions, playback UX). **Caveat:** microphone use needs data-safety text updated and a clear parent opt-in; do not store recordings.

### 11. Collectible customisation: dress Marko with earned items (M, score 4)
- **Best apps:** Khan Kids hats, bugs and toys ([Khan Kids](https://khankids.zendesk.com/hc/en-us/articles/360029139531-Learn-on-the-go-with-offline-content-in-Khan-Academy-Kids)); Finch items.
- **Today:** sticker book (one deterministic sticker per mastered letter) and pearls; no way to *use* what you earned, so rewards are display-only.
- **Design:** unit completion unlocks a Marko accessory (topi, ajrak scarf, kite, cricket cap) equipped in the home scene; deterministic, never random loot, never purchasable. Pairs with the Lottie rig layers.
- **Effort:** M. **Caveat:** no loot boxes, no scarcity, no "limited time".

### 12. Calm "welcome back" for returning children, with no counting (S, score 4)
- **Best apps:** Finch ("missing a day costs you nothing"); Duolingo is the cautionary tale ([screenwise](https://screenwiseapp.com/guides/duolingo-streaks-and-anxiety-in-kids)).
- **Today:** counters only go up and the goal ring "says nothing when missed", which is good, but the return screen after a week away is the same as any other day.
- **Design:** if last session > 5 days ago, Marko waves and offers a 3-card warm-up from the Leitner deck ("Let's remember together") before the path; no mention of days missed.
- **Effort:** S. **Caveat:** the copy must be tested aloud with parents.

### 13. Accessibility pass: TalkBack, focus order, contrast, and a dyslexia font option (S-M, score 4)
- **Today:** large text, letter spacing, audio-first, reduced motion and a tap-target audit exist. Not on record: a TalkBack walkthrough, `role/aria` labels on tile drills, and a screen-reader test of the tracing canvas. Our listing already claims "dyslexia-friendly" spacing, so this must hold up.
- **Design:** run TalkBack through onboarding + one lesson, add labels to icon buttons and tiles, expose letter names as accessible text, add "Hold to hear" alternative for tracing, check WCAG AA contrast on the coral/saffron accents in dark mode. Add a text-size slider beyond 1.0x on the child track.
- **Effort:** S-M. **Caveat:** none.

### 14. Parent "co-play" prompts: five-minute family activities (S, score 4)
- **Best apps:** Khan Kids and Duolingo ABC both lean on adult co-viewing; our diaspora target segment (parents who cannot read Urdu themselves) has no guidance on *how to help*.
- **Today:** the Parent report suggests what to practise next, but nothing tells a non-reading parent what to do beside the child.
- **Design:** a "Practise together" card in the parent area per unit: three short instructions in plain English with Urdu audio for the parent (e.g. "Ask Ayesha to find ب in the room's labels"), printable from the existing `course/unit_NN.md`.
- **Effort:** S. **Caveat:** no screen-time-expanding prompts.

### 15. Data-safety / Families-policy hardening and a visible "no tracking" proof (S, score 4)
- **Evidence:** Families policy requires a compliant privacy policy and bars advertising-ID transmission to child audiences ([Families policy](https://support.google.com/googleplay/android-developer/answer/9893335?hl=en)); our checklist says "mixed 5-8 .. 18+" but also says to re-read the policy. Trust is a differentiator: the arXiv study found 90% of kid apps showed ads and 72.8% of ads were unskippable ([arXiv 2512.17819](https://arxiv.org/html/2512.17819v1)).
- **Today:** claims are right in the store text, but INTERNET permission is declared in the manifest, and the WhatsApp link opens externally behind a trivially easy gate.
- **Design:** remove INTERNET if no feature needs it (or document it), add a "What this app never does" card in the parent area (no ads, no account, no tracking, no purchases, works offline), and run a manifest/permission audit against the Data safety form.
- **Effort:** S. **Caveat:** verify web build (PWA) separately.

## 4. Things we do better than the market (do NOT over-correct)

1. **Real Urdu script teaching.** Nobody in the Urdu set mentions Naskh vs Nastaliq (`research/17`: zero competitors; we ship both with a switch), frequency-ordered letters, look-alike (dots) contrast, positional forms, join/blend rules. Competitors are letter-tile menus.
2. **Fully offline, no account, no ads, no IAP, no tracking.** Duolingo ABC matches us on ad-free; Lingokids and Reading Eggs are subscriptions; the Urdu set is ad-supported ([research/17](../../../research/17_aso.md)). Do not add an account or cloud sync to fix backup; do restore-from-file instead (gap 2).
3. **Teacher mode + EGRA-style assessment + class reports.** No competitor in either set offers this. Duolingo ABC, Khan Kids and Reading Eggs are home-first.
4. **Child-safe motivation by design.** No hearts, lives, leaderboards, loss streaks or guilt copy ("days practised" only goes up), already stricter than Duolingo's family of apps. The arXiv study (20 kid apps) found 100% with interface interference and 90% with ads disguised as rewards; we have none.
5. **Audio quality and verification.** 490 clips, ElevenLabs Sara, blind-judged 36/38, human-recording path. Little Tree House and the other Urdu apps use stock or synthetic voices.
6. **Mascot and feel.** Marko (8 Lottie states) and the feel layer beat Finch and Duolingo's real lesson moments in the blind critic rounds (`RESUME.md`, r7/r8, v0.10.0 "all four won"). Do not add a second mascot or more confetti.
7. **Placement and per-profile pace** for child, adult and heritage-speaker tracks; few kids' apps support an adult learner on the same device.
8. **Open course data (CC BY 4.0) and printable lessons** that the whole market lacks.

## 5. Mobbin shopping list (run after OAuth succeeds)

When `mcp__mobbin__*` tools appear, pull and save to `.audit/validation/competitive/mobbin/<app>/<flow>/` (third-party images, keep gitignored) and add the screen ids to each gap above:

- Parent gate / grown-up area: Duolingo ABC, Khan Academy Kids, Lingokids, Endless Alphabet (gaps 1, 6, 15).
- Reminder set-up and notification permission priming: Duolingo, Finch, Headspace (gap 3).
- Widgets (iOS/Android): Duolingo, Finch (gap 7).
- Parent dashboard / progress report / milestone email: Reading Eggs, Lingokids, Epic (gap 6).
- Story/book completion, library shelf: Duolingo ABC, Khan Kids, Epic (gap 4).
- Settings with language toggle and RTL: any Arabic/Urdu-localised app (Drops, Busuu, Speak) (gap 5).
- Empty states and returning-user screens: Finch, Duolingo (gap 12).
- Backup/restore flows: Finch, Day One (gap 2).
- Collectibles/customisation: Khan Kids, Finch (gap 11).

## 6. Suggested sequencing (child-safe, smallest first)

1. Gap 1 (gate), 2 (restore), 15 (permissions audit): all S, trust and no-data-loss.
2. Gap 3 (parent-set reminder) and 6 (family dashboard): the retention pair; ship together so the reminder links to something worth opening.
3. Gap 5 (Urdu UI) and 8 (tablets): reach.
4. Gap 4 (stories) as the next content epic; gap 9 and 11 as delight.
5. Keep 10 (speaking) and 7 (widget) on the backlog until 1-6 are validated with real families.

## Sources

Duolingo ABC: https://mwm.ai/apps/learn-to-read-duolingo-abc/1440502568 , https://screensdesign.com/showcase/learn-to-read-duolingo-abc , https://privacy.commonsense.org/evaluation/Duolingo-ABC---Learn-to-Read . Khan Kids: https://khankids.zendesk.com/hc/en-us/articles/360029139531-Learn-on-the-go-with-offline-content-in-Khan-Academy-Kids , https://screenwiseapp.com/guides/khan-academy-kids . Lingokids: https://techpoint.africa/guide/lingokids-tested-review/ . Endless Reader: https://www.commonsensemedia.org/app-reviews/endless-reader . Reading Eggs: https://readingeggs.com/articles/getting-started-guide-parents/ . Finch: https://www.deconstructoroffun.com/blog/x0hd2ssr80y5n7gv0w967pg7hwd7tl . Duolingo retention/criticism: https://www.digia.tech/post/duolingo-habit-forming-reminders-retention-architecture/ , https://screenwiseapp.com/guides/duolingo-streaks-and-anxiety-in-kids . Deceptive design study: https://arxiv.org/html/2512.17819v1 . Play Families policy: https://support.google.com/googleplay/android-developer/answer/9893335?hl=en . Urdu apps: repo `research/17_aso.md`, `research/02_apps_tools.md`.
