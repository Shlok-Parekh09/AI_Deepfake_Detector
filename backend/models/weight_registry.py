"""Private model artifact locations, independent from architecture attribution."""
PRIVATE_REPOSITORY='Shlok0829/deepfake-models'
WEIGHTS_REVISION='1c27bfd1e29a99fac219f56a8d41b130ba092af6'
AUDIO_FILE='audio/spectra_aasist3/model.safetensors'
VIDEO_FILE='video/gend_clip_l14/model.safetensors'
VIDEO_FACE_FILE='video/gend_clip_l14/det_10g.onnx'
IMAGE_FILE='image/vision_best.pth'


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
