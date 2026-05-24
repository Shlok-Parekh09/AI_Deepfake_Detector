"""
Data Splitting Script.
Creates train/validation/test splits from the processed dataset.
"""

# TODO: Import required modules
# import os
# import pandas as pd
# from sklearn.model_selection import train_test_split


def create_splits(data_dir, output_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42):
    """
    Split dataset into train/validation/test sets.
    
    Creates CSV files:
    - train.csv (filepath, label)
    - val.csv (filepath, label)
    - test.csv (filepath, label)
    
    TODO:
    - Scan data directory for all files
    - Stratified split (maintain real/fake ratio)
    - Save split CSVs
    - Print split statistics
    """
    pass


def verify_splits(splits_dir):
    """
    Verify that splits are valid (no overlap, correct ratios).
    
    TODO: Load splits and verify
    """
    pass


if __name__ == "__main__":
    # TODO: Parse arguments
    # python scripts/split_data.py --data data/processed --output data/splits
    pass
