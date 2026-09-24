# Play Console upload guide · Urdu Qaida: Learn to Read Urdu (com.oyekamal.urdureader)

Follow top to bottom; the order matches Play Console's own menus. Everything to paste or upload is in `store/`.
Build: `~/.kamil-harness/keys/releases/urdu-reader-0.8.2.aab` (versionCode 12, targetSdk 36, signed with the upload key).

## 1. Create app (Home → Create app)
| Field | Enter |
|---|---|
| App name | `Urdu Qaida: Learn to Read Urdu` |
| Default language | English (United States) – en-US |
| App or game | App |
| Free or paid | Free |
| Declarations | Tick Developer Program Policies and US export laws |

## 2. Main store listing (Grow users → Store presence → Main store listing)
| Field | Source |
|---|---|
| App name | `Urdu Qaida: Learn to Read Urdu` (30/30) |
| Short description | `Urdu alphabet for kids: hear, trace and read Alif Bay Pay. No ads, offline.` (75/80) |
| Full description | `listing_en.md`, section "Full description": from "Urdu Qaida for kids and beginners" to "…has a WhatsApp button." Do **not** paste the "Keywords this text carries" line. |
| App icon | `icon-512.png` |
| Feature graphic | `feature-graphic-1024x500.png` |
| Phone screenshots | `screenshots_en/01.png` … `08.png`, **in this order** (01 is the thumbnail parents see first) |
| 7-inch tablet screenshots | `tablet7_en/01.png` … `08.png` |
| 10-inch tablet screenshots | `tablet10_en/01.png` … `08.png` |
| Video | Leave empty (optional, a YouTube link) |

## 3. Urdu listing (same page → Manage translations → Add your own translation → Urdu – ur)
| Field | Source |
|---|---|
| App name | `اردو قاعدہ: اردو پڑھنا سیکھیں` |
| Short description | from `listing_ur.md` → مختصر تعارف |
| Full description | from `listing_ur.md` → تفصیل |
| Screenshots | `screenshots_ur/`, `tablet7_ur/`, `tablet10_ur/` (01–08 in order). Same icon and feature graphic. |

## 4. Store settings (Store presence → Store settings)
| Field | Enter |
|---|---|
| App category | Education |
| Tags | Pick up to 5 of the closest Play offers: Language learning · Reading · Alphabet · Kids · Education |
| Email | A public contact address (Play shows it on the listing). Required. |
| Phone | Optional: +92 336 0506129 |
| Website | `https://oyekamal.github.io/urdu-reading-course/` |

## 5. App content (Policy → App content) — answer exactly
| Section | Answer |
|---|---|
| Privacy policy | `https://oyekamal.github.io/urdu-reading-course/docs/privacy.html` |
| App access | All functionality is available without special access (no login) |
| Ads | No, my app does not contain ads |
| Content rating (IARC) | Category: Reference, news, or educational. Violence, fear, sexuality, language, drugs, gambling: **No** to all. Users interact or exchange content: **No**. Shares location: **No**. Digital purchases: **No** (Donate is an outside Easypaisa transfer, no in-app payment). Expected: Everyone / PEGI 3 / IARC 3+ |
| Target audience and content | Ages 5–8, 9–12, 13–15, 16–17, 18+ (children learn; parents and teachers use the family and class modes). Because under-13s are included, the Families policy applies: no ads, no data collection, outside links behind a grown-ups check (done in v0.8.1). |
| News app | No |
| COVID-19 contact tracing | No |
| Data safety | "Does your app collect or share any of the required user data types?" → **No**. All progress stays on the phone; backup export is started by the user through the Android share sheet. |
| Advertising ID | No, the app does not use advertising ID |
| Government app | No |
| Financial features | My app doesn't provide any financial features |
| Health | No health features |

## 6. First release (Test and release)
New personal developer accounts must run a closed test before Production:
1. **Testing → Closed testing → Create track.** Add at least **12 testers** (an email list or a Google Group) and share the opt-in link.
2. **Create release** → upload `urdu-reader-0.8.2.aab` → accept **Play App Signing** when asked.
3. Release name: `0.8.2 (12)`. Release notes: paste the `<en-US>` and `<ur>` blocks from `whats_new.md` (Play reads the tags).
4. Countries: all countries, Pakistan first. Save → Review → Start rollout.
5. Keep all 12 testers opted in for **14 days in a row** and ask each to open the app.
6. Dashboard → **Apply for production access**. Google usually answers within 7 days. Then promote the same release to Production.

## 7. Before pressing publish
- [ ] Re-read the live Families policy page (it changes often).
- [ ] Easypaisa number and account name in More → Donate are right.
- [ ] ElevenLabs licence question settled (see `PLAY_CONSOLE_CHECKLIST.md`).

## Why these choices (ASO notes)
- **Title** "Urdu Qaida: Learn to Read Urdu": in a simulated Play search page with the 5 top "urdu qaida" apps (their real titles and short descriptions), a blind Gemini parent picked ours first 3/3. The old title "Urdu Qaida: Read & Quiz" got 1/3.
- **Screenshots**: first shot is the benefit (kids + Urdu letters), then the playful parts of the app. A blind critic preferred ours over the top Urdu competitor's (Basic Urdu Qaida, 100K+) 3/3 in both English and Urdu.
- **Urdu listing**: localised listings are the biggest documented install lever (research/17 §3), and none of the competitors have one.
