import unittest
import torch
from backend.models.audio_spectral import SpectralResidual


class SpectralTests(unittest.TestCase):
    @torch.inference_mode()
    def test_frequency_sensitivity_and_padding_invariance(self):
        t=torch.arange(16000)/16000
        a=torch.sin(2*torch.pi*440*t)
        b=torch.sin(2*torch.pi*3000*t)
        features=SpectralResidual.features(torch.stack([a,b]))
        self.assertEqual(tuple(features.shape),(2,384))
        self.assertTrue(torch.isfinite(features).all())
        self.assertFalse(torch.allclose(features[0],features[1]))
        padded=torch.nn.functional.pad(a,(0,8000))[None]
        mask=torch.cat([torch.ones(16000),torch.zeros(8000)])[None]
        torch.testing.assert_close(features[:1],SpectralResidual.features(padded,mask))

    @torch.inference_mode()
    def test_initial_residual_preserves_old_logits_and_silence_is_finite(self):
        residual=SpectralResidual()
        output=residual(torch.zeros(2,16000))
        torch.testing.assert_close(output,torch.zeros(2,2))
        with self.assertRaises(ValueError): residual(torch.zeros(1,16000),torch.zeros(1,16000))

if __name__=='__main__':unittest.main()
