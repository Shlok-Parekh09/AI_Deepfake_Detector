"""Multi-resolution short-time Fourier features for a learned residual head."""
import torch
from torch import nn
from torch.nn import functional as F


class SpectralResidual(nn.Module):
    def __init__(self):
        super().__init__()
        self.head=nn.Sequential(nn.LayerNorm(384),nn.Linear(384,128),nn.GELU(),nn.Linear(128,2))
        # Preserve the pretrained waveform model's initial predictions exactly.
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)

    @staticmethod
    def features(waveform,attention_mask=None):
        rows=[]
        # Exclude padding before the STFT so duration padding is not a cue.
        with torch.autocast(device_type=waveform.device.type,enabled=False):
            for i,raw in enumerate(waveform.float()):
                length=int(attention_mask[i].sum().item()) if attention_mask is not None else len(raw)
                if length<=0: raise ValueError('Spectral input has no valid samples')
                wave=raw[:length]
                wave=wave-wave.mean()
                wave=wave/wave.square().mean().sqrt().clamp_min(1e-6)
                features=[]
                for size in (256,512,1024):
                    padded=F.pad(wave,(0,max(0,size-len(wave))))
                    window=torch.hann_window(size,device=wave.device)
                    spectrum=torch.stft(padded,n_fft=size,hop_length=size//4,window=window,
                                        center=False,return_complex=True)
                    log_power=torch.log1p(spectrum.abs().square()/size)
                    for stat in (log_power.mean(-1),log_power.std(-1,unbiased=False)):
                        features.append(F.adaptive_avg_pool1d(stat[None,None],64).flatten())
                rows.append(torch.cat(features))
        return torch.stack(rows)

    def forward(self,waveform,attention_mask=None):
        return self.head(self.features(waveform,attention_mask))
