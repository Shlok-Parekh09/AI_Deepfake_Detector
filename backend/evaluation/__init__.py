# Evaluation module for AI Deepfake Detector

from .metrics import (
    compute_accuracy,
    compute_precision,
    compute_recall,
    compute_f1,
    compute_auc_roc,
    compute_average_precision,
    compute_all_metrics,
    print_classification_report,
)
from .confusion_matrix import (
    generate_confusion_matrix,
    plot_confusion_matrix,
    plot_roc_curve,
    plot_precision_recall_curve,
)
from .evaluate import evaluate_model, evaluate_from_checkpoint
