"""GenConViT VAE inference, adapted from erprogs/GenConViT (MIT).

The original ConvNeXt forward never consumes its attached Swin/HybridEmbed.
Those unused entries are excluded explicitly; all active parameters load strictly.
See genconvit_LICENSE.txt for upstream attribution and license.
"""
import hashlib
import torch
from torch import nn

EXPECTED_SHA256='53c627c82d1439fc80e18ac462c1ed6969a3babe5376124a5c38d1c0c88c9042'


class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        layers=[]
        for a,b in [(3,16),(16,32),(32,64),(64,128)]:
            layers.extend([nn.Conv2d(a,b,3,stride=2,padding=1),nn.BatchNorm2d(b),nn.LeakyReLU()])
        self.features=nn.Sequential(*layers)
        self.fc1=nn.Linear(25088,256)
        self.fc2=nn.Linear(256,128)
        self.mu=nn.Linear(25088,12544)
        self.var=nn.Linear(25088,12544)

    def forward(self,x):
        mu=self.mu(self.features(x).flatten(1))
        # Preserve upstream sampling formula, with repeatable inference RNG.
        generator=torch.Generator(device=mu.device).manual_seed(0)
        eps=torch.randn(mu.shape,dtype=mu.dtype,device=mu.device,generator=generator)
        return eps*torch.exp(.5*mu)+mu


class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        layers=[]
        for a,b in [(256,64),(64,32),(32,16),(16,3)]:
            layers.extend([nn.ConvTranspose2d(a,b,2,stride=2),nn.LeakyReLU()])
        self.features=nn.Sequential(*layers)
        self.unflatten=nn.Unflatten(1,(256,7,7))

    def forward(self,x): return self.features(self.unflatten(x))


class GenConViTVAE(nn.Module):
    def __init__(self):
        super().__init__()
        import timm
        self.encoder=Encoder()
        self.decoder=Decoder()
        self.convnext_backbone=timm.create_model('convnext_tiny',pretrained=False,
            num_classes=1000,drop_path_rate=0.,head_init_scale=1.)
        self.fc=nn.Linear(2000,500)
        self.fc3=nn.Linear(1000,500)
        self.fc2=nn.Linear(500,2)
        self.relu=nn.ReLU()

    def forward(self,x):
        if x.ndim!=4 or tuple(x.shape[1:])!=(3,224,224):
            raise ValueError('GenConViT requires normalized RGB face crops sized 224x224')
        reconstructed=self.decoder(self.encoder(x))
        features=torch.cat([self.convnext_backbone(x),self.convnext_backbone(reconstructed)],dim=1)
        logits=self.fc2(self.relu(self.fc(self.relu(features))))
        return logits.flip(-1)  # Upstream [fake,real] -> application [real,fake].


def load_video_checkpoint(path,device):
    digest=hashlib.sha256()
    with open(path,'rb') as source:
        for chunk in iter(lambda:source.read(8*1024*1024),b''):digest.update(chunk)
    if digest.hexdigest()!=EXPECTED_SHA256:
        raise ValueError('Video weights do not match the configured architecture/labels')
    weights=torch.load(path,map_location='cpu',weights_only=True,mmap=True)
    selected={k:v for k,v in weights.items() if not k.startswith(('embedder.','convnext_backbone.patch_embed.'))}
    with torch.device('meta'):model=GenConViTVAE()
    model.load_state_dict(selected,strict=True,assign=True)
    return model.to(device).eval()
