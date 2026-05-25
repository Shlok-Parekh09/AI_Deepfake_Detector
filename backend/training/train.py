"""
Main Training Loop for the Deepfake Detector.
Handles the full training pipeline: data loading, forward/backward pass,
validation, checkpointing, and logging.
"""

import argparse
import time

import torch
from torch.cuda.amp import GradScaler, autocast
from tqdm import tqdm

from backend.config import (
    BATCH_SIZE, CHECKPOINTS_DIR, LEARNING_RATE, LOGS_DIR,
    MIXED_PRECISION, NUM_EPOCHS, WEIGHT_DECAY,
)
from backend.models.cnn_model import CNNDetector
from backend.training.callbacks import EarlyStopping, ModelCheckpoint, TensorBoardLogger
from backend.training.dataloader import get_train_loader, get_val_loader
from backend.training.loss_functions import get_loss_function
from backend.training.optimizer import get_optimizer, get_scheduler
from backend.utils.gpu_utils import get_device, set_seed
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def train_model(
    model: torch.nn.Module,
    train_loader,
    val_loader,
    num_epochs: int = NUM_EPOCHS,
    learning_rate: float = LEARNING_RATE,
    device: torch.device | None = None,
) -> dict:
    """
    Full training loop with AMP, gradient clipping, validation,
    checkpointing, and early stopping.

    Returns the metrics of the best epoch.
    """
    device = device or get_device()
    model = model.to(device)

    criterion = get_loss_function("focal")
    optimizer = get_optimizer(model, learning_rate=learning_rate, weight_decay=WEIGHT_DECAY)
    scheduler = get_scheduler(optimizer, "cosine", num_epochs)

    early_stopping = EarlyStopping(patience=10)
    checkpoint = ModelCheckpoint(CHECKPOINTS_DIR)
    tb_logger = TensorBoardLogger(LOGS_DIR)

    scaler = GradScaler(enabled=MIXED_PRECISION)
    best_metrics: dict = {}

    for epoch in range(num_epochs):
        t0 = time.time()

        # ── Train ──
        train_metrics = train_one_epoch(
            model, train_loader, optimizer, criterion, device, scaler,
        )

        # ── Validate ──
        val_metrics = validate(model, val_loader, criterion, device)

        # ── Scheduler step ──
        if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
            scheduler.step(val_metrics["loss"])
        else:
            scheduler.step()

        elapsed = time.time() - t0
        lr_now = optimizer.param_groups[0]["lr"]

        logger.info(
            "Epoch %d/%d  [%.1fs]  train_loss=%.4f  val_loss=%.4f  "
            "val_acc=%.4f  lr=%.2e",
            epoch + 1, num_epochs, elapsed,
            train_metrics["loss"], val_metrics["loss"],
            val_metrics["accuracy"], lr_now,
        )

        # ── TensorBoard ──
        tb_logger.log_metrics(train_metrics, epoch, prefix="train")
        tb_logger.log_metrics(val_metrics, epoch, prefix="val")
        tb_logger.log_scalar("learning_rate", lr_now, epoch)

        # ── Checkpoint ──
        all_metrics = {"val_loss": val_metrics["loss"], **val_metrics}
        checkpoint.save(model, optimizer, epoch, all_metrics)
        if val_metrics["loss"] == checkpoint.best_metric:
            best_metrics = all_metrics

        # ── Early stopping ──
        if early_stopping(val_metrics["loss"]):
            logger.info("Early stopping at epoch %d", epoch + 1)
            break

    tb_logger.close()
    return best_metrics


def train_one_epoch(model, train_loader, optimizer, criterion, device, scaler) -> dict:
    """Train for a single epoch. Returns loss and accuracy."""
    model.train()
    running_loss = 0.0
    correct = total = 0

    for images, labels in tqdm(train_loader, desc="Training", leave=False):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        with autocast(enabled=MIXED_PRECISION):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()

        running_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    return {
        "loss": running_loss / total if total else 0.0,
        "accuracy": correct / total if total else 0.0,
    }


@torch.no_grad()
def validate(model, val_loader, criterion, device) -> dict:
    """Run validation. Returns loss and accuracy."""
    model.eval()
    running_loss = 0.0
    correct = total = 0

    for images, labels in tqdm(val_loader, desc="Validating", leave=False):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        with autocast(enabled=MIXED_PRECISION):
            outputs = model(images)
            loss = criterion(outputs, labels)

        running_loss += loss.item() * images.size(0)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    return {
        "loss": running_loss / total if total else 0.0,
        "accuracy": correct / total if total else 0.0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the Deepfake Detector")
    parser.add_argument("--data", type=str, required=True, help="Path to data directory")
    parser.add_argument("--epochs", type=int, default=NUM_EPOCHS)
    parser.add_argument("--lr", type=float, default=LEARNING_RATE)
    parser.add_argument("--batch_size", type=int, default=BATCH_SIZE)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    device = get_device()
    logger.info("Device: %s", device)

    model = CNNDetector()
    train_loader = get_train_loader(args.data, batch_size=args.batch_size)
    val_loader = get_val_loader(args.data, batch_size=args.batch_size)

    best = train_model(model, train_loader, val_loader, args.epochs, args.lr, device)
    logger.info("Training complete. Best metrics: %s", best)
