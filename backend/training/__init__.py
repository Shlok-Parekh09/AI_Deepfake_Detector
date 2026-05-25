# Training module for AI Deepfake Detector

from .augmentations import get_train_transforms, get_val_transforms
from .dataset import DeepfakeDataset, VideoDataset
from .dataloader import get_train_loader, get_val_loader, get_test_loader
from .loss_functions import FocalLoss, WeightedBCELoss, get_loss_function
from .optimizer import get_optimizer, get_scheduler
from .callbacks import EarlyStopping, ModelCheckpoint, TensorBoardLogger
from .train import train_model
