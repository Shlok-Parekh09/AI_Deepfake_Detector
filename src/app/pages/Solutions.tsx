import { useNavigate } from 'react-router';
import { NeuroLogo } from '../components/NeuroLogo';
import { ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';

export default function Solutions() {
  const navigate = useNavigate();

  const solutions = [
    { 
      label: 'ENTERPRISE', 
      title: 'Corporate Security', 
      desc: 'Protect KYC workflows, video calls, and internal communications from AI-generated impostors.', 
      items: ['Executive identity protection', 'Real-time KYC validation', 'Employee fraud prevention'] 
    },
    { 
      label: 'GOVERNMENT', 
      title: 'Judicial & Forensics', 
      desc: 'Verify digital evidence with forensic-grade reports admissible in court and legal proceedings.', 
      items: ['Court-ready evidence reports', 'Bulk media screening', 'Classified on-premise deployment'] 
    },
    { 
      label: 'MEDIA', 
      title: 'Content Verification', 
      desc: 'Stop synthetic misinformation before it spreads across your platform or publication.', 
      items: ['Automated content screening', 'Provenance tracking', 'Publisher trust scores'] 
    },
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

      {/* SOLUTIONS SECTION */}
      <section style={{ padding: '140px 24px 100px', position: 'relative', zIndex: 2 }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <button onClick={() => navigate('/')} style={{
            display: 'flex', alignItems: 'center', gap: 8, border: 'none', background: 'transparent',
            color: 'rgba(255,255,255,0.6)', fontSize: 14, fontWeight: 500, cursor: 'pointer', marginBottom: 40,
          }} onMouseEnter={e => e.currentTarget.style.color = '#fff'} onMouseLeave={e => e.currentTarget.style.color = 'rgba(255,255,255,0.6)'}>
            <ArrowLeft size={18} /> Back to Home
          </button>

          <div style={{ textAlign: 'center', marginBottom: 80 }}>
            <span style={{ color: '#a78bfa', fontSize: 12, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase' }}>Solutions</span>
            <h1 style={{ fontSize: 56, fontWeight: 900, marginTop: 16, marginBottom: 24, letterSpacing: '-1.5px' }}>Built for Every Use Case</h1>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 18, maxWidth: 600, margin: '0 auto', lineHeight: 1.6 }}>
              From enterprise security to government forensics, Neuro provides tailored solutions for organizations that need to verify digital authenticity.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(350px,1fr))', gap: 24 }}>
            {solutions.map((s, i) => (
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
                <span style={{ color: '#a78bfa', fontSize: 11, fontWeight: 700, letterSpacing: 2 }}>{s.label}</span>
                <h3 style={{ fontSize: 24, fontWeight: 800, margin: 0 }}>{s.title}</h3>
                <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 15, lineHeight: 1.7, margin: 0 }}>{s.desc}</p>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {s.items.map((item, j) => (
                    <li key={j} style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 14, color: 'rgba(255,255,255,0.7)' }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#7c3aed', flexShrink: 0 }} />
                      {item}
                    </li>
                  ))}
                </ul>
                <button onClick={() => navigate('/analyze')} style={{
                  marginTop: 12, alignSelf: 'flex-start',
                  border: '1.5px solid rgba(124,58,237,0.5)', borderRadius: 50,
                  padding: '10px 24px', background: 'transparent',
                  color: '#a78bfa', fontSize: 14, fontWeight: 600, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 8, transition: 'all .2s',
                }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.15)'; }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                >
                  Learn more <ArrowRight size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      <style>{`
        @media(max-width:768px){.nav-links{display:none!important}}
      `}</style>
    </div>
  );
}
