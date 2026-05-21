import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Menu, X, Grid3x3, Mic, FileSearch, ArrowRight } from 'lucide-react';
import svgPaths from '../../imports/MacBookPro166/svg-vk1owfvmuu';

export default function Home() {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8">
                <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 47 47">
                  <path d={svgPaths.p3be4e980} fill="#4F46E5" />
                </svg>
              </div>
              <span className="text-xl font-bold text-gray-900">
                Neuro
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#why" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                Why Neuro
              </a>
              <a href="#detection" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                Deepfake Detection
              </a>
              <a href="#use-cases" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                Use Cases
              </a>
              <a href="#resources" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                Resources
              </a>
              <button 
                onClick={() => navigate('/dashboard')}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg transition-colors text-sm font-medium"
              >
                Get Started
              </button>
              <button className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                Log In
              </button>
            </div>

            {/* Mobile menu button */}
            <button
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-4 space-y-3">
              <a href="#why" className="block py-2 text-gray-600 hover:text-gray-900 transition-colors">
                Why Neuro
              </a>
              <a href="#detection" className="block py-2 text-gray-600 hover:text-gray-900 transition-colors">
                Deepfake Detection
              </a>
              <a href="#use-cases" className="block py-2 text-gray-600 hover:text-gray-900 transition-colors">
                Use Cases
              </a>
              <a href="#resources" className="block py-2 text-gray-600 hover:text-gray-900 transition-colors">
                Resources
              </a>
              <button 
                onClick={() => navigate('/dashboard')}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg transition-colors"
              >
                Get Started
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-16 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6 leading-tight text-gray-900">
                Forensic <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Deepfake Detection</span>
              </h1>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                All-in-one, forensic-grade deepfake detection for videos, images, and audio. 
                Boost your investigations into AI-generated synthetic media with our deepfake 
                detection hub. Neuro is a user friendly application with API access, cloud-based 
                and on-premise deployment options. Upload files or URLs and get a multilayer 
                assessment in a few seconds.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => navigate('/dashboard')}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl transition-all duration-300 font-semibold flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  Get started
                  <ArrowRight size={20} />
                </button>
                <button className="border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 px-8 py-4 rounded-xl transition-all duration-300 font-semibold">
                  Talk to an expert
                </button>
              </div>
            </div>

            {/* Right Content - Illustration */}
            <div className="relative">
              <div className="bg-gradient-to-br from-orange-200 via-orange-100 to-yellow-100 rounded-full aspect-square flex items-center justify-center relative overflow-hidden shadow-2xl">
                {/* Floating elements */}
                <div className="absolute top-10 left-10 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-5 py-2 rounded-xl text-sm font-bold shadow-lg animate-bounce">
                  Neuro AI
                </div>
                <div className="absolute top-20 right-10 w-14 h-14 bg-gradient-to-br from-indigo-400 to-purple-400 rounded-xl transform rotate-12 shadow-lg"></div>
                <div className="absolute bottom-20 left-16 w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full shadow-lg"></div>
                <div className="absolute bottom-32 right-20 w-10 h-10 bg-gradient-to-br from-pink-400 to-red-400 rounded-xl transform -rotate-12 shadow-lg"></div>
                
                {/* Center laptop mockup */}
                <div className="relative z-10 bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-3 shadow-2xl w-72 transform hover:scale-105 transition-transform duration-300">
                  <div className="bg-white rounded-xl p-6">
                    <div className="w-full h-36 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-lg mb-3 flex items-center justify-center">
                      <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl"></div>
                    </div>
                    <div className="space-y-2">
                      <div className="h-2 bg-gradient-to-r from-indigo-200 to-purple-200 rounded w-3/4"></div>
                      <div className="h-2 bg-gradient-to-r from-indigo-200 to-purple-200 rounded w-1/2"></div>
                    </div>
                  </div>
                </div>

                {/* Analysis badges */}
                <div className="absolute bottom-4 left-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg">
                  PIXEL ANALYSIS
                </div>
                <div className="absolute top-1/2 right-4 bg-gradient-to-r from-purple-600 to-purple-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg">
                  AUDIO ANALYSIS
                </div>
                <div className="absolute bottom-12 right-12 bg-gradient-to-r from-green-600 to-green-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg">
                  FILE FORENSIC
                </div>
              </div>
            </div>
          </div>

          {/* Analysis Types */}
          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-8 rounded-2xl border-2 border-blue-200 hover:border-blue-400 hover:shadow-xl transition-all duration-300 group">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Grid3x3 className="text-white" size={28} />
              </div>
              <h3 className="text-lg font-bold mb-2 text-gray-900">PIXEL LEVEL ANALYSIS</h3>
              <p className="text-gray-600 text-sm">Detect manipulation at the pixel level with advanced computer vision</p>
            </div>
            <div className="bg-white p-8 rounded-2xl border-2 border-purple-200 hover:border-purple-400 hover:shadow-xl transition-all duration-300 group">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Mic className="text-white" size={28} />
              </div>
              <h3 className="text-lg font-bold mb-2 text-gray-900">VOICE ANALYSIS</h3>
              <p className="text-gray-600 text-sm">Identify AI-generated voices and audio deepfakes with precision</p>
            </div>
            <div className="bg-white p-8 rounded-2xl border-2 border-green-200 hover:border-green-400 hover:shadow-xl transition-all duration-300 group">
              <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <FileSearch className="text-white" size={28} />
              </div>
              <h3 className="text-lg font-bold mb-2 text-gray-900">FILE FORENSIC ANALYSIS</h3>
              <p className="text-gray-600 text-sm">Examine metadata and file signatures for tampering evidence</p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Neuro Section */}
      <section id="why" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-gray-900">
              Why Choose <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Neuro</span>?
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Industry-leading deepfake detection powered by advanced AI and forensic analysis
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-2 text-gray-900">99.8%</h3>
              <p className="text-sm font-semibold text-indigo-600 mb-2">Accuracy</p>
              <p className="text-gray-600 text-sm">
                State-of-the-art detection algorithms trained on millions of samples
              </p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-2 text-gray-900">&lt;2s</h3>
              <p className="text-sm font-semibold text-purple-600 mb-2">Real-Time Analysis</p>
              <p className="text-gray-600 text-sm">
                Get results in seconds, not hours. Fast processing for urgent investigations
              </p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-2 text-gray-900">100%</h3>
              <p className="text-sm font-semibold text-green-600 mb-2">Secure & Private</p>
              <p className="text-gray-600 text-sm">
                End-to-end encryption. Your data never leaves our secure servers
              </p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-2 text-gray-900">Court-Ready</h3>
              <p className="text-sm font-semibold text-orange-600 mb-2">Forensic Reports</p>
              <p className="text-gray-600 text-sm">
                Detailed documentation with evidence trails for legal proceedings
              </p>
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-3xl p-8 md:p-12 shadow-xl">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-2xl md:text-3xl font-bold mb-4 text-gray-900">
                  Trusted by Leading Organizations
                </h3>
                <p className="text-gray-600 mb-6 leading-relaxed">
                  Law enforcement agencies, media companies, and enterprises worldwide rely on Neuro 
                  to protect against deepfake threats and verify content authenticity.
                </p>
                <div className="flex flex-wrap gap-4">
                  <div className="bg-white px-6 py-4 rounded-xl shadow-lg border-2 border-indigo-200">
                    <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">500+</p>
                    <p className="text-xs text-gray-600 font-semibold">Organizations</p>
                  </div>
                  <div className="bg-white px-6 py-4 rounded-xl shadow-lg border-2 border-purple-200">
                    <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">50M+</p>
                    <p className="text-xs text-gray-600 font-semibold">Files Analyzed</p>
                  </div>
                  <div className="bg-white px-6 py-4 rounded-xl shadow-lg border-2 border-pink-200">
                    <p className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-red-600">24/7</p>
                    <p className="text-xs text-gray-600 font-semibold">Support</p>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border-2 border-blue-200">
                  <p className="text-sm font-bold text-gray-900 mb-1">Law Enforcement</p>
                  <p className="text-xs text-gray-600">Criminal investigations</p>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border-2 border-purple-200">
                  <p className="text-sm font-bold text-gray-900 mb-1">Media & News</p>
                  <p className="text-xs text-gray-600">Content verification</p>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border-2 border-green-200">
                  <p className="text-sm font-bold text-gray-900 mb-1">Legal Firms</p>
                  <p className="text-xs text-gray-600">Evidence analysis</p>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border-2 border-orange-200">
                  <p className="text-sm font-bold text-gray-900 mb-1">Enterprises</p>
                  <p className="text-xs text-gray-600">Brand protection</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="detection" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-white to-indigo-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-gray-900">
              How Does <span className="text-indigo-600">Neuro AI</span> Work?
            </h2>
            <p className="text-lg text-gray-600 max-w-4xl mx-auto leading-relaxed">
              Our multilayer detection engine analyzes every dimension of an image, video, or audio file, visual 
              artifacts, acoustic patterns, metadata, behavioral cues, and cross-modal inconsistencies. By stacking 
              independent forensic signals, it delivers a level of certainty that single-layer detectors cannot match. 
              Built for real-world adversaries, trusted in investigations where truth is non-negotiable.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
            {/* Laptop Illustration */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-3xl blur-3xl"></div>
              <div className="relative bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 shadow-2xl">
                <div className="bg-white rounded-xl p-8 shadow-inner">
                  <div className="w-full h-56 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-lg mb-4 flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10"></div>
                    <div className="relative w-40 h-40 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-lg transform rotate-6 hover:rotate-0 transition-transform duration-300">
                      <div className="absolute inset-4 bg-white/20 rounded-xl"></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="h-3 bg-gradient-to-r from-indigo-200 to-purple-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gradient-to-r from-indigo-200 to-purple-200 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Points */}
            <div className="space-y-6">
              <div className="group">
                <div className="flex items-start gap-4 p-6 rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-300 border border-indigo-100 hover:border-indigo-300">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <Grid3x3 className="text-white" size={28} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-gray-900">Pixel Analysis</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Our engine breaks visuals down to their raw pixel structure to detect manipulation at its 
                      origin. No matter how subtle the alteration, pixel-level forensics brings it to light.
                    </p>
                  </div>
                </div>
              </div>

              <div className="group">
                <div className="flex items-start gap-4 p-6 rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-300 border border-purple-100 hover:border-purple-300">
                  <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <Mic className="text-white" size={28} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-gray-900">Voice Analysis</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Our system analyzes the raw audio spectrum to uncover artifacts left by synthesis and manipulation. 
                      Even the most natural-sounding cloned voices reveal hidden acoustic inconsistencies.
                    </p>
                  </div>
                </div>
              </div>

              <div className="group">
                <div className="flex items-start gap-4 p-6 rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-300 border border-green-100 hover:border-green-300">
                  <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <FileSearch className="text-white" size={28} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-gray-900">Forensic Analysis</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Our system analyzes every technical signature inside the file container, from codecs to timestamps. 
                      These forensic markers reveal manipulation paths invisible in the visual or audio layers alone.
                    </p>
                  </div>
                </div>
              </div>

              <div className="group">
                <div className="flex items-start gap-4 p-6 rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-300 border border-orange-100 hover:border-orange-300">
                  <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-gray-900">Forensic Report</h3>
                    <p className="text-gray-600 leading-relaxed">
                      A court-ready forensic report delivers a complete, auditable record of every analysis performed. 
                      Designed for judicial environments, it ensures findings are transparent, reproducible, and admissible.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center">
            <button className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl transition-all duration-300 inline-flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:-translate-y-1 font-semibold">
              Explore Our Technology
              <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section id="use-cases" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-purple-50 via-pink-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-gray-900">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">Use Cases</span>
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Neuro protects organizations across industries from deepfake threats
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Law Enforcement */}
            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-blue-100 hover:border-blue-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Law Enforcement</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">
                Verify evidence authenticity in criminal investigations. Detect manipulated videos, 
                images, and audio recordings used in fraud, harassment, or misinformation campaigns.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1 font-bold">✓</span>
                  <span>Evidence verification for court proceedings</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1 font-bold">✓</span>
                  <span>Fraud and identity theft investigations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1 font-bold">✓</span>
                  <span>Forensic-grade reporting and documentation</span>
                </li>
              </ul>
            </div>

            {/* Media & Journalism */}
            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-purple-100 hover:border-purple-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Media & Journalism</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">
                Verify user-generated content and source materials before publication. Protect 
                editorial integrity and prevent the spread of manipulated media.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 mt-1 font-bold">✓</span>
                  <span>Real-time content verification workflows</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 mt-1 font-bold">✓</span>
                  <span>Source authentication and fact-checking</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 mt-1 font-bold">✓</span>
                  <span>Misinformation detection and prevention</span>
                </li>
              </ul>
            </div>

            {/* Corporate Security */}
            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-green-100 hover:border-green-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Corporate Security</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">
                Protect executives from deepfake impersonation attacks. Detect fraudulent videos 
                used in social engineering, CEO fraud, and business email compromise.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1 font-bold">✓</span>
                  <span>Executive impersonation detection</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1 font-bold">✓</span>
                  <span>Brand protection and reputation management</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 mt-1 font-bold">✓</span>
                  <span>Employee security awareness training</span>
                </li>
              </ul>
            </div>

            {/* Legal & Compliance */}
            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-orange-100 hover:border-orange-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Legal & Compliance</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">
                Authenticate digital evidence for litigation. Provide expert analysis and testimony 
                on media authenticity in civil and criminal cases.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1 font-bold">✓</span>
                  <span>Court-admissible forensic reports</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1 font-bold">✓</span>
                  <span>Chain of custody documentation</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1 font-bold">✓</span>
                  <span>Expert witness support services</span>
                </li>
              </ul>
            </div>

            {/* Social Media Platforms */}
            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-pink-100 hover:border-pink-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Social Media Platforms</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">
                Moderate user-generated content at scale. Detect and flag deepfakes before they 
                spread, protecting users from manipulation and harassment.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-pink-600 mt-1 font-bold">✓</span>
                  <span>Automated content moderation pipelines</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-pink-600 mt-1 font-bold">✓</span>
                  <span>API integration for real-time scanning</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-pink-600 mt-1 font-bold">✓</span>
                  <span>User safety and trust & safety tools</span>
                </li>
              </ul>
            </div>

            {/* Financial Services */}
            <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border-2 border-indigo-100 hover:border-indigo-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Financial Services</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">
                Prevent fraud in KYC processes and transaction verification. Detect deepfake 
                attempts in video authentication and identity verification workflows.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-indigo-600 mt-1 font-bold">✓</span>
                  <span>KYC and identity verification enhancement</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-indigo-600 mt-1 font-bold">✓</span>
                  <span>Transaction authentication security</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-indigo-600 mt-1 font-bold">✓</span>
                  <span>Fraud prevention and risk management</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Resources Section */}
      <section id="resources" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-white via-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-gray-900">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Resources</span>
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Learn more about deepfake detection and how to protect your organization
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Documentation */}
            <div className="bg-white rounded-2xl p-8 hover:shadow-2xl transition-all duration-300 border-2 border-indigo-100 hover:border-indigo-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Documentation</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Complete API documentation, integration guides, and technical specifications for developers.
              </p>
              <button className="text-indigo-600 hover:text-indigo-700 font-semibold text-sm flex items-center gap-2 group-hover:gap-3 transition-all">
                View Docs
                <ArrowRight size={16} />
              </button>
            </div>

            {/* API Access */}
            <div className="bg-white rounded-2xl p-8 hover:shadow-2xl transition-all duration-300 border-2 border-purple-100 hover:border-purple-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">API Access</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Integrate Neuro's detection capabilities directly into your applications and workflows.
              </p>
              <button className="text-purple-600 hover:text-purple-700 font-semibold text-sm flex items-center gap-2 group-hover:gap-3 transition-all">
                Get API Key
                <ArrowRight size={16} />
              </button>
            </div>

            {/* Research Papers */}
            <div className="bg-white rounded-2xl p-8 hover:shadow-2xl transition-all duration-300 border-2 border-green-100 hover:border-green-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Research Papers</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Academic publications and whitepapers on deepfake detection methodologies and AI forensics.
              </p>
              <button className="text-green-600 hover:text-green-700 font-semibold text-sm flex items-center gap-2 group-hover:gap-3 transition-all">
                Read Research
                <ArrowRight size={16} />
              </button>
            </div>

            {/* Case Studies */}
            <div className="bg-white rounded-2xl p-8 hover:shadow-2xl transition-all duration-300 border-2 border-orange-100 hover:border-orange-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Case Studies</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Real-world examples of how organizations use Neuro to combat deepfakes and protect their assets.
              </p>
              <button className="text-orange-600 hover:text-orange-700 font-semibold text-sm flex items-center gap-2 group-hover:gap-3 transition-all">
                View Cases
                <ArrowRight size={16} />
              </button>
            </div>

            {/* Blog & News */}
            <div className="bg-white rounded-2xl p-8 hover:shadow-2xl transition-all duration-300 border-2 border-cyan-100 hover:border-cyan-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Blog & News</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Latest updates on deepfake threats, detection techniques, and industry insights from our experts.
              </p>
              <button className="text-cyan-600 hover:text-cyan-700 font-semibold text-sm flex items-center gap-2 group-hover:gap-3 transition-all">
                Read Blog
                <ArrowRight size={16} />
              </button>
            </div>

            {/* Support Center */}
            <div className="bg-white rounded-2xl p-8 hover:shadow-2xl transition-all duration-300 border-2 border-violet-100 hover:border-violet-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-violet-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Support Center</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Get help from our support team. FAQs, troubleshooting guides, and 24/7 technical assistance.
              </p>
              <button className="text-violet-600 hover:text-violet-700 font-semibold text-sm flex items-center gap-2 group-hover:gap-3 transition-all">
                Get Support
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-72 h-72 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-6 text-white">
            Ready to Secure Your Digital Future?
          </h2>
          <p className="text-lg text-indigo-100 mb-10 leading-relaxed">
            Join leading organizations protecting their digital assets with Neuro's advanced deepfake detection
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => navigate('/dashboard')}
              className="bg-white text-indigo-600 hover:bg-gray-50 px-10 py-4 rounded-xl transition-all duration-300 font-bold shadow-2xl hover:shadow-3xl transform hover:-translate-y-1 flex items-center justify-center gap-2"
            >
              Start Free Trial
              <ArrowRight size={20} />
            </button>
            <button className="border-2 border-white text-white hover:bg-white/10 px-10 py-4 rounded-xl transition-all duration-300 font-bold backdrop-blur-sm">
              Contact Sales
            </button>
          </div>
          
          {/* Trust indicators */}
          <div className="mt-12 flex flex-wrap justify-center gap-8 text-white/90">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium">No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium">14-day free trial</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium">Cancel anytime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white py-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Decorative gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/10 via-purple-600/10 to-pink-600/10"></div>
        
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10">
                  <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 47 47">
                    <path d={svgPaths.p3be4e980} fill="#818CF8" />
                  </svg>
                </div>
                <span className="text-2xl font-bold">
                  Neuro
                </span>
              </div>
              <p className="text-gray-400 text-sm leading-relaxed mb-6">
                Advanced AI-powered detection and protection against synthetic media threats.
              </p>
              <div className="flex gap-4">
                <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-indigo-600 rounded-lg flex items-center justify-center transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                  </svg>
                </a>
                <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-indigo-600 rounded-lg flex items-center justify-center transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                </a>
                <a href="#" className="w-10 h-10 bg-gray-800 hover:bg-indigo-600 rounded-lg flex items-center justify-center transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
              </div>
            </div>

            <div>
              <h4 className="font-bold mb-6 text-lg text-white">Product</h4>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Features
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Pricing
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  API
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Documentation
                </a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold mb-6 text-lg text-white">Company</h4>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  About
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Blog
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Careers
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Contact
                </a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold mb-6 text-lg text-white">Legal</h4>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Privacy Policy
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Terms of Service
                </a></li>
                <li><a href="#" className="hover:text-indigo-400 transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-indigo-400 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></span>
                  Cookie Policy
                </a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-gray-400 text-sm">
                &copy; 2026 Neuro. All rights reserved.
              </p>
              <div className="flex items-center gap-6 text-gray-400 text-sm">
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  All systems operational
                </span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
