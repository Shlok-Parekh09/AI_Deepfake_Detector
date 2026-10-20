"""Private model artifact locations, independent from architecture attribution."""
PRIVATE_REPOSITORY='Shlok0829/deepfake-models'
WEIGHTS_REVISION='c4d100041e4f5c5180cb9d840bf5858badfce459'
AUDIO_FILE='audio/mms_1b.safetensors'
VIDEO_FILE='video/genconvit_vae.pth'
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
