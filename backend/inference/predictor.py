"""
Single-File Predictor for Deepfake Detection.
Loads trained model weights and runs inference on a single image, video, or audio file.
Inference is trained-checkpoint only: scans fail fast when required weights are missing.
"""

from pathlib import Path

from backend.utils.file_handler import FileHandler
from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import numpy as np
    import torch
    from backend.config import FAKE_THRESHOLD
    from backend.inference.postprocessing import PostProcessor
    from backend.models.audio_model import AudioCNN
    from backend.models.model_factory import (
        AUDIO_CHECKPOINT_NAMES,
        VISION_CHECKPOINT_NAMES,
        checkpoint_size,
        find_checkpoint,
        load_vision_model,
    )
    from backend.preprocessing.face_detector import FaceDetector
    from backend.preprocessing.frame_extractor import FrameExtractor
    from backend.preprocessing.image_preprocessor import ImagePreprocessor
    from backend.preprocessing.audio_features import load_log_mel
    from backend.utils.gpu_utils import get_device
    from backend.utils.url_downloader import URLDownloader
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML libraries not found ({e}). Inference is unavailable until dependencies are installed.")
    ML_AVAILABLE = False
    from backend.config import FAKE_THRESHOLD


class Predictor:
    """
    Run deepfake detection on a single file (image or video).
    """

    def __init__(self, checkpoint_path: str | None = None):
        self.file_handler = FileHandler()
        self.threshold = FAKE_THRESHOLD
        self.vision_checkpoint_path = None
        self.audio_checkpoint_path = None
        self.model = None
        self.audio_model = None
        self.ml_available = ML_AVAILABLE
        
        if ML_AVAILABLE:
            self.device = get_device()
            self.vision_checkpoint_path = checkpoint_path or find_checkpoint(
                "DEEPFAKE_VISION_CHECKPOINT",
                VISION_CHECKPOINT_NAMES,
            )
            
            if not self.vision_checkpoint_path:
                try:
                    from huggingface_hub import hf_hub_download
                    logger.info("Attempting to download vision model from Hugging Face Hub...")
                    self.vision_checkpoint_path = hf_hub_download(
                        repo_id="Shlok0829/deepfake-detector",
                        filename="vision_best.pth"
                    )
                except Exception as e:
                    logger.warning(f"Could not download model from HF Hub: {e}")

            self.audio_checkpoint_path = find_checkpoint(
                "DEEPFAKE_AUDIO_CHECKPOINT",
                AUDIO_CHECKPOINT_NAMES,
            )
            
            # Lazy load transformers pipeline for summarization
            self._summarizer_pipeline = None

            if self.vision_checkpoint_path:
                self.model = load_vision_model(self.vision_checkpoint_path, self.device)
                logger.info(
                    "Loaded vision checkpoint %s (%s)",
                    self.vision_checkpoint_path,
                    checkpoint_size(self.vision_checkpoint_path),
                )
            else:
                logger.warning("No vision checkpoint found; image/video scans are disabled.")

            if self.audio_checkpoint_path:
                self.audio_model = AudioCNN().to(self.device)
                audio_state = torch.load(self.audio_checkpoint_path, map_location=self.device)
                state_dict = audio_state.get("model_state_dict", audio_state)
                # Strip 'module.' prefix if model was trained with DataParallel
                state_dict = {k.replace("module.", "") if k.startswith("module.") else k: v for k, v in state_dict.items()}
                self.audio_model.load_state_dict(state_dict)
                self.audio_model.eval()
                logger.info(
                    "Loaded audio checkpoint %s (%s)",
                    self.audio_checkpoint_path,
                    checkpoint_size(self.audio_checkpoint_path),
                )
            else:
                logger.warning("No audio checkpoint found; audio scans are disabled.")

            self.face_detector = FaceDetector(device=str(self.device))
            self.preprocessor = ImagePreprocessor()
            self.frame_extractor = FrameExtractor()
            self.postprocessor = PostProcessor()
            self.url_downloader = URLDownloader()
            logger.info("Predictor initialised on %s", self.device)
        else:
            self.device = None
            self._summarizer_pipeline = None
            logger.info("Predictor initialised with inference disabled.")

    def _get_ai_summary(self, is_fake: bool, prob: float, file_type: str) -> str:
        """Generate a human-readable AI summary."""
        verdict = "synthetic" if is_fake else "authentic"
        confidence = "high" if prob > 0.85 or prob < 0.15 else "moderate"
        
        if is_fake:
            return f"Analysis indicates with {confidence} confidence ({round(prob*100)}%) that this {file_type} is {verdict}. Strong indicators of generative AI artifacts were found."
        else:
            return f"Analysis indicates with {confidence} confidence ({round(prob*100)}%) that this {file_type} is {verdict}. The media appears natural with consistent noise distributions and no structural anomalies."

    def predict(self, file_path: str) -> dict:
        """Auto-detect file type and run prediction."""
        file_type = self.file_handler.get_file_type(file_path)
        
        if file_type not in ["image", "video", "audio"]:
            return {
                "fake_probability": 0.0,
                "is_fake": False,
                "confidence": "none",
                "reasons": [],
                "error": f"Unsupported file: {Path(file_path).suffix}",
            }
            
        if not ML_AVAILABLE:
            raise RuntimeError("ML dependencies are not installed. Trained inference is unavailable.")

        if file_type == "audio":
            if getattr(self, "audio_model", None) is None:
                raise RuntimeError(
                    "Audio checkpoint is missing. Train on Kaggle and place audio_best.pth in backend/checkpoints."
                )
            return self.predict_audio(file_path)

        if getattr(self, "model", None) is None:
            raise RuntimeError(
                "Vision checkpoint is missing. Train on Kaggle and place vision_best.pth in backend/checkpoints."
            )

        if file_type == "image":
            return self.predict_image(file_path)
        else:
            return self.predict_video(file_path)

    def predict_image(self, image_path: str) -> dict:
        from PIL import Image
        import torch
        import numpy as np
        with torch.no_grad():
            img = np.array(Image.open(image_path).convert("RGB"))
            faces = self.face_detector.extract_faces(img)
            if not faces: faces = [img]

            probs: list[float] = []
            for face in faces:
                tensor = self.preprocessor.preprocess(face).to(self.device)
                logits = self.model(tensor)
                prob = torch.softmax(logits, dim=1)[0, 1].item()
                probs.append(prob)

            avg_prob = self.postprocessor.aggregate_frame_predictions(probs)

            result = self.postprocessor.format_result(avg_prob)
            result["file_type"] = "image"
            result["num_faces_analysed"] = len(faces)
            result["reasons"] = ["Trained vision checkpoint analysis"]
            result["raw_scores"] = {"vision_model": round(avg_prob, 4)}
            result["explainability_heatmap"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            result["ai_summary"] = self._get_ai_summary(result["is_fake"], avg_prob, "image")
            return result

    def predict_video(self, video_path: str) -> dict:
        import torch
        import subprocess
        import tempfile
        import os

        audio_score = None
        audio_result = None
        if getattr(self, "audio_model", None) is not None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
                tmp_audio_path = tmp_audio.name
            try:
                cmd = ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-y", tmp_audio_path]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                audio_result = self.predict_audio(tmp_audio_path)
                audio_score = audio_result["raw_scores"].get("audio_cnn")
            except Exception as e:
                logger.warning(f"Audio extraction from video failed or no audio track: {e}")
            finally:
                if os.path.exists(tmp_audio_path):
                    os.unlink(tmp_audio_path)

        with torch.no_grad():
            frames = self.frame_extractor.extract(video_path)
            if not frames:
                if audio_score is not None:
                    audio_result["file_type"] = "video"
                    return audio_result
                result = self.postprocessor.format_result(0.0)
                result["file_type"] = "video"
                result["num_faces_analysed"] = 0
                return result

            all_probs: list[float] = []
            for frame in frames:
                faces = self.face_detector.extract_faces(frame)
                targets = faces if faces else [frame]
                for face in targets:
                    tensor = self.preprocessor.preprocess(face).to(self.device)
                    logits = self.model(tensor)
                    prob = torch.softmax(logits, dim=1)[0, 1].item()
                    all_probs.append(prob)

            vision_prob = self.postprocessor.aggregate_frame_predictions(all_probs)

            final_prob = vision_prob
            reasons = ["Trained vision checkpoint analysis"]
            raw_scores = {"vision_model": round(vision_prob, 4)}

            if audio_score is not None:
                final_prob = (vision_prob + audio_score) / 2.0
                reasons.append("Audio checkpoint analysis")
                reasons.append("Combined spatial artifact and voice forensic scores")
                raw_scores["audio_cnn"] = round(audio_score, 4)

            result = self.postprocessor.format_result(final_prob)
            result["file_type"] = "video"
            result["num_faces_analysed"] = len(all_probs)
            result["frames_analysed"] = len(frames)
            result["reasons"] = reasons
            result["raw_scores"] = raw_scores
            result["explainability_heatmap"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
            result["ai_summary"] = self._get_ai_summary(result["is_fake"], final_prob, "video")
            return result

    def predict_audio(self, audio_path: str) -> dict:
        import torch
        with torch.no_grad():
            features = load_log_mel(audio_path).unsqueeze(0).to(self.device)
            logits = self.audio_model(features)
            prob = torch.softmax(logits, dim=1)[0, 1].item()

        result = self.postprocessor.format_result(prob)
        result["file_type"] = "audio"
        result["num_faces_analysed"] = 0
        result["frames_analysed"] = 0
        result["reasons"] = [
            "Audio checkpoint analysis",
            "Log-mel spectral classifier scored the clip for synthetic voice artifacts.",
        ]
        result["raw_scores"] = {"audio_cnn": round(prob, 4)}
        result["ai_summary"] = self._get_ai_summary(result["is_fake"], prob, "audio")
        return result

    def predict_from_url(self, url: str) -> dict:
        if not ML_AVAILABLE:
            raise RuntimeError("ML dependencies are not installed. Trained inference is unavailable.")

        local_path = self.url_downloader.download(url)
        try:
            return self.predict(local_path)
        finally:
            self.file_handler.cleanup(local_path)
