# Urdu Local TTS Bake-off — 2026-09-18

**Question:** Is there a better local Urdu TTS than the baseline (`facebook/mms-tts-urd-script_arabic`, VITS) we can run on this machine (Quadro T2000 4GB, fp16-on-GPU produces NaN here, torch 2.12 + transformers 5.15)?

**Method:** All synthesis on CPU, seed 0, 16 kHz-native output kept as-is (no upsampling except inside the scorer's concat step). Judge = `openai-whisper` "medium" on CPU (`fp16=False`, `language="ur"`, `temperature=0`), run on (a) each of the 3 sentences individually, (b) the 18 letter names concatenated with 0.7s silence gaps, (c) the 6 words concatenated the same way. Score = `difflib.SequenceMatcher` character-ratio between expected and heard text, after NFC normalization, stripping whitespace/ZWNJ/ZWJ, Arabic diacritics (harakat), and punctuation (including tatweel). Whisper is a smoke test for intelligibility only, not an accent/prosody judge.

Wavs saved under `assets/audio/_bakeoff/<model>/` (one `.wav` per clip id + `_meta.json` with load time/duration/RMS/peak, and `_whisper_scores.json` with the raw transcripts and scores). Blind A/B page: `app/tts_blind_test.html`, answer key: `app/tts_blind_test_answer_key.json`.

## Results

| Model | Sentence score (avg of 3) | Letter-names score (concat) | Words score (concat) | Load time* | Licence | Status / notes |
|---|---|---|---|---|---|---|
| **facebook/mms-tts-urd-script_arabic** (baseline) | **0.994** | 0.366 | 0.356 | 3.96s (weights already cached locally) | **CC-BY-NC-4.0** (non-commercial) | Loaded clean, no clipping, RMS 0.077–0.175. Whisper nailed all 3 sentences near-verbatim. |
| **sharjeel103/mms-tts-urdu-finetune** | 0.983 | **0.639** | **0.596** | 83.8s (includes first download; ~700MB+ cache pull) | Not specified on model card (fine-tune of an MMS/CC-BY-NC-4.0 base — treat as inheriting that restriction until the author states otherwise) | Loaded clean via the same `VitsModel`/`AutoTokenizer` API as baseline. No clipping, RMS 0.069–0.13. Sentence quality ~matches baseline; letters/words intelligibility to Whisper is roughly **1.7–1.9x** better than baseline. |
| **syedmuhammad/mms-tts-urdu-vits_finetuned** | 0.487 | 0.032 | 0.340 | 175.5s (includes download) | Not specified (no README at all — "Entry not found") | Loaded (with expected/ignorable "UNEXPECTED" discriminator-weight warnings — discriminator isn't used at inference). Audio is *not* silent or clipped (sane RMS/peak) but is clearly degraded: one sentence transcribed as empty string, the letter-names clip made Whisper hallucinate a 100+ word loop of "بھی". Worse than baseline on every axis. |
| **AhsanTalal/urdu-matcha-tts** | — | — | — | — | Apache-2.0 | **FAILED to run.** Matcha-TTS (ONNX + Vocos vocoder architecture, not `VitsModel`-compatible). Its documented vocoder dependency, `charactr/vocos-mel-22khz`, has been **removed from Hugging Face** (404/401 — repo gone). Tried the closest same-name substitute, `BSC-LT/vocos-mel-22khz`, but it is a different training run with an incompatible `vocos` package API (`MelSpectrogramFeatures.__init__() got an unexpected keyword argument 'f_min'`) — mismatched mel config would produce meaningless audio even if it loaded. No score invented. |
| **multilingual-tts/VITS-OpenBible-Urdu** | — | — | — | — | CC-BY-SA-4.0 | **SKIPPED — setup budget exceeded.** Requires `coqui-tts` (the `TTS` package), which needs Python <3.12; this machine runs 3.12.3, so the classic `TTS` package has no compatible wheel. The maintained `coqui-tts` fork does install on 3.12, but its XTTS import path calls `transformers.pytorch_utils.isin_mps_friendly`, which was removed in the transformers 5.15 already required by the baseline/candidate-1/candidate-2 models in this same environment — importing `TTS` crashes immediately. Downgrading transformers to satisfy it would break the three models above, so this was not attempted. No score invented. |

\* Load time includes first-time Hugging Face download where the model wasn't already cached; not a fair runtime comparison — baseline's 3.96s reflects a warm local cache, both fine-tunes' times are dominated by network transfer, not model init.

**Duration/RMS/clipping sanity (27 clips each, baseline vs. sharjeel103):**

| Model | mean RMS | mean duration | max peak | clipping (>0.99)? |
|---|---|---|---|---|
| baseline | 0.121 | 0.83s | 0.881 | No |
| sharjeel103 | 0.098 | 1.02s | 0.866 | No |
| syedmuhammad | 0.068 | ~0.86s (sentences longer, 2.9–8.5s) | 0.79 | No |

No clipping or silence in any generated clip across the three models that ran — degraded intelligibility in `syedmuhammad`'s case is a genuine model-quality issue, not a signal-processing artifact.

## Raw heard transcripts

### baseline (facebook/mms-tts-urd-script_arabic)
- `sentence_00` expected `یہ میری کتاب ہے۔` → heard `یہ میری کتاب ہے` (1.0)
- `sentence_01` expected `بچے اسکول جاتے ہیں لیکن آج چھٹی ہے۔` → heard `بچے سکول جاتے ہیں لیکن آج چھٹی ہے` (0.981)
- `sentence_02` expected `اگر بارش ہوئی تو ہم گھر پر رہیں گے۔` → heard `اگر بارش ہوئی تو ہم گھر پر رہیں گے` (1.0)
- letters concat expected `الف بے پے تے ٹے جیم چے دال رے سین شین کاف گاف لام میم نون واؤ ہے` → heard `آلف بے اے جیل اے مر اے ہم کی طاور جا مم مم روہ نی` (0.366)
- words concat expected `کتاب پانی گھر بچہ لڑکی اسکول` → heard `تر بھائی ہی بجھا رکھے اسرور` (0.356)

### sharjeel103/mms-tts-urdu-finetune
- `sentence_00` → heard `یہ میری کتاب ہے` (1.0)
- `sentence_01` → heard `بچے اسکول جاتے ہیں لیکن آج چھوٹے ہی ہے` (0.947)
- `sentence_02` → heard `اگر بارش ہوئی تو ہم گھر پر رہیں گے` (1.0)
- letters concat → heard `طرف میں پین اے کی جیم چھے دارل ہے سیم شیم کاف داف جام میم نون وا نے` (0.639)
- words concat → heard `پتا پانی دیر بچا لے کیہی اسطور` (0.596)

### syedmuhammad/mms-tts-urdu-vits_finetuned
- `sentence_00` → heard `` (empty — 0.0)
- `sentence_01` → heard `اچھے سحور لکھیں لیڈے آنچھڑی ہے` (0.539)
- `sentence_02` → heard `اگر بارش ہوئی تو ہم گھر بن رہیں گے` (0.923)
- letters concat → heard `اگر آپ کو اپنے بارے میں بھی بھی بھی ...` (repeated ~100+ times — Whisper hallucination loop, 0.032)
- words concat → heard `پاہو آئے یہ پچا دیو افیل پیسوں` (0.340)

## Verdict

Of the four candidates, only two produced usable audio at all, and only one is actually better than the baseline: **`sharjeel103/mms-tts-urdu-finetune`** matches the baseline on full-sentence intelligibility (0.983 vs 0.994 — both effectively perfect to Whisper) and is meaningfully better at isolated letter-name and word reading (0.639 vs 0.366, 0.596 vs 0.356) — the exact skill a reading-primer course leans on hardest (alphabet drills, word-by-word decoding). It uses the identical `VitsModel`/`AutoTokenizer` API as the baseline, so it's a drop-in swap with no new runtime dependency. The one open question is licensing: the fine-tune's model card states no licence, but since it's built on Meta's MMS weights (CC-BY-NC-4.0, non-commercial), the same restriction should be assumed until the author clarifies — worth a direct ask to `sharjeel103` before shipping this in anything commercial, and the same caveat already applies to the current baseline. `syedmuhammad`'s fine-tune loaded but is clearly worse than the baseline on every metric (including one dead-silent sentence and a Whisper hallucination loop on the letters clip) and should not be used. The two remaining candidates couldn't be evaluated honestly: Matcha-TTS's required vocoder repo has been deleted from Hugging Face with no compatible substitute found in the time budget, and the OpenBible VITS model needs `coqui-tts`, which conflicts with the transformers version this environment already depends on for every other model tested. **Recommendation: adopt `sharjeel103/mms-tts-urdu-finetune` for the letter/word-drill parts of the course (pending the licence question), keep the current baseline as a fallback for full-sentence narration where both are equivalent, and do not pursue Matcha-TTS or VITS-OpenBible-Urdu further without either a working alternate vocoder host or a separate Python 3.11 environment.**
