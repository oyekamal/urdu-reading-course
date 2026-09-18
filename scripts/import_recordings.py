#!/usr/bin/env python3
"""Import human-recorded audio to replace machine-generated clips.

Two input modes:

  1. A folder of individual clips, one file per manifest id, named
     `<kind>__<id>.{wav,mp3,m4a}` (e.g. `units__u01_02.m4a`) or just
     `<id>.{wav,mp3,m4a}` (e.g. `u01_02.m4a`) when the bare id is unique
     across the whole manifest (letter/word/name ids are; some numeric
     unit/sentence ids collide across kinds, so those need the `kind__`
     prefix — the script tells you which ones on a naming clash).

       python3 scripts/import_recordings.py --folder ~/recordings/session1 \\
           --recorded-by "Ayesha Khan" --date 2026-09-18

  2. One long recording plus a CSV of start/end seconds per clip
     (columns: `key,start,end` where key is `kind/id` or a bare `id`,
     OR `kind,id,start,end` — either header works):

       python3 scripts/import_recordings.py --source ~/recordings/full.m4a \\
           --cuts recording/cuts.csv --recorded-by "Ayesha Khan" --date 2026-09-18

Every matched clip is: decoded to 16 kHz mono (ffmpeg), silence-trimmed
(simple RMS-over-20ms-frames threshold, numpy), peak-normalised to 0.9,
padded with the same 0.15 s lead / 0.25 s tail gen_audio.py uses, and written
to assets/audio/<kind>/<id>.wav + .mp3. Each imported clip is recorded in
data/audio_overrides.json as {"method": "human", ...} so gen_audio.py's
`if not os.path.exists(wav) and f"{kind}/{id_}" not in ovr` guard skips it on
every future regeneration.

Requires only python3 + numpy + soundfile + ffmpeg on PATH (all already used
by scripts/gen_audio.py and scripts/regen_flagged.py in this repo).

`--dry-run` reports what would happen (matches, mismatches, coverage after)
without writing or converting anything.
`--assets-root` / `--overrides-file` let you redirect output for a test run
without touching the real assets/audio or data/audio_overrides.json — see
the worked example at the bottom of this docstring and in README.md.
"""
import argparse
import csv
import datetime
import glob
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 16000
LEAD_S, TAIL_S = 0.15, 0.25
PEAK = 0.9
AUDIO_EXTS = (".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac", ".webm")


def load_manifest(root):
    manifest = json.load(open(f"{root}/assets/audio/manifest.json", encoding="utf8"))
    kind_id = set()
    bare_id_to_kinds = {}
    for j in manifest:
        kind_id.add((j["kind"], j["id"]))
        bare_id_to_kinds.setdefault(j["id"], []).append(j["kind"])
    return manifest, kind_id, bare_id_to_kinds


def resolve_stem(stem, kind_id, bare_id_to_kinds):
    """Return (kind, id) for a filename stem, or (None, reason) if it can't be resolved."""
    if "__" in stem:
        kind, id_ = stem.split("__", 1)
        if (kind, id_) in kind_id:
            return kind, id_
        return None, f"'{kind}/{id_}' is not in manifest.json"
    kinds = bare_id_to_kinds.get(stem)
    if not kinds:
        return None, f"id '{stem}' not found in manifest.json in any kind"
    if len(kinds) > 1:
        return None, f"id '{stem}' is ambiguous across kinds {kinds} — rename to '<kind>__{stem}.<ext>'"
    return kinds[0], stem


def ffmpeg_decode_to_wav(src_path, dst_wav):
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", src_path, "-ar", str(SR), "-ac", "1", dst_wav],
        check=True,
    )


def rms_trim(a, sr=SR, thresh_db=-35.0, frame_ms=20, pad_ms=30):
    """Trim leading/trailing silence using RMS-over-fixed-frames vs. a threshold
    relative to the loudest frame in the clip. Simple by design (per spec) —
    good enough for a human recording read at a normal pace, not a general
    speech-activity detector."""
    if len(a) == 0:
        return a
    frame = max(1, int(sr * frame_ms / 1000))
    n_frames = len(a) // frame
    if n_frames < 2:
        return a
    usable = a[: n_frames * frame].reshape(n_frames, frame).astype(np.float64)
    rms = np.sqrt(np.mean(usable**2, axis=1) + 1e-12)
    peak_rms = rms.max()
    if peak_rms <= 1e-9:
        return a  # silent clip; nothing to trim against
    rms_db = 20 * np.log10(rms / peak_rms + 1e-12)
    active = np.where(rms_db > thresh_db)[0]
    if len(active) == 0:
        return a
    pad = int(sr * pad_ms / 1000)
    start = max(0, active[0] * frame - pad)
    end = min(len(a), (active[-1] + 1) * frame + pad)
    return a[start:end]


def peak_normalise(a, peak=PEAK):
    m = np.abs(a).max()
    if m < 1e-9:
        return a.astype(np.float32)
    return (a / m * peak).astype(np.float32)


def pad_clip(a, sr=SR):
    return np.concatenate([np.zeros(int(LEAD_S * sr), dtype=np.float32), a, np.zeros(int(TAIL_S * sr), dtype=np.float32)]).astype(np.float32)


def process_array(a, sr=SR):
    a = rms_trim(a, sr)
    a = peak_normalise(a)
    a = pad_clip(a, sr)
    return a


def write_clip(a, kind, id_, assets_root, dry_run):
    out_dir = f"{assets_root}/{kind}"
    wav_path = f"{out_dir}/{id_}.wav"
    mp3_path = f"{out_dir}/{id_}.mp3"
    if dry_run:
        return wav_path
    os.makedirs(out_dir, exist_ok=True)
    sf.write(wav_path, a, SR)
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-q:a", "4", mp3_path],
        check=True,
    )
    return wav_path


def load_overrides(path):
    if os.path.exists(path):
        return json.load(open(path, encoding="utf8"))
    return {}


def save_overrides(ovr, path, dry_run):
    if dry_run:
        return
    json.dump(ovr, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=1)


def coverage_report(manifest, overrides):
    total = len(manifest)
    human = sum(1 for k in overrides if overrides[k].get("method") == "human")
    other_override = sum(1 for k in overrides if overrides[k].get("method") not in (None, "human"))
    machine = total - human - other_override
    print(f"\nCoverage: {human}/{total} human, {other_override}/{total} machine-but-overridden (regen_flagged.py etc.), {machine}/{total} plain machine (gen_audio.py default)")
    by_kind = {}
    for j in manifest:
        key = f"{j['kind']}/{j['id']}"
        by_kind.setdefault(j["kind"], {"total": 0, "human": 0})
        by_kind[j["kind"]]["total"] += 1
        if overrides.get(key, {}).get("method") == "human":
            by_kind[j["kind"]]["human"] += 1
    for kind, c in by_kind.items():
        print(f"  {kind:12s} {c['human']:3d}/{c['total']:3d} human")


def gather_folder_jobs(folder, kind_id, bare_id_to_kinds):
    jobs, errors = [], []
    for path in sorted(glob.glob(os.path.join(folder, "*"))):
        base = os.path.basename(path)
        stem, ext = os.path.splitext(base)
        if ext.lower() not in AUDIO_EXTS:
            continue
        kind, id_or_reason = resolve_stem(stem, kind_id, bare_id_to_kinds)
        if kind is None:
            errors.append(f"{base}: {id_or_reason}")
            continue
        jobs.append((kind, id_or_reason, path, None, None))
    return jobs, errors


def gather_cuts_jobs(cuts_csv, kind_id, bare_id_to_kinds):
    jobs, errors = [], []
    with open(cuts_csv, encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start = float(row["start"])
            end = float(row["end"])
            if "key" in row and row["key"]:
                key = row["key"].strip()
                if "/" in key:
                    kind, id_ = key.split("/", 1)
                else:
                    kind, id_ = resolve_stem(key, kind_id, bare_id_to_kinds)
            elif "kind" in row and row.get("kind"):
                kind, id_ = row["kind"].strip(), row["id"].strip()
            else:
                kind, id_ = resolve_stem(row["id"].strip(), kind_id, bare_id_to_kinds)
            if kind is None or (kind, id_) not in kind_id:
                errors.append(f"row {row}: could not resolve to a manifest kind/id")
                continue
            jobs.append((kind, id_, None, start, end))
    return jobs, errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", help="folder of per-clip recordings named <kind>__<id>.ext or <id>.ext")
    ap.add_argument("--source", help="one long recording (with --cuts)")
    ap.add_argument("--cuts", help="CSV of start,end seconds per clip id (with --source)")
    ap.add_argument("--recorded-by", default="unknown", help="speaker name/id for audio_overrides.json")
    ap.add_argument("--date", default=datetime.date.today().isoformat(), help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    ap.add_argument("--assets-root", default=f"{ROOT}/assets/audio", help="override assets/audio root (for testing)")
    ap.add_argument("--overrides-file", default=f"{ROOT}/data/audio_overrides.json", help="override audio_overrides.json path (for testing)")
    ap.add_argument("--manifest-root", default=ROOT, help="repo root to read manifest.json/letters.json from (for testing)")
    args = ap.parse_args()

    if not args.folder and not (args.source and args.cuts):
        ap.error("pass either --folder, or --source together with --cuts")

    manifest, kind_id, bare_id_to_kinds = load_manifest(args.manifest_root)

    if args.folder:
        jobs, errors = gather_folder_jobs(args.folder, kind_id, bare_id_to_kinds)
    else:
        jobs, errors = gather_cuts_jobs(args.cuts, kind_id, bare_id_to_kinds)

    for e in errors:
        print(f"SKIP: {e}", file=sys.stderr)

    if not jobs:
        print("No matched clips to import.", file=sys.stderr)
        sys.exit(1)

    print(f"{len(jobs)} clip(s) matched" + (f", {len(errors)} skipped (see above)" if errors else ""))

    overrides = load_overrides(args.overrides_file)
    tmpdir = tempfile.mkdtemp(prefix="urc_import_")
    source_wav = None
    imported = []
    try:
        if args.source:
            source_wav = os.path.join(tmpdir, "source.wav")
            print(f"Decoding source recording {args.source} -> 16 kHz mono ...")
            if not args.dry_run:
                ffmpeg_decode_to_wav(args.source, source_wav)
            else:
                # still decode in dry-run so we can report real durations/levels
                ffmpeg_decode_to_wav(args.source, source_wav)
            full, sr = sf.read(source_wav, dtype="float32")
            assert sr == SR

        for kind, id_, path, start, end in jobs:
            key = f"{kind}/{id_}"
            if path is not None:
                tmp_wav = os.path.join(tmpdir, f"{kind}__{id_}.wav")
                ffmpeg_decode_to_wav(path, tmp_wav)
                a, sr = sf.read(tmp_wav, dtype="float32")
            else:
                s0, s1 = int(start * SR), int(end * SR)
                a = full[s0:s1]
            a = process_array(a)
            out_path = write_clip(a, kind, id_, args.assets_root, args.dry_run)
            overrides[key] = {"method": "human", "recordedBy": args.recorded_by, "date": args.date}
            imported.append((key, out_path, len(a) / SR))
            action = "would write" if args.dry_run else "wrote"
            print(f"  {key:24s} {action} {out_path}  ({len(a)/SR:.2f}s)")
    finally:
        for f in glob.glob(os.path.join(tmpdir, "*")):
            os.remove(f)
        os.rmdir(tmpdir)

    save_overrides(overrides, args.overrides_file, args.dry_run)
    if args.dry_run:
        print(f"\nDRY RUN: {len(imported)} clip(s) would be imported. Nothing was written.")
        # report current coverage plus what a real run would add, without mutating the file
        preview = load_overrides(args.overrides_file)
        for key, *_ in imported:
            preview.setdefault(key, {"method": "human"})
        coverage_report(manifest, preview)
    else:
        print(f"\n{len(imported)} clip(s) imported. data/audio_overrides.json updated ({args.overrides_file}).")
        coverage_report(manifest, overrides)
        print("Now run: python3 scripts/build_app.py   (rebuilds app/index.html + app/audio.json from the new audio)")


if __name__ == "__main__":
    main()
