import { useNavigate } from 'react-router';
import { GandivaBowLogo } from '../components/GandivaBowLogo';
import { ArrowLeft, Upload, Cpu, BarChart3, Shield, ChevronRight, CheckCircle, AlertTriangle } from 'lucide-react';

export default function HowItWorks() {
  const navigate = useNavigate();

  const steps = [
    {
      number: "01",
      title: "Upload Your Media",
      description: "Upload any video, audio, or image file. Gandiva supports all major formats including MP4, AVI, MOV for video; MP3, WAV, FLAC for audio; and JPEG, PNG, WebP for images.",
      icon: Upload,
      color: "from-orange-500/20 to-orange-600/10",
      border: "border-orange-500/30",
      iconColor: "text-orange-400",
    },
    {
      number: "02",
      title: "AI Preprocessing",
      description: "The media is broken into frames (video), segments (audio), or pixel matrices (image). Our preprocessing pipeline normalizes, denoises, and prepares the data for deep analysis using industry-standard techniques.",
      icon: Cpu,
      color: "from-yellow-500/20 to-yellow-600/10",
      border: "border-yellow-500/30",
      iconColor: "text-yellow-400",
    },
    {
      number: "03",
      title: "Multimodal Detection",
      description: "Gandiva's AI ensemble runs multiple specialized neural networks simultaneously — vision transformers for spatial artifacts, RNNs for temporal inconsistencies, and spectral CNNs for audio frequency anomalies.",
      icon: Shield,
      color: "from-orange-500/20 to-yellow-500/10",
      border: "border-orange-400/30",
      iconColor: "text-orange-300",
    },
    {
      number: "04",
      title: "Results & Insights",
      description: "Get a detailed deepfake probability score, anomaly count, visual graphs (Spectrograms, ROC Curves, Spatiotemporal Graphs), and a plain-language explanation of every suspicious pattern detected.",
      icon: BarChart3,
      color: "from-yellow-500/20 to-orange-500/10",
      border: "border-yellow-400/30",
      iconColor: "text-yellow-300",
    },
  ];

  const techniques = [
    {
      title: "GAN Artifact Detection",
      description: "Generative Adversarial Networks leave subtle frequency-domain fingerprints invisible to the human eye. Our CNN models trained on 10M+ GAN-generated images identify these patterns with 99.8% accuracy.",
      tag: "Image & Video",
    },
    {
      title: "Temporal Inconsistency Analysis",
      description: "Real faces have consistent micro-expressions and natural motion blur between frames. We model optical flow and detect unnatural frame-to-frame transitions that deepfake generators struggle to replicate.",
      tag: "Video",
    },
    {
      title: "Audio Spectrogram Analysis",
      description: "Voice cloning models introduce unique spectral artifacts in the frequency domain. Our spectrogram CNNs detect unnatural harmonics, missing breath sounds, and phase discontinuities in cloned voices.",
      tag: "Audio",
    },
    {
      title: "Facial Landmark Geometry",
      description: "We track 468 facial landmarks per frame and measure geometric consistency. Deepfakes often show subtle distortions in ear shape, neck boundaries, and eye reflection patterns.",
      tag: "Image & Video",
    },
    {
      title: "Lip Sync Verification",
      description: "Cross-modal analysis correlates audio phonemes with lip movement geometry. A mismatch between spoken phonemes and lip shape is a strong indicator of video manipulation.",
      tag: "Video",
    },
    {
      title: "Metadata & Compression Forensics",
      description: "Every digital file carries metadata and compression signatures. Re-encoded or manipulated media breaks the original compression pattern, which our forensics engine detects at the binary level.",
      tag: "All Formats",
    },
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <button onClick={() => navigate('/home')} className="flex items-center gap-3 group">
              <GandivaBowLogo size={36} />
              <span className="text-xl font-bold" style={{ fontFamily: "'Eagle Lake', serif" }}>Gandiva</span>
            </button>
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/home')}
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
              >
                <ArrowLeft size={16} /> Back to Home
              </button>
              <button
                onClick={() => navigate('/analyze')}
                className="bg-orange-500 hover:bg-orange-400 text-black font-bold px-5 py-2 rounded-lg text-sm transition-colors"
              >
                Try It Now
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-orange-500/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="max-w-4xl mx-auto text-center relative">
          <span className="inline-block text-orange-500 text-xs font-bold uppercase tracking-widest mb-5">How It Works</span>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black mb-6 tracking-tight">
            AI That Thinks Like{' '}
            <span className="text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(90deg, #f97316, #fbbf24)' }}>
              a Forensic Expert
            </span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">
            Gandiva uses a multi-layer AI pipeline combining computer vision, spectral analysis, and temporal reasoning 
            to detect synthetic media with industry-leading accuracy.
          </p>
        </div>
      </section>

      {/* Steps */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="space-y-6">
            {steps.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={i} className={`flex flex-col sm:flex-row gap-6 bg-gradient-to-r ${step.color} border ${step.border} rounded-2xl p-8`}>
                  <div className="flex-shrink-0 flex sm:flex-col items-center sm:items-start gap-4">
                    <div className={`w-14 h-14 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center`}>
                      <Icon className={step.iconColor} size={26} />
                    </div>
                    <span className="text-5xl font-black text-white/10">{step.number}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                    <p className="text-gray-400 leading-relaxed">{step.description}</p>
                  </div>
                  {i < steps.length - 1 && (
                    <div className="hidden sm:flex items-center text-orange-500/30">
                      <ChevronRight size={24} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Technical Details */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-[#070707]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <span className="text-orange-500 text-xs font-bold uppercase tracking-widest block mb-4">Detection Techniques</span>
            <h2 className="text-3xl sm:text-4xl font-black mb-4">Under the Hood</h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Six specialized detection methods run in parallel to ensure nothing slips through.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {techniques.map((tech, i) => (
              <div key={i} className="bg-[#0d0d0d] border border-white/5 hover:border-orange-500/20 rounded-2xl p-6 transition-all duration-300">
                <div className="flex items-start justify-between mb-4">
                  <CheckCircle size={18} className="text-orange-400 mt-0.5 flex-shrink-0" />
                  <span className="text-xs font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded-full px-3 py-1">
                    {tech.tag}
                  </span>
                </div>
                <h3 className="font-bold text-white mb-3">{tech.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{tech.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Model Performance */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="bg-[#0d0d0d] border border-white/5 rounded-2xl p-8 sm:p-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
              <div>
                <span className="text-orange-500 text-xs font-bold uppercase tracking-widest block mb-4">Model Performance</span>
                <h2 className="text-3xl font-black mb-5">Benchmarked Against Industry Standards</h2>
                <p className="text-gray-400 mb-6 leading-relaxed">
                  Gandiva's detection models are tested monthly on public deepfake datasets including FaceForensics++, 
                  DFDC, and CelebDF. Our models consistently rank in the top tier for detection F1 score.
                </p>
                <div className="space-y-4">
                  {[
                    { label: "Image Deepfake Detection", value: 99.8, color: "#f97316" },
                    { label: "Audio Clone Detection", value: 97.4, color: "#fbbf24" },
                    { label: "Video Deepfake Detection", value: 98.1, color: "#f97316" },
                  ].map((m, i) => (
                    <div key={i}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-400">{m.label}</span>
                        <span className="font-bold" style={{ color: m.color }}>{m.value}%</span>
                      </div>
                      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-1000"
                          style={{ width: `${m.value}%`, background: `linear-gradient(90deg, ${m.color}, #fbbf24)` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-4">
                {[
                  { icon: AlertTriangle, label: "False Positive Rate", value: "< 0.2%", color: "text-yellow-400" },
                  { icon: Shield, label: "Processing Speed", value: "< 10ms per frame", color: "text-orange-400" },
                  { icon: CheckCircle, label: "Formats Supported", value: "40+ file types", color: "text-green-400" },
                  { icon: Cpu, label: "Model Parameters", value: "2.4 Billion", color: "text-orange-300" },
                ].map((m, i) => {
                  const Icon = m.icon;
                  return (
                    <div key={i} className="flex items-center gap-4 bg-white/3 border border-white/5 rounded-xl p-4">
                      <Icon size={20} className={m.color} />
                      <div className="flex-1">
                        <div className="text-xs text-gray-500">{m.label}</div>
                        <div className="font-bold text-white">{m.value}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-[#070707]">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-black mb-4">Ready to Detect?</h2>
          <p className="text-gray-400 mb-8">Upload your first file and get results in seconds.</p>
          <button
            onClick={() => navigate('/analyze')}
            className="bg-orange-500 hover:bg-orange-400 text-black font-bold px-10 py-4 rounded-xl text-base transition-all duration-200 inline-flex items-center gap-2"
            style={{ boxShadow: '0 0 40px rgba(249,115,22,0.25)' }}
          >
            Start Analysis <ChevronRight size={18} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-4 text-center text-gray-700 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <GandivaBowLogo size={18} />
          <span className="font-bold text-gray-600">Gandiva</span>
        </div>
        <p>&copy; 2026 Gandiva. All rights reserved.</p>
      </footer>
    </div>
  );
}
