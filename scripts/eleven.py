#!/usr/bin/env python3
"""ElevenLabs TTS for course clips (stdlib only). Key from ELEVENLABS_API_KEY or repo .env.
Voices live in data/voices.json ({"default": id, "voices": {id: {name, note}}}); Voice Studio adds to it.

  python3 scripts/eleven.py <voice_id> "<urdu text>" out.mp3     # one clip
"""
import json, os, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICES = f"{ROOT}/data/voices.json"
MODEL = os.environ.get("URC_EL_MODEL", "eleven_v3")  # only v3 models list Urdu (checked /v1/models 2026-09-24)
# ponytail: one settings preset for every clip; per-clip tuning lives in audio_overrides.json if a family needs it
SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.0, "use_speaker_boost": True, "speed": float(os.environ.get("URC_EL_SPEED", "0.85"))}  # 1.0 rushed letter names ("jim" for jeem)


def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k and os.path.exists(f"{ROOT}/.env"):
        for line in open(f"{ROOT}/.env"):
            if line.startswith("ELEVENLABS_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"')
    if not k:
        sys.exit("ELEVENLABS_API_KEY missing (env or repo .env)")
    return k


def api(path, body=None, method=None):
    req = urllib.request.Request(f"https://api.elevenlabs.io{path}", method=method or ("POST" if body is not None else "GET"),
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"xi-api-key": key(), "Content-Type": "application/json"})
    for i in range(6):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < 5:  # plan allows 3 concurrent requests; back off and retry
                time.sleep(3 * (i + 1))
                continue
            raise RuntimeError(f"ElevenLabs {e.code}: {e.read()[:300].decode(errors='replace')}") from None


def tts(text, voice_id, out, settings=None, seed=None):
    """Write an mp3 of `text` to `out`. seed=None lets a re-roll give a different take."""
    body = {"text": text, "model_id": MODEL, "language_code": "ur", "voice_settings": {**SETTINGS, **(settings or {})}}
    if seed is not None:
        body["seed"] = seed
    audio = api(f"/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128", body)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "wb").write(audio)
    return out


def load_voices():
    return json.load(open(VOICES, encoding="utf8")) if os.path.exists(VOICES) else {"default": None, "voices": {}}


def save_voices(v):
    json.dump(v, open(VOICES, "w", encoding="utf8"), ensure_ascii=False, indent=1)


def credits():
    s = json.loads(api("/v1/user/subscription"))
    return s["character_limit"] - s["character_count"]


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    print(tts(sys.argv[2], sys.argv[1], sys.argv[3]), f"({credits()} chars left)")
