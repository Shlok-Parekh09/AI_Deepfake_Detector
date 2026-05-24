"""
Evaluation Metrics for Deepfake Detection.
Computes accuracy, precision, recall, F1-score, AUC-ROC, etc.
"""

# TODO: Import required modules
# from sklearn.metrics import (
#     accuracy_score, precision_score, recall_score, f1_score,
#     roc_auc_score, average_precision_score, classification_report
# )
# import numpy as np


def compute_accuracy(y_true, y_pred):
    """Compute classification accuracy. TODO: Implement"""
    pass


def compute_precision(y_true, y_pred):
    """Compute precision. TODO: Implement"""
    pass


def compute_recall(y_true, y_pred):
    """Compute recall (sensitivity). TODO: Implement"""
    pass


def compute_f1(y_true, y_pred):
    """Compute F1-score. TODO: Implement"""
    pass


def compute_auc_roc(y_true, y_scores):
    """Compute AUC-ROC score. TODO: Implement"""
    pass


def compute_average_precision(y_true, y_scores):
    """Compute Average Precision (AP). TODO: Implement"""
    pass


def compute_all_metrics(y_true, y_pred, y_scores=None):
    """
    Compute all metrics and return as a dict.
    
    Returns:
        dict: {
            "accuracy": float,
            "precision": float,
            "recall": float,
            "f1_score": float,
            "auc_roc": float (if y_scores provided),
            "average_precision": float (if y_scores provided)
        }
    """
    # TODO: Compute and return all metrics
    pass


def print_classification_report(y_true, y_pred, target_names=None):
    """
    Print a detailed classification report.
    
    TODO: Use sklearn.metrics.classification_report
    """
    pass
