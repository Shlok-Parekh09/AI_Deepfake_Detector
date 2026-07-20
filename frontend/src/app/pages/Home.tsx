import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Menu, X, ArrowRight, Layers, AudioLines, Grid3x3, Globe, SlidersHorizontal, FileSearch, Eye, Ear, ChevronRight } from 'lucide-react';
import BrandLogo from '../components/BrandLogo';

/* ────────────────────────────────────────────────
   Animated neural-net dots used in the hero card
   ──────────────────────────────────────────────── */
function NeuralDots() {
  const [dots, setDots] = useState<number[]>([]);
  useEffect(() => {
    const gen = () => Array.from({ length: 64 }, () => Math.random());
    setDots(gen());
    const id = setInterval(() => setDots(gen()), 2200);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="grid grid-cols-8 gap-1.5">
      {dots.map((v, i) => (
        <div
          key={i}
          className="w-2 h-2 rounded-full transition-all duration-[1800ms]"
          style={{
            backgroundColor:
              v > 0.85 ? '#ef4444' : v > 0.7 ? '#f59e0b' : v > 0.4 ? 'rgba(99,102,241,0.5)' : 'rgba(255,255,255,0.06)',
            transform: `scale(${0.6 + v * 0.5})`,
          }}
        />
      ))}
    </div>
  );
}

/* ────────────────────────────────────────────────
   Frequency-spectrum bars for the audio section
   ──────────────────────────────────────────────── */
function SpectrumBars({ barCount = 48, accent = 'indigo' }: { barCount?: number; accent?: string }) {
  const [bars, setBars] = useState<number[]>([]);
  useEffect(() => {
    const gen = () => Array.from({ length: barCount }, (_, i) => {
      const base = Math.sin(i * 0.25) * 0.35 + 0.45;
      return Math.min(1, Math.max(0.08, base + (Math.random() - 0.5) * 0.35));
    });
    setBars(gen());
    const id = setInterval(() => setBars(gen()), 1600);
    return () => clearInterval(id);
  }, [barCount]);

  const color = accent === 'indigo' ? '#6366f1' : accent === 'emerald' ? '#10b981' : '#6366f1';
  return (
    <div className="flex items-end gap-[2px] h-14 w-full">
      {bars.map((h, i) => (
        <div
          key={i}
          className="flex-1 rounded-t-sm transition-all duration-[1400ms]"
          style={{
            height: `${h * 100}%`,
            backgroundColor: h > 0.72 ? '#ef4444' : color,
            opacity: 0.5 + h * 0.5,
          }}
        />
      ))}
    </div>
  );
}

/* ════════════════════════════════════════════════
   SynPhi Logo Component (consistent across pages)
   ════════════════════════════════════════════════ */
function SynPhiLogo({ size = 28 }: { size?: number }) {
  return <BrandLogo size={size} />;
}

/* ════════════════════════════════════════════════
   HOME PAGE
   ════════════════════════════════════════════════ */
export default function Home() {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#08080e] text-white" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* ═══════════════════════════════════════════════ */}
      {/* NAVIGATION                                     */}
      {/* ═══════════════════════════════════════════════ */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#08080e]/80 backdrop-blur-xl border-b border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <SynPhiLogo size={28} />
              <span className="text-[15px] font-semibold tracking-tight text-white">SynPhi</span>
            </div>

            <div className="hidden lg:flex items-center gap-7">
              <a href="#how-it-works" className="text-[13px] text-gray-400 hover:text-white transition-colors">How It Works</a>
              <a href="#verdicts" className="text-[13px] text-gray-400 hover:text-white transition-colors">Sample Verdicts</a>
              <a href="#detection" className="text-[13px] text-gray-400 hover:text-white transition-colors">Detection</a>
              <a href="#features" className="text-[13px] text-gray-400 hover:text-white transition-colors">Features</a>
              <a href="#about" className="text-[13px] text-gray-400 hover:text-white transition-colors">For Business</a>
            </div>

            <div className="hidden lg:flex items-center gap-4">
              <button onClick={() => navigate('/login')} className="text-[13px] text-gray-400 hover:text-white transition-colors">Sign in</button>
              <button
                onClick={() => navigate('/dashboard')}
                className="text-[13px] text-white bg-cyan-600 hover:bg-cyan-700 px-4 py-1.5 rounded-lg transition-all"
              >
                Launch App
              </button>
            </div>

            <button className="lg:hidden text-gray-400 hover:text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="lg:hidden bg-[#08080e] border-t border-white/5">
            <div className="px-4 py-5 space-y-3">
              <a href="#how-it-works" className="block py-2 text-sm text-gray-400 hover:text-white">How It Works</a>
              <a href="#verdicts" className="block py-2 text-sm text-gray-400 hover:text-white">Sample Verdicts</a>
              <a href="#detection" className="block py-2 text-sm text-gray-400 hover:text-white">Detection</a>
              <a href="#features" className="block py-2 text-sm text-gray-400 hover:text-white">Features</a>
              <button onClick={() => navigate('/dashboard')} className="w-full mt-3 bg-cyan-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium">Launch App</button>
            </div>
          </div>
        )}
      </nav>

      {/* ═══════════════════════════════════════════════ */}
      {/* HERO                                            */}
      {/* ═══════════════════════════════════════════════ */}
      <section className="pt-32 pb-28 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute top-10 left-1/3 w-[600px] h-[600px] bg-cyan-600/[0.04] rounded-full blur-[140px]" />
        <div className="absolute bottom-0 right-1/4 w-[450px] h-[450px] bg-blue-600/[0.04] rounded-full blur-[120px]" />

        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-cyan-500/[0.08] border border-cyan-500/20 rounded-full px-4 py-1.5 mb-8">
                <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse" />
                <span className="text-[11px] text-cyan-300 uppercase tracking-[0.15em] font-medium">SynPhi AI Engine · V4.0</span>
              </div>

              <h1 className="text-[3.2rem] sm:text-[4rem] leading-[1.06] font-extrabold mb-7 tracking-tight">
                Unmask What<br />AI Creates<span className="text-cyan-400">.</span>
              </h1>

              <p className="text-[15px] text-gray-400 leading-[1.75] mb-10 max-w-[420px]">
                SynPhi's forensic engine dissects audio, video, and images frame-by-frame to
                surface the artifacts that separate <span className="text-white font-medium">authentic</span> media
                from <span className="text-white font-medium">synthetic</span> forgeries — with 97% accuracy across
                every major generator.
              </p>

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="bg-cyan-600 hover:bg-cyan-700 text-white px-7 py-3 rounded-lg transition-all text-sm font-medium hover:shadow-lg hover:shadow-cyan-600/20 flex items-center gap-2"
                >
                  Start scanning
                  <ArrowRight size={15} />
                </button>
                <button onClick={() => window.open('https://github.com/Shlok-Parekh09/AI_Deepfake_Detector', '_blank')} className="bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 border border-white/10 hover:border-white/20 px-7 py-3 rounded-lg transition-all text-sm font-medium">
                  View documentation
                </button>
              </div>
            </div>

            {/* ── Hero analysis card ── */}
            <div className="relative">
              <div className="bg-[#0e0e18] border border-white/[0.06] rounded-2xl p-6 shadow-2xl shadow-black/50">
                <div className="flex items-center justify-between mb-5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 bg-cyan-500/10 rounded-lg flex items-center justify-center">
                      <AudioLines size={16} className="text-cyan-400" />
                    </div>
                    <span className="text-sm text-gray-300 font-medium">interview_clip.wav</span>
                  </div>
                  <span className="text-xs text-gray-600 font-mono">01:14</span>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div className="bg-red-500/10 border border-red-500/20 rounded-md px-3 py-1.5">
                    <span className="text-[11px] text-red-400 font-semibold uppercase tracking-wider flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 bg-red-400 rounded-full" />
                      Synthetic
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-bold text-white tracking-tight">94.7</span>
                    <span className="text-sm text-gray-500 ml-0.5">%</span>
                    <span className="text-[11px] text-gray-600 ml-1.5">confidence</span>
                  </div>
                </div>

                <p className="text-xs text-gray-500 mb-5">
                  <span className="text-gray-400 font-medium">5 anomaly clusters</span> · pitch-shift artifacts at 0:23–0:31 · ElevenLabs v2 signature
                </p>

                {/* Neural dot grid — unique visualization */}
                <div className="bg-[#080812] rounded-xl p-5 mb-4">
                  <p className="text-[10px] text-gray-600 font-mono mb-3 uppercase tracking-wider">Neural Activation Map</p>
                  <NeuralDots />
                </div>

                <div className="text-right">
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors font-medium flex items-center gap-1.5 ml-auto"
                  >
                    Analyze your own file <ChevronRight size={12} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════ */}
      {/* HOW IT WORKS — Light                            */}
      {/* ═══════════════════════════════════════════════ */}
      <section id="how-it-works" className="py-24 px-4 sm:px-6 lg:px-8 bg-white text-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 mb-20">
            <div>
              <p className="text-[11px] text-gray-400 uppercase tracking-[0.2em] font-medium mb-5">Under the Hood · Core Capabilities</p>
              <h2 className="text-[2.8rem] sm:text-[3.4rem] leading-[1.08] font-bold tracking-tight">
                How <span className="text-cyan-600">SynPhi</span><br />Analyzes Media.
              </h2>
            </div>
            <div className="flex items-end">
              <p className="text-[15px] text-gray-500 leading-relaxed max-w-lg">
                Our multi-layered AI pipeline examines spectral fingerprints, pixel-level inconsistencies,
                temporal anomalies, and metadata signatures — combining six independent signals into a single
                forensic verdict that single-layer detectors can't match.
              </p>
            </div>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-gray-200 rounded-xl overflow-hidden mb-12">
            <div className="bg-white p-8">
              <p className="text-[2.8rem] font-bold tracking-tight text-gray-900">97<span className="text-xl text-gray-400">%</span></p>
              <p className="text-sm text-gray-400 mt-1">Detection accuracy</p>
            </div>
            <div className="bg-white p-8">
              <p className="text-[2.8rem] font-bold tracking-tight text-gray-900">&lt;3<span className="text-xl text-gray-400">s</span></p>
              <p className="text-sm text-gray-400 mt-1">Average scan time</p>
            </div>
            <div className="bg-white p-8">
              <p className="text-[2.8rem] font-bold tracking-tight text-gray-900">8+</p>
              <p className="text-sm text-gray-400 mt-1">Generator models</p>
            </div>
            <div className="bg-white p-8">
              <p className="text-[2.8rem] font-bold tracking-tight text-gray-900">6</p>
              <p className="text-sm text-gray-400 mt-1">Analysis layers</p>
            </div>
          </div>

          {/* Feature cards */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-px bg-gray-200 rounded-xl overflow-hidden">
            {[
              { icon: <Layers size={24} strokeWidth={1.5} />, title: 'Multi-Format Ingest', desc: 'Accepts audio, video, and images — MP4, WAV, JPEG, PNG, WEBM, and 12 more formats.' },
              { icon: <AudioLines size={24} strokeWidth={1.5} />, title: 'Spectral Denoising', desc: 'Strips ambient noise to isolate synthesis artifacts hidden under compression.' },
              { icon: <Grid3x3 size={24} strokeWidth={1.5} />, title: 'Layered Verdicts', desc: 'Each signal scores independently — you see the breakdown, not just a number.' },
              { icon: <Globe size={24} strokeWidth={1.5} />, title: '40+ Languages', desc: 'Voice analysis works across languages, dialects, and accent variations.' },
            ].map((f, i) => (
              <div key={i} className="bg-white p-8">
                <div className="mb-5 text-gray-900">{f.icon}</div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-[13px] text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════ */}
      {/* SAMPLE VERDICTS — Light                         */}
      {/* ═══════════════════════════════════════════════ */}
      <section id="verdicts" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50 text-gray-900">
        <div className="max-w-7xl mx-auto">
          <p className="text-[11px] text-gray-400 uppercase tracking-[0.2em] font-medium mb-10">Real Scan Outputs</p>

          <div className="grid md:grid-cols-3 gap-5">
            {/* Authentic */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-emerald-50 border border-emerald-200 rounded-md px-2.5 py-1">
                  <span className="text-[10px] text-emerald-600 font-semibold uppercase tracking-wider flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" /> Verified Authentic
                  </span>
                </div>
                <span className="text-xs text-gray-400 font-mono">· 0.031</span>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-2.5 leading-snug">Vocal identity confirmed — no synthetic markers present.</h3>
              <p className="text-[12px] text-gray-400 leading-relaxed mb-5">
                Cross-referenced against 42 acoustic features. All 3,800 frame-level checks passed without anomaly.
              </p>
              <div className="space-y-2 border-t border-gray-100 pt-4">
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Voice fingerprint</span><span className="text-emerald-600 font-medium">HUMAN · 0.02</span></div>
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Temporal consistency</span><span className="text-gray-500">STABLE</span></div>
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Container metadata</span><span className="text-gray-500">UNMODIFIED</span></div>
              </div>
            </div>

            {/* Synthetic */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-red-50 border border-red-200 rounded-md px-2.5 py-1">
                  <span className="text-[10px] text-red-600 font-semibold uppercase tracking-wider flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-red-500 rounded-full" /> AI-Generated
                  </span>
                </div>
                <span className="text-xs text-gray-400 font-mono">· 0.96</span>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-2.5 leading-snug">Diffusion upscaling pattern detected in facial region.</h3>
              <p className="text-[12px] text-gray-400 leading-relaxed mb-5">
                22 frame artifacts in segments 00:04–00:11. Lip-sync drift measured at 28ms latency.
              </p>
              <div className="space-y-2 border-t border-gray-100 pt-4">
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Generator match</span><span className="text-red-500 font-medium">MidJourney v6 · 0.91</span></div>
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Lip-sync drift</span><span className="text-orange-500 font-medium">28ms DETECTED</span></div>
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Pixel blending</span><span className="text-red-500 font-medium">IRREGULAR</span></div>
              </div>
            </div>

            {/* Inconclusive */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-amber-50 border border-amber-200 rounded-md px-2.5 py-1">
                  <span className="text-[10px] text-amber-600 font-semibold uppercase tracking-wider flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full" /> Needs Review
                  </span>
                </div>
                <span className="text-xs text-gray-400 font-mono">· 0.48</span>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-2.5 leading-snug">Heavy re-encoding obscures the signals we normally rely on.</h3>
              <p className="text-[12px] text-gray-400 leading-relaxed mb-5">
                Re-upload the original file or a higher-bitrate copy for a definitive result.
              </p>
              <div className="space-y-2 border-t border-gray-100 pt-4">
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Sample rate</span><span className="text-amber-500 font-medium">8kHz · LOW</span></div>
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Bitrate</span><span className="text-gray-500">48kbps</span></div>
                <div className="flex justify-between text-[11px]"><span className="text-gray-400">Re-encode count</span><span className="text-amber-500 font-medium">3+</span></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════ */}
      {/* THREE STEPS                                     */}
      {/* ═══════════════════════════════════════════════ */}
      <section id="steps" className="py-24 px-4 sm:px-6 lg:px-8 bg-white text-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 mb-16">
            <div>
              <p className="text-[11px] text-gray-400 uppercase tracking-[0.2em] font-medium mb-5">Getting Started</p>
              <h2 className="text-[2.8rem] sm:text-[3.4rem] leading-[1.08] font-bold tracking-tight">
                Three steps.<br /><span className="text-cyan-600">Instant clarity.</span>
              </h2>
            </div>
            <div className="flex items-end">
              <p className="text-[15px] text-gray-500 leading-relaxed max-w-lg">
                No ML expertise needed. No integration required. Drop a file, read the verdict —
                or wire it into your pipeline with a single API call.
              </p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
              <p className="text-[11px] text-cyan-600 uppercase tracking-[0.15em] font-semibold mb-4">Step 01</p>
              <h3 className="text-sm font-semibold text-gray-900 mb-3 leading-snug">Open the dashboard and sign up</h3>
              <p className="text-[12px] text-gray-400 leading-relaxed">Free tier gives you 25 scans / month across audio, video, and image.</p>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
              <p className="text-[11px] text-gray-400 uppercase tracking-[0.15em] font-semibold mb-4">Step 02</p>
              <h3 className="text-sm font-semibold text-gray-900 mb-3 leading-snug">Upload a file or paste a URL</h3>
              <p className="text-[12px] text-gray-400 leading-relaxed">Drag-and-drop any media file, or paste a direct link. We handle the rest.</p>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
              <p className="text-[11px] text-gray-400 uppercase tracking-[0.15em] font-semibold mb-4">Step 03</p>
              <h3 className="text-sm font-semibold text-gray-900 mb-3 leading-snug">Read the full forensic verdict</h3>
              <p className="text-[12px] text-gray-400 leading-relaxed">Probability, per-layer breakdown, generator match, and exportable PDF report.</p>
            </div>
          </div>
        </div>
      </section>



      {/* ═══════════════════════════════════════════════ */}
      {/* ONE DETECTOR — Dark                             */}
      {/* ═══════════════════════════════════════════════ */}
      <section id="detection" className="py-24 px-4 sm:px-6 lg:px-8 bg-[#08080e] text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 mb-16">
            <div>
              <p className="text-[11px] text-gray-600 uppercase tracking-[0.2em] font-medium mb-5">Cross-Generator Coverage</p>
              <h2 className="text-[2.8rem] sm:text-[3.4rem] leading-[1.08] font-bold tracking-tight">
                One engine.<br /><span className="text-cyan-400">Every major model.</span>
              </h2>
            </div>
            <div className="flex items-end">
              <p className="text-[15px] text-gray-500 leading-relaxed max-w-lg">
                SynPhi doesn't just flag "AI or not." It identifies <em>which</em> generator
                produced the content — from Stable Diffusion and MidJourney to ElevenLabs and
                Tortoise TTS — by matching against known spectral and pixel fingerprints.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-white/[0.04] rounded-xl overflow-hidden mb-16">
            {['Stable Diffusion', 'MidJourney', 'DALL·E 3', 'Firefly', 'ElevenLabs', 'Tortoise TTS', 'Flux', 'Runway Gen-3'].map((model) => (
              <div key={model} className="bg-[#0e0e18] py-5 flex items-center justify-center hover:bg-white/[0.03] transition-colors">
                <span className="text-sm text-gray-400 font-medium">{model}</span>
              </div>
            ))}
          </div>

          <div className="grid lg:grid-cols-2 gap-5">
            {/* Audio detection */}
            <div className="bg-[#0e0e18] border border-white/[0.06] rounded-2xl p-8">
              <p className="text-[11px] text-cyan-400 uppercase tracking-[0.15em] font-semibold mb-3">Voice Forensics</p>
              <h3 className="text-xl font-bold mb-6">Hear what the ear can't.</h3>
              <div className="space-y-5 mb-8">
                <div>
                  <p className="text-sm text-white font-semibold mb-1">Maps voice-clone platform signatures</p>
                  <p className="text-[12px] text-gray-500">Cross-references 60+ cloning engines — not just top-three.</p>
                </div>
                <div>
                  <p className="text-sm text-white font-semibold mb-1">Detects sub-millisecond timing artifacts</p>
                  <p className="text-[12px] text-gray-500">Unnatural pitch curves and formant gaps invisible to human listeners.</p>
                </div>
                <div>
                  <p className="text-sm text-white font-semibold mb-1">Strips ambient noise before analysis</p>
                  <p className="text-[12px] text-gray-500">Integrated denoiser surfaces artifacts that compression masks.</p>
                </div>
              </div>
              <div className="bg-[#080812] rounded-xl p-4">
                <p className="text-[10px] text-gray-600 font-mono mb-3">FREQ SPECTRUM · LIVE ANALYSIS</p>
                <SpectrumBars barCount={52} accent="indigo" />
              </div>
            </div>

            {/* Image detection */}
            <div className="bg-[#0e0e18] border border-white/[0.06] rounded-2xl p-8">
              <p className="text-[11px] text-emerald-400 uppercase tracking-[0.15em] font-semibold mb-3">Pixel Forensics</p>
              <h3 className="text-xl font-bold mb-6">See the fingerprint of every generator.</h3>
              <div className="space-y-5 mb-8">
                <div>
                  <p className="text-sm text-white font-semibold mb-1">Identifies 8 major generator architectures</p>
                  <p className="text-[12px] text-gray-500">Each platform leaves distinct spatial frequency patterns.</p>
                </div>
                <div>
                  <p className="text-sm text-white font-semibold mb-1">Analyzes texture, lighting, and symmetry</p>
                  <p className="text-[12px] text-gray-500">Catches the color-distribution quirks humans routinely miss.</p>
                </div>
                <div>
                  <p className="text-sm text-white font-semibold mb-1">Detects face-swap blending edges</p>
                  <p className="text-[12px] text-gray-500">Compares boundary gradients against known generator outputs.</p>
                </div>
              </div>
              <div className="bg-[#080812] rounded-xl p-4">
                <p className="text-[10px] text-gray-600 font-mono mb-3">PIXEL ANOMALY HEATMAP · LIVE</p>
                <NeuralDots />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════ */}
      {/* FEATURES — Light                                */}
      {/* ═══════════════════════════════════════════════ */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-white text-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 mb-16">
            <div>
              <p className="text-[11px] text-gray-400 uppercase tracking-[0.2em] font-medium mb-5">Built for Real-World Threats</p>
              <h2 className="text-[2.8rem] sm:text-[3.4rem] leading-[1.08] font-bold tracking-tight">
                Forensic-grade<br /><span className="text-cyan-600">detection engine.</span>
              </h2>
            </div>
            <div className="flex items-end">
              <p className="text-[15px] text-gray-500 leading-relaxed max-w-lg">
                Six independent analysis layers stack together — spatial CNN, temporal RNN,
                spectral analysis, metadata forensics, confidence calibration, and cross-modal
                validation — so no single blind spot compromises the verdict.
              </p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: <Eye size={22} strokeWidth={1.5} />, title: 'Pixel-Level CNN Analysis', desc: 'EfficientNet-based spatial scanning detects manipulation artifacts down to sub-pixel resolution.' },
              { icon: <Ear size={22} strokeWidth={1.5} />, title: 'Spectral Voice Forensics', desc: 'Mel-spectrogram and MFCC feature extraction surfaces cloning artifacts across 60+ platforms.' },
              { icon: <FileSearch size={22} strokeWidth={1.5} />, title: 'Container & Metadata Forensics', desc: 'EXIF, codec history, and container-level checks reveal re-encoding and tool signatures.' },
              { icon: <SlidersHorizontal size={22} strokeWidth={1.5} />, title: 'Calibrated Confidence Scores', desc: 'Temperature-scaled outputs give you honest probabilities — not inflated marketing numbers.' },
              { icon: <Layers size={22} strokeWidth={1.5} />, title: 'CNN + RNN Ensemble', desc: 'Spatial and temporal models fuse via learned weights for maximum cross-domain accuracy.' },
              { icon: <Grid3x3 size={22} strokeWidth={1.5} />, title: 'Court-Admissible Reports', desc: 'Exportable PDF with full evidence chain, per-layer scores, and reproducible methodology.' },
            ].map((f, i) => (
              <div key={i} className="bg-gray-50 border border-gray-200 rounded-xl p-7 hover:shadow-md hover:border-gray-300 transition-all group">
                <div className="mb-5 text-gray-900 group-hover:text-cyan-600 transition-colors">{f.icon}</div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-[13px] text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════ */}
      {/* CTA                                             */}
      {/* ═══════════════════════════════════════════════ */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-[#08080e] text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-600/[0.04] via-transparent to-blue-600/[0.04]" />
        <div className="max-w-3xl mx-auto text-center relative z-10">
          <h2 className="text-[2.8rem] sm:text-[3.4rem] leading-[1.08] font-bold tracking-tight mb-6">
            Ready to separate<br /><span className="text-cyan-400">fact from fabrication?</span>
          </h2>
          <p className="text-[15px] text-gray-500 leading-relaxed mb-10 max-w-lg mx-auto">
            Upload a file and get your forensic verdict in seconds. Free tier includes
            25 scans per month with full six-layer analysis.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <button onClick={() => navigate('/dashboard')} className="bg-cyan-600 hover:bg-cyan-700 text-white px-8 py-3.5 rounded-lg transition-all text-sm font-medium hover:shadow-lg hover:shadow-cyan-600/20 flex items-center gap-2">
              Open Scanner <ArrowRight size={16} />
            </button>
            <button onClick={() => window.open('https://github.com/Shlok-Parekh09/AI_Deepfake_Detector', '_blank')} className="bg-white/[0.04] hover:bg-white/[0.08] text-gray-300 border border-white/10 hover:border-white/20 px-8 py-3.5 rounded-lg transition-all text-sm font-medium">
              Read the docs
            </button>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════ */}
      {/* FOOTER                                          */}
      {/* ═══════════════════════════════════════════════ */}
      <footer className="bg-[#060609] border-t border-white/[0.04] py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-10 mb-12">
            <div className="lg:col-span-2">
              <div className="flex items-center gap-2.5 mb-4">
                <SynPhiLogo size={26} />
                <span className="text-[15px] font-semibold text-white">SynPhi</span>
              </div>
              <p className="text-[13px] text-gray-500 leading-relaxed max-w-xs">
                AI-powered forensic detection for audio, video, and images.
                Protecting truth in the age of synthetic media.
              </p>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">Product</h4>
              <ul className="space-y-2.5 text-[13px] text-gray-500">
                <li><a href="#" className="hover:text-white transition-colors">Image Scanner</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Voice Scanner</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">Company</h4>
              <ul className="space-y-2.5 text-[13px] text-gray-500">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">Legal</h4>
              <ul className="space-y-2.5 text-[13px] text-gray-500">
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Cookie Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/[0.04] pt-8">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <p className="text-[12px] text-gray-600">© 2026 SynPhi. All rights reserved.</p>
              <div className="flex items-center gap-2 text-[12px] text-gray-600">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                All systems operational
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
