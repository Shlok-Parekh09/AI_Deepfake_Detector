"""Private model artifact locations, independent from architecture attribution."""
PRIVATE_REPOSITORY='Shlok0829/deepfake-models'
WEIGHTS_REVISION='def3d6af24cf7fac4b9cc99cdd01f0f843b27674'
AUDIO_FILE='audio/spectra_aasist3/model.safetensors'
VIDEO_FILE='video/gend_clip_l14/model.safetensors'
VIDEO_FACE_FILE='video/gend_clip_l14/det_10g.onnx'
IMAGE_FILE='image/vision_best.pth'
WHOLE_IMAGE_FILE='image/community_forensics/model.safetensors'


def local_weight(filename):
    """Resolve an organized local artifact without downloading anything."""
    from pathlib import Path
    path = Path(__file__).resolve().parents[2] / 'model_weights' / filename
    return str(path) if path.is_file() else None


def private_weight(filename):
    import os
    from huggingface_hub import hf_hub_download
    return hf_hub_download(repo_id=PRIVATE_REPOSITORY,filename=filename,
                           revision=WEIGHTS_REVISION,repo_type='model',token=os.getenv('HF_TOKEN'))
