"""Small offline tests of model, masks, calibration, and checkpoint reconstruction."""
import tempfile
import unittest
import argparse
import json
import os
from unittest.mock import patch
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from transformers import Wav2Vec2Config
from backend.models.audio_ssl import AudioSSL, load_audio_checkpoint
from backend.preprocessing.audio_waveform import audio_windows, crop_tensor, window_starts
from backend.training.train_audio_ssl import calibrate, metrics
from backend.training.prepare_audio import folder_label, speaker_key


class AudioSSLTests(unittest.TestCase):
    @unittest.skipUnless(os.getenv("KAGGLE_KERNEL_RUN_TYPE") and torch.cuda.is_available(), "Training smoke test runs on Kaggle GPU only")
    def test_training_candidate_end_to_end(self):
        from backend.training.train_audio_ssl import train
        config = Wav2Vec2Config(hidden_size=16, num_hidden_layers=1, num_attention_heads=2,
            intermediate_size=32, conv_dim=(8, 8, 8), conv_stride=(5, 2, 2),
            conv_kernel=(10, 3, 3), num_conv_pos_embedding_groups=2,
            num_conv_pos_embeddings=16, mask_time_prob=0.)
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); rows = []
            for split in ("train", "validation", "calibration", "test", "external_test"):
                for label in (0, 1):
                    path = folder / f"{split}_{label}.wav"
                    sf.write(path, np.sin(np.arange(16000) * (.1 + label*.05)), 16000)
                    rows.append(dict(path=str(path), label=label, source="smoke", recording=path.stem,
                                     language="smoke", generator="smoke", sha256=path.stem, speakers=[], split=split))
            manifest = folder / "manifest.jsonl"
            manifest.write_text("".join(json.dumps(r)+"\n" for r in rows))
            args = argparse.Namespace(manifest=str(manifest), output=str(folder / "out"), seed=42,
                resume=False, encoder="tiny-offline", unfreeze_layers=1,
                seconds=.25, epochs=1, batch_size=2, accumulate=2, workers=0,
                samples_per_epoch=4, lr=1e-4, patience=2, target=.8)
            with patch("backend.training.train_audio_ssl.AudioSSL", side_effect=lambda *a, **k:
                       AudioSSL("tiny-offline", config.to_dict(), pretrained=False, unfreeze_layers=1)):
                report = train(args)
            self.assertFalse(report["target_met"])
            self.assertTrue((folder / "out/audio_candidate.pth").exists())
            self.assertEqual(report["tests"]["external_test"]["n"], 2)

    def test_model_backward_and_checkpoint(self):
        config = Wav2Vec2Config(hidden_size=32, num_hidden_layers=2, num_attention_heads=2,
            intermediate_size=64, conv_dim=(16, 16, 16), conv_stride=(5, 2, 2),
            conv_kernel=(10, 3, 3), num_conv_pos_embedding_groups=2,
            num_conv_pos_embeddings=16, mask_time_prob=0., hidden_dropout=0., attention_dropout=0.)
        model = AudioSSL("tiny-offline", config.to_dict(), pretrained=False, unfreeze_layers=1)
        model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        x = torch.randn(2, 1600); masks = torch.ones_like(x, dtype=torch.long)
        masks[1, 1200:] = 0
        output = model(x, masks)
        self.assertEqual(output.shape, (2, 2))
        torch.nn.functional.cross_entropy(output, torch.tensor([0, 1])).backward()
        self.assertIsNotNone(model.encoder.encoder.layers[-1].attention.q_proj.weight.grad)
        self.assertIsNone(model.encoder.encoder.layers[0].attention.q_proj.weight.grad)
        model.eval()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "candidate.pth"
            torch.save({"model_state_dict": model.state_dict(), "metadata": {
                "arch": "audio_ssl", "encoder_name": "tiny-offline", "encoder_config": config.to_dict()}}, path)
            restored, _ = load_audio_checkpoint(path, torch.device("cpu"))
            with torch.no_grad(): torch.testing.assert_close(model(x, masks), restored(x, masks))

    def test_windows_cover_end_and_padding_mask(self):
        starts = window_starts(16000 * 100, 64000, 12)
        self.assertEqual(starts[0], 0); self.assertEqual(starts[-1], 16000 * 100 - 64000)
        crop, mask = crop_tensor(np.arange(200, dtype=np.float32), 0, 400)
        self.assertEqual(int(mask.sum()), 200); self.assertEqual(float(crop[200:].sum()), 0.)

    def test_resampling_and_silence(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "audio.wav"
            wave = np.sin(np.arange(8000) * .1).astype(np.float32)
            sf.write(path, wave, 8000)
            x, masks, starts, duration = audio_windows(path)
            self.assertEqual(x.shape, (1, 64000)); self.assertEqual(int(masks.sum()), 16000)
            self.assertEqual(duration, 1.)
            sf.write(path, np.zeros(8000), 8000)
            with self.assertRaisesRegex(ValueError, "silent"): audio_windows(path)

    def test_metric_class_mapping_and_calibration(self):
        result = metrics([0, 0, 1, 1], [.05, .1, .9, .95])
        self.assertEqual(result["roc_auc"], 1.)
        self.assertEqual(result["confusion_matrix_real_fake"], [[2, 0], [0, 2]])
        temperature, threshold = calibrate([torch.tensor([[3., 0.]]), torch.tensor([[0., 3.]])], [0, 1])
        self.assertGreater(temperature, 0); self.assertTrue(.05 <= threshold <= .95)

    def test_labels_fail_closed_and_speaker_normalization(self):
        root = Path("data")
        self.assertEqual(folder_label(root / "real" / "x.wav", root), 0)
        self.assertEqual(folder_label(root / "synthetic" / "x.wav", root), 1)
        self.assertIsNone(folder_label(root / "ambiguous" / "x.wav", root))
        with self.assertRaises(ValueError): folder_label(root / "real" / "fake" / "x.wav", root)
        self.assertEqual(speaker_key(1005.0), speaker_key(1005))


if __name__ == "__main__": unittest.main()
