"""Build a manually launched notebook that resumes its attached private checkpoint."""
import json
from backend.scripts.build_kaggle_native_audio import build, ROOT

KERNEL = 'shlokparekh08/audio-native15-auto-resume'

def prepare():
    base = build()
    nb = json.loads((base/'training.ipynb').read_text())
    spec = json.loads((ROOT/'backend/training/kaggle_native_sources.json').read_text())
    nb['cells'][0]['source'] = ['# Native15 continuation — 15 total epochs\n',
        'The private continuation dataset is attached as a Kaggle input. Save & Run All verifies its hash and restores model, optimizer, duplicate ledger, random state and next-file cursor before training. '
        'A missing or outdated checkpoint stops before training. Enable KAGGLE_API_TOKEN and Internet for checking and publishing checkpoint metadata. '
        'No Hugging Face code or downloads. Each session trains for at most eight hours; wait at least one hour before manually starting another.\n']
    helper = (ROOT/'backend/training/native_audio_autoresume.py').read_text()
    nb['cells'][-1]['source'] = (helper+'\nSPEC = '+repr(spec)+'\nautomatic_run(SPEC)\n').splitlines(True)
    folder = ROOT/'audio_kaggle_run/native15_autoresume'; folder.mkdir(parents=True, exist_ok=True)
    (folder/'training.ipynb').write_text(json.dumps(nb, indent=2))
    (folder/'training.py').write_text('\n\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code'), encoding='utf-8')
    meta = json.loads((base/'kernel-metadata.json').read_text())
    meta.update(id=KERNEL, title='Audio Native15 Auto Resume', enable_internet=True,
                dataset_sources=list(dict.fromkeys(meta['dataset_sources'] + ['shlokparekh08/native15-continuation-state'])),
                kernel_sources=[])
    (folder/'kernel-metadata.json').write_text(json.dumps(meta, indent=2))
    return folder

if __name__=='__main__': print(prepare())
