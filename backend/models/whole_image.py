"""Whole-image ViT adapter; strict weights and official Community Forensics transforms."""
from pathlib import Path
import torch
from torch import nn
from safetensors.torch import load_file
from backend.models.replacement_models import verify_weights

SHA256 = 'b89f36275f3bf5e2b040eee36597a8f19db051bff9a473a9cf7b2466284fb387'
REVISION = '6076002bf0d9dd37537f965ee2f06f826c333b61'

class WholeImageDetector(nn.Module):
    def __init__(self):
        super().__init__()
        import timm
        self.vit = timm.create_model('vit_small_patch16_384.augreg_in21k_ft_in1k', pretrained=False)
        self.vit.head = nn.Linear(384, 1)

    def forward(self, images):
        return self.vit(images)

    @staticmethod
    def preprocess(image):
        from torchvision import transforms as T
        return T.Compose([T.Resize(440), T.CenterCrop(384), T.ToTensor(),
                          T.Normalize([.485,.456,.406],[.229,.224,.225])])(image.convert('RGB'))

def load_whole_image(device):
    from backend.models.weight_registry import local_weight, private_weight, WHOLE_IMAGE_FILE
    path = local_weight(WHOLE_IMAGE_FILE)
    if not path:
        # Retain an already downloaded verified local copy without another download.
        candidate = Path(__file__).resolve().parents[2]/'model_weights/video/community_forensics/model.safetensors'
        path = str(candidate) if candidate.is_file() else private_weight(WHOLE_IMAGE_FILE)
    verify_weights(path, SHA256)
    with torch.device('meta'):
        model = WholeImageDetector()
    model.load_state_dict(load_file(path, device='cpu'), strict=True, assign=True)
    model = model.to(device).eval()
    model.metadata = dict(arch='vit_small_patch16_384', source='OwensLab/commfor-model-384',
                          revision=REVISION, weights_sha256=SHA256, score_calibrated=False)
    return model
