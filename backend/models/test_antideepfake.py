"""Offline checks of checkpoint translation and the application's label contract."""
import unittest
import torch
from backend.models.antideepfake import AntiDeepfake, encoder_key


class AntiDeepfakeTests(unittest.TestCase):
    def test_fairseq_key_translation(self):
        self.assertEqual(encoder_key('m_ssl.model.encoder.layers.0.self_attn.q_proj.weight'),
                         'encoder.encoder.layers.0.attention.q_proj.weight')
        self.assertEqual(encoder_key('m_ssl.model.feature_extractor.conv_layers.2.2.1.weight'),
                         'encoder.feature_extractor.conv_layers.2.layer_norm.weight')
        self.assertEqual(encoder_key('m_ssl.model.encoder.pos_conv.0.weight_g'),
                         'encoder.encoder.pos_conv_embed.conv.parametrizations.weight.original0')
        self.assertIsNone(encoder_key('m_ssl.model.quantizer.vars'))
        with self.assertRaises(ValueError): encoder_key('another_model.weight')

    def test_upstream_fake_index_zero_becomes_application_index_one(self):
        config=dict(hidden_size=16,num_hidden_layers=1,num_attention_heads=2,
                    intermediate_size=32,conv_dim=[8,8,8],conv_kernel=[10,3,3],
                    conv_stride=[5,2,2],num_conv_pos_embedding_groups=2,
                    num_conv_pos_embeddings=16,do_stable_layer_norm=True,
                    feat_extract_norm='layer',conv_bias=True,mask_time_prob=0.)
        model=AntiDeepfake(config).eval()
        with torch.no_grad():
            model.proj_fc.weight.zero_()
            model.proj_fc.bias.copy_(torch.tensor([5.,-5.]))
            result=model(torch.randn(1,1600))
        self.assertTrue(torch.isfinite(result).all())
        torch.testing.assert_close(result,torch.tensor([[-5.,5.]]))

if __name__=='__main__': unittest.main()
