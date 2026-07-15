# Training module for AI Deepfake Detector
# Lazy imports to avoid pulling pandas, heavy dataset code, etc. during
# lightweight training scripts (e.g. train_lightning_ai.py).

__all__ = [
    "get_train_transforms",
    "get_val_transforms",
    "DeepfakeDataset",
    "VideoDataset",
    "get_dataloader",
    "FocalLoss",
    "WeightedBCELoss",
    "get_loss_function",
    "get_optimizer",
    "get_scheduler",
    "EarlyStopping",
    "ModelCheckpoint",
    "TensorBoardLogger",
]


def __getattr__(name: str):
    if name in ("get_train_transforms", "get_val_transforms"):
        from .augmentations import get_train_transforms, get_val_transforms
        if name == "get_train_transforms":
            return get_train_transforms
        return get_val_transforms
    if name in ("DeepfakeDataset", "VideoDataset"):
        from .dataset import DeepfakeDataset, VideoDataset
        if name == "DeepfakeDataset":
            return DeepfakeDataset
        return VideoDataset
    if name == "get_dataloader":
        from .dataloader import get_dataloader
        return get_dataloader
    if name in ("FocalLoss", "WeightedBCELoss", "get_loss_function"):
        from .loss_functions import FocalLoss, WeightedBCELoss, get_loss_function
        return {"FocalLoss": FocalLoss, "WeightedBCELoss": WeightedBCELoss,
                "get_loss_function": get_loss_function}[name]
    if name in ("get_optimizer", "get_scheduler"):
        from .optimizer import get_optimizer, get_scheduler
        if name == "get_optimizer":
            return get_optimizer
        return get_scheduler
    if name in ("EarlyStopping", "ModelCheckpoint", "TensorBoardLogger"):
        from .callbacks import EarlyStopping, ModelCheckpoint, TensorBoardLogger
        return {"EarlyStopping": EarlyStopping, "ModelCheckpoint": ModelCheckpoint,
                "TensorBoardLogger": TensorBoardLogger}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")