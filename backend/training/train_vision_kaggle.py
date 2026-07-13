"""
Train the vision detector from Kaggle-mounted datasets.

Example on Kaggle:
    python -m backend.training.train_vision_kaggle --epochs 3 --batch-size 32
"""

from __future__ import annotations

import argparse
import os
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from tqdm import tqdm

from backend.config import IMAGE_SIZE
from backend.models.cnn_model import CNNDetector
from backend.models.vit_model import ViTDetector
from backend.training.kaggle_media_dataset import (
    DEFAULT_VISION_SOURCES,
    IMAGE_EXTS,
    VIDEO_EXTS,
    KaggleVisionDataset,
    build_index,
    parse_source_arg,
)


def train(args: argparse.Namespace) -> str:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    sources = list(DEFAULT_VISION_SOURCES)
    if args.source:
        sources = [parse_source_arg(raw, frozenset(IMAGE_EXTS | VIDEO_EXTS)) for raw in args.source]

    samples = build_index(sources, max_samples=args.max_samples_per_source)
    if not samples:
        raise RuntimeError("No labeled image/video samples found. Check Kaggle dataset attachments.")

    counts = Counter(label for _path, label, _source in samples)
    print(f"Indexed {len(samples)} vision samples: real={counts.get(0, 0)} fake={counts.get(1, 0)}")

    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    dataset = KaggleVisionDataset(samples, transform=transform)

    val_size = int(len(dataset) * args.val_fraction)
    train_size = len(dataset) - val_size
    
    if val_size > 0:
        train_ds, val_ds = random_split(dataset, [train_size, val_size], generator=torch.Generator().manual_seed(42))
        val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.workers, pin_memory=True)
    else:
        train_ds = dataset
        val_loader = None

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=args.workers, pin_memory=True)

    if args.arch == "vit":
        model = ViTDetector(backbone=args.backbone or "vit_base_patch16_224", pretrained=args.pretrained)
    else:
        model = CNNDetector(backbone=args.backbone or "efficientnet_b0", pretrained=args.pretrained)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scaler = torch.cuda.amp.GradScaler(enabled=args.amp and device.type == "cuda")

    os.makedirs(args.output_dir, exist_ok=True)
    best_val_loss = float("inf")
    best_path = os.path.join(args.output_dir, "vision_best.pth")

    for epoch in range(args.epochs):
        model.train()
        train_loss = run_epoch(model, train_loader, criterion, optimizer, scaler, device, train=True)
        if val_loader is not None:
            model.eval()
            with torch.no_grad():
                val_loss, val_acc = run_epoch(model, val_loader, criterion, None, scaler, device, train=False)

            print(f"epoch={epoch + 1}/{args.epochs} train_loss={train_loss:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")
        else:
            val_loss = train_loss
            print(f"epoch={epoch + 1}/{args.epochs} train_loss={train_loss:.4f}")

        if val_loss <= best_val_loss:
            best_val_loss = val_loss
            torch.save({
                "model_state_dict": model.state_dict(),
                "metadata": {
                    "arch": args.arch,
                    "backbone": args.backbone or ("vit_base_patch16_224" if args.arch == "vit" else "efficientnet_b0"),
                    "image_size": IMAGE_SIZE,
                    "sources": [source.name for source in sources],
                },
            }, best_path)
            print(f"saved {best_path}")

    return best_path


def run_epoch(model, loader, criterion, optimizer, scaler, device, train: bool):
    total_loss = 0.0
    correct = 0
    total = 0
    for inputs, labels in tqdm(loader, leave=False):
        inputs = inputs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        with torch.cuda.amp.autocast(enabled=scaler.is_enabled()):
            outputs = model(inputs)
            loss = criterion(outputs, labels)

        if train:
            optimizer.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

        total_loss += loss.item()
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += labels.numel()

    avg_loss = total_loss / max(1, len(loader))
    accuracy = correct / total if total else 0.0
    return (avg_loss, accuracy) if not train else avg_loss


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train vision deepfake detector on Kaggle-mounted data")
    parser.add_argument("--source", action="append", help="Optional source as name=/kaggle/input/path[:fake|real]")
    parser.add_argument("--output-dir", default="/kaggle/working/checkpoints")
    parser.add_argument("--arch", choices=["cnn", "vit"], default="cnn")
    parser.add_argument("--backbone", default="efficientnet_b0")
    parser.add_argument("--pretrained", action="store_true")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--val-fraction", type=float, default=0.0)
    parser.add_argument("--max-samples-per-source", type=int, default=None)
    parser.add_argument("--amp", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
