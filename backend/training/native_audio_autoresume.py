"""Resume the fresh native15 run from its attached private Kaggle dataset."""
STORE = 'shlokparekh08/native15-continuation-state'
TARGET_EPOCHS = 15
EXPECTED_CORPUS = '7e9bfef6cabc8c2dcd86060cb2dd6352269487ba62928effbba486b7252953dc'


def read_remote_handoff(api, directory):
    import json
    from pathlib import Path
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory/'handoff.json'
    if path.exists():
        path.unlink()
    api.dataset_download_file(STORE, 'handoff.json', path=str(directory), force=True, quiet=True)
    return json.loads(path.read_text())


def publish_checkpoint(api, work, expected, parent_sha, attempts=3, checks=40, pause=15):
    """Confirm the served manifest; an accepted upload alone is not success."""
    import tempfile
    import time
    with tempfile.TemporaryDirectory(prefix='checkpoint_verify_') as verification:
        for attempt in range(attempts):
            current = read_remote_handoff(api, verification)
            if current == expected:
                return
            if current.get('sha256') != parent_sha:
                raise RuntimeError('Remote checkpoint changed; refusing to overwrite another run')
            try:
                response = api.dataset_create_version(str(work), 'Saved native15 continuation checkpoint',
                    quiet=True, convert_to_csv=False, delete_old_versions=False)
                if getattr(response, 'error', None):
                    raise RuntimeError('Checkpoint publication rejected')
            except Exception:
                # A request may succeed server-side even if its response is lost.
                log('checkpoint_upload_response_uncertain', attempt=attempt+1)
            for check in range(checks):
                try:
                    if str(api.dataset_status(STORE)).lower() == 'ready':
                        current = read_remote_handoff(api, verification)
                        if current == expected:
                            return
                        if current.get('sha256') not in (parent_sha, expected['sha256']):
                            raise RuntimeError('Remote checkpoint changed during publication')
                except RuntimeError:
                    raise
                except Exception:
                    pass
                log('checkpoint_publication_wait', attempt=attempt+1, check=check+1)
                time.sleep(pause)
        raise RuntimeError('Checkpoint update not verified; recovery checkpoint remains in notebook outputs')


def validate_continuation(state):
    if state.get('fingerprint') != EXPECTED_CORPUS:
        raise RuntimeError('Checkpoint is not from the authorized fresh 15-dataset experiment')
    if state.get('phase') or state.get('parent_progress'):
        raise RuntimeError('Unexpected checkpoint lineage; automatic resume refused')
    if not isinstance(state.get('epoch'), int) or not isinstance(state.get('cursor'), int):
        raise RuntimeError('Invalid checkpoint progress')
    if state['epoch'] < 0 or state['cursor'] < 0:
        raise RuntimeError('Negative checkpoint progress')
    return state['epoch'] >= TARGET_EPOCHS


def automatic_run(spec):
    import hashlib
    import json
    import os
    from pathlib import Path
    import shutil
    import time
    import zipfile
    import torch

    log('resume_bootstrap_started', checkpoint_source='attached Kaggle input', store=STORE)
    mount = Path('/kaggle/input')
    roots = [mount/STORE.split('/')[-1], *mount.glob('datasets/*/'+STORE.split('/')[-1])]
    checkpoint_root = next((root for root in roots if (root/'checkpoint.bin').is_file()), roots[0])
    checkpoint = checkpoint_root / 'checkpoint.bin'
    handoff_path = checkpoint_root / 'handoff.json'
    if not checkpoint.is_file() or not handoff_path.is_file():
        raise RuntimeError('Attached continuation checkpoint is missing; stopping before GPU training')
    log('checkpoint_files_found', checkpoint_bytes=checkpoint.stat().st_size)
    handoff = json.loads(handoff_path.read_text())
    if handoff.get('blocked'):
        raise RuntimeError('Previous session failed; checkpoint retained, repair required')
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest() != handoff.get('sha256'):
        raise RuntimeError('Attached checkpoint checksum mismatch; stopping before GPU training')
    log('checkpoint_checksum_verified')
    with zipfile.ZipFile(checkpoint) as archive:
        if archive.testzip() is not None or not {'state.pt', 'ledger.sqlite'}.issubset(archive.namelist()):
            raise RuntimeError('Attached checkpoint archive is incomplete or corrupt')
        with archive.open('state.pt') as source:
            saved = torch.load(source, map_location='cpu', weights_only=False)
    state = saved['state']
    done = validate_continuation(state)
    if state != handoff.get('state'):
        raise RuntimeError('Checkpoint and handoff progress do not match')
    del saved
    log('automatic_checkpoint_selected', epoch=state['epoch'], cursor=state['cursor'], complete=done)
    if done:
        log('target_already_complete', full_epochs=state['epoch'], training_started=False)
        return
    if time.time() < handoff.get('next_eligible_start', 0):
        log('cooldown_active', training_started=False)
        return

    from kaggle_secrets import UserSecretsClient
    log('checkpoint_api_preflight_started')
    os.environ['KAGGLE_API_TOKEN'] = UserSecretsClient().get_secret('KAGGLE_API_TOKEN')
    os.environ['KAGGLE_USERNAME'] = 'shlokparekh08'
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    import tempfile
    with tempfile.TemporaryDirectory(prefix='checkpoint_preflight_') as verification:
        current = read_remote_handoff(api, verification)
    if current != handoff:
        raise RuntimeError('Attached checkpoint is outdated. Update its Kaggle input version before running')
    log('checkpoint_preflight_passed_starting_inventory')
    error = None
    try:
        run(spec, resume=checkpoint, epochs=TARGET_EPOCHS, hours=8)
    except Exception as exc:
        error = type(exc).__name__
        raise
    finally:
        output = Path('/kaggle/working/audio_native')
        latest, progress = output/'last_checkpoint.zip', output/'progress.json'
        if not latest.is_file() or not progress.is_file():
            raise RuntimeError('No new checkpoint available; attached source checkpoint remains intact')
        next_state = json.loads(progress.read_text())
        validate_continuation(next_state)
        if (next_state['epoch'], next_state['cursor']) < (state['epoch'], state['cursor']):
            raise RuntimeError('Checkpoint progress regressed; refusing publication')
        with zipfile.ZipFile(latest) as archive:
            if archive.testzip() is not None or 'ledger.sqlite' not in archive.namelist():
                raise RuntimeError('New checkpoint is corrupt or missing its duplicate ledger')
            with archive.open('state.pt') as source:
                saved = torch.load(source, map_location='cpu', weights_only=False)
            if saved['state'] != next_state:
                raise RuntimeError('New checkpoint progress does not match its report')
            if not all(bool(torch.isfinite(value).all()) for value in saved['model'].values()):
                raise RuntimeError('New checkpoint has nonfinite model weights; refusing publication')
            del saved
        work = Path('/kaggle/temp/native15_handoff')
        work.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(latest, work/'checkpoint.bin')
        next_handoff = dict(
            sha256=hashlib.sha256((work/'checkpoint.bin').read_bytes()).hexdigest(),
            state=next_state, blocked=bool(error), error_type=error,
            next_eligible_start=time.time()+3600)
        (work/'handoff.json').write_text(json.dumps(next_handoff))
        (work/'dataset-metadata.json').write_text(json.dumps(dict(
            id=STORE, title='Native15 Continuation State',
            licenses=[{'name':'CC0-1.0'}])))
        log('checkpoint_upload_started', epoch=next_state['epoch'], cursor=next_state['cursor'])
        publish_checkpoint(api, work, next_handoff, handoff['sha256'])
        log('checkpoint_update_verified', epoch=next_state['epoch'],
            cursor=next_state['cursor'], blocked=bool(error))
