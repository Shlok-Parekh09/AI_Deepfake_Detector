import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import numpy as np
import soundfile as sf
import torch
from backend.training.kaggle_native_audio import AudioNet, admit, crop, decode, inventory, label_for, finite_gradient_step
from backend.scripts.build_kaggle_native_audio import build


class NativeAudioTests(unittest.TestCase):
    def test_labels_partitions_and_conflicts(self):
        source = dict(folder_labels={'real':0, 'synthetic':1}, exclude_folders=['test'])
        self.assertEqual(label_for(source, 'train/synthetic/a.wav'), 1)
        self.assertEqual(label_for(source, 'REAL/a.wav'), 0)
        self.assertIsNone(label_for(source, 'test/real/a.wav'))
        with self.assertRaises(ValueError): label_for(source, 'unknown/a.wav')
        with self.assertRaises(ValueError): label_for(source, 'real/synthetic/a.wav')

    def test_decode_dedup_short_and_model(self):
        torch.set_num_threads(2)
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/'audio.wav'
            sf.write(p, np.sin(np.arange(32000)*.05)*.4, 16000)
            row = ('a', str(p), 0, 'source')
            wave, digest, error = decode(row)
            self.assertIsNone(error)
            db = sqlite3.connect(':memory:')
            db.execute('CREATE TABLE hashes(digest TEXT PRIMARY KEY,owner TEXT,label INTEGER,split TEXT,source TEXT)')
            db.execute('CREATE TABLE exclusions(owner TEXT PRIMARY KEY,reason TEXT)')
            self.assertIn(admit(db, row, digest), ('train','valid'))
            self.assertIsNone(admit(db, ('b',str(p),0,'other'), digest))
            with self.assertRaises(ValueError): admit(db, ('c',str(p),1,'other'), digest)
            with torch.inference_mode():
                result = AudioNet().eval()(torch.from_numpy(crop(wave, False)[None]))
            self.assertEqual(tuple(result.shape), (1, 2))
            self.assertTrue(torch.isfinite(result).all())
            sf.write(p, np.ones(8000)*.1, 16000)
            self.assertEqual(decode(row)[2], 'shorter_than_one_second')

    def test_notebook_self_contained(self):
        folder = build()
        nb = json.loads((folder/'training.ipynb').read_text())
        for cell in nb['cells']:
            if cell['cell_type']=='code': compile(''.join(cell['source']), 'notebook', 'exec')
        meta = json.loads((folder/'kernel-metadata.json').read_text())
        self.assertEqual(len(meta['dataset_sources']), 15)
        self.assertFalse(meta['kernel_sources'])
        spec = json.loads((Path(__file__).parent/'kaggle_native_sources.json').read_text())
        self.assertEqual(len(spec['sources']), 15)
        self.assertEqual(next(s for s in spec['sources'] if 'voxceleb2' in s['id'])['label'], 0)
        self.assertFalse(meta['enable_internet'])
        self.assertTrue(meta['is_private'])

    def test_nonfinite_gradients_never_update_optimizer(self):
        from unittest.mock import Mock
        model = torch.nn.Linear(2, 2)
        optimizer = Mock()
        optimizer.zero_grad.side_effect = lambda **kw: model.zero_grad(set_to_none=True)
        handle = model.weight.register_hook(lambda g: torch.full_like(g, float('inf')))
        with self.assertRaisesRegex(RuntimeError, 'Persistent nonfinite'):
            finite_gradient_step(model, optimizer, torch.nn.CrossEntropyLoss(), torch.ones(2, 2), torch.tensor([0, 1]))
        optimizer.step.assert_not_called()
        handle.remove()

    def test_constant_feature_pooling_has_finite_derivative(self):
        x = torch.ones(2, 3, 4, requires_grad=True)
        (x.var(2, unbiased=False)+1e-5).sqrt().sum().backward()
        self.assertTrue(torch.isfinite(x.grad).all())


if __name__ == '__main__': unittest.main()
