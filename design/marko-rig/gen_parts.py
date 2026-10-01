#!/usr/bin/env python3
"""Generate Marko's separated body parts with Gemini (reference: the approved hello pose), for the raster rig.
    python3 design/marko-rig/gen_parts.py [part ...]   -> design/marko-rig/parts/raw_<part>.png (white bg, as returned)
"""
import sys, io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gen"))
from gen_assets import call
from PIL import Image
HERE = Path(__file__).parent; REF = str(HERE.parents[0] / "gen/out/mascot_hello.png")
COMMON = ("This is a CHARACTER PART for a cut-out animation rig of the exact character in the reference image (Marko the "
          "markhor). Same art style, same colours, same outline weight, same fur texture, same size proportions. "
          "Front view, perfectly symmetric where the character is symmetric. Only the requested part, nothing else, "
          "isolated on a plain pure white background, centered, generous margin. ")
PARTS = {
    "head": "Draw ONLY Marko's HEAD: the turquoise furry head with both saffron spiral horns, both ears, the cream face mask, "
            "both big round dark eyes with white highlights open and looking straight ahead, small nose, gentle closed smile, "
            "and the small turquoise beard tuft under the chin. A floating head like a sticker: the outline closes under the chin and beard. NO neck, NO bust, NO chest, NO shoulders, no body at all below the head.",
    "body": "Draw ONLY Marko's BODY WITHOUT HEAD AND WITHOUT ARMS: the furry turquoise torso with the cream chest/belly patch, "
            "the two short legs with saffron hooves, standing, front view. The top of the torso (neck area) is a simple "
            "rounded top. No arms at all, no head, no beard, no horns.",
    "arm":  "Draw ONLY ONE of Marko's ARMS on its own, exactly in the style of the arm hanging at the character's side in the "
            "reference: a short chunky furry turquoise arm hanging straight down, TAPERING slightly toward the wrist, with "
            "irregular fur tufts along both edges and a thick indigo outline, ending in a ROUNDED saffron hoof-paw as wide as the "
            "wrist with a small cleft. The top end is a simple rounded shoulder. Vertical, front view, one arm only, about 2.6 times "
            "as long as it is wide.",
}
for name in (sys.argv[1:] or PARTS):
    data = call(COMMON + PARTS[name], REF)
    Image.open(io.BytesIO(data)).save(HERE / "parts" / f"raw_{name}.png"); print("ok", name)
