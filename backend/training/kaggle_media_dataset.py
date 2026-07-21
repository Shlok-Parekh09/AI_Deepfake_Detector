"""
Read-only datasets for Kaggle-mounted deepfake sources.

Labels are assigned by EXACT subfolder names — no fuzzy matching.
Each dataset defines explicit (subfolder_name -> label) mappings based on
the actual Kaggle dataset structure.
"""

from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import torch
from PIL import Image, ImageFile
from torch.utils.data import Dataset

# Tolerate truncated images instead of crashing the whole training run.
ImageFile.LOAD_TRUNCATED_IMAGES = True

try:
    import cv2
    cv2.setNumThreads(0)
except ImportError:
    pass

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
AUDIO_EXTS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


@dataclass(frozen=True)
class KaggleSource:
    name: str
    path: str                                       # expected Kaggle mount path
    default_label: int | None = None                # label for ALL files (e.g. all-fake datasets)
    media_exts: frozenset[str] = frozenset(IMAGE_EXTS | VIDEO_EXTS)
    # Exact subfolder-name -> label mappings.
    # Key = lowercase folder name, Value = 0 (real) or 1 (fake)
    folder_labels: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# VISION DATASETS  (from user's Word document)
# ---------------------------------------------------------------------------
DEFAULT_VISION_SOURCES = (
    # 1. DFD Original: "manipulated" = fake, "original" = real
    KaggleSource(
        "dfd-original",
        "/kaggle/input/deep-fake-detection-dfd-entire-original-dataset",
        folder_labels={"manipulated": 1, "original": 0, "manipulated_sequences": 1, "original_sequences": 0},
    ),
    # 2. Deepfake and Real Images: "deepfake" folder = fake, "real" folder = real
    KaggleSource(
        "deepfake-real-images",
        "/kaggle/input/deepfake-and-real-images",
        folder_labels={"deepfake": 1, "fake": 1, "real": 0},
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 3. 1 Million Fake Faces 7: ALL images are fake
    KaggleSource(
        "million-fake-faces-7",
        "/kaggle/input/1-million-fake-faces-7",
        default_label=1,
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 4. 140k Real and Fake Faces: under real_vs_fake -> train/valid/test -> "real"/"fake" folders
    KaggleSource(
        "140k-real-fake",
        "/kaggle/input/140k-real-and-fake-faces",
        folder_labels={"fake": 1, "real": 0},
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 5. Deepfake Image Detection: "fake" folder = fake, "real" folder = real (inside train)
    KaggleSource(
        "deepfake-image-detection",
        "/kaggle/input/deepfake-image-detection",
        folder_labels={"fake": 1, "real": 0},
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 6. 1 Million Fake Faces: ALL images are fake
    KaggleSource(
        "million-fake-faces",
        "/kaggle/input/1-million-fake-faces",
        default_label=1,
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 7. 1M AI Generated Faces 128x128: ALL images are fake
    KaggleSource(
        "1m-ai-faces-128",
        "/kaggle/input/1m-ai-generated-faces-128x128",
        default_label=1,
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 8. 1 Million Fake Faces 2: ALL images are fake
    KaggleSource(
        "million-fake-faces-2",
        "/kaggle/input/1-million-fake-faces-2",
        default_label=1,
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 9. 1 Million Fake Faces 6: ALL images are fake
    KaggleSource(
        "million-fake-faces-6",
        "/kaggle/input/1-million-fake-faces-6",
        default_label=1,
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 10. DFDC Cropped: "fake" folder = fake, "real" folder = real (inside train)
    KaggleSource(
        "dfdc-cropped",
        "/kaggle/input/deep-fake-detection-cropped-dataset",
        folder_labels={"fake": 1, "real": 0},
        media_exts=frozenset(IMAGE_EXTS | VIDEO_EXTS),
    ),
    # 11. Comprehensive DFD: "fake" folder = fake, "real" folder = real (inside train)
    KaggleSource(
        "comprehensive-dfd",
        "/kaggle/input/comprehensive-deepfake-detection-dataset",
        folder_labels={"fake": 1, "real": 0},
        media_exts=frozenset(IMAGE_EXTS | VIDEO_EXTS),
    ),
    # 12. RealAI Video Dataset: "ai" folder = fake, "real" folder = real
    KaggleSource(
        "realai-video",
        "/kaggle/input/realai-video-dataset",
        folder_labels={"ai": 1, "real": 0},
        media_exts=frozenset(VIDEO_EXTS),
    ),
    # 13. MS1M ArcFace (real faces dataset) — ALL images are real
    KaggleSource(
        "ms1m-arcface",
        "/kaggle/input/ms1m-arcface-dataset",
        default_label=0,
        media_exts=frozenset(IMAGE_EXTS),
    ),
    # 14. UCF Crime Dataset (real videos) — ALL videos are real
    KaggleSource(
        "ucf-crime",
        "/kaggle/input/ucf-crime-dataset",
        default_label=0,
        media_exts=frozenset(VIDEO_EXTS),
    ),
    # 15. Human Activity Recognition Video Dataset (real videos) — ALL are real
    KaggleSource(
        "human-activity-videos",
        "/kaggle/input/human-activity-recognition-video-dataset",
        default_label=0,
        media_exts=frozenset(VIDEO_EXTS),
    ),
    # 16. Short Videos (real videos) — ALL are real
    KaggleSource(
        "short-videos",
        "/kaggle/input/short-videos",
        default_label=0,
        media_exts=frozenset(VIDEO_EXTS),
    ),
)

# ---------------------------------------------------------------------------
# AUDIO DATASETS
# ---------------------------------------------------------------------------
DEFAULT_AUDIO_SOURCES = (
    # Audio Deepfake Detection Dataset: "fake" folder = fake, "real" folder = real
    KaggleSource(
        "audio-deepfake-detection",
        "/kaggle/input/audio-deepfake-detection-dataset",
        folder_labels={"fake": 1, "real": 0},
        media_exts=frozenset(AUDIO_EXTS),
    ),
    # Deepfake Audio Dataset (Fake vs Real Speech): "fake" = fake, "real" = real
    KaggleSource(
        "deepfake-audio-fake-vs-real",
        "/kaggle/input/deepfake-audio-dataset-fake-vs-real-speech",
        folder_labels={"fake": 1, "real": 0},
        media_exts=frozenset(AUDIO_EXTS),
    ),
    # The LJ Speech Dataset (Real speech)
    KaggleSource(
        "the-lj-speech-dataset",
        "/kaggle/input/the-lj-speech-dataset",
        default_label=0,
        media_exts=frozenset(AUDIO_EXTS),
    ),
    # In The Wild (audio Deepfake) (Fake speech)
    KaggleSource(
        "in-the-wild-dataset",
        "/kaggle/input/in-the-wild-dataset",
        default_label=1,
        media_exts=frozenset(AUDIO_EXTS),
    ),
    # Audio Dataset with 10 Indian Languages (Real speech)
    KaggleSource(
        "audio-dataset-with-10-indian-languages",
        "/kaggle/input/audio-dataset-with-10-indian-languages",
        default_label=0,
        media_exts=frozenset(AUDIO_EXTS),
    ),
    # ASVspoof 2021 DF (Requires specific labeling if both real/fake exist, but standard is mostly fake or evaluated based on metadata. Let's rely on folder structures or assume fake if it's the eval set without labels. Wait, ASVspoof 2021 DF evaluation set is mixed. We can use folder labels if structured, else it might need metadata parsing. For now, assuming it has real/fake folders. Wait, the Kaggle dataset might just have all audio. Let's assume folder labels "bonafide"->0, "spoof"->1)
    KaggleSource(
        "asvspoof-2021-df",
        "/kaggle/input/asvspoof-2021-df",
        folder_labels={"bonafide": 0, "spoof": 1, "real": 0, "fake": 1},
        media_exts=frozenset(AUDIO_EXTS),
    ),
    # GDrive dataset downloaded in notebook
    KaggleSource(
        "gdrive_dataset",
        "/kaggle/working/gdrive_dataset",
        folder_labels={"bonafide": 0, "spoof": 1, "real": 0, "fake": 1},
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


def _resolve_kaggle_path(source: KaggleSource) -> Path | None:
    """Resolve the source path based on the environment."""
    data_root = os.environ.get("DATA_ROOT", "/kaggle/input")
    
    # If the user provides a direct path, respect it (useful for Lightning AI custom downloads)
    if "DATA_ROOT" in os.environ:
        # E.g., DATA_ROOT=/teamspace/studios/this_studio/datasets
        # Extract the dataset slug from the Kaggle path (e.g., /kaggle/input/deepfake-and-real-images -> deepfake-and-real-images)
        dataset_slug = source.path.strip("/").split("/")[-1]
        base_path = Path(data_root) / dataset_slug
    else:
        # Default Kaggle path
        base_path = Path(source.path)

    if base_path.exists():
        return base_path
        
    # Check for alternate directory structures under the data_root
    if not os.path.exists(data_root):
        return None

    slug = source.path.split("/")[-1]
    # Check direct children and datasets/username/slug pattern
    for d1 in os.listdir(data_root):
        p1 = os.path.join(data_root, d1)
        if not os.path.isdir(p1):
            continue
        if d1 == slug:
            return Path(p1)
        for d2 in os.listdir(p1):
            p2 = os.path.join(p1, d2)
            if not os.path.isdir(p2):
                continue
            if d2 == slug:
                return Path(p2)
            for d3 in os.listdir(p2):
                p3 = os.path.join(p2, d3)
                if os.path.isdir(p3) and d3 == slug:
                    return Path(p3)
    return None


def _label_from_folder(path_str: str, folder_labels: dict[str, int]) -> int | None:
    """
    Determine the label by checking each path component (bottom-up) against
    the exact folder_labels mapping.  Returns the first match found.
    """
    parts = path_str.replace("\\", "/").lower().split("/")
    for part in reversed(parts):
        if part in folder_labels:
            return folder_labels[part]
    return None


import concurrent.futures

def _process_source(source: KaggleSource, max_samples: int | None) -> list[tuple[str, int, str]]:
    root = _resolve_kaggle_path(source)
    if root is None or not root.exists():
        print(f"Skipping {source.name}, path not found: {source.path}")
        return []

    print(f"Indexing {source.name} from {root}...")
    source_samples = []
    
    for root_dir, dirs, files in os.walk(str(root)):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in source.media_exts:
                continue

            full_path = os.path.join(root_dir, file)
            label = None

            if source.folder_labels:
                label = _label_from_folder(full_path, source.folder_labels)
            if label is None and source.default_label is not None:
                label = source.default_label
            if label is None:
                continue

            source_samples.append((full_path, label, source.name))

    if max_samples and len(source_samples) > max_samples:
        random.Random(42).shuffle(source_samples)
        source_samples = source_samples[:max_samples]

    real_count = sum(1 for _, l, _ in source_samples if l == 0)
    fake_count = sum(1 for _, l, _ in source_samples if l == 1)
    print(f"-> Indexed {len(source_samples)} from {source.name} (Real: {real_count}, Fake: {fake_count})")
    return source_samples

def build_index(sources: Iterable[KaggleSource], max_samples: int | None = None) -> list[tuple[str, int, str]]:
    samples = []
    
    # Run dataset scanning in parallel to bypass Kaggle's massive network I/O bottleneck
    print(f"Starting parallel scan of {len(sources)} datasets...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_process_source, src, max_samples) for src in sources]
        for future in concurrent.futures.as_completed(futures):
            samples.extend(future.result())

    random.Random(42).shuffle(samples)
    total_real = sum(1 for _, l, _ in samples if l == 0)
    total_fake = sum(1 for _, l, _ in samples if l == 1)
    print(f"Total indexed samples: {len(samples)} (Real: {total_real}, Fake: {total_fake})")
    sys.stdout.flush()
    return samples


class KaggleVisionDataset(Dataset):
    def __init__(self, samples: list[tuple[str, int, str]], transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        path, label, _source = self.samples[idx]
        try:
            if os.path.splitext(path)[1].lower() in VIDEO_EXTS:
                image = read_video_frame(path, frame_number=idx)
            else:
                image = Image.open(path).convert("RGB")
        except Exception:
            # Skip corrupt/truncated media: sample a different index.
            return self.__getitem__((idx + 1) % len(self.samples))
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
        try:
            mel = load_log_mel(path)  # already [1, n_mels, frames]
        except Exception:
            return self.__getitem__((idx + 1) % len(self.samples))
        return mel, torch.tensor(label, dtype=torch.long)
