"""
Confusion Matrix Generation and Visualization.
"""

# TODO: Import required modules
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


def generate_confusion_matrix(y_true, y_pred, labels=None):
    """
    Generate a confusion matrix from predictions.
    
    TODO:
    - Compute confusion matrix using sklearn
    - Return as numpy array
    """
    pass


def plot_confusion_matrix(y_true, y_pred, labels=None, save_path=None):
    """
    Plot and save confusion matrix as an image.
    
    TODO:
    - Generate confusion matrix
    - Plot using matplotlib/seaborn
    - Save to file if save_path provided
    - Show plot if not saving
    """
    pass


def plot_roc_curve(y_true, y_scores, save_path=None):
    """
    Plot ROC curve with AUC score.
    
    TODO:
    - Compute FPR and TPR at various thresholds
    - Plot ROC curve
    - Annotate with AUC score
    """
    pass


def plot_precision_recall_curve(y_true, y_scores, save_path=None):
    """
    Plot Precision-Recall curve.
    
    TODO: Compute and plot precision-recall curve
    """
    pass
