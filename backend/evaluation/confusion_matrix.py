"""
Confusion Matrix Generation and Visualisation.
"""

import os

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for servers
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
    auc,
)

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def generate_confusion_matrix(y_true, y_pred, labels=None) -> np.ndarray:
    """
    Compute and return the confusion matrix as a numpy array.
    """
    return confusion_matrix(y_true, y_pred, labels=labels)


def plot_confusion_matrix(
    y_true,
    y_pred,
    labels=None,
    save_path: str | None = None,
) -> None:
    """
    Plot confusion matrix using seaborn heatmap and optionally save.
    """
    cm = generate_confusion_matrix(y_true, y_pred, labels=labels)
    display_labels = labels or ["Real", "Fake"]

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=display_labels, yticklabels=display_labels,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150)
        logger.info("Confusion matrix saved to %s", save_path)
    else:
        plt.show()
    plt.close(fig)


def plot_roc_curve(
    y_true,
    y_scores,
    save_path: str | None = None,
) -> None:
    """
    Plot ROC curve annotated with AUC score.
    """
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#4C72B0", lw=2, label=f"AUC = {roc_auc:.4f}")
    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Receiver Operating Characteristic (ROC)")
    ax.legend(loc="lower right")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150)
        logger.info("ROC curve saved to %s", save_path)
    else:
        plt.show()
    plt.close(fig)


def plot_precision_recall_curve(
    y_true,
    y_scores,
    save_path: str | None = None,
) -> None:
    """
    Plot Precision–Recall curve.
    """
    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    pr_auc = auc(recall, precision)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(recall, precision, color="#DD8452", lw=2, label=f"AP = {pr_auc:.4f}")
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision–Recall Curve")
    ax.legend(loc="lower left")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150)
        logger.info("PR curve saved to %s", save_path)
    else:
        plt.show()
    plt.close(fig)
