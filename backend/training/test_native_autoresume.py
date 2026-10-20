import unittest
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from backend.training import native_audio_autoresume as module
from backend.training.native_audio_autoresume import EXPECTED_CORPUS, validate_continuation

class ContinuationTests(unittest.TestCase):
    def state(self, **changes):
        return dict(fingerprint=EXPECTED_CORPUS, epoch=0, cursor=1042176, **changes)

    def test_partial_epoch_continues(self):
        self.assertFalse(validate_continuation(self.state()))

    def test_complete(self):
        state=self.state(); state['epoch']=15
        self.assertTrue(validate_continuation(state))

    def test_fourteen_epochs_not_complete(self):
        state=self.state(); state['epoch']=14
        self.assertFalse(validate_continuation(state))

    def test_wrong_corpus_and_lineage_rejected(self):
        for change in ({'fingerprint':'old'}, {'phase':'expanded'}, {'cursor':-1}):
            state=self.state(); state.update(change)
            with self.assertRaises(RuntimeError): validate_continuation(state)

    def test_publication_requires_served_manifest(self):
        expected={'sha256':'new','state':{'epoch':1}}
        class API:
            calls=0
            current={'sha256':'old'}
            def dataset_download_file(self, store, name, path, **kwargs):
                (Path(path)/name).write_text(json.dumps(self.current))
            def dataset_create_version(self, *args, **kwargs):
                self.calls += 1
                self.current=expected
                # Simulate accepted server update followed by a lost response.
                raise ConnectionError('lost response')
            def dataset_status(self, store): return 'ready'
        api=API()
        with patch.object(module,'log',create=True), tempfile.TemporaryDirectory() as folder:
            module.publish_checkpoint(api,folder,expected,'old',checks=1,pause=0)
        self.assertEqual(api.calls,1)

    def test_unconfirmed_upload_is_failure(self):
        class API:
            def dataset_download_file(self, store, name, path, **kwargs):
                (Path(path)/name).write_text(json.dumps({'sha256':'old'}))
            def dataset_create_version(self,*args,**kwargs): return SimpleNamespace(error=None)
            def dataset_status(self,store): return 'ready'
        with patch.object(module,'log',create=True), tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RuntimeError,'not verified'):
                module.publish_checkpoint(API(),folder,{'sha256':'new'},'old',attempts=1,checks=1,pause=0)

    def test_other_run_checkpoint_cannot_be_overwritten(self):
        class API:
            def dataset_download_file(self, store, name, path, **kwargs):
                (Path(path)/name).write_text(json.dumps({'sha256':'other-run'}))
            def dataset_create_version(self,*args,**kwargs):
                raise AssertionError('must not upload')
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RuntimeError,'refusing to overwrite'):
                module.publish_checkpoint(API(),folder,{'sha256':'new'},'old',pause=0)

if __name__ == '__main__': unittest.main()
