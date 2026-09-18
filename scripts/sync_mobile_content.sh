#!/usr/bin/env bash
# Copy the canonical content (data json, mp3 audio, fonts, lesson markdown) into the mobile app bundle.
# Run after gen_audio.py / regen_flagged.py / apply_picks.py / import_recordings.py or any data edit, then `cd mobile && npm run build`.
set -e; cd "$(dirname "$0")/.."
mkdir -p mobile/public/{audio,fonts,data/lessons}
for k in names words syllables aspirates diacritics units sentences sight numerals; do mkdir -p mobile/public/audio/$k; cp assets/audio/$k/*.mp3 mobile/public/audio/$k/; done
cp assets/fonts/NotoNaskhArabic.ttf assets/fonts/NotoNastaliqUrdu-Regular.ttf mobile/public/fonts/
cp data/letters.json data/units.json mobile/public/data/
cp course/unit_*.md mobile/public/data/lessons/
python3 - <<'PY'
import json; M=json.load(open('assets/audio/manifest.json',encoding='utf8'))
json.dump({f"{j['kind']}/{j['id']}": f"audio/{j['file'][:-4]}.mp3" for j in M}, open('mobile/public/data/audio_index.json','w',encoding='utf8'), ensure_ascii=False)
PY
echo "mobile content synced: $(ls mobile/public/audio/*/*.mp3 | wc -l) clips"
