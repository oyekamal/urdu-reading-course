# Onboarding blueprint (app-onboarding-questionnaire skill, phases 1–4)

Bar: Finch: Self-Care Pet first-run onboarding (frames in `bar/`, notes in `bar/FINCH_FLOW.md`).

## Phase 1 — App profile
- **What:** Urdu Qaida teaches anyone, child or adult, to read Urdu script, offline, 10 minutes a day (synthetic phonics, 13 units).
- **Who:** (a) parents of 5–10 year olds, in Pakistan and the diaspora; (b) adults who speak Urdu but can't read it (heritage); (c) adults new to Urdu; (d) teachers with a class.
- **Core loop:** one short lesson on the pearl path, where each lesson is one letter or one word set, with audio on every item.
- **Aha moment:** reading a real word on your own the first time. بابا (baba, dad) is decodable from ا + ب alone.
- **Paywall:** none. The app is free, with a donation option behind the grown-ups gate. The skill's paywall and account screens are replaced (see below).
- **Permissions:** INTERNET only. No priming screen.

## Phase 2 — Transformation
- BEFORE: "I can speak it (or my child should learn it) but the script is a wall of dots and loops. Old qaida books are boring and nobody is there to check."
- AFTER: "I can sound out real Urdu words by myself, ten minutes a day, and I can hear I'm right."
- Benefits: (1) the first real word in the first 2 minutes, which answers "it's too hard"; (2) every letter, word and sentence is spoken aloud, which answers "no one to check me"; (3) look-alike letters are taught side by side, which answers "the dots confuse me"; (4) ten-minute lessons, which answers "no time"; (5) works with no internet and no account, which answers "data/ads/sign-ups".

## Phase 3 — Blueprint (skill archetype → our screen)
1. WELCOME → Marko greets you, "Read Urdu in 10 minutes a day", CTA "Let's begin".
2. WHO (segment, new, needed for routing) → Me / My child / My children / My class. Class → teacher setup (existing).
3. NAME (Finch-style investment) → "What should Marko call you / your child?" Marko then says "Hi, <name>!"
4. GOAL [req] → "Why Urdu?", single-select.
5. SPEAK LEVEL (sets track) → "How much Urdu do you speak?"
6. PAIN [req] → "What's made reading Urdu hard?", multi-select.
7. SOCIAL PROOF → **skipped as testimonials** (no real reviews yet, and fabricated ones are off-limits). Replaced by a real evidence line on the solution screen (USAID Pakistan Reading Project phonics result).
8. TINDER CARDS → skipped. Screens 6 and 9 already cover it, and children would face a longer flow.
9. SOLUTION [req] → your pains mirrored back with how the app fixes each one.
10. PREFERENCE → daily time (5/10/15 min) + best time of day. The time goal shows on Today.
11. PERMISSION → skipped (no permissions).
12. PROCESSING [req] → "Marko is threading your first pearls…" (pearl thread animation, ~2 s).
13. DEMO [req] → a real micro-lesson: hear + tap ا, hear + tap ب, blend با, read بابا.
14. VALUE + SHARE [req] → "<name> read a first Urdu word: بابا", shareable card (canvas PNG → share sheet).
15. ACCOUNT / PAYWALL → replaced by a "Your plan" commitment screen: unit 1, the daily goal, "Start my first lesson". No account (offline by design). Level "can read some" → placement check.
