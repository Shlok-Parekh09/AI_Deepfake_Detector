"""Inference plumbing checks, not an accuracy benchmark."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import soundfile as sf
import torch

from backend.inference.predictor import Predictor


class MediaPredictionTests(unittest.TestCase):
    def test_audio_scores_are_input_specific_and_report_partial_coverage(self):
        predictor=Predictor.__new__(Predictor)
        predictor.device=torch.device('cpu'); predictor.threshold=.5
        predictor.audio_metadata={'arch':'antideepfake_mms_1b','seconds':1,'max_windows':2,'threshold':.5}
        # A deterministic surrogate verifies routing/aggregation; this is not a deepfake classifier.
        def surrogate(wave):
            value=(wave.diff().abs().mean()-.15)*20
            return torch.stack([-value,value]).unsqueeze(0)
        predictor.audio_model=surrogate
        with tempfile.TemporaryDirectory() as folder:
            results=[]
            for frequency in (100,2000):
                path=Path(folder)/f'{frequency}.wav'
                sf.write(path,.1*np.sin(2*np.pi*frequency*np.arange(80000)/16000),16000)
                results.append(predictor.predict_audio(str(path)))
            self.assertGreater(abs(results[0]['p_fake']-results[1]['p_fake']),.5)
            for result in results:
                self.assertEqual(result['audio_assessment']['analyzed_seconds'],2.)
                self.assertAlmostEqual(result['audio_assessment']['coverage_fraction'],.4)
                self.assertFalse(result['score_calibrated'])
                self.assertTrue(result['review_required'])

    def test_image_without_face_is_not_classified_by_compression(self):
        predictor=Predictor.__new__(Predictor)
        predictor.face_detector=SimpleNamespace(extract_faces=lambda image:[])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'plain.png'; Image.new('RGB',(40,30)).save(path)
            with self.assertRaisesRegex(ValueError,'No face was detected'):
                predictor.predict_image(str(path))

    def test_unsupported_upload_returns_422(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        predictor=SimpleNamespace(predict=lambda path:(_ for _ in ()).throw(ValueError('Unsupported codec')))
        with patch('backend.api.routes._get_predictor',return_value=predictor):
            response=TestClient(app).post('/api/v1/detect',files={'file':('broken.xyz',b'broken')})
        self.assertEqual(response.status_code,422)
        self.assertIn('Unsupported codec',response.json()['detail'])


if __name__=='__main__': unittest.main()
