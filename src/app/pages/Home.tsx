import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router';
import { Shield, Eye, Zap, Lock, ArrowRight, Scan, Brain } from 'lucide-react';
import { NeuroLogo } from '../components/NeuroLogo';
import { SquareGridBackground } from '../components/SquareGridBackground';
import HiddenGame from '../components/HiddenGame';

export default function Home() {
  const navigate = useNavigate();
  const [mousePos, setMousePos] = useState({ x: -1000, y: -1000 });
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isGameUnlocked, setIsGameUnlocked] = useState(false);
  const virtualScroll = useRef(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    const handleWheel = (e: WheelEvent) => {
      if (isGameUnlocked) return;

      const maxScroll = 1200; // Virtual scroll distance required
      virtualScroll.current += e.deltaY;
      virtualScroll.current = Math.max(0, Math.min(virtualScroll.current, maxScroll));

      let progress = (virtualScroll.current / maxScroll) * 100;
      setScrollProgress(progress);

      if (progress >= 100) {
        setIsGameUnlocked(true);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('wheel', handleWheel, { passive: true });

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('wheel', handleWheel);
    };
  }, [isGameUnlocked]);

  return (
    <div style={{ height: '100vh', overflow: 'hidden', background: '#05050f', color: '#fff', fontFamily: "'Inter', sans-serif", cursor: 'none' }}>

      {/* SQUARE GRID BACKGROUND */}
      <SquareGridBackground />
      {/* Removed page-overlay to eliminate darkness */}

      {/* GIANT POINTED ARROW CURSOR */}
      <div style={{
        position: 'fixed',
        top: mousePos.y,
        left: mousePos.x,
        width: 48,
        height: 48,
        pointerEvents: 'none',
        zIndex: 9999,
        transform: 'translate(-10px, -10px)',
      }}>
        <svg viewBox="0 0 24 24" fill="none" stroke="#ffffffff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: '100%', height: '100%', filter: 'drop-shadow(0 0 10px rgba(56,189,248,0.8))' }}>
          <path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z" fill="rgba(0, 0, 0, 0.3)" />
        </svg>
      </div>

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
                style={{ color: 'rgba(255,255,255,0.6)', fontSize: 14, fontWeight: 500, textDecoration: 'none', transition: 'color .2s', cursor: 'none' }}
                onMouseEnter={e => (e.currentTarget.style.color = '#fff')}
                onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.6)')}
              >{l}</a>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button onClick={() => navigate('/login')} style={{
              border: '1.5px solid rgba(255,255,255,0.25)', borderRadius: 50,
              padding: '9px 24px', background: 'transparent', color: '#fff',
              fontSize: 14, fontWeight: 600, cursor: 'none', transition: 'all .2s',
            }}>Log In</button>
            <button onClick={() => navigate('/analyze')} style={{
              background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              border: 'none', borderRadius: 50, padding: '10px 26px',
              color: '#fff', fontSize: 14, fontWeight: 700, cursor: 'none',
              boxShadow: '0 0 24px rgba(124,58,237,0.4)', transition: 'all .2s',
            }}>Get Started</button>
          </div>
        </div>
      </nav>

      {/* INTERACTIVE HERO SECTION (VIRTUAL SCROLL) */}
      <section style={{
        height: '100vh',
        position: 'relative',
        zIndex: 3,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        padding: '68px 24px 24px',
      }}>
        {!isGameUnlocked ? (
          <div style={{ width: '100%', maxWidth: 860, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            {/* The text container shrinks and fades out as you scroll */}
            <div style={{ opacity: Math.max(0, 1 - scrollProgress / 70), transform: `scale(${1 - (scrollProgress / 100) * 0.05})`, transition: 'opacity 0.1s, transform 0.1s' }}>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                border: '1px solid rgba(124,58,237,0.6)', borderRadius: 50,
                padding: '7px 20px', marginBottom: 36,
                background: 'rgba(124,58,237,0.15)', backdropFilter: 'blur(12px)',
                fontSize: 13, color: 'rgba(255,255,255,0.85)', fontWeight: 600,
              }}>
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#a78bfa', display: 'inline-block', animation: 'pulse 2s infinite' }} />
                AI-Powered Deepfake & Synthetic Media Detection
              </div>

              <h1 style={{
                fontSize: 'clamp(44px, 8vw, 88px)',
                fontWeight: 900,
                lineHeight: 1.05,
                marginBottom: 24,
                letterSpacing: '-2px',
                color: '#17b4f7ff',
                textShadow: '0 0 15px rgba(0, 0, 0, 0.6), 1px 1px 0 #165c5c, 2px 2px 0 #165c5c, 3px 3px 0 #165c5c, 4px 4px 0 #165c5c, 5px 5px 0 #165c5c, 6px 6px 0 #165c5c, 6px 6px 20px rgba(68,216,216,0.8)'
              }}>
                Detect. Verify. Protect Reality.
              </h1>

              <p style={{ fontSize: 18, color: 'rgba(255,255,255,0.6)', maxWidth: 560, margin: '0 auto 40px', lineHeight: 1.7 }}>
                Forensic-grade deepfake detection for videos, images, and audio. Upload any file and get a multi-layer assessment in seconds.
              </p>
            </div>

            {/* Loading Bar Below Text */}
            <div style={{ width: '100%', maxWidth: 400, marginTop: 20 }}>
              <div style={{
                width: '100%',
                height: 10,
                background: 'rgba(255,255,255,0.05)',
                borderRadius: 5,
                overflow: 'hidden',
                position: 'relative',
                border: '1px solid rgba(255,255,255,0.1)'
              }}>
                <div style={{
                  position: 'absolute',
                  top: 0, left: 0, bottom: 0,
                  width: `${scrollProgress}%`,
                  background: 'linear-gradient(90deg, #7c3aed, #4f46e5)',
                  boxShadow: '0 0 30px rgba(124,58,237,0.6)',
                  transition: 'width 0.1s ease-out'
                }} />
              </div>
              <div style={{ marginTop: 20, fontSize: 16, color: '#a78bfa', fontWeight: 700, letterSpacing: 3 }}>
                LOADING {Math.round(scrollProgress)}%
              </div>
            </div>
          </div>
        ) : (
          <HiddenGame />
        )}
      </section>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
        @keyframes fadeIn { from{opacity:0; transform:translateY(30px)} to{opacity:1; transform:translateY(0)} }
        * { margin:0; padding:0; box-sizing:border-box; }
        @media(max-width:768px){.nav-links{display:none!important}}
        
        ::-webkit-scrollbar { display: none; }
      `}</style>
    </div>
  );
}
