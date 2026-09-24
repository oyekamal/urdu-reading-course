#!/usr/bin/env python3
"""ElevenLabs course audio: same job list and file layout as gen_audio.py, so the app does not change.

Short items (letter names, syllables, single short words) come out garbled when sent alone, so they are
spoken inside a frame and the target is cut out on silence (v3 returns all-zero timestamps for Urdu):
  repeat  -> "X۔ X۔ X۔"  keep the median-length take (teacher cadence)
  plain   -> the text as is (sentences, UI prompts, longer words)

  python3 scripts/el_audio.py audition <voice_id> <kind/id> [...]   # write to assets/audio/_el/<voice>/, no overwrite of real clips
  python3 scripts/el_audio.py build [--voice ID] [--kinds names,syllables] [--force] [--judge]
  python3 scripts/el_audio.py install <staged_dir> <voice_id> <kind/id> ...   # copy chosen takes into assets/audio
  --judge: Gemini checks every take (listen_judge.check) and re-rolls up to 4x; misses are kept but marked "unverified"
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eleven

ROOT = eleven.ROOT
OUT = f"{ROOT}/assets/audio"
OVR = f"{ROOT}/data/audio_overrides.json"
SHORT_KINDS = {"names", "syllables", "diacritics", "aspirates", "numerals", "sight"}


def jobs():
    # gen_audio.py imports torch at module load; parse its jobs() without that cost
    src = open(f"{ROOT}/scripts/gen_audio.py", encoding="utf8").read()
    head = src.split("def main():")[0].replace("import numpy as np, soundfile as sf, torch", "").replace("from transformers import VitsModel, AutoTokenizer", "")
    ns = {"__file__": f"{ROOT}/scripts/gen_audio.py"}
    exec(compile(head, "gen_audio_jobs", "exec"), ns)
    return list(ns["jobs"]())


FRAME = os.environ.get("URC_EL_FRAME", "carrier")  # carrier won round 3 (36/39 blind-identified vs 30 for repeat)
SPEED_SHORT, SPEED_PLAIN = float(os.environ.get("URC_EL_SPEED", "0.75")), float(os.environ.get("URC_EL_SPEED_PLAIN", "0.85"))


def frame_for(kind, text):
    return FRAME if kind in SHORT_KINDS or (kind in ("words", "units") and len(text) <= 3) else "plain"


STYLE = os.environ.get("URC_EL_STYLE", "")  # optional v3 delivery tag, e.g. "[warmly, slowly]"
TAIL = float(os.environ.get("URC_EL_TAIL", "0.25"))  # letter names decay slowly; 0.12 read as "abrupt" to the critic


def frame_text(frame, text):
    t = {"repeat": f"{text}۔ {text}۔ {text}۔", "carrier": f"یہ ہے... {text}۔", "kids": f"بچو، یہ ہے... {text}!"}.get(frame, text)
    return f"{STYLE} {t}".strip()


def segments(path, db=-45, gap=0.18):
    """Voiced (start, end) spans from ffmpeg silencedetect."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={db}dB:d={gap}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if not d:
        raise RuntimeError("unreadable take")
    h, m, s = d.groups()
    dur = 3600 * int(h) + 60 * int(m) + float(s)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    edges, t = [], 0.0
    for s, e in zip(starts, ends + [dur]):
        if s - t > 0.08:
            edges.append((t, s))
        t = e
    if dur - t > 0.08:
        edges.append((t, dur))
    return edges


def finish(src, start, end, dst_base, lead=0.10, tail=0.10):
    """Cut, pad 150/250 ms like gen_audio, loudness-normalise; .mp3 at 22.05 kHz (blind-tested = 44.1 kHz, half the size), .wav 16 kHz for the old tools."""
    s, e = max(0, start - lead), end + tail  # lead/tail capped by the caller so they never reach a neighbouring take
    af = f"atrim={s}:{e},asetpts=N/SR/TB,afade=t=in:d=0.02,areverse,afade=t=in:d=0.08,areverse,adelay=150,apad=pad_dur=0.25,loudnorm=I=-18:TP=-2"
    subprocess.run(["ffmpeg", "-loglevel", "quiet", "-y", "-i", src, "-af", af, "-ar", "22050", "-ac", "1", "-codec:a", "libmp3lame", "-q:a", "5", dst_base + ".mp3"], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "quiet", "-y", "-i", dst_base + ".mp3", "-ar", "16000", dst_base + ".wav"], check=True)


def make(kind, text, voice, dst_base, seed=None):
    """Generate one clip. Returns a note for audio_overrides.json, or raises if the take is unusable."""
    frame = frame_for(kind, text)
    with tempfile.TemporaryDirectory() as td:
        raw = f"{td}/raw.mp3"
        # short items slower (critic: "rushed", "jim" for jeem); running text at a normal-slow reading pace
        eleven.tts(frame_text(frame, text), voice, raw, seed=seed, settings={"speed": SPEED_SHORT if frame != "plain" else SPEED_PLAIN})
        seg = segments(raw)
        if not seg:
            raise RuntimeError("silent take")
        if frame == "repeat":
            if len(seg) != 3:
                raise RuntimeError(f"expected 3 takes, got {len(seg)}")  # merged or split takes = unreliable cut; caller re-rolls
            k = sorted(range(3), key=lambda j: seg[j][1] - seg[j][0])[1]
        elif frame in ("carrier", "kids"):
            if len(seg) < 2:
                raise RuntimeError(f"expected carrier + target, got {len(seg)}")
            # longest span after the carrier = the target; short spans are breaths/clicks (critic heard "just a breath" on کا، رو)
            k = max(range(1, len(seg)), key=lambda j: seg[j][1] - seg[j][0])
            if seg[k][1] - seg[k][0] < 0.2:
                raise RuntimeError("target span under 0.2 s (breath?)")
        else:
            seg, k = [(seg[0][0], seg[-1][1])], 0
        gap_before = seg[k][0] - (seg[k - 1][1] if k else 0)
        gap_after = (seg[k + 1][0] if k + 1 < len(seg) else seg[k][1] + 1) - seg[k][1]
        os.makedirs(os.path.dirname(dst_base), exist_ok=True)
        finish(raw, *seg[k], dst_base, lead=min(0.10, gap_before / 2), tail=min(TAIL, gap_after / 2))
    return {"method": "elevenlabs", "voice": voice, "frame": frame, "text": text}


def make_retry(kind, text, voice, dst_base, tries=int(os.environ.get("URC_EL_TRIES", "4")), reroll=False, judge=False):
    """judge=True: Gemini checks each take against the text and we re-roll until one matches;
    if none match, the best-scored take is kept and marked unverified so a human can look."""
    last, best = None, None
    for i in range(tries):
        try:
            note = make(kind, text, voice, dst_base, seed=None if (i or reroll) else 1)
        except RuntimeError as e:
            last = e
            continue
        if not judge:
            return note
        import listen_judge
        try:
            v = listen_judge.check(dst_base + ".mp3", text, model=os.environ.get("URC_LOOP_JUDGE", "gemini-2.5-pro"))
        except Exception as e:  # judge outage must not block generation
            return {**note, "judge": f"error: {e}"[:80]}
        score = (bool(v.get("match")), v.get("native", 0))
        if v.get("match") and v.get("native", 0) >= 4:
            for f in glob.glob(dst_base + ".best*"):
                os.remove(f)
            return {**note, "judge": "ok", "takes": i + 1}
        if not best or score > best[0]:
            best = (score, dst_base + f".best{i}")
            for ext in (".wav", ".mp3"):
                shutil.copy(dst_base + ext, best[1] + ext)
        last = RuntimeError(v.get("problem") or "judge rejected")
    if best:
        for ext in (".wav", ".mp3"):
            shutil.move(best[1] + ext, dst_base + ext)
        for f in glob.glob(dst_base + ".best*"):
            os.remove(f)
        return {**note, "judge": f"unverified: {last}"[:120], "takes": tries}
    raise RuntimeError(f"{kind}: {last}")


def main():
    a = sys.argv[1:]
    J = {f"{k}/{i}": (k, t) for k, i, t in jobs()}
    if a and a[0] == "audition":
        voice, keys = a[1], [x for x in a[2:] if not x.startswith("--")]
        for key in keys:
            k, t = J[key]
            try:
                n = make_retry(k, t, voice, f"{OUT}/_el/{voice}{os.environ.get('URC_EL_TAG', '')}/{key}", judge="--judge" in a)
                print("ok", key, n.get("judge", ""), flush=True)
            except RuntimeError as e:
                print("FAIL", key, e)
    elif a and a[0] == "build":
        voice = a[a.index("--voice") + 1] if "--voice" in a else eleven.load_voices()["default"]
        kinds = set(a[a.index("--kinds") + 1].split(",")) if "--kinds" in a else None
        ovr = json.load(open(OVR, encoding="utf8"))
        for key, (k, t) in J.items():
            if (kinds and k not in kinds) or ovr.get(key, {}).get("method") == "human":
                continue  # never overwrite a human recording
            if ovr.get(key, {}).get("voice") == voice and "--force" not in a:
                continue
            try:
                ovr[key] = make_retry(k, t, voice, f"{OUT}/{key}", judge="--judge" in a)
                print("ok", key, flush=True)
            except RuntimeError as e:
                print("FAIL", key, e, flush=True)
            json.dump(ovr, open(OVR, "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print("chars left", eleven.credits())
    elif a and a[0] == "install":
        # install <staged_dir> <voice> <kind/id> ...  — copy chosen staged takes into the app (never over a human recording)
        staged, voice, keys = a[1], a[2], a[3:]
        ovr = json.load(open(OVR, encoding="utf8"))
        n = 0
        for key in keys:
            if ovr.get(key, {}).get("method") == "human":
                continue
            for ext in (".wav", ".mp3"):
                shutil.copy(f"{staged}/{key}{ext}", f"{OUT}/{key}{ext}")
            ovr[key] = {"method": "elevenlabs", "voice": voice, "frame": frame_for(*J[key]), "text": J[key][1], "via": os.path.basename(staged.rstrip("/"))}
            n += 1
        json.dump(ovr, open(OVR, "w", encoding="utf8"), ensure_ascii=False, indent=1)
        open(f"{OUT}/MODEL.txt", "w").write(f"elevenlabs {eleven.MODEL} voice {voice} (see data/audio_overrides.json per clip; MMS for the rest)\n")
        print(f"installed {n}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
