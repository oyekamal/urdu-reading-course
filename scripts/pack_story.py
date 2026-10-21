#!/usr/bin/env python3
"""design/words/story_final/*.jpg (p01 = unit 1 passage, s05_02 = unit 5 sentence 2) -> mobile/public/img/story/<id>.webp (384px) + list.json."""
import json, os, glob
from PIL import Image
ROOT = os.path.abspath(f"{os.path.dirname(__file__)}/.."); out = f"{ROOT}/mobile/public/img/story"; os.makedirs(out, exist_ok=True); ids = []
for f in sorted(glob.glob(f"{ROOT}/design/words/story_final/*.jpg")):
    i = os.path.basename(f)[:-4]; im = Image.open(f).convert("RGB").resize((384, 384), Image.LANCZOS); im.save(f"{out}/{i}.webp", quality=82, method=6); ids.append(i)
json.dump(ids, open(f"{out}/list.json", "w")); print(len(ids), "story pictures")
