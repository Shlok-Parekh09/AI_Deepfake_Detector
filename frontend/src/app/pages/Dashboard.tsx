import { useState, useEffect, useRef } from 'react';
import { Menu, ArrowRight, Upload, X, Monitor, Moon, Sun, Paperclip, ChevronLeft, ShieldAlert, ShieldCheck } from 'lucide-react';
import BrandLogo from '../components/BrandLogo';
import { AudioWaveform } from '../components/visualizers/AudioWaveform';

// Visualizers
import { ScanningView } from '../components/visualizers/ScanningView';
import { VideoVisualizer } from '../components/visualizers/VideoVisualizer';
import { AudioVisualizer } from '../components/visualizers/AudioVisualizer';
import { ImageVisualizer } from '../components/visualizers/ImageVisualizer';

// Use the hosted backend consistently in local development and deployed builds.
const API_BASE_URL = 'https://shlok0829-deepfake.hf.space';

interface ScanHistory {
  id: string;
  title: string;
  type: 'video' | 'image' | 'audio';
  probability: number;
  time: string;
  status: 'high' | 'medium' | 'low';
}

type Theme = 'system' | 'dark' | 'light';
type ScanState = 'idle' | 'scanning' | 'results';

export default function Dashboard() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'recent' | 'top'>('recent');
  const [urlInput, setUrlInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanHistory[]>([]);

  // Scanning & Results State
  const [scanState, setScanState] = useState<ScanState>('idle');
  const [scanProgress, setScanProgress] = useState(0);
  const [scanStatusText, setScanStatusText] = useState('Initiating Scan...');
  const [currentScanType, setCurrentScanType] = useState<'video' | 'audio' | 'image'>('video');
  const [currentMediaUrl, setCurrentMediaUrl] = useState<string>('');
  const [currentIsFake, setCurrentIsFake] = useState(false);
  const [currentAudioNeedsReview, setCurrentAudioNeedsReview] = useState(false);
  const [currentAiSummary, setCurrentAiSummary] = useState<string>('');
  const [currentDetectedTool, setCurrentDetectedTool] = useState<string>('');
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<Theme>('dark');
  useEffect(() => {
    const preference = window.matchMedia('(prefers-color-scheme: dark)');
    const applyTheme = () => document.documentElement.classList.toggle('dark', currentTheme === 'dark' || (currentTheme === 'system' && preference.matches));
    applyTheme();
    preference.addEventListener('change', applyTheme);
    return () => preference.removeEventListener('change', applyTheme);
  }, [currentTheme]);
  const themeMenuRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoElementRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (themeMenuRef.current && !themeMenuRef.current.contains(event.target as Node)) {
        setShowThemeMenu(false);
      }
    };
    if (showThemeMenu) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showThemeMenu]);

  useEffect(() => {
    if (!mobileMenuOpen) return;
    const close = (event: KeyboardEvent) => { if (event.key === 'Escape') setMobileMenuOpen(false); };
    document.addEventListener('keydown', close);
    return () => document.removeEventListener('keydown', close);
  }, [mobileMenuOpen]);

  // Clean up object URLs to avoid memory leaks
  useEffect(() => {
    return () => {
      if (currentMediaUrl && currentMediaUrl.startsWith('blob:')) {
        URL.revokeObjectURL(currentMediaUrl);
      }
    };
  }, [currentMediaUrl]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUrlInput('');
    }
  };

  const determineMediaType = (file: File | null, url: string): 'video' | 'audio' | 'image' => {
    if (file) {
      if (file.type.startsWith('image/')) return 'image';
      if (file.type.startsWith('audio/')) return 'audio';
      return 'video'; // Default
    }
    const lowerUrl = url.toLowerCase();
    if (lowerUrl.match(/\.(jpeg|jpg|gif|png|webp)$/)) return 'image';
    if (lowerUrl.match(/\.(mp3|wav|ogg)$/)) return 'audio';
    return 'video'; // Default for YouTube links etc.
  };

  const handleAnalyze = async () => {
    if (!urlInput && !selectedFile) return;

    // Determine type and set media URL
    const type = determineMediaType(selectedFile, urlInput);
    setCurrentScanType(type);

    if (selectedFile) {
      setCurrentMediaUrl(URL.createObjectURL(selectedFile));
    } else {
      // Proxy the URL through our backend to avoid CORS and ensure it loads properly
      setCurrentMediaUrl(`${API_BASE_URL}/api/v1/proxy-media?url=${encodeURIComponent(urlInput)}`);
    }

    setScanState('scanning');
    setScanProgress(0);
    setScanStatusText('Initiating Scan...');

    // Mock scanning progression just for visual feedback while waiting for backend
    let progress = 0;
    const interval = window.setInterval(() => {
      progress += Math.random() * 5 + 2;
      // Cap at 90% while waiting for the actual backend response
      if (progress > 90) progress = 90;
      setScanProgress(progress);

      if (progress < 20) setScanStatusText('Extracting metadata...');
      else if (progress < 40) setScanStatusText(type === 'image' ? 'Running pixel analysis...' : 'Extracting frames...');
      else if (progress < 60) setScanStatusText('Analyzing spatial features...');
      else if (progress < 80) setScanStatusText('Cross-referencing generative models...');
      else setScanStatusText('Waiting for backend inference...');
    }, 400);

    try {
      let resultData: any;
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        const res = await fetch(`${API_BASE_URL}/api/v1/detect`, {
          method: 'POST',
          body: formData,
        });
        resultData = await res.json();
        if (!res.ok) {
          throw new Error(resultData.detail || 'Backend scan failed');
        }
      } else {
        const res = await fetch(`${API_BASE_URL}/api/v1/detect/url`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: urlInput }),
        });
        resultData = await res.json();
        if (!res.ok) {
          throw new Error(resultData.detail || 'Backend scan failed');
        }
      }

      if (resultData.error || typeof resultData.fake_probability !== 'number' ||
          !Number.isFinite(resultData.fake_probability) || resultData.fake_probability < 0 ||
          resultData.fake_probability > 1 || typeof resultData.is_fake !== 'boolean') {
        throw new Error('The detector returned no valid prediction. Please retry the analysis.');
      }
      window.clearInterval(interval);
      setScanProgress(100);
      setScanStatusText('Finalizing report...');

      setTimeout(() => {
        // The backend returns a probability float (0.0 to 1.0)
        const prob = Math.round(resultData.fake_probability * 100);
        setCurrentIsFake(Boolean(resultData.is_fake));
        if (['audio', 'video', 'image'].includes(resultData.file_type)) setCurrentScanType(resultData.file_type);
        setCurrentAudioNeedsReview(Boolean(resultData.review_required));
        setCurrentAiSummary(`Model prediction: ${resultData.is_fake ? 'Fake' : 'Real'}. This is not proof of authenticity.`);
        setCurrentDetectedTool(resultData.detected_tool || '');

        const newScan: ScanHistory = {
          id: Date.now().toString(),
          title: selectedFile ? selectedFile.name : urlInput,
          type: ['audio', 'video', 'image'].includes(resultData.file_type) ? resultData.file_type : type,
          probability: prob,
          time: 'Just now',
          status: resultData.is_fake ? 'high' : 'low',
        };
        setScanHistory(prev => [newScan, ...prev]);
        setScanState('results');
      }, 500);

    } catch (error) {
      console.error("Backend scan failed:", error);
      window.clearInterval(interval);
      setScanStatusText(error instanceof Error ? error.message : 'Scan failed. Ensure backend is running.');
      // Revert after error
      setTimeout(() => setScanState('idle'), 5000);
    }
  };

  const handleThemeChange = (theme: Theme) => {
    setCurrentTheme(theme);
    setShowThemeMenu(false);
    if (theme === 'system') {
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', systemPrefersDark);
    } else if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };


  return (
    <div className="min-h-dvh lg:h-dvh bg-white dark:bg-[#08080e] text-gray-900 dark:text-white flex flex-col lg:flex-row lg:overflow-hidden transition-colors duration-200">
      {mobileMenuOpen && <button aria-label="Close navigation overlay" onClick={() => setMobileMenuOpen(false)} className="fixed inset-0 z-40 bg-black/60 lg:hidden" />}
      {/* Sidebar */}
      <div id="dashboard-navigation" className={`${mobileMenuOpen ? 'fixed inset-y-0 left-0 flex' : 'hidden'} lg:relative lg:flex w-56 max-w-[85vw] bg-gray-50 dark:bg-[#0e0e18] border-r border-gray-200 dark:border-gray-800/50 flex flex-col transition-colors duration-200 flex-shrink-0 z-50`}>
        <button aria-label="Close navigation" onClick={() => setMobileMenuOpen(false)} className="min-h-11 px-5 text-right text-gray-500 lg:hidden">Close ×</button>
        {/* Logo */}
        <div className="p-5 border-b border-gray-200 dark:border-gray-800/50">
          <div className="flex items-center gap-2">
            <BrandLogo size={24} />
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Deepfake Analyser</span>
            <svg className="w-3.5 h-3.5 ml-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Scan Button */}
        <div className="p-3">
          <button
            onClick={() => { setMobileMenuOpen(false); setScanState('idle'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
            className="w-full bg-white dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-900 dark:text-white px-3 py-2 rounded-lg transition-colors flex items-center gap-2 text-xs font-medium border border-gray-200 dark:border-gray-700/50"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            New Scan
          </button>
        </div>

        {/* Public Scans */}
        <div className="px-3 py-1.5">
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-xs px-2">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Public Scans
          </div>
        </div>

        {/* Recents */}
        <div className="flex-1 px-3 py-2 overflow-y-auto">
          <h3 className="text-gray-400 dark:text-gray-500 text-[10px] uppercase tracking-wider mb-2 px-2 font-medium">Recents</h3>
          <div className="space-y-0.5">
            {scanHistory.length === 0 ? (
              <p className="text-[11px] text-gray-400 dark:text-gray-600 py-2 px-2">No scans yet</p>
            ) : (
              scanHistory.slice(0, 10).map((scan) => (
                <div
                  key={scan.id}
                  className="text-[11px] text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white cursor-pointer py-1.5 px-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-colors flex items-center gap-2"
                >
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${scan.status === 'high' ? 'bg-red-500' : scan.status === 'medium' ? 'bg-orange-500' : 'bg-yellow-500'}`}></div>
                  <span className="truncate">{scan.title}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Bottom Menu */}
        <div className="p-3 border-t border-gray-200 dark:border-gray-800/50 space-y-0.5">
          <div className="relative" ref={themeMenuRef}>
            <button
              onClick={() => setShowThemeMenu(!showThemeMenu)}
              className="w-full text-left text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-xs py-2 px-3 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-colors flex items-center gap-2"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" /></svg>
              Theme
            </button>
            {showThemeMenu && (
              <div className="absolute bottom-full left-0 mb-1 w-44 bg-white dark:bg-[#12121f] border border-gray-200 dark:border-gray-700/50 rounded-lg shadow-xl overflow-hidden z-50">
                <button onClick={() => handleThemeChange('system')} className={`w-full text-left px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-3 ${currentTheme === 'system' ? 'bg-gray-50 dark:bg-gray-800' : ''}`}><Monitor size={14} className="text-gray-600 dark:text-gray-400" /><span className="text-xs text-gray-900 dark:text-white">System</span></button>
                <button onClick={() => handleThemeChange('dark')} className={`w-full text-left px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-3 ${currentTheme === 'dark' ? 'bg-gray-50 dark:bg-gray-800' : ''}`}><Moon size={14} className="text-gray-600 dark:text-gray-400" /><span className="text-xs text-gray-900 dark:text-white">Dark</span></button>
                <button onClick={() => handleThemeChange('light')} className={`w-full text-left px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-3 ${currentTheme === 'light' ? 'bg-gray-50 dark:bg-gray-800' : ''}`}><Sun size={14} className="text-gray-600 dark:text-gray-400" /><span className="text-xs text-gray-900 dark:text-white">Light</span></button>
              </div>
            )}
          </div>
          <button className="w-full bg-white dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-900 dark:text-white text-xs py-2 px-4 rounded-md transition-colors mt-1 border border-gray-200 dark:border-gray-700/50">
            Sign In
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0 relative">
        <header className="flex items-center gap-3 border-b border-gray-200 dark:border-gray-800/50 bg-white dark:bg-[#0e0e18] px-3 py-2 lg:hidden"><button aria-label="Open navigation" aria-expanded={mobileMenuOpen} aria-controls="dashboard-navigation" onClick={() => setMobileMenuOpen(true)} className="flex min-h-11 min-w-11 items-center justify-center text-gray-500 dark:text-gray-300"><Menu size={22} /></button><BrandLogo size={25} /><span className="text-sm font-semibold">SynPhi</span></header>

        {scanState === 'idle' && (
          <div className="flex-1 overflow-y-auto">
            {/* Header */}
            <div className="text-center px-4 py-8 sm:py-12 border-b border-gray-200 dark:border-gray-800/50 bg-white dark:bg-[#08080e] transition-colors duration-200">
              <div className="flex items-center justify-center gap-2.5 mb-3">
                <BrandLogo size={48} />
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">SynPhi</h1>
              </div>
              <p className="text-gray-500 dark:text-gray-400 text-sm max-w-md mx-auto">
                Scan for suspicious deepfakes using SynPhi's forensic engine. We support Video, Audio, and Image formats.
              </p>
            </div>

            <div className="p-4 sm:p-8">
              <div className="max-w-3xl mx-auto">
                {/* Input Bar */}
                <div className="mb-4">
                  <div className="flex gap-2 items-center">
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileChange}
                      accept="*/*"
                      className="hidden"
                      id="file-attach"
                    />
                    <div className="min-w-0 flex-1 relative flex flex-wrap sm:flex-nowrap items-center bg-white dark:bg-[#0e0e18] border border-gray-300 dark:border-gray-800 rounded-xl overflow-hidden focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all shadow-sm">
                      {selectedFile ? (
                        <div className="min-w-0 flex-1 flex items-center gap-2 px-3 sm:px-5 py-4">
                          <Paperclip size={18} className="text-indigo-400 flex-shrink-0" />
                          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{selectedFile.name}</span>
                          <span className="text-xs text-gray-400 flex-shrink-0">({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)</span>
                          <button onClick={() => setSelectedFile(null)} className="ml-2 text-gray-400 hover:text-gray-200 flex-shrink-0 bg-gray-800 rounded-full p-1"><X size={12} /></button>
                        </div>
                      ) : (
                        <input
                          type="text"
                          value={urlInput}
                          onChange={(e) => setUrlInput(e.target.value)}
                          onKeyDown={(e) => { if (e.key === 'Enter') handleAnalyze(); }}
                          placeholder="Paste URL or upload a file to scan"
                          className="min-w-0 flex-1 bg-transparent px-3 sm:px-5 py-4 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none text-base sm:text-sm"
                        />
                      )}
                      {!selectedFile && (
                        <button onClick={() => fileInputRef.current?.click()} className="px-4 text-gray-400 hover:text-indigo-400 transition-colors" title="Attach large file"><Upload size={20} /></button>
                      )}
                      <button
                        onClick={handleAnalyze}
                        disabled={!urlInput && !selectedFile}
                        className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-800 disabled:text-gray-500 text-white w-full sm:w-auto justify-center px-4 sm:px-6 py-4 transition-colors flex items-center gap-2 text-sm font-semibold flex-shrink-0"
                      >
                        Analyse <ArrowRight size={16} />
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 mb-10 text-xs text-gray-400 dark:text-gray-500 px-2">
                  <span>Supports media files up to 100 MB</span>
                </div>

                {/* Tabs & Table */}
                <div className="flex items-center gap-6 mb-5 border-b border-gray-200 dark:border-gray-800">
                  <button onClick={() => setActiveTab('recent')} className={`flex items-center gap-1.5 pb-3 border-b-2 ${activeTab === 'recent' ? 'border-indigo-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-400 hover:text-gray-300'} text-sm transition-colors`}>Recent Scans</button>
                </div>

                {scanHistory.length === 0 ? (
                  <div className="bg-white dark:bg-[#0e0e18] rounded-xl p-8 sm:p-16 text-center border border-gray-200 dark:border-gray-800/50">
                    <div className="w-16 h-16 rounded-full bg-indigo-500/10 flex items-center justify-center mx-auto mb-4">
                      <ShieldCheck size={32} className="text-indigo-400" />
                    </div>
                    <p className="text-gray-900 dark:text-white font-medium mb-1">Ready to scan</p>
                    <p className="text-gray-500 text-sm">Upload media to begin forensic analysis.</p>
                  </div>
                ) : (
                  <div className="bg-white dark:bg-[#0e0e18] rounded-xl overflow-hidden border border-gray-200 dark:border-gray-800/50 shadow-sm">
                    {/* Simplified table rendering for brevity */}
                    <div className="divide-y divide-gray-100 dark:divide-gray-800/50">
                      {scanHistory.map((scan) => (
                        <div key={scan.id} className="grid grid-cols-12 gap-2 sm:gap-4 px-3 sm:px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                          <div className="col-span-7 text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{scan.title}</div>
                          <div className="col-span-3 text-xs text-gray-500">{scan.status === 'high' ? 'Fake' : 'Real'}</div>
                          <div className="col-span-2 text-xs text-gray-400 text-right">{scan.time}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* SCANNING STATE */}
        {scanState === 'scanning' && (
          <div className="flex-1 flex flex-col p-4 sm:p-8 items-center justify-center bg-[#08080e]">
            {/* Top Toast */}
            <div className="hidden sm:flex absolute top-6 right-6 bg-emerald-500/10 border border-emerald-500/30 px-4 py-3 rounded-xl flex items-start gap-3 shadow-2xl animate-[slideIn_0.3s_ease-out]">
              <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-emerald-400">Media submitted for scanning</p>
                <p className="text-xs text-gray-400 mt-1">Detailed forensics will be available shortly.</p>
              </div>
              <button className="text-gray-500 hover:text-white ml-4"><X size={16} /></button>
            </div>

            <div className="w-full max-w-4xl">
              <div className="flex items-center gap-3 mb-6 text-gray-400">
                <span className="min-w-0 truncate font-mono text-xs sm:text-sm uppercase tracking-wider">{selectedFile ? selectedFile.name : urlInput}</span>
              </div>

              <ScanningView
                progress={scanProgress}
                statusText={scanStatusText}
                mediaUrl={currentMediaUrl}
                mediaType={currentScanType}
              />
            </div>
          </div>
        )}

        {/* RESULTS STATE */}
        {scanState === 'results' && (
          <div className="flex-1 flex flex-col bg-[#08080e] overflow-hidden">
            {/* Header / Back button */}
            <div className="p-4 border-b border-gray-800/50 flex items-center gap-4 bg-[#0e0e18]">
              <button onClick={() => setScanState('idle')} className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors">
                <ChevronLeft size={20} />
              </button>
              <div className="min-w-0">
                <h2 className="text-base sm:text-lg font-bold text-white truncate max-w-md">{selectedFile ? selectedFile.name : urlInput}</h2>
                <p className="text-xs text-gray-400 font-mono uppercase tracking-wider">Analysis Complete · {currentScanType} · {scanHistory[0]?.time}</p>
              </div>
            </div>

            <div className="flex-1 min-h-0 flex flex-col xl:flex-row xl:overflow-hidden">
              {/* Left Panel: Summary Classification */}
              <div className="w-full xl:w-80 border-b xl:border-b-0 xl:border-r border-gray-800/50 bg-[#0a0a14] p-4 sm:p-6 xl:overflow-y-auto flex-shrink-0">
                <h3 className="text-sm font-bold text-white mb-6 uppercase tracking-wider">Classification</h3>

                {/* Binary model prediction; no confidence score is displayed. */}
                <div className={`p-5 rounded-2xl border mb-6 ${currentIsFake ? 'bg-red-500/10 border-red-500/30' : 'bg-emerald-500/10 border-emerald-500/30'}`}>
                  <div className="flex items-center gap-3">{currentIsFake ? <ShieldAlert className="text-red-400" size={22} /> : <ShieldCheck className="text-emerald-400" size={22} />}<p className="text-xl font-bold text-white">{currentIsFake ? 'Fake' : 'Real'}</p></div>
                  <p className="mt-3 text-xs leading-6 text-gray-400">Model prediction. This result is not proof of authenticity.</p>
                </div>
                {currentScanType === 'audio' && (
                  <div className="space-y-4">
                    <div className="bg-[#12121f] rounded-xl p-4 border border-gray-800">
                      <p className="text-[10px] text-gray-500 font-mono mb-2">VOICE FORENSICS</p>
                      <div className="space-y-3">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Detector</span>
                          <span className="text-white font-medium">
                            Multilingual audio model
                          </span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Assessment</span>
                          <span className={`font-semibold ${currentAudioNeedsReview ? 'text-orange-400' : currentIsFake ? 'text-red-400' : 'text-slate-300'}`}>
                            {currentIsFake ? 'Fake' : 'Real'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Main Visualizer Area */}
              <div className={`min-w-0 flex-1 p-4 sm:p-6 xl:p-8 bg-black/20 xl:overflow-y-auto flex justify-center ${currentScanType === 'audio' ? 'items-start' : 'items-center'}`}>
                <div className="w-full max-w-5xl">
                  {currentScanType === 'video' && (
                    <div className="flex flex-col gap-6">
                      <VideoVisualizer
                        mediaUrl={currentMediaUrl || '/placeholder.mp4'}
                        onPlayStateChange={setIsVideoPlaying}
                        externalVideoRef={videoElementRef}
                      />
                      <AudioVisualizer
                        mediaUrl={currentMediaUrl || '/placeholder.mp4'}
                        isExternalPlaying={isVideoPlaying}
                        hideAudioElement={true}
                        externalMediaRef={videoElementRef}
                      />
                    </div>
                  )}
                  {currentScanType === 'audio' && (
                    <div className="space-y-4">
                      <audio controls src={currentMediaUrl || undefined} className="w-full" />
                      <AudioWaveform mediaUrl={currentMediaUrl} />
                      {currentAudioNeedsReview && <p className="text-sm text-orange-300">Review recommended.</p>}
                      <p className="text-sm text-gray-300">Model prediction: {currentIsFake ? 'Fake' : 'Real'}. This prediction is not proof of authenticity.</p>
                    </div>
                  )}
                  {currentScanType === 'image' && <ImageVisualizer mediaUrl={currentMediaUrl || '/placeholder.jpg'} aiSummary={currentAiSummary} detectedTool={currentDetectedTool} />}


                </div>
              </div>
            </div>
          </div>
        )}

      </div>
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
