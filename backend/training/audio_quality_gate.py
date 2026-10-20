"""Deployment checks stricter than an average balanced accuracy target."""


def assess_audio_report(report, max_false_positive_rate=.1, min_fake_recall=.8):
    reasons=[]
    tests=report.get('tests',{})
    for name in ('test','external_test','modern_tts_test','unseen_generator_test','unseen_speaker_test'):
        result=tests.get(name)
        if not result:
            reasons.append(f'Missing {name} evaluation')
            continue
        if name in ('external_test','modern_tts_test','unseen_generator_test','unseen_speaker_test') and result.get('training_overlap_audit_passed') is not True:
            reasons.append(f'{name} needs verified separation from training data')
        counts=result.get('class_counts_real_fake',[])
        if len(counts)!=2 or min(counts)<200:
            reasons.append(f'{name} needs at least 200 genuine and 200 synthetic recordings')
        if result.get('balanced_accuracy_lower_95',0)<.8:
            reasons.append(f'{name} balanced accuracy confidence bound is below 80 percent')
        if result.get('false_positive_rate',1)>max_false_positive_rate:
            reasons.append(f'{name} genuine false positives exceed {max_false_positive_rate:.0%}')
        if result.get('fake_recall',0)<min_fake_recall:
            reasons.append(f'{name} fake recall is below {min_fake_recall:.0%}')
    return dict(deployment_ready=not reasons,reasons=reasons,
                required_max_false_positive_rate=max_false_positive_rate,
                required_min_fake_recall=min_fake_recall)
