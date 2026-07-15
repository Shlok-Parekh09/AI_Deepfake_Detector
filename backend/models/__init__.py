# Initialize Models module
# Lazy imports to avoid heavy dependencies (facenet_pytorch, etc.) during training.

__all__ = ["ViTDetector", "CNNDetector", "AudioCNN", "RNNDetector", "EnsembleDetector", "DeepfakeDetector"]


def __getattr__(name: str):
    if name == "ViTDetector":
        from .vit_model import ViTDetector
        return ViTDetector
    if name == "CNNDetector":
        from .cnn_model import CNNDetector
        return CNNDetector
    if name == "AudioCNN":
        from .audio_model import AudioCNN
        return AudioCNN
    if name == "RNNDetector":
        from .rnn_model import RNNDetector
        return RNNDetector
    if name == "EnsembleDetector":
        from .ensemble import EnsembleDetector
        return EnsembleDetector
    if name == "DeepfakeDetector":
        from .detector import DeepfakeDetector
        return DeepfakeDetector
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")