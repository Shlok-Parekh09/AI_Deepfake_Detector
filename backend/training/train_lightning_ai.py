"""
Lightning AI Studio — Sequential Deepfake Training Pipeline.

Designed specifically for Lightning AI Studio's free tier:
    - 15 monthly credits (~80 GPU hours on T4/L4)
    - 50 GB persistent storage (checkpoints survive between sessions)
    - Runs inside the Studio's persistent environment
    - You can close your browser / shut off your PC and training continues

PIPELINE (per dataset):
    1. Download ONE Kaggle dataset via the Kaggle API
    2. Index it (find all labeled files)
    3. Train on it (continuing from the accumulated checkpoint)
    4. Save the updated checkpoint (carries ALL prior learning forward)
    5. DELETE the dataset files to free disk space (50GB limit)
    6. Move to the next dataset

The model weights CARRY FORWARD from dataset to dataset. By the end,
the final checkpoint has learned from ALL datasets sequentially.

HUGGING FACE HUB PUSH:
    After all datasets are trained, the final checkpoint is pushed to
    the Hugging Face Hub so it's permanently saved and downloadable.

USAGE on Lightning AI Studio:
    # In the Studio terminal:
    python -m backend.training.train_lightning_ai \\
        --data-root /teamspace/studios/this_studio/data \\
        --output-dir /teamspace/studios/this_studio/checkpoints \\
        --hf-repo your-username/deepfake-detector \\
        --epochs-per-dataset 1 --amp --resume

Then close your browser. Training keeps running.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm

from backend.config import IMAGE_SIZE
from backend.models.cnn_model import CNNDetector
from backend.models.vit_model import ViTDetector
from backend.models.audio_model import AudioCNN
from backend.training.kaggle_media_dataset import (
    IMAGE_EXTS,
    VIDEO_EXTS,
    AUDIO_EXTS,
    KaggleVisionDataset,
    KaggleAudioDataset,
    _label_from_folder,
)
from backend.utils.amp_utils import autocast_context, get_amp_scaler, move_to_device


# ---------------------------------------------------------------------------
# Dataset definitions — all Kaggle datasets used by the project
# ---------------------------------------------------------------------------

DATASET_PIPELINE = [
    # === VISION (ordered: smaller datasets first to build up quickly) ===
    {
        "slug": "deepfake-and-real-images",
        "name": "deepfake-real-images",
        "folder_labels": {"deepfake": 1, "fake": 1, "real": 0},
        "default_label": None,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "140k-real-and-fake-faces",
        "name": "140k-real-fake",
        "folder_labels": {"fake": 1, "real": 0},
        "default_label": None,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "deepfake-image-detection",
        "name": "deepfake-image-detection",
        "folder_labels": {"fake": 1, "real": 0},
        "default_label": None,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "deep-fake-detection-cropped-dataset",
        "name": "dfdc-cropped",
        "folder_labels": {"fake": 1, "real": 0},
        "default_label": None,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"}),
    },
    {
        "slug": "comprehensive-deepfake-detection-dataset",
        "name": "comprehensive-dfd",
        "folder_labels": {"fake": 1, "real": 0},
        "default_label": None,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"}),
    },
    {
        "slug": "1-million-fake-faces-7",
        "name": "million-fake-faces-7",
        "folder_labels": {},
        "default_label": 1,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "1-million-fake-faces",
        "name": "million-fake-faces",
        "folder_labels": {},
        "default_label": 1,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "1m-ai-generated-faces-128x128",
        "name": "1m-ai-faces-128",
        "folder_labels": {},
        "default_label": 1,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "1-million-fake-faces-2",
        "name": "million-fake-faces-2",
        "folder_labels": {},
        "default_label": 1,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "1-million-fake-faces-6",
        "name": "million-fake-faces-6",
        "folder_labels": {},
        "default_label": 1,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "ms1m-arcface-dataset",
        "name": "ms1m-arcface",
        "folder_labels": {},
        "default_label": 0,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"}),
    },
    {
        "slug": "deep-fake-detection-dfd-entire-original-dataset",
        "name": "dfd-original",
        "folder_labels": {"manipulated": 1, "original": 0,
                          "manipulated_sequences": 1, "original_sequences": 0},
        "default_label": None,
        "media_type": "vision",
        "exts": frozenset({".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"}),
    },
    # === AUDIO ===
    {
        "slug": "deepfake-audio-dataset-fake-vs-real-speech",
        "name": "deepfake-audio-fake-vs-real",
        "folder_labels": {"fake": 1, "real": 0},
        "default_label": None,
        "media_type": "audio",
        "exts": frozenset({".wav", ".mp3", ".flac", ".ogg", ".m4a"}),
    },
    {
        "slug": "audio-deepfake-detection-dataset",
        "name": "audio-deepfake-detection",
        "folder_labels": {"fake": 1, "real": 0},
        "default_label": None,
        "media_type": "audio",
        "exts": frozenset({".wav", ".mp3", ".flac", ".ogg", ".m4a"}),
    },
]


# ---------------------------------------------------------------------------
# Kaggle dataset download + cleanup
# ---------------------------------------------------------------------------

def download_kaggle_dataset(slug: str, target_dir: str, max_retries: int = 3) -> bool:
    """Download a single Kaggle dataset via the Kaggle CLI."""
    if os.path.isdir(target_dir) and os.listdir(target_dir):
        print(f"    [SKIP] Already exists: {target_dir}")
        return True

    os.makedirs(os.path.dirname(target_dir), exist_ok=True)

    for attempt in range(1, max_retries + 1):
        print(f"    [Download] {slug} (attempt {attempt}/{max_retries})...")
        cmd = ["kaggle", "datasets", "download", "-d", slug,
               "-p", target_dir, "--unzip"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"    [OK] Downloaded to {target_dir}")
            return True
        stderr_short = result.stderr.strip()[:300] if result.stderr else "no error message"
        print(f"    [FAIL] {stderr_short}")
        if attempt < max_retries:
            print(f"    Retrying in 10s...")
            time.sleep(10)

    print(f"    [GIVE UP] {slug} failed after {max_retries} attempts")
    return False


def delete_dataset(target_dir: str):
    """Delete a downloaded dataset directory to free disk space."""
    if os.path.isdir(target_dir):
        size_gb = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, _, fns in os.walk(target_dir) for f in fns
        ) / (1024 ** 3)
        shutil.rmtree(target_dir, ignore_errors=True)
        print(f"    [CLEANUP] Deleted {target_dir} (~{size_gb:.1f} GB freed)")


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def index_dataset(dataset_dir: str, ds_config: dict,
                  max_samples: int | None = None) -> list[tuple[str, int, str]]:
    """Walk a directory and build (path, label, source) tuples."""
    media_exts = ds_config["exts"]
    folder_labels = ds_config.get("folder_labels", {})
    default_label = ds_config.get("default_label")
    source_name = ds_config["name"]

    samples = []
    for root_dir, _dirs, files in os.walk(dataset_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in media_exts:
                continue
            full_path = os.path.join(root_dir, file)
            label = None
            if folder_labels:
                label = _label_from_folder(full_path, folder_labels)
            if label is None and default_label is not None:
                label = default_label
            if label is None:
                continue
            samples.append((full_path, label, source_name))

    if max_samples and len(samples) > max_samples:
        import random
        random.Random(42).shuffle(samples)
        samples = samples[:max_samples]

    return samples


# ---------------------------------------------------------------------------
# Checkpointing
# ---------------------------------------------------------------------------

def save_checkpoint(model, optimizer, scaler, dataset_idx, datasets_done,
                    total_samples, args, path):
    """Save the accumulated sequential checkpoint."""
    # Handle DataParallel — save the underlying module's state
    model_to_save = model.module if isinstance(model, nn.DataParallel) else model

    state = {
        "dataset_idx": dataset_idx,
        "datasets_done": list(datasets_done),
        "total_samples": total_samples,
        "model_state_dict": model_to_save.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scaler_state_dict": scaler.state_dict() if scaler is not None else None,
        "metadata": {
            "arch": args.arch,
            "backbone": args.backbone or (
                "vit_base_patch16_224" if args.arch == "vit" else "efficientnet_b4"),
            "image_size": IMAGE_SIZE,
            "mode": "lightning_ai_sequential",
            "datasets_trained": list(datasets_done),
            "total_samples": total_samples,
        },
    }
    torch.save(state, path)


def load_checkpoint(model, optimizer, scaler, path, device):
    """Load a sequential checkpoint. Returns (dataset_idx, datasets_done, total_samples)."""
    print(f"  [Resume] Loading checkpoint: {path}")
    ckpt = torch.load(path, map_location=device, weights_only=False)

    # Handle DataParallel
    model_to_load = model.module if isinstance(model, nn.DataParallel) else model
    model_to_load.load_state_dict(ckpt["model_state_dict"])
    optimizer.load_state_dict(ckpt["optimizer_state_dict"])
    if scaler is not None and ckpt.get("scaler_state_dict"):
        scaler.load_state_dict(ckpt["scaler_state_dict"])

    datasets_done = set(ckpt.get("datasets_done", []))
    dataset_idx = ckpt.get("dataset_idx", -1) + 1  # start at NEXT dataset
    total_samples = ckpt.get("total_samples", 0)
    print(f"  [Resume] Already trained on {len(datasets_done)} datasets, "
          f"starting at index {dataset_idx}, total_samples={total_samples}")
    return dataset_idx, datasets_done, total_samples


# ---------------------------------------------------------------------------
# Training on a single dataset
# ---------------------------------------------------------------------------

def train_on_dataset(model, samples, criterion, optimizer, scaler, device,
                     args, ds_config, dataset_idx, datasets_done, total_samples,
                     checkpoint_path) -> int:
    """
    Train on one dataset's samples.
    Returns the number of samples trained on.
    The checkpoint is saved after training, carrying ALL prior learning forward.
    """
    if not samples:
        print(f"  [SKIP] No samples in {ds_config['name']}")
        return 0

    is_audio = ds_config["media_type"] == "audio"
    counts = Counter(label for _p, label, _s in samples)
    ds_size = len(samples)

    print(f"\n{'='*70}")
    print(f"  DATASET {dataset_idx + 1}: {ds_config['name']}")
    print(f"  Type: {'AUDIO' if is_audio else 'VISION'}  |  Slug: {ds_config['slug']}")
    print(f"  Samples: {ds_size}  (Real: {counts.get(0,0)}, Fake: {counts.get(1,0)})")
    print(f"  Cumulative samples trained: {total_samples}")
    print(f"  Datasets completed so far: {len(datasets_done)}")
    print(f"{'='*70}")

    # Build dataset + loader
    if is_audio:
        dataset = KaggleAudioDataset(samples)
    else:
        transform = transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        dataset = KaggleVisionDataset(samples, transform=transform)

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.workers,
        pin_memory=(device.type in ("cuda", "xpu")),
        drop_last=False,
        persistent_workers=(args.workers > 0),
    )

    # Train for N epochs on this dataset
    for epoch in range(args.epochs_per_dataset):
        model.train()
        epoch_loss = 0.0
        correct = 0
        total = 0

        pbar = tqdm(
            loader,
            desc=f"  {ds_config['name']} E{epoch+1}/{args.epochs_per_dataset}",
            leave=True,
        )

        for step, (inputs, labels) in enumerate(pbar):
            inputs = move_to_device(inputs, device)
            labels = move_to_device(labels, device)

            # Forward + loss with device-appropriate autocast
            with autocast_context(device, enabled=args.amp):
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            # Backward
            optimizer.zero_grad(set_to_none=True)
            if scaler is not None:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()

            epoch_loss += loss.item()
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.numel()

            # Mid-dataset step checkpoint (crash-proof)
            if args.save_every and step > 0 and step % args.save_every == 0:
                save_checkpoint(
                    model, optimizer, scaler, dataset_idx, datasets_done,
                    total_samples + total, args, checkpoint_path,
                )

            if step % 20 == 0:
                pbar.set_postfix(
                    loss=f"{loss.item():.4f}",
                    acc=f"{correct/max(1,total):.4f}",
                )

        avg_loss = epoch_loss / max(1, len(loader))
        acc = correct / max(1, total)
        print(f"  -> {ds_config['name']} epoch {epoch+1}: "
              f"loss={avg_loss:.4f}  acc={acc:.4f}")

    # Save checkpoint — carries ALL learning forward
    new_total = total_samples + ds_size
    datasets_done.add(ds_config["name"])
    save_checkpoint(
        model, optimizer, scaler, dataset_idx, datasets_done,
        new_total, args, checkpoint_path,
    )
    print(f"  -> Checkpoint saved: {checkpoint_path}")
    print(f"  -> Cumulative samples: {new_total}  |  Datasets done: {len(datasets_done)}")

    # Clear cache between datasets
    if device.type == "cuda":
        torch.cuda.empty_cache()
    elif device.type == "xpu" and hasattr(torch, "xpu"):
        torch.xpu.empty_cache()

    return ds_size


# ---------------------------------------------------------------------------
# Hugging Face Hub push
# ---------------------------------------------------------------------------

def push_to_huggingface(checkpoint_path: str, repo_id: str, token: str | None = None):
    """Push the final checkpoint to the Hugging Face Hub."""
    print(f"\n{'='*70}")
    print(f"  PUSHING TO HUGGING FACE HUB")
    print(f"{'='*70}")
    print(f"  Repo: {repo_id}")
    print(f"  File: {checkpoint_path}")

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("  Installing huggingface_hub...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "huggingface_hub"], check=True)
        from huggingface_hub import HfApi, create_repo

    token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if not token:
        print("  ERROR: No Hugging Face token found!")
        print("  Set it:  export HF_TOKEN=hf_your_token_here")
        print("  Get one: https://huggingface.co/settings/tokens")
        return False

    api = HfApi(token=token)

    # Create repo if needed
    try:
        create_repo(repo_id, token=token, exist_ok=True, repo_type="model")
        print(f"  [OK] Repo ready: {repo_id}")
    except Exception as e:
        print(f"  [WARN] Repo creation: {e}")

    # Upload checkpoint
    checkpoint_name = os.path.basename(checkpoint_path)
    try:
        api.upload_file(
            path_or_fileobj=checkpoint_path,
            path_in_repo=checkpoint_name,
            repo_id=repo_id,
            token=token,
        )
        print(f"  [OK] Uploaded {checkpoint_name}")
    except Exception as e:
        print(f"  [ERROR] Upload failed: {e}")
        return False

    # Upload metadata
    meta_path = os.path.join(os.path.dirname(checkpoint_path), "training_info.json")
    try:
        ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        meta = ckpt.get("metadata", {})
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        api.upload_file(
            path_or_fileobj=meta_path,
            path_in_repo="training_info.json",
            repo_id=repo_id,
            token=token,
        )
        print(f"  [OK] Uploaded training_info.json")
    except Exception as e:
        print(f"  [WARN] Metadata upload: {e}")

    print(f"\n  Download your model anytime from:")
    print(f"  https://huggingface.co/{repo_id}")
    return True


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(args: argparse.Namespace):
    print(f"\n{'='*70}")
    print(f"  LIGHTNING AI STUDIO — SEQUENTIAL DEEPFAKE TRAINING")
    print(f"{'='*70}")

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
        print(f"  GPU: {gpu_name}  ({gpu_mem:.1f} GB)")
        if torch.cuda.device_count() > 1:
            print(f"  Multi-GPU: {torch.cuda.device_count()} GPUs")
    else:
        print(f"  WARNING: No GPU detected — training will be very slow on CPU")
        print(f"  Switch to a GPU instance in Lightning AI Studio settings")

    print(f"  Data root: {args.data_root}")
    print(f"  Checkpoint dir: {args.output_dir}")
    print(f"  HF repo: {args.hf_repo or '(not set — checkpoint saved locally only)'}")
    print(f"  Epochs per dataset: {args.epochs_per_dataset}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  AMP: {'on' if args.amp else 'off'}")
    print(f"{'='*70}\n")

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.data_root, exist_ok=True)

    # Determine pipeline based on modality
    if args.modality == "vision":
        pipeline = [d for d in DATASET_PIPELINE if d["media_type"] == "vision"]
    elif args.modality == "audio":
        pipeline = [d for d in DATASET_PIPELINE if d["media_type"] == "audio"]
    else:
        pipeline = DATASET_PIPELINE

    print(f"  Datasets to process ({len(pipeline)}):")
    for i, ds in enumerate(pipeline):
        print(f"    {i+1}. [{ds['media_type'].upper():5s}] {ds['name']:30s}  ({ds['slug']})")
    print()

    # Determine modality for model construction
    is_audio_pipeline = pipeline[0]["media_type"] == "audio" if pipeline else False

    # Build model
    if is_audio_pipeline:
        model = AudioCNN()
        checkpoint_name = "audio_best.pth"
    elif args.arch == "vit":
        model = ViTDetector(backbone=args.backbone or "vit_base_patch16_224",
                            pretrained=args.pretrained)
        checkpoint_name = "vision_best.pth"
    else:
        model = CNNDetector(backbone=args.backbone or "efficientnet_b4",
                            pretrained=args.pretrained)
        checkpoint_name = "vision_best.pth"

    model.to(device)

    # Multi-GPU
    if device.type == "cuda" and torch.cuda.device_count() > 1:
        print(f"  Using {torch.cuda.device_count()} GPUs via DataParallel")
        model = nn.DataParallel(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr,
                                  weight_decay=args.weight_decay)
    scaler = get_amp_scaler(device) if args.amp else None

    # Checkpoint paths
    seq_ckpt = os.path.join(args.output_dir, "seq_checkpoint.pth")
    best_ckpt = os.path.join(args.output_dir, checkpoint_name)

    # Resume
    start_idx = 0
    datasets_done: set[str] = set()
    total_samples = 0

    if args.resume and os.path.exists(seq_ckpt):
        start_idx, datasets_done, total_samples = load_checkpoint(
            model, optimizer, scaler, seq_ckpt, device,
        )

    remaining = pipeline[start_idx:] if start_idx < len(pipeline) else []

    if not remaining:
        print("\n  All datasets already trained!")
        if args.hf_repo:
            push_to_huggingface(best_ckpt if os.path.exists(best_ckpt) else seq_ckpt,
                                args.hf_repo, args.hf_token)
        return

    print(f"\n  Starting at dataset index {start_idx}, {len(remaining)} remaining\n")

    # === SEQUENTIAL PIPELINE ===
    for i, ds_config in enumerate(remaining):
        dataset_idx = start_idx + i
        ds_dir = os.path.join(args.data_root, ds_config["slug"])

        # 1. Download
        print(f"\n  [Step 1] Downloading: {ds_config['slug']}")
        ok = download_kaggle_dataset(ds_config["slug"], ds_dir)
        if not ok:
            print(f"  [SKIP] Could not download {ds_config['slug']} — moving on")
            continue

        # 2. Index
        print(f"  [Step 2] Indexing {ds_config['name']}...")
        samples = index_dataset(ds_dir, ds_config, args.max_samples_per_source)
        print(f"  [Step 2] Found {len(samples)} labeled samples")

        # 3. Train
        print(f"  [Step 3] Training on {ds_config['name']}...")
        trained_count = train_on_dataset(
            model, samples, criterion, optimizer, scaler, device,
            args, ds_config, dataset_idx, datasets_done, total_samples,
            seq_ckpt,
        )
        total_samples += trained_count

        # Copy to best checkpoint (sequential: latest = best)
        shutil.copy2(seq_ckpt, best_ckpt)

        # 4. Delete dataset to free disk space
        print(f"  [Step 4] Freeing disk space...")
        delete_dataset(ds_dir)

        # Progress summary
        print(f"\n  --- PROGRESS ---")
        print(f"  Datasets completed: {len(datasets_done)}/{len(pipeline)}")
        print(f"  Total samples trained: {total_samples}")
        print(f"  Checkpoint: {seq_ckpt}")
        print(f"  ----------------")

        # Disk space check
        try:
            stat = os.statvfs(args.data_root)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
            if free_gb < 5:
                print(f"  [WARN] Low disk space: {free_gb:.1f} GB free")
            else:
                print(f"  [Disk] {free_gb:.1f} GB free")
        except Exception:
            pass

    # === FINAL: Push to Hugging Face Hub ===
    print(f"\n{'='*70}")
    print(f"  ALL DATASETS PROCESSED")
    print(f"  Total samples trained: {total_samples}")
    print(f"  Datasets completed: {len(datasets_done)}")
    print(f"  Final checkpoint: {best_ckpt}")
    print(f"{'='*70}")

    if args.hf_repo:
        push_to_huggingface(best_ckpt, args.hf_repo, args.hf_token)
    else:
        print(f"\n  No --hf-repo specified. Final checkpoint at:")
        print(f"  {best_ckpt}")
        print(f"\n  To push to HF later:")
        print(f"    export HF_TOKEN=hf_your_token")
        print(f"    python -m backend.training.train_lightning_ai --resume --hf-repo your-repo/id")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lightning AI Studio — Sequential Deepfake Training Pipeline"
    )
    parser.add_argument("--data-root", default="/teamspace/studios/this_studio/data",
                        help="Where to download datasets (cleaned up after each)")
    parser.add_argument("--output-dir", default="/teamspace/studios/this_studio/checkpoints",
                        help="Where to save checkpoints (persistent storage)")
    parser.add_argument("--modality", choices=["vision", "audio", "both"], default="both")
    parser.add_argument("--arch", choices=["cnn", "vit"], default="cnn")
    parser.add_argument("--backbone", default="efficientnet_b4")
    parser.add_argument("--pretrained", action="store_true")
    parser.add_argument("--epochs-per-dataset", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--max-samples-per-source", type=int, default=None)
    parser.add_argument("--amp", action="store_true", help="Use mixed precision")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from seq_checkpoint.pth (skip completed datasets)")
    parser.add_argument("--save-every", type=int, default=500,
                        help="Save mid-dataset step checkpoint every N steps")
    parser.add_argument("--hf-repo", default=None,
                        help="HF repo to push final checkpoint (e.g. username/deepfake-detector)")
    parser.add_argument("--hf-token", default=None,
                        help="HF token (or set HF_TOKEN env var)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.modality == "both":
        print("\n" + "#" * 70)
        print("#  PHASE 1: VISION TRAINING")
        print("#" * 70)
        args.modality = "vision"
        run_pipeline(args)

        print("\n" + "#" * 70)
        print("#  PHASE 2: AUDIO TRAINING")
        print("#" * 70)
        args.modality = "audio"
        run_pipeline(args)

        print("\n" + "#" * 70)
        print("#  ALL TRAINING COMPLETE")
        print("#" * 70)
    else:
        run_pipeline(args)