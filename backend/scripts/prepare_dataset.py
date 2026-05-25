"""
Dataset Preparation Script.
Downloads and organises deepfake detection datasets.
"""

import argparse
import os
import shutil

from backend.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

_IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def download_faceforensics(output_dir: str = RAW_DATA_DIR) -> None:
    """
    Download FaceForensics++ dataset.

    Requires manual access request:
    https://github.com/ondyari/FaceForensics

    Contains: Original, Deepfakes, Face2Face, FaceSwap, NeuralTextures.
    """
    print(
        "FaceForensics++ requires a manual access request.\n"
        "1. Visit https://github.com/ondyari/FaceForensics\n"
        "2. Follow the instructions to request download access.\n"
        "3. Use the provided download script to save data to:\n"
        f"   {output_dir}/faceforensics\n"
    )


def download_celeb_df(output_dir: str = RAW_DATA_DIR) -> None:
    """
    Download Celeb-DF (v2) dataset.

    Repository: https://github.com/yuezunli/celeb-deepfakeforensics
    """
    print(
        "Celeb-DF v2 requires manual download.\n"
        "1. Visit https://github.com/yuezunli/celeb-deepfakeforensics\n"
        "2. Follow the Google Drive links to download.\n"
        f"3. Extract to: {output_dir}/celeb_df\n"
    )


def download_dfdc(output_dir: str = RAW_DATA_DIR) -> None:
    """
    Download DFDC (DeepFake Detection Challenge) dataset.

    Requires Kaggle account and the Kaggle CLI.
    """
    print(
        "DFDC requires a Kaggle account.\n"
        "1. Install kaggle CLI: pip install kaggle\n"
        "2. Configure API credentials (~/.kaggle/kaggle.json).\n"
        "3. Run:\n"
        "   kaggle competitions download -c deepfake-detection-challenge\n"
        f"4. Extract to: {output_dir}/dfdc\n"
    )


def organize_dataset(
    raw_dir: str = RAW_DATA_DIR,
    processed_dir: str = PROCESSED_DATA_DIR,
) -> None:
    """
    Copy images from *raw_dir* into a standard structure::

        processed/
        ├── real/
        │   ├── img_000001.jpg
        │   └── …
        └── fake/
            ├── img_000001.jpg
            └── …

    The function looks for sub-directories named ``real`` and ``fake``
    anywhere under *raw_dir* and flattens them.
    """
    for label in ("real", "fake"):
        dest = os.path.join(processed_dir, label)
        os.makedirs(dest, exist_ok=True)

        counter = 0
        for root, _, files in os.walk(raw_dir):
            # Only gather from folders whose name matches the label
            if os.path.basename(root).lower() != label:
                continue
            for fname in sorted(files):
                if os.path.splitext(fname)[1].lower() in _IMG_EXTS:
                    counter += 1
                    ext = os.path.splitext(fname)[1]
                    new_name = f"img_{counter:06d}{ext}"
                    shutil.copy2(
                        os.path.join(root, fname),
                        os.path.join(dest, new_name),
                    )

        print(f"[{label}] Copied {counter} images → {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare deepfake datasets")
    parser.add_argument(
        "--dataset",
        choices=["faceforensics", "celeb_df", "dfdc", "organize"],
        required=True,
    )
    parser.add_argument("--raw", type=str, default=RAW_DATA_DIR)
    parser.add_argument("--output", type=str, default=PROCESSED_DATA_DIR)
    args = parser.parse_args()

    if args.dataset == "faceforensics":
        download_faceforensics(args.raw)
    elif args.dataset == "celeb_df":
        download_celeb_df(args.raw)
    elif args.dataset == "dfdc":
        download_dfdc(args.raw)
    elif args.dataset == "organize":
        organize_dataset(args.raw, args.output)
