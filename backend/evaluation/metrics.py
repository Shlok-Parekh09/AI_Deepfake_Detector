"""
Evaluation Metrics for Deepfake Detection.
Computes accuracy, precision, recall, F1-score, AUC-ROC, etc.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_accuracy(y_true, y_pred) -> float:
    """Compute classification accuracy."""
    return float(accuracy_score(y_true, y_pred))


def compute_precision(y_true, y_pred) -> float:
    """Compute precision (positive = fake)."""
    return float(precision_score(y_true, y_pred, zero_division=0))


def compute_recall(y_true, y_pred) -> float:
    """Compute recall (sensitivity)."""
    return float(recall_score(y_true, y_pred, zero_division=0))


def compute_f1(y_true, y_pred) -> float:
    """Compute F1-score."""
    return float(f1_score(y_true, y_pred, zero_division=0))


def compute_auc_roc(y_true, y_scores) -> float:
    """Compute AUC-ROC score from continuous probability scores."""
    return float(roc_auc_score(y_true, y_scores))


def compute_average_precision(y_true, y_scores) -> float:
    """Compute Average Precision (area under the PR curve)."""
    return float(average_precision_score(y_true, y_scores))


def compute_all_metrics(y_true, y_pred, y_scores=None) -> dict:
    """
    Compute all relevant classification metrics.

    Parameters
    ----------
    y_true : array-like
        Ground-truth labels.
    y_pred : array-like
        Predicted labels (0 or 1).
    y_scores : array-like, optional
        Predicted probabilities for the positive class.

    Returns
    -------
    dict
        Keys: accuracy, precision, recall, f1_score, and optionally
        auc_roc and average_precision.
    """
    metrics = {
        "accuracy": compute_accuracy(y_true, y_pred),
        "precision": compute_precision(y_true, y_pred),
        "recall": compute_recall(y_true, y_pred),
        "f1_score": compute_f1(y_true, y_pred),
    }

    if y_scores is not None:
        try:
            metrics["auc_roc"] = compute_auc_roc(y_true, y_scores)
        except ValueError:
            metrics["auc_roc"] = None
        try:
            metrics["average_precision"] = compute_average_precision(y_true, y_scores)
        except ValueError:
            metrics["average_precision"] = None

    return metrics


def print_classification_report(y_true, y_pred, target_names=None) -> str:
    """
    Generate and print a detailed classification report.

    Returns the report as a string.
    """
    if target_names is None:
        target_names = ["Real", "Fake"]
    report = classification_report(y_true, y_pred, target_names=target_names)
    print(report)
    return report
