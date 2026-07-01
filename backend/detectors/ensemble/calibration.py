import torch
import torch.nn as nn
from typing import Dict, Any

class TemperatureScaler(nn.Module):
    """
    Wraps the final ensemble probability to calibrate confidence scores.
    Learns a single scalar temperature parameter to smooth out over-confident logits.
    """
    def __init__(self):
        super().__init__()
        # Initialized to 1.5 to slightly soften extreme predictions
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
        
    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Scales logits by temperature before sigmoid.
        """
        return torch.sigmoid(logits / self.temperature)

    def calibrate_probability(self, probability: float) -> float:
        """
        Applies temperature scaling to a raw probability (0.0 to 1.0).
        """
        if probability >= 1.0:
            probability = 0.9999
        if probability <= 0.0:
            probability = 0.0001
            
        # Inverse sigmoid to get mock logits
        import math
        logit = math.log(probability / (1 - probability))
        
        # Apply temperature
        scaled_logit = logit / self.temperature.item()
        
        # Back to probability
        return 1.0 / (1.0 + math.exp(-scaled_logit))


def fit_temperature(scaler: TemperatureScaler, val_logits: torch.Tensor, val_labels: torch.Tensor):
    """
    Calibration Script Stub:
    Fits the temperature scaler on a held-out validation set to minimize NLL loss.
    """
    import torch.optim as optim
    
    criterion = nn.BCELoss()
    optimizer = optim.LBFGS([scaler.temperature], lr=0.01, max_iter=50)
    
    def eval_loss():
        optimizer.zero_grad()
        probs = scaler(val_logits)
        loss = criterion(probs, val_labels.float())
        loss.backward()
        return loss
        
    optimizer.step(eval_loss)
    return scaler.temperature.item()
