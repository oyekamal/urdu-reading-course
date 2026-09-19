# Play Console checklist · Urdu Qaida: Read & Quiz (com.oyekamal.urdureader)

Everything the app side needs is in this folder. The steps below can only be done by Kamal in Play Console.
Sources: research/16_play_store_readiness.md (official Google pages, fetched 2026-09-19).

## 1. Account
- [ ] Personal developer account ($25 once), identity verified.

## 2. First upload
- [ ] Upload `~/.kamil-harness/keys/releases/urdu-reader-0.7.0.aab` (versionCode 9, targetSdk 36) to an **Internal testing** track.
- [ ] Enrol in Play App Signing when asked (upload key = the keystore in ~/.kamil-harness/keys/urdu-reader.env).

## 3. Declarations (answer exactly like this)
| Form | Answer |
|---|---|
| Data safety | **No data collected. No data shared.** All data on device; user-initiated export via Android share sheet. |
| Privacy policy URL | https://oyekamal.github.io/urdu-reading-course/docs/privacy.html |
| Ads | No ads |
| App access | All functionality available without restrictions (no login) |
| Content rating (IARC) | Category Education; no violence, no user-generated content, no gambling, no ads, no purchases → expect Everyone |
| Target audience | Mixed: 5–8, 9–12, 13–15, 16–17, 18+ (children learn; parents and teachers use teacher/parent modes) |
| Government / News / COVID / Financial features | No / No / No / No (Easypaisa donate is an outbound link, no in-app payment processing) |
| Health | No |

## 4. Store listing (copy from this folder)
- `listing_en.md` → default listing (en-US). `listing_ur.md` → add localised listing ur-PK.
- Icon `icon-512.png`, feature graphic `feature-graphic-1024x500.png`, screenshots `screenshots_en/01..08.png` (upload in that order), `screenshots_ur/` for the Urdu listing.
- Category: Education. Tags: Language learning, Kids. Contact email + the WhatsApp number. Free, all countries (Pakistan first).

## 5. Closed testing gate (new personal accounts)
- [ ] Create a **Closed testing** track, add ≥12 testers (email list or Google Group), send the opt-in link.
- [ ] Keep them opted in for **14 uninterrupted days**. Ask each to open the app at least once.
- [ ] After 14 days: **Apply for production access** (dashboard). Google answers within ~7 days.
- [ ] Promote the release to Production. Countries: all, Pakistan first. Price: Free.

## 6. Before pressing Publish
- [ ] Re-read the Families policy page linked in research/16 (it changes often).
- [ ] Confirm the Easypaisa number and account name in the app (More → Donate) are right.
- [ ] Optional: apply for Teacher Approved after launch.

## Known follow-ups (not blockers)
- Urdu UI localisation (the Urdu listing shows an English UI under Urdu captions).
- Human voice recording to replace the CC-BY-NC machine voice (recording/SCRIPT.md).
- Tablet screenshots and a 30 s promo video.
