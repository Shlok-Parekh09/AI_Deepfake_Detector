"""NII MMS-1B AntiDeepfake inference using its supplied Fairseq-layout weights.

Architecture/preprocessing: nii-yamagishilab/mms-1b-anti-deepfake,
revision e8574a77b9934a18383292678ac441cc495707b5. Weights: CC-BY-NC-SA-4.0.
The Transformers encoder uses the equivalent stable-layer-norm architecture;
pretraining-only quantizer/projection tensors are not used for detection.
"""
from pathlib import Path
import json
import re
import torch
from torch import nn

REPOSITORY = 'nii-yamagishilab/mms-1b-anti-deepfake'
REVISION = 'e8574a77b9934a18383292678ac441cc495707b5'
EXPECTED_SHA256 = 'b0f5511494b0e39f1ad649d8f78a8e94eaed5bae90519f26b405ddc54906d283'


def encoder_key(key):
    """Translate a Fairseq feature-encoder parameter to its Transformers name."""
    if key in ('proj_fc.weight', 'proj_fc.bias'):
        return key
    prefix = 'm_ssl.model.'
    if not key.startswith(prefix):
        raise ValueError('Unknown AntiDeepfake parameter: '+key)
    key = key[len(prefix):]
    if key.startswith(('quantizer.', 'project_q.', 'final_proj.')):
        return None
    if key == 'mask_emb': key = 'masked_spec_embed'
    elif key.startswith('post_extract_proj.'): key = key.replace('post_extract_proj.', 'feature_projection.projection.', 1)
    elif key.startswith('layer_norm.'): key = key.replace('layer_norm.', 'feature_projection.layer_norm.', 1)
    elif key.startswith('encoder.pos_conv.0.'):
        key = key.replace('encoder.pos_conv.0.', 'encoder.pos_conv_embed.conv.', 1)
        key = key.replace('weight_g', 'parametrizations.weight.original0').replace('weight_v', 'parametrizations.weight.original1')
    elif key.startswith('feature_extractor.conv_layers.'):
        match = re.fullmatch(r'feature_extractor\.conv_layers\.(\d+)\.(0|2\.1)\.(weight|bias)', key)
        if not match: raise ValueError('Unknown convolution parameter: '+key)
        layer, part, parameter = match.groups()
        key = f'feature_extractor.conv_layers.{layer}.{"conv" if part == "0" else "layer_norm"}.{parameter}'
    else:
        key = key.replace('.self_attn.', '.attention.')
        key = key.replace('.self_attn_layer_norm.', '.layer_norm.')
        key = key.replace('.fc1.', '.feed_forward.intermediate_dense.')
        key = key.replace('.fc2.', '.feed_forward.output_dense.')
    return 'encoder.'+key


class AntiDeepfake(nn.Module):
    def __init__(self, config):
        super().__init__()
        from transformers import Wav2Vec2Config, Wav2Vec2Model
        cfg = Wav2Vec2Config(**config)
        cfg._attn_implementation = 'eager'
        self.encoder = Wav2Vec2Model(cfg)
        self.proj_fc = nn.Linear(cfg.hidden_size, 2)

    def forward(self, waveform, attention_mask=None):
        if waveform.ndim != 2 or waveform.shape[1] < 400:
            raise ValueError('Expected a batch of 16 kHz speech waveforms')
        hidden = self.encoder(waveform, attention_mask=attention_mask).last_hidden_state
        if attention_mask is None:
            pooled = hidden.mean(dim=1)
        else:
            mask = self.encoder._get_feature_vector_attention_mask(hidden.shape[1], attention_mask)
            pooled = (hidden * mask.unsqueeze(-1)).sum(1) / mask.sum(1, keepdim=True).clamp_min(1)
        # Upstream is [fake, real]. The application contract is [real, fake].
        return self.proj_fc(pooled).flip(-1)


def load_antideepfake(path, device):
    import hashlib
    from safetensors import safe_open
    hasher = hashlib.sha256()
    with open(path, 'rb') as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b''): hasher.update(chunk)
    digest = hasher.hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError('Unrecognized AntiDeepfake safetensors checksum; refusing unknown architecture/label order')
    config = json.loads((Path(__file__).parent/'antideepfake_reference/config.json').read_text())
    with torch.device('meta'):
        model = AntiDeepfake(config)
    weights = {}
    with safe_open(str(path), framework='pt', device='cpu') as archive:
        for name in archive.keys():
            target = encoder_key(name)
            if target is not None:
                if target in weights: raise ValueError('Duplicate converted model parameter')
                weights[target] = archive.get_tensor(name)
    model.load_state_dict(weights, strict=True, assign=True)
    model = model.to(device).eval()
    from backend.models.weight_registry import PRIVATE_REPOSITORY
    storage_revision = next((p.name for p in Path(path).parents if p.parent.name == 'snapshots'), None)
    return model, dict(arch='antideepfake_mms_1b', seconds=10., max_windows=12,
        threshold=.5, temperature=1., aggregation='mean_window_probability',
        source=PRIVATE_REPOSITORY, revision=storage_revision, weights_sha256=digest,
        architecture_source=REPOSITORY, architecture_revision=REVISION, label_map={'real':0, 'fake':1},
        score_calibrated=False, evaluation={})
