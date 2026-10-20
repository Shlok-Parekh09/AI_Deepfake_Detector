"""Contracts that prevent inverted labels and incorrect audio preprocessing."""
import unittest
import numpy as np
import torch
from torch import nn
from backend.models.replacement_models import (
    SpectraDetector, SPECTRA_REAL_THRESHOLD, SPECTRA_SAMPLES, spectra_crop, GenDDetector,
)


class FixedLogits(nn.Module):
    def __init__(self, real):
        super().__init__()
        self.real = real

    def forward(self, wave):
        # An unrelated first logit must not change the published raw-logit decision.
        return torch.tensor([[100., self.real]])


class ReplacementContractTests(unittest.TestCase):
    def test_spectra_preserves_native_decision_and_app_class_order(self):
        for offset, fake in [(-.1,True),(.1,False)]:
            model = SpectraDetector(FixedLogits(SPECTRA_REAL_THRESHOLD + offset))
            logits = model(torch.zeros(1,10))
            self.assertEqual(bool(logits.softmax(-1)[0,1] > .5), fake)

    def test_preemphasis_precedes_crop_and_short_audio_is_tiled(self):
        wave = np.asarray([1.,2.,3.],dtype=np.float32)
        crop = spectra_crop(wave)
        self.assertEqual(crop.shape, (SPECTRA_SAMPLES,))
        np.testing.assert_allclose(crop[:6], [1.,1.03,1.06,1.,1.03,1.06],rtol=1e-6)
        self.assertAlmostEqual(float(spectra_crop(wave,1)[0]),1.03,places=5)

    def test_invalid_audio_is_rejected(self):
        for wave in [[],[np.nan]]:
            with self.assertRaises(ValueError): spectra_crop(wave)

    def test_clip_preprocessing_is_finite_and_has_expected_size(self):
        crop = GenDDetector.preprocess(np.full((300,240,3),128,dtype=np.uint8))
        self.assertEqual(tuple(crop.shape),(3,224,224))
        self.assertTrue(torch.isfinite(crop).all())

    def test_video_alignment_can_retain_multiple_faces(self):
        from types import SimpleNamespace
        landmarks = np.array([[[20,20],[40,20],[30,30],[23,40],[37,40]],
                              [[90,20],[110,20],[100,30],[93,40],[107,40]]],dtype=np.float32)
        detector = SimpleNamespace(detect=lambda _: (np.array([[10,10,50,50,.99],[80,10,120,50,.99]]),landmarks))
        adapter = SimpleNamespace(landmark_detector=detector)
        frame = np.zeros((150,150,3),dtype=np.uint8)
        self.assertEqual(len(GenDDetector.faces(adapter,frame)),1)
        self.assertEqual(len(GenDDetector.faces(adapter,frame,max_faces=16)),2)


if __name__ == '__main__': unittest.main()
