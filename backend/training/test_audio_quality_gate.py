import unittest
from backend.training.audio_quality_gate import assess_audio_report


class QualityGateTests(unittest.TestCase):
    def test_high_fake_recall_does_not_hide_genuine_false_positives(self):
        good=dict(class_counts_real_fake=[1000,1000],balanced_accuracy_lower_95=.9,
                  false_positive_rate=.03,fake_recall=.95,training_overlap_audit_passed=True)
        tests={name:dict(good) for name in ('test','external_test','modern_tts_test','unseen_generator_test','unseen_speaker_test')}
        tests['external_test'].update(false_positive_rate=.3252,fake_recall=.9944)
        self.assertFalse(assess_audio_report({'tests':tests})['deployment_ready'])

    def test_modern_generator_benchmark_required(self):
        good=dict(class_counts_real_fake=[1000,1000],balanced_accuracy_lower_95=.9,
                  false_positive_rate=.03,fake_recall=.95,training_overlap_audit_passed=True)
        report={'tests':dict(test=good,external_test=good)}
        self.assertFalse(assess_audio_report(report)['deployment_ready'])
        report['tests'].update(modern_tts_test=good,unseen_generator_test=good,unseen_speaker_test=good)
        self.assertTrue(assess_audio_report(report)['deployment_ready'])

    def test_high_scores_without_verified_isolation_cannot_pass(self):
        good=dict(class_counts_real_fake=[1000,1000],balanced_accuracy_lower_95=.9,
                  false_positive_rate=.03,fake_recall=.95)
        tests={name:dict(good) for name in ('test','external_test','modern_tts_test','unseen_generator_test','unseen_speaker_test')}
        self.assertFalse(assess_audio_report({'tests':tests})['deployment_ready'])

if __name__=='__main__': unittest.main()
