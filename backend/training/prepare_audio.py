"""Stream HF audio and index explicit Kaggle labels into an auditable manifest."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
import traceback
from pathlib import Path

from backend.training.audio_protocol import finalize, recording_key, validate_manifest

LABELS = {"real": 0, "bonafide": 0, "bona-fide": 0, "bonafied": 0, "human": 0,
          "fake": 1, "spoof": 1, "synthetic": 1, "generated": 1}
EXTS = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}


def speaker_key(value):
    text = str(value)
    try:
        number = float(text)
        return str(int(number)) if number.is_integer() else text
    except ValueError:
        return text


def folder_label(path, root, default=None, mappings=None):
    labels = {**LABELS, **{k.lower(): v for k, v in (mappings or {}).items()}}
    values = {labels[p.lower()] for p in path.relative_to(root).parts[:-1] if p.lower() in labels}
    if len(values) > 1:
        raise ValueError(f"Conflicting class folders: {path}")
    return next(iter(values)) if values else default


def prepare(args):
    from datasets import Audio, get_dataset_config_names, get_dataset_split_names, load_dataset
    import soundfile as sf
    import numpy as np

    spec = json.loads(Path(args.sources).read_text())
    if getattr(args, 'preflight_only', False):
        # Exercise the actual schema and one decoded row before indexing huge mounts.
        for source in spec['hf']:
            token = os.getenv('HF_TOKEN')
            configs = get_dataset_config_names(source['id'], token=token) if source['configs'] == 'all' else source['configs']
            for config in configs:
                splits = source.get('splits') or get_dataset_split_names(source['id'], config, token=token)
                for split in splits:
                    ds = load_dataset(source['id'], config, split=split, streaming=True, token=token)
                    field = source.get('audio_field', 'audio')
                    if ds.features is None or field not in ds.features:
                        raise ValueError(f"Missing audio schema: {source['id']}:{config}:{split}:{field}")
                    raw = next(iter(ds.cast_column(field, Audio(decode=False))))[field]
                    blob = raw.get('bytes')
                    with sf.SoundFile(io.BytesIO(blob) if blob is not None else raw['path']) as audio:
                        sample = audio.read(min(audio.frames, audio.samplerate), dtype='float32')
                        if not len(sample) or not np.isfinite(sample).all():
                            raise ValueError('Invalid audio in preflight')
                    print({'preflight': source['id'], 'config': config, 'split': split, 'audio': 'ok'}, flush=True)
        return
    output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
    fingerprint = hashlib.sha256(json.dumps(dict(spec=spec, seed=args.seed,
        per_config=args.per_config, max_gb=args.max_gb), sort_keys=True).encode()).hexdigest()
    cache_marker = output / 'prepared.json'
    if cache_marker.exists():
        cached = json.loads(cache_marker.read_text())
        if cached['fingerprint'] != fingerprint:
            raise ValueError('Saved data configuration differs; refuse to rebuild underneath a checkpoint')
        manifest = output / 'manifest.jsonl'
        if hashlib.sha256(manifest.read_bytes()).hexdigest() != cached['manifest_sha256']:
            raise ValueError('Saved manifest checksum mismatch')
        saved = [json.loads(line) for line in manifest.read_text().splitlines() if line.strip()]
        validate_manifest(saved)
        missing = next((r['path'] for r in saved if not Path(r['path']).is_file()), None)
        if missing:
            raise FileNotFoundError(f'Saved audio missing: {missing}')
        print('Verified prepared dataset reused; skipping download, indexing and hashing', flush=True)
        return
    audio_dir = output / "audio"; audio_dir.mkdir(exist_ok=True)
    rows, status = [], []
    bytes_used = sum(p.stat().st_size for p in audio_dir.iterdir() if p.is_file())
    max_bytes = int(args.max_gb * 1024**3)
    # Persist original rows so preparation can resume without downloading completed sources.
    journal = output / "rows.jsonl"
    completed_path = output / "completed.json"
    completed = set(json.loads(completed_path.read_text())) if completed_path.exists() else set()
    if journal.exists():
        rows = [json.loads(l) for l in journal.read_text().splitlines() if l.strip()]
    def identity(row):
        return (row["path"], row["source"], row.get("language"), row["label"], row["recording"])
    existing = {identity(r) for r in rows}
    def append(row):
        if identity(row) not in existing:
            rows.append(row); existing.add(identity(row))
            with journal.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")

    for source in spec["kaggle"]:
        slug = source["id"].split("/")[-1]
        root = Path(args.kaggle_root)
        candidates = [p for p in [root / slug, *root.glob(f"datasets/*/{slug}"), *root.glob(f"*/{slug}")] if p.is_dir()]
        if not candidates:
            status.append({"source": source["id"], "status": "missing_mount"}); continue
        count, unknown, short = 0, 0, 0
        for path in sorted(candidates[0].rglob("*")):
            if path.suffix.lower() not in EXTS: continue
            parts = path.relative_to(candidates[0]).parts
            if source.get("include_top_folders") and parts[0] not in source["include_top_folders"]: continue
            label = folder_label(path, candidates[0], source.get("label"), source.get("folder_labels"))
            if label is None:
                unknown += 1; continue
            try:
                info = sf.info(path)
                if info.duration < 1.:
                    short += 1; continue
            except (RuntimeError, OSError):
                # The full decoder validation handles formats requiring fallback.
                pass
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            speakers = []
            for folder, separator in source.get("speaker_filename_folders", {}).items():
                if folder in parts:
                    speakers = [path.name.split(separator)[0]]
            generator = next((p for p in parts[:-1] if source.get("folder_labels", {}).get(p) == 1), "unknown")
            append(dict(path=str(path.resolve()), label=label, source=source["id"],
                        recording=recording_key(path.name), speakers=speakers, language="unknown",
                        generator=generator, sha256=digest, holdout=source.get("holdout", False),
                        group_source='librispeech' if speakers and source['id'].startswith('adarshsingh0903/') else source['id']))
            count += 1
        status.append({"source": source["id"], "indexed": count, "unlabeled_excluded": unknown,
                       "short_audio_excluded": short})
        print(status[-1], flush=True)

    for source in spec["hf"]:
        try:
            token = os.getenv("HF_TOKEN")
            configs = get_dataset_config_names(source["id"], token=token) if source["configs"] == "all" else source["configs"]
            # Reserve equal storage for each HF source and distribute it across
            # language configurations; one large real corpus cannot consume all space.
            source_budget = max_bytes // len(spec["hf"])
            config_budget = source_budget // max(1, len(configs))
            for config in configs:
                config_used = sum(Path(r["path"]).stat().st_size for r in rows
                                  if r["source"] == source["id"] and r.get("language") == config)
                splits = source.get('splits') or get_dataset_split_names(source["id"], config, token=token)
                for original_split in splits:
                    key = f"{source['id']}:{config}:{original_split}"
                    if key in completed: continue
                    if bytes_used >= max_bytes:
                        status.append({"source": key, "status": "storage_budget_reached"}); continue
                    ds = load_dataset(source["id"], config, split=original_split, streaming=True, token=token)
                    audio_field = source.get("audio_field", "audio")
                    if ds.features is None:
                        raise ValueError(f"Dataset {key} has no declared features; cannot safely configure audio decoding")
                    if audio_field not in ds.features:
                        raise ValueError(f"Dataset {key} is missing configured audio field {audio_field!r}")
                    ds = ds.cast_column(audio_field, Audio(decode=False)).shuffle(seed=args.seed, buffer_size=64)
                    count = 0
                    for item in ds:
                        if count >= args.per_config or bytes_used >= max_bytes or config_used >= config_budget: break
                        raw = item[audio_field]
                        audio_path = raw.get("path") or str(item.get("id", ""))
                        blob = raw.get("bytes")
                        if blob is None and not (audio_path and os.path.isfile(audio_path)):
                            raise ValueError("Audio row has neither embedded bytes nor a local file")
                        wave, sr = sf.read(io.BytesIO(blob) if blob is not None else audio_path, dtype="float32", always_2d=True)
                        if not np.isfinite(wave).all() or len(wave) / sr < 1.: continue
                        # Keep complete recordings for random train crops and multi-window evaluation.
                        if len(wave) / sr > 60: wave = wave[:sr * 60]
                        buf = io.BytesIO(); sf.write(buf, wave, sr, format="WAV", subtype="PCM_16")
                        content = buf.getvalue(); digest = hashlib.sha256(content).hexdigest()
                        if bytes_used + len(content) > max_bytes: break
                        dest = audio_dir / f"{digest}.wav"
                        if not dest.exists(): dest.write_bytes(content); bytes_used += len(content)
                        config_used += len(content)
                        label = source.get("label", item.get(source.get("label_field", "label")))
                        if label not in (0, 1): raise ValueError(f"Unrecognized label: {label}")
                        speakers = [speaker_key(item[f]) for f in source.get("speaker_fields", [])
                                    if item.get(f) is not None and str(item[f]).lower() not in ("nan", "none", "")]
                        append(dict(path=str(dest.resolve()), label=int(label), source=source["id"],
                                    recording=recording_key(str(item.get(source.get('recording_field', ''), audio_path or digest))), speakers=speakers,
                                    group_source=source.get('group_source', source['id']),
                                    provenance=source.get('provenance', 'unspecified'),
                                    language=config, generator=str(item.get(source.get("generator_field", "generator"), "unknown")),
                                    sha256=digest, original_split=original_split))
                        count += 1
                    completed.add(key)
                    completed_path.write_text(json.dumps(sorted(completed)))
                    status.append({"source": key, "materialized": count}); print(status[-1], flush=True)
        except Exception as exc:
            # Never silently replace inaccessible datasets with unrelated data.
            detail = traceback.format_exc()
            # Diagnostics must not expose the credential if a dependency includes it.
            if os.getenv("HF_TOKEN"):
                detail = detail.replace(os.environ["HF_TOKEN"], "[REDACTED]")
            status.append({"source": source["id"], "status": "failed", "error_type": type(exc).__name__,
                           "traceback": detail})
            print(status[-1], flush=True)
    if spec.get('extra_sources'):
        from backend.training.extra_audio_sources import prepare_extras
        status.extend(prepare_extras(output, append, completed, args.per_config))
        completed_path.write_text(json.dumps(sorted(completed)))
    clean, report = finalize(rows, args.seed, spec["heldout_generators"])
    report["sources"] = status
    report["bytes_materialized"] = bytes_used
    report["per_config_limit"] = args.per_config
    (output / "manifest.jsonl").write_text("".join(json.dumps(r) + "\n" for r in clean), encoding="utf-8")
    (output / "data_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    validate_manifest(clean)
    if args.require_all:
        requested = {s["id"] for s in spec["hf"] + spec["kaggle"]}
        if spec.get('extra_sources'):
            requested.add('openslr/12')
        available = {r["source"] for r in clean}
        missing = requested - available
        if missing: raise RuntimeError(f"Requested datasets missing: {sorted(missing)}; inspect data_report.json")
    cache_marker.write_text(json.dumps(dict(fingerprint=fingerprint,
        manifest_sha256=hashlib.sha256((output / 'manifest.jsonl').read_bytes()).hexdigest())))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sources", default="backend/training/audio_sources.json")
    p.add_argument("--output", default="audio_data")
    p.add_argument("--kaggle-root", default="/kaggle/input")
    p.add_argument("--per-config", type=int, default=2500)
    p.add_argument("--max-gb", type=float, default=15)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--require-all", action="store_true")
    p.add_argument("--preflight-only", action="store_true")
    prepare(p.parse_args())
