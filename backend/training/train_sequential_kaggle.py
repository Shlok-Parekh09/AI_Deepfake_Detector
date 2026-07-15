"""
Sequential dataset-by-dataset trainer for Kaggle / Colab / RunPod.

Strategy
--------
Instead of indexing ALL datasets at once (which takes forever and crashes
when one corrupt file appears), this trainer processes datasets ONE AT A
TIME in a continuous pipeline:

    1. Index dataset[0]          (foreground)
    2. Start training on dataset[0]
    3. While training, index dataset[1] in a BACKGROUND thread
    4. When dataset[0] finishes, save checkpoint, move to dataset[1]
    5. Repeat for all datasets

The model weights CARRY FORWARD from dataset to dataset (continual learning),
so each dataset builds on what the previous one learned.  A checkpoint is
saved after every single dataset, so a crash or Kaggle timeout never loses
more than the current dataset's progress.

Usage on Kaggle:
    python -m backend.training.train_sequential_kaggle \
        --epochs-per-dataset 1 --batch-size 32 --amp --resume

Usage on Colab / RunPod (after downloading datasets locally):
    python -m backend.training.train_sequential_kaggle \
        --data-root /content/data --epochs-per-dataset 1 --amp --resume
"""

from __future__ import annotations

import argparse
import glob
import os
import threading
import time
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from tqdm import tqdm

from backend.config import IMAGE_SIZE
from backend.models.cnn_model import CNNDetector
from backend.models.vit_model import ViTDetector
from backend.models.audio_model import AudioCNN
from backend.training.kaggle_media_dataset import (
    DEFAULT_VISION_SOURCES,
    DEFAULT_AUDIO_SOURCES,
    IMAGE_EXTS,
    VIDEO_EXTS,
    AUDIO_EXTS,
    KaggleVisionDataset,
    KaggleAudioDataset,
    KaggleSource,
    _process_source,
    parse_source_arg,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dataset_size_gb(samples: list[tuple[str, int, str]]) -> float:
    """Estimate total file size of indexed samples in GB."""
    total_bytes = 0
    for path, _label, _src in samples:
        try:
            total_bytes += os.path.getsize(path)
        except OSError:
            pass
    return total_bytes / (1024 ** 3)


def _save_seq_checkpoint(model, optimizer, scaler, dataset_idx, epoch, step,
                         total_gb, args, path):
    """Save a sequential-training checkpoint."""
    torch.save({
        "dataset_idx": dataset_idx,
        "epoch": epoch,
        "step": step,
        "total_gb": total_gb,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scaler_state_dict": scaler.state_dict() if scaler is not None else None,
        "metadata": {
            "arch": args.arch,
            "backbone": args.backbone or ("vit_base_patch16_224" if args.arch == "vit" else "efficientnet_b4"),
            "image_size": IMAGE_SIZE,
            "mode": "sequential",
        },
    }, path)


def _find_seq_checkpoint(output_dir: str) -> str | None:
    """Return the most recent sequential checkpoint, or None."""
    pattern = os.path.join(output_dir, "seq_checkpoint.pth")
    return pattern if os.path.exists(pattern) else None


def _find_best_checkpoint(output_dir: str, prefix: str) -> str | None:
    pattern = os.path.join(output_dir, f"{prefix}_best.pth")
    return pattern if os.path.exists(pattern) else None


# ---------------------------------------------------------------------------
# Background indexer — indexes the NEXT dataset while training on current
# ---------------------------------------------------------------------------

class BackgroundIndexer:
    """Index a dataset in a background thread so I/O overlaps with training."""

    def __init__(self, source: KaggleSource, max_samples: int | None):
        self.source = source
        self.max_samples = max_samples
        self.result: list[tuple[str, int, str]] | None = None
        self.error: Exception | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            self.result = _process_source(self.source, self.max_samples)
        except Exception as exc:
            self.error = exc

    def wait(self) -> list[tuple[str, int, str]]:
        if self._thread is not None:
            self._thread.join()
        if self.error is not None:
            raise self.error
        return self.result or []


# ---------------------------------------------------------------------------
# Training loop for a single dataset
# ---------------------------------------------------------------------------

def _train_one_dataset(model, samples, criterion, optimizer, scaler, device,
                       args, dataset_name, dataset_idx, total_gb,
                       is_audio: bool) -> float:
    """Train on one dataset's samples. Returns the average loss for this dataset."""

    if not samples:
        print(f"  [{dataset_name}] No samples — skipping.")
        return 0.0

    counts = Counter(label for _p, label, _s in samples)
    print(f"\n{'='*70}")
    print(f"  DATASET {dataset_idx + 1}: {dataset_name}")
    print(f"  Samples: {len(samples)}  (Real: {counts.get(0, 0)}, Fake: {counts.get(1, 0)})")
    print(f"  Cumulative data processed: ~{total_gb:.1f} GB")
    print(f"{'='*70}")

    if is_audio:
        dataset = KaggleAudioDataset(samples)
        transform = None
    else:
        transform = transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        dataset = KaggleVisionDataset(samples, transform=transform)

    # Use the full dataset for training in sequential mode (no val split —
    # the continual-learning checkpoint after each dataset is our safety net).
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.workers,
        pin_memory=True,
        drop_last=False,
    )

    best_path = os.path.join(args.output_dir, "audio_best.pth" if is_audio else "vision_best.pth")
    seq_ckpt = os.path.join(args.output_dir, "seq_checkpoint.pth")

    for epoch in range(args.epochs_per_dataset):
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        pbar = tqdm(loader, desc=f"  {dataset_name} E{epoch+1}/{args.epochs_per_dataset}", leave=True)

        for step, (inputs, labels) in enumerate(pbar):
            inputs = inputs.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            if scaler is not None:
                with torch.cuda.amp.autocast():
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
            else:
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            optimizer.zero_grad(set_to_none=True)
            if scaler is not None:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()

            total_loss += loss.item()
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.numel()

            # Mid-dataset step checkpoint every N steps.
            if args.save_every and (step % args.save_every == 0):
                _save_seq_checkpoint(
                    model, optimizer, scaler, dataset_idx, epoch, step,
                    total_gb, args, seq_ckpt,
                )

            if step % 20 == 0:
                pbar.set_postfix(loss=f"{loss.item():.4f}", acc=f"{correct/max(1,total):.4f}")

        avg_loss = total_loss / max(1, len(loader))
        acc = correct / max(1, total)
        print(f"  -> {dataset_name} epoch {epoch+1}: loss={avg_loss:.4f}  acc={acc:.4f}")

        # Save after each epoch within the dataset.
        _save_seq_checkpoint(
            model, optimizer, scaler, dataset_idx, epoch, len(loader) - 1,
            total_gb, args, seq_ckpt,
        )
        # Always update the best checkpoint (sequential mode: latest = best).
        _save_seq_checkpoint(
            model, optimizer, scaler, dataset_idx, epoch, len(loader) - 1,
            total_gb, args, best_path,
        )

    return avg_loss


# ---------------------------------------------------------------------------
# Main sequential pipeline
# ---------------------------------------------------------------------------

def train_sequential(args: argparse.Namespace) -> str:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Mode: SEQUENTIAL dataset-by-dataset training")
    print(f"Target: >= {args.target_gb} GB of data")
    print(f"Epochs per dataset: {args.epochs_per_dataset}")
    print(f"Batch size: {args.batch_size}")
    print()

    # Determine which sources to use.
    if args.modality == "vision":
        sources = list(DEFAULT_VISION_SOURCES)
        media_exts = frozenset(IMAGE_EXTS | VIDEO_EXTS)
        is_audio = False
    else:
        sources = list(DEFAULT_AUDIO_SOURCES)
        media_exts = frozenset(AUDIO_EXTS)
        is_audio = True

    if args.source:
        sources = [parse_source_arg(raw, media_exts) for raw in args.source]

    print(f"Datasets to process ({len(sources)}):")
    for i, src in enumerate(sources):
        print(f"  {i+1}. {src.name}  ->  {src.path}")
    print()

    os.makedirs(args.output_dir, exist_ok=True)

    # Build or resume the model.
    if is_audio:
        model = AudioCNN()
    elif args.arch == "vit":
        model = ViTDetector(backbone=args.backbone or "vit_base_patch16_224", pretrained=args.pretrained)
    else:
        model = CNNDetector(backbone=args.backbone or "efficientnet_b4", pretrained=args.pretrained)

    model.to(device)
    if torch.cuda.device_count() > 1:
        print(f"Using {torch.cuda.device_count()} GPUs via DataParallel")
        model = nn.DataParallel(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    scaler = None
    if args.amp and device.type == "cuda":
        scaler = torch.cuda.amp.GradScaler()

    best_path = os.path.join(args.output_dir, "audio_best.pth" if is_audio else "vision_best.pth")
    seq_ckpt = os.path.join(args.output_dir, "seq_checkpoint.pth")

    # Resume state.
    start_dataset_idx = 0
    total_gb = 0.0

    if args.resume:
        ckpt_file = _find_seq_checkpoint(args.output_dir)
        if ckpt_file:
            print(f"Resuming from: {ckpt_file}")
            ckpt = torch.load(ckpt_file, map_location=device, weights_only=False)
            model.load_state_dict(ckpt["model_state_dict"])
            optimizer.load_state_dict(ckpt["optimizer_state_dict"])
            if scaler is not None and ckpt.get("scaler_state_dict"):
                scaler.load_state_dict(ckpt["scaler_state_dict"])
            start_dataset_idx = ckpt.get("dataset_idx", 0)
            total_gb = ckpt.get("total_gb", 0.0)
            print(f"Resumed at dataset index {start_dataset_idx}, total_gb={total_gb:.1f}")
        else:
            print("No sequential checkpoint found — starting fresh.")

    # ---- Sequential pipeline with background indexing ----
    sources_to_run = sources[start_dataset_idx:]

    # Pre-index the first dataset (no overlap possible yet).
    if not sources_to_run:
        print("All datasets already processed!")
        return best_path

    print(f"Indexing first dataset: {sources_to_run[0].name}...")
    current_samples = _process_source(sources_to_run[0], args.max_samples_per_source)
    current_gb = _dataset_size_gb(current_samples)
    total_gb += current_gb

    for i, source in enumerate(sources_to_run):
        dataset_idx = start_dataset_idx + i
        is_last = (i == len(sources_to_run) - 1)

        # Start background indexing of the NEXT dataset while we train.
        next_indexer: BackgroundIndexer | None = None
        if not is_last:
            next_source = sources_to_run[i + 1]
            print(f"\n[Background] Pre-indexing next dataset: {next_source.name}...")
            next_indexer = BackgroundIndexer(next_source, args.max_samples_per_source)
            next_indexer.start()

        # Train on the current dataset.
        _train_one_dataset(
            model, current_samples, criterion, optimizer, scaler, device,
            args, source.name, dataset_idx, total_gb, is_audio,
        )

        # Save checkpoint after completing this dataset.
        _save_seq_checkpoint(
            model, optimizer, scaler, dataset_idx, args.epochs_per_dataset - 1, 0,
            total_gb, args, best_path,
        )
        print(f"  -> Saved checkpoint after {source.name} ({best_path})")

        # Check if we've hit the target GB.
        if total_gb >= args.target_gb:
            print(f"\n{'='*70}")
            print(f"  TARGET REACHED: {total_gb:.1f} GB >= {args.target_gb} GB")
            print(f"  Stopping early. Checkpoint saved at {best_path}")
            print(f"{'='*70}")
            break

        # Get the next dataset's samples (wait for background indexing).
        if next_indexer is not None:
            print(f"\n[Waiting] Fetching indexed samples for next dataset...")
            current_samples = next_indexer.wait()
            current_gb = _dataset_size_gb(current_samples)
            total_gb += current_gb
            print(f"[Ready] Next dataset indexed: {len(current_samples)} samples, ~{current_gb:.1f} GB")
        elif not is_last:
            # Fallback if background indexer wasn't started.
            current_samples = _process_source(sources_to_run[i + 1], args.max_samples_per_source)
            current_gb = _dataset_size_gb(current_samples)
            total_gb += current_gb

    # Final checkpoint.
    _save_seq_checkpoint(
        model, optimizer, scaler, len(sources) - 1, 0, 0,
        total_gb, args, best_path,
    )
    print(f"\n{'='*70}")
    print(f"  SEQUENTIAL TRAINING COMPLETE")
    print(f"  Total data processed: ~{total_gb:.1f} GB")
    print(f"  Final checkpoint: {best_path}")
    print(f"{'='*70}")
    return best_path


# ---------------------------------------------------------------------------
# Combined vision + audio runner
# ---------------------------------------------------------------------------

def train_both(args: argparse.Namespace):
    """Run sequential training for vision first, then audio."""
    print("\n" + "=" * 70)
    print("  PHASE 1: VISION TRAINING (sequential)")
    print("=" * 70)
    args.modality = "vision"
    train_sequential(args)

    print("\n" + "=" * 70)
    print("  PHASE 2: AUDIO TRAINING (sequential)")
    print("=" * 70)
    args.modality = "audio"
    train_sequential(args)

    print("\n" + "=" * 70)
    print("  ALL TRAINING COMPLETE")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sequential dataset-by-dataset trainer (crash-proof, continual learning)"
    )
    parser.add_argument("--modality", choices=["vision", "audio", "both"], default="both",
                        help="Which modality to train (default: both)")
    parser.add_argument("--source", action="append",
                        help="Override source: name=/path[:fake|real]")
    parser.add_argument("--output-dir", default="/kaggle/working/checkpoints")
    parser.add_argument("--arch", choices=["cnn", "vit"], default="cnn")
    parser.add_argument("--backbone", default="efficientnet_b4")
    parser.add_argument("--pretrained", action="store_true")
    parser.add_argument("--epochs-per-dataset", type=int, default=1,
                        help="Epochs to train on EACH dataset (default: 1)")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--max-samples-per-source", type=int, default=None,
                        help="Cap samples per dataset (None = all)")
    parser.add_argument("--amp", action="store_true", help="Use mixed precision")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from seq_checkpoint.pth")
    parser.add_argument("--save-every", type=int, default=500,
                        help="Save mid-dataset step checkpoint every N steps")
    parser.add_argument("--target-gb", type=float, default=35.0,
                        help="Stop after processing this much data (default: 35 GB)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.modality == "both":
        train_both(args)
    else:
        train_sequential(args)