"""Pinned, offline inference adapters. Application class order is [real, fake]."""
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from safetensors.torch import load_file

REFERENCE = Path(__file__).parent / 'replacement_reference'
SPECTRA_REVISION = 'bc0ded888080ddad493177bb53aa6f5b95219d7c'
GEND_REVISION = '891ce014a0308386c4d7d25b3dcf436a22db5504'
SPECTRA_SHA256 = '327762caab3106ecee5f26b821ccdc6ab1fe34906a3e7042f416c87927df2088'
GEND_SHA256 = 'd76f0bdfd74a29fe1b1c1b84a80ac92486993e426878e8c7a3944281fbb96833'
GEND_FACE_SHA256 = '5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91'
SPECTRA_REAL_THRESHOLD = -1.0625009
SPECTRA_SAMPLES = 64600


def verify_weights(path, expected):
    hasher = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    if digest != expected:
        raise ValueError('Checkpoint checksum differs from the pinned model; refusing activation')
    return digest


def spectra_crop(wave, start=0):
    """Preemphasize the full waveform before crop/tile, as upstream evaluation does."""
    wave = np.asarray(wave, dtype=np.float32)
    if wave.ndim != 1 or not len(wave) or not np.isfinite(wave).all():
        raise ValueError('Expected finite, nonempty mono audio at 16 kHz')
    emphasized = np.concatenate((wave[:1], wave[1:] - .97 * wave[:-1]))
    crop = emphasized[start:start + SPECTRA_SAMPLES]
    if not len(crop):
        raise ValueError('Audio crop is empty')
    if len(crop) < SPECTRA_SAMPLES:
        crop = np.tile(crop, int(np.ceil(SPECTRA_SAMPLES / len(crop))))[:SPECTRA_SAMPLES]
    return torch.from_numpy(crop.copy())


class SpectraDetector(nn.Module):
    def __init__(self, network):
        super().__init__()
        self.network = network

    def forward(self, wave):
        raw = self.network(wave)
        # Preserve upstream classify(): raw[:, 1] > -1.0625009 means bona fide.
        # This is a monotonic decision score, NOT a calibrated probability.
        real = raw[:, 1] - SPECTRA_REAL_THRESHOLD
        return torch.stack((real, torch.zeros_like(real)), dim=-1)


def load_spectra(path, device):
    from backend.models.spectra_network import SpectraAASIST3
    digest = verify_weights(path, SPECTRA_SHA256)
    with torch.device('meta'):
        network = SpectraAASIST3()
    network.load_state_dict(load_file(str(path), device='cpu'), strict=True, assign=True)
    model = SpectraDetector(network).to(device).eval()
    return model, dict(arch='spectra_aasist3', seconds=SPECTRA_SAMPLES / 16000,
        max_windows=32, threshold=.5, source='lab260/Spectra-AASIST3',
        revision=SPECTRA_REVISION, weights_sha256=digest, label_map={'real':0,'fake':1},
        native_real_logit_threshold=SPECTRA_REAL_THRESHOLD,
        aggregation='mean_native_real_logit', score_calibrated=False,
        evaluation={}, preprocessing='16 kHz mono; preemphasis 0.97; tile short crops')


class GenDDetector(nn.Module):
    """GenD CLIP-L/14 architecture without redundant base-model downloads.

    Adapted from yermandy/GenD (MIT). All tensors, including vision projection,
    are checked strictly against the official checkpoint.
    """
    def __init__(self):
        super().__init__()
        from transformers import CLIPVisionConfig, CLIPVisionModel
        cfg = json.loads((REFERENCE / 'clip_config.json').read_text())
        vision = CLIPVisionConfig(**cfg['vision_config'])
        self.feature_extractor = nn.Module()
        self.feature_extractor.vision_model = CLIPVisionModel(vision).vision_model
        self.feature_extractor.visual_projection = nn.Linear(vision.hidden_size, cfg['projection_dim'], bias=False)
        self.model = nn.Module()
        self.model.linear = nn.Linear(vision.hidden_size, 2)

    def forward(self, images):
        features = self.feature_extractor.vision_model(images).pooler_output
        return self.model.linear(torch.nn.functional.normalize(features, p=2, dim=1))

    @staticmethod
    def preprocess(face):
        from PIL import Image
        # Official CLIP processor: shortest edge 224, bicubic, center crop, CLIP stats.
        from transformers import CLIPImageProcessor
        processor = CLIPImageProcessor()
        return processor(images=Image.fromarray(face).convert('RGB'), return_tensors='pt')['pixel_values'][0]

    def faces(self, frame, detector=None):
        """Five-landmark similarity alignment, adapted from GenD detector.py (MIT)."""
        import cv2
        faces = []
        boxes, landmarks = self.landmark_detector.detect(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        if len(boxes) == 0 or landmarks is None:
            return faces
        # Match the official pipeline: largest visible face per sampled frame.
        areas = (boxes[:,2]-boxes[:,0]) * (boxes[:,3]-boxes[:,1])
        for index in [int(np.argmax(areas))]:
            src = landmarks[index].astype(np.float32)
            dst = np.asarray([[.34,.46],[.66,.46],[.5,.64],[.37,.82],[.63,.82]], dtype=np.float32)
            upper = np.triu_indices(5, k=1)
            distances = np.linalg.norm(src[:,None] - src[None,:], axis=-1)[upper]
            reference = np.linalg.norm(dst[:,None] - dst[None,:], axis=-1)[upper]
            size = int(np.round(np.mean(distances / reference) * 1.3))
            if size < 2:
                continue
            # Bound extreme detections before allocating the aligned image.
            size = min(size, 2 * max(frame.shape[:2]))
            dst = (dst * size + size * .15) / 1.3
            transform, _ = cv2.estimateAffinePartial2D(src, dst, method=cv2.LMEDS)
            if transform is None or not np.isfinite(transform).all():
                continue
            faces.append(cv2.warpAffine(frame, transform, (size,size), flags=cv2.INTER_LINEAR))
        return faces


def load_gend(path, device):
    digest = verify_weights(path, GEND_SHA256)
    with torch.device('meta'):
        model = GenDDetector()
    model.load_state_dict(load_file(str(path), device='cpu'), strict=True, assign=True)
    # CLIP stores this deterministic buffer as nonpersistent (absent from weights).
    embeddings = model.feature_extractor.vision_model.embeddings
    embeddings.position_ids = torch.arange(embeddings.num_positions).expand((1, -1))
    model = model.to(device).eval()
    from backend.models.gend_face_detector import RetinaFace
    face_path = Path(path).parent / 'det_10g.onnx'
    if not face_path.is_file():
        from backend.models.weight_registry import private_weight, VIDEO_FACE_FILE
        face_path = Path(private_weight(VIDEO_FACE_FILE))
    verify_weights(face_path, GEND_FACE_SHA256)
    model.landmark_detector = RetinaFace(str(face_path), providers=['CPUExecutionProvider'])
    model.landmark_detector.prepare(ctx_id=-1, input_size=(640,640), det_thresh=.1, nms_thresh=.4)
    model.metadata = dict(arch='gend_clip_l14', source='yermandy/GenD_CLIP_L_14',
        revision=GEND_REVISION, weights_sha256=digest, label_map={'real':0,'fake':1},
        score_calibrated=False, face_detector_sha256=GEND_FACE_SHA256)
    return model
