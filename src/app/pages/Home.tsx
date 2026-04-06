import { useState } from 'react';
import { Menu, X, ChevronRight, Shield, Zap, Eye, Lock, Users, BarChart3, ArrowRight, CheckCircle } from 'lucide-react';

function GandivaBowLogo({ size = 40, className = '' }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M 14 3 Q 40 24 14 45"
        stroke="#f97316"
        strokeWidth="3.5"
        fill="none"
        strokeLinecap="round"
      />
      <line
        x1="14" y1="3"
        x2="14" y2="45"
        stroke="#fbbf24"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
      <line
        x1="14" y1="24"
        x2="38" y2="24"
        stroke="#fbbf24"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
      <polygon
        points="36,20 44,24 36,28"
        fill="#f97316"
      />
      <circle cx="14" cy="3" r="1.5" fill="#fbbf24" />
      <circle cx="14" cy="45" r="1.5" fill="#fbbf24" />
    </svg>
  );
}

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const features = [
    {
      icon: Shield,
      title: "Advanced Protection",
      description: "State-of-the-art AI security measures to protect your digital assets and identity from synthetic media threats.",
    },
    {
      icon: Eye,
      title: "Real-time Detection",
      description: "Instantly identify and flag deepfakes, AI-generated voices, and manipulated content with millisecond latency.",
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Process and analyze thousands of media files in real-time with our distributed AI infrastructure.",
    },
    {
      icon: Lock,
      title: "End-to-End Encryption",
      description: "Your data is encrypted at every stage of processing and storage with military-grade protocols.",
    },
    {
      icon: Users,
      title: "Team Collaboration",
      description: "Work seamlessly with your security team while maintaining strict access controls and audit logs.",
    },
    {
      icon: BarChart3,
      title: "Detailed Analytics",
      description: "Comprehensive dashboards and reports to track threats, patterns, and protection effectiveness.",
    },
  ];

  const useCases = [
    {
      label: "ENTERPRISE",
      title: "Enterprise Security",
      description: "Protect your organization from deepfakes and synthetic media threats at scale. Integrate seamlessly with your existing security stack.",
      items: ["Executive identity protection", "Internal media verification", "Employee fraud prevention"],
      image: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
    },
    {
      label: "MEDIA",
      title: "Content Verification",
      description: "Verify the authenticity of media content across your platforms instantly. Stop misinformation before it spreads.",
      items: ["Automated content screening", "Provenance tracking", "Publisher trust scores"],
      image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    },
    {
      label: "IDENTITY",
      title: "Identity Protection",
      description: "Safeguard personal and professional identities from manipulation and impersonation in the age of AI.",
      items: ["Face swap detection", "Voice cloning alerts", "Biometric verification"],
      image: "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80",
    },
  ];

  const stats = [
    { value: "99.8%", label: "Detection Accuracy" },
    { value: "50M+", label: "Media Analyzed" },
    { value: "500+", label: "Enterprise Clients" },
    { value: "<10ms", label: "Response Time" },
  ];

  const trustedBy = ["AXIS BANK", "HDFC LIFE", "INFOSYS", "WIPRO", "TATA GROUP", "RELIANCE"];

  return (
    <div className="min-h-screen bg-black text-white">

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-3">
              <GandivaBowLogo size={38} />
              <span
                className="text-2xl font-bold tracking-tight"
                style={{ fontFamily: "'Eagle Lake', serif" }}
              >
                Gandiva
              </span>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">Features</a>
              <a href="#use-cases" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">Solutions</a>
              <a href="#about" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">About</a>
              <a href="#contact" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">Contact</a>
              <button
                onClick={() => window.location.href = '/'}
                className="bg-orange-500 hover:bg-orange-400 text-black font-semibold px-6 py-2.5 rounded-lg transition-colors text-sm"
              >
                Get Started
              </button>
            </div>

            <button
              className="md:hidden text-gray-400 hover:text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden bg-black border-t border-white/10">
            <div className="px-4 py-5 space-y-4">
              <a href="#features" className="block text-gray-300 hover:text-white">Features</a>
              <a href="#use-cases" className="block text-gray-300 hover:text-white">Solutions</a>
              <a href="#about" className="block text-gray-300 hover:text-white">About</a>
              <a href="#contact" className="block text-gray-300 hover:text-white">Contact</a>
              <button className="w-full bg-orange-500 hover:bg-orange-400 text-black font-semibold px-6 py-3 rounded-lg">
                Get Started
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-orange-500/10 rounded-full blur-[120px]" />
          <div className="absolute top-20 left-1/4 w-[300px] h-[300px] bg-yellow-400/5 rounded-full blur-[80px]" />
        </div>

        <div className="relative max-w-7xl mx-auto">
          <div className="text-center max-w-5xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-2 text-sm text-gray-400 mb-8">
              <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
              AI-Powered Deepfake &amp; Synthetic Media Detection
            </div>

            <h1 className="text-5xl sm:text-6xl md:text-8xl font-black mb-6 leading-tight tracking-tight">
              Protect What's{' '}
              <span className="text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(90deg, #f97316, #fbbf24)' }}>
                Real.
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              Gandiva provides enterprise-grade AI detection and protection against deepfakes,
              synthetic media, and digital identity fraud — in real time.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={() => window.location.href = '/'}
                className="w-full sm:w-auto bg-orange-500 hover:bg-orange-400 text-black font-bold px-8 py-4 rounded-xl text-base transition-all duration-200 flex items-center justify-center gap-2"
                style={{ boxShadow: '0 0 40px rgba(249,115,22,0.25)' }}
              >
                Request Demo <ArrowRight size={18} />
              </button>
              <button className="w-full sm:w-auto bg-white/5 hover:bg-white/10 border border-white/10 text-white px-8 py-4 rounded-xl text-base font-semibold transition-all duration-200">
                See How It Works
              </button>
            </div>
          </div>

          {/* Dashboard Preview */}
          <div className="mt-20 relative">
            <div className="mx-auto max-w-4xl rounded-2xl border border-white/10 bg-[#0d0d0d] overflow-hidden" style={{ boxShadow: '0 40px 80px rgba(0,0,0,0.8)' }}>
              <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-[#111]">
                <div className="w-3 h-3 rounded-full bg-red-500/70" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                <div className="w-3 h-3 rounded-full bg-green-500/70" />
                <span className="ml-4 text-xs text-gray-500">Gandiva Detection Dashboard</span>
              </div>
              <div className="p-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-[#161616] rounded-xl p-4 border border-white/5">
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Threats Blocked</div>
                  <div className="text-3xl font-bold text-orange-400">1,247</div>
                  <div className="text-xs text-green-400 mt-1">↑ 12% today</div>
                </div>
                <div className="bg-[#161616] rounded-xl p-4 border border-white/5">
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Detection Rate</div>
                  <div className="text-3xl font-bold text-yellow-400">99.8%</div>
                  <div className="text-xs text-green-400 mt-1">Industry leading</div>
                </div>
                <div className="bg-[#161616] rounded-xl p-4 border border-white/5">
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Response Time</div>
                  <div className="text-3xl font-bold text-white">8ms</div>
                  <div className="text-xs text-green-400 mt-1">Real-time analysis</div>
                </div>
                <div className="col-span-1 sm:col-span-3 bg-[#161616] rounded-xl p-4 border border-white/5">
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-4">Live Threat Feed</div>
                  {[
                    { type: "Deepfake Video", source: "Social Media Upload", status: "BLOCKED", color: "text-red-400" },
                    { type: "Voice Clone", source: "Call Center API", status: "FLAGGED", color: "text-yellow-400" },
                    { type: "Face Swap Image", source: "Document Verification", status: "BLOCKED", color: "text-red-400" },
                    { type: "GAN-generated Face", source: "KYC Portal", status: "CLEARED", color: "text-green-400" },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0 text-sm">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${item.status === 'CLEARED' ? 'bg-green-400' : item.status === 'FLAGGED' ? 'bg-yellow-400' : 'bg-red-400'}`} />
                        <span className="text-gray-300">{item.type}</span>
                      </div>
                      <span className="text-gray-500 hidden sm:block">{item.source}</span>
                      <span className={`text-xs font-bold ${item.color}`}>{item.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trusted By */}
      <section className="py-14 px-4 sm:px-6 lg:px-8 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-xs text-gray-600 uppercase tracking-widest mb-8">
            Trusted by leading organizations
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 sm:gap-16">
            {trustedBy.map((name, i) => (
              <span key={i} className="text-gray-700 font-bold text-sm tracking-widest hover:text-gray-400 transition-colors cursor-default">
                {name}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, i) => (
            <div key={i} className="text-center">
              <div
                className="text-4xl sm:text-5xl font-black mb-3 text-transparent bg-clip-text"
                style={{ backgroundImage: i % 2 === 0 ? 'linear-gradient(90deg, #f97316, #fbbf24)' : 'linear-gradient(90deg, #fbbf24, #f97316)' }}
              >
                {stat.value}
              </div>
              <div className="text-gray-500 text-sm sm:text-base">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-[#070707]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="inline-block text-orange-500 text-xs font-bold uppercase tracking-widest mb-4">Capabilities</span>
            <h2 className="text-4xl sm:text-5xl font-black mb-5 tracking-tight">Built for the AI Age</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Every tool you need to detect, respond to, and prevent synthetic media threats.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="group bg-[#0d0d0d] border border-white/5 hover:border-orange-500/30 rounded-2xl p-7 transition-all duration-300 hover:bg-[#111]"
                >
                  <div className="w-11 h-11 rounded-lg bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mb-5 group-hover:bg-orange-500/20 transition-colors">
                    <Icon className="text-orange-400" size={22} />
                  </div>
                  <h3 className="text-lg font-bold mb-3">{feature.title}</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section id="use-cases" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="inline-block text-orange-500 text-xs font-bold uppercase tracking-widest mb-4">Solutions</span>
            <h2 className="text-4xl sm:text-5xl font-black mb-5 tracking-tight">For Every Industry</h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Gandiva adapts to your industry's unique threats and compliance requirements.
            </p>
          </div>

          <div className="space-y-8">
            {useCases.map((useCase, index) => (
              <div
                key={index}
                className={`flex flex-col ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'} gap-0 bg-[#0d0d0d] border border-white/5 rounded-2xl overflow-hidden hover:border-orange-500/20 transition-all duration-300`}
              >
                <div className="lg:w-1/2">
                  <img
                    src={useCase.image}
                    alt={useCase.title}
                    className="w-full h-64 lg:h-full object-cover"
                  />
                </div>
                <div className="lg:w-1/2 p-8 lg:p-12 flex flex-col justify-center">
                  <span className="text-orange-500 text-xs font-bold uppercase tracking-widest mb-3">{useCase.label}</span>
                  <h3 className="text-2xl sm:text-3xl font-black mb-4">{useCase.title}</h3>
                  <p className="text-gray-400 mb-6 leading-relaxed">{useCase.description}</p>
                  <ul className="space-y-3">
                    {useCase.items.map((item, i) => (
                      <li key={i} className="flex items-center gap-3 text-sm text-gray-300">
                        <CheckCircle size={16} className="text-orange-500 flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <button className="mt-8 self-start flex items-center gap-2 text-orange-400 hover:text-orange-300 font-semibold text-sm transition-colors group">
                    Learn more <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#070707]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative rounded-3xl overflow-hidden border border-orange-500/20 p-12 sm:p-16">
            <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, rgba(249,115,22,0.1) 0%, rgba(0,0,0,1) 50%, rgba(251,191,36,0.08) 100%)' }} />
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[200px] bg-orange-500/10 blur-3xl" />
            <div className="relative z-10">
              <div className="flex justify-center mb-6">
                <GandivaBowLogo size={56} />
              </div>
              <h2 className="text-4xl sm:text-5xl font-black mb-5 tracking-tight">
                Secure Your Digital Future
              </h2>
              <p className="text-gray-400 text-lg mb-10 max-w-xl mx-auto">
                Join 500+ organizations protecting their digital assets with Gandiva's AI-powered detection platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => window.location.href = '/'}
                  className="bg-orange-500 hover:bg-orange-400 text-black font-bold px-8 py-4 rounded-xl text-base transition-all duration-200 flex items-center justify-center gap-2"
                  style={{ boxShadow: '0 0 40px rgba(249,115,22,0.3)' }}
                >
                  Start Free Trial <ArrowRight size={18} />
                </button>
                <button className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-8 py-4 rounded-xl text-base font-semibold transition-all duration-200">
                  Contact Sales
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-14 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <GandivaBowLogo size={32} />
                <span className="text-xl font-bold" style={{ fontFamily: "'Eagle Lake', serif" }}>Gandiva</span>
              </div>
              <p className="text-gray-500 text-sm leading-relaxed">
                AI-powered detection and protection against synthetic media threats.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-5 text-xs uppercase tracking-wider text-gray-500">Product</h4>
              <ul className="space-y-3 text-gray-600 text-sm">
                {["Features", "Pricing", "API", "Documentation"].map(l => (
                  <li key={l}><a href="#" className="hover:text-white transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-5 text-xs uppercase tracking-wider text-gray-500">Company</h4>
              <ul className="space-y-3 text-gray-600 text-sm">
                {["About", "Blog", "Careers", "Contact"].map(l => (
                  <li key={l}><a href="#" className="hover:text-white transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-5 text-xs uppercase tracking-wider text-gray-500">Legal</h4>
              <ul className="space-y-3 text-gray-600 text-sm">
                {["Privacy Policy", "Terms of Service", "Cookie Policy"].map(l => (
                  <li key={l}><a href="#" className="hover:text-white transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
          </div>
          <div className="border-t border-white/5 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-gray-700 text-sm">
            <p>&copy; 2026 Gandiva. All rights reserved.</p>
            <div className="flex items-center gap-2">
              <GandivaBowLogo size={18} />
              <span>Protecting the real from the synthetic.</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
