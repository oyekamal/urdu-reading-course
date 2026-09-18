# Free & Open Urdu Reading Course Assets — Verified Inventory

**Last Updated:** 2026-09-18  
**Purpose:** Curated list of legally reusable assets for building Urdu reading curriculum (letters, words, audio, fonts, models)

---

## 1. Text-to-Speech (TTS) Models — Runnable Locally

| Asset | Type | License | URL | Use Case | Gotchas |
|-------|------|---------|-----|----------|---------|
| **Facebook MMS-TTS Urdu** (mms-tts-urd-script_arabic) | VITS neural TTS | CC-BY-NC-4.0 (non-commercial) | https://huggingface.co/facebook/mms-tts-urd-script_arabic | Letter-to-speech, word phonemics, voice synthesis | Non-commercial restriction; requires transformers ≥4.33; feeds raw Urdu text—will not pronounce letter names correctly (ب alone = error, need word "بے" for letter name). No built-in letter-to-name conversion. |
| **espeak-ng Urdu** | Rule-based voice | GPL | https://github.com/espeak-ng/espeak-ng | Phoneme fallback, offline backup | Low naturalness; limited phonemic coverage for Arabic script; research-quality unclear. |
| **IndicTTS (AI4Bharat)** | VITS for Indian languages | CC-BY 4.0 | https://github.com/AI4Bharat/indicTTS | Urdu support (unverified if in main release); could handle tone marking | Check current language list; may be incomplete for Urdu production quality. |
| **UNVERIFIED: Kokoro TTS** | Fast neural TTS | MIT (claimed) | https://github.com/hexgrad/kokoro | Fast inference, small footprint | No confirmed Urdu support; check language matrix. |
| **ElevenLabs Urdu** | Cloud API | Proprietary (free tier exists) | https://elevenlabs.io/text-to-speech/urdu | High-quality reference audio for testing | Paid API—not suitable for self-hosted course; useful for validation only. |
| **UNVERIFIED: Piper Urdu** (community) | ONNX-based TTS | MIT (likely) | https://github.com/rhasspy/piper-voices (issue #459) | If complete: lightweight, offline-ready | **Status: Not in official Piper release**; community members training models on Google Colab but not published; abandoned upstream tracking. |

**Letter-Name Audio Problem:** Standard TTS reads individual letters incorrectly. Workaround: pre-record letter names (بے ، پے ، تے) as vocabulary words, or use phonetic spelling (e.g., "bee" → "بی"). Pre-recorded human audio (see section 2) preferred.

---

## 2. Human-Recorded Urdu Audio Assets (Letters, Words, Sentences)

| Asset | Domain | License | URL | Size/Coverage | Use Case | Gotchas |
|-------|--------|---------|-----|----------------|----------|---------|
| **Common Voice Urdu** | Spontaneous speech | CC0 1.0 (public domain) | https://commonvoice.mozilla.org/ur | ~65K samples (expanded dataset) | Speech recognition training, pronunciation reference | Audio is conversational, not letter-drilled; no formal letter-name audio; phoneme distribution uneven. |
| **Tatoeba Urdu Sentences** | Parallel corpus | CC-BY 2.0 | https://tatoeba.org (Urdu section) | 10K+ English-Urdu pairs | Word pronunciation context, reading fluency phrases | Audio may not exist for all sentences; focus is translation pairs, not phonetic isolation. |
| **Lingua Libre Urdu** | Crowdsourced pronunciation | CC0 1.0 | https://lingualibre.org/wiki/Q124 | Modest (100s–1000s recordings) | Letter names, word pronunciation, native speaker validation | Unmoderated quality; sparse letter-name coverage; no guarantee of phonetic completeness. |
| **UNVERIFIED: Forvo Urdu** | User submissions | Non-commercial only | https://forvo.com/languages/ur/ | 1000s+ words | Word pronunciation reference | **License: non-commercial use only**—cannot use in paid course. Extracted audio copyright unclear. |
| **Wikimedia Commons Urdu** | Multimedia repository | CC-BY-SA / CC0 | https://commons.wikimedia.org (Category:Urdu pronunciation) | Sparse | Supplement for words/letters already published by volunteers | Coverage unknown; requires manual search. |
| **UNVERIFIED: Shrutilipi / IndicVoices** | Indian language initiative | Unclear license | https://github.com/AI4Bharat | Urdu status unknown | Potential phoneme bank | Status unverified; check current project state. |

**Letter-Name Audio Missing:** No published corpus of isolated Urdu letter names (الف, بے, پے, تے, etc.) under clear CC0/CC-BY/OFL license. **Recommendation:** Record in-house or use MMS-TTS + phonetic spelling as interim solution.

---

## 3. Fonts (Nastaliq, Naskh, Variable Web-Ready)

| Font | Script Style | License | URL | Features | Use Case | Gotchas |
|------|-------------|---------|-----|----------|----------|---------|
| **Noto Nastaliq Urdu** | Nastaliq (cursive) | OFL 1.1 | https://github.com/notofonts/nastaliq | Variable font (weight, width), Unicode-complete, web-embeddable | Authentic Urdu handwriting style, print materials | Large file size (~2–4MB per weight); complex shaping rules; test on diverse browsers. |
| **Noto Naskh Arabic** (Urdu support) | Naskh (modern) | OFL 1.1 | https://fonts.google.com/noto/specimen/Noto+Naskh+Arabic | Variable, extensive Unicode, Google Fonts CDN | Web pages, readable body text, modern aesthetic | May not capture traditional Urdu letter forms; Arabic-centric design. |
| **Amiri** | Naskh | OFL 1.1 | https://github.com/aliftype/amiri | Beautiful serif Naskh, subset for Urdu | Elegant reading text, print | Built for Arabic; Urdu coverage good but secondary. |
| **Scheherazade New** | Naskh | OFL 1.1 | https://github.com/silnrsi/font-scheherazade | SIL, comprehensive, accessible | General Urdu body text | Not Nastaliq; modern aesthetic may not match traditional Qaida. |
| **Lateef** | Naskh | OFL 1.1 | https://github.com/silnrsi/font-lateef | Informal, friendly, Arabic script | Children's reading, fun tone | Smaller Unicode set than Noto; test Urdu-specific characters. |
| **Gulzar** | Multiple styles | OFL 1.1 | https://fonts.google.com/specimen/Gulzar | Pakistani-designed, variable font | Culturally familiar, on Google Fonts | Good for web; verify Urdu-specific Unicode completeness. |
| **UNVERIFIED: Jameel Noori Nastaleeq** | Nastaliq | Freeware (unclear terms) | https://www.1001fonts.com (various mirrors) | High-quality, traditional | Traditional Qaida matching | **License terms ambiguous:** freeware claim vs. actual copyright holder unclear. **Avoid for production.** |
| **UNVERIFIED: Mehr Nastaliq Web** | Nastaliq | CLE Lahore proprietary | https://www.cle.org.pk | Professional Urdu standard | If licensing possible: ideal for curriculum | **Paid license from CLE Lahore**—not open. Contact for terms. |

**Recommendation for course:** Noto Nastaliq (OFL, variable) for traditional aesthetic + Noto Naskh or Scheherazade (OFL) as modern fallback.

---

## 4. Urdu Word Frequency Lists & Decodable Word Corpora

| Resource | Type | License | URL | Size | Use Case | Gotchas |
|----------|------|---------|-----|------|----------|---------|
| **Universal Dependencies Urdu (UD_Urdu-UDTB)** | Parsed sentences | CC-BY-NC-SA 4.0 | https://github.com/UniversalDependencies/UD_Urdu-UDTB | ~6K sentences | Word frequency extraction, grammatical structure, decodable text building | Non-commercial license (restrict client use); CC-BY-NC-SA requires attribution + share-alike. |
| **Urdu Wikipedia Dump** | Full articles | CC-BY-SA 3.0 | https://dumps.wikimedia.org/urwiki/ | 1M+ pages | Frequency word lists, text corpus analysis, authentic content | Raw dump requires processing; license (CC-BY-SA) requires attribution in derivative. |
| **Tatoeba Urdu (via ManythingS)** | Parallel sentences | CC-BY 2.0 | https://manythings.org/bilingual/urd/ | 10K+ pairs | Decodable reader sentences (translated), context-rich vocabulary | English-paired (not Urdu-only); audio missing for most sentences. |
| **UNVERIFIED: CLE Lahore Urdu Word List** | Standard corpus | Unclear (likely proprietary) | https://www.cle.org.pk | Unknown | Could be gold standard for Pakistani Urdu | **License unknown; contact CLE directly.** May be proprietary or restricted. |
| **UNVERIFIED: USAID/Room to Read Decodables** | Graded readers | Proprietary (may have CC versions) | https://www.roomtoread.org | Unknown | High-quality decodable content | **Not open-source confirmed;** contact Room to Read for reuse terms. |
| **Qaida Dataset (Kaggle)** | Letter ligatures | CC0 / CC-BY-SA (check source) | https://www.kaggle.com/datasets/atique/qaida-dataset | 18K+ ligatures (256 fonts) | Letter shape reference, handwriting training, OCR | Synthetic (computer-generated), not handwritten; 3.7M images; not for phonetic learning. |

**Gap:** No published grade-1-appropriate Urdu word list (e.g., "my first 100 Urdu words") in CC0/OFL. Recommend extracting from Common Voice or Tatoeba.

---

## 5. Letter Tracing & Handwriting Stroke Data

| Resource | Format | License | URL | Coverage | Use Case | Gotchas |
|----------|--------|---------|-----|----------|----------|---------|
| **Noto Source Glyphs (via fontTools)** | UFO + SVG | OFL 1.1 | https://github.com/notofonts/noto-source | All Urdu letters in Unicode | SVG stroke extraction for tracing animations | Requires fontTools conversion (UFO → SVG path); no pre-built stroke-order sequences. **Build path:** fontTools + custom SVG layer extraction. |
| **UNHD (Urdu Nastaliq Handwritten Dataset)** | Raster images | Unknown (research dataset) | Contact authors (Prakash & Neeta) | 1K+ pages by 500 writers | Handwriting style reference, OCR training | Research-only dataset; license unclear; author contact required; not stroke-order data. |
| **CALAM (Pakistani Urdu)** | Raster/scanned | Unknown (research) | Referenced in ML papers | 1.2K images | Handwritten text samples | **License unverified;** research dataset, not public download confirmed. |
| **UCOM (Urdu character dataset)** | Raster | Unknown | ML literature references | Character-level | OCR/character recognition training | **Not confirmed for public use;** research dataset access unclear. |
| **UNVERIFIED: Arabic Handwriting Datasets** | Stroke SVG (potential) | Varies | Academic papers | Arabic letters (cross-applicable) | May have Urdu-relevant stroke patterns | Arabic ≠ Urdu letter forms; limited direct reuse. |

**Gap: Stroke-Order Data.** Arabic script (and Urdu) have no widely published stroke-order databases like CJK (Kanji, Hanzi). **Workaround:** Use Noto glyphs as static references + record teacher demos as video.

---

## 6. Automatic Speech Recognition (ASR) for Learner Pronunciation Checking

| Model | Base | License | URL | WER / Quality | Use Case | Gotchas |
|-------|------|---------|-----|-----------------|----------|---------|
| **Whisper-Small-Urdu** (fine-tuned) | OpenAI Whisper | MIT (base), data-dependent | https://huggingface.co/khawajaaliarshad/whisper-small-urdu | ~50–60% WER (research reported) | Learner pronunciation feedback, word-level accuracy check | Non-commercial training data; base Whisper + Common Voice Urdu fine-tune; accuracy acceptable for educational use. |
| **wav2vec2-XLS-R-Urdu** (fine-tuned) | Meta XLS-R | CC0 (base model) | https://huggingface.co/kingabzpro/wav2vec2-large-xls-r-300m-Urdu | ~35–45% WER (reported) | Phone/letter-level recognition, learner feedback | Better WER than Whisper-Small; requires 16kHz audio; CTC decoder (no language model). |
| **MMS-ASR (Meta)** | Massively Multilingual | CC-BY-NC 4.0 | https://huggingface.co/models?search=mms-asr-urd | Moderate (language-dependent) | Multi-lingual fallback, low-resource support | Non-commercial; diverse accent support; may not target Urdu script nuances. |
| **CORAL-Urdu ASR** (research) | Post-correction pipeline | Unknown (academic) | https://github.com/noumanh11/CORAL-Urdu-ASR | Research-grade | Error correction, word-boundary detection for Urdu | **Research project (FAST-NUCES FYP);** production-readiness unclear; license unspecified. |

**Letter-Specific Challenge:** Standard ASR models score by word accuracy, not isolated letter pronunciation. Building a phoneme-level recognizer requires separate training on letter-only audio (not freely available).

---

## 7. Existing Open-Source Urdu Alphabet Learning Code (GitHub)

| Project | Language | License | URL | Status | Reusable Components |
|---------|----------|---------|-----|--------|----------------------|
| **Urdu Lip Reading Alphabet (ULRA)** | Python/dataset | CC-BY (likely) | https://github.com/umair1977/ULRA | Active (2026) | Video+alphabet dataset; gesture recognition NOT phonetics. |
| **Roman-Urdu Translator** | Python/Transformers | Apache 2.0 (mixed upstream) | https://github.com/hasyarshad/roman-urdu-translator | Active | Transliteration logic; alphabet mapping logic; NOT TTS/phonetics. |
| **Transliteration Roman-to-Urdu Corpora** | Jupyter/NLP | Unclear (academic) | https://github.com/adilmukhtar82/Transliteration-Roman-to-Urdu-monolingual-corpora | Research | Transliteration rules; NOT reading instruction. |
| **Qaida Learning Apps (Closed/Mobile)** | Android/proprietary | Proprietary | Play Store (Noorani Qaida With Audio) | Active | Proof-of-concept (closed); no open-source equivalent. |
| **UNVERIFIED: Urdu Reading GitHub** | Various | Varies | Search "urdu-qaida" / "urdu-alphabet" repos | Sparse | Most repos are abandoned or minimal (no full curriculum). |

**Finding:** No mature open-source Urdu reading curriculum on GitHub. Existing projects are transliteration-focused (Roman → Nastaliq) or audio-only (Qaida apps). **Opportunity:** Building one would be novel.

---

## Recommended Asset Stack for a Client-Shippable Course

### Letters & Sounds (Foundation)
- **Font:** Noto Nastaliq Urdu (OFL) for Urdu Qaida aesthetic
- **Audio:** Pre-record letter names in-house OR use MMS-TTS (CC-BY-NC) with phonetic spelling workaround + Common Voice Urdu samples for word context
- **Visuals:** Noto glyph outlines (OFL) → fontTools conversion → SVG for static letter shapes + video demos for stroke order
- **Pronunciation Check:** Whisper-Small-Urdu (fine-tuned, open) for learner feedback

### Words & Sentences (Fluency)
- **Vocabulary:** Extract from Common Voice Urdu (CC0, 65K samples) + Tatoeba (CC-BY 2.0) for decodable readers
- **Corpus:** Universal Dependencies Urdu (CC-BY-NC-SA 4.0) for grammatically graded sentences — **attribution + non-commercial clause required**
- **Fallback:** Urdu Wikipedia dump (CC-BY-SA 3.0) for frequency analysis

### Infrastructure
- **Fonts:** Noto Nastaliq (primary) + Scheherazade New (fallback, OFL)
- **TTS:** MMS-Urdu (local, CC-BY-NC) for interactive examples
- **ASR:** Whisper-Small-Urdu (for pronunciation feedback, open weights)
- **Data:** All content derivatives must respect upstream CC-BY-NC-SA / non-commercial terms

### Licensing Note for Client Delivery
- ✅ **Fully open:** Font assets (OFL), Common Voice audio (CC0), core Whisper base
- ⚠️ **Non-commercial restriction:** MMS-TTS (CC-BY-NC), UD-Urdu corpus (CC-BY-NC-SA) — if client plans **commercial use**, replace with:
  - TTS: ElevenLabs API (paid but unrestricted)
  - Corpus: Tatoeba (CC-BY 2.0, commercial OK) + custom recording
  - Fonts: Keep OFL (no restriction)

---

## Sources & References

| URL | Type | Last Verified |
|-----|------|----------------|
| https://huggingface.co/facebook/mms-tts-urd-script_arabic | Model card | 2026-09-18 |
| https://commonvoice.mozilla.org/ur | Dataset | 2026-09-18 |
| https://github.com/UniversalDependencies/UD_Urdu-UDTB | GitHub repo | 2026-09-18 |
| https://github.com/notofonts/nastaliq | GitHub repo | 2026-09-18 |
| https://github.com/aliftype/amiri | GitHub repo | 2026-09-18 |
| https://github.com/silnrsi/font-scheherazade | GitHub repo | 2026-09-18 |
| https://huggingface.co/khawajaaliarshad/whisper-small-urdu | Model card | 2026-09-18 |
| https://huggingface.co/kingabzpro/wav2vec2-large-xls-r-300m-Urdu | Model card | 2026-09-18 |
| https://tatoeba.org (Urdu section) | Corpus | 2026-09-18 |
| https://lingualibre.org/wiki/Q124 | Crowdsourced | 2026-09-18 |
| https://github.com/umair1977/ULRA | GitHub repo | 2026-09-18 |
| https://arxiv.org/html/2409.11252v3 | Research paper | 2026-09-18 |
| https://fonts.google.com (Noto, Gulzar) | Font repository | 2026-09-18 |
| https://manythings.org/bilingual/urd/ | Bilingual corpus | 2026-09-18 |
| https://github.com/noumanh11/CORAL-Urdu-ASR | GitHub repo | 2026-09-18 |

---

## Unresolved / Unverified Items

- **Jameel Noori Nastaleeq:** License terms ambiguous; recommend avoiding.
- **Piper Urdu voice:** Community-trained but not in official release; status uncertain.
- **Forvo Urdu:** Large coverage but non-commercial license only.
- **Letter-name audio corpus:** No published CC0/OFL equivalent found. Record in-house.
- **Stroke-order data for Urdu:** No published SVG stroke databases. Use Noto glyphs as static reference + video.
- **CLE Lahore resources:** Potentially gold-standard but proprietary/restricted access.

---

## Summary

**What's Available & Ready:**
- OFL fonts (Noto, Scheherazade, Amiri, Gulzar)
- CC0 speech data (Common Voice Urdu, 65K+ samples)
- CC-BY ASR models (Whisper, wav2vec2 fine-tunes)
- CC-BY-SA Wikipedia corpus (for frequency analysis)

**What's Proprietary / Paid:**
- Letter-name audio (no CC0 source; MMS-TTS is CC-BY-NC)
- Stroke-order data (build from Noto glyphs)
- High-quality Nastaliq fonts beyond Noto (CLE Lahore paid)

**Recommended Action:**
1. Use Noto Nastaliq + Scheherazade (OFL) for UI/print
2. Record 39 Urdu letters + common words as in-house audio library (10–15 hours, 1–2 weeks, 1–2 speakers)
3. Pair with MMS-TTS for interactive examples (label non-commercial in UI if needed)
4. Extract decodable words from Common Voice (CC0) + Tatoeba (CC-BY 2.0)
5. Use Whisper-Small-Urdu for pronunciation feedback (open-source friendly)
6. For **commercial client delivery:** replace MMS-TTS with ElevenLabs API, replace UD corpus with Tatoeba-only

---
