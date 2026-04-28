import { useNavigate } from 'react-router';
import { NexusLogo } from '../components/NexusLogo';
import { ArrowLeft, Upload, Cpu, BarChart3, Shield, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';

export default function HowItWorks() {
  const navigate = useNavigate();

  const steps = [
    {
      number: '01',
      title: 'Upload Your Media',
      description: 'Upload any video, audio, or image file. Nexus supports all major formats including MP4, AVI, MOV for video; MP3, WAV, FLAC for audio; and JPEG, PNG, WebP for images.',
      icon: Upload,
    },
    {
      number: '02',
      title: 'AI Preprocessing',
      description: 'The media is broken into frames (video), segments (audio), or pixel matrices (image). Our preprocessing pipeline normalizes, denoises, and prepares data for deep analysis using industry-standard techniques.',
      icon: Cpu,
    },
    {
      number: '03',
      title: 'Multimodal Detection',
      description: "Nexus's AI ensemble runs multiple specialized neural networks simultaneously — vision transformers for spatial artifacts, RNNs for temporal inconsistencies, and spectral CNNs for audio frequency anomalies.",
      icon: Shield,
    },
    {
      number: '04',
      title: 'Results & Insights',
      description: 'Get a detailed deepfake probability score, anomaly count, visual graphs (Spectrograms, ROC Curves, Spatiotemporal Graphs), and a plain-language explanation of every suspicious pattern detected.',
      icon: BarChart3,
    },
  ];

  const techniques = [
    { title: 'GAN Artifact Detection', description: 'Generative Adversarial Networks leave subtle frequency-domain fingerprints invisible to the human eye. Our CNN models trained on 10M+ GAN-generated images identify these patterns with 99.8% accuracy.', tag: 'Image & Video' },
    { title: 'Temporal Inconsistency Analysis', description: 'Real faces have consistent micro-expressions and natural motion blur between frames. We model optical flow and detect unnatural frame-to-frame transitions that deepfake generators struggle to replicate.', tag: 'Video' },
    { title: 'Audio Spectrogram Analysis', description: 'Voice cloning models introduce unique spectral artifacts in the frequency domain. Our spectrogram CNNs detect unnatural harmonics, missing breath sounds, and phase discontinuities in cloned voices.', tag: 'Audio' },
    { title: 'Facial Landmark Geometry', description: 'We track 468 facial landmarks per frame and measure geometric consistency. Deepfakes often show subtle distortions in ear shape, neck boundaries, and eye reflection patterns.', tag: 'Image & Video' },
    { title: 'Lip Sync Verification', description: 'Cross-modal analysis correlates audio phonemes with lip movement geometry. A mismatch between spoken phonemes and lip shape is a strong indicator of video manipulation.', tag: 'Video' },
    { title: 'Metadata & Compression Forensics', description: 'Every digital file carries metadata and compression signatures. Re-encoded or manipulated media breaks the original compression pattern, which our forensics engine detects at the binary level.', tag: 'All Formats' },
  ];

  const metrics = [
    { label: 'Image Deepfake Detection', value: 99.8 },
    { label: 'Audio Clone Detection', value: 97.4 },
    { label: 'Video Deepfake Detection', value: 98.1 },
  ];

  const highlights = [
    { icon: AlertTriangle, label: 'False Positive Rate', value: '< 0.2%' },
    { icon: Shield, label: 'Processing Speed', value: '< 10ms per frame' },
    { icon: CheckCircle, label: 'Formats Supported', value: '40+ file types' },
    { icon: Cpu, label: 'Model Parameters', value: '2.4 Billion' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'transparent', color: '#fff', fontFamily: "'Inter', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />

      {/* FULL-PAGE ANIMATED BACKGROUND */}
      <div className="page-bg" />
      <div className="page-overlay" />

      {/* Nav */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'rgba(5,5,15,0.85)', backdropFilter: 'blur(16px)', borderBottom: '1px solid rgba(255,255,255,0.06)', padding: '0 40px' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 68 }}>
          <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10 }}>
            <NexusLogo size={32} />
            <span style={{ fontSize: 18, fontWeight: 800, color: '#fff' }}>Nexus</span>
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button onClick={() => navigate('/')} style={{ background: 'none', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 50, padding: '7px 18px', color: 'rgba(255,255,255,0.6)', fontSize: 13, fontWeight: 500, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, transition: 'all .2s' }}
              onMouseEnter={e => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.4)'; }}
              onMouseLeave={e => { e.currentTarget.style.color = 'rgba(255,255,255,0.6)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'; }}
            >
              <ArrowLeft size={14} /> Back to Home
            </button>
            <button onClick={() => navigate('/analyze')} style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)', border: 'none', borderRadius: 50, padding: '9px 22px', color: '#fff', fontSize: 13, fontWeight: 700, cursor: 'pointer', boxShadow: '0 0 20px rgba(124,58,237,0.35)', transition: 'all .2s' }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 0 32px rgba(124,58,237,0.6)'; e.currentTarget.style.transform = 'translateY(-1px)'; }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 0 20px rgba(124,58,237,0.35)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              Try It Now
            </button>
          </div>
        </div>
      </nav>

      {/* Page content */}
      <div style={{ position: 'relative', zIndex: 2 }}>

        {/* Hero */}
        <section style={{ paddingTop: 140, paddingBottom: 80, padding: '140px 24px 80px', textAlign: 'center' }}>
          <div style={{ maxWidth: 800, margin: '0 auto' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, border: '1px solid rgba(124,58,237,0.45)', borderRadius: 50, padding: '5px 16px', marginBottom: 24, background: 'rgba(124,58,237,0.1)', fontSize: 12, color: '#a78bfa', fontWeight: 600, letterSpacing: 1.5, textTransform: 'uppercase' }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#a78bfa', display: 'inline-block' }} />
              How It Works
            </div>
            <h1 style={{ fontSize: 'clamp(36px,6vw,64px)', fontWeight: 900, letterSpacing: '-2px', lineHeight: 1.08, marginBottom: 20 }}>
              AI That Thinks Like a{' '}
              <span style={{ background: 'linear-gradient(90deg,#a78bfa,#60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Forensic Expert
              </span>
            </h1>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 18, lineHeight: 1.7, maxWidth: 600, margin: '0 auto' }}>
              Gandiva uses a multi-layer AI pipeline combining computer vision, spectral analysis, and temporal reasoning to detect synthetic media with forensic-grade accuracy.
            </p>
          </div>
        </section>

        {/* Steps */}
        <section style={{ padding: '20px 24px 80px' }}>
          <div style={{ maxWidth: 900, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
            {steps.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={i} style={{ display: 'flex', gap: 24, background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, padding: '28px 32px', backdropFilter: 'blur(12px)', alignItems: 'flex-start', transition: 'all .3s' }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(124,58,237,0.4)'; e.currentTarget.style.background = 'rgba(124,58,237,0.06)'; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'; e.currentTarget.style.background = 'rgba(255,255,255,0.025)'; }}
                >
                  <div style={{ flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                    <div style={{ width: 52, height: 52, borderRadius: 14, background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon size={22} color="#a78bfa" />
                    </div>
                    <span style={{ fontSize: 36, fontWeight: 900, color: 'rgba(124,58,237,0.25)', lineHeight: 1 }}>{step.number}</span>
                  </div>
                  <div style={{ flex: 1, paddingTop: 4 }}>
                    <h3 style={{ fontSize: 19, fontWeight: 800, marginBottom: 10 }}>{step.title}</h3>
                    <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 15, lineHeight: 1.7 }}>{step.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Detection Techniques */}
        <section style={{ padding: '80px 24px', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: 56 }}>
              <span style={{ color: '#a78bfa', fontSize: 11, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase' }}>Detection Techniques</span>
              <h2 style={{ fontSize: 40, fontWeight: 900, letterSpacing: '-1px', marginTop: 12, marginBottom: 14 }}>Under the Hood</h2>
              <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 16, maxWidth: 480, margin: '0 auto' }}>Six specialized detection methods run in parallel so nothing slips through.</p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 16 }}>
              {techniques.map((tech, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, padding: '28px 24px', transition: 'all .3s', backdropFilter: 'blur(12px)' }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(124,58,237,0.4)'; e.currentTarget.style.background = 'rgba(124,58,237,0.06)'; e.currentTarget.style.transform = 'translateY(-3px)'; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'; e.currentTarget.style.background = 'rgba(255,255,255,0.025)'; e.currentTarget.style.transform = 'translateY(0)'; }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                    <CheckCircle size={18} color="#a78bfa" />
                    <span style={{ fontSize: 11, fontWeight: 700, color: '#a78bfa', border: '1px solid rgba(167,139,250,0.3)', borderRadius: 50, padding: '2px 10px', background: 'rgba(124,58,237,0.1)' }}>{tech.tag}</span>
                  </div>
                  <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 10 }}>{tech.title}</h3>
                  <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13, lineHeight: 1.7 }}>{tech.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Model Performance */}
        <section style={{ padding: '80px 24px' }}>
          <div style={{ maxWidth: 900, margin: '0 auto' }}>
            <div style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 24, padding: '48px 40px', backdropFilter: 'blur(12px)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, alignItems: 'center' }}>
                <div>
                  <span style={{ color: '#a78bfa', fontSize: 11, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase', display: 'block', marginBottom: 12 }}>Model Performance</span>
                  <h2 style={{ fontSize: 30, fontWeight: 900, letterSpacing: '-0.5px', marginBottom: 16 }}>Benchmarked Against Industry Standards</h2>
                  <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 14, lineHeight: 1.7, marginBottom: 28 }}>
                    Our models are tested monthly on public deepfake datasets including FaceForensics++, DFDC, and CelebDF, consistently ranking in the top tier for detection F1 score.
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                    {metrics.map((m, i) => (
                      <div key={i}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                          <span style={{ color: 'rgba(255,255,255,0.55)' }}>{m.label}</span>
                          <span style={{ fontWeight: 700, color: '#a78bfa' }}>{m.value}%</span>
                        </div>
                        <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 4, overflow: 'hidden' }}>
                          <div style={{ height: '100%', borderRadius: 4, width: `${m.value}%`, background: 'linear-gradient(90deg,#7c3aed,#60a5fa)' }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {highlights.map((h, i) => {
                    const Icon = h.icon;
                    return (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.2)', borderRadius: 14, padding: '14px 18px' }}>
                        <Icon size={20} color="#a78bfa" />
                        <div>
                          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginBottom: 2 }}>{h.label}</div>
                          <div style={{ fontSize: 15, fontWeight: 700 }}>{h.value}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section style={{ padding: '60px 24px 100px', textAlign: 'center' }}>
          <div style={{ maxWidth: 600, margin: '0 auto' }}>
            <h2 style={{ fontSize: 40, fontWeight: 900, letterSpacing: '-1px', marginBottom: 14 }}>Ready to Detect?</h2>
            <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 16, marginBottom: 32 }}>Upload your first file and get forensic-grade results in seconds.</p>
            <button onClick={() => navigate('/analyze')} style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)', border: 'none', borderRadius: 50, padding: '15px 40px', color: '#fff', fontSize: 16, fontWeight: 700, cursor: 'pointer', boxShadow: '0 0 40px rgba(124,58,237,0.45)', display: 'inline-flex', alignItems: 'center', gap: 10, transition: 'all .25s' }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 0 60px rgba(124,58,237,0.65)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(124,58,237,0.45)'; }}
            >
              Start Analysis <ArrowRight size={18} />
            </button>
          </div>
        </section>



      </div>
      <style>{`* { margin:0; padding:0; box-sizing:border-box; }`}</style>
    </div>
  );
}
