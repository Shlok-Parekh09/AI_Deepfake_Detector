# Preprocessing module for AI Deepfake Detector
# Lazy imports to avoid heavy dependencies (facenet_pytorch, cv2, etc.) during training.

__all__ = [
    "FrameExtractor",
    "FaceDetector",
    "ImagePreprocessor",
    "AudioExtractor",
    "MetadataExtractor",
]


def __getattr__(name: str):
    if name == "FrameExtractor":
        from .frame_extractor import FrameExtractor
        return FrameExtractor
    if name == "FaceDetector":
        from .face_detector import FaceDetector
        return FaceDetector
    if name == "ImagePreprocessor":
        from .image_preprocessor import ImagePreprocessor
        return ImagePreprocessor
    if name == "AudioExtractor":
        from .audio_extractor import AudioExtractor
        return AudioExtractor
    if name == "MetadataExtractor":
        from .metadata_extractor import MetadataExtractor
        return MetadataExtractor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")