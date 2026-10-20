"""Dependency-free leakage controls for audio manifests. Real=0, synthetic=1."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def recording_key(value: str) -> str:
    """Keep segments of a parent recording together (not speaker identity)."""
    name = Path(value).stem
    return re.sub(r"(?:_c|_p2)?_part_\d+$|_\d{5}$", "", name)


def partition(key: str, seed: int = 42) -> str:
    n = int(hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()[:8], 16) / 2**32
    return "test" if n < .1 else "calibration" if n < .2 else "validation" if n < .3 else "train"


def assign_split(row: dict, seed: int = 42, heldout_generators=()) -> str:
    if row.get("holdout"):
        return "external_test"
    # All source AND target identities must belong to the same partition.
    # Cross-partition voice conversions are excluded, not assigned arbitrarily.
    speakers = row.get("speakers", [])
    groups = speakers or [row["recording"]]
    kind = "speaker" if speakers else "recording"
    # Conservatively keep an ID together across language configurations too.
    namespace = row.get('group_source', row['source'])
    parts = {partition(f"{namespace}:{kind}:{g}", seed) for g in groups}
    if len(parts) != 1:
        return "excluded"
    split = parts.pop()
    if row.get("generator", "").lower() in heldout_generators:
        return "unseen_generator_test" if split == "test" else "excluded"
    return split


def finalize(rows: list[dict], seed=42, heldout_generators=()) -> tuple[list[dict], dict]:
    # Duplicate bytes across sources are removed globally before partitioning.
    by_hash = defaultdict(list)
    for row in rows:
        by_hash[row["sha256"]].append(row)
    clean, conflicts = [], 0
    for copies in by_hash.values():
        if len({r["label"] for r in copies}) != 1:
            conflicts += len(copies)
            continue
        # A copy in the external benchmark must never leak into training.
        row = dict(next((r for r in copies if r.get("holdout")), copies[0]))
        row["split"] = assign_split(row, seed, heldout_generators)
        clean.append(row)
    report = {
        "indexed": len(rows), "unique": len(clean), "conflicting_labels_excluded": conflicts,
        "duplicates_removed": len(rows) - conflicts - len(clean),
        "counts": dict(Counter(f"{r['split']}:{r['source']}:{r['label']}" for r in clean)),
        "speaker_metadata_rows": sum(bool(r.get("speakers")) for r in clean),
        "limitation": "Sources without verified speaker IDs use recording groups; unseen-speaker performance cannot be claimed for those sources. Byte hashes do not detect transcoded duplicates."
    }
    return clean, report


def validate_manifest(rows: list[dict], required_splits=None) -> None:
    seen, groups = {}, {}
    for r in rows:
        if r["split"] == "excluded":
            continue
        if r["label"] not in (0, 1):
            raise ValueError("Labels must be real=0 or fake=1")
        if r["sha256"] in seen:
            raise ValueError("Duplicate audio hash in manifest")
        seen[r["sha256"]] = r["split"]
        # External sources are distinct by construction; generator test shares
        # the test speaker bucket but never shares train/validation identities.
        bucket = "test" if r["split"] == "unseen_generator_test" else r["split"]
        identities = [("recording", r["recording"])] + [("speaker", g) for g in r.get("speakers", [])]
        for kind, g in identities:
            key = (r.get('group_source', r['source']), kind, g)
            if key in groups and groups[key] != bucket:
                raise ValueError(f"Group leakage: {key}")
            groups[key] = bucket
    for split in required_splits or ("train", "validation", "calibration", "test", "external_test"):
        labels = {r["label"] for r in rows if r["split"] == split}
        if labels != {0, 1}:
            raise ValueError(f"{split} must contain both classes; got {labels}")


def read_manifest(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
