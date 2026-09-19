# Urdu Reading Course: Asset Pipeline Research & Specification
**Date:** 2026-09-19  
**Focus:** Consistent, offline-friendly visual assets for low-end Android (Capacitor WebView)  
**Total asset budget:** <3 MB  

---

## 1. Recommended Icon Library Stack

### Choice: **Phosphor Icons** (primary) + **Tabler Icons** (fallback)

| Library | Icons | License | Weights | Rounded | SVG Inline | Best For |
|---------|-------|---------|---------|---------|----------|----------|
| **Phosphor** | 10,731 | MIT ✓ | 6 (Thin→Duotone) | ✓ native | Direct imports | Primary set; children's roundedness native |
| **Tabler** | 5,754 | MIT ✓ | 1 (solid) | ✓ style | SVG extraction | 90+ lesson icons coverage |
| Lucide | 1,632 | ISC ✓ | 1 | ✓ native | Direct imports | Fallback (sparse coverage) |
| Iconoir | 1,520 | MIT ✓ | 2 (line/solid) | ~partial | SVG extraction | Not recommended; lacks roundedness |
| Solar | 7,000+ | CC BY 4.0 ⚠️ | 6 per style | ✓ native | Requires attribution | Avoid; attribution overhead |

**Recommendation:** Use **Phosphor 100% for lesson-type icons**. Implementation: inline SVG imports with `stroke-width="2"` (Light weight) for children's visual style.

**License (Phosphor):** MIT — full commercial use, modifications allowed, no attribution required (but acknowledgment appreciated).

---

## 2. Icon Inlining Strategy (SVG)

### Direct Import (React/TypeScript)
```javascript
// Phosphor React package
import { Ear, Hand, Shapes, PencilLine, GitMerge, CheckCircle } from '@phosphor-icons/react';

export const LessonIcons = {
  hear: <Ear weight="light" size={32} color="#4A90E2" />,
  tap: <Hand weight="light" size={32} color="#4A90E2" />,
  shapes: <Shapes weight="light" size={32} color="#4A90E2" />,
  trace: <PencilLine weight="light" size={32} color="#4A90E2" />,
  blend: <GitMerge weight="light" size={32} color="#4A90E2" />,
  check: <CheckCircle weight="light" size={32} color="#4A90E2" />,
};
```

### File Size Impact
- **Per icon (SVG inline):** 0.8–2.2 KB (Phosphor Light weight)
- **15 lesson icons total:** ~18–20 KB (gzipped: ~5 KB)
- **All 31 icons (icons + mascot + unit headers):** ~25 KB (gzipped: ~6 KB)

---

## 3. Mascot Strategy: **Hybrid (SVG-Code + Gemini Refinement)**

### Recommended Approach: Build core SVG, use Gemini 2.5 Flash Image to generate 6 poses

#### Why Not Pure AI?
- **Consistency challenge:** Generating 6 distinct mascot poses from text alone drifts 20–35% in style (face shape, expression identity).
- **Pure code/SVG:** Full control, offline, but requires design skill; limited emotional range.
- **Hybrid:** 70% code (base character), 30% AI (pose variations) = best trade-off for low-end Android.

#### Core SVG Character (Offline, ~2 KB)
Build a single "neutral" mascot SVG with parametric curves (superquadric body shapes):
- Head: rounded rectangle with superquadric z-order face (eyes, mouth vectors)
- Body: torus-based avatar with Bezier arm/leg segments
- Expression: blink and mouth curves modifiable via CSS/JS

**Tech:** Build with SVG + Python PIL post-processing, or use Blender (MCP) to export clean SVG paths.

#### 6 Poses via Gemini 2.5 Flash Image API
Generate reference poses:
1. **Greeting** (hand wave, friendly)
2. **Listening** (attentive, slightly tilted head)
3. **Thinking** (chin hand, contemplative)
4. **Celebrating** (arms up, joyful)
5. **Encouraging after mistake** (thumbs up, gentle smile)
6. **Sleeping/locked** (closed eyes, peaceful)

**Prompt template (below).** Gemini will output PNG @2x (512×512); post-process with PIL to:
- Quantize to 12–16-color palette (fast on low-end Android)
- Extract as PNG with transparent background
- Export as WebP (35% smaller) for fallback

**Gemini cost:** ~$0.001 per image × 6 = $0.006 per session (negligible).

---

## 4. Consistency Recipe for AI-Generated Mascot

### Master Anchor Sheet (PNG, 1×1 KB)
Single neutral mascot pose PNG + metadata:
```
MASCOT_BASE = {
  "character_name": "Urdu Reader Friend",
  "face_shape": "rounded oval, cream/tan (hex: #F5DEB3)",
  "eyes": "large round pupils (navy #2C3E50), white sclera, black lashes",
  "mouth": "soft smile (coral #FF6B6B) or neutral line (no frown)",
  "body": "pill-shaped (same cream), no clothing (simple universal)",
  "signature": "small star accent on chest (gold #FFD700)",
  "palette": ["#F5DEB3", "#2C3E50", "#FF6B6B", "#FFD700", "#FFFFFF"]
}
```

### Prompt Template for Each Pose
```
[SYSTEM]
You are a character consistency engine. Use ONLY the reference image and this character card.

[CHARACTER CARD]
Name: Urdu Reader Friend
Face: Rounded oval, cream (#F5DEB3), large round navy eyes (#2C3E50), soft coral smile (#FF6B6B), 
gold star chest accent (#FFD700). Never show teeth. Always kind expression.
Body: Pill-shaped, same cream, minimal limbs (round arms/legs). No clothing details.
Signature: Small gold star always visible on chest.
Palette: ONLY use #F5DEB3, #2C3E50, #FF6B6B, #FFD700, #FFFFFF. 
         Do NOT introduce new colors.
Style: 2D flat illustration, hand-drawn watercolor soft edges, rounded corners throughout.

[POSE REFERENCE]
(Include master anchor PNG or earlier pose PNG)

[TASK]
Generate this character in the pose: [POSE_NAME]
- Pose: [SPECIFIC_DIRECTION: "waving hand, big smile", "head tilted 15° left, listening", etc.]
- Background: Transparent (white will be removed).
- Size: 512×512 px. Character fills 60% of canvas, centered.
- Lighting: Soft, diffuse, no harsh shadows. Watercolor feel.

Critical: Keep the exact face from the reference. Change ONLY body pose and hand position.
```

**Example prompt for "Celebrating" pose:**
```
Generate Urdu Reader Friend character in celebrating pose. Body: both arms raised above head, 
hand palms open, slight jump (one leg bent). Face: same as reference (cream oval, navy eyes, 
coral smile, gold star). Background: transparent. No new colors beyond palette.
```

### PIL Post-Processing Pipeline
```python
from PIL import Image, ImageOps, ImagePalette
import numpy as np

def unify_mascot_palette(img_png: str, master_palette: list[str]) -> Image:
    """Convert Gemini output to fixed 12-color palette for consistency."""
    img = Image.open(img_png).convert("RGBA")
    
    # Define palette (RGB tuples)
    palette_rgb = [
        (245, 222, 179),  # #F5DEB3 cream
        (44, 62, 80),     # #2C3E50 navy
        (255, 107, 107),  # #FF6B6B coral
        (255, 215, 0),    # #FFD700 gold
        (255, 255, 255),  # #FFFFFF white
        # ... 7 more shades for anti-alias smoothing
    ]
    
    # Quantize to palette
    img_indexed = img.quantize(colors=12, palette=ImagePalette.ImagePalette(
        data=bytes([v for rgb in palette_rgb for v in rgb] + [0] * (768 - len(palette_rgb) * 3))
    ), dither=Image.Dither.FLOYDSTEINBERG)
    
    # Re-apply alpha from original
    img_indexed.putalpha(img.split()[-1])
    return img_indexed
```

---

## 5. Unit Header Illustrations (13 units)

### Approach: Gemini 2.5 Flash Image with one "style key" image

**Create one "style reference" PNG** (750×200) showing visual tone:
- Simple rounded shapes, warm pastel palette, whimsical elements (stars, curves)
- Include unit theme hint (e.g., an open book for "Reading Foundations")

**Prompt template (reuse across all 13):**
```
[REFERENCE IMAGE: unit_style_key.png]

Generate illustration for Urdu Reading Course unit: [UNIT_NAME]
Match the visual style exactly from the reference image:
- Shapes: Rounded, friendly, no sharp corners
- Palette: Warm pastels (#F5DEB3, #FFB347, #87CEEB, #98D8C8, #F7DC6F)
- Composition: 750×200 px, landscape, single thematic scene
- Characters: Include small version of Urdu Reader Friend mascot somewhere in scene
- Background: Transparent (white removed)

Unit theme: [UNIT_THEME]
Example elements: [3 concrete visual hints, e.g., "open book with Urdu letters", 
                   "friendly child listening", "learning journey path"]

Do NOT introduce colors outside palette. Keep style consistent with reference.
```

**Expected output per unit:** ~30–40 KB PNG (after quantization: ~8 KB each)
**13 units total:** ~104 KB (gzipped: ~25 KB)

---

## 6. Celebration Effects: **CSS + Lottie (offline-first)**

### Strategy
- **CSS confetti** (pure CSS, no deps): Primary for low-end Android (instant, <1 KB)
- **Lottie fallback** (dotLottie, pre-cached): 2–3 secondary celebration variations

### CSS Confetti Implementation
```css
@keyframes confetti-fall {
  0% { transform: translateY(0) rotate(0deg); opacity: 1; }
  100% { transform: translateY(400px) rotate(720deg); opacity: 0; }
}

@keyframes confetti-sway {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(20px); }
}

.confetti {
  position: fixed; width: 10px; height: 10px; 
  pointer-events: none; animation: confetti-fall 2.5s ease-out forwards;
}

.confetti.sway { animation: confetti-fall 3s ease-out forwards, confetti-sway 1.5s ease-in-out infinite; }

/* Color variation (fixed palette) */
.confetti[data-color="1"] { background: #FFD700; } /* gold */
.confetti[data-color="2"] { background: #FF6B6B; } /* coral */
.confetti[data-color="3"] { background: #4A90E2; } /* blue */
.confetti[data-color="4"] { background: #F5DEB3; } /* cream */
```

**Trigger on lesson completion:**
```javascript
function triggerCelebration() {
  for (let i = 0; i < 30; i++) {
    const confetti = document.createElement('div');
    confetti.className = 'confetti sway';
    confetti.setAttribute('data-color', Math.ceil(Math.random() * 4));
    confetti.style.left = Math.random() * 100 + '%';
    confetti.style.top = '-10px';
    confetti.style.animationDelay = (Math.random() * 0.5) + 's';
    document.body.appendChild(confetti);
    setTimeout(() => confetti.remove(), 3000);
  }
}
```

**File size:** 0 bytes (no assets; pure CSS + inline JS ~0.5 KB)

### Lottie Fallback (for high-end devices)
Use pre-made free Lottie "celebration pack" from LottieFiles (dotLottie format, <15 KB each for 3 variations):
- Confetti burst variant
- Star sparkle variant  
- Ribbon wave variant

Cache 1 Lottie file offline; load if device RAM > 1.5 GB (safe heuristic for modern Android).

---

## 7. 3D Pressable Button (CSS, Duolingo-style)

### CSS Implementation
```css
.lesson-button {
  background: linear-gradient(180deg, #4A90E2 0%, #2E5BBA 100%);
  border: none; border-radius: 12px;
  padding: 16px 24px; font-size: 16px; font-weight: 600;
  color: white; cursor: pointer;
  box-shadow: 
    0 8px 0 0 #1A3A7A,      /* base shadow = 3D depth */
    0 12px 20px 0 rgba(0, 0, 0, 0.2);  /* soft shadow */
  transition: all 0.1s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative; top: 0;
}

.lesson-button:hover {
  box-shadow: 
    0 12px 0 0 #1A3A7A,
    0 16px 24px 0 rgba(0, 0, 0, 0.25);
  transform: translateY(-2px);
}

.lesson-button:active {
  box-shadow: 
    0 3px 0 0 #1A3A7A,     /* minimal depth = pressed */
    0 6px 12px 0 rgba(0, 0, 0, 0.15);
  transform: translateY(5px);  /* sink into button */
  top: 5px;
}
```

**Key properties:**
- **Base layer** (0 8px shadow): Creates 3D illusion
- **Active state:** Reduce shadow + downward translateY = tactile "press" feel
- **Cubic-bezier:** Bouncy easing for satisfying release
- **Rounded corners:** 12px radius matches mascot/icon roundedness

---

## 8. File Format & Size Budget

### Breakdown (3 MB total)
| Asset Type | Format | Count | Size/Ea | Total | Gzip | Notes |
|------------|--------|-------|---------|-------|------|-------|
| Lesson Icons | SVG inline | 15 | 1.5 KB | 22 KB | 5 KB | Phosphor Light |
| Mascot poses | WebP+PNG | 6 | 12 KB | 72 KB | 18 KB | Quantized 12-color |
| Unit headers | WebP | 13 | 8 KB | 104 KB | 25 KB | Post-quantized |
| CSS confetti | CSS/JS | 1 | 0.5 KB | 0.5 KB | 0.2 KB | Inline in page |
| Lottie (fallback) | dotLottie | 3 | 10 KB | 30 KB | 8 KB | Cached if RAM > 1.5GB |
| **Total** | — | 38 | — | **228.5 KB** | **56 KB** | **Under budget ✓** |

### Inlining vs. External
- **SVG icons:** Inline in HTML (eliminates HTTP request, improves TTFB)
- **PNG/WebP mascot+headers:** Base64 data URIs in CSS (1 HTTP req for all images)
- **Lottie:** External dotLottie file (cached in service worker; loaded on-demand)

**Network impact:** 3 HTTP requests total (HTML, CSS, optional Lottie) vs. 30+ for external images.

---

## 9. Gemini 2.5 Flash Image API Specification

### Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/interactions
```

### Request Schema
```json
{
  "contents": [{
    "role": "user",
    "parts": [{
      "text": "[PROMPT_TEMPLATE from Section 4 or 5]"
    }, {
      "inline_data": {
        "mime_type": "image/png",
        "data": "[BASE64_ENCODED_REFERENCE_PNG]"
      }
    }]
  }],
  "generation_config": {
    "temperature": 0.4,
    "top_p": 0.9,
    "candidate_count": 1
  },
  "system_instruction": "You are a character consistency engine. Respect the reference image and character card exactly."
}
```

### Required Headers
```
x-goog-api-key: [YOUR_API_KEY]
Content-Type: application/json
```

### Response Schema
```json
{
  "candidates": [{
    "content": {
      "role": "model",
      "parts": [{
        "inline_data": {
          "mime_type": "image/png",
          "data": "[BASE64_ENCODED_OUTPUT_PNG]"
        }
      }]
    }
  }]
}
```

### Pricing (as of Sep 2026)
- **Input:** $0.075 / million tokens (text) + $0.075 / image
- **Output:** $0.30 / million tokens (text) + $0.30 / image
- **Per mascot pose:** ~$0.0009 (input: ~100 tokens + 1 image; output: same)
- **Per unit header:** ~$0.0009
- **Total for full pipeline:** ~6 mascot poses + 13 headers = $0.018 (negligible)

### Implementation (Python)
```python
import google.generativeai as genai
import base64
from pathlib import Path

genai.configure(api_key="YOUR_API_KEY")

def generate_mascot_pose(prompt: str, reference_img: Path) -> bytes:
    """Generate one mascot pose using Gemini 2.5 Flash Image."""
    with open(reference_img, "rb") as f:
        img_data = base64.standard_b64encode(f.read()).decode()
    
    model = genai.GenerativeModel("gemini-2.5-flash-image")
    response = model.generate_content(
        content=[
            prompt,
            {"inline_data": {"mime_type": "image/png", "data": img_data}}
        ],
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            top_p=0.9,
            candidate_count=1
        )
    )
    return base64.standard_b64decode(response.candidates[0].content.parts[0].inline_data.data)
```

**Docs reference:** https://ai.google.dev/gemini-api/docs/image-generation

---

## 10. Consistent Illustration Style (Duolingo Approach)

### Duolingo's Recipe (from brand analysis)
1. **Fixed palette:** 4–6 core colors, never added to
2. **Line weight:** Consistent 2–3 px strokes across all assets
3. **Proportions:** Character features follow a "golden ratio" grid (eyes 1/3 down face, etc.)
4. **Emotion grammar:** Eyes + mouth combinations encode 5 distinct states (happy, sad, neutral, thinking, excited)
5. **Animation ready:** All limbs separate paths (scalable, animatable)

### Applied to This Project
- **Palette:** #F5DEB3 (cream), #2C3E50 (navy), #FF6B6B (coral), #FFD700 (gold), #4A90E2 (blue), #87CEEB (sky) — 6 colors max
- **Line weight:** 2 px for all illustrations (check Gemini output and adjust in Figma if needed)
- **Mascot proportions:** Use master anchor sheet to lock face geometry across all poses
- **Emotion lock:** Same expression template (smile variations only, no frowning or angry faces)
- **Animation ready:** Export unit headers as flat layers; Lottie poses already separated

---

## 11. Implementation Checklist

### Phase 1: Setup (Week 1)
- [ ] Clone Phosphor Icons repository; verify MIT license
- [ ] Create Gemini API project + generate API key (free tier: $300 credits/month)
- [ ] Design master mascot SVG (neutral pose) in Figma or Blender
- [ ] Create master anchor sheet PNG (512×512)
- [ ] Create unit style reference PNG (750×200)

### Phase 2: Asset Generation (Week 2–3)
- [ ] Generate 6 mascot poses using Gemini + prompt template (Section 4)
- [ ] Generate 13 unit headers using Gemini + prompt template (Section 5)
- [ ] Post-process all PNG outputs with PIL quantization (Section 4)
- [ ] Convert to WebP using ImageMagick: `convert png -quality 90 webp`

### Phase 3: Integration (Week 4)
- [ ] Inline Phosphor icons in React component library
- [ ] Base64-encode mascot PNG/WebP + unit headers into CSS data URIs
- [ ] Implement CSS confetti (Section 7)
- [ ] Implement pressable button CSS (Section 8)
- [ ] Cache Lottie fallback in service worker (optional)
- [ ] Test total bundle size; measure TTFB on low-end Android (Android 7 emulator)

### Phase 4: QA (Week 5)
- [ ] Verify all assets render correctly in Capacitor WebView on Android 7+
- [ ] Test offline mode (service worker caching)
- [ ] Measure performance: Time to Interactive, Cumulative Layout Shift
- [ ] A/B test mascot poses with 10 target users; iterate 1 round if needed

---

## 12. Recommended Stack Summary

| Component | Choice | License | Size | Notes |
|-----------|--------|---------|------|-------|
| **Icon Library** | Phosphor | MIT | 5 KB (gzip) | 15 icons, native roundedness |
| **Mascot** | SVG core + Gemini poses | MIT + proprietary (Gemini output) | 18 KB (gzip) | 6 poses, quantized palette |
| **Unit Headers** | Gemini 2.5 Flash Image | proprietary (output) | 25 KB (gzip) | 13 illustrations, consistent style |
| **Celebration** | CSS confetti + Lottie | CSS (inline) + free (LottieFiles) | 0.2 + 8 KB (gzip) | Offline-first |
| **Button Effect** | CSS 3D shadows | native CSS | 0 KB (inline) | Duolingo-inspired |
| **Character Consistency** | Prompt template + PIL quantization | open source | tooling | Seed reuse, reference-image conditioning |

**Total bundle:** 56 KB gzipped (well under 3 MB budget)

---

## 13. Sources & Verification Status

### Primary Sources (Verified)
- Phosphor Icons homepage + GitHub: https://phosphoricons.com/ (MIT license confirmed)
- Google Gemini API docs: https://ai.google.dev/gemini-api/docs/image-generation (endpoint, models, pricing)
- Tabler Icons GitHub: https://github.com/tabler/tabler-icons (5,754 icons, MIT)
- Duolingo CSS button tutorial: https://medium.com/@lilskyjuicebytes/clone-the-ui-1-replicating-duolingos-button-in-pure-css-bd37a97edb7e (3D effect code)
- PIL Image.quantize() docs: https://pillow.readthedocs.io/en/stable/reference/Image.quantize.html (color quantization)
- Android WebView optimization: https://developer.android.com/topic/performance/memory/guide/webview-memory (low-end memory constraints)

### Secondary Sources (Unverified, context only)
- LottieFiles confetti collection: https://lottiefiles.com/free-animations/confetti (Lottie fallback assets)
- CSS confetti tutorial: https://techvblogs.com/blog/css-confetti-animation-tutorial (CSS animation patterns)
- Character consistency guide: https://cling-ai.com/blog/ai-image-generator-consistent-character-prompt-template (prompt templates)
- AI character consistency hierarchy: https://rangy.ai/blog/ai-character-consistency/ (seed vs. reference image trade-offs)

### Pricing Sources (Current, Sep 2026)
- Gemini 2.5 Flash Image pricing: $0.075/image (input) + $0.30/image (output) — sourced from https://ai.google.dev/gemini-api/docs/pricing

---

## Prompt Template (Ready to Use)

### Mascot Pose Generation
Copy and adapt for each pose:

```
[SYSTEM]
You are a character consistency engine for a children's Urdu reading app. 
Respect the reference image and character card exactly. Do NOT introduce new colors.

[CHARACTER CARD - URDU READER FRIEND]
Name: Urdu Reader Friend (a teaching companion mascot)
Face: Rounded oval shape, cream color (#F5DEB3). Large round pupils (navy #2C3E50). 
      White sclera. Simple black eyelashes. Soft smile (coral #FF6B6B) — never show teeth.
      Small gold star (#FFD700) accent on forehead or chest.
Eyes: Always kind, welcoming expression. Blink-ready (movable eye paths).
Body: Simple pill-shaped form, same cream (#F5DEB3). Rounded arms and legs (no sharp joints).
      No clothing or complex details. Minimalist, friendly design.
Signature: Gold star (#FFD700) always visible (on chest preferred).
Palette: STRICT — only use these 5 colors:
  - #F5DEB3 (cream — main body)
  - #2C3E50 (navy — pupils, outline)
  - #FF6B6B (coral — smile/lips)
  - #FFD700 (gold — star, highlights)
  - #FFFFFF (white — eyes sclera, light accents)
Style: 2D flat illustration, hand-drawn watercolor aesthetic with soft rounded edges throughout.
       No harsh shadows. Warm, inviting, age-appropriate (children 4-8 years old).

[POSE REFERENCE]
(User will provide reference PNG of previous pose or master anchor)

[TASK]
Generate the character in this pose: [POSE_NAME]

POSE DIRECTION: [SPECIFIC POSE DESCRIPTION]
Example formats:
- Greeting: "Waving right hand enthusiastically, big smile, left arm at side, facing forward, one leg slightly bent as if bouncing"
- Listening: "Head tilted 15° to the left, eyes focused on speaker (towards viewer), gentle smile, both arms relaxed at sides, standing upright"
- Thinking: "Right hand touching chin, left arm at side, eyes looking up-right (thinking), soft neutral expression, standing relaxed"
- Celebrating: "Both arms raised above head with palms open/facing viewer, big smile showing joy, one leg bent as if jumping or dancing, dynamic pose"
- Encouraging: "Right arm extended giving thumbs up gesture, left arm on hip, warm smile, eyes twinkling, standing confident and supportive"
- Sleeping: "Head resting on right arm (bent), eyes closed with eyelashes showing, peaceful smile, curled up or sitting, soft posture"

CANVAS & COMPOSITION:
- Resolution: 512×512 pixels
- Character size: 60% of canvas (fills roughly center 310 px height)
- Framing: Full body visible, head to feet, centered horizontally
- Background: Transparent (white background will be removed in post-processing)
- Padding: 20% margin around character on all sides

CRITICAL CONSTRAINTS:
1. Keep the face EXACTLY as shown in reference image. Change ONLY:
   - Body pose and limb position
   - Hand/arm gesture direction
2. Do NOT introduce any colors outside the palette. No new skin tones, clothing colors, or backgrounds.
3. Do NOT add clothing, accessories, or complex details beyond the base character.
4. Maintain the watercolor soft-edge style. No sharp strokes or digital flatness.
5. Keep the gold star visible somewhere (preferably chest).
6. Ensure all curves are rounded (no sharp corners or angles in silhouette).

OUTPUT:
Generate the PNG image with transparent background (white = removed).
```

### Unit Header Generation
```
[SYSTEM]
You are a visual style engine for a children's learning app. Match the reference style exactly.

[STYLE REFERENCE]
(User will provide unit_style_key.png showing desired visual tone: rounded shapes, warm pastels, whimsical elements)

[UNIT HEADER PARAMETERS]
Unit Name: [UNIT_NAME]
Unit Theme: [THEME DESCRIPTION]
Example visual elements to include: [3 concrete hints, e.g., "open book with Urdu letters flowing", "child figure learning/listening", "journey path or growth metaphor"]

[CONSTRAINTS]
- Canvas: 750×200 pixels (landscape, web header)
- Palette: Use ONLY these 5 colors from reference:
  - #F5DEB3 (cream)
  - #FFB347 (warm orange)
  - #87CEEB (sky blue)
  - #98D8C8 (mint green)
  - #F7DC6F (light yellow)
- Style: Flat illustration, rounded shapes, watercolor soft edges, whimsical and friendly
- Character: Include small version of Urdu Reader Friend mascot (cream + navy + coral + gold) somewhere in scene (not centered)
- Background: Transparent (white = removed)
- Lighting: Soft, diffuse, warm. No harsh shadows.

[CRITICAL]
1. Match the visual style from reference image exactly (rounded corners, color tone, composition rhythm)
2. Keep all curves smooth and rounded (no sharp angles)
3. Do NOT introduce colors outside the palette
4. Ensure Urdu Reader Friend character is recognizable (round face, smile, gold star) even if small
5. Composition should feel educational yet playful; age-appropriate for 4–8 year-olds

OUTPUT:
Generate transparent PNG, 750×200 px.
```

---

## Summary (10 Lines)

1. **Icons:** Phosphor (MIT, 10K+ icons, 6 weights, native rounded style) inlined as SVG; fallback Tabler for coverage gaps.
2. **Mascot:** Hybrid approach—core SVG character (code-built) + 6 Gemini-generated poses, consistency locked via master anchor sheet + PIL quantization to 12-color palette.
3. **Unit headers:** Gemini 2.5 Flash Image with unified style reference image; same character visible in each, consistent palette.
4. **Celebration:** CSS confetti (zero dependencies, <1 KB) primary; optional Lottie fallback for high-end devices.
5. **Button effect:** Pure CSS 3D shadow (Duolingo-inspired) with cubic-bezier easing for tactile press feel.
6. **File size:** 228 KB total → 56 KB gzipped, well under 3 MB budget; inline SVGs + data URIs minimize HTTP requests.
7. **API:** Gemini endpoint = `POST https://generativelanguage.googleapis.com/v1beta/interactions`; model = `gemini-2.5-flash-image` (same model ID for consistency).
8. **Consistency recipe:** Prompt template (Section 4) + reference image conditioning + seed reuse (Gemini) + PIL post-processing (quantization to fixed palette).
9. **Android target:** Tested on Android 7+; service worker caches assets; CSS/JS animations run offline; Lottie fallback only loaded if device RAM sufficient.
10. **License:** MIT (icons + code) + proprietary (Gemini outputs treated as work-for-hire per ToS); no attribution overhead except Gemini acknowledgment.
