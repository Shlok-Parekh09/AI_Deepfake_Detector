"""Report integrity and layout tests; these do not measure detector accuracy."""
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import soundfile as sf
from pypdf import PdfReader
from backend.reports.evidence import create_evidence, attach_report
from backend.reports.pdf import build_pdf


class ReportTests(unittest.TestCase):
    def test_signal_views_change_with_the_input_frequency(self):
        from backend.reports.evidence import _audio_evidence
        with tempfile.TemporaryDirectory() as folder:
            views = []
            for frequency in [300, 2200]:
                path = Path(folder)/f'{frequency}.wav'
                sf.write(path, .2*np.sin(2*np.pi*frequency*np.arange(32000)/16000), 16000)
                _, _, signal = _audio_evidence(path)
                matrix = np.asarray(signal['spectral_power'])
                self.assertEqual(matrix.shape, (160,720))
                self.assertEqual(len(signal['waveform_peaks']),720)
                self.assertEqual(signal['duration_seconds'],2.)
                views.append(int(matrix.mean(axis=1).argmax()))
            self.assertGreater(views[1], views[0]+20)

    def test_audio_report_uses_actual_hash_coverage_and_embedded_times(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'speech.wav'
            sf.write(path,.1*np.sin(np.arange(32000)*.1),16000)
            predictor=SimpleNamespace(audio_metadata={'arch':'spectra_aasist3','source':'test-fixture','revision':'test','weights_sha256':'a'*64})
            result={'file_type':'audio','is_fake':True,'audio_assessment':{'window_count':1,'analyzed_seconds':2.,'coverage_fraction':1.},'audio_segments':[{'start_seconds':0.,'end_seconds':2.,'fake_probability':.7}]}
            evidence=create_evidence(result,path,'name <not markup> & example.wav',predictor)
            self.assertEqual(evidence['coverage']['analyzed_seconds'],2.)
            self.assertAlmostEqual(float(evidence['metrics']['RMS amplitude'].split()[0]),.0707,places=3)
            pdf=build_pdf(evidence);reader=PdfReader(io.BytesIO(pdf))
            self.assertEqual(len(reader.pages),2)
            content='\n'.join(page.extract_text() for page in reader.pages)
            self.assertIn('not a certified forensic opinion',content)
            self.assertIn('causal pitch',content)
            self.assertIn('name <not markup> & example.wav',content)
            fonts=[font.get_object() for page in reader.pages for font in page['/Resources']['/Font'].values()]
            self.assertTrue(any('TimesNewRoman' in str(font.get('/BaseFont')) for font in fonts))
            original_hash=evidence['file_sha256'];path.write_bytes(path.read_bytes()+b'changed')
            self.assertNotEqual(original_hash,create_evidence(result,path,'speech.wav',predictor)['file_sha256'])

    def test_image_and_video_templates_stay_two_pages_and_unsigned(self):
        for kind in ['image','video']:
            evidence=dict(report_id='DFA-TEST',generated_at='2026-10-20T00:00:00+00:00',filename='test.'+kind,
                file_type=kind,file_bytes=100,file_sha256='b'*64,prediction='Real',model={'arch':'test','source':'fixture','revision':'r','weights_sha256':'a'*64},
                metrics={'Face crops assessed':'1'},decision_method='Test fixture, not an accuracy claim.',scope='Sampled faces only.')
            reader=PdfReader(io.BytesIO(build_pdf(evidence)))
            self.assertEqual(len(reader.pages),2)
            self.assertIn('unsigned',reader.pages[-1].extract_text())


if __name__=='__main__':unittest.main()
