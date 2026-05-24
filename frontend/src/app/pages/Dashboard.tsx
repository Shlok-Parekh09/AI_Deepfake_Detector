import { useState, useEffect, useRef } from 'react';
import { ArrowRight, Upload, X, Monitor, Moon, Sun, Paperclip } from 'lucide-react';
import svgPaths from '../../imports/MacBookPro166/svg-vk1owfvmuu';

interface ScanHistory {
  id: string;
  title: string;
  type: 'video' | 'image' | 'audio';
  probability: number;
  time: string;
  status: 'high' | 'medium' | 'low';
}

type Theme = 'system' | 'dark' | 'light';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'recent' | 'top'>('recent');
  const [urlInput, setUrlInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanHistory[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<Theme>('dark');
  const themeMenuRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Close theme menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (themeMenuRef.current && !themeMenuRef.current.contains(event.target as Node)) {
        setShowThemeMenu(false);
      }
    };

    if (showThemeMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showThemeMenu]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUrlInput('');
    }
  };

  const handleAnalyze = async () => {
    if (!urlInput && !selectedFile) return;

    setIsAnalyzing(true);

    // Simulate analysis
    setTimeout(() => {
      const newScan: ScanHistory = {
        id: Date.now().toString(),
        title: selectedFile ? selectedFile.name : urlInput,
        type: 'video',
        probability: Math.floor(Math.random() * 100),
        time: 'Just now',
        status: Math.random() > 0.5 ? 'high' : Math.random() > 0.3 ? 'medium' : 'low',
      };

      setScanHistory([newScan, ...scanHistory]);
      setUrlInput('');
      setSelectedFile(null);
      setIsAnalyzing(false);
    }, 2000);
  };

  const getStatusColor = (probability: number) => {
    if (probability > 70) return 'bg-red-500';
    if (probability > 40) return 'bg-orange-500';
    return 'bg-yellow-500';
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

  const formatTime = (time: string) => {
    if (time === 'Just now') return 'Just now';
    return time;
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-white flex transition-colors duration-200">
      {/* Sidebar */}
      <div className="w-56 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-colors duration-200 flex-shrink-0">
        {/* Logo */}
        <div className="p-5 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5">
              <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 47 47">
                <path d={svgPaths.p3be4e980} fill="#818CF8" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Deepfake Analyser</span>
            <svg className="w-3.5 h-3.5 ml-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Scan Button */}
        <div className="p-3">
          <button 
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="w-full bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 rounded-lg transition-colors flex items-center gap-2 text-xs font-medium border border-gray-200 dark:border-gray-700"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Scan
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
                  onClick={() => {
                    alert(`Scan Details:\n\nFile: ${scan.title}\nType: ${scan.type}\nAI Probability: ${scan.probability}%\nStatus: ${scan.status}\nTime: ${scan.time}`);
                  }}
                  className="text-[11px] text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white cursor-pointer py-1.5 px-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
                >
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${scan.status === 'high' ? 'bg-red-500' : scan.status === 'medium' ? 'bg-orange-500' : 'bg-yellow-500'}`}></div>
                  <span className="truncate">{scan.title.length > 22 ? scan.title.substring(0, 22) + '...' : scan.title}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Bottom Menu — Theme + Sign In only */}
        <div className="p-3 border-t border-gray-200 dark:border-gray-800 space-y-0.5">
          {/* Theme Button with Dropdown */}
          <div className="relative" ref={themeMenuRef}>
            <button 
              onClick={() => setShowThemeMenu(!showThemeMenu)}
              className="w-full text-left text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-xs py-2 px-3 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
              Theme
            </button>

            {/* Theme Dropdown Menu */}
            {showThemeMenu && (
              <div className="absolute bottom-full left-0 mb-1 w-44 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl overflow-hidden z-50">
                <button
                  onClick={() => handleThemeChange('system')}
                  className={`w-full text-left px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                    currentTheme === 'system' ? 'bg-gray-50 dark:bg-gray-700' : ''
                  }`}
                >
                  <Monitor size={14} className="text-gray-600 dark:text-gray-400" />
                  <span className="text-xs text-gray-900 dark:text-white">System</span>
                  {currentTheme === 'system' && (
                    <svg className="w-3 h-3 ml-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
                <button
                  onClick={() => handleThemeChange('dark')}
                  className={`w-full text-left px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                    currentTheme === 'dark' ? 'bg-gray-50 dark:bg-gray-700' : ''
                  }`}
                >
                  <Moon size={14} className="text-gray-600 dark:text-gray-400" />
                  <span className="text-xs text-gray-900 dark:text-white">Dark</span>
                  {currentTheme === 'dark' && (
                    <svg className="w-3 h-3 ml-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
                <button
                  onClick={() => handleThemeChange('light')}
                  className={`w-full text-left px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                    currentTheme === 'light' ? 'bg-gray-50 dark:bg-gray-700' : ''
                  }`}
                >
                  <Sun size={14} className="text-gray-600 dark:text-gray-400" />
                  <span className="text-xs text-gray-900 dark:text-white">Light</span>
                  {currentTheme === 'light' && (
                    <svg className="w-3 h-3 ml-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              </div>
            )}
          </div>

          <button 
            onClick={() => alert('Sign in feature coming soon!')}
            className="w-full bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white text-xs py-2 px-4 rounded-md transition-colors mt-1 border border-gray-200 dark:border-gray-700"
          >
            Sign In
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="text-center py-10 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 transition-colors duration-200">
          <div className="flex items-center justify-center gap-2.5 mb-2">
            <div className="w-8 h-8">
              <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 47 47">
                <path d={svgPaths.p3be4e980} fill="#818CF8" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Neuro</h1>
          </div>
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            Scan for suspicious deepfakes using Neuro's Community Platform.
          </p>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-6 overflow-y-auto bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
          <div className="max-w-4xl mx-auto">
            {/* Single Input Bar — URL + File Upload */}
            <div className="mb-2">
              <div className="flex gap-2 items-center">
                {/* File attachment button */}
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileChange}
                  accept="video/*,image/*,audio/*"
                  className="hidden"
                  id="file-attach"
                />

                {/* Main input area */}
                <div className="flex-1 relative flex items-center bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-xl overflow-hidden focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
                  {selectedFile ? (
                    <div className="flex-1 flex items-center gap-2 px-4 py-3">
                      <Paperclip size={16} className="text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-900 dark:text-white truncate">{selectedFile.name}</span>
                      <span className="text-xs text-gray-400 flex-shrink-0">({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)</span>
                      <button
                        onClick={() => setSelectedFile(null)}
                        className="ml-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 flex-shrink-0"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ) : (
                    <input
                      type="text"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') handleAnalyze(); }}
                      placeholder="Enter Video URL"
                      className="flex-1 bg-transparent px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none text-sm"
                    />
                  )}

                  {/* Inline file upload button */}
                  {!selectedFile && (
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="px-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                      title="Attach file"
                    >
                      <Upload size={18} />
                    </button>
                  )}

                  {/* Analyse button inside input */}
                  <button
                    onClick={handleAnalyze}
                    disabled={(!urlInput && !selectedFile) || isAnalyzing}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white px-5 py-3 transition-colors flex items-center gap-1.5 text-sm font-medium flex-shrink-0"
                  >
                    {isAnalyzing ? (
                      <>
                        <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Analysing...
                      </>
                    ) : (
                      <>
                        Analyse
                        <ArrowRight size={15} />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Helper text */}
            <div className="flex items-center gap-3 mb-8 text-xs text-gray-400 dark:text-gray-500 px-1">
              <span>Video duration should be less than 5 minutes</span>
              <button 
                onClick={() => {
                  alert('Supported sources:\n\n• YouTube, Vimeo, direct MP4/AVI/MOV links\n• Direct JPG/PNG/GIF/WEBP image links\n• Direct MP3/WAV/OGG audio links\n• File upload: drag & drop or click the upload icon');
                }}
                className="hover:text-gray-600 dark:hover:text-gray-400 flex items-center gap-1 transition-colors"
              >
                Sources supported
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </div>

            {/* Tabs */}
            <div className="flex items-center gap-6 mb-5 border-b border-gray-200 dark:border-gray-800">
              <button 
                onClick={() => setActiveTab('recent')}
                className={`flex items-center gap-1.5 pb-3 border-b-2 ${activeTab === 'recent' ? 'border-blue-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'} text-sm transition-colors`}
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recent Public Scans
              </button>
              <button 
                onClick={() => setActiveTab('top')}
                className={`flex items-center gap-1.5 pb-3 border-b-2 ${activeTab === 'top' ? 'border-blue-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'} text-sm transition-colors`}
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                Top 10 Scans
              </button>
              {scanHistory.length > 0 && (
                <button 
                  onClick={() => alert(`Total scans: ${scanHistory.length}`)}
                  className="ml-auto text-blue-500 hover:text-blue-600 text-xs font-medium"
                >
                  View All Scans
                </button>
              )}
            </div>

            {/* Scans Table */}
            {scanHistory.length === 0 ? (
              <div className="bg-white dark:bg-gray-900 rounded-lg p-12 text-center border border-gray-200 dark:border-gray-800">
                <svg className="w-14 h-14 mx-auto mb-4 text-gray-200 dark:text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-gray-500 dark:text-gray-400 mb-1 text-sm">No scans yet</p>
                <p className="text-gray-400 dark:text-gray-600 text-xs">Enter a URL or upload a file to start analyzing</p>
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-900 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-800">
                {/* Table Header */}
                <div className="grid grid-cols-12 gap-4 px-5 py-2.5 bg-gray-50 dark:bg-gray-800/50 text-[11px] text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wider border-b border-gray-200 dark:border-gray-800">
                  <div className="col-span-6">URL</div>
                  <div className="col-span-3">AI Probability</div>
                  <div className="col-span-3 text-right">Scanned on</div>
                </div>

                {/* Table Rows */}
                <div className="divide-y divide-gray-100 dark:divide-gray-800">
                  {scanHistory.map((scan) => (
                    <div
                      key={scan.id}
                      onClick={() => {
                        alert(`Scan Details:\n\nFile: ${scan.title}\nType: ${scan.type}\nAI Probability: ${scan.probability}%\nStatus: ${scan.status.toUpperCase()}\nTime: ${scan.time}\n\nAnalysis: ${scan.probability > 70 ? 'High probability of deepfake detected!' : scan.probability > 40 ? 'Medium probability - further investigation recommended' : 'Low probability - likely authentic'}`);
                      }}
                      className="grid grid-cols-12 gap-4 px-5 py-3.5 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors cursor-pointer"
                    >
                      <div className="col-span-6 text-sm text-gray-800 dark:text-gray-300 truncate">
                        {scan.title}
                      </div>
                      <div className="col-span-3 flex items-center gap-2.5">
                        <div className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-1.5 max-w-[100px]">
                          <div
                            className={`h-1.5 rounded-full ${getStatusColor(scan.probability)} transition-all duration-500`}
                            style={{ width: `${scan.probability}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="col-span-3 text-xs text-gray-400 dark:text-gray-500 text-right flex items-center justify-end">
                        {formatTime(scan.time)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
