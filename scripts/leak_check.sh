#!/usr/bin/env bash
# Leak check: nothing shipped or published may mention the TTS vendor, the owner's phone number or the old donation wallet.
# Scans sources, built dist, the reader/ PWA copy, docs, store text, and the built debug APK. Exits 1 on any hit.
# Dev-only provenance (scripts/, data/, .audit/) is deliberately NOT scanned: it is never copied into the app.
cd "$(dirname "$0")/.." || exit 2
PAT='eleven[ _-]?labs|elevenlabs|eleven_v3|xi[ _-]?labs|9cI5mhBtM4WtQ9Fo6jWQ|0336[ -]?0?506129|336[ -]?0?506129|\+?92[ -]?336[ -]?0506129|wa\.me|easypaisa|whatsapp (kamal|number|me|button)|(chat|message|contact) (kamal )?(on|via) whatsapp'
TARGETS=(mobile/src mobile/index.html mobile/public mobile/dist reader docs store README.md recording app course)
hits=0
scan() { # $1 = path; prints file:line:match
  local out; out=$(grep -rIinE -o "$PAT" "$1" 2>/dev/null)
  if [ -n "$out" ]; then echo "$out" | sed 's/^/LEAK  /'; hits=$((hits + $(echo "$out" | wc -l))); fi
}
for t in "${TARGETS[@]}"; do [ -e "$t" ] && scan "$t"; done
APK=mobile/android/app/build/outputs/apk/debug/app-debug.apk
if [ -f "$APK" ]; then
  tmp=$(mktemp -d); unzip -qo "$APK" -d "$tmp"
  out=$(grep -rIinE -o "$PAT" "$tmp" 2>/dev/null; grep -rainE -o "$PAT" "$tmp" --include='*.dex' --include='*.arsc' --include='*.xml' 2>/dev/null)
  out=$(echo "$out" | sed "s#^$tmp/#apk:#" | sort -u | grep -v '^$')
  if [ -n "$out" ]; then echo "$out" | sed 's/^/LEAK  /'; hits=$((hits + $(echo "$out" | wc -l))); fi
  rm -rf "$tmp"; echo "scanned APK $APK ($(stat -c %y "$APK" | cut -d. -f1))"
else echo "note: no APK found at $APK (not scanned)"; fi
if [ "$hits" -gt 0 ]; then echo "FAIL: $hits leak(s)"; exit 1; fi
echo "OK: no leaks"
