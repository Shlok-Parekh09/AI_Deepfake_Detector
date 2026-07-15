"""
Train the audio detector from a Kaggle-mounted audio deepfake dataset.
Supports checkpointing every epoch and resuming from interruptions.

Example on Kaggle:
    python -m backend.training.train_audio_kaggle --epochs 5 --batch-size 64 --amp --resume
"""

from __future__ import annotations

import argparse
import glob
import os
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

from backend.models.audio_model import AudioCNN
from backend.training.kaggle_media_dataset import (
    AUDIO_EXTS,
    DEFAULT_AUDIO_SOURCES,
    KaggleAudioDataset,
    build_index,
    parse_source_arg,
)


def _save_checkpoint(model, optimizer, scaler, epoch, val_loss, args, sources, path):
    """Save a full resumable checkpoint."""
    # Handle scaler which might be None if AMP is not used
    scaler_state = scaler.state_dict() if scaler is not None else None
    torch.save({
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scaler_state_dict": scaler_state,
        "val_loss": val_loss,
        "metadata": {
            "arch": "audio_cnn",
            "sources": [source.name for source in sources],
        },
    }, path)


def _find_latest_checkpoint(output_dir: str) -> str | None:
    """Return the path of the most recently saved epoch checkpoint, or None."""
    pattern = os.path.join(output_dir, "audio_epoch_*.pth")
    checkpoints = sorted(glob.glob(pattern))
    return checkpoints[-1] if checkpoints else None


def _find_step_checkpoint(output_dir: str) -> str | None:
    """Return the path of the most recent mid-epoch step checkpoint, or None."""
    pattern = os.path.join(output_dir, "audio_step_*.pth")
    checkpoints = sorted(glob.glob(pattern))
    return checkpoints[-1] if checkpoints else None


def train(args: argparse.Namespace) -> str:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    sources = list(DEFAULT_AUDIO_SOURCES)
    if args.source:
        sources = [parse_source_arg(raw, frozenset(AUDIO_EXTS)) for raw in args.source]

    samples = build_index(sources, max_samples=args.max_samples_per_source)
    if not samples:
        raise RuntimeError("No labeled audio samples found. Check Kaggle dataset attachments.")

    counts = Counter(label for _path, label, _source in samples)
    print(f"Indexed {len(samples)} audio samples: real={counts.get(0, 0)} fake={counts.get(1, 0)}")

    dataset = KaggleAudioDataset(samples)
    val_size = int(len(dataset) * args.val_fraction)
    train_size = len(dataset) - val_size

    if val_size > 0:
        train_ds, val_ds = random_split(dataset, [train_size, val_size], generator=torch.Generator().manual_seed(42))
        val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.workers, pin_memory=True)
    else:
        train_ds = dataset
        val_loader = None

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=args.workers, pin_memory=True)

    model = AudioCNN().to(device)
    if torch.cuda.device_count() > 1:
        print(f"🚀 Using {torch.cuda.device_count()} GPUs for 2x faster audio training!")
        model = nn.DataParallel(model)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    
    scaler = None
    if args.amp and device.type == "cuda":
        scaler = torch.cuda.amp.GradScaler()

    os.makedirs(args.output_dir, exist_ok=True)
    best_path = os.path.join(args.output_dir, "audio_best.pth")
    step_ckpt = os.path.join(args.output_dir, "audio_step.pth")
    best_val_loss = float("inf")
    start_epoch = 0
    start_step = 0

    # --- Resume from last checkpoint if requested and available ---
    if args.resume:
        step_latest = _find_step_checkpoint(args.output_dir)
        latest = step_latest or _find_latest_checkpoint(args.output_dir)
        if latest:
            print(f"Resuming from checkpoint: {latest}")
            ckpt = torch.load(latest, map_location=device, weights_only=False)
            model.load_state_dict(ckpt["model_state_dict"])
            optimizer.load_state_dict(ckpt["optimizer_state_dict"])
            if scaler is not None and ckpt.get("scaler_state_dict"):
                scaler.load_state_dict(ckpt["scaler_state_dict"])
            start_epoch = ckpt.get("epoch", 0) + 1 if latest != step_latest else ckpt.get("epoch", 0)
            start_step = ckpt.get("step", 0) + 1 if latest == step_latest else 0
            best_val_loss = ckpt.get("val_loss", float("inf"))
            print(f"Resumed at epoch {start_epoch}, step {start_step}, best_val_loss={best_val_loss:.4f}")
        else:
            print("No checkpoint found to resume from - starting fresh.")

    for epoch in range(start_epoch, args.epochs):
        model.train()
        train_loss = run_epoch(
            model, train_loader, criterion, optimizer, scaler, device,
            train=True, epoch=epoch, start_step=start_step,
            step_ckpt=step_ckpt, save_every=args.save_every, args=args, sources=sources,
        )
        start_step = 0  # only the first resumed epoch skips steps

        if val_loader is not None:
            model.eval()
            with torch.no_grad():
                val_loss, val_acc = run_epoch(model, val_loader, criterion, None, scaler, device, train=False)

            print(f"epoch={epoch + 1}/{args.epochs}  train_loss={train_loss:.4f}  val_loss={val_loss:.4f}  val_acc={val_acc:.4f}")
        else:
            val_loss = train_loss
            print(f"epoch={epoch + 1}/{args.epochs}  train_loss={train_loss:.4f}")

        # Clear stale step checkpoint now that the epoch is complete.
        if os.path.exists(step_ckpt):
            os.remove(step_ckpt)

        # Save per-epoch checkpoint
        epoch_path = os.path.join(args.output_dir, f"audio_epoch_{epoch + 1:02d}.pth")
        _save_checkpoint(model, optimizer, scaler, epoch, val_loss, args, sources, epoch_path)
        print(f"  -> saved epoch checkpoint: {epoch_path}")

        if val_loss <= best_val_loss:
            best_val_loss = val_loss
            _save_checkpoint(model, optimizer, scaler, epoch, val_loss, args, sources, best_path)
            print(f"  -> new best: {best_path}  (val_loss={best_val_loss:.4f})")

    return best_path


def run_epoch(model, loader, criterion, optimizer, scaler, device, train: bool,
              epoch: int = 0, start_step: int = 0, step_ckpt: str | None = None,
              save_every: int = 100, args=None, sources=None):
    total_loss = 0.0
    correct = 0
    total = 0
    for step, (inputs, labels) in enumerate(tqdm(loader, leave=False)):
        if step < start_step:
            continue  # skip already-completed batches when resuming mid-epoch

        inputs = inputs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        if scaler is not None:
            with torch.cuda.amp.autocast():
                outputs = model(inputs)
                loss = criterion(outputs, labels)
        else:
            outputs = model(inputs)
            loss = criterion(outputs, labels)

        if train:
            optimizer.zero_grad(set_to_none=True)
            if scaler is not None:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()

            # Mid-epoch checkpoint so a crash/timeout can't wipe out the epoch.
            if step_ckpt and save_every and (step % save_every == 0):
                torch.save({
                    "epoch": epoch,
                    "step": step,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "scaler_state_dict": scaler.state_dict() if scaler is not None else None,
                    "val_loss": float("inf"),
                    "metadata": {
                        "arch": "audio_cnn",
                        "sources": [s.name for s in sources] if sources else [],
                    },
                }, step_ckpt)

        total_loss += loss.item()
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += labels.numel()

    avg_loss = total_loss / max(1, len(loader))
    accuracy = correct / total if total else 0.0
    return (avg_loss, accuracy) if not train else avg_loss


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train audio deepfake detector on Kaggle-mounted data")
    parser.add_argument("--source", action="append", help="Optional source as name=/kaggle/input/path[:fake|real]")
    parser.add_argument("--output-dir", default="/kaggle/working/checkpoints")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--val-fraction", type=float, default=0.05)
    parser.add_argument("--max-samples-per-source", type=int, default=None)
    parser.add_argument("--amp", action="store_true", help="Use Automatic Mixed Precision")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from the latest checkpoint in --output-dir")
    parser.add_argument("--save-every", type=int, default=100,
                        help="Save a mid-epoch checkpoint every N training steps")
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
