"""
Model Evaluation Pipeline.
Runs the trained model on the test set and reports metrics.
"""

import argparse
import json
import os

import numpy as np
import torch
from torch.cuda.amp import autocast
from tqdm import tqdm

from backend.config import CHECKPOINTS_DIR, MIXED_PRECISION
from backend.evaluation.confusion_matrix import (
    plot_confusion_matrix,
    plot_precision_recall_curve,
    plot_roc_curve,
)
from backend.evaluation.metrics import compute_all_metrics, print_classification_report
from backend.models.cnn_model import CNNDetector
from backend.training.dataloader import get_test_loader
from backend.utils.gpu_utils import get_device
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@torch.no_grad()
def evaluate_model(
    model: torch.nn.Module,
    test_loader,
    device: str | torch.device = "cuda",
    save_dir: str | None = None,
) -> dict:
    """
    Evaluate a trained model on the test set.

    Returns a dict with all computed metrics.
    """
    device = torch.device(device)
    model = model.to(device)
    model.eval()

    all_labels: list[int] = []
    all_preds: list[int] = []
    all_scores: list[float] = []

    for images, labels in tqdm(test_loader, desc="Evaluating"):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        with autocast(enabled=MIXED_PRECISION):
            outputs = model(images)

        probs = torch.softmax(outputs, dim=1)
        preds = probs.argmax(dim=1)

        all_labels.extend(labels.cpu().numpy().tolist())
        all_preds.extend(preds.cpu().numpy().tolist())
        all_scores.extend(probs[:, 1].cpu().numpy().tolist())  # P(fake)

    metrics = compute_all_metrics(all_labels, all_preds, all_scores)
    report = print_classification_report(all_labels, all_preds)

    # ── Visualisations ──
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        plot_confusion_matrix(
            all_labels, all_preds,
            save_path=os.path.join(save_dir, "confusion_matrix.png"),
        )
        plot_roc_curve(
            all_labels, all_scores,
            save_path=os.path.join(save_dir, "roc_curve.png"),
        )
        plot_precision_recall_curve(
            all_labels, all_scores,
            save_path=os.path.join(save_dir, "pr_curve.png"),
        )
        # Save metrics JSON
        with open(os.path.join(save_dir, "metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info("Evaluation results saved to %s", save_dir)

    logger.info("Evaluation metrics: %s", metrics)
    return metrics


def evaluate_from_checkpoint(
    checkpoint_path: str,
    test_data_path: str,
    save_dir: str | None = None,
) -> dict:
    """
    Load a checkpoint, build a test DataLoader, and run evaluation.
    """
    device = get_device()
    model = CNNDetector()
    model.load_weights(checkpoint_path)
    test_loader = get_test_loader(test_data_path)
    return evaluate_model(model, test_loader, device, save_dir=save_dir)


def cross_dataset_evaluation(
    model: torch.nn.Module,
    dataset_paths: dict[str, str],
    device: str | torch.device = "cuda",
) -> dict[str, dict]:
    """
    Evaluate model generalisation across multiple datasets.

    Parameters
    ----------
    dataset_paths : dict
        ``{"dataset_name": "path/to/data", ...}``

    Returns
    -------
    dict
        ``{"dataset_name": metrics_dict, ...}``
    """
    results = {}
    for name, path in dataset_paths.items():
        logger.info("Evaluating on dataset: %s", name)
        loader = get_test_loader(path)
        results[name] = evaluate_model(model, loader, device)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the Deepfake Detector")
    parser.add_argument(
        "--checkpoint", type=str,
        default=os.path.join(CHECKPOINTS_DIR, "best.pth"),
        help="Path to model checkpoint",
    )
    parser.add_argument("--test_data", type=str, required=True, help="Path to test data")
    parser.add_argument("--save_dir", type=str, default=None, help="Directory to save results")
    args = parser.parse_args()

    evaluate_from_checkpoint(args.checkpoint, args.test_data, args.save_dir)
