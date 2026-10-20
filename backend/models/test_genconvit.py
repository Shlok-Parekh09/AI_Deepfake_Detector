"""Check dedicated video routing without loading weights or training."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import cv2
import numpy as np
import torch
from backend.inference.predictor import Predictor
from backend.inference.postprocessing import PostProcessor


class VideoRoutingTests(unittest.TestCase):
    def check_clip(self,has_faces):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sample.avi'
            writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),2.,(32,32))
            self.assertTrue(writer.isOpened())
            for _ in range(2): writer.write(np.full((32,32,3),100,dtype=np.uint8))
            writer.release()
            detector=Predictor.__new__(Predictor)
            detector.device=torch.device('cpu')
            detector.postprocessor=PostProcessor(.5)
            detector.video_model=lambda x:torch.tensor([[0.,2.]])
            detector.face_detector=SimpleNamespace(extract_faces=lambda image,margin:[image] if has_faces else [])
            if has_faces:
                result=detector.predict_video(str(path))
                self.assertEqual(result['label'],'FAKE')
                self.assertIn('genconvit_vae',result['raw_scores'])
                self.assertEqual(result['frames_analysed'],2)
                expected = float(torch.sigmoid(torch.tensor(2.)))
                self.assertAlmostEqual(result['fake_probability'],expected/(.5+expected),places=4)
                self.assertFalse(result['score_calibrated'])
            else:
                with self.assertRaisesRegex(ValueError,'No face was detected'):
                    detector.predict_video(str(path))

    def test_video_uses_its_own_model(self): self.check_clip(True)
    def test_no_face_is_not_a_real_prediction(self): self.check_clip(False)

    def test_reference_sigmoid_aggregation_can_differ_from_softmax(self):
        # Old averaging predicts FAKE for these logits; reference sigmoid means predict REAL.
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sample.avi'
            writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),2.,(32,32))
            self.assertTrue(writer.isOpened())
            for _ in range(2): writer.write(np.full((32,32,3),100,dtype=np.uint8))
            writer.release()
            detector=Predictor.__new__(Predictor)
            detector.device=torch.device('cpu'); detector.postprocessor=PostProcessor(.5)
            logits=torch.tensor([[-10.,-8.],[2.,1.]])
            iterator=iter(logits)
            detector.video_model=lambda x: next(iterator).unsqueeze(0)
            detector.face_detector=SimpleNamespace(extract_faces=lambda image,margin:[image])
            self.assertGreater(float(logits.softmax(-1)[:,1].mean()),.5)
            result=detector.predict_video(str(path))
            self.assertEqual(result['label'],'REAL')
            expected=logits.sigmoid().mean(0)
            self.assertAlmostEqual(result['p_fake'],float(expected[1]/expected.sum()),places=6)

if __name__=='__main__': unittest.main()
