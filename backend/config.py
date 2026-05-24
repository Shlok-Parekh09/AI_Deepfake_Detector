"""
Global configuration for the AI Deepfake Detector.
Stores paths, hyperparameters, model settings, and detection thresholds.
"""

import os

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
SPLITS_DIR = os.path.join(DATA_DIR, "splits")
CHECKPOINTS_DIR = os.path.join(BASE_DIR, "checkpoints")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# ============================================================
# MODEL HYPERPARAMETERS
# ============================================================
# TODO: Adjust these values based on your dataset and hardware
IMAGE_SIZE = (224, 224)          # Input image dimensions (H, W)
BATCH_SIZE = 32                 # Training batch size
NUM_EPOCHS = 50                 # Maximum training epochs
LEARNING_RATE = 1e-4            # Initial learning rate
WEIGHT_DECAY = 1e-5             # L2 regularization
NUM_CLASSES = 2                 # Real vs Fake
SEQUENCE_LENGTH = 20            # Number of frames for temporal analysis

# ============================================================
# DATA AUGMENTATION
# ============================================================
AUGMENTATION_PROBABILITY = 0.5  # Probability of applying each augmentation

# ============================================================
# VIDEO PROCESSING
# ============================================================
FRAME_EXTRACTION_FPS = 5        # Frames per second to extract from video
MAX_VIDEO_DURATION = 300        # Maximum video duration in seconds (5 min)
MAX_FRAMES_PER_VIDEO = 100      # Maximum frames to extract per video

# ============================================================
# FACE DETECTION
# ============================================================
FACE_DETECTION_CONFIDENCE = 0.9  # Minimum confidence for face detection
FACE_MARGIN = 0.3               # Margin around detected face (percentage)

# ============================================================
# INFERENCE / DETECTION THRESHOLDS
# ============================================================
FAKE_THRESHOLD = 0.5            # Probability above which media is classified as fake
CONFIDENCE_CALIBRATION = True   # Whether to apply confidence calibration

# ============================================================
# LOGGING
# ============================================================
LOG_LEVEL = "INFO"
TENSORBOARD_ENABLED = True

# ============================================================
# GPU SETTINGS
# ============================================================
DEVICE = "cuda"                 # "cuda" or "cpu"
MIXED_PRECISION = True          # Use AMP (Automatic Mixed Precision)
