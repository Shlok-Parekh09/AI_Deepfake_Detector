"""
Read-only datasets for Kaggle-mounted deepfake sources.

These loaders never download or copy the raw datasets. They scan paths such as
``/kaggle/input/deepfake-and-real-images`` and read samples lazily at training
time.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import torch
from PIL import Image
from torch.utils.data import Dataset

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
AUDIO_EXTS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}

REAL_TOKENS = {"real", "original", "authentic", "bonafide", "bona-fide", "genuine", "human"}
FAKE_TOKENS = {"fake", "deepfake", "deep_fake", "deep-fake", "synthetic", "generated", "manipulated", "spoof", "valle", "openai"}


@dataclass(frozen=True)
class KaggleSource:
    name: str
    path: str
    default_label: int | None = None
    media_exts: frozenset[str] = frozenset(IMAGE_EXTS | VIDEO_EXTS)


DEFAULT_VISION_SOURCES = (
    KaggleSource("dfd-original", "/kaggle/input/deep-fake-detection-dfd-entire-original-dataset"),
    KaggleSource("deepfake-real-images", "/kaggle/input/deepfake-and-real-images"),
    KaggleSource("million-fake-faces-7", "/kaggle/input/1-million-fake-faces-7", default_label=1, media_exts=frozenset(IMAGE_EXTS)),
    KaggleSource("140k-real-fake", "/kaggle/input/140k-real-and-fake-faces"),
    KaggleSource("deepfake-image-detection", "/kaggle/input/deepfake-image-detection"),
    KaggleSource("million-fake-faces", "/kaggle/input/1-million-fake-faces", default_label=1, media_exts=frozenset(IMAGE_EXTS)),
    KaggleSource("1m-ai-faces-128", "/kaggle/input/1m-ai-generated-faces-128x128", default_label=1, media_exts=frozenset(IMAGE_EXTS)),
    KaggleSource("million-fake-faces-2", "/kaggle/input/1-million-fake-faces-2", default_label=1, media_exts=frozenset(IMAGE_EXTS)),
    KaggleSource("million-fake-faces-6", "/kaggle/input/1-million-fake-faces-6", default_label=1, media_exts=frozenset(IMAGE_EXTS)),
    KaggleSource("dfdc-cropped", "/kaggle/input/deep-fake-detection-cropped-dataset"),
    KaggleSource("comprehensive-dfd", "/kaggle/input/comprehensive-deepfake-detection-dataset"),
)

DEFAULT_AUDIO_SOURCES = (
    KaggleSource(
        "audio-deepfake-detection",
        "/kaggle/input/audio-deepfake-detection-dataset",
        default_label=1,
        media_exts=frozenset(AUDIO_EXTS),
    ),
)


def parse_source_arg(raw: str, media_exts: frozenset[str]) -> KaggleSource:
    """
    Parse ``name=path[:label]`` or ``path[:label]``.

    Label can be ``real``/``0`` or ``fake``/``1`` and applies only when a path
    does not contain obvious label tokens.
    """
    name = Path(raw).name
    value = raw
    if "=" in raw:
        name, value = raw.split("=", 1)

    default_label = None
    path = value
    if ":" in value and not Path(value).drive:
        maybe_path, maybe_label = value.rsplit(":", 1)
        if maybe_label.lower() in {"real", "0", "fake", "1"}:
            path = maybe_path
            default_label = 1 if maybe_label.lower() in {"fake", "1"} else 0

    return KaggleSource(name=name, path=path, default_label=default_label, media_exts=media_exts)


def build_index(sources: Iterable[KaggleSource], max_samples: int | None = None) -> list[tuple[str, int, str]]:
    import os
    samples: list[tuple[str, int, str]] = []
    
    for source in sources:
        root = Path(source.path)
        if not root.exists():
            print(f"Skipping {source.name}, path not found: {source.path}")
            continue

        print(f"Indexing {source.name} from {source.path}...")
        source_samples: list[tuple[str, int, str]] = []
        
        # Optimize scanning by using fast os.walk
        for root_dir, dirs, files in os.walk(str(root)):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in source.media_exts:
                    continue
                
                full_path = os.path.join(root_dir, file)
                label = source.default_label
                inferred = infer_label(Path(full_path))
                if inferred is not None:
                    label = inferred
                    
                if label is not None:
                    source_samples.append((full_path, label, source.name))

        if max_samples and len(source_samples) > max_samples:
            random.Random(42).shuffle(source_samples)
            source_samples = source_samples[:max_samples]
            
        print(f"-> Indexed {len(source_samples)} samples from {source.name}")
        samples.extend(source_samples)
        
    random.Random(42).shuffle(samples)
    print(f"Total indexed samples across all datasets: {len(samples)}")
    return samples


def infer_label(path: Path) -> int | None:
    tokens = set()
    for part in path.parts:
        for token in part.lower().replace("-", "_").split("_"):
            if token:
                tokens.add(token)
        tokens.add(part.lower())

    if tokens & FAKE_TOKENS:
        return 1
    if tokens & REAL_TOKENS:
        return 0
    return None


class KaggleVisionDataset(Dataset):
    def __init__(self, samples: list[tuple[str, int, str]], transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        path, label, _source = self.samples[idx]
        if Path(path).suffix.lower() in VIDEO_EXTS:
            image = read_video_frame(path, frame_number=idx)
        else:
            image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, torch.tensor(label, dtype=torch.long)


def read_video_frame(path: str, frame_number: int = 0) -> Image.Image:
    import cv2

    cap = cv2.VideoCapture(path)
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total > 1:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number % total)
        ok, frame = cap.read()
        if not ok:
            raise ValueError(f"Could not read frame from {path}")
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)
    finally:
        cap.release()


class KaggleAudioDataset(Dataset):
    def __init__(self, samples: list[tuple[str, int, str]]):
        self.samples = samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        from backend.preprocessing.audio_features import load_log_mel

        path, label, _source = self.samples[idx]
        return load_log_mel(path).unsqueeze(0), torch.tensor(label, dtype=torch.long)
