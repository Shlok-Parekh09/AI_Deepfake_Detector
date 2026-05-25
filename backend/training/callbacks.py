"""
Training Callbacks: Early Stopping, Model Checkpointing, Logging.
"""

import os

import torch

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class EarlyStopping:
    """
    Stop training when validation loss stops improving.
    """

    def __init__(self, patience: int = 10, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss: float | None = None
        self.counter: int = 0
        self.should_stop: bool = False

    def __call__(self, val_loss: float) -> bool:
        """
        Returns ``True`` when training should stop.
        """
        if self.best_loss is None or val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
                logger.info(
                    "EarlyStopping triggered after %d epochs without improvement",
                    self.counter,
                )

        return self.should_stop


class ModelCheckpoint:
    """
    Save model checkpoints during training.

    * Best model (based on validation metric).
    * Periodic checkpoints (every *save_every* epochs).
    * Last checkpoint (for resuming training).
    """

    def __init__(
        self,
        checkpoint_dir: str,
        save_best: bool = True,
        save_every: int = 5,
    ):
        self.checkpoint_dir = checkpoint_dir
        self.save_best = save_best
        self.save_every = save_every
        self.best_metric: float | None = None
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save(
        self,
        model,
        optimizer,
        epoch: int,
        metrics: dict,
    ) -> None:
        """
        Save the current state.  Automatically saves ``best.pth``
        when the tracked metric improves, and periodic checkpoints.
        """
        payload = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "metrics": metrics,
        }

        # ── Always save "last" ──
        last_path = os.path.join(self.checkpoint_dir, "last.pth")
        torch.save(payload, last_path)

        # ── Best model ──
        val_loss = metrics.get("val_loss")
        if self.save_best and val_loss is not None:
            if self.best_metric is None or val_loss < self.best_metric:
                self.best_metric = val_loss
                best_path = os.path.join(self.checkpoint_dir, "best.pth")
                torch.save(payload, best_path)
                logger.info("Saved best model (val_loss=%.5f)", val_loss)

        # ── Periodic ──
        if (epoch + 1) % self.save_every == 0:
            periodic_path = os.path.join(
                self.checkpoint_dir, f"checkpoint_epoch_{epoch + 1}.pth",
            )
            torch.save(payload, periodic_path)
            logger.info("Saved periodic checkpoint: %s", periodic_path)

    def load(
        self,
        model,
        optimizer=None,
        checkpoint_path: str | None = None,
    ) -> dict:
        """
        Load a checkpoint and restore model (and optionally optimizer) state.

        Returns the stored metrics dict.
        """
        if checkpoint_path is None:
            checkpoint_path = os.path.join(self.checkpoint_dir, "best.pth")

        ckpt = torch.load(checkpoint_path, map_location="cpu")
        model.load_state_dict(ckpt["model_state_dict"])
        if optimizer and "optimizer_state_dict" in ckpt:
            optimizer.load_state_dict(ckpt["optimizer_state_dict"])

        logger.info(
            "Loaded checkpoint from %s (epoch %d)", checkpoint_path, ckpt.get("epoch", -1),
        )
        return ckpt.get("metrics", {})


class TensorBoardLogger:
    """
    Log training metrics to TensorBoard.
    """

    def __init__(self, log_dir: str):
        from torch.utils.tensorboard import SummaryWriter

        self.writer = SummaryWriter(log_dir)
        logger.info("TensorBoard logging to %s", log_dir)

    def log_scalar(self, tag: str, value: float, step: int) -> None:
        """Log a single scalar value."""
        self.writer.add_scalar(tag, value, step)

    def log_metrics(self, metrics_dict: dict, step: int, prefix: str = "train") -> None:
        """Log multiple scalars under a common *prefix*."""
        for key, value in metrics_dict.items():
            self.writer.add_scalar(f"{prefix}/{key}", value, step)

    def close(self) -> None:
        """Flush and close the writer."""
        self.writer.flush()
        self.writer.close()
