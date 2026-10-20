"""Multilingual waveform encoder with attentive statistics pooling."""
from __future__ import annotations
import torch
from torch import nn


class AudioSSL(nn.Module):
    def __init__(self, encoder_name="facebook/wav2vec2-xls-r-300m", encoder_config=None,
                 pretrained=True, unfreeze_layers=4, spectral_residual=False):
        super().__init__()
        from transformers import Wav2Vec2Config, Wav2Vec2Model
        if pretrained:
            from pathlib import Path
            self.encoder = Wav2Vec2Model.from_pretrained(encoder_name,local_files_only=Path(encoder_name).is_dir())
        else:
            self.encoder = Wav2Vec2Model(Wav2Vec2Config(**encoder_config))
        self.encoder_name = encoder_name
        self.encoder.freeze_feature_encoder()
        for parameter in self.encoder.parameters(): parameter.requires_grad = False
        for layer in list(self.encoder.encoder.layers)[-unfreeze_layers:] if unfreeze_layers else []:
            for parameter in layer.parameters(): parameter.requires_grad = True
        dim = self.encoder.config.hidden_size
        self.attention = nn.Sequential(nn.Linear(dim, 128), nn.Tanh(), nn.Linear(128, 1))
        self.classifier = nn.Sequential(nn.LayerNorm(dim * 2), nn.Linear(dim * 2, 256),
                                        nn.GELU(), nn.Dropout(.3), nn.Linear(256, 2))
        if spectral_residual:
            from backend.models.audio_spectral import SpectralResidual
            self.spectral = SpectralResidual()

    def forward(self, waveform, attention_mask=None):
        hidden = self.encoder(waveform, attention_mask=attention_mask).last_hidden_state
        scores = self.attention(hidden).squeeze(-1)
        if attention_mask is not None:
            valid = self.encoder._get_feature_vector_attention_mask(hidden.shape[1], attention_mask)
            scores = scores.masked_fill(~valid, torch.finfo(scores.dtype).min)
        weights = scores.softmax(dim=1).unsqueeze(-1)
        mean = (hidden * weights).sum(dim=1)
        std = ((hidden - mean[:, None]).square() * weights).sum(dim=1).clamp_min(1e-5).sqrt()
        logits=self.classifier(torch.cat([mean, std], dim=-1))
        if hasattr(self,'spectral'): logits=logits+self.spectral(waveform,attention_mask)
        return logits


def load_audio_checkpoint(path, device):
    if str(path).endswith('.safetensors'):
        if 'spectra_aasist3' in str(path).lower():
            from backend.models.replacement_models import load_spectra
            return load_spectra(path, device)
        from backend.models.antideepfake import load_antideepfake
        return load_antideepfake(path, device)
    state = torch.load(path, map_location="cpu", weights_only=False, mmap=True)
    meta = state.get("metadata", {})
    if meta.get("arch") == "audio_ssl":
        # Build shapes on the meta device, then attach trained tensors directly.
        # Avoid allocating and initializing a second 1.2 GB copy on startup.
        with torch.device('meta'):
            model = AudioSSL(meta["encoder_name"], meta["encoder_config"], pretrained=False, unfreeze_layers=0,
                             spectral_residual=meta.get('spectral_residual',False))
    else:
        from backend.models.audio_model import AudioCNN
        model = AudioCNN(pretrained=False)
    weights = state.get("model_state_dict", state)
    model.load_state_dict({k.removeprefix("module."): v for k, v in weights.items()}, assign=True)
    return model.to(device).eval(), meta
