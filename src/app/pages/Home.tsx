import { useNavigate } from 'react-router';
import { Shield, Eye, Zap, Lock, ArrowRight, Scan, Brain } from 'lucide-react';
import { NeuroLogo } from '../components/NeuroLogo';

export default function Home() {
  const navigate = useNavigate();

  const features = [
    { icon: Shield, title: 'Pixel-Level Analysis', desc: 'Break visuals down to raw pixel structure and detect manipulation at its origin — no matter how subtle.' },
    { icon: Eye, title: 'Voice Analysis', desc: 'Analyze the raw audio spectrum to uncover artifacts left by voice synthesis and cloning.' },
    { icon: Zap, title: 'Forensic File Analysis', desc: 'Inspect every technical signature inside the file — codecs, metadata, timestamps — to reveal hidden manipulation.' },
    { icon: Lock, title: 'Multi-Layer Detection', desc: 'Stack independent forensic signals for certainty that single-layer detectors simply cannot match.' },
    { icon: Scan, title: 'Forensic Reports', desc: 'Court-ready reports with full audit trails, confidence scores, and admissible forensic documentation.' },
    { icon: Brain, title: 'Real-Time Results', desc: 'Upload files or URLs and get a comprehensive multi-layer assessment in seconds — not hours.' },
  ];

  const stats = [
    { value: '98%', label: 'Detection Accuracy' },
    { value: '50M+', label: 'Files Analyzed' },
    { value: '<5s', label: 'Analysis Time' },
    { value: '30+', label: 'Countries Deployed' },
  ];

  return (
    <div style={{ height: '100vh', overflow: 'hidden', background: 'transparent', color: '#fff', fontFamily: "'Inter', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />

      {/* FULL-PAGE ANIMATED BACKGROUND */}
      <div className="page-bg" />
      <div className="page-overlay" />

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
              <a key={l} onClick={() => navigate(`/${l.toLowerCase().replace(/ /g, '-' )}`)}
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

      {/* HERO */}
      <section style={{
        position: 'relative', minHeight: 'calc(100vh - 68px)', display: 'flex', alignItems: 'center',
        justifyContent: 'center', textAlign: 'center', overflow: 'hidden', padding: '68px 24px 24px',
        zIndex: 2,
      }}>

        {/* Floating pill badge */}
        <div style={{ position: 'relative', zIndex: 2, maxWidth: 860, margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            border: '1px solid rgba(124,58,237,0.6)', borderRadius: 50,
            padding: '7px 20px', marginBottom: 36,
            background: 'rgba(124,58,237,0.15)', backdropFilter: 'blur(12px)',
            fontSize: 13, color: 'rgba(255,255,255,0.85)', fontWeight: 600,
            boxShadow: '0 0 24px rgba(124,58,237,0.2), inset 0 0 12px rgba(124,58,237,0.1)',
          }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#a78bfa', display: 'inline-block', animation: 'pulse 2s infinite', boxShadow: '0 0 8px #a78bfa' }} />
            AI-Powered Deepfake & Synthetic Media Detection
          </div>

          <h1 style={{
            fontSize: 'clamp(44px, 8vw, 88px)', fontWeight: 900,
            lineHeight: 1.05, marginBottom: 24, letterSpacing: '-2px',
          }}>
            Detect. Verify.{' '}
            <span style={{
              background: 'linear-gradient(90deg, #a78bfa, #60a5fa)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>Protect Reality.</span>
          </h1>

          <p style={{ fontSize: 18, color: 'rgba(255,255,255,0.6)', maxWidth: 560, margin: '0 auto 40px', lineHeight: 1.7 }}>
            Forensic-grade deepfake detection for videos, images, and audio. Upload any file and get a multi-layer assessment in seconds.
          </p>

          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 56 }}>
            <button onClick={() => navigate('/analyze')} style={{
              background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              border: 'none', borderRadius: 50, padding: '15px 36px',
              color: '#fff', fontSize: 16, fontWeight: 700, cursor: 'pointer',
              boxShadow: '0 0 40px rgba(124,58,237,0.5)', display: 'flex', alignItems: 'center', gap: 8,
              transition: 'all .25s',
            }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 0 60px rgba(124,58,237,0.7)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(124,58,237,0.5)'; }}
            >
              Start Detecting <ArrowRight size={18} />
            </button>
            <button onClick={() => navigate('/how-it-works')} style={{
              border: '1.5px solid rgba(255,255,255,0.25)', borderRadius: 50,
              padding: '15px 36px', background: 'rgba(255,255,255,0.04)',
              color: '#fff', fontSize: 16, fontWeight: 600, cursor: 'pointer',
              backdropFilter: 'blur(8px)', transition: 'all .25s',
            }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.5)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.25)'; }}
            >
              See How It Works
            </button>
          </div>

        </div>
      </section>

      {/* STATS */}
      <section style={{ padding: '56px 24px', position: 'relative' }}>
        <div style={{ position: 'absolute', inset: 0, borderTop: '1px solid rgba(124,58,237,0.15)', borderBottom: '1px solid rgba(124,58,237,0.15)' }} />
        <div style={{ maxWidth: 1000, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 40, textAlign: 'center', position: 'relative', zIndex: 1 }}>
          {stats.map((s, i) => (
            <div key={i} style={{ padding: '20px 0' }}>
              <div style={{ fontSize: 56, fontWeight: 900, background: 'linear-gradient(90deg,#a78bfa,#60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', lineHeight: 1.1, marginBottom: 10, filter: 'drop-shadow(0 0 20px rgba(124,58,237,0.4))' }}>{s.value}</div>
              <div style={{ color: 'rgba(255,255,255,0.45)', fontSize: 14, fontWeight: 500, letterSpacing: 0.5 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" style={{ padding: '72px 24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 44 }}>
            <span style={{ color: '#a78bfa', fontSize: 12, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase' }}>Capabilities</span>
            <h2 style={{ fontSize: 44, fontWeight: 900, marginTop: 12, marginBottom: 16, letterSpacing: '-1px' }}>Multi-Layer Detection Engine</h2>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 17, maxWidth: 520, margin: '0 auto' }}>Every dimension analyzed — visual, acoustic, metadata, and cross-modal inconsistencies.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 20 }}>
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <div key={i} style={{
                  background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: 20, padding: '32px 28px', transition: 'all .35s', cursor: 'default',
                  position: 'relative', overflow: 'hidden',
                }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'rgba(124,58,237,0.5)';
                    e.currentTarget.style.background = 'rgba(124,58,237,0.07)';
                    e.currentTarget.style.transform = 'translateY(-5px)';
                    e.currentTarget.style.boxShadow = '0 20px 40px rgba(124,58,237,0.12)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)';
                    e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <span style={{ position: 'absolute', top: 20, right: 20, fontSize: 11, fontWeight: 700, color: 'rgba(124,58,237,0.3)', letterSpacing: 1 }}>0{i + 1}</span>
                  <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>
                    <Icon size={20} color="#a78bfa" />
                  </div>
                  <h3 style={{ fontSize: 17, fontWeight: 700, marginBottom: 10 }}>{f.title}</h3>
                  <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 14, lineHeight: 1.7 }}>{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" style={{ padding: '72px 24px', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 44 }}>
            <span style={{ color: '#a78bfa', fontSize: 12, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase' }}>Process</span>
            <h2 style={{ fontSize: 44, fontWeight: 900, marginTop: 12, marginBottom: 16, letterSpacing: '-1px' }}>How Neuro Works</h2>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 17, maxWidth: 520, margin: '0 auto' }}>Three steps. Seconds to results. Forensic-grade confidence.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: 24 }}>
            {[
              { step: '01', title: 'Upload Media', desc: 'Drop any video, image, or audio file — or paste a URL. Our engine accepts all major formats.' },
              { step: '02', title: 'Multi-Layer Scan', desc: 'Our AI analyzes pixel structure, audio waveforms, metadata, and cross-modal patterns simultaneously.' },
              { step: '03', title: 'Forensic Report', desc: 'Receive a confidence score, visual indicators, and a detailed court-ready report within seconds.' },
            ].map((s, i) => (
              <div key={i} style={{ position: 'relative', background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, padding: '36px 28px' }}>
                <div style={{ fontSize: 56, fontWeight: 900, background: 'linear-gradient(135deg, rgba(167,139,250,0.8), rgba(96,165,250,0.4))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', lineHeight: 1, marginBottom: 20 }}>{s.step}</div>
                <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12 }}>{s.title}</h3>
                <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 14, lineHeight: 1.7 }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SOLUTIONS */}
      <section id="solutions" style={{ padding: '72px 24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 44 }}>
            <span style={{ color: '#a78bfa', fontSize: 12, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase' }}>Solutions</span>
            <h2 style={{ fontSize: 44, fontWeight: 900, marginTop: 12, marginBottom: 16, letterSpacing: '-1px' }}>Built for Every Use Case</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 20 }}>
            {[
              { label: 'ENTERPRISE', title: 'Corporate Security', desc: 'Protect KYC workflows, video calls, and internal communications from AI-generated impostors.', items: ['Executive identity protection', 'Real-time KYC validation', 'Employee fraud prevention'] },
              { label: 'GOVERNMENT', title: 'Judicial & Forensics', desc: 'Verify digital evidence with forensic-grade reports admissible in court and legal proceedings.', items: ['Court-ready evidence reports', 'Bulk media screening', 'Classified on-premise deployment'] },
              { label: 'MEDIA', title: 'Content Verification', desc: 'Stop synthetic misinformation before it spreads across your platform or publication.', items: ['Automated content screening', 'Provenance tracking', 'Publisher trust scores'] },
            ].map((u, i) => (
              <div key={i} style={{
                background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: 20, padding: '36px 28px', display: 'flex', flexDirection: 'column', gap: 16,
                transition: 'all .3s',
              }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(124,58,237,0.4)'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'; e.currentTarget.style.transform = 'translateY(0)'; }}
              >
                <span style={{ color: '#a78bfa', fontSize: 11, fontWeight: 700, letterSpacing: 2 }}>{u.label}</span>
                <h3 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>{u.title}</h3>
                <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 14, lineHeight: 1.7, margin: 0 }}>{u.desc}</p>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {u.items.map((item, j) => (
                    <li key={j} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'rgba(255,255,255,0.65)' }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#7c3aed', flexShrink: 0 }} />
                      {item}
                    </li>
                  ))}
                </ul>
                <button onClick={() => navigate('/analyze')} style={{
                  marginTop: 8, alignSelf: 'flex-start',
                  border: '1.5px solid rgba(124,58,237,0.5)', borderRadius: 50,
                  padding: '8px 20px', background: 'transparent',
                  color: '#a78bfa', fontSize: 13, fontWeight: 600, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 6, transition: 'all .2s',
                }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.15)'; }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                >
                  Learn more <ArrowRight size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '56px 24px' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', position: 'relative', borderRadius: 28, overflow: 'hidden', border: '1px solid rgba(124,58,237,0.35)', textAlign: 'center', padding: '56px 32px', background: 'rgba(5,5,15,0.4)', backdropFilter: 'blur(8px)' }}>
          <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(124,58,237,0.2) 0%, transparent 70%)' }} />
          <div style={{ position: 'relative', zIndex: 1 }}>
            <h2 style={{ fontSize: 42, fontWeight: 900, marginBottom: 16, letterSpacing: '-1px' }}>Ready to Detect Deepfakes?</h2>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 17, marginBottom: 36 }}>Upload your first file for free. No registration required.</p>
            <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button onClick={() => navigate('/analyze')} style={{
                background: 'linear-gradient(135deg, #7c3aed, #4f46e5)', border: 'none', borderRadius: 50,
                padding: '15px 36px', color: '#fff', fontSize: 16, fontWeight: 700, cursor: 'pointer',
                boxShadow: '0 0 40px rgba(124,58,237,0.5)', display: 'flex', alignItems: 'center', gap: 8, transition: 'all .25s',
              }}
                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 0 60px rgba(124,58,237,0.7)'; }}
                onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(124,58,237,0.5)'; }}
              >
                Start Free Trial <ArrowRight size={18} />
              </button>
              <button onClick={() => navigate('/how-it-works')} style={{
                border: '1.5px solid rgba(255,255,255,0.2)', borderRadius: 50, padding: '15px 36px',
                background: 'rgba(255,255,255,0.04)', color: '#fff', fontSize: 16, fontWeight: 600,
                cursor: 'pointer', backdropFilter: 'blur(8px)', transition: 'all .25s',
              }}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; }}
              >
                Learn More
              </button>
            </div>
          </div>
        </div>
      </section>



      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
        * { margin:0; padding:0; box-sizing:border-box; }
        @media(max-width:768px){.nav-links{display:none!important}}
      `}</style>
    </div>
  );
}




