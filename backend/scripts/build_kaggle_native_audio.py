"""Build a readable, standalone notebook with exactly fourteen mounted audio sources."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KERNEL = 'shlokparekh08/audio-native-waveform-15-fp32-v3'
PARENT = 'shlokparekh08/audio-native-waveform-14-v1'
CHECKPOINT_DATASET = 'shlokparekh08/native-audio14-recovery-checkpoint'


def build():
    spec = json.loads((ROOT/'backend/training/kaggle_native_sources.json').read_text())
    assert len(spec['sources']) == 15 and all(s['provider'] == 'kaggle' for s in spec['sources'])
    source = (ROOT/'backend/training/kaggle_native_audio.py').read_text()
    imports = [n for n in ast.walk(ast.parse(source)) if isinstance(n, (ast.Import, ast.ImportFrom))]
    forbidden = ('transformers', 'huggingface_hub', 'datasets')
    for node in imports:
        names = [node.module or ''] if isinstance(node, ast.ImportFrom) else [n.name for n in node.names]
        assert not any(name.split('.')[0] in forbidden for name in names)
    cells = []
    def cell(kind, text):
        item = dict(cell_type=kind, metadata={}, source=text.splitlines(True))
        if kind == 'code': item.update(execution_count=None, outputs=[])
        cells.append(item)
    cell('markdown', '# Native audio waveform training\n\nFifteen mounted Kaggle audio datasets. Fresh FP32 waveform and Fourier detector; no prior checkpoint loaded. '
         'No network access, package installation or external encoder. Real=0; Fake=1. '
         'Twenty full passes are the target, across resumable sessions. '
         'Checkpoint ZIPs contain matching model, optimizer, random state and duplicate ledger. '
         'Internal recording holdout does not establish unseen-speaker or unseen-generator accuracy.\n')
    cell('code', "print('Notebook execution started: checking installed audio libraries', flush=True)\n"+source)
    cell('code', 'SPEC = '+repr(spec)+"\nrun(SPEC, epochs=20, hours=8, resume=None)\n")
    folder = ROOT/'audio_kaggle_run/native_waveform15_fp32'
    folder.mkdir(parents=True, exist_ok=True)
    nb = dict(cells=cells, nbformat=4, nbformat_minor=5,
              metadata={'kernelspec': {'display_name':'Python 3', 'language':'python', 'name':'python3'}})
    for i, c in enumerate(cells): c['id'] = f'cell-{i}'
    path = folder/'training.ipynb'
    path.write_text(json.dumps(nb, indent=2), encoding='utf-8')
    metadata = dict(id=KERNEL, title='Audio Native Waveform 15 FP32 V3', code_file=path.name, language='python',
                    kernel_type='notebook', is_private=True, enable_gpu=True, enable_internet=False,
                    dataset_sources=[s['id'] for s in spec['sources']], kernel_sources=[],
                    model_sources=[], competition_sources=[])
    (folder/'kernel-metadata.json').write_text(json.dumps(metadata, indent=2))
    return folder


if __name__ == '__main__':
    print(build())
