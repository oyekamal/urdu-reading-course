# 17 — App Store Optimization (Google Play primary, Apple secondary)

Method: live Google Play fetches (curl + HTML parse, Sept 19 2026) for exact
title/rating/installs/description; screenshots downloaded and visually inspected; DuckDuckGo/WebSearch
for keyword and ASO-rule evidence with URLs. `asoworld.com` case-study pages DNS-failed in this
sandbox — those two are cited from WebSearch's page synthesis + URL, treat as vendor-reported.

## 1. Competitor listings (Google Play, live-pulled)

| App (exact title) | Package | Installs | Rating (n) | Short description (exact) | First screenshots |
|---|---|---|---|---|---|
| Kids Urdu Qaida: Learn Urdu | com.hegodev.urdualphabet | 10K+ | 4.1 (82) | "Learn write and recognize Urdu Alphabets, words and picture names" | Bright-green home menu (قائدہ / گنتی سیکھیں / لکھیں); a 29-tile alphabet grid with one word+image header (انار); a freehand finger-tracing screen for a single letter with pencil/eraser controls. Dated UI, generic clip-art icon. |
| Urdu Qaida - Kids Urdu Learnin | com.ehsas.khybercoded.kidsUrduLearner | 50K+ | 4.49 (121) | "Urdu Qaida is Best Kids Urdu learning app and Urdu Alphabet Activity For Kids" | (not opened — text data only) |
| Urdu Ka Qaida \| اردو کا قاعدہ | com.deenicapps.urdukaqaida | 10K+ | unrated (too few reviews) | "Urdu Ka Asan Qaida App for Learning Urdu offline" | (not opened — text data only) |
| Kids Urdu Learning App | com.ranksol.kidsurdu.learning | 100K+ | 4.23 (141) | "Kids Urdu Alphabets Learning App is for kids to learn & Recognize Urdu." | (not opened — text data only) |
| Basic Urdu Qaida for Kids | com.littletreehouse.urduqaida | 100K+ | 4.39 (568) | "Urdu Alphabets Learning Application is for Kids, Toddlers and Kindergartens." | Phone-frame mockup of a 5-icon menu (حروف تہجی / اردو قاعدہ / کھیلیں اور سیکھیں / کہانی / اب پ کا کیٹ) over a cartoon meadow; a card-grid "word + object photo" screen (جہاز/تحفہ/چاند/درخت/…) using real stock photography, not illustration. Best production values of the set — matches its highest install count. |
| LEARN URDU | com.LearnUrdu.Free | 100K+ | 4.21 (698) | "Urdu Learning Qaida app for new learners." | (not opened — text data only) |

**Read on the category:** every top result is "Qaida" or "Alif Bay Pay," all free/ad-monetized,
ratings cluster 4.1–4.5 on a shallow 82–698 reviews (winnable), and visual quality is the clearest
differentiator — the app using real photography for word-objects (Basic Urdu Qaida) has both the
highest installs and review count. None surfaced teacher-mode, reading-assessment, or parent-report;
none mention Nastaliq vs Naskh; only Urdu Ka Qaida claims offline explicitly. Two other candidate
packages 404'd — likely delisted, a soft signal that "Alif Bay Pay"-branded apps under-invest in
maintenance.

## 2. Keyword demand (ranked by evidence found)

| # | Keyword | Language | Evidence |
|---|---|---|---|
| 1 | urdu qaida | EN/Roman | Dominant term, 6+ live titles, 10K–100K+ installs each |
| 2 | learn urdu | EN | In 3 of 6 top titles; also top Apple Store hit |
| 3 | اردو قاعدہ | Urdu script | Native-script title (deenicapps, littletreehouse) |
| 4 | urdu alphabet | EN | In 4 of 6 titles/descriptions |
| 5 | urdu alphabets for kids | EN | Exact phrase in Pinterest listing + app copy |
| 6 | alif bay pay | Roman Urdu | Standalone branded app + APK-mirror site; strong parent recall |
| 7 | urdu for kids | EN | Recurring modifier across nearly every title |
| 8 | urdu likhna sikhna (writing) | Roman Urdu | Dedicated "Learn To Write Urdu Alphabet" listing — writing ≠ reading intent |
| 9 | offline urdu app | EN | Urdu Ka Qaida's own tagline; r/Urdu poster: "built the best free, offline Urdu Qaida app" myself |
| 10 | urdu qaida for beginners | EN | r/Urdu 2022: "couldn't find a good Urdu learning app for beginners or children" |
| 11 | urdu reading app | EN | Separate cluster (Preply's 2026 "apps to learn Urdu" roundup) from qaida-branded apps |
| 12 | teach urdu to kids overseas | EN | Two live r/pakistan threads on exactly this need |
| 13 | urdu for diaspora / heritage speakers | EN | Same threads: parents raising UK/US kids who can't read Urdu |
| 14 | duolingo for urdu | EN | Multiple Reddit "is there Duolingo for Urdu" posts — no true product exists, open wedge |
| 15 | urdu qaida book for kids | EN | Littletreehouse names the book format directly |
| 16 | نستعلیق | Urdu script | Zero competitors mention script style — real parent/teacher term, total gap |
| 17 | naskh vs nastaliq | EN | Same gap — never appears in any competitor metadata |
| 18 | urdu qaida app free | EN | Can't be in title (policy) but is in nearly every short description |
| 19 | kids urdu tracing | EN | "Arabic Alphabet Trace & Learn" mislabels its Urdu tracing under Arabic — term to own cleanly |
| 20 | حروف تہجی | Urdu script | In-app menu label (littletreehouse) for "alphabet" |
| 21 | urdu qaida pdf | EN | Scribd "Urdu Qaida Learning Apps for Kids \| PDF" ranks — static-doc intent an app can absorb |
| 22 | urdu reading assessment | EN | Zero hits anywhere — white-space keyword, seed via description not title |
| 23 | urdu parent report | EN | Same — zero coverage, ours to originate |
| 24 | montessori urdu | EN | "KG Urdu Qaida Games for Kids" (10,000+ downloads) borrows Montessori/KG framing |
| 25 | مدنی قائدہ | Urdu script | Religious qaida term (Quranic reading readiness) — shares root, different intent; awareness only |

## 3. Google Play ASO rules (2026), with sources

- **Character limits**: title 30, short description 80, full description 4000 — hard-enforced in Play
  Console. Short description outweighs the long description algorithmically; don't repeat title words
  there. ([AppStyle](https://www.appstyle.dev/blog/app-store-character-limits/), [WhixFrame](https://www.whixframe.com/blog/google-play-short-description-guide))
- **Banned/restricted title & icon terms**: "best", "#1", "top", "free", "no ads", any action prompt
  ("download now"). No emoji/emoticons/repeated special characters in title, icon, or developer name.
  Avoid ALL CAPS unless it's the literal brand name. ([yellowHEAD](https://www.yellowhead.com/blog/google-play-takes-another-step-closer-to-the-app-store/))
- **Full description**: unlike Apple, Play indexes it for search relevance — write for humans first,
  place priority keywords naturally in the first ~2 sentences and once more mid-body.
- **Screenshots**: install decisions are dominated by the icon plus first 2–3 screenshots; front-load
  the single clearest value prop, not a menu screen (which is what 2 of our 6 competitors lead with).
- **Feature graphic**: 1024×500, JPEG/24-bit PNG, no alpha. Keep the core message and app name in the
  center safe zone — Play crops/resizes edges. Vivid, non-black/white background (Play's own UI chrome
  is black/white). ([ScreenKit](https://screenkit.tools/specs/google-play-feature-graphic-size))
- **Localized listings**: a Play Console case study (Koo) got +15% installs from a language-targeted
  Custom Store Listing; broader industry data cites 26% CVR lift and up to 128% install lift moving
  English-only → localized. A full Urdu-script store listing (title, screenshots, captions) alongside
  the English one is directly applicable — none of the 6 competitors reviewed ship one. ([ASO localization playbook](https://appfollow.io/blog/app-store-optimization-localization))
- **"Teacher Approved" badge**: requires the app to already qualify for Designed for Families; Google's
  own reviewers/teachers then score design, age-appropriateness, ad/IAP appropriateness, and
  "enrichment" — it does not require the app to be explicitly educational, just non-harmful and
  developmentally sound. No competitor here displays it — an open badge to pursue once DFF-qualified. ([Android Police](https://www.androidpolice.com/google-expands-teacher-approved-play-store-apps-program/), [Google Play Console](https://play.google.com/console/about/programs/teacherapproved/))

## 4. Case studies / guides

1. **ASOWorld — kids educational game, organic #3 rank**: +180% store visibility, +108% organic
   installs (vendor-reported via search synthesis; page itself DNS-blocked in this sandbox).
   asoworld.com/case-studies/…-reached-the-3-position…
2. **ASOWorld — kids game app conversion**: +61.2% conversion-rate lift, 3.5M installs/yr from Play
   search post-ASO (same fetch caveat). asoworld.com/blog/case-study-…conversion-rate-by-61-2…
3. **Storemaven/industry localization data** (AppFollow's 2026 playbook, fetched live): +26% CVR from
   localizing a listing; up to +128% installs English-only → fully localized — argues for shipping an
   Urdu-script listing on day one, not as a v2 add-on.

## 5. Recommended listing draft

**Titles — English (≤30 chars)**
1. `Urdu Reading: Qaida & Quiz` (26)
2. `Learn Urdu Reading – Qaida` (27)
3. `Urdu Qaida: Read & Assess` (25)

**Titles — Urdu script (≤30 chars)**
1. `اردو پڑھنا سیکھیں – قاعدہ`
2. `اردو قاعدہ: پڑھیں، لکھیں`
3. `اردو پڑھو – آسان قاعدہ`

**Short descriptions (≤80 chars, EN)**
1. "Offline Urdu reading app: letters to words to sentences, teacher mode, reports." (80)
2. "Urdu Qaida app with reading assessment & parent reports — works fully offline." (79)
3. "Learn to read Urdu script step by step: Naskh & Nastaliq, kids and adults." (76)

**Full description (English, keyword placement noted)**
Opens with "urdu reading" + "urdu qaida" in sentence one (top-weighted zone), restates "offline" and
"Urdu alphabet" in sentence two, names "Naskh"/"Nastaliq"/"reading assessment"/"parent report"/
"teacher mode" once each in the feature list (keywords #16, #17, #22, #23 — zero-competitor gaps),
closes with "made in Pakistan" for trust + local-SEO. Final marketing copy belongs in
`course/store-listing/full_description_en.md` at submission time — out of scope here.

**Full description (Urdu)** — mirrors the same structure in Urdu script for the localized listing
(title/short/full all in Urdu), per the +26%/+128% localization evidence above; draft alongside the
English copy at submission time, not here.

**8-screenshot storyboard**

| # | Shows | Caption (EN, ≤6 words) | Caption (UR, ≤6 words) |
|---|---|---|---|
| 1 | Mascot + single letter, huge, tapped to hear sound | "Hear every letter instantly" | "ہر حرف کی آواز سنیں" |
| 2 | Letter → word → picture chain (anaar → ا) | "Letters become real words" | "حروف الفاظ بن جاتے ہیں" |
| 3 | Finger-tracing a letter with stroke-order guide | "Trace strokes the right way" | "صحیح ترتیب سے لکھیں" |
| 4 | Naskh vs Nastaliq toggle, same word both styles | "Naskh and Nastaliq both" | "نسخ اور نستعلیق دونوں" |
| 5 | Simple sentence being read aloud, word-highlight | "Build up to sentences" | "جملے پڑھنا سیکھیں" |
| 6 | Teacher-mode screen: a child reading, mic icon | "Teacher mode assesses reading" | "استاد موڈ: پڑھائی جانچیں" |
| 7 | Parent report: progress chart, letters mastered | "Parents see real progress" | "والدین پیشرفت دیکھیں" |
| 8 | "100% offline, made in Pakistan" badge screen | "Fully offline, made local" | "مکمل آف لائن، پاکستانی" |

**Feature graphic concept**: mascot centered against a warm cream/sand background (not black/white —
policy-safe), holding an oversized Urdu letter; app name in Nastaliq-styled lockup top-left inside the
safe zone; no competitor uses a mascot at all, so this alone visually separates the listing on a
crowded "Qaida" search page.

**Icon concept**: mascot's face only, flat bold shapes, single accent color, no text (Play discourages
text-in-icon and it disappears at launcher size) — tested against the busy clip-art icons of all 6
competitors, which look near-identical to each other at thumbnail size.

**Mascot — which Pakistani animal**

| Animal | One-line fit |
|---|---|
| Markhor | Spiral horns give a strong silhouette, but "fierce mountain goat" reads adult, not warm for 3–7yo |
| Chukar (partridge) | Small, round, chubby, big-eyed — best toddler-friendly proportions, but low outside recognition |
| Snow leopard | Visually stunning but solitary/cold connotation; heavy fur pattern breaks down at icon size |
| Camel | Instant "Pakistan/desert" recall and a patient, friendly expression, but body shape resists a small round mascot silhouette |
| Indus dolphin | Rare/endemic "only in Pakistan" press hook and a naturally rounded friendly body — but zero existing cultural familiarity to build on |

**Recommendation**: the **chukar** — no competitor uses an animal mascot at all, so recognition is
built from scratch either way; its round, big-eyed body is easiest to keep warm and consistent across
icon, screenshots, and feature graphic at every size. Camel is the strongest fallback if instant
Pakistan-recognition matters more than animation ease.
