# 19. Brand colour system for "Urdu Qaida: Learn to Read Urdu"

Date: 2026-10-13. Builds on `14_pakistani_visual_identity.md` (ajrak indigo, Multani turquoise, saffron, ralli red); that cultural case is not repeated here.

## Bottom line

Keep the teal-indigo-saffron idea. The current palette's flaw is tonal, not hue: the teal is about 18 tone points too light to carry white labels, and the pale cool paper is the wrong end of the one reading-colour study found. Move the **action** teal to #00756B, keep #1E9C8F as the mascot/illustration teal, warm the paper, and replace red/green feedback with a pair that survives protanopia.

## Findings

### 1. What other apps use
| App | Colour | Basis |
|---|---|---|
| Duolingo | Feather Green #58CC02, Mask Green #89E219, Eel #4B4B4B, Macaw #1CB0F6 | Hex from brandpalettes.com plus the fills in Duolingo's own page. `design.duolingo.com/identity/color` 301-redirects to the blog hub, so the official guideline text was not read. |
| Duolingo ABC (kids reading) | Same green plus yellow | Sampled from App Store icon |
| Khan Academy Kids | Teal-green about #08B898, orange accent | Sampled from App Store icon; no brand page found |
| Lingokids | Orange about #F87838 on cream | Sampled |
| ABCmouse | Yellow about #F8E818 | Sampled |
| Sesame Street | #00AF42 green, #FCD000 yellow | brandpalettes.com (third party) |
| Toca Boca, Finch | Icon samples too noisy to trust | Not used |

Icon samples are 16-step quantised, so each channel is within about 8. Two points follow. First, a teal-green primary is already normal in kids' learning (Khan Kids), so teal is not a risk. Second, Duolingo's own white-on-#58CC02 contrast is 2.09:1 (computed). It gets away with this because logotypes are exempt under WCAG 1.4.3 and because it uses a darker lip on buttons. We should not copy the raw value.

### 2. Colour and children
- Boyatzis and Varghese (1994, *J. Genetic Psychology* 155(1)): children link bright colours with positive feelings and brown, black and grey with negative ones. I read only the abstract-level summary because the PDF was a scan.
- Zentner (2001, *Developmental Science*): children as young as 3 detect colour-emotion links. The abstract does not state preference results. Secondary snippets say 3-4 year olds favour bright, saturated colours; not verified from the paper.
- Plass, Heidig, Hayward, Homer, Um (2014, *Learning and Instruction* 29): warm colours plus round, face-like shapes raised comprehension. I read this from a search-result snippet; the paper was behind a 403.
- Rello and Bigham (2017, ASSETS '17; n=341, 89 dyslexic; read via a docslib copy): warm backgrounds (peach, orange, yellow) beat cool ones (blue, blue-grey, green) on reading performance. The authors say cool colours need not be avoided. Caveat: they tested saturated fills with black text, on adults.
- Hughes and Wilkins (2000, *J. Research in Reading* 23): for ages 5-7, text size and spacing drove reading speed; I found no colour effect in it. Colour matters less than Nastaliq/Naskh size here.
- Mehta and Zhu (2009, *Science* 323:1226): red favoured detail work and blue favoured creative work. It had an adult Canadian sample, and a 2012 poster questioned it. I use it only as a reason not to put red in the primary slot, nothing stronger.
- Kuhbandner and Pekrun (2013, *Emotion*): red boosted memory for negative words and green for positive words. This suggests red should mean "wrong", which argues against red as a decorative primary.
- Honest gap: I found no study of tinted versus white backgrounds for early readers, and none measuring saturation on 4-10 year olds' reading. The paper-colour advice below is an extrapolation.

### 3. Accessibility
- WCAG 2.2 1.4.3: text needs 4.5:1; large text (18pt, or 14pt bold) needs 3:1. Logotypes are exempt.
- WCAG 2.2 1.4.11: UI components and meaningful graphics need 3:1 against adjacent colours.
- APCA (candidate for WCAG 3): Lc 90 is the body-text target and Lc 75 the minimum for text columns. It says WCAG 2.x overstates dark-colour contrast, so dark mode should get an extra check.
- CVD prevalence is about 1 in 12 men and 1 in 200 women (colourblindawareness.org); NEI confirms red-green is the commonest type. A teen/adult male cohort in the diaspora audience will include affected users.
- I simulated deuteranopia and protanopia (Machado 2009 matrices, my own code). The current good/bad pair #3E9A5E and #C74A3B scores CIELAB ΔE 19.8 (deut) and 17.6 (prot). That is weak, and any red-green pair relies on hue alone.
- Teal versus leaf green stays distinguishable (ΔE about 26 in both). Teal is blue-leaning, so it is a safer primary than a pure green, which collapses toward olive/brown with red.

### 4. Cultural
- The Pakistan flag green is dark: #00401A (Wikipedia; the government text says only "dark green"). Wikipedia says the green stands for the Muslim-majority population. A leaf or bright green therefore invites "religious studies app" or "government form" readings, and a qaida teaching Urdu script, not Quran recitation, should not claim it. This supports the previous report's "avoid flag green".
- Qaida cover conventions: I could not establish a firm convention from primary sources. Sampled covers: OUP Pakistan's Urdu Qaida for Beginners is red and saffron on white; Yassarnal Quran is purple and yellow with an ornate border (azeembooks); the Darussalam Qurani Qaidah has muted olive/green. No single dominant hue, so we have no convention to conform to or break.
- Manuscripts: Wikipedia's Persian miniature article describes bright, pure mineral pigments and gold. The page did not name lapis. Gold or saffron as the reward colour is well supported; indigo as ink fits the lapis-to-ajrak lineage.

### 5. Dark mode
- Material 3 (material-color-utilities source and Android docs, read): dark primary is tone 80, light primary tone 40; dark surface is tone 6, light surface tone 98; neutral palette chroma is 6 and primary chroma 36. So accents get lighter and less chromatic in dark mode, and surfaces are near-neutral with only a trace of tint.
- Apple HIG Dark Mode (read via its JSON): base and elevated backgrounds, dimmer backgrounds and brighter foregrounds, "not necessarily inversions", and a 4.5:1 floor with 7:1 for small custom text.
- The current dark palette has surfaces of chroma about 21-25 (a clear navy) and an accent at tone 68 and chroma 46. Both are more saturated than M3 would produce. The accent also sits 12 tone points below M3's tone 80, leaving it 6.9:1 on paper, which passes but vibrates.

## What the current palette gets wrong
1. White on #1E9C8F is 3.38:1, which fails 4.5:1 for button labels. The accent on paper is 3.13:1, so teal text and links fail.
2. Saffron on white is 2.0:1. It fails 3:1 as an outline or icon, so it may only be a fill with ink text (ink on saffron is 6.6:1).
3. Good #3E9A5E on white is 3.51:1, so green text fails too.
4. Red/green feedback depends on hue alone (ΔE under 20 in CVD).
5. Pale cool paper #F2F7F6 sits on the cool side of the one background-colour study found. Weak evidence, but nothing supports cool.
6. Dark surfaces are more saturated than M3 and the accent is off-tone.

## Recommendation: one system

| Role | Light | Dark | Single strongest reason |
|---|---|---|---|
| Primary (action) | **#00756B** | **#82D5C9** | Passes white-label contrast (5.59:1) while staying in the Multani/Marko teal hue; dark value is M3 tone 80. |
| Mascot / illustration teal | #1E9C8F (unchanged) | #1E9C8F | Marko's fur needs no recolour; used only for non-text fills (3.14:1 on paper, so ok for graphics). |
| Reward / secondary | **#F2A93B** saffron | **#FFB94E** | Warm hues helped comprehension (Plass 2014); always a fill with ink text, never text or outline on paper. |
| Ink | **#1E2F55** ajrak indigo | **#E6E8F0** | 12.2:1 on paper; the lapis/ajrak tie to the culture is already established. |
| Paper | **#FBF6EC** warm cream | **#10131C** | Warm over cool per Rello and Bigham; dark is a near-neutral navy (chroma 10) after M3's chroma-6 rule. |
| Card | **#FFFFFF** + 1px #E6DDCB border | **#181B25** | White cards give ink 13.2:1; the border replaces contrast lost on cream. |
| Success | **#1D6730** | **#9ED4A0** | Dark and low-lightness, so it stays distinct from the error colour by lightness as well as hue. |
| Error ("try again") | **#C0426A** berry-rose | **#FF9DB5** | Rose, not red: ΔE vs success is 18 (deut) and 37 (prot) against 17.6 for the old pair under protanopia, and it avoids a harsh "red = wrong" for 5-year-olds. |

Computed contrast (WCAG): primary text on paper 5.19:1; white on success 6.92; white on error 4.97; error on paper 4.61. Dark: text on paper 15.2; teal on card 10.07; saffron on card 10.06. Every dark accent clears 7:1.

Rules that make it work: success and error always pair with an icon (tick or cross) and a Marko reaction, never colour alone; saffron never carries text; no flag green and no red in the chrome.

### Rejected alternatives
- **Leaf green (Duolingo's #58CC02 family).** Direct visual collision with Duolingo and its ABC app, 2.09:1 with white, and Wikipedia's reading of the flag green as Islamic green risks a religious/national read.
- **Ajrak indigo as the primary (e.g. #2F4A8A).** Blue is the safest hue for CVD, but indigo is already the ink, so a blue primary leaves no brand hue and buttons would look like body text. It also looks like a bank or LMS, not a child's app.
- **Saffron/orange as the primary.** Warm colours helped learning (Plass 2014) and reading (Rello 2017), but orange cannot carry white text (about 2:1), it reads as a warning, and it would take the reward colour away from its job.

### Mascot
Marko can stay teal (#1E9C8F). Put his eyes, horn tips and outline in ink indigo and give him one saffron accessory so he sits on cream and on dark navy without a halo.

## Sources actually read
- https://brandpalettes.com/duolingo-colors/
- https://design.duolingo.com/identity/color (redirected to https://blog.duolingo.com/hub/design/ with no colour text; hex values from inline fills only)
- https://brandfetch.com/khankids.org (hex scrape only)
- https://brandpalettes.com/sesame-street-color-codes/
- https://itunes.apple.com/search (App Store icon artwork, sampled for Khan Kids, Lingokids, ABCmouse, Duolingo, Duolingo ABC)
- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
- https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html
- https://www.colourblindawareness.org/colour-blindness/
- https://nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness
- https://en.wikipedia.org/wiki/Flag_of_Pakistan
- https://en.wikipedia.org/wiki/Persian_miniature
- https://www.azeembooks.com/products/yassarnal-quran-tajweed-guide-with-colorful-ornate-design
- https://oup.com.pk/school-textbooks/urdu/urdu-qaida/urdu-qaida-for-beginners.html (cover image sampled)
- https://darussalam.pk/products/qurani-qaidah-14x21 (cover image sampled)
- https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Color.md
- https://raw.githubusercontent.com/material-foundation/material-color-utilities/main/dart/lib/scheme/scheme_tonal_spot.dart
- https://raw.githubusercontent.com/material-foundation/material-color-utilities/main/dart/lib/dynamiccolor/material_dynamic_colors.dart
- https://developer.android.com/design/ui/mobile/guides/styles/color
- https://developer.apple.com/tutorials/data/design/human-interface-guidelines/dark-mode.json
- https://docslib.org/doc/1403611/good-background-colors-for-readers-a-study-of-people-with-and-without-dyslexia (Rello and Bigham 2017)
- https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.00206/full (first 100k chars; citations to Boyatzis and Cimbalo)
- Abstracts via Europe PMC and Crossref APIs: Mehta and Zhu 2009, Kuhbandner and Pekrun 2013, Zentner 2001, Hughes and Wilkins 2000
- Search-result snippet only (page not readable, 403): Plass et al. 2014, https://www.sciencedirect.com/science/article/pii/S0959475213000273
- Computed locally: contrast ratios, Machado CVD simulation, HCT tone values (`materialyoucolor` library)
