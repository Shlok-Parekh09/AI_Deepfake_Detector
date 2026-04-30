import { useNavigate } from 'react-router';
import { NeuroLogo } from '../components/NeuroLogo';
import { ArrowLeft, Shield, Eye, Zap, Lock, Scan, Brain, ArrowRight } from 'lucide-react';

export default function Features() {
  const navigate = useNavigate();

  const features = [
    { icon: Shield, title: 'Pixel-Level Analysis', desc: 'Break visuals down to raw pixel structure and detect manipulation at its origin — no matter how subtle.' },
    { icon: Eye, title: 'Voice Analysis', desc: 'Analyze the raw audio spectrum to uncover artifacts left by voice synthesis and cloning.' },
    { icon: Zap, title: 'Forensic File Analysis', desc: 'Inspect every technical signature inside the file — codecs, metadata, timestamps — to reveal hidden manipulation.' },
    { icon: Lock, title: 'Multi-Layer Detection', desc: 'Stack independent forensic signals for certainty that single-layer detectors simply cannot match.' },
    { icon: Scan, title: 'Forensic Reports', desc: 'Court-ready reports with full audit trails, confidence scores, and admissible forensic documentation.' },
    { icon: Brain, title: 'Real-Time Results', desc: 'Upload files or URLs and get a comprehensive multi-layer assessment in seconds — not hours.' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'transparent', color: '#fff', fontFamily: "'Inter', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />

      {/* NAV */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: 'rgba(5,5,15,0.85)', backdropFilter: 'blur(16px)',
        padding: '0 40px',
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 68 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <NeuroLogo size={34} />
            <span style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.5px', color: '#fff' }}>Neuro</span>
          </div>

          <div className="nav-links" style={{ display: 'flex', alignItems: 'center', gap: 36 }}>
            {['Features', 'Solutions', 'How It Works'].map(l => (
              <a key={l} onClick={() => navigate(`/${l.toLowerCase().replace(/ /g, '-')}`)}
                style={{ color: 'rgba(255,255,255,0.6)', fontSize: 14, fontWeight: 500, textDecoration: 'none', transition: 'color .2s', cursor: 'pointer' }}
                onMouseEnter={e => (e.currentTarget.style.color = '#fff')}
                onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.6)')}
              >{l}</a>
            ))}
          </div>

          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button onClick={() => navigate('/analyze')} style={{
              border: '1.5px solid rgba(255,255,255,0.25)', borderRadius: 50,
              padding: '9px 24px', background: 'transparent', color: '#fff',
              fontSize: 14, fontWeight: 600, cursor: 'pointer', transition: 'all .2s',
            }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.5)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.25)'; }}
            >Log In</button>
            <button onClick={() => navigate('/analyze')} style={{
              background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              border: 'none', borderRadius: 50, padding: '10px 26px',
              color: '#fff', fontSize: 14, fontWeight: 700, cursor: 'pointer',
              boxShadow: '0 0 24px rgba(124,58,237,0.4)', transition: 'all .2s',
            }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 0 36px rgba(124,58,237,0.6)'; e.currentTarget.style.transform = 'translateY(-1px)'; }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 0 24px rgba(124,58,237,0.4)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >Get Started</button>
          </div>
        </div>
      </nav>

      {/* FEATURES SECTION */}
      <section style={{ padding: '140px 24px 100px', position: 'relative', zIndex: 2 }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <button onClick={() => navigate('/')} style={{
            display: 'flex', alignItems: 'center', gap: 8, border: 'none', background: 'transparent',
            color: 'rgba(255,255,255,0.6)', fontSize: 14, fontWeight: 500, cursor: 'pointer', marginBottom: 40,
          }} onMouseEnter={e => e.currentTarget.style.color = '#fff'} onMouseLeave={e => e.currentTarget.style.color = 'rgba(255,255,255,0.6)'}>
            <ArrowLeft size={18} /> Back to Home
          </button>

          <div style={{ textAlign: 'center', marginBottom: 80 }}>
            <span style={{ color: '#a78bfa', fontSize: 12, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase' }}>Capabilities</span>
            <h1 style={{ fontSize: 56, fontWeight: 900, marginTop: 16, marginBottom: 24, letterSpacing: '-1.5px' }}>Powerful Detection Features</h1>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 18, maxWidth: 600, margin: '0 auto', lineHeight: 1.6 }}>
              Our multi-layered forensic analysis engine combines cutting-edge AI with traditional signal processing to detect deepfakes with unprecedented accuracy.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(350px,1fr))', gap: 24 }}>
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <div key={i} style={{
                  background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: 24, padding: '40px 32px', display: 'flex', flexDirection: 'column', gap: 20,
                  transition: 'all .3s',
                }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'rgba(124,58,237,0.4)';
                    e.currentTarget.style.transform = 'translateY(-4px)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div style={{ width: 56, height: 56, borderRadius: 16, background: 'rgba(124,58,237,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={28} style={{ color: '#a78bfa' }} />
                  </div>
                  <h3 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>{f.title}</h3>
                  <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 15, lineHeight: 1.7, margin: 0 }}>{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <style>{`
        @media(max-width:768px){.nav-links{display:none!important}}
      `}</style>
    </div>
  );
}
