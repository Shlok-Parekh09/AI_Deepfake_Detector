"""
Train the audio detector from a Kaggle-mounted audio deepfake dataset.

Example on Kaggle:
    python -m backend.training.train_audio_kaggle --epochs 5 --batch-size 64
"""

from __future__ import annotations

import argparse
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


def train(args: argparse.Namespace) -> str:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    os.makedirs(args.output_dir, exist_ok=True)
    best_val_loss = float("inf")
    best_path = os.path.join(args.output_dir, "audio_best.pth")

    for epoch in range(args.epochs):
        model.train()
        train_loss = run_epoch(model, train_loader, criterion, optimizer, device, train=True)
        if val_loader is not None:
            model.eval()
            with torch.no_grad():
                val_loss, val_acc = run_epoch(model, val_loader, criterion, None, device, train=False)

            print(f"epoch={epoch + 1}/{args.epochs} train_loss={train_loss:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")
        else:
            val_loss = train_loss
            print(f"epoch={epoch + 1}/{args.epochs} train_loss={train_loss:.4f}")

        if val_loss <= best_val_loss:
            best_val_loss = val_loss
            torch.save({
                "model_state_dict": model.state_dict(),
                "metadata": {
                    "arch": "audio_cnn",
                    "sources": [source.name for source in sources],
                },
            }, best_path)
            print(f"saved {best_path}")

    return best_path


def run_epoch(model, loader, criterion, optimizer, device, train: bool):
    total_loss = 0.0
    correct = 0
    total = 0
    for inputs, labels in tqdm(loader, leave=False):
        inputs = inputs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        if train:
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()

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
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--val-fraction", type=float, default=0.0)
    parser.add_argument("--max-samples-per-source", type=int, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
