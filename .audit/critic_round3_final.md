# Critic Round 3 (FINAL) — Urdu Script-Reading Course

Method: read `data/letters.json`/`data/units.json` directly, ran `python3 scripts/check_decodable.py`,
diffed `scripts/build_course.py` against the committed `course/unit_*.md`, served `app/` on
`localhost:8765` and drove it with Playwright (sync, chromium) — including a real localStorage
`urc.progress` unlock, a live 10-question quiz submit with deliberately-wrong picks, hash
navigation + `go_back()`, and a screenshot of the tracer canvas — then parsed
`assets/audio/verify.json` and ran `soundfile` RMS/duration checks over all 1,035 `.wav` files
under `assets/audio/`. Files were not edited.

---

## 1. Fix-verification table

| # | Claim | Evidence | Verdict |
|---|---|---|---|
| 1 | Unit 12 assessment (passage/questions/answers/nonwords) lives in `data/letters.json` `"assessment"`, printed in `course/unit_12.md`, and used by the app | `data/letters.json` → `assessment.{passage,questions,answers,nonwords}` all present and correct. `app/index.html:267` `secTest()` reads `DATA.letters.assessment` live — Playwright confirmed unit 12 renders the real passage ("میرا نام کمال…", "لاہور" present). **But** `course/unit_12.md` prints the **literal, unsubstituted** Python expressions `{A['passage']}`, `{A['questions'][0]}` … `{' · '.join(A['nonwords'])}` — verbatim, in the shipped file. Root cause: `scripts/build_course.py:170` — `special_units()`'s dict entry for unit 12 is a plain `"""…"""` string, not an f-string (every other block — `0:`, `4:`, `6:`, `11:` — uses `f"""`). Re-running `python3 scripts/build_course.py` reproduces the identical broken output; this is not a stale-file issue, it's a live bug. | **PARTIAL — data model FIXED, app-usage FIXED, markdown-course output BROKEN** (new regression, not previously flagged) |
| 2 | Stroke guidance moved into §2 "See it" of each unit, with a source caveat | `course/unit_01.md` §2: every letter card now carries `✎ *How the pen moves:* …` directly under its forms images, followed by `(… These are the conventional Naskh/Nastaliq stroke orders as taught in Pakistani qaida classes; no published study was found, see research/05_open_assets.md.)`. `research/05_open_assets.md:80` independently confirms "Gap: Stroke-Order Data … no widely published stroke-order databases" — the caveat is honest, not decorative. | **FIXED** |
| 3 | ک corrected to base-first/cap-last | `course/unit_01.md`: "base stroke first, right to left along the line, then the sloping cap (sar-kash) added on top last; گ gets a second cap." Consistent with the course's own repeated "dots and marks last" rule — Round 2's specific "cap-first, likely wrong and self-contradictory" defect is resolved. | **FIXED** |
| 4 | `check_decodable.py` no longer exempts آ ئ ؤ ء wholesale — folds them instead | `scripts/check_decodable.py`: `FOLD = {"آ":"ا","أ":"ا","ؤ":"و","ء":"ئ"}`, applied per-character before the taught-set check (replacing Round 2's blanket `ALWAYS = set("ءئؤآأـ")`). Live run: `python3 scripts/check_decodable.py` → `0 violations, 11 declared previews` — the nonzero preview count proves the mechanism is actually doing work, not silently passing everything. Residual gap (documented, not part of this claim): `letters.json` still has no standalone entries for آ/ؤ/ۃ, so their distinct sounds are folded into already-taught base letters rather than ever formally taught — a real but pre-existing content gap, now hidden behind a more rigorous-looking check rather than an obvious exemption. | **FIXED** (mechanism genuinely changed and works; underlying content gap persists, not what was claimed) |
| 5 | Unit 10's letter list is ئ ۃ | `data/units.json` unit 10: `"letters": ["ئ", "ۃ"]`. Exact match. | **FIXED** |
| 6 | ذائقہ tagged preview | `data/units.json` unit 9: `["ذائقہ","ẕāʾiqa","taste (ئ preview)","ذائِقَہ"]`. | **FIXED** |
| 7 | App nav uses `pushState` (back button works) | `index.html:126` unit-nav clicks call `history.pushState(...,'#unit-'+cur)`; a `hashchange` listener (`index.html:108`) re-renders on any hash change, including browser back/forward. **Live Playwright test:** unlocked all units, navigated hash `#unit-3 → #unit-5 → #unit-6`, then `page.go_back()` → URL returned to `#unit-5` (the correct previous state), not out of the SPA. This directly reverses Round 2's confirmed regression ("`go_back()` leaves the SPA entirely"). | **FIXED — live-verified** |
| 8 | Locked units have `aria-disabled` | `index.html:125`: `if(locked){ b.classList.add('locked'); b.setAttribute('aria-disabled','true'); }`. **Live:** before unlocking, units 1–11 nav buttons all report `aria-disabled="true"`; after setting `urc.progress` to all-passed and reloading, the count of `[aria-disabled='true']` elements drops to 0. | **FIXED — live-verified** |
| 9 | Quiz feedback names the missed words | `index.html:229`: `const missed=qs.filter(...).map(w=>w.rom).slice(0,4).join(', ')`, then `'— re-read '+missed+' in step 5, then try again'`. **Live:** submitted unit 1's quiz with deliberately-wrong first-option picks → `Score 2/10 — re-read nānā, bābā, imām, kamān in step 5, then try again`. This replaces Round 2's confirmed defect (hardcoded, misleading "review steps 3, 5 and 7"). | **FIXED — live-verified** |
| 10 | Tracer shows a "start" marker | `index.html` `base()`: draws a filled circle plus the text label `start` near the glyph's rightmost top point. **Live screenshot** of unit 1's "6 · Write it" canvas shows the small dot + "start" label at the top-right of the alif stroke. | **FIXED — live-verified** |
| 11 | Tracer counts strokes against body+dots(+cap) | `index.html check.onclick`: `const expect=1+(DOTS[l.ch]||0)+(l.ch==='گ'||l.ch==='ک'?1:0); const strokeNote = strokes>expect+1?` `… ${strokes} strokes, aim for ${expect} (body${...' + dots'}${...' + cap'})`. Matches claim exactly (body baseline of 1, + dot count, + cap for ک/گ). | **FIXED** |
| 12 | ALL audio regenerated with `sharjeel103/mms-tts-urdu-finetune` | `assets/audio/MODEL.txt` = `sharjeel103/mms-tts-urdu-finetune`. All 474 production `.wav` files (matches `manifest.json`'s 474 entries) under `assets/audio/{aspirates,diacritics,names,numerals,sentences,sight,syllables,units,words}` have mtimes from today's regeneration run; none are stale. `research/06_tts_bakeoff.md` documents the actual bake-off (baseline vs. sharjeel103 vs. two failed candidates) with real Whisper scores, not an assertion. | **FIXED** |
| 13 | Whisper chunk scores in `assets/audio/verify.json` | File exists, 43 groups across 9 categories (`aspirates`,`diacritics`,`names`×4,`numerals`,`sentences`×3,`sight`×2,`syllables`×8,`units`×19,`words`×4), each with `expected`/`heard`/`char_match`. | **FIXED** |

**Score: 12 of 13 claims FIXED (one — #4 — fixed exactly as claimed, with a documented pre-existing residual). 1 PARTIAL (#1): the data model and the live app both genuinely use the assessment content correctly; the markdown course file does not, due to a one-character build-script bug (missing `f` prefix) that produces literal unrendered template syntax in the shipped `course/unit_12.md`.**

---

## 2. Final blind A/B vs. `research/00_quality_bar.md`

| Component | Winner | Gap (if B) |
|---|---|---|
| Letter intro | **A** | — |
| Joining | **A** | — |
| Vowels | **A** | — |
| Drills | **A** | — |
| Tracing | **B** | Feedback is end-state-only (coverage % + one start-side check + a stroke-count note), evaluated after the whole trace is finished — the reference apps in the quality bar give live, per-stroke directional guidance while drawing, not a single post-hoc summary. |
| Dictation | **A** | — |
| Assessment | **B** | The capstone reading-test passage/answer-key is fully correct and live in the app, but a learner reading only the shipped `course/unit_12.md` — the primary text deliverable — sees raw Python template syntax (`{A['passage']}` etc.) instead of the passage; this is a worse failure than either Round 1 or Round 2's version of this same recurring defect. |
| Audio | **B** | 7 of 43 verify.json chunks score char_match < 0.5 (see §3), and the TTS model's license is unresolved for commercial use (see judgement below) — a quality bar for a paid pilot needs both closed out, not just documented. |
| Mobile | **A** | — |
| Accessibility | **A** | `aria-disabled` on locked nav (live-verified), `aria-current`, canvas `role="img"`+`aria-label`, play-button labels all present and functioning; no gap found this round. |

**Tally: 8 A, 2 B (tracing, assessment), 1 mixed-B (audio).** Net: 8/11 wins for the course, versus 6/11 at Round 2 (drills and accessibility flipped to A since the last pass) — but the assessment category actually got *worse* in severity (a broken template placeholder shipped to the primary deliverable, vs. a "missing link" in Round 2), and audio is a new category with a real, unresolved defect.

---

## 3. Audio verification

### `assets/audio/verify.json` — chunks with `char_match < 0.5` (7 of 43 groups)

| Category | IDs | Expected | Heard | Score | What the transcript suggests |
|---|---|---|---|---|---|
| names | ڑے زے ژے فے قاف خے غین عین بڑی حے صاد ضاد طوے (12 letter names) | — | "نے جے یہ خے آف پھین یے بے بےہے سائ زا توے" | 0.41 | Near-total mismatch across nearly every one-syllable name. Isolated single-syllable letter names are the hardest case for Whisper (little context to disambiguate) — most likely **ASR noise on inherently short clips**, not silent/wrong audio (all clips pass the RMS/duration check below). Needs a human listen to rule out mislabeling, since the failure rate is unusually total for a "just ASR is bad at short clips" explanation. |
| names | ظوے ذال ہمزہ | — | "زیح زالیل ہمزرا" | 0.43 | Partial phonetic resemblance (زال≈ذال, ہمزرا≈ہمزہ) — consistent with ASR struggling on retroflex/uncommon consonants rather than wrong audio. Lower concern. |
| syllables | ثا ثی ثو را ری رو دا دی دو ہا ہی ہو | — | "سا سی سو دا یہ دےہو د یہ نڑو بھا بھی بھو" | 0.42 | ہا/ہی/ہو → "بھا/بھی/بھو" is a **repeating pattern** (ہ consistently heard as بھ), seen again below — this recurring substitution across two independent chunks is more consistent with a genuine TTS mispronunciation of ہ (or clip mislabeling) than random ASR noise. Worth a targeted human listen on the ہ-family syllable clips specifically. |
| syllables | سا سی سو شا شی شو جا جی جو چا چی چو | — | **"" (empty)** | **0.0** | Empty transcript is the single most concerning result in the file — either a genuinely silent/near-silent clip Whisper couldn't transcribe at all, or a total ASR dropout. **This is the one chunk that most needs a direct human listen before shipping**, since "empty" is qualitatively different from "wrong." (Note: the RMS/duration scan below found no near-silent or too-short files among the production syllables — if this chunk's underlying clip(s) are in that clean set, the empty transcript is more likely a whisper/ASR artifact than a truly silent file, but this cannot be confirmed without listening.) |
| syllables | حا حی حو صا صی صو ضا ضی ضو طا طی طو | — | "بھا یہ بھو سا زی سو زا زی زو تا دی تو" | 0.48 | Same ح→"بھ" substitution pattern as above (حا→بھا, حو→بھو) — reinforces that this looks like a systematic TTS/ASR confusion between ح-family and بھ, not isolated noise. |
| syllables | ظا ظی ظو ذا ذی ذو | — | "زی ی زو زی ی زو" | 0.36 | ظ and ذ are correctly, universally pronounced /z/ in spoken Urdu (they're spelling-only distinctions inherited from Arabic) — **this is very likely a false positive**: the audio is probably phonetically correct Urdu, and `char_match` is penalizing it for not matching the Arabic-derived letter-name spelling. Lowest-priority item on this list despite the low score. |
| units | u11_16–19: لیکن اگر پھر بہت ("but", "if", "again", "much") | — | "لے کے ان پورزر ویر بہس" | 0.33 | Poor match on four extremely high-frequency function words used throughout the course's later reading material. Unlike the letter-name chunks, these are real running-text words a learner will hear repeatedly — **highest-priority item to manually verify**, since a systematic mispronunciation here would affect dictation/comprehension exercises across multiple units, not just one drill. |

### RMS / duration scan (`soundfile`, all `.wav` under `assets/audio/`)

- **1,035 total `.wav` files** scanned (474 production files matching `manifest.json`, plus 561 under `_bakeoff/` and `_baseline_mms/` — confirmed **not referenced** by `app/index.html` or `app/audio.json`, i.e. research artifacts, not shipped content).
- **Near-silent (RMS < 0.01): 0 files.** No silent clips anywhere in the tree.
- **Too-short (< 0.5s): 17 files**, all in `assets/audio/_bakeoff/{baseline,sharjeel103}/letter_*.wav` and one `word_02.wav` — i.e. entirely inside the non-shipped bake-off comparison set, all with healthy RMS (0.077–0.173), consistent with genuinely short single-syllable letter-name clips rather than corrupted audio. **Zero flagged files among the 474 production clips actually used by the course/app.**

**Bottom line on audio:** no silent or corrupted files were found by signal analysis in the shipped set, but 7 of 43 Whisper-scored chunks (16%) — including one empty transcript and a cluster of high-frequency function words — cannot be cleared without a human listening pass; signal-level cleanliness does not substitute for that.

---

## 4. Final judgement

**Not yet ready to hand to a client as a paid pilot, though close.** Of the builder's 13 specific claims, 12 are genuinely fixed and several (back-button navigation, locked-unit accessibility, named quiz feedback, the tracer's start marker and stroke count) were independently live-verified with Playwright, not just read from source — this is real, substantive progress since Round 2, and the app-side experience (which is what a pilot user actually touches) is in good shape. The one broken claim is nonetheless serious: `course/unit_12.md`, the primary text deliverable for anyone not using the app, currently ships literal `{A['passage']}` template syntax instead of the capstone reading passage — a one-line bug (`scripts/build_course.py:170`, missing `f` prefix) that is trivial to fix but was never caught because nobody diffed the actually-rendered markdown against expectations before calling it done.

**Top 3 things Kamal must still do by hand before this goes to a client:**

1. **Fix and re-verify the build bug**, then re-generate and spot-check every `course/unit_*.md` file by eye (not just grep for the claim) — `scripts/build_course.py:170`'s missing `f` prefix is the kind of error that survives automated checks because the script still exits 0.
2. **Listen to the 7 flagged audio chunks** in `assets/audio/verify.json` (§3 above), especially the empty-transcript syllables chunk and the `لیکن/اگر/پھر/بہت` unit-11 clips — these are Whisper-detected, not human-confirmed, and at least one (empty transcript) is a plausible real defect rather than noise.
3. **Resolve the TTS licensing question before any commercial use.** `research/06_tts_bakeoff.md` states plainly that `sharjeel103/mms-tts-urdu-finetune` — now the model behind 100% of shipped audio — has no stated license on its model card and, being a fine-tune of Meta's MMS weights (CC-BY-NC-4.0, non-commercial), should be assumed to inherit that non-commercial restriction "until the author clarifies." Shipping all-synthetic non-commercially-licensed audio to a paying client is a real legal exposure, not a cosmetic gap — get a direct answer from the model author or record a human voice before this goes anywhere near a commercial pilot.
