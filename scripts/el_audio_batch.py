#!/usr/bin/env python3
"""Rebuild every course clip that changed, 3 concurrent ElevenLabs requests, blind Gemini judge in the loop.

  python3 scripts/el_audio_batch.py plan            # what would be reused / generated / removed, nothing written
  python3 scripts/el_audio_batch.py run [--no-judge] [--kinds units,sentences,passages] [--limit N] [--workers 3]
  python3 scripts/el_audio_batch.py manifest        # rewrite assets/audio/manifest.json from the job list (no audio work)

Why a wrapper: scripts/el_audio.py `build` is sequential and keys clips by position (units/u04_17). When the word lists were
rebuilt the positions moved, so first every unchanged text is re-attached to its new key from a snapshot of the old audio
(same text + same frame = same clip, judge note carried over), and only genuinely new texts are generated. The frame logic
(carrier frame for short items, plain for sentences), speeds and the judge loop are el_audio's own, unchanged.
Human recordings (method "human") are never touched. Judge failures after 4 re-rolls are kept and marked "unverified".
"""
import json, os, shutil, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import el_audio, eleven

OUT, OVR, ROOT = el_audio.OUT, el_audio.OVR, el_audio.ROOT
SNAP = "/tmp/urc/audio_snapshot"  # copy of the old clips taken before the first re-key
KINDS_REKEY = ("units", "sentences", "passages")


def need_snapshot():
    if os.path.isdir(SNAP):
        return
    os.makedirs(SNAP, exist_ok=True)
    for k in KINDS_REKEY:
        if os.path.isdir(f"{OUT}/{k}"):
            shutil.copytree(f"{OUT}/{k}", f"{SNAP}/{k}")
    shutil.copy(OVR, f"{SNAP}/audio_overrides.json")
    shutil.copy(f"{OUT}/manifest.json", f"{SNAP}/manifest.json")
    print("snapshot of old audio ->", SNAP)


def plan(J, ovr_old):
    """-> (reuse {key: old_key}, todo [key], remove [files])"""
    by_text = {}
    for k, v in ovr_old.items():
        if v.get("method") in ("elevenlabs", "human") and os.path.exists(f"{SNAP}/{k}.mp3"):
            by_text.setdefault((v["text"], v.get("frame")), k)
    reuse, todo = {}, []
    for key, (kind, text) in J.items():
        if kind not in KINDS_REKEY:
            continue
        frame = el_audio.frame_for(kind, text)
        old = by_text.get((text, frame))
        if old:
            reuse[key] = old
        else:
            todo.append(key)
    return reuse, todo


def main():
    a = sys.argv[1:]
    J = {f"{k}/{i}": (k, t) for k, i, t in el_audio.jobs()}
    if a and a[0] == "manifest":
        write_manifest(J)
        return
    need_snapshot()
    ovr_old = json.load(open(f"{SNAP}/audio_overrides.json", encoding="utf8"))
    ovr = json.load(open(OVR, encoding="utf8"))
    reuse, todo = plan(J, ovr_old)
    kinds = set(a[a.index("--kinds") + 1].split(",")) if "--kinds" in a else None
    # already regenerated in an earlier run of this script: the file exists and the override text matches
    done = [k for k in todo if ovr.get(k, {}).get("text") == J[k][1] and ovr.get(k, {}).get("method") == "elevenlabs" and os.path.exists(f"{OUT}/{k}.mp3") and k not in reuse]
    todo = [k for k in todo if k not in done and (not kinds or J[k][0] in kinds)]
    stale = []
    for k in KINDS_REKEY:
        if os.path.isdir(f"{OUT}/{k}"):
            stale += [f"{k}/{os.path.splitext(f)[0]}" for f in os.listdir(f"{OUT}/{k}") if f.endswith((".wav", ".mp3")) and f"{k}/{os.path.splitext(f)[0]}" not in J]
    print(f"jobs {len(J)} | reuse {len(reuse)} | already done {len(done)} | to generate {len(todo)} | stale files {len(set(stale))}")
    if a and a[0] == "plan":
        by = {}
        for k in todo:
            by[J[k][0]] = by.get(J[k][0], 0) + 1
        print("to generate by kind", by, "chars", sum(len(J[k][1]) for k in todo))
        return
    # 1. re-attach unchanged clips
    for key, old in reuse.items():
        if ovr.get(key, {}).get("text") == J[key][1] and os.path.exists(f"{OUT}/{key}.mp3") and ovr.get(key, {}).get("via_rekey") == old:
            continue
        os.makedirs(os.path.dirname(f"{OUT}/{key}"), exist_ok=True)
        for ext in (".wav", ".mp3"):
            shutil.copy(f"{SNAP}/{old}{ext}", f"{OUT}/{key}{ext}")
        ovr[key] = {**ovr_old[old], "text": J[key][1], "via_rekey": old}
    # 2. remove stale files (keys that no longer exist) and their override rows
    for k in set(stale):
        for ext in (".wav", ".mp3"):
            if os.path.exists(f"{OUT}/{k}{ext}"):
                os.remove(f"{OUT}/{k}{ext}")
        ovr.pop(k, None)
    for k in [k for k in ovr if k.split("/")[0] in KINDS_REKEY and k not in J]:
        ovr.pop(k)
    json.dump(ovr, open(OVR, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    # 3. generate the rest
    judge = "--no-judge" not in a
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    workers = int(a[a.index("--workers") + 1]) if "--workers" in a else 3
    if limit:
        todo = todo[:limit]
    voice = eleven.load_voices()["default"] or "9cI5mhBtM4WtQ9Fo6jWQ"  # Sara, the voice of every shipped clip
    lock, t0, n_ok, n_fail = threading.Lock(), time.time(), 0, 0

    reserve = int(os.environ.get("URC_EL_RESERVE", "400"))  # never spend the last N characters of the monthly quota (payg plan, cannot be extended)

    def work(key):
        kind, text = J[key]
        need = len(el_audio.frame_text(el_audio.frame_for(kind, text), text))
        if eleven.credits() < need + reserve:
            raise RuntimeError("stopped: ElevenLabs character quota nearly used up")
        return key, el_audio.make_retry(kind, text, voice, f"{OUT}/{key}", judge=judge)

    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(work, k): k for k in todo}
        for f in as_completed(futs):
            k = futs[f]
            with lock:
                try:
                    _, note = f.result()
                    ovr[k] = note
                    n_ok += 1
                    print("ok", k, note.get("judge", ""), f"[{n_ok + n_fail}/{len(todo)} {time.time() - t0:.0f}s]", flush=True)
                except Exception as e:  # noqa
                    n_fail += 1
                    print("FAIL", k, e, flush=True)
                json.dump(ovr, open(OVR, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    write_manifest(J)
    print(f"generated {n_ok}, failed {n_fail}; chars left {eleven.credits()}")


def write_manifest(J):
    M = [{"kind": k, "id": i, "text": t, "file": f"{k}/{i}.wav"} for k, i, t in el_audio.jobs()]
    json.dump(M, open(f"{OUT}/manifest.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("manifest", len(M), "entries")


if __name__ == "__main__":
    main()
