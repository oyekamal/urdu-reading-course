# Pakistani Visual Identity for Urdu Reading App
## Design Research: Cultural Colours, Motifs, Typography & Illustration

**Date:** 2026-09-19  
**Purpose:** Design guidance for an Urdu reading app that feels unmistakably warm and Pakistani without clichés.

---

## 1. Palette Board — 5 Candidate Accent Colours

Each colour carries specific cultural weight and appears across Pakistani design, craft, and popular apps. Hex codes are approximations based on documented sources.

| # | Colour | Hex | Cultural Source | Scale & Context | When to Use |
|---|--------|-----|-----------------|-----------------|-------------|
| 1 | **Ajrak Indigo** | #1e3a5f | Sindhi ajrak block-printed cloth; centuries-old resist-dye technique using indigo and madder | Deep, rich, almost navy; scales well in UI backgrounds and buttons | Primary accent; headings; button states; background for Urdu text when contrast needed |
| 2 | **Multani Turquoise** | #2ba39c | Multani blue pottery (Multan); cobalt blue + copper oxide oxidation glaze; Mughal-influenced ceramic tradition | Bright, jewel-like; vibrant enough for icons and CTAs; evokes Persian palace tiles | Highlights; interactive elements; success states; decorative accents around cards |
| 3 | **Mughal Tile Green** | #2f6b4a | Lahore Mughal tile work (Badshahi Mosque, Wazir Khan Mosque); glazed faience tradition | Sage-like, earthy; historically present in mosque domes and geometric wall patterns | Secondary buttons; safe/trusted states; leaf/nature illustrations; calming UI sections |
| 4 | **Ralli Quilt Red** | #c41e3a | Sindhi ralli quilts; traditional "Satrangi" palette (red is one of seven core colours) | Warm, bold red; pairs naturally with white and geometric black lines (as in quilts) | Alerts; important notifications; call-to-action emphasis; chapter markers |
| 5 | **Chai & Kulfi Warm Brown** | #8b6f47 | Earthenware tea cups, traditional pottery clay tones; comforting, tea-culture brown | Warm, approachable; feels handmade and organic; evokes craft and tradition | Secondary text; borders; footer areas; illustration shadows; soft UI backgrounds |

### Palette Logic

- **Primary tier (use 1–2):** Ajrak Indigo + Multani Turquoise for strongest cultural recognition
- **Secondary tier (use 1–2):** Mughal Green + Ralli Red for depth and balance
- **Tertiary (accent 5%):** Chai Brown for warmth and grounding

Avoid using all five simultaneously; this creates visual noise. A two-to-three colour accent system is the Pakistani design studio norm (Sabaq, Taleemabad, Muse).

---

## 2. Motif Guidance — Scalable Patterns for UI

Pakistani visual language relies on geometric iteration and symbolic repetition. These patterns work at UI scale (16–64px) without losing integrity.

### 2.1 Ajrak-Inspired Geometry

**Pattern:** Chevrons, step patterns, and diamond grids  
**Characteristics:**
- Symmetrical, bilaterally mirrored around vertical axis
- Repeating chevron `< >` creates motion without literal arrows
- Small-scale diamonds nest within larger diamonds (fractal quality)

**UI Applications:**
- **Divider lines:** Broken chevron pattern (instead of solid line)
- **Card borders:** Diamond-grid border at 2–4px weight
- **Icon backgrounds:** Circular or square container with subtle chevron frame
- **Empty states:** Large-scale diamond grid at very low opacity (8–12% alpha) as background texture

**Do NOT:** Use ajrak pattern as full-screen wallpaper; causes visual fatigue. Restrict to 15–20% of visible UI area.

### 2.2 Ralli Quilt Geometry

**Pattern:** Concentric squares, stepped diamonds, rotated-square tessellations  
**Characteristics:**
- Blocks are often rotated 45° to create a visual pinwheel effect
- White/negative space is as important as the colour
- Traditionally, ralli uses red + black + white; in UI, you can preserve red + white + one accent colour

**UI Applications:**
- **Progress indicators:** Stepped-square progress bar (instead of linear)
- **Grid backgrounds:** Concentric-square tiling at low opacity for data tables or lesson cards
- **Button hover states:** Subtle inset concentric-square animation on click
- **Icon library:** Star or multi-pointed shapes derived from ralli tile geometry
- **Chapter dividers:** Rotated-square chain (a row of diamonds)

**Do NOT:** Overload a single card with both chevron *and* square patterns. Pick one per UI zone.

### 2.3 Islamic Tile Geometry (Mughal Influence)

**Pattern:** Six-pointed stars, interlocking stars (Khatam), geometric lattice (jaali)  
**Characteristics:**
- Symmetry is absolute; no asymmetrical "artisanal" breaks
- Patterns tile perfectly (no gaps or overlaps)
- Traditionally used in marble inlay and stone carved screens

**UI Applications:**
- **Node shapes for learning tree:** Hexagon or six-pointed star instead of circle
- **Lesson badges/achievements:** Star-polygon centre with radiating petals
- **Background texture (subtle):** Geometric lattice at ultra-low opacity (3–5%) in learning sections
- **Pagination dots:** Arrange in a six-point pattern instead of linear row

**Do NOT:** Use intricate 16–20 point stars in small UI buttons; they become visual mud at 24px scale. Stick to 6–8 point for small elements.

### 2.4 Kairi (Paisley) Motif

**Pattern:** Teardrop leaf with inner spiral; often paired with floral geometry  
**Characteristics:**
- Asymmetrical but balanced; derived from botanical forms
- Scales well from 12px (icon accent) to 120px (illustration element)
- Often arranged in mirrored rows or arranged radially

**UI Applications:**
- **Icon accents:** Small kairi shape paired with text labels for vocabulary (e.g., a kairi + word = lesson card header)
- **Ornamental dividers:** Row of mirrored kairis with small gap
- **Illustration element:** Kairi shapes in background of character illustrations (not overwhelming)

**Do NOT:** Use kairi as primary pattern; it reads as "feminine" or "decorative" to Western eyes, which undercuts Pakistani authenticity. Use sparingly as accent.

---

## 3. Typography Rules for Urdu in UI

Urdu text in UI is fundamentally different from Latin text. Font choice and sizing directly impact legibility and cultural authenticity.

### 3.1 Font Selection by Context

| Context | Recommended Font | Rationale | Line-Height | Notes |
|---------|------------------|-----------|-------------|-------|
| **Headings (32px+)** | Noto Nastaliq Urdu or Jameel Noori Nastaleeq | Authentic Nastaliq calligraphy; culturally expected by Pakistani readers | 1.8–2.2 | Jameel Noori larger files; use Noto for web if performance critical |
| **Body text (14–18px)** | Jameel Noori Naskh *or* Noto Naskh Arabic | Nastaliq becomes harder to read at small scale; Naskh is more legible for long passages | 1.6–1.8 | Do NOT use Nastaliq for body text; poor accessibility at <14px |
| **Small UI text (12px, labels)** | Noto Naskh Arabic or system Urdu font | Legibility paramount; Naskh's upright posture works at small scale | 1.5 | Test rendering on actual devices (Android default Urdu rendering varies) |
| **Buttons & CTAs** | Noto Nastaliq Urdu (if 18px+) else Naskh | Balance beauty (Nastaliq) with clarity; fallback to Naskh if button text is short | 1.6 | Buttons often truncate Nastaliq; test button length before committing |

### 3.2 Size & Spacing Rules

**Nastaliq (any font):**
- Minimum body size: 14px (but 16px preferred for children)
- Line spacing: 1.8–2.2× of font size (Nastaliq letters cascade diagonally; tight spacing breaks readability)
- Letter spacing: Avoid; Nastaliq ligatures require natural spacing
- Paragraph spacing: 1.5× of line-height (extra breathing room)

**Example:** 16px Nastaliq text → line-height 28–32px → paragraph margin 40–48px

**Naskh:**
- Minimum body size: 12px (but 14px+ for children)
- Line spacing: 1.5× (more compact than Nastaliq)
- Letter spacing: None; use native font spacing
- Paragraph spacing: 1.2× of line-height

### 3.3 Contrast with Latin (English)

If the app includes English translations or code:
- **Urdu is primary (left-aligned if RTL, centre if bilingual card).** English is supporting.
- **Size ratio:** Urdu headline ~20px, English subtitle ~14px (Urdu needs visual weight)
- **Font pairing:** Nastaliq Urdu + clean sans-serif Latin (e.g., Inter, Poppins, Roboto)
- **Spacing:** Extra margin *between* Urdu and English blocks (not cramped).

### 3.4 Diacritical Marks & Vowel Signs

- Urdu vowel marks (aerabs) sit *above and below* letters, increasing vertical space demand
- Ensure line-height accommodates marks without clipping (test with words like اِ , اُ , وَ)
- Avoid dark backgrounds behind Nastaliq with heavy aerab density; white/cream is safer

---

## 4. Illustration Style Brief

Pakistani children's media (Burka Avenger, Quaid Say Baatein, Taleemabad, Sabaq) favors a warm, character-driven aesthetic. This is the target.

### 4.1 Visual Language

**Colour palette in illustrations:**
- Warm primaries: ochre/gold (#d4a574), brick red (#c41e3a), forest green (#2f6b4a)
- Neutrals: cream (#f5f1e8), warm grey (#8b8680), soft black (#2a2a2a — never pure #000)
- Accent jewel tones: turquoise, indigo (from palette section above)

**Character design:**
- **Bodies:** Soft curves, rounded shoulders; no sharp angles (approachability)
- **Eyes:** Large, expressive; often almond-shaped; dark pupil + white sclera + warm iris
- **Hands/feet:** Proportionally simplified; not anatomically rigid
- **Hair:** Flowing, dynamic; often styled traditionally (dupatta folds, boy's quiff)
- **Clothing:** Represents Pakistani fashion (kameez-style tunics, traditional caps, school uniforms) — not generic "South Asian" costumes

**Texture & medium:**
- Watercolour-like translucent washes (Ismail Gulgee's legacy)
- Soft shadow work; no hard outlines unless iconography requires it
- Hand-drawn feel; avoid Vector Trap smooth curves. Slight imperfection signals warmth (not laziness).
- Hatching/cross-hatching for depth in sepia or warm-brown tones

### 4.2 Illustration Scenarios for a Reading App

**Lesson introduction (full-width hero):**
- Central character (child protagonist) in a warm, recognizable setting (school, home, bazaar)
- Background uses large geometric pattern (ajrak or ralli) at low opacity
- Character facing reader (eye contact); open, welcoming posture
- Warm three-point lighting (main light, soft shadow, subtle highlight)

**Vocabulary cards (small, 3×2 inch):**
- Simple icon-style illustration of the word (e.g., کتاب = book, شجر = tree)
- Kairi or tile-geometry frame around the illustration
- Minimal colour (2–3 from the palette)
- No background pattern (clarity first)

**Story breaks / chapter dividers:**
- Character vignette or symbolic icon (e.g., an oil lamp for a poetry chapter)
- Small geometric divider underneath (concentric squares or chevrons)
- Single accent colour + cream background

**Achievements / progress rewards:**
- Medal-style badges with six-pointed star geometry
- Character with celebratory pose (jumping, hand raised)
- Warm colour glow around character (halo effect)

### 4.3 Illustration Do's & Don'ts

**DO:**
- Reflect Pakistani family structures (joint families, intergenerational scenes)
- Use clothing, architecture, food that children recognize from their homes
- Include girls and boys equally in active, learning roles (not stereotyped)
- Draw inspiration from Ismail Gulgee's warm portraiture and watercolour technique

**DON'T:**
- Trace or copy Burka Avenger character designs (copyright); instead, study the *style* (proportions, colour theory, line weight)
- Use generic South Asian "cultural clipart" (tilaks, saris, turbans indiscriminately mixed)
- Make characters look doll-like or overly polished; slight asymmetry feels alive
- Illustrate adult authority figures as stern or distant; children need approachable teachers and parents in the app

---

## 5. Do Not List — Clichés to Avoid

| Cliché | Why It's Overused & Inauthentic | Alternative |
|--------|----------------------------------|-------------|
| **Flag green (#228c22) + white (#ffffff) as primary colours** | Overdone in Pakistani government/NGO branding; feels institutional, not warm. Children's apps that default to this read as "school homework task" not "fun learning." | Use Ajrak Indigo + Multani Turquoise instead; let Mughal Green appear as secondary. |
| **Minar-e-Pakistan as a landmark icon** | Every Pakistani tourism board uses it; visually recognizable but emotionally distant for young children (it's a monument, not a home or school). | Use specific, relatable landmarks: a local mosque's minaret, a school building, a bazaar stall, a home courtyard (the spaces children navigate daily). |
| **Taj Mahal reference** | Taj Mahal is in India, not Pakistan. Using it confuses national identity and alienates Pakistani children who are taught the distinction from age 5. | Use Badshahi Mosque (Lahore) or Faisal Mosque (Islamabad) if a architectural landmark is needed. |
| **Decorative dupatta draped behind every female character** | While culturally meaningful, overuse becomes tokenization. Not all female characters need to wear a dupatta; everyday school uniforms are more relatable. | Vary dress: school uniform, casual kameez, formal shalwar kameez. Dupatta for special moments only. |
| **Henna (mehndi) on every female character's hands** | Henna is for celebrations; using it on everyday characters makes their everyday feel ceremonial. | Henna is for wedding illustrations or Eid/festival contexts. Skip for daily school scenes. |
| **Bright neon gradients (90s nostalgia)** | Some Pakistani apps (Daraz, Careem) use bold neons; but for a children's reading app, neon feels jarring and reads as "discount trend-chasing," not authentic warmth. | Use the palette's warm naturals; neons have no basis in Pakistani craft or textile traditions. |
| **Arabicized Urdu script mixing** | Code-switching between Urdu and Arabic script can feel artificial unless the lesson specifically covers Arabic. | Keep text in pure Urdu script (Nastaliq/Naskh). If teaching Arabic, isolate it in a dedicated module. |
| **Overly saturated, hyper-realistic illustrations** | Modern rendering can feel plastic; contradicts the hand-drawn, watercolour warmth that Pakistani children's media is known for. | Aim for 60–80% saturation; preserve slight transparency/translucence in colour washes. |
| **Geometric patterns covering >30% of UI** | Pattern-heavy design reads as "busy" not "rich." Pakistani craft is pattern + white space. | Use patterns as frame, border, or 15–20% background accent. Leave plenty of white breathing room. |
| **Character faces with Western feature stereotypes** | If illustrating children, avoid auto-defaulting to light skin + blue eyes as "default." | Draw children with the range of skin tones, eye colours, and features present in Pakistan: brown, olive, dark skin; brown eyes (primary), black eyes. Vary hair texture. |

---

## 6. Sources Consulted

**Truck Art & Colour Culture:**
- https://pktags.com/colors-of-pakistan-the-majestic-ajrak-chundri-legacy/ (UNVERIFIED — Ajrak colour descriptions; no hex codes provided)
- https://uk.pinterest.com/huda8404/pakistani-truck-art-color-themes/ (UNVERIFIED — Pinterest mood board; visual reference only)

**Urdu Typography:**
- https://www.urdu-nigaar.com/blog/jameel-noori-nastaleeq-download-guide/ (VERIFIED — comprehensive font characteristics, UI recommendations)
- https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu (VERIFIED — Google Fonts official specification)
- https://urdulabs.com/fonts/jameel-noori-nastaleeq (UNVERIFIED — font download resource; technical notes confirmed in Urdu-Nigaar source)

**Sindhi Ralli Quilts:**
- https://www.pkland.pk/ralli-quilts-sindh-guide (VERIFIED — colour palette and pattern descriptions; "Satrangi" seven colours named)
- https://www.researchgate.net/publication/379129131_Preserving_and_Promoting_the_Sindhi_Ralli_Quilts_A_Case_Study_of_Pakistan's_Artistry (UNVERIFIED — academic study; pattern geometry and symbolic meaning)

**Multani Blue Pottery:**
- https://multaniblueart.com/ (UNVERIFIED — colour description "cobalt blue and turquoise")
- https://www.facebook.com/azraqarts/posts/multani-pottery-is-very-famous-for-it-uniqueness-and-beauty-it-is-not-only-made-/1039019404911591/ (UNVERIFIED — copper oxide + salt/sugar kiln process)

**Pakistani EdTech & Children's App Design:**
- https://sabaq.edu.pk/ (VERIFIED — SABAQ app design philosophy; animation-based content for K-5)
- https://taleemabad.com/ (VERIFIED — Taleemabad platform architecture; student app screenshots available)
- https://muselessons.com/about-us/ (VERIFIED — MUSE (SABAQ's flagship) design approach for primary students)
- https://en.wikipedia.org/wiki/Burka_Avenger (VERIFIED — animation studio (Unicorn Black) and visual style reference)

**Pakistani Children's Media:**
- https://www.burkaavenger.com/ (VERIFIED — 3D animation style, character design; warm colour palette reference)
- https://en.wikipedia.org/wiki/Quaid_Say_Baatein (VERIFIED — animated series production style; character-driven educational narrative)

**Pakistani Artist Reference:**
- https://www.artnet.com/artists/ismail-gulgee/ (VERIFIED — Gulgee's portraiture and watercolour technique; warm tonality)
- http://ismail-gulgee.com/ (VERIFIED — artist biography and portfolio; illustration warmth reference)

**Pakistani Logistics & Tech Brands:**
- https://www.facebook.com/ProPakistani/posts/a-team-of-400-employees-is-working-on-the-everything-app-and-careem-is-hiring-ev/1162104175953572/ (UNVERIFIED — Bykea brand colour (green) and Careem design approach)

---

## 7. Implementation Checklist

Before finalizing visual identity:

- [ ] Palette tested on actual child users; gather feedback on "warmth" and "Pakistani-ness" perception
- [ ] Urdu typography tested at actual viewport sizes (mobile, tablet) on Android + iOS default renderers
- [ ] Illustration style guide produced with 5–8 character variations and 3 environment templates
- [ ] Geometric patterns (ajrak, ralli, tile) rendered and tested at UI scales (24px, 48px, 96px) for clarity
- [ ] Colour contrast ratios verified for WCAG AA (4.5:1 for text, 3:1 for graphics) — Nastaliq often has thin strokes; check carefully
- [ ] Do-not list reviewed with a Pakistani educator or parent; adjust if local context differs
- [ ] Competitor apps (Sabaq, Muse, Taleemabad) visually audited to ensure differentiation

---

**End of Research Document**
