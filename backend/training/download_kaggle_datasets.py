"""
Download all Kaggle datasets used by the deepfake detector.

Works on Google Colab, RunPod, Lambda Cloud, or any machine with the
Kaggle API configured.  Downloads datasets sequentially to /content/data
(or a custom root), then the sequential trainer picks them up from there.

Setup (one-time):
    pip install kaggle
    # Go to https://kaggle.com -> Account -> Create New API Token
    # Upload kaggle.json to Colab or place at ~/.kaggle/kaggle.json

Usage:
    python -m backend.training.download_kaggle_datasets --data-root /content/data
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# All Kaggle dataset slugs used by the project.
# These match the DEFAULT_VISION_SOURCES and DEFAULT_AUDIO_SOURCES in
# kaggle_media_dataset.py — the folder name after download is the slug.
VISION_DATASETS = [
    "deep-fake-detection-dfd-entire-original-dataset",
    "deepfake-and-real-images",
    "1-million-fake-faces-7",
    "140k-real-and-fake-faces",
    "deepfake-image-detection",
    "1-million-fake-faces",
    "1m-ai-generated-faces-128x128",
    "1-million-fake-faces-2",
    "1-million-fake-faces-6",
    "deep-fake-detection-cropped-dataset",
    "comprehensive-deepfake-detection-dataset",
    "realai-video-dataset",
    "ms1m-arcface-dataset",
    "ucf-crime-dataset",
    "human-activity-recognition-video-dataset",
    "short-videos",
]

AUDIO_DATASETS = [
    "adarshsingh0903/audio-deepfake-detection-dataset",
    "jayjoshi37/deepfake-audio-dataset-fake-vs-real-speech",
]


def _slug_to_dirname(slug: str) -> str:
    """Convert a Kaggle slug to a directory name (last path component)."""
    return slug.split("/")[-1]


def download_dataset(slug: str, data_root: str, max_retries: int = 3) -> bool:
    """Download a single Kaggle dataset. Returns True on success."""
    dirname = _slug_to_dirname(slug)
    target = os.path.join(data_root, dirname)

    if os.path.isdir(target) and os.listdir(target):
        print(f"  [SKIP] {slug} already exists at {target}")
        return True

    os.makedirs(data_root, exist_ok=True)

    for attempt in range(1, max_retries + 1):
        print(f"  [Download] {slug} (attempt {attempt}/{max_retries})...")
        cmd = ["kaggle", "datasets", "download", "-d", slug,
               "-p", target, "--unzip"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [OK] {slug} -> {target}")
            return True
        print(f"  [FAIL] {result.stderr.strip()}")
        if attempt < max_retries:
            print(f"  Retrying in 10s...")
            import time
            time.sleep(10)

    print(f"  [GIVE UP] {slug} failed after {max_retries} attempts")
    return False


def download_all(data_root: str, modality: str = "both") -> dict:
    """Download all datasets. Returns a dict {slug: success_bool}."""
    datasets = []
    if modality in ("vision", "both"):
        datasets.extend(VISION_DATASETS)
    if modality in ("audio", "both"):
        datasets.extend(AUDIO_DATASETS)

    print(f"\n{'='*70}")
    print(f"  Downloading {len(datasets)} Kaggle datasets to {data_root}")
    print(f"{'='*70}\n")

    results = {}
    for i, slug in enumerate(datasets):
        print(f"\n[{i+1}/{len(datasets)}] {slug}")
        results[slug] = download_dataset(slug, data_root)

    # Summary
    succeeded = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    print(f"\n{'='*70}")
    print(f"  Download complete: {succeeded} succeeded, {failed} failed")
    if failed:
        print(f"  Failed datasets:")
        for slug, ok in results.items():
            if not ok:
                print(f"    - {slug}")
    print(f"{'='*70}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Download all Kaggle datasets for deepfake training")
    parser.add_argument("--data-root", default="/content/data",
                        help="Where to download datasets (default: /content/data for Colab)")
    parser.add_argument("--modality", choices=["vision", "audio", "both"], default="both")
    args = parser.parse_args()

    # Check kaggle API is configured.
    kaggle_dir = os.path.expanduser("~/.kaggle")
    if not os.path.isfile(os.path.join(kaggle_dir, "kaggle.json")):
        print("ERROR: kaggle.json not found at ~/.kaggle/kaggle.json")
        print("Get it from: https://www.kaggle.com/ -> Account -> Create New API Token")
        print("Then run:  mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json")
        sys.exit(1)

    download_all(args.data_root, args.modality)


if __name__ == "__main__":
    main()