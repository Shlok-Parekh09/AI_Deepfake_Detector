"""
Custom PyTorch Datasets for Deepfake Detection.
Loads images / frame sequences with labels (real=0, fake=1).
"""

import os

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset

from backend.config import IMAGE_SIZE, SEQUENCE_LENGTH
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Common image extensions
_IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class DeepfakeDataset(Dataset):
    """
    Image-level deepfake dataset.

    Supports two layouts:

    1. **CSV** – a CSV file (``filepath,label``) located at
       ``<data_path>/<split>.csv``.
    2. **Directory** – sub-folders ``<data_path>/real/`` and
       ``<data_path>/fake/``.
    """

    def __init__(
        self,
        data_path: str,
        transform=None,
        split: str = "train",
    ):
        self.transform = transform
        self.file_paths: list[str] = []
        self.labels: list[int] = []

        csv_path = os.path.join(data_path, f"{split}.csv")
        if os.path.isfile(csv_path):
            self._load_from_csv(csv_path)
        else:
            split_dir = os.path.join(data_path, split)
            self._load_from_directory(split_dir)

        logger.info(
            "DeepfakeDataset [%s]: %d samples  (real=%d  fake=%d)",
            split,
            len(self),
            self.labels.count(0),
            self.labels.count(1),
        )

    def _load_from_csv(self, csv_path: str) -> None:
        df = pd.read_csv(csv_path)
        self.file_paths = df["filepath"].tolist()
        self.labels = df["label"].astype(int).tolist()

    def _load_from_directory(self, data_path: str) -> None:
        for label_name, label_val in [("real", 0), ("fake", 1)]:
            folder = os.path.join(data_path, label_name)
            if not os.path.isdir(folder):
                continue
            for fname in sorted(os.listdir(folder)):
                if os.path.splitext(fname)[1].lower() in _IMG_EXTS:
                    self.file_paths.append(os.path.join(folder, fname))
                    self.labels.append(label_val)

    def __len__(self) -> int:
        return len(self.file_paths)

    def __getitem__(self, idx: int):
        image = Image.open(self.file_paths[idx]).convert("RGB")
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label


class VideoDataset(Dataset):
    """
    Video-level dataset that returns a *sequence* of frames for RNN
    temporal analysis.

    Expected CSV: ``video_dir,label``  where ``video_dir`` contains
    pre-extracted frame images.
    """

    def __init__(
        self,
        data_path: str,
        sequence_length: int = SEQUENCE_LENGTH,
        transform=None,
        split: str = "train",
    ):
        self.sequence_length = sequence_length
        self.transform = transform
        self.video_dirs: list[str] = []
        self.labels: list[int] = []

        csv_path = os.path.join(data_path, f"{split}_videos.csv")
        if os.path.isfile(csv_path):
            df = pd.read_csv(csv_path)
            self.video_dirs = df["video_dir"].tolist()
            self.labels = df["label"].astype(int).tolist()
        else:
            # Fall back to directory layout: data_path/real/<video_id>/frames
            for label_name, label_val in [("real", 0), ("fake", 1)]:
                folder = os.path.join(data_path, label_name)
                if not os.path.isdir(folder):
                    continue
                for vid in sorted(os.listdir(folder)):
                    vid_path = os.path.join(folder, vid)
                    if os.path.isdir(vid_path):
                        self.video_dirs.append(vid_path)
                        self.labels.append(label_val)

        logger.info(
            "VideoDataset [%s]: %d videos  (seq_len=%d)",
            split, len(self), sequence_length,
        )

    def __len__(self) -> int:
        return len(self.video_dirs)

    def __getitem__(self, idx: int):
        vid_dir = self.video_dirs[idx]
        label = self.labels[idx]

        # Gather sorted frame images
        frame_files = sorted(
            f for f in os.listdir(vid_dir)
            if os.path.splitext(f)[1].lower() in _IMG_EXTS
        )

        # Sample or pad to fixed sequence_length
        if len(frame_files) >= self.sequence_length:
            indices = np.linspace(
                0, len(frame_files) - 1, self.sequence_length, dtype=int,
            )
            frame_files = [frame_files[i] for i in indices]
            actual_length = self.sequence_length
        else:
            actual_length = len(frame_files)
            # Pad by repeating last frame
            while len(frame_files) < self.sequence_length:
                frame_files.append(frame_files[-1] if frame_files else "")

        frames = []
        for fname in frame_files:
            path = os.path.join(vid_dir, fname)
            if os.path.isfile(path):
                img = Image.open(path).convert("RGB")
                if self.transform:
                    img = self.transform(img)
                frames.append(img)
            else:
                # Zero tensor as padding
                frames.append(torch.zeros(3, *IMAGE_SIZE))

        sequence = torch.stack(frames)  # [T, C, H, W]
        return sequence, label, actual_length
