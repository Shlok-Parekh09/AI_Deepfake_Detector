"""Decode real small fixtures; do not load model weights or train."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image
import soundfile as sf

from backend.preprocessing.media_io import load_image, probe_media, run_ffmpeg, sample_video_frames
from backend.preprocessing.audio_waveform import read_waveform
from backend.utils.file_handler import FileHandler


class MediaDecodeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_image_formats_and_content_over_extension(self):
        for fmt, ext in [('PNG','png'),('JPEG','jpg'),('TIFF','tiff'),('BMP','bmp'),
                         ('GIF','gif'),('WEBP','webp'),('PPM','ppm'),('TGA','tga'),('PCX','pcx')]:
            with self.subTest(fmt=fmt):
                path = self.root / ('image.'+ext)
                Image.new('RGB',(40,30),(100,50,20)).save(path,format=fmt)
                self.assertEqual(probe_media(path),'image')
                self.assertEqual(load_image(path).size,(40,30))
        renamed = self.root/'image.mp3'
        shutil.copy(self.root/'image.png',renamed)
        self.assertEqual(probe_media(renamed),'image')

    def test_image_orientation(self):
        image = Image.new('RGB',(40,30))
        exif = Image.Exif(); exif[274] = 6
        path = self.root/'rotated.jpg'; image.save(path,exif=exif)
        self.assertEqual(load_image(path).size,(30,40))

    def make_audio(self):
        path = self.root/'speech.wav'
        wave = .1*np.sin(2*np.pi*220*np.arange(32000)/16000)
        sf.write(path,wave,16000)
        return path

    def test_audio_codecs_mislabeled_filename_and_video_container(self):
        original = self.make_audio()
        for ext, codec in [('flac','flac'),('aiff','pcm_s16be'),('opus','libopus'),
                           ('m4a','aac'),('mp3','libmp3lame')]:
            with self.subTest(ext=ext):
                path = self.root/('sound.'+ext)
                run_ffmpeg(['-i',str(original),'-c:a',codec,str(path)])
                self.assertEqual(probe_media(path),'audio')
                wave=read_waveform(path)
                self.assertTrue(np.isfinite(wave).all())
                self.assertGreaterEqual(len(wave),16000)
        renamed = self.root/'sound.mp4'
        shutil.copy(original,renamed)
        self.assertEqual(probe_media(renamed),'audio')

    def make_video(self, ext, codec):
        path=self.root/('clip.'+ext)
        run_ffmpeg(['-f','lavfi','-i','color=c=blue:s=64x48:r=4:d=2',
                    '-c:v',codec,'-pix_fmt','yuv420p',str(path)])
        return path

    def test_video_formats_and_renamed_file(self):
        for ext, codec in [('mp4','mpeg4'),('avi','mpeg4'),('mkv','ffv1'),('webm','libvpx-vp9')]:
            with self.subTest(ext=ext):
                path = self.make_video(ext,codec)
                self.assertEqual(probe_media(path),'video')
                frames=sample_video_frames(path,3)
                self.assertGreater(len(frames),0)
                self.assertLessEqual(len(frames),3)
                self.assertEqual(frames[0][1].shape[2],3)
        renamed=self.root/'video.jpg'
        shutil.copy(self.root/'clip.mp4',renamed)
        self.assertEqual(probe_media(renamed),'video')

    def test_video_falls_back_when_opencv_cannot_open(self):
        path=self.make_video('mkv','ffv1')
        capture=Mock(); capture.isOpened.return_value=False
        with patch('cv2.VideoCapture',return_value=capture):
            frames=sample_video_frames(path,3)
        self.assertGreater(len(frames),0)
        self.assertLessEqual(len(frames),3)
        capture.release.assert_called_once()

    def test_corrupt_empty_oversize_and_silent_files_rejected(self):
        handler=FileHandler(); self.addCleanup(handler.cleanup)
        path=self.root/'corrupt.mp3'; path.write_bytes(b'not audio')
        self.assertFalse(handler.validate_file(str(path))['valid'])
        path.write_bytes(b'')
        self.assertIn('empty',handler.validate_file(str(path))['error'])
        path=self.make_audio()
        self.assertFalse(handler.validate_file(str(path),max_size_mb=0)['valid'])
        sf.write(path,np.zeros(16000),16000)
        with self.assertRaisesRegex(ValueError,'silent'):
            read_waveform(path)

    def test_attached_cover_art_is_not_a_video(self):
        result=Mock(returncode=0,stdout=b'{"streams":[{"codec_type":"video","disposition":{"attached_pic":1}},{"codec_type":"audio"}]}')
        path=self.root/'audio.bin'; path.write_bytes(b'invalid pillow image')
        with patch('backend.preprocessing.media_io.shutil.which',return_value='ffprobe'), \
             patch('backend.preprocessing.media_io.subprocess.run',return_value=result):
            self.assertEqual(probe_media(path),'audio')


if __name__ == '__main__': unittest.main()
