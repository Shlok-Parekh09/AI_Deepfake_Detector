import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Video, Mic, Image as ImageIcon, ArrowRight } from 'lucide-react';
import svgPaths from '../../imports/MacBookPro166/svg-vk1owfvmuu';

export default function AnalysisType() {
  const navigate = useNavigate();
  const [hoveredType, setHoveredType] = useState<string | null>(null);

  const analysisTypes = [
    {
      id: 'video',
      icon: Video,
      title: 'Video Analysis',
      badge: 'DEEPFAKE VIDEO',
      description: 'Detect deepfakes in video content. Analyzes facial movements, lip sync, temporal consistency, and spatiotemporal patterns across frames.',
      formats: 'Supports: MP4, AVI, MOV, MKV, WEBM',
      color: 'from-blue-500 to-blue-600',
    },
    {
      id: 'audio',
      icon: Mic,
      title: 'Audio Analysis',
      badge: 'VOICE CLONE',
      description: 'Identify AI-cloned or synthetically generated voices. Examines spectral patterns, breath artifacts, and frequency anomalies.',
      formats: 'Supports: MP3, WAV, AAC, FLAC, OGG, M4A',
      color: 'from-purple-500 to-purple-600',
    },
    {
      id: 'image',
      icon: ImageIcon,
      title: 'Image Analysis',
      badge: 'SYNTHETIC IMAGE',
      description: 'Uncover GAN-generated, face-swapped, or manipulated images. Uses pixel-level forensics and JPEG-based scoring.',
      formats: 'Supports: JPG, JPEG, PNG, WEBP, BMP, TIFF',
      color: 'from-green-500 to-green-600',
    },
  ];

  const handleSelectType = (type: string) => {
    navigate(`/upload?type=${type}`);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white relative overflow-hidden">
      {/* Animated background stars */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              opacity: Math.random() * 0.5 + 0.2,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <div className="relative z-10 flex items-center justify-between px-8 py-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8">
            <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 47 47">
              <path d={svgPaths.p3be4e980} fill="#60A5FA" />
            </svg>
          </div>
          <span className="text-xl font-bold">Neuro</span>
        </div>
        <button
          onClick={() => navigate('/home')}
          className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-2"
        >
          ← Back to Home
        </button>
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 py-16">
        {/* Badge */}
        <div className="text-center mb-8">
          <span className="inline-block px-4 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full text-blue-400 text-xs font-medium tracking-wider">
            ⚡ CHOOSE ANALYSIS TYPE
          </span>
        </div>

        {/* Title */}
        <h1 className="text-5xl md:text-6xl font-bold text-center mb-4">
          What Are You <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">Analyzing?</span>
        </h1>
        <p className="text-center text-gray-400 text-lg mb-16">
          Select media type to begin forensic-grade deepfake detection
        </p>

        {/* Analysis Type Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {analysisTypes.map((type) => {
            const Icon = type.icon;
            return (
              <div
                key={type.id}
                onMouseEnter={() => setHoveredType(type.id)}
                onMouseLeave={() => setHoveredType(null)}
                onClick={() => handleSelectType(type.id)}
                className="relative group cursor-pointer"
              >
                <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 hover:border-blue-500/50 transition-all duration-300 h-full">
                  {/* Icon */}
                  <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${type.color} flex items-center justify-center mb-6`}>
                    <Icon size={32} className="text-white" />
                  </div>

                  {/* Title and Badge */}
                  <div className="mb-4">
                    <h3 className="text-2xl font-bold mb-2">{type.title}</h3>
                    <span className="inline-block px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded text-blue-400 text-xs font-medium">
                      {type.badge}
                    </span>
                  </div>

                  {/* Description */}
                  <p className="text-gray-400 text-sm mb-4 leading-relaxed">
                    {type.description}
                  </p>

                  {/* Formats */}
                  <p className="text-gray-500 text-xs mb-6">
                    {type.formats}
                  </p>

                  {/* Arrow */}
                  <div className="flex items-center justify-end">
                    <div className={`w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center group-hover:bg-blue-600 transition-all duration-300 ${hoveredType === type.id ? 'translate-x-2' : ''}`}>
                      <ArrowRight size={20} />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Note */}
        <p className="text-center text-gray-600 text-sm">
          All uploads are processed securely. Files are never stored beyond the analysis session.
        </p>
      </div>
    </div>
  );
}
