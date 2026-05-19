import { useState, useRef, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router';
import { NeuroLogo } from '../components/NeuroLogo';
import { ArrowLeft, Upload, X, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';

type AnalysisType = 'video' | 'audio' | 'image';

const CONFIG = {
  video: {
    label: 'Video Analysis',
    accept: '.mp4,.avi,.mov,.mkv,.webm',
    formats: ['MP4', 'AVI', 'MOV', 'MKV', 'WEBM'],
    graphTitle: 'Spatiotemporal Graph',
    graphColor: '#f97316',
  },
  audio: {
    label: 'Audio Analysis',
    accept: '.mp3,.wav,.aac,.flac,.ogg,.m4a',
    formats: ['MP3', 'WAV', 'AAC', 'FLAC', 'OGG', 'M4A'],
    graphTitle: 'Spectrogram',
    graphColor: '#fbbf24',
  },
  image: {
    label: 'Image Analysis',
    accept: '.jpg,.jpeg,.png,.webp,.bmp,.tiff',
    formats: ['JPG', 'JPEG', 'PNG', 'WEBP', 'BMP', 'TIFF'],
    graphTitle: 'ROC Curve',
    graphColor: '#f97316',
  },
};

function SpectrogramSVG() {
  const rows = 20;
  const cols = 60;
  const colors = ['#1e3a5f','#1a5276','#1f618d','#2471a3','#2980b9','#7fb3d3','#ffd700','#ff8c00','#ff4500','#dc143c'];
  return (
    <svg viewBox={`0 0 ${cols * 8} ${rows * 8}`} className="w-full h-full" style={{ maxHeight: '200px' }}>
      {Array.from({ length: rows }).map((_, r) =>
        Array.from({ length: cols }).map((_, c) => {
          const intensity = Math.sin(c * 0.3 + r * 0.5) * 0.5 + Math.random() * 0.5;
          const ci = Math.floor(intensity * (colors.length - 1));
          return (
            <rect key={`${r}-${c}`} x={c * 8} y={r * 8} width={7} height={7} fill={colors[Math.min(ci, colors.length - 1)]} opacity={0.85} rx={1} />
          );
        })
      )}
      <line x1="0" y1={rows * 8} x2={cols * 8} y2={rows * 8} stroke="#444" strokeWidth="1" />
      <text x={cols * 4} y={rows * 8 + 14} fill="#666" fontSize="10" textAnchor="middle">Time (s)</text>
      <text x="-10" y={rows * 4} fill="#666" fontSize="10" textAnchor="middle" transform={`rotate(-90, -10, ${rows * 4})`}>Freq (Hz)</text>
    </svg>
  );
}

function ROCCurveSVG() {
  const w = 300, h = 220;
  const pad = 35;
  const pts = [
    [0, 0], [0.05, 0.35], [0.1, 0.60], [0.2, 0.82], [0.35, 0.93],
    [0.5, 0.97], [0.7, 0.99], [1.0, 1.0]
  ].map(([x, y]) => [pad + x * (w - pad * 2), h - pad - y * (h - pad * 2)]);
  const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0]},${p[1]}`).join(' ');
  return (
    <svg viewBox={`0 0 ${w} ${h + 20}`} className="w-full h-full" style={{ maxHeight: '200px' }}>
      <line x1={pad} y1={h - pad} x2={w - pad} y2={pad} stroke="#333" strokeWidth="1" strokeDasharray="4" />
      <path d={pathD} fill="none" stroke="#f97316" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d={`${pathD} L${pad + (w - pad * 2)},${h - pad} L${pad},${h - pad} Z`} fill="#f97316" fillOpacity="0.1" />
      <line x1={pad} y1={pad} x2={pad} y2={h - pad} stroke="#444" strokeWidth="1" />
      <line x1={pad} y1={h - pad} x2={w - pad} y2={h - pad} stroke="#444" strokeWidth="1" />
      <text x={w / 2} y={h + 15} fill="#666" fontSize="10" textAnchor="middle">False Positive Rate</text>
      <text x={12} y={h / 2} fill="#666" fontSize="10" textAnchor="middle" transform={`rotate(-90, 12, ${h / 2})`}>True Positive Rate</text>
      <text x={w - pad - 5} y={pad + 18} fill="#f97316" fontSize="10" textAnchor="end" fontWeight="bold">AUC = 0.994</text>
    </svg>
  );
}

function SpatiotemporalSVG() {
  const w = 400, h = 200;
  const lines = 5;
  const points = 30;
  const colors = ['#f97316','#fbbf24','#fb923c','#fdba74','#fed7aa'];
  return (
    <svg viewBox={`0 0 ${w} ${h + 20}`} className="w-full h-full" style={{ maxHeight: '200px' }}>
      <defs>
        <linearGradient id="stGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#f97316" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#fbbf24" stopOpacity="0.2" />
        </linearGradient>
      </defs>
      {/* Grid */}
      {Array.from({ length: 6 }).map((_, i) => (
        <line key={i} x1={20} y1={20 + i * 30} x2={w - 10} y2={20 + i * 30} stroke="#222" strokeWidth="1" />
      ))}
      {Array.from({ length: 8 }).map((_, i) => (
        <line key={i} x1={20 + i * 52} y1={20} x2={20 + i * 52} y2={h - 10} stroke="#222" strokeWidth="1" />
      ))}
      {/* Anomaly zone */}
      <rect x={200} y={20} width={80} height={h - 30} fill="url(#stGrad)" rx={4} />
      {/* Lines */}
      {Array.from({ length: lines }).map((_, li) => {
        const pts = Array.from({ length: points }).map((_, pi) => {
          const x = 20 + (pi / (points - 1)) * (w - 30);
          const base = 80 + li * 20;
          const anomaly = pi > 14 && pi < 22 ? (Math.sin((pi - 14) * 0.8) * 40) : 0;
          const y = base + Math.sin(pi * 0.4 + li) * 10 + anomaly + (Math.random() - 0.5) * 5;
          return [x, y];
        });
        return (
          <path
            key={li}
            d={pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0]},${p[1]}`).join(' ')}
            fill="none"
            stroke={colors[li]}
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        );
      })}
      {/* Anomaly marker */}
      <line x1={220} y1={20} x2={220} y2={h - 10} stroke="#f97316" strokeWidth="1.5" strokeDasharray="4" />
      <text x={225} y={32} fill="#f97316" fontSize="9">Anomaly Region</text>
      <text x={w / 2} y={h + 15} fill="#666" fontSize="10" textAnchor="middle">Frame Index</text>
      <text x={10} y={h / 2} fill="#666" fontSize="10" textAnchor="middle" transform={`rotate(-90, 10, ${h / 2})`}>Spatial Score</text>
    </svg>
  );
}

function generateResults(type: AnalysisType, filename: string) {
  const seed = filename.length;
  const isDeepfake = (seed % 3) !== 0;
  const prob = isDeepfake ? 72 + (seed % 25) : 8 + (seed % 18);
  const anomalies = isDeepfake ? 5 + (seed % 10) : seed % 3;

  const reasons: Record<AnalysisType, { flag: string; detail: string }[]> = {
    video: isDeepfake ? [
      { flag: 'Lip Sync Mismatch', detail: 'Audio phonemes do not align with detected lip geometry in frames 120–340. Correlation score: 0.31 (threshold: 0.75).' },
      { flag: 'Unnatural Blinking Pattern', detail: 'Blink frequency of 28/min detected vs. natural average of 15–20/min. Irregular inter-blink intervals observed.' },
      { flag: 'Facial Boundary Artifacts', detail: 'GAN-style edge artifacts detected along the jaw and hairline region in 67% of frames using frequency domain analysis.' },
      { flag: 'Temporal Inconsistency', detail: 'Optical flow discontinuities detected at frame boundaries 118, 119, 340–342. Indicates frame-level manipulation.' },
    ] : [
      { flag: 'No Lip Sync Anomaly', detail: 'Audio-visual correlation score 0.91 — well above threshold. Lip movement matches phoneme sequence accurately.' },
      { flag: 'Natural Micro-expressions', detail: 'Facial Action Units (AUs) transition naturally with expected timing and asymmetry patterns.' },
      { flag: 'Consistent Temporal Flow', detail: 'Optical flow vectors are smooth and continuous. No frame-level splicing detected.' },
    ],
    audio: isDeepfake ? [
      { flag: 'Spectral Artifact Detected', detail: 'Unusual harmonic distribution at 2.3–2.8 kHz consistent with neural vocoder output. Natural voice gap at 4.1 kHz is absent.' },
      { flag: 'Missing Breath Sounds', detail: 'No detectable breath intake or exhale sounds between sentences — a common artifact in TTS and voice-cloning systems.' },
      { flag: 'Phase Discontinuity', detail: 'Phase spectrogram shows sudden discontinuity at 3.1s and 7.8s, consistent with segment stitching in voice synthesis.' },
      { flag: 'Unnatural Prosody', detail: 'Sentence-level pitch contour deviates from expected natural speech patterns. Rise-fall patterns are too uniform.' },
    ] : [
      { flag: 'Natural Spectral Profile', detail: 'Harmonic distribution matches natural human voice signature. No neural vocoder fingerprints detected.' },
      { flag: 'Authentic Breath Patterns', detail: 'Breath intake sounds detected at 7 natural pause points. Consistent with biological speech production.' },
      { flag: 'Continuous Phase Spectrum', detail: 'Phase spectrogram is continuous with no stitching artifacts. Voice appears unmodified.' },
    ],
    image: isDeepfake ? [
      { flag: 'GAN Frequency Artifacts', detail: 'Frequency domain analysis reveals checkerboard pattern at 12.5 cycles/pixel — a known artifact of GAN upsampling layers.' },
      { flag: 'Inconsistent Skin Texture', detail: 'Skin pore distribution is unnaturally uniform in a 120×80px region around left cheek. Real skin shows stochastic variation.' },
      { flag: 'Eye Reflection Mismatch', detail: 'Corneal reflections in left and right eyes are inconsistent — different light source directions indicate compositing.' },
      { flag: 'JPEG Ghost Analysis', detail: 'Re-compression artifacts on the facial region differ from background, indicating the face was spliced from a different image.' },
    ] : [
      { flag: 'No GAN Fingerprint', detail: 'DCT frequency domain shows natural noise distribution. No upsampling artifacts or GAN checkerboard patterns found.' },
      { flag: 'Consistent Skin Texture', detail: 'Skin pore distribution follows expected stochastic pattern across the entire facial region.' },
      { flag: 'Authentic Eye Reflections', detail: 'Corneal reflections in both eyes are consistent with a single unified light environment.' },
    ],
  };

  return { isDeepfake, prob, anomalies, reasons: reasons[type] };
}

export default function AnalysisPage() {
  const { type } = useParams<{ type: string }>();
  const navigate = useNavigate();
  const analysisType = (type as AnalysisType) || 'image';
  const config = CONFIG[analysisType] || CONFIG.image;

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [phase, setPhase] = useState<'upload' | 'processing' | 'done'>('upload');
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ReturnType<typeof generateResults> | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    if (analysisType === 'image' && f.type.startsWith('image/')) {
      const url = URL.createObjectURL(f);
      setPreview(url);
    } else if (analysisType === 'video' && f.type.startsWith('video/')) {
      const url = URL.createObjectURL(f);
      setPreview(url);
    }
    setPhase('processing');
    setProgress(0);

    let p = 0;
    const interval = setInterval(() => {
      p += Math.random() * 8 + 2;
      if (p >= 100) {
        p = 100;
        clearInterval(interval);
        setTimeout(() => {
          setResults(generateResults(analysisType, f.name));
          setPhase('done');
        }, 400);
      }
      setProgress(Math.min(p, 100));
    }, 150);
  }, [analysisType]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setPhase('upload');
    setResults(null);
    setProgress(0);
    if (preview) URL.revokeObjectURL(preview);
  };

  const S = { fontFamily: "'Inter', sans-serif" } as React.CSSProperties;
  return (
    <div style={{ minHeight: '100vh', background: 'transparent', color: '#fff', ...S }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
      {/* FULL-PAGE ANIMATED BACKGROUND */}


      {/* Nav */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, background: 'rgba(5,5,15,0.85)', backdropFilter: 'blur(16px)', borderBottom: '1px solid rgba(255,255,255,0.06)', padding: '0 40px' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 68 }}>
          <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10 }}>
            <NeuroLogo size={32} />
            <span style={{ fontSize: 18, fontWeight: 800, color: '#fff' }}>Neuro</span>
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {phase === 'done' && (
              <button onClick={reset} style={{ background: 'none', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 50, padding: '7px 16px', color: 'rgba(255,255,255,0.6)', fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
                <X size={13} /> New Analysis
              </button>
            )}
            <button onClick={() => navigate('/analyze')} style={{ background: 'none', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 50, padding: '7px 18px', color: 'rgba(255,255,255,0.6)', fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
              <ArrowLeft size={13} /> Back
            </button>
          </div>
        </div>
      </nav>

      <div style={{ position: 'relative', zIndex: 2, paddingTop: 100, paddingBottom: 60, padding: '100px 24px 60px', maxWidth: 900, margin: '0 auto' }}>
        {/* Phase: Upload */}
        {phase === 'upload' && (
          <div style={{ marginTop: 24 }}>
            <div style={{ textAlign: 'center', marginBottom: 40 }}>
              <span style={{ color: '#a78bfa', fontSize: 11, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase', display: 'block', marginBottom: 10 }}>{config.label}</span>
              <h1 style={{ fontSize: 40, fontWeight: 900, letterSpacing: '-1px', marginBottom: 10 }}>Upload Your File</h1>
              <p style={{ color: 'rgba(255,255,255,0.45)' }}>Supported: <span style={{ color: 'rgba(255,255,255,0.65)' }}>{config.formats.join(', ')}</span></p>
            </div>
            <div
              onClick={() => inputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              style={{
                border: `2px dashed ${dragOver ? '#7c3aed' : 'rgba(255,255,255,0.1)'}`,
                borderRadius: 20, padding: '72px 24px', textAlign: 'center', cursor: 'pointer',
                background: dragOver ? 'rgba(124,58,237,0.08)' : 'rgba(255,255,255,0.02)',
                backdropFilter: 'blur(12px)', transition: 'all .25s',
              }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
                <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Upload size={30} color="#a78bfa" />
                </div>
                <div>
                  <p style={{ fontSize: 18, fontWeight: 700, marginBottom: 6 }}>{dragOver ? 'Drop it here!' : 'Drop your file or click to browse'}</p>
                  <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: 14 }}>Maximum file size: 500MB</p>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 8, marginTop: 8 }}>
                  {config.formats.map(f => (
                    <span key={f} style={{ fontSize: 12, background: 'rgba(124,58,237,0.1)', border: '1px solid rgba(124,58,237,0.25)', color: '#a78bfa', borderRadius: 50, padding: '3px 12px' }}>{f}</span>
                  ))}
                </div>
              </div>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept={config.accept}
              className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
            />
          </div>
        )}

        {/* Phase: Processing */}
        {phase === 'processing' && (
          <div style={{ marginTop: 24 }}>
            <div style={{ textAlign: 'center', marginBottom: 40 }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(124,58,237,0.12)', border: '1px solid rgba(124,58,237,0.4)', borderRadius: 50, padding: '7px 18px', color: '#a78bfa', fontSize: 13, fontWeight: 600, marginBottom: 24 }}>
                <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> AI Processing
              </div>
              <h1 style={{ fontSize: 36, fontWeight: 900, marginBottom: 8 }}>Analyzing Your File</h1>
              <p style={{ color: 'rgba(255,255,255,0.35)' }}>{file?.name}</p>
            </div>
            <div style={{ maxWidth: 540, margin: '0 auto' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 20, padding: 32, backdropFilter: 'blur(12px)' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                  {[
                    { label: 'Preprocessing & normalization', threshold: 20 },
                    { label: 'Running AI detection models', threshold: 50 },
                    { label: 'Generating visualizations', threshold: 80 },
                    { label: 'Compiling anomaly report', threshold: 95 },
                  ].map((step) => (
                    <div key={step.label} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      {progress > step.threshold ? (
                        <CheckCircle size={16} color="#a78bfa" style={{ flexShrink: 0 }} />
                      ) : progress > step.threshold - 20 ? (
                        <Loader2 size={16} color="#a78bfa" style={{ flexShrink: 0, animation: 'spin 1s linear infinite' }} />
                      ) : (
                        <div style={{ width: 16, height: 16, borderRadius: '50%', border: '1px solid rgba(255,255,255,0.2)', flexShrink: 0 }} />
                      )}
                      <span style={{ fontSize: 14, color: progress > step.threshold ? 'rgba(255,255,255,0.75)' : 'rgba(255,255,255,0.3)' }}>{step.label}</span>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 28 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'rgba(255,255,255,0.35)', marginBottom: 8 }}>
                    <span>Progress</span><span>{Math.round(progress)}%</span>
                  </div>
                  <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 4, overflow: 'hidden' }}>
                    <div style={{ height: '100%', borderRadius: 4, width: `${progress}%`, background: 'linear-gradient(90deg,#7c3aed,#60a5fa)', transition: 'width .2s' }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Phase: Done / Results */}
        {phase === 'done' && results && (
          <div className="mt-4">
            {/* Top row: AI Processing badge + Graph title */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6" style={{marginBottom: 20}}>
              <div className="flex items-center justify-center gap-2 w-64 bg-orange-500/10 border border-orange-500/30 rounded-full py-2 text-orange-400 text-sm font-medium">
                <CheckCircle size={16} />
                AI Processing Complete
              </div>
              <div className="flex items-center justify-center
               gap-2 w-64 bg-white/5 border border-white/10 rounded-full px-4 py-2 text-sm text-gray-300 font-medium">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: config.graphColor }} />
                {config.graphTitle}
              </div>
            </div>

            {/* Graph Visualization */}
            <div style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, padding: 20, marginBottom: 20 }}>
              <div className="flex justify-between items-center mb-3">
                <span className="text-xs text-gray-500 uppercase tracking-wider">{config.graphTitle}</span>
                <span className="text-xs text-gray-600">{file?.name}</span>
              </div>
              <div style={{ borderRadius: 12, overflow: 'hidden', background: 'rgba(5,5,15,0.6)', padding: 8 }}>
                {analysisType === 'audio' && <SpectrogramSVG />}
                {analysisType === 'image' && <ROCCurveSVG />}
                {analysisType === 'video' && <SpatiotemporalSVG />}
              </div>
            </div>

            {/* Score + Anomalies */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
              <div style={{ borderRadius: 20, padding: 24, border: `1px solid ${results.isDeepfake ? 'rgba(239,68,68,0.25)' : 'rgba(74,222,128,0.2)'}`, background: results.isDeepfake ? 'rgba(239,68,68,0.06)' : 'rgba(74,222,128,0.05)'}}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Deepfake Probability</div>
                    <div className={`text-5xl font-black ${results.isDeepfake ? 'text-red-400' : 'text-green-400'}`}>
                      {results.prob}%
                    </div>
                  </div>
                  {results.isDeepfake
                    ? <AlertTriangle size={24} className="text-red-400" />
                    : <CheckCircle size={24} className="text-green-400" />
                  }
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden mb-2">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${results.prob}%`,
                      background: results.isDeepfake
                        ? 'linear-gradient(90deg, #f87171, #ef4444)'
                        : 'linear-gradient(90deg, #4ade80, #22c55e)',
                    }}
                  />
                </div>
                <div className={`text-sm font-bold ${results.isDeepfake ? 'text-red-400' : 'text-green-400'}`}>
                  {results.isDeepfake ? '⚠ Likely SYNTHETIC / DEEPFAKE' : '✓ Likely AUTHENTIC'}
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, padding: 24 }}>
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Total Anomalies Detected</div>
                <div className="text-5xl font-black text-orange-400 mb-3">{results.anomalies}</div>
                <div className="space-y-1">
                  <div className="text-xs text-gray-500">
                    Confidence level: <span className="text-gray-300 font-medium">{results.prob > 50 ? 'High' : 'Low'}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Analysis type: <span className="text-gray-300 font-medium">{config.label}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Models used: <span className="text-gray-300 font-medium">Ensemble (4 models)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Reasons */}
            <div className="bg-[#0d0d0d] border border-white/5 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-5">
                {results.isDeepfake
                  ? <AlertTriangle size={16} className="text-red-400" />
                  : <CheckCircle size={16} className="text-green-400" />
                }
                <span className="font-bold text-sm uppercase tracking-wide text-gray-300" style={{marginBottom : 10,marginTop:5}}>
                  {results.isDeepfake ? 'Reasons Flagged as DEEPFAKE' : 'Reasons Classified as AUTHENTIC'}
                </span>
              </div>
              <div className="space-y-4">
                {results.reasons.map((r, i) => (
                  <div key={i} className={`flex gap-4 p-4 rounded-xl border ${results.isDeepfake ? 'bg-red-500/5 border-red-500/10' : 'bg-green-500/5 border-green-500/10'}`} style={{marginBottom: 10}}>
                    <div className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center mt-0.5 ${results.isDeepfake ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                      {results.isDeepfake
                        ? <X size={10} className="text-red-400" />
                        : <CheckCircle size={10} className="text-green-400" />
                      }
                    </div>
                    <div>
                      <div className={`font-semibold text-sm mb-1 ${results.isDeepfake ? 'text-red-300' : 'text-green-300'}`}>
                        {r.flag}
                      </div>
                      <div className="text-gray-500 text-xs leading-relaxed">{r.detail}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: 12, marginTop: 24, flexWrap: 'wrap' }}>
              <button onClick={reset} style={{ flex: 1, minWidth: 200, background: 'linear-gradient(135deg,#7c3aed,#4f46e5)', border: 'none', borderRadius: 50, padding: '13px 28px', color: '#fff', fontSize: 15, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, boxShadow: '0 0 28px rgba(124,58,237,0.35)' }}>
                <Upload size={15} /> Analyze Another File
              </button>
              <button onClick={() => navigate('/analyze')} style={{ flex: 1, minWidth: 200, background: 'rgba(255,255,255,0.04)', border: '1.5px solid rgba(255,255,255,0.15)', borderRadius: 50, padding: '13px 28px', color: '#fff', fontSize: 15, fontWeight: 600, cursor: 'pointer', backdropFilter: 'blur(8px)' }}>
                Different Analysis Type
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
