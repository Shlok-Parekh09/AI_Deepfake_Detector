"""Publish the verified fresh experiment checkpoint, never overwrite a store."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
import torch
from backend.training.native_audio_autoresume import STORE, validate_continuation
from backend.scripts.kaggle_credentials import credentials

def main():
    checkpoint = Path('audio_kaggle_run/native15_completed_report/audio_native/last_checkpoint.zip')
    with zipfile.ZipFile(checkpoint) as archive:
        if archive.testzip():
            raise RuntimeError('Checkpoint archive corruption')
        assert 'ledger.sqlite' in archive.namelist()
        with archive.open('state.pt') as stream:
            saved = torch.load(stream, map_location='cpu', weights_only=False)
    state = saved['state']; validate_continuation(state)
    assert all(torch.isfinite(v).all() for v in saved['model'].values())
    assert saved['optimizer']['state']
    print(json.dumps({'verified_epoch':state['epoch'], 'verified_cursor':state['cursor'], 'counts':state['counts']}))
    credentials()
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi(); api.authenticate()
    existing = api.dataset_list(mine=True, search=STORE.split('/')[-1])
    if any(str(item.ref) == STORE for item in existing):
        print('Checkpoint store already exists; not overwritten'); return
    folder = Path('audio_kaggle_run/native15_checkpoint_seed'); folder.mkdir(exist_ok=True)
    shutil.copyfile(checkpoint, folder/'checkpoint.bin')
    (folder/'handoff.json').write_text(json.dumps(dict(sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(), state=state, blocked=False, next_eligible_start=0)))
    (folder/'dataset-metadata.json').write_text(json.dumps(dict(id=STORE,title='Native15 Continuation State',licenses=[{'name':'CC0-1.0'}])))
    result=api.dataset_create_new(str(folder),public=False,quiet=True,convert_to_csv=False)
    if getattr(result,'error',None): raise RuntimeError('Checkpoint publication rejected')
    print('Private checkpoint store submitted')

if __name__ == '__main__': main()
