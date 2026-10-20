import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
import torch
from PIL import Image
from backend.inference.predictor import Predictor
from backend.inference.postprocessing import PostProcessor

class Head(torch.nn.Module):
    def __init__(self, value=.8):
        super().__init__(); self.value=value
        self.metadata={'arch':'vit_small_patch16_384','weights_sha256':'fixture'}
    def preprocess(self, image): return torch.zeros(3,384,384)
    def forward(self, image): return torch.tensor([[np.log(self.value/(1-self.value))]])

class RoutingTests(unittest.TestCase):
    def predictor(self):
        p=Predictor.__new__(Predictor);p.device=torch.device('cpu');p.postprocessor=PostProcessor()
        p.face_detector=SimpleNamespace(extract_faces=lambda *args,**kw:[])
        p.video_metadata={'arch':'gend_clip_l14'}
        p.video_model=SimpleNamespace(faces=lambda *args,**kw:[])
        p.whole_image_model=Head()
        return p

    def test_no_face_image_uses_whole_image_head(self):
        p=self.predictor()
        with patch('backend.preprocessing.media_io.load_image',return_value=Image.new('RGB',(100,100))):
            result=p.predict_image('nonexistent-fixture.png')
        self.assertTrue(result['is_fake']);self.assertEqual(result['num_faces_analysed'],0)
        self.assertEqual(result['detector_metadata']['arch'],'vit_small_patch16_384')

    def test_multiple_image_faces_are_not_averaged_away(self):
        p=self.predictor();faces=[np.zeros((8,8,3),dtype=np.uint8)]*2
        p.face_detector.extract_faces=lambda _:faces
        p.preprocessor=SimpleNamespace(preprocess=lambda _:torch.zeros(1,3,8,8))
        values=iter([torch.tensor([[3.,0.]]),torch.tensor([[0.,3.]])])
        p.model=lambda _:next(values)
        with patch('backend.preprocessing.media_io.load_image',return_value=Image.new('RGB',(100,100))):
            result=p.predict_image('nonexistent-fixture.png')
        self.assertEqual(result['num_faces_analysed'],2);self.assertTrue(result['is_fake'])
        self.assertEqual(len(result['image_face_scores']),2)

    def test_no_face_video_uses_sampled_whole_frame_head(self):
        p=self.predictor()
        with patch('backend.preprocessing.media_io.sample_video_frames',return_value=[(0,np.zeros((16,16,3),dtype=np.uint8)),(10,np.zeros((16,16,3),dtype=np.uint8))]):
            result=p.predict_video('fixture.mp4')
        self.assertTrue(result['is_fake']);self.assertEqual(result['frames_analysed'],2)
        self.assertEqual(result['num_faces_analysed'],0)
        self.assertIn('No motion',result['analysis_scope'])

    def test_video_scores_both_faces_with_existing_model(self):
        p=self.predictor(); crops=[np.zeros((8,8,3),dtype=np.uint8)]*2
        values=iter([torch.tensor([[3.,0.]]),torch.tensor([[0.,3.]])])
        class FaceModel:
            def faces(self,*args,**kwargs):
                self.requested=kwargs['max_faces'];return crops
            def preprocess(self,_):return torch.zeros(3,8,8)
            def __call__(self,_):return next(values)
        p.video_model=FaceModel()
        with patch('backend.preprocessing.media_io.sample_video_frames',return_value=[(0,np.zeros((16,16,3),dtype=np.uint8))]):
            result=p.predict_video('fixture.mp4')
        self.assertEqual(p.video_model.requested,16)
        self.assertEqual(result['num_faces_analysed'],2)
        self.assertEqual(len(result['video_frame_scores'][0]['face_scores']),2)
        self.assertTrue(result['is_fake'])

if __name__=='__main__':unittest.main()
