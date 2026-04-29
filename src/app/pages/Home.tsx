import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Menu, X, Shield, Eye, Zap, Lock, ArrowRight, CheckCircle, ChevronRight, Scan, Brain, FileSearch } from 'lucide-react';
import { NeuroLogo } from '../components/NeuroLogo';

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
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

  const detectionTypes = [
    { label: 'pixel level analysis', active: true },
    { label: 'voice analysis', active: false },
    { label: 'file forensic analysis', active: false },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'transparent', color: '#fff', fontFamily: "'Inter', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />

      {/* FULL-PAGE ANIMATED BACKGROUND */}
      <div className="page-bg" />
      <div className="page-overlay" />

      {/* NAV */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: 'rgba(5,5,15,0.85)', backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        padding: '0 40px',
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 68 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <NeuroLogo size={34} />
            <span style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.5px', color: '#fff' }}>Neuro</span>
          </div>

          <div className="nav-links" style={{ display: 'flex', alignItems: 'center', gap: 36 }}>
            {['Features', 'Solutions', 'How It Works'].map(l => (
              <a key={l} href={`#${l.toLowerCase().replace(/ /g, '-')}`}
                style={{ color: 'rgba(255,255,255,0.6)', fontSize: 14, fontWeight: 500, textDecoration: 'none', transition: 'color .2s' }}
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
        position: 'relative', minHeight: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center', textAlign: 'center', overflow: 'hidden', paddingTop: 100,
        zIndex: 2,
      }}>

        {/* Floating pill badge */}
        <div style={{ position: 'relative', zIndex: 2, maxWidth: 900, margin: '0 auto', padding: '0 24px' }}>
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

          {/* Dashboard Preview - floating */}
          <div style={{ marginTop: 72, animation: 'float 6s ease-in-out infinite' }}>
            <div style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', inset: -1, borderRadius: 24, background: 'linear-gradient(135deg,rgba(124,58,237,0.5),rgba(96,165,250,0.2),rgba(124,58,237,0.15))', zIndex: 0 }} />
              <div style={{ position: 'relative', zIndex: 1, borderRadius: 22, background: 'rgba(6,6,18,0.96)', overflow: 'hidden', backdropFilter: 'blur(20px)', boxShadow: '0 40px 80px rgba(0,0,0,0.6),0 0 60px rgba(124,58,237,0.08)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', background: 'rgba(255,255,255,0.02)' }}>
                  <div style={{ width: 11, height: 11, borderRadius: '50%', background: '#ff5f57' }} />
                  <div style={{ width: 11, height: 11, borderRadius: '50%', background: '#febc2e' }} />
                  <div style={{ width: 11, height: 11, borderRadius: '50%', background: '#28c840' }} />
                  <span style={{ marginLeft: 12, fontSize: 12, color: 'rgba(255,255,255,0.3)', fontWeight: 500 }}>Neuro � Live Detection Dashboard</span>
                  <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#4ade80', fontWeight: 700 }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#4ade80', display: 'inline-block', animation: 'pulse 2s infinite' }} /> LIVE
                  </span>
                </div>
                <div style={{ padding: 24, display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
                  {[
                    { label: 'Threats Blocked', value: '1,247', delta: '↑ 12% today', color: '#a78bfa', bg: 'rgba(124,58,237,0.1)', border: 'rgba(124,58,237,0.2)' },
                    { label: 'Detection Rate', value: '99.8%', delta: 'Industry leading', color: '#60a5fa', bg: 'rgba(96,165,250,0.08)', border: 'rgba(96,165,250,0.2)' },
                    { label: 'Response Time', value: '8ms', delta: 'Real-time analysis', color: '#34d399', bg: 'rgba(52,211,153,0.08)', border: 'rgba(52,211,153,0.2)' },
                  ].map((card, i) => (
                    <div key={i} style={{ background: card.bg, border: `1px solid ${card.border}`, borderRadius: 16, padding: '18px 20px' }}>
                      <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>{card.label}</div>
                      <div style={{ fontSize: 28, fontWeight: 900, color: card.color, marginBottom: 4 }}>{card.value}</div>
                      <div style={{ fontSize: 11, color: '#4ade80' }}>{card.delta}</div>
                    </div>
                  ))}
                  <div style={{ gridColumn: '1 / -1', background: 'rgba(255,255,255,0.015)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 16, padding: '16px 20px' }}>
                    <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>Live Threat Feed</div>
                    {[
                      { type: 'Deepfake Video', source: 'Social Media Upload', status: 'BLOCKED', dot: '#f87171' },
                      { type: 'Voice Clone', source: 'Call Center API', status: 'FLAGGED', dot: '#fbbf24' },
                      { type: 'Face Swap Image', source: 'Document Verification', status: 'BLOCKED', dot: '#f87171' },
                      { type: 'GAN-generated Face', source: 'KYC Portal', status: 'CLEARED', dot: '#4ade80' },
                    ].map((item, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: i < 3 ? '1px solid rgba(255,255,255,0.04)' : 'none', fontSize: 13 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div style={{ width: 7, height: 7, borderRadius: '50%', background: item.dot, boxShadow: `0 0 6px ${item.dot}` }} />
                          <span style={{ color: 'rgba(255,255,255,0.75)' }}>{item.type}</span>
                        </div>
                        <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12 }}>{item.source}</span>
                        <span style={{ fontSize: 11, fontWeight: 800, color: item.dot, letterSpacing: 0.5 }}>{item.status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* STATS */}
      <section style={{ padding: '80px 24px', position: 'relative' }}>
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
      <section id="features" style={{ padding: '100px 24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 64 }}>
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
      <section id="how-it-works" style={{ padding: '100px 24px', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 64 }}>
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
      <section id="solutions" style={{ padding: '100px 24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 64 }}>
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
      <section style={{ padding: '80px 24px' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', position: 'relative', borderRadius: 28, overflow: 'hidden', border: '1px solid rgba(124,58,237,0.35)', textAlign: 'center', padding: '80px 40px', background: 'rgba(5,5,15,0.4)', backdropFilter: 'blur(8px)' }}>
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
