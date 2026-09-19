# Visual UI Reference — Children's Language-Learning Apps
## What makes the best ones look and feel excellent, concretely enough to copy the principles

**Research date:** 2026-09-19
**Scope:** Palette, type, illustration style, progress/path design, button/card shaping, celebration
screens, RTL/Arabic-script typesetting, emoji usage, and review-sourced criticisms — across
Duolingo/Duolingo ABC, Khan Academy Kids, Lingokids, Kitkit School, Endless Alphabet, HOMER
Reading, Google Read Along, Noorani Qaida apps, and Rekhta Aamozish — then a recommended
direction for an Urdu reading app.

---

## Part 1 — Comparison Table

| App | Palette | Type | Illustration style | Progress/path | Buttons/cards | Celebration | Emoji | Reviewer visual gripes |
|---|---|---|---|---|---|---|---|---|
| **Duolingo (main)** | Duo green (~#58CC02) + a rotating unit-color band (blue, purple, pink, orange) on white/off-white; gold for mastered skills, gray for locked | Display: **Feather Bold** (custom, Fontsmith 2019, drawn from the owl's wing/beak shapes, not public); Body/UI: **DIN Next Rounded** (Monotype, softened corners) | Bold, bouncy, flat-vector characters; deliberate *exaggeration* ("almost caricature") + *rhythm* (varied shape/size) for personality; vector-based since ~2018 redesign, replacing hard-edged/pixel art | Node-based **skill path** — winding vertical "board game" trail of circular/badge nodes; state = color, not shape: locked=gray, active=bright unit color with a pulsing ring, complete=gold; **decay**: mastered nodes visually crack and fade gold→broken when a skill isn't practiced | Big pill/rounded-rect buttons with a **hard drop shadow directly below** (2–4px offset, no blur) that disappears on press — the "press = shadow collapses, button drops 2px" 3D affordance; cards are white with 12–16px radius | Confetti burst + character animation + audio chime + animated XP bar fill; errors get a **soft "Correct solution:" in green**, never a red X | Almost none as UI icons — real vector illustrations and the owl mascot carry emotion instead | "Feels like a slot machine," heavy monetization overlay (hearts/gems/ads) crowding the visual system; overly cute mascot fatigue in reviews of the redesign |
| **Duolingo ABC** | Same brand green + softer pastel unit bands, more white space, larger character-to-chrome ratio than the main app | Same Feather/DIN Next Rounded family, sized up for pre-readers | Even rounder, no sharp corners at all; characters (Duo, Lin, Oscar) are simplified/softened versions of main-app cast so 3–8 year-olds read them as instantly friendly | Simple **linear stepping-stone path**, fewer branches than main app (kids don't need a skill tree, just "next") | Very large single-tap targets, minimal chrome, almost no text-only buttons — icons/illustrations *are* the buttons | Same confetti+chime language, tuned gentler (softer sound, slower pacing) | None — audio narration replaces on-screen text/emoji entirely for pre-readers | Parents note it can feel "babyish" for the top of its 3–8 range by ~age 7 |
| **Khan Academy Kids** | Warm, saturated but not neon: greens/teals with mascot **Kodi the Bear** in an olive/forest green; cards use a light cream/paper background rather than pure white | Rounded geometric sans across the system (not publicly named as a single custom face; reads close to a Nunito/Quicksand family) | Soft "storybook" flat illustration, animal-cast ensemble (not just one mascot) guiding activities; gentler and less graphic-design-forward than Duolingo — reads more like a children's-book | Not a game path — a **library/shelf + activity-card grid** by subject, non-linear; progress shown as stars/badges per activity, not a snaking trail | Large rounded cards (book/shelf metaphor), soft drop shadows, no aggressive 3D-press effect — softer, "picture book" affordance vs. Duolingo's "arcade button" affordance | Star/badge collection + short celebratory animation per activity, not a full-screen event every time | Minimal; badges are custom illustrated icons, not emoji | Praised for being ad-free and calm; occasional review complaints that the content library is so large it's hard to browse (navigation, not visual, issue) |
| **Lingokids** | Bright **primary colors** (red/blue/yellow/green) deliberately — Lingokids' own design write-up states palettes shift by age: muted/low-saturation for babies, full primary-color energy for preschoolers | Rounded sans, heavy use of large friendly numerals/letters | "Fluffy," toy-like character design — Lingokids explicitly designs shapes to evoke stuffed toys because that reads as safe/positive to a child; diverse character cast | Map-like world/level select rather than a single path; unlockable characters and outfits (a Duolingo-Plus-style meta-layer for kids) | Big, rounded, colorful buttons kept away from screen edges (explicit rule: interactive elements never at the very edge, to avoid accidental exits) | Sticker/reward collection system, badges, character customization as the "reward," not just a screen animation | None as functional UI — mascots and big colorful icons instead | Some parent reviews flag ad/upsell density and a "busy" home screen with many entry points |
| **Kitkit School** | Muted-but-warm, high contrast for offline/low-power tablets (designed for refugee-camp/no-electricity deployment); not a bright-neon palette — prioritizes clarity in poor lighting/screens | Simple sans, large sizes, minimal font count (built for zero-literacy first use, no adult required) | Flat, simple, universally-legible icon-driven illustration — deliberately low on cultural specificity/text so it works across many countries with no localization | **Icon-grid home** (Play, Learn, Read, Open Library) rather than a path; each subject has its own mini game-map | Big square/rounded icon tiles, minimal chrome, designed for zero-instruction self-discovery by a child alone | Simple positive-audio + animation, kept lightweight for low-end Android tablets | None — icon pictograms instead, since the whole point is a child who may not read *any* script yet | Academic/NGO literature (it's a research-backed, award-winning app — Learning XPRIZE) praises legibility and low cognitive load over "polish" |
| **Endless Alphabet** | Saturated, candy-bright per-letter colors — each letter/monster gets its own color identity | No real "typography system" per se — the letters *are* the illustration | **Letter-monster** conceit: every letter of a word is a distinct googly-eyed, wobbly, textured "cut-paper" looking monster that must be dragged into place, then animates/eats/dances into the word's meaning | No progress path at all — it's a flat alphabetical/word-list grid; progress is implicit (which words you've played) | Drag-and-drop monster pieces rather than conventional buttons; huge tap/drag targets | The whole interaction *is* the celebration — each solved word plays a short comic animation, no separate "you did it" screen needed | None — monsters replace both emoji and icons | Reviewers (School Library Journal/Horn Book) consistently call out the "cut-paper," tactile illustration texture and sound design as the standout, not UI chrome |
| **HOMER Reading** | Warm, friendly palette leaning yellow/orange/teal on white; less saturated than Duolingo, closer to a picture-book palette | Rounded sans; heavy reliance on the child's own name/photo personalization rather than typographic flourish | Soft, warm flat illustration; the designer's own case study describes an explicit *simplification pass* — reducing screen complexity/decision points for very young users after testing with real children | Personalized **"Learn Path"** — a step sequence generated per-child from an assessment, shown as a simple forward track rather than a branching tree | Large simple cards/buttons, generous whitespace, few choices per screen (explicit UX goal per the designer write-up: reduce cognitive load for 2–8 year olds) | Positive reinforcement animations tied to the child's own avatar/name | Minimal | Design case study itself documents *why* earlier versions had too many screen elements/pain points for young kids — a rare public "what we simplified and why" account |
| **Google Read Along** | Clean, minimal, mostly white/light background so text is the hero; a simple friendly buddy character **Diya** provides the only strong color accent | System sans (Google Sans/Roboto family), optimized for legibility across many scripts including Urdu, Hindi, Bangla, Tamil, Telugu, Marathi | Minimal-chrome, almost text-and-book-cover forward; Diya is a small friendly blob/bird-like character rather than a dominant illustrated world | Star/badge count and simple "read X books" counters rather than a path or map — reading itself is the core loop, not a game board | Simple, flat, low-ornamentation buttons — this app is closer to a "reading tool" than a "game," visually restrained on purpose | Light star/badge reward on finishing a story, no confetti-scale spectacle | None — the whole design intentionally minimizes chrome so multilingual text (including Urdu) stays the visual focus | Praised for working offline and across many low-resource languages; visually the least "designed" of this set — a deliberate, useful contrast case |
| **Noorani Qaida apps (best of a weak field)** | Highly inconsistent across the category; the better-reviewed ones (e.g. "Noorani Qaida with Audio") explicitly call out UI redesigns and font-switching options in their changelogs — evidence that most started visually poor and are iterating | Mostly system default or a single Arabic-script font with no real Latin/Arabic pairing thought given | Mostly plain — colored highlight boxes over the traditional Qaida page layout, little to no custom illustration/character work; some kid-oriented ones add flat cartoon backgrounds | No path/game layer in most — literally a paginated Qaida with tap-to-hear letters, i.e. a digitized book, not a designed learning path | Basic rectangular buttons, often default OS styling | Minimal to none | Rare | This is the clearest gap in the whole category — reviewers frequently praise *audio accuracy* while criticizing dated/inconsistent visuals, cluttered ad placement, and poor font legibility |
| **Rekhta Aamozish (Urdu learning, adult-leaning)** | Not documented in public hex form; portfolio note describes "custom illustrations & interactive UI" built specifically to make **Urdu poetry** learning visual, gamified with challenges/rewards | Uses real Nastaliq/Urdu type for content, paired with a clean Latin sans for UI chrome (typical of Rekhta's broader properties) | Custom illustration commissioned specifically for this product (not stock/default) — a rare case of a *bespoke* illustration system built around Urdu content rather than skinning a generic template | Structured progressive journey ("beginners to poetry connoisseurs") — a designed learning path, unlike most Qaida apps | Not independently documented beyond "interactive UI"; treat as an example that a *custom-built* system, not a generic template, is achievable for Urdu content | Uses reward/challenge gamification (Duolingo-style layer) per its own case-study description | Not documented | No independent negative reviews surfaced in this pass; the app is a positive proof-point that a properly designed Urdu/Nastaliq learning product is buildable |

---

## Part 2 — Principles Worth Copying (with source)

1. **Color = state, not decoration, on a progress path.** Duolingo's skill path uses exactly three
   visual states — gray/locked, saturated unit-color/active, gold/complete — plus a fourth "cracked
   gold" decay state for skills that need review. No shape changes; color and a subtle crack texture
   do all the work. *Source: blog.duolingo.com/shape-language-duolingos-art-style; newform.community
   Duolingo breakdown.*

2. **A unique color band per unit/section, inside one consistent overall brand palette.** Keeps a
   long curriculum from feeling monotonous while the app still reads as one product. *Source: Duolingo
   path structure, corroborated across multiple design breakdowns.*

3. **The "press = shadow collapses" 3D button.** A hard, unblurred drop shadow directly under a
   pill-shaped button that visually "flattens" on tap is what makes Duolingo's buttons feel physically
   pressable rather than flat/web-like. Cheap to build (just a second shadow layer + a 2px translateY
   on `:active`), and it's one of the most-cited "why does this feel so good" details in UI breakdowns.
   *Source: newform.community breakdown; general Duolingo UI teardown consensus.*

4. **Exaggeration + rhythm in illustration, not realism.** Duolingo's own design team names these as
   their two levers for character personality: push details "almost to caricature," and vary shape/size
   rhythmically rather than using uniform, evenly-spaced elements. This is what separates a *character-led*
   illustration system from a *decorated* one. *Source: blog.duolingo.com/shape-language-duolingos-art-style.*

5. **Soft correction, never a red X.** Duolingo shows a green "Correct solution:" callout instead of a
   failure indicator. Gapsy Studio's children's-UX research and the existing `12_child_ux.md` file in
   this repo independently confirm this as a hard rule for young learners — errors should read as
   "here's the answer," not "you failed."

6. **Age-tunable saturation, not one fixed brand palette.** Lingokids' own published design principles
   state explicitly: lower-saturation, calmer palettes for the youngest users, full primary-color energy
   for preschoolers. If this app spans "children through adults," the palette (or at least its
   saturation/contrast) should flex by the selected age-band, not stay static. *Source: Lingokids,
   "Visual principles when designing for children," LinkedIn.*

7. **Rounded shapes read as "toy-safe."** Lingokids frames rounded corners as deliberately evoking
   stuffed toys and familiar objects — a psychological, not just aesthetic, choice. Reinforced by
   Duolingo's 2018 shift from hard-edged to rounded shapes specifically when building for kids.
   *Source: Lingokids visual-principles article; Duolingo shape-language post.*

8. **Interactive elements never sit at the screen edge.** Explicit Lingokids rule to prevent
   accidental app-exit taps or menu triggers by small, imprecise fingers — a concrete, testable
   layout constraint. *Source: Lingokids visual-principles article.*

9. **Reduce chrome and decision points per screen, then test with real children and simplify again.**
   HOMER Reading's own design case study is unusually candid: an early version had too many elements
   per screen for 2–8 year olds, and the documented fix was a deliberate *simplification pass*, not
   an addition of more delight. *Source: HOMER Reading product-design case study, hollydoodlestudio.com
   (via search-result summary; site itself returned a network error on direct fetch).*

10. **When the content is the point (reading itself), minimize the game layer.** Google Read Along
    deliberately keeps its UI restrained — plain buttons, light reward counters, no path/map — so a
    multilingual, often lower-bandwidth reading tool stays legible and fast rather than becoming a
    second "game" competing with the story. Useful counter-example to "always gamify harder."
    *Source: Google Read Along product pages, Wikipedia, newliteracies.ai guide.*

11. **A bespoke illustration system beats a skinned template, even on a modest budget.** Rekhta
    Aamozish is the one Urdu-learning product in this survey that commissioned custom illustration
    for its specific content (Urdu poetry) rather than reusing a generic children's-app look — and
    it's also the one example here of a *designed* progressive path for Urdu content specifically.
    *Source: Fatema Rangwalla (designer) LinkedIn case-study post.*

12. **Letters can be characters, not just glyphs, when teaching an alphabet.** Endless Alphabet's
    "letter monster" conceit — each letter is its own textured, googly-eyed creature that physically
    drags into place and animates the word's meaning — is a directly portable idea for teaching the
    Urdu alphabet's isolated letterforms before compound/joined forms are introduced. *Source:
    Horn Book review; Originator Kids product description.*

13. **Design for zero prior literacy and low-end hardware when that's the real constraint.** Kitkit
    School (a Learning XPRIZE-recognized, offline-first literacy app used in low-resource settings)
    prioritizes icon-only navigation, high-contrast/legible-in-poor-light palettes, and minimal font
    variety over visual richness — the right reference point if the Urdu app's Pakistani-market
    reality includes low-end Android devices and low/no adult supervision during first use. *Source:
    kitkitschool.com product pages.*

---

## Part 3 — Clichés to Avoid

- **The "AI-default cream + terracotta" palette.** A specific, now-recognizable AI-generated-UI tell:
  backgrounds around `#f5f1ea` / `#f7f5f1` / `#efeae0`, accents in `#b08947` (brass), `#b6553a`
  (terracotta), `#9a2436` (oxblood), text in near-black `#1a1714`/`#1b1814`. Fine as *one* mood board
  reference, dangerous as the whole palette — it now reads as "generated," not "designed." *Source:
  aiuxplayground.com design-taste skill (explicitly documents these as banned AI defaults).*
- **Purple/blue gradient hero glows.** The other most-cited "this looks AI-made" tell. Avoid as a
  default background treatment; if a gradient is used at all, it should be a deliberate, narrow brand
  choice, not a generic glow. *Source: same.*
- **Inter (or any single ubiquitous grotesk) as the only typeface.** Both the AI-cliché research and
  Duolingo's own approach argue against it: Duolingo built a bespoke display face precisely so its
  headlines wouldn't look like every other app. For a children's product the risk is compounded —
  Inter reads corporate/adult, not playful.
- **Emoji as functional icons.** None of the well-designed apps in this survey use emoji for buttons,
  status, or navigation — Duolingo, Khan Academy Kids, Lingokids, Kitkit, HOMER, and Read Along all
  use custom illustrated icons or characters instead. Reasons implied across the research: emoji
  render inconsistently across OS/devices (a real risk for a Pakistan-market Android-heavy audience),
  carry adult social-media connotations rather than storybook ones, and can't be color/brand-matched
  to the rest of the illustration system the way a custom vector can.
- **Three-identical-cards feature rows, centered hero over a dark mesh gradient, floating "01 / index"
  eyebrow labels, fake `<div>` screenshots, hand-drawn custom SVG icons instead of a real icon set.**
  General AI-generated-UI tells, not specific to kids' apps, but worth screening any generated
  marketing/landing surface for the course against. *Source: aiuxplayground.com.*
- **Treating Naskh/system-default Arabic-script rendering as "good enough" for Urdu.** Most weak
  Noorani-Qaida apps in this survey simply use whatever Arabic font ships with the OS at Latin-scale
  sizing and single-line spacing — legible for adults, genuinely hard for a child learning letterforms.
  See Part 4 for the concrete fix.
- **A single fixed palette/saturation level "for kids" regardless of actual age.** If the product
  spans children through adults (as this course does), one flat "kids palette" for everyone is itself
  a cliché-in-waiting; Lingokids' own research argues for tuning saturation to the age band in view.

---

## Part 4 — RTL / Nastaliq Typesetting Notes (concrete, load-bearing for this project)

- Nastaliq is a diagonal, cursive, vertically-cascading script — it needs **significantly more
  vertical space per line** than Latin or even Naskh Arabic. Documented guidance: **line-height
  ≥2.0, and ≥2.2 for web body content** using Nastaliq fonts (vs. ~1.4–1.6 typical for Latin body
  text). *Source: urdu-nigaar.com Jameel Noori Nastaleeq guide.*
- **Font size should run larger than the paired Latin/English text** — roughly 14–16pt minimum for
  Nastaliq body copy (vs. Latin body copy that reads fine at 11–13pt), and headings at 20pt+.
  *Source: same.*
- Google Fonts' own **Noto Nastaliq Urdu** page and independent pairing guides (FontTest, TypeBarn,
  TypographySmith) converge on pairing it with a **calm, low-personality Latin sans** so the two
  scripts don't visually compete — **IBM Plex Sans** is the most consistently recommended partner;
  Latin UI chrome should stay quiet while Nastaliq carries the visual "voice." *Source: fonts.google.com,
  typebarn.com, fonttest.com.*
- Set `dir: rtl`, right-align Urdu text blocks, and don't mirror illustrations/icons that have inherent
  left-right meaning (e.g., a progress arrow) purely because the text direction flipped — mirror only
  where the icon's meaning is genuinely directional. *(General RTL best practice, corroborated by the
  Medium "frustration-free guide to designing in Urdu" search summary, though the full article was
  blocked by a 403 on direct fetch — treat as directionally correct but not independently re-verified
  in full.)*
- Nastaliq needs real vertical breathing room around each line for its rising/falling baseline — don't
  reuse a Latin card/list-item height and just drop Nastaliq text into it; the line will visually clip
  or crowd its neighbors.

---

## Part 5 — Recommended Direction: Urdu Reading App for Pakistani Children *and* Adults

The product spans two very different visual-literacy levels (a first-time-reading child, and an
adult who is Urdu-literate but perhaps disengaged from formal apps). Recommendation: **one brand
identity, two saturation/density modes** — not two different apps — following Lingokids' age-tuning
principle (Part 2, #6) and HOMER's chrome-reduction principle (#9) for the child mode specifically.

### Three Palette Options (hex)

**Option A — "Subah" (Morning), warm-neutral base + single confident accent**
Avoids the AI-cliché cream/terracotta trap by using a genuinely warm off-white paired with a
saturated, non-brass, non-oxblood accent (a teal-green reads as fresh/legible against Urdu black ink
and doesn't clash with common Pakistani-flag-adjacent green associations the way a full flag-green
brand might feel derivative).
- Background: `#FAF6ED` (warm paper, lighter/cleaner than the banned `#f5f1ea` cream — verify against
  it side-by-side before finalizing)
- Primary accent: `#1E7A6E` (deep teal — for buttons, active path nodes, CTAs)
- Secondary/unit-band accent: `#F2A93B` (warm amber — for a second unit color band, celebration
  bursts)
- Text ink: `#20211D` (near-black, not pure black — matches the "off-black over pure black" rule)
- Locked/inactive: `#D8D3C4` (warm gray, not cold gray, so it still feels part of the same palette)

**Option B — "Chiraagh" (Lamp), cooler and higher-contrast, better for low-end/bright-sunlight screens**
Leans toward Kitkit School's high-contrast-for-poor-viewing-conditions logic (#13) — a real
consideration for Pakistan's outdoor/low-end-Android usage patterns.
- Background: `#FFFFFF` (pure white — deliberately, for max legibility of Nastaliq's fine strokes,
  overriding the general "avoid pure white" rule because script legibility wins here)
- Primary accent: `#2E5EAA` (confident mid-blue — reads well in daylight, distinct from most
  competitors' green-heavy palettes)
- Secondary/unit-band accent: `#D94F70` (warm rose — for a second unit, celebration screens)
- Text ink: `#1A1A1A`
- Locked/inactive: `#C7CDD6`

**Option C — "Gulzar" (Garden), the most child-forward / Lingokids-style primary-energy option**
For the child-mode skin specifically, following Lingokids' explicit "preschoolers get full primary-color
energy" principle (#6); the adult mode would dial saturation down from this base rather than starting
here.
- Background: `#FFF9EF` (soft warm cream, slightly lighter/yellower than the banned AI palette)
- Primary accent: `#3AA655` (grass green — path/active states)
- Secondary/unit-band accent: `#E85D4C` (coral-red — distinct from the banned oxblood `#9a2436`,
  much brighter/friendlier)
- Tertiary accent (for a 3rd unit band / celebration confetti mix): `#F4B93F` (sunflower yellow)
- Text ink: `#26241D`
- Locked/inactive: `#E4DECF`

*Recommendation: build the design system on Option A as the adult/default brand, and derive the
child-mode skin as a higher-saturation variant close to Option C, sharing the same underlying shape
language, type, and layout so it reads as one product family — this directly implements the
age-tunable-saturation principle rather than shipping two unrelated palettes.*

### Three Google Fonts Typeface Pairings

1. **Noto Nastaliq Urdu (display/body Urdu content) + IBM Plex Sans (Latin UI chrome, numerals,
   English labels).** The most independently-corroborated pairing found (FontTest, TypeBarn,
   TypographySmith all converge on this or near-equivalents) — safe, legible, quiet-Latin/expressive-Urdu
   balance. Best default choice for both child and adult modes.
2. **Noto Nastaliq Urdu (Urdu content) + Baloo 2 (Latin UI chrome, child mode only).** Baloo 2 is a
   rounded, friendly Google Fonts display face in the same visual family as the Nunito/Quicksand/Varela
   Round cluster identified as Feather-Bold-style alternatives — gives the child-mode skin a
   Duolingo-ABC-like warmth for buttons, numerals, and short English/Urdu-transliteration labels,
   without touching the Nastaliq content type itself.
3. **Noto Nastaliq Urdu (Urdu content) + Poppins (Latin UI chrome, adult mode).** Poppins is
   geometric, confident, and reads as more "serious learning tool" than the rounded child-mode
   option — appropriate for an adult-facing skin that still shares the same brand bones, and it's
   another face explicitly named as a Feather-Bold-style, widely-available alternative in the
   Duolingo typography research above.

### Illustration Style

Flat-vector, rounded, character-led — closer to Duolingo ABC's softened, high-white-space treatment
than to Duolingo main-app's busier skill-tree chrome. Avoid Endless-Alphabet-style heavy texture
(charming but harder to keep visually consistent across a large curriculum built over time) and
avoid Kitkit's icon-only austerity (this product isn't solving zero-literacy/zero-hardware the way
Kitkit is — some illustrated warmth is affordable and expected by the target market). Commission a
small custom cast (2–3 recurring characters, in the spirit of Rekhta Aamozish's bespoke approach)
rather than reusing generic stock-style children's-app art — letterform "characters" for the Urdu
alphabet itself (Endless-Alphabet-style, principle #12) are a strong, differentiated option worth
prototyping specifically for teaching isolated letterforms before joined/positional forms.

### Node/Path Design

A single winding vertical path (Duolingo's proven pattern) with circular nodes, color-only state
changes (locked=warm gray, active=primary accent with a pulse, complete=amber/gold), and a
color-band change per unit — but keep the path **linear, not branching**, following Duolingo ABC's
simplification for pre/early readers rather than main-Duolingo's skill-tree complexity, since this is
a structured literacy curriculum (letters → joined forms → words → sentences) with a clear intended
order, not a menu of optional skills.

### Celebration

Confetti burst + character animation + a satisfying audio chime on lesson completion (Duolingo/Duolingo
ABC pattern), scaled gentler for the child mode (softer sound, slightly slower pacing, per Duolingo
ABC's own tuning down from the main app) and scaled to a quieter badge/star acknowledgment for the
adult mode (closer to Khan Academy Kids' or Google Read Along's lower-intensity reward, since an
adult learner doesn't need full-screen confetti every few minutes to stay motivated). Errors always
resolve to a soft, non-red correction state, never a failure indicator, per principle #5.

---

## Sources (every URL opened during this research)

- https://blog.duolingo.com/shape-language-duolingos-art-style/
- https://app.newform.community/blog/duolingo-app-design-breakdown-ux-ui-analysis-2026
- https://www.designyourway.net/blog/duolingo-font/
- https://www.monotype.com/resources/duolingo-custom-font-inspired-their-owl-mascot-duo
- https://www.monotype.com/studio/portfolio/duolingo
- https://www.kristaradoeva.com/work/duolingo
- https://bethjohnson.design/duolingo
- https://60fps.design/shots/duolingo-50-day-streak-animation
- https://www.smashingmagazine.com/2026/02/designing-streak-system-ux-psychology/
- https://abc.duolingo.com/
- https://appshots.design/apps/interactive-stories-for-kids-app-shot-duolingo_abc/
- https://kitkitschool.com/ , https://kitkitschool.com/product/ , https://kitkitschool.com/faq/
- https://www.hbook.com/story/endless-alphabet-app-review (via search summary; direct fetch blocked 403)
- https://www.originatorkids.com/index.html?p=564.html
- http://www.hollydoodlestudio.com/homer-reading (via search summary; direct fetch failed DNS)
- https://learnwithhomer.com/
- https://en.wikipedia.org/wiki/Read_Along
- https://readalong.google/
- https://newliteracies.ai/guides/google-read-along/
- https://apps.apple.com/sa/app/noorani-qaida-with-audio/id6504334051
- https://riwaqalquran.com/blog/app-to-learn-quran-with-tajweed/
- https://chrome-stats.com/d/com.tarbiyati.tarbiyatinisab
- https://www.linkedin.com/posts/fatema-rangwalla-b60b181b_uxdesign-gamification-poetry-activity-7300189389467303937-4QB9 (via search summary; direct fetch 403)
- https://www.rekhta.org/CMS/FAQ
- https://medium.com/@usama.waheed/the-frustration-free-guide-to-designing-in-urdu-d1ad6cdc2690 (direct fetch 403 — not independently re-verified in full)
- https://www.urdu-nigaar.com/blog/jameel-noori-nastaleeq-download-guide/
- https://www.figma.com/fonts/noto-nastaliq-urdu/
- https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu
- https://fonttest.com/fonts/noto-nastaliq-urdu/
- https://fontscope.app/fonts/noto-nastaliq-urdu
- https://typographysmith.com/fonts/noto-nastaliq-urdu
- https://typebarn.com/font/noto-nastaliq-urdu
- https://aiuxplayground.com/skills/design-taste-frontend/
- https://gendesigns.ai/blog/ai-generated-ui-mistakes-how-to-fix
- https://www.linkedin.com/pulse/visual-principles-when-designing-children-lingokids
- https://www.lemon8-app.com/@life.withkasper/7471109579611374123 (Khan Academy Kids / Kodi reference)
- https://himalayas.app/companies/khan-academy/jobs/bilingual-content-creator-khan-academy-kids-24-months-fixed-term

Not independently loaded (dead-end searches / no usable page found): Khan Academy Kids official
hex codes (chromaxp.com and colorcodehub.com both returned DNS errors on fetch — treat the Khan
Academy Kids palette description above as descriptive, not hex-verified), Lingokids official app-store
screenshots (not directly fetched, relied on the company's own published design-principles article
instead), screensdesign.com (DNS error on both attempts).
