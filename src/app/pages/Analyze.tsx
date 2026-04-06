import { useNavigate } from 'react-router';
import { GandivaBowLogo } from '../components/GandivaBowLogo';
import { ArrowLeft, Video, Mic, Image } from 'lucide-react';

const options = [
  {
    id: 'video',
    label: 'VIDEO ANALYSIS',
    description: 'Detect deepfakes in video content. Analyzes facial movements, lip sync, temporal consistency, and spatiotemporal patterns across frames.',
    icon: Video,
    bg: 'https://images.unsplash.com/photo-1616469829581-73993eb86b02?w=900&q=80',
    supported: 'MP4, AVI, MOV, MKV, WEBM',
    accent: '#f97316',
  },
  {
    id: 'audio',
    label: 'AUDIO ANALYSIS',
    description: 'Identify AI-cloned or synthetically generated voices. Examines spectral patterns, breath artifacts, and frequency anomalies.',
    icon: Mic,
    bg: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=900&q=80',
    supported: 'MP3, WAV, AAC, FLAC, OGG, M4A',
    accent: '#fbbf24',
  },
  {
    id: 'image',
    label: 'IMAGE ANALYSIS',
    description: 'Uncover GAN-generated, face-swapped, or manipulated images. Uses pixel-level forensics and ROC-based scoring.',
    icon: Image,
    bg: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=900&q=80',
    supported: 'JPG, JPEG, PNG, WEBP, BMP, TIFF',
    accent: '#f97316',
  },
];

export default function Analyze() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <button onClick={() => navigate('/home')} className="flex items-center gap-3">
              <GandivaBowLogo size={36} />
              <span className="text-xl font-bold" style={{ fontFamily: "'Eagle Lake', serif" }}>Gandiva</span>
            </button>
            <button
              onClick={() => navigate('/home')}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
            >
              <ArrowLeft size={16} /> Back
            </button>
          </div>
        </div>
      </nav>

      <div className="pt-28 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <span className="text-orange-500 text-xs font-bold uppercase tracking-widest block mb-4">Choose Analysis Type</span>
            <h1 className="text-4xl sm:text-5xl font-black mb-4 tracking-tight">
              What Are You{' '}
              <span className="text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(90deg, #f97316, #fbbf24)' }}>
                Analyzing?
              </span>
            </h1>
            <p className="text-gray-400">Select the type of media to start AI-powered deepfake detection</p>
          </div>

          {/* Vertical Cards */}
          <div className="flex flex-col gap-5">
            {options.map((opt) => {
              const Icon = opt.icon;
              return (
                <button
                  key={opt.id}
                  onClick={() => navigate(`/analyze/${opt.id}`)}
                  className="group relative w-full rounded-2xl overflow-hidden text-left transition-all duration-300 hover:scale-[1.01] focus:outline-none"
                  style={{ height: '180px' }}
                >
                  {/* Background image */}
                  <div
                    className="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
                    style={{ backgroundImage: `url(${opt.bg})` }}
                  />
                  {/* Dark overlay */}
                  <div className="absolute inset-0 bg-black/60 group-hover:bg-black/50 transition-colors duration-300" />
                  {/* Gradient overlay */}
                  <div
                    className="absolute inset-0"
                    style={{ background: `linear-gradient(135deg, rgba(0,0,0,0.8) 0%, transparent 60%, rgba(0,0,0,0.4) 100%)` }}
                  />
                  {/* Border glow on hover */}
                  <div
                    className="absolute inset-0 rounded-2xl border-2 border-transparent group-hover:border-opacity-60 transition-all duration-300"
                    style={{ borderColor: opt.accent + '60' }}
                  />

                  {/* Content */}
                  <div className="relative z-10 h-full flex items-center gap-6 px-8">
                    {/* Icon box */}
                    <div
                      className="flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center border-2"
                      style={{
                        backgroundColor: opt.accent + '20',
                        borderColor: opt.accent + '60',
                      }}
                    >
                      <Icon size={28} style={{ color: opt.accent }} />
                    </div>

                    {/* Text */}
                    <div className="flex-1">
                      <div
                        className="text-xl font-black tracking-wide mb-1.5"
                        style={{ color: opt.accent }}
                      >
                        {opt.label}
                      </div>
                      <p className="text-gray-300 text-sm leading-relaxed mb-2 max-w-lg">
                        {opt.description}
                      </p>
                      <span className="text-xs text-gray-500">
                        Supports: <span className="text-gray-400">{opt.supported}</span>
                      </span>
                    </div>

                    {/* Arrow */}
                    <div
                      className="flex-shrink-0 w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300 group-hover:scale-110"
                      style={{ borderColor: opt.accent + '50', color: opt.accent }}
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          <p className="text-center text-xs text-gray-600 mt-8">
            All uploads are processed securely. Files are never stored beyond the analysis session.
          </p>
        </div>
      </div>
    </div>
  );
}
