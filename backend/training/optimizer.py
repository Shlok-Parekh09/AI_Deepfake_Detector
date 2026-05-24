"""
Optimizer and Learning Rate Scheduler Configuration.
"""

# TODO: Import PyTorch
# import torch.optim as optim
# from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau, OneCycleLR


def get_optimizer(model, optimizer_type="adamw", learning_rate=1e-4, weight_decay=1e-5):
    """
    Create optimizer for the model.
    
    Supported optimizers:
    - AdamW (recommended for transformers and modern CNNs)
    - SGD with momentum
    - Adam
    
    TODO:
    - Initialize the selected optimizer with model parameters
    - Optionally use different learning rates for backbone vs classifier
    """
    pass


def get_scheduler(optimizer, scheduler_type="cosine", num_epochs=50, steps_per_epoch=100):
    """
    Create learning rate scheduler.
    
    Supported schedulers:
    - CosineAnnealingLR (smooth decay)
    - ReduceLROnPlateau (reduce on validation loss plateau)
    - OneCycleLR (super-convergence)
    - StepLR (step decay)
    
    TODO:
    - Initialize and return the selected scheduler
    """
    pass
