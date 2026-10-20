"""
Single-File Predictor for Deepfake Detection.
Loads trained model weights and runs inference on a single image, video, or audio file.
Inference is trained-checkpoint only: scans fail fast when required weights are missing.
"""

import os
from pathlib import Path

from backend.utils.file_handler import FileHandler
from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import numpy as np
    import torch
    from backend.config import FAKE_THRESHOLD
    from backend.inference.postprocessing import PostProcessor
    from backend.models.model_factory import (
        AUDIO_CHECKPOINT_NAMES,
        VISION_CHECKPOINT_NAMES,
        checkpoint_size,
        find_checkpoint,
        load_vision_model,
    )
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
        self.video_checkpoint_path = None
        self.model = None
        self.audio_model = None
        self.video_model = None
        self.whole_image_model = None
        self.ml_available = ML_AVAILABLE

        if ML_AVAILABLE:
            self.device = get_device()
            from backend.models.weight_registry import local_weight, AUDIO_FILE, VIDEO_FILE, IMAGE_FILE
            self.vision_checkpoint_path = checkpoint_path or find_checkpoint(
                "DEEPFAKE_VISION_CHECKPOINT",
                VISION_CHECKPOINT_NAMES,
            )
            self.vision_checkpoint_path = self.vision_checkpoint_path or local_weight(IMAGE_FILE)

            if not self.vision_checkpoint_path:
                try:
                    from backend.models.weight_registry import private_weight, IMAGE_FILE
                    logger.info("Attempting to download vision model from Hugging Face Hub...")
                    self.vision_checkpoint_path = private_weight(IMAGE_FILE)
                    logger.info(f"Downloaded vision model to {self.vision_checkpoint_path}")
                except ImportError:
                    logger.warning("huggingface_hub not installed. Cannot download vision model automatically.")
                except Exception as e:
                    logger.warning(f"Could not download model from HF Hub: {e}")

            if self.vision_checkpoint_path and not os.path.exists(self.vision_checkpoint_path):
                logger.warning(f"Vision model checkpoint not found at {self.vision_checkpoint_path}")

            explicit_audio_path = os.getenv('DEEPFAKE_AUDIO_CHECKPOINT')
            if explicit_audio_path:
                if not Path(explicit_audio_path).is_file():
                    raise FileNotFoundError('Configured audio checkpoint does not exist')
                self.audio_checkpoint_path = explicit_audio_path
            else:
                self.audio_checkpoint_path = local_weight(AUDIO_FILE)

            # 2) Audio Model
            if not self.audio_checkpoint_path:
                if "KAGGLE_KERNEL_RUN_TYPE" not in os.environ:
                    try:
                        from backend.models.weight_registry import private_weight, AUDIO_FILE
                        logger.info("Attempting to download audio model from Hugging Face Hub...")
                        self.audio_checkpoint_path = private_weight(AUDIO_FILE)
                        logger.info(f"Downloaded audio model to {self.audio_checkpoint_path}")
                    except ImportError:
                        logger.warning("huggingface_hub not installed. Cannot download audio model automatically.")
                    except Exception as e:
                        logger.warning(f"Could not download audio model from HF Hub: {e}")

            # Lazy load transformers pipeline for summarization
            self._summarizer_pipeline = None

            try:
                from backend.preprocessing.face_detector import FaceDetector
                from backend.preprocessing.frame_extractor import FrameExtractor
                from backend.preprocessing.image_preprocessor import ImagePreprocessor
                self.face_detector = FaceDetector(device=str(self.device))
                self.preprocessor = ImagePreprocessor()
                self.frame_extractor = FrameExtractor()
                if self.vision_checkpoint_path:
                    self.model = load_vision_model(self.vision_checkpoint_path, self.device)
            except (ImportError, OSError) as exc:
                logger.warning('Vision inference unavailable: %s; audio can still run.', exc)
            if self.model is not None:
                logger.info(
                    "Loaded vision checkpoint %s (%s)",
                    self.vision_checkpoint_path,
                    checkpoint_size(self.vision_checkpoint_path),
                )
            else:
                logger.warning("Vision inference is unavailable; image/video scans are disabled.")

            if self.audio_checkpoint_path:
                from backend.models.audio_ssl import load_audio_checkpoint
                self.audio_model, self.audio_metadata = load_audio_checkpoint(self.audio_checkpoint_path, self.device)
                logger.info(
                    "Loaded audio checkpoint %s (%s)",
                    self.audio_checkpoint_path,
                    checkpoint_size(self.audio_checkpoint_path),
                )
            else:
                logger.warning("No audio checkpoint found; audio scans are disabled.")

            video_path = os.getenv('DEEPFAKE_VIDEO_CHECKPOINT')
            if not video_path:
                local_video = local_weight(VIDEO_FILE)
                if local_video:
                    video_path = local_video
                else:
                    from backend.models.weight_registry import private_weight, VIDEO_FILE
                    video_path = private_weight(VIDEO_FILE)
            self.video_checkpoint_path = video_path
            if 'gend_clip_l14' in str(video_path).lower():
                from backend.models.replacement_models import load_gend
                self.video_model = load_gend(video_path, self.device)
                self.video_metadata = self.video_model.metadata
            else:
                from backend.models.genconvit import load_video_checkpoint
                self.video_model = load_video_checkpoint(video_path, self.device)
                self.video_metadata = {'arch':'genconvit_vae'}
            logger.info('Loaded dedicated video detector: %s', self.video_metadata['arch'])

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

    def predict(self, file_path: str, original_name: str | None = None) -> dict:
        """Auto-detect file type and run prediction."""
        validation = self.file_handler.validate_file(file_path)
        if not validation['valid']:
            raise ValueError(validation['error'])
        file_type = validation['file_type']

        if not ML_AVAILABLE:
            raise RuntimeError("ML dependencies are not installed. Trained inference is unavailable.")

        if file_type == "audio":
            if getattr(self, "audio_model", None) is None:
                raise RuntimeError(
                    "The configured audio checkpoint is unavailable. Check model_weights/audio or private Hugging Face access."
                )
            return self._with_report(self.predict_audio(file_path), file_path, original_name)

        if file_type == 'video':
            if getattr(self, 'video_model', None) is None:
                raise RuntimeError('The dedicated video checkpoint is unavailable')
            return self._with_report(self.predict_video(file_path), file_path, original_name)

        if file_type == "image":
            return self._with_report(self.predict_image(file_path), file_path, original_name)
        else:
            return self._with_report(self.predict_video(file_path), file_path, original_name)

    def _with_report(self, result, path, original_name=None):
        try:
            from backend.reports.evidence import attach_report
            return attach_report(result, path, original_name or Path(path).name, self)
        except Exception:
            logger.exception('Audit report generation failed; retaining the detection result')
            result['report_error'] = 'The PDF report could not be generated. Retry the scan to request a fresh report.'
            return result

    def predict_image(self, image_path: str) -> dict:
        from PIL import Image
        from backend.preprocessing.media_io import load_image
        import torch
        import numpy as np

        detected_tool = None
        try:
            with Image.open(image_path) as pil_img:
                exif = pil_img.getexif()
                if exif and 305 in exif:
                    detected_tool = str(exif[305])
        except Exception as e:
            logger.warning(f"Failed to read EXIF: {e}")

        decoded_image = load_image(image_path)
        img = np.array(decoded_image)
        faces = self.face_detector.extract_faces(img)[:16]
        with torch.inference_mode():
            if faces:
                probs = []
                for face in faces:
                    if self.model is None: raise RuntimeError('Face-image checkpoint unavailable')
                    logits = self.model(self.preprocessor.preprocess(face).to(self.device))
                    if not torch.isfinite(logits).all(): raise RuntimeError('Nonfinite face-image prediction')
                    probs.append(float(logits.softmax(-1)[0,1]))
                # Mixed images must retain evidence from a suspicious face instead of averaging it away.
                probability = max(probs)
                metadata = dict(arch='efficientnet_b4')
                scope = 'Up to 16 detected faces, assessed independently; maximum face evidence. Background authenticity is not assessed.'
                method = 'EfficientNet-B4 scores each detected face independently after face preprocessing. Maximum face evidence is compared with 0.5. This multi-face application rule is not calibrated certainty; background edits are not assessed.'
            else:
                if getattr(self, 'whole_image_model', None) is None:
                    from backend.models.whole_image import load_whole_image
                    self.whole_image_model = load_whole_image(self.device)
                model = self.whole_image_model
                logits = model(model.preprocess(decoded_image).to(self.device).unsqueeze(0))
                if not torch.isfinite(logits).all(): raise RuntimeError('Nonfinite whole-image prediction')
                probability = float(logits.sigmoid().item())
                probs = []
                metadata = dict(model.metadata)
                scope = 'Whole-image synthetic-content classifier: aspect-preserving resize to shortest edge 440, then central 384 x 384 crop. No face required; peripheral regions can be omitted.'
                method = ('ViT-S/16 at 384 pixels uses ImageNet normalization and a binary sigmoid head. '
                          'Evidence at or above 0.5 produces Fake; otherwise Real. This detects learned image synthesis patterns, '
                          'not every possible edit, and does not identify a generator or establish authenticity.')
            result = self.postprocessor.format_result(probability)
            result.update(file_type='image', num_faces_analysed=len(faces),
                reasons=['Independent detected-face assessment' if faces else 'Whole-image synthesis assessment'],
                raw_scores={'image_model':round(probability,4)}, explainability_heatmap=None,
                detected_tool=detected_tool or 'Unknown', score_calibrated=False,
                decision_threshold=.5, is_fake=probability>=.5, label='FAKE' if probability>=.5 else 'REAL',
                fake_probability=probability, review_required=True, confidence='uncalibrated',
                analysis_scope=scope, detector_metadata=metadata, detector_method=method,
                image_face_scores=[{'face_index':i,'fake_probability':p} for i,p in enumerate(probs)])
            result['ai_summary'] = 'Model prediction: '+result['label']+'. '+scope
            return result

    def predict_video(self, video_path: str) -> dict:
        """Score face crops with the dedicated video checkpoint."""
        import cv2
        import numpy as np
        import torch
        if self.video_model is None:
            raise RuntimeError('A dedicated video checkpoint is required')
        from backend.preprocessing.media_io import sample_video_frames
        frames = sample_video_frames(video_path)
        scores = []
        frame_scores = []
        mean = torch.tensor([.485,.456,.406],device=self.device)[:,None,None]
        std = torch.tensor([.229,.224,.225],device=self.device)[:,None,None]
        with torch.inference_mode():
            for position, frame in frames:
                is_gend = getattr(self, 'video_metadata', {}).get('arch') == 'gend_clip_l14'
                faces = (self.video_model.faces(frame, self.face_detector, max_faces=16) if is_gend
                         else self.face_detector.extract_faces(frame,margin=0.))
                current = []
                for face in faces[:16]:
                    if not face.size:
                        continue
                    if is_gend:
                        tensor = self.video_model.preprocess(face).to(self.device)
                        logits = self.video_model(tensor.unsqueeze(0))
                    else:
                        face = cv2.resize(face,(224,224),interpolation=cv2.INTER_AREA)
                        tensor = torch.from_numpy(face.transpose(2,0,1).copy()).float().to(self.device)/255.
                        logits = self.video_model(((tensor-mean)/std).unsqueeze(0))
                    if not torch.isfinite(logits).all():
                        raise RuntimeError('Video model produced nonfinite scores')
                    # Reference inference averages independent sigmoid class scores.
                    evidence = (logits.float().softmax(-1) if is_gend else logits.float().sigmoid())[0].cpu().tolist()
                    probability = evidence[1] / max(sum(evidence), 1e-12)
                    scores.append(evidence); current.append(probability)
                if current:
                    frame_scores.append({'frame_index':int(position),'fake_probability':max(current),
                        'faces_analysed':len(current),'face_scores':current})
        if not scores:
            if not frames: raise ValueError('No readable video frames were decoded')
            from PIL import Image
            if getattr(self, 'whole_image_model', None) is None:
                from backend.models.whole_image import load_whole_image
                self.whole_image_model = load_whole_image(self.device)
            model = self.whole_image_model
            with torch.inference_mode():
                for position, frame in frames:
                    logits = model(model.preprocess(Image.fromarray(frame)).to(self.device).unsqueeze(0))
                    if not torch.isfinite(logits).all(): raise RuntimeError('Nonfinite whole-frame video prediction')
                    frame_scores.append({'frame_index':int(position),'fake_probability':float(logits.sigmoid().item()),'faces_analysed':0})
            probability = float(np.mean([item['fake_probability'] for item in frame_scores]))
            result = self.postprocessor.format_result(probability)
            result.update(file_type='video',is_fake=probability>=.5,fake_probability=probability,
                label='FAKE' if probability>=.5 else 'REAL',num_faces_analysed=0,
                frames_analysed=len(frame_scores),video_frame_scores=frame_scores,
                score_calibrated=False,review_required=True,confidence='uncalibrated',decision_threshold=.5,
                explainability_heatmap=None,detector_metadata=dict(model.metadata),
                analysis_scope='No detected faces in sampled frames. Whole-frame image synthesis classification on central 384 x 384 crops; mean across sampled frames. No motion, soundtrack or confirmed temporal localization analysis.',
                detector_method='ViT-S/16: shortest-edge resize 440, central crop 384, ImageNet normalization, sigmoid head. Mean frame evidence at or above 0.5 gives Fake. This is an image detector applied to sampled video frames, not a temporal video model.',
                ai_summary='Whole-frame sampled video assessment. Image-based synthesis evidence only; not proof of authenticity.')
            return result
        real_evidence, fake_evidence = np.asarray(scores).mean(axis=0).tolist()
        # Multi-face extension: strongest face in each frame, averaged over sampled frames.
        probability = float(np.mean([frame['fake_probability'] for frame in frame_scores]))
        result = self.postprocessor.format_result(probability)
        result.update(file_type='video',num_faces_analysed=len(scores),frames_analysed=len(frame_scores),
            raw_scores={getattr(self, 'video_metadata', {}).get('arch', 'genconvit_vae'):round(probability,4),
                        'real_mean_evidence':real_evidence, 'fake_mean_evidence':fake_evidence},
            reasons=['Dedicated face-video model: ' + getattr(self, 'video_metadata', {}).get('arch', 'genconvit_vae'),
            f'Analyzed {len(scores)} face crops across {len(frame_scores)} sampled frames.'],
            decision_threshold=.5,explainability_heatmap=None,
            label='FAKE' if probability>=.5 else 'REAL',p_fake=probability,p_fake_int=round(100*probability))
        result.update(score_calibrated=False, review_required=True, confidence='uncalibrated',
                      video_frame_scores=frame_scores,
                      analysis_scope='Up to 16 faces per sampled frame: maximum face evidence per frame, then mean across frames. Video audio and non-face manipulations are not assessed.')
        result['ai_summary'] = (f"Video model prediction: {result['label']}. Synthetic score: {round(100*probability)}%. "
                                'Sampled face analysis only. The score is uncalibrated and is not proof of authenticity.')
        return result

    def predict_audio(self, audio_path: str) -> dict:
        import torch

        if self.audio_model is None:
            raise RuntimeError("A trained audio checkpoint is required")
        metadata = getattr(self, "audio_metadata", {})
        segments = []
        with torch.no_grad():
            if metadata.get('arch') == 'spectra_aasist3':
                from backend.preprocessing.audio_waveform import read_waveform, window_starts, SAMPLE_RATE
                from backend.models.replacement_models import spectra_crop, SPECTRA_SAMPLES
                wave = read_waveform(audio_path)
                duration = len(wave) / SAMPLE_RATE
                starts = window_starts(len(wave), SPECTRA_SAMPLES, metadata['max_windows'])
                real_margins = []
                for start in starts:
                    crop = spectra_crop(wave, start).unsqueeze(0).to(self.device)
                    logits = self.audio_model(crop)
                    if not torch.isfinite(logits).all():
                        raise RuntimeError('Audio model produced nonfinite scores')
                    real_margins.append(float(logits[0,0]))
                # Aggregate native margins rather than silently substituting two-logit softmax.
                prob = float(torch.sigmoid(torch.tensor(-sum(real_margins)/len(real_margins))))
                segments = [{'start_seconds':round(start/SAMPLE_RATE,3),
                             'end_seconds':round(min(duration,(start+SPECTRA_SAMPLES)/SAMPLE_RATE),3),
                             'fake_probability':float(torch.sigmoid(torch.tensor(-margin)))}
                            for start,margin in zip(starts,real_margins)]
            elif metadata.get('arch') == 'antideepfake_mms_1b':
                from backend.preprocessing.audio_waveform import read_waveform, window_starts, SAMPLE_RATE
                wave = read_waveform(audio_path)
                duration = len(wave) / SAMPLE_RATE
                length = int(metadata['seconds'] * SAMPLE_RATE)
                starts = window_starts(len(wave), length, metadata['max_windows'])
                scores = []
                for start in starts:
                    crop = torch.from_numpy(wave[start:start+length].copy()).to(self.device)
                    # Published preprocessing: layer_norm of the valid mono 16 kHz waveform.
                    crop = torch.nn.functional.layer_norm(crop, crop.shape)
                    logits = self.audio_model(crop.unsqueeze(0))
                    if not torch.isfinite(logits).all():
                        raise RuntimeError('Audio model produced nonfinite scores')
                    scores.append(float(logits.float().softmax(-1)[0, 1]))
                prob = sum(scores) / len(scores)
                segments = [{'start_seconds':round(start/SAMPLE_RATE,3),
                             'end_seconds':round(min(duration,(start+length)/SAMPLE_RATE),3),
                             'fake_probability':round(score,4)} for start,score in zip(starts,scores)]
            elif metadata.get("arch") == "audio_ssl":
                from backend.preprocessing.audio_waveform import audio_windows, SAMPLE_RATE
                inputs, masks, starts, duration = audio_windows(
                    audio_path, metadata.get("seconds", 4.), metadata.get("max_windows", 12))
                scores = []
                for offset in range(0, len(inputs), 4):
                    logits = self.audio_model(inputs[offset:offset+4].to(self.device), masks[offset:offset+4].to(self.device))
                    scores.extend((logits.float() / metadata.get("temperature", 1.)).softmax(-1)[:, 1].cpu().tolist())
                prob = max(scores) if metadata.get('aggregation') == 'max_window_probability' else sum(scores) / len(scores)
                segments = [{"start_seconds": round(start / SAMPLE_RATE, 3),
                             "end_seconds": round(min(duration, start / SAMPLE_RATE + metadata.get("seconds", 4.)), 3),
                             "fake_probability": round(score, 4)} for start, score in zip(starts, scores)]
            else:
                features = load_log_mel(audio_path).unsqueeze(0).to(self.device)
                logits = self.audio_model(features)
                prob = torch.softmax(logits, dim=1)[0, 1].item()

        from backend.inference.postprocessing import PostProcessor
        result = PostProcessor(threshold=metadata.get("threshold", self.threshold)).format_result(prob)
        result["file_type"] = "audio"
        result["num_faces_analysed"] = 0
        result["frames_analysed"] = 0
        result["reasons"] = [
            "Audio checkpoint analysis",
            "Log-mel spectral classifier scored the clip for synthetic voice artifacts.",
        ]
        result["raw_scores"] = {metadata.get("arch", "audio_cnn"): round(prob, 4)}
        if segments:
            result["audio_segments"] = segments
            result["audio_duration_seconds"] = round(duration, 3)
            result["reasons"] = ["Multilingual speech encoder with model window scores",
                                 f"Evaluated {len(segments)} windows across the recording."]
            result["model_evaluation"] = metadata.get("evaluation", {})
        result["spectrogram_is_attribution"] = False
        result["explainability_heatmap"] = None
        threshold = float(metadata.get("threshold", self.threshold))
        result["decision_threshold"] = threshold
        result['p_fake'] = prob
        result['p_fake_int'] = int(round(100 * prob))
        result['label'] = 'FAKE' if result['is_fake'] else 'REAL'
        result['surety_int'] = int(round(100 * (prob if result['is_fake'] else 1-prob)))
        result['surety_percentage'] = str(result['surety_int']) + '%'
        # A probability near the calibrated cutoff is not high-confidence evidence.
        margin = ((prob - threshold) / (1 - threshold) if result['is_fake']
                  else (threshold - prob) / threshold)
        result['confidence'] = 'high' if margin >= .8 else 'medium' if margin >= .5 else 'low'
        result['review_required'] = result['confidence'] == 'low'
        result['score_calibrated'] = bool(metadata.get('score_calibrated', False))
        if not result['score_calibrated']:
            result['review_required'] = True
            result['confidence'] = 'uncalibrated'
        if segments:
            intervals = sorted((s['start_seconds'], s['end_seconds']) for s in segments)
            covered = 0.; end = 0.
            for start, stop in intervals:
                covered += max(0., stop-max(start,end)); end=max(end,stop)
            result['audio_assessment'] = {'analyzed_seconds':round(covered,3),
                'coverage_fraction':min(1.,covered/duration), 'window_count':len(segments),
                'max_window_fake_score':max(s['fake_probability'] for s in segments),
                'min_window_fake_score':min(s['fake_probability'] for s in segments),
                'scope':'Speech synthesis detection; non-speech sound authenticity is not established.'}
        coverage_note = (f" Analyzed {covered:.1f} of {duration:.1f} seconds in sampled speech windows."
                         if segments else '')
        calibration_note = ('This is an uncalibrated model estimate, not proof of authenticity.'
                            if not result['score_calibrated'] else 'This model estimate is not proof of authenticity.')
        result['ai_summary'] = (f"Model prediction: {result['label']}. "
                               f"Synthetic score: {result['p_fake_int']}%. "
                               f'Decision threshold: {threshold:.0%}.{coverage_note} {calibration_note}')
        return result

    def predict_from_url(self, url: str) -> dict:
        if not ML_AVAILABLE:
            raise RuntimeError("ML dependencies are not installed. Trained inference is unavailable.")

        local_path = self.url_downloader.download(url)
        try:
            return self.predict(local_path)
        finally:
            self.file_handler.cleanup(local_path)
