import { useNavigate } from 'react-router';
import { NeuroLogo } from '../components/NeuroLogo';
import { ArrowLeft, Video, Mic, ImageIcon, ArrowRight } from 'lucide-react';

const options = [
  {
    id: 'video',
    label: 'Video Analysis',
    tag: 'DEEPFAKE VIDEO',
    description: 'Detect deepfakes in video content. Analyzes facial movements, lip sync, temporal consistency, and spatiotemporal patterns across frames.',
    icon: Video,
    supported: 'MP4, AVI, MOV, MKV, WEBM',
  },
  {
    id: 'audio',
    label: 'Audio Analysis',
    tag: 'VOICE CLONE',
    description: 'Identify AI-cloned or synthetically generated voices. Examines spectral patterns, breath artifacts, and frequency anomalies.',
    icon: Mic,
    supported: 'MP3, WAV, AAC, FLAC, OGG, M4A',
  },
  {
    id: 'image',
    label: 'Image Analysis',
    tag: 'SYNTHETIC IMAGE',
    description: 'Uncover GAN-generated, face-swapped, or manipulated images. Uses pixel-level forensics and ROC-based scoring.',
    icon: ImageIcon,
    supported: 'JPG, JPEG, PNG, WEBP, BMP, TIFF',
  },
];

const NAV: React.CSSProperties = {
  position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
  background: 'rgba(5,5,15,0.85)', backdropFilter: 'blur(16px)',
  borderBottom: '1px solid rgba(255,255,255,0.06)',
  padding: '0 40px',
};

export default function Analyze() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', background: 'transparent', color: '#fff', fontFamily: "'Inter', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />

      {/* FULL-PAGE ANIMATED BACKGROUND */}
      <div className="page-bg" />
      <div className="page-overlay" />

      {/* Nav */}
      <nav style={NAV}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 68 }}>
          <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10 }}>
            <NeuroLogo size={32} />
            <span style={{ fontSize: 18, fontWeight: 800, color: '#fff' }}>Neuro</span>
          </button>
          <button onClick={() => navigate('/')} style={{
            background: 'none', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 50,
            padding: '7px 18px', color: 'rgba(255,255,255,0.6)', fontSize: 13, fontWeight: 500,
            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, transition: 'all .2s',
          }}
            onMouseEnter={e => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.35)'; }}
            onMouseLeave={e => { e.currentTarget.style.color = 'rgba(255,255,255,0.6)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'; }}
          >
            <ArrowLeft size={14} /> Back to Home
          </button>
        </div>
      </nav>

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 2, paddingTop: 120, paddingBottom: 80, padding: '120px 24px 80px' }}>
        <div style={{ maxWidth: 780, margin: '0 auto' }}>

          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              border: '1px solid rgba(124,58,237,0.45)', borderRadius: 50,
              padding: '5px 16px', marginBottom: 24,
              background: 'rgba(124,58,237,0.1)', fontSize: 12,
              color: '#a78bfa', fontWeight: 600, letterSpacing: 1.5, textTransform: 'uppercase',
            }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#a78bfa', display: 'inline-block' }} />
              Choose Analysis Type
            </div>
            <h1 style={{ fontSize: 'clamp(32px, 5vw, 52px)', fontWeight: 900, letterSpacing: '-1.5px', marginBottom: 16, lineHeight: 1.1 }}>
              What Are You{' '}
              <span style={{ background: 'linear-gradient(90deg,#a78bfa,#60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Analyzing?
              </span>
            </h1>
            <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 16 }}>Select media type to begin forensic-grade deepfake detection</p>
          </div>

          {/* Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {options.map((opt) => {
              const Icon = opt.icon;
              return (
                <button
                  key={opt.id}
                  onClick={() => navigate(`/analyze/${opt.id}`)}
                  style={{
                    background: 'rgba(255,255,255,0.025)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: 20, padding: '28px 32px',
                    cursor: 'pointer', textAlign: 'left',
                    display: 'flex', alignItems: 'center', gap: 24,
                    transition: 'all .25s', color: '#fff',
                    backdropFilter: 'blur(12px)',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background = 'rgba(124,58,237,0.08)';
                    e.currentTarget.style.borderColor = 'rgba(124,58,237,0.45)';
                    e.currentTarget.style.transform = 'translateY(-3px)';
                    e.currentTarget.style.boxShadow = '0 12px 40px rgba(124,58,237,0.15)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.025)';
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  {/* Icon */}
                  <div style={{
                    flexShrink: 0, width: 60, height: 60, borderRadius: 16,
                    background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Icon size={26} color="#a78bfa" />
                  </div>

                  {/* Text */}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                      <span style={{ fontSize: 18, fontWeight: 800 }}>{opt.label}</span>
                      <span style={{
                        fontSize: 10, fontWeight: 700, letterSpacing: 1.5,
                        color: '#a78bfa', border: '1px solid rgba(167,139,250,0.35)',
                        borderRadius: 50, padding: '2px 10px',
                        background: 'rgba(124,58,237,0.12)',
                      }}>{opt.tag}</span>
                    </div>
                    <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 14, lineHeight: 1.6, marginBottom: 10, maxWidth: 500 }}>{opt.description}</p>
                    <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.3)' }}>
                      Supports: <span style={{ color: 'rgba(255,255,255,0.5)' }}>{opt.supported}</span>
                    </span>
                  </div>

                  {/* Arrow */}
                  <div style={{
                    flexShrink: 0, width: 40, height: 40, borderRadius: '50%',
                    border: '1px solid rgba(124,58,237,0.4)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: '#a78bfa',
                  }}>
                    <ArrowRight size={16} />
                  </div>
                </button>
              );
            })}
          </div>

          <p style={{ textAlign: 'center', fontSize: 12, color: 'rgba(255,255,255,0.2)', marginTop: 32 }}>
            All uploads are processed securely. Files are never stored beyond the analysis session.
          </p>
        </div>
      </div>
    </div>
  );
}
