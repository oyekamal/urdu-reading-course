# Bar (round 11g, strings / branding / grown-up gate)
1. `bash scripts/leak_check.sh` exits 0 on source, mobile/dist, reader/, docs, store, README, recording, app, course AND the built APK.
   Patterns: eleven labs / elevenlabs / eleven_v3 / the voice id, owner phone (0336 0506129 in any format), wa.me, Easypaisa, "WhatsApp Kamal/number/button".
2. `python3 mobile/tools/gate_test.py 5188` ALL PASS: correct number opens, wrong number does not, 3 wrong = 30 s lockout,
   keyboard only works, window.prompt/confirm/alert never called, Email / Copy address / Support (bank) / Reset / Export are all behind the gate.
3. `node --check` on changed JS, `npm run build` ok, `ui_audit.py` 0 violations.
4. A fresh verifier subagent finds no leftovers and cannot bypass the gate (max 4 rounds).
