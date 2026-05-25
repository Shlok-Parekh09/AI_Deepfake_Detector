"""
Data Splitting Script.
Creates stratified train / validation / test splits from the processed dataset.
"""

import argparse
import os

import pandas as pd
from sklearn.model_selection import train_test_split

from backend.config import PROCESSED_DATA_DIR, SPLITS_DIR

_IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def create_splits(
    data_dir: str = PROCESSED_DATA_DIR,
    output_dir: str = SPLITS_DIR,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> None:
    """
    Scan *data_dir* for images organised as ``real/`` and ``fake/``
    sub-folders, then produce stratified CSV splits.

    Outputs
    -------
    ``train.csv``, ``val.csv``, ``test.csv`` in *output_dir*,
    each with columns ``filepath,label``.
    """
    file_paths: list[str] = []
    labels: list[int] = []

    for label_name, label_val in [("real", 0), ("fake", 1)]:
        folder = os.path.join(data_dir, label_name)
        if not os.path.isdir(folder):
            print(f"Warning: directory not found: {folder}")
            continue
        for fname in sorted(os.listdir(folder)):
            if os.path.splitext(fname)[1].lower() in _IMG_EXTS:
                file_paths.append(os.path.join(folder, fname))
                labels.append(label_val)

    if not file_paths:
        print("No images found – aborting.")
        return

    # First split: train vs (val + test)
    X_train, X_rest, y_train, y_rest = train_test_split(
        file_paths, labels,
        test_size=(val_ratio + test_ratio),
        stratify=labels,
        random_state=seed,
    )

    # Second split: val vs test
    relative_test = test_ratio / (val_ratio + test_ratio)
    X_val, X_test, y_val, y_test = train_test_split(
        X_rest, y_rest,
        test_size=relative_test,
        stratify=y_rest,
        random_state=seed,
    )

    os.makedirs(output_dir, exist_ok=True)

    for name, X, y in [("train", X_train, y_train), ("val", X_val, y_val), ("test", X_test, y_test)]:
        df = pd.DataFrame({"filepath": X, "label": y})
        csv_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(csv_path, index=False)
        real_count = y.count(0) if isinstance(y, list) else (df["label"] == 0).sum()
        fake_count = y.count(1) if isinstance(y, list) else (df["label"] == 1).sum()
        print(f"{name:>5}: {len(df):>6} samples  (real={real_count}  fake={fake_count})  → {csv_path}")


def verify_splits(splits_dir: str = SPLITS_DIR) -> bool:
    """
    Verify that the splits have no overlap and correct ratios.
    """
    sets: dict[str, set] = {}
    for name in ("train", "val", "test"):
        csv_path = os.path.join(splits_dir, f"{name}.csv")
        if not os.path.isfile(csv_path):
            print(f"Missing split: {csv_path}")
            return False
        df = pd.read_csv(csv_path)
        sets[name] = set(df["filepath"])
        print(f"{name}: {len(df)} samples")

    for a, b in [("train", "val"), ("train", "test"), ("val", "test")]:
        overlap = sets[a] & sets[b]
        if overlap:
            print(f"ERROR: {len(overlap)} overlapping samples between {a} and {b}")
            return False

    print("All splits verified — no overlaps.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split dataset into train/val/test")
    parser.add_argument("--data", type=str, default=PROCESSED_DATA_DIR)
    parser.add_argument("--output", type=str, default=SPLITS_DIR)
    parser.add_argument("--train_ratio", type=float, default=0.70)
    parser.add_argument("--val_ratio", type=float, default=0.15)
    parser.add_argument("--test_ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        verify_splits(args.output)
    else:
        create_splits(args.data, args.output, args.train_ratio, args.val_ratio, args.test_ratio, args.seed)
