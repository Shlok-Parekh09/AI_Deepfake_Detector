import { useState, useEffect, useRef } from 'react';
import { ArrowRight, Upload, Link as LinkIcon, X, Monitor, Moon, Sun } from 'lucide-react';
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
  const [inputType, setInputType] = useState<'url' | 'file'>('url');
  const [mediaType, setMediaType] = useState<'video' | 'image' | 'audio'>('video');
  const [urlInput, setUrlInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanHistory[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<Theme>('dark');
  const themeMenuRef = useRef<HTMLDivElement>(null);

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
    }
  };

  const handleAnalyze = async () => {
    if (inputType === 'url' && !urlInput) return;
    if (inputType === 'file' && !selectedFile) return;

    setIsAnalyzing(true);

    // Simulate analysis
    setTimeout(() => {
      const newScan: ScanHistory = {
        id: Date.now().toString(),
        title: inputType === 'url' ? urlInput : selectedFile!.name,
        type: mediaType,
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

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-white flex transition-colors duration-200">
      {/* Sidebar */}
      <div className="w-64 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-colors duration-200">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6">
              <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 47 47">
                <path d={svgPaths.p3be4e980} fill="#818CF8" />
              </svg>
            </div>
            <span className="text-lg font-semibold text-gray-900 dark:text-white">Deepfake Analyser</span>
            <svg className="w-4 h-4 ml-auto text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Scan Button */}
        <div className="p-4">
          <button 
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="w-full bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white px-4 py-2.5 rounded-lg transition-colors flex items-center gap-2 text-sm border border-gray-200 dark:border-gray-700"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Scan
          </button>
        </div>

        {/* Public Scans */}
        <div className="px-4 py-2">
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-xs">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Public Scans
          </div>
        </div>

        {/* Recents */}
        <div className="flex-1 px-4 py-2 overflow-y-auto">
          <h3 className="text-gray-500 dark:text-gray-400 text-xs mb-3">Recents</h3>
          <div className="space-y-1">
            {scanHistory.length === 0 ? (
              <p className="text-xs text-gray-400 dark:text-gray-600 py-2">No scans yet</p>
            ) : (
              scanHistory.slice(0, 10).map((scan) => (
                <div
                  key={scan.id}
                  onClick={() => {
                    alert(`Scan Details:\n\nFile: ${scan.title}\nType: ${scan.type}\nAI Probability: ${scan.probability}%\nStatus: ${scan.status}\nTime: ${scan.time}`);
                  }}
                  className="text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white cursor-pointer py-2 px-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
                >
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${scan.status === 'high' ? 'bg-red-500' : scan.status === 'medium' ? 'bg-orange-500' : 'bg-yellow-500'}`}></div>
                  <span className="truncate">{scan.title.substring(0, 30)}...</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Bottom Menu */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-1">
          <button 
            onClick={() => alert('Updates feature coming soon!')}
            className="w-full text-left text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-xs py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Updates
          </button>
          <button 
            onClick={() => alert('Performance metrics coming soon!')}
            className="w-full text-left text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-xs py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Performance
          </button>
          
          {/* Theme Button with Dropdown */}
          <div className="relative" ref={themeMenuRef}>
            <button 
              onClick={() => setShowThemeMenu(!showThemeMenu)}
              className="w-full text-left text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-xs py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
              Theme
            </button>

            {/* Theme Dropdown Menu */}
            {showThemeMenu && (
              <div className="absolute bottom-full left-0 mb-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl overflow-hidden z-50">
                <button
                  onClick={() => handleThemeChange('system')}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                    currentTheme === 'system' ? 'bg-gray-50 dark:bg-gray-700' : ''
                  }`}
                >
                  <Monitor size={18} className="text-gray-600 dark:text-gray-400" />
                  <span className="text-sm text-gray-900 dark:text-white">System</span>
                  {currentTheme === 'system' && (
                    <svg className="w-4 h-4 ml-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
                <button
                  onClick={() => handleThemeChange('dark')}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                    currentTheme === 'dark' ? 'bg-gray-50 dark:bg-gray-700' : ''
                  }`}
                >
                  <Moon size={18} className="text-gray-600 dark:text-gray-400" />
                  <span className="text-sm text-gray-900 dark:text-white">Dark</span>
                  {currentTheme === 'dark' && (
                    <svg className="w-4 h-4 ml-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
                <button
                  onClick={() => handleThemeChange('light')}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                    currentTheme === 'light' ? 'bg-gray-50 dark:bg-gray-700' : ''
                  }`}
                >
                  <Sun size={18} className="text-gray-600 dark:text-gray-400" />
                  <span className="text-sm text-gray-900 dark:text-white">Light</span>
                  {currentTheme === 'light' && (
                    <svg className="w-4 h-4 ml-auto text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              </div>
            )}
          </div>

          <button 
            onClick={() => alert('Sign in feature coming soon!')}
            className="w-full bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white text-xs py-2.5 px-4 rounded transition-colors mt-2 border border-gray-200 dark:border-gray-700"
          >
            Sign In
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="text-center py-12 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 transition-colors duration-200">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-10 h-10">
              <svg className="w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 47 47">
                <path d={svgPaths.p3be4e980} fill="#818CF8" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Neuro</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Scan for suspicious deepfakes using Neuro's Community Platform.
          </p>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-8 overflow-y-auto bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
          <div className="max-w-5xl mx-auto">
            {/* Input Type Selector */}
            <div className="flex gap-3 mb-6">
              <button
                onClick={() => setInputType('url')}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-colors ${
                  inputType === 'url'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <LinkIcon size={18} />
                Enter URL
              </button>
              <button
                onClick={() => setInputType('file')}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-colors ${
                  inputType === 'file'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Upload size={18} />
                Upload File
              </button>
            </div>

            {/* Media Type Selector */}
            <div className="mb-6">
              <label className="block text-sm text-gray-600 dark:text-gray-400 mb-3">Select Media Type</label>
              <div className="flex gap-3">
                <button
                  onClick={() => setMediaType('video')}
                  className={`px-6 py-2 rounded-lg transition-colors ${
                    mediaType === 'video'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Video
                </button>
                <button
                  onClick={() => setMediaType('image')}
                  className={`px-6 py-2 rounded-lg transition-colors ${
                    mediaType === 'image'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Image
                </button>
                <button
                  onClick={() => setMediaType('audio')}
                  className={`px-6 py-2 rounded-lg transition-colors ${
                    mediaType === 'audio'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Audio
                </button>
              </div>
            </div>

            {/* URL Input */}
            {inputType === 'url' && (
              <div className="mb-8">
                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Enter {mediaType.charAt(0).toUpperCase() + mediaType.slice(1)} URL
                </label>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder={`https://example.com/${mediaType}.${mediaType === 'video' ? 'mp4' : mediaType === 'image' ? 'jpg' : 'mp3'}`}
                    className="flex-1 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-blue-500 text-sm"
                  />
                  <button
                    onClick={handleAnalyze}
                    disabled={!urlInput || isAnalyzing}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium"
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyse'}
                    {!isAnalyzing && <ArrowRight size={16} />}
                  </button>
                </div>
                <div className="flex items-center gap-4 mt-3 text-xs text-gray-500 dark:text-gray-500">
                  <span>{mediaType === 'video' ? 'Video duration should be less than 5 minutes' : `${mediaType.charAt(0).toUpperCase() + mediaType.slice(1)} file size should be less than 50MB`}</span>
                  <span>·</span>
                  <button 
                    onClick={() => {
                      const sources = mediaType === 'video' 
                        ? 'YouTube, Vimeo, Direct MP4/AVI/MOV links'
                        : mediaType === 'image'
                        ? 'Direct JPG/PNG/GIF/WEBP links, Imgur, Google Drive'
                        : 'Direct MP3/WAV/OGG links, SoundCloud';
                      alert(`Supported sources for ${mediaType}:\n\n${sources}`);
                    }}
                    className="hover:text-gray-700 dark:hover:text-gray-400 flex items-center gap-1"
                  >
                    Sources supported
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            {/* File Upload */}
            {inputType === 'file' && (
              <div className="mb-8">
                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Upload {mediaType.charAt(0).toUpperCase() + mediaType.slice(1)} File
                </label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-12 text-center hover:border-indigo-500 transition-colors cursor-pointer bg-white dark:bg-gray-900">
                  <input
                    type="file"
                    id="file-upload"
                    onChange={handleFileChange}
                    accept={
                      mediaType === 'video'
                        ? 'video/*'
                        : mediaType === 'image'
                        ? 'image/*'
                        : 'audio/*'
                    }
                    className="hidden"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    {selectedFile ? (
                      <div className="flex items-center justify-center gap-3">
                        <Upload size={32} className="text-indigo-500" />
                        <div className="text-left">
                          <p className="text-gray-900 dark:text-gray-300 font-medium">{selectedFile.name}</p>
                          <p className="text-gray-500 dark:text-gray-600 text-sm">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            setSelectedFile(null);
                          }}
                          className="ml-4 text-gray-400 hover:text-gray-900 dark:hover:text-white"
                        >
                          <X size={20} />
                        </button>
                      </div>
                    ) : (
                      <>
                        <Upload size={48} className="mx-auto mb-4 text-gray-400 dark:text-gray-500" />
                        <p className="text-gray-600 dark:text-gray-400 mb-2">
                          Drop your {mediaType} file here or click to browse
                        </p>
                        <p className="text-gray-500 dark:text-gray-600 text-sm">
                          Supported formats: {mediaType === 'video' ? 'MP4, AVI, MOV, MKV, WEBM' : mediaType === 'image' ? 'JPG, PNG, GIF, WEBP, BMP' : 'MP3, WAV, OGG, M4A, FLAC'}
                        </p>
                      </>
                    )}
                  </label>
                </div>
                <button
                  onClick={handleAnalyze}
                  disabled={!selectedFile || isAnalyzing}
                  className="w-full mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg transition-colors flex items-center justify-center gap-2 text-sm font-medium"
                >
                  {isAnalyzing ? 'Analyzing...' : `Analyse ${mediaType.charAt(0).toUpperCase() + mediaType.slice(1)}`}
                  {!isAnalyzing && <ArrowRight size={16} />}
                </button>
              </div>
            )}

            {/* Tabs */}
            <div className="flex items-center gap-6 mb-6 border-b border-gray-200 dark:border-gray-800">
              <button 
                onClick={() => setActiveTab('recent')}
                className={`flex items-center gap-2 pb-3 border-b-2 ${activeTab === 'recent' ? 'border-blue-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'} text-sm transition-colors`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recent Public Scans
              </button>
              <button 
                onClick={() => setActiveTab('top')}
                className={`flex items-center gap-2 pb-3 border-b-2 ${activeTab === 'top' ? 'border-blue-500 text-gray-900 dark:text-white' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'} text-sm transition-colors`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                Top 10 Scans
              </button>
              {scanHistory.length > 0 && (
                <button 
                  onClick={() => alert(`Total scans: ${scanHistory.length}`)}
                  className="ml-auto text-blue-500 hover:text-blue-600 text-xs"
                >
                  View All Scans
                </button>
              )}
            </div>

            {/* Scans Table */}
            {scanHistory.length === 0 ? (
              <div className="bg-white dark:bg-gray-900 rounded-lg p-12 text-center border border-gray-200 dark:border-gray-800">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-gray-600 dark:text-gray-400 mb-2">No scans yet</p>
                <p className="text-gray-500 dark:text-gray-600 text-sm">Upload a file or enter a URL to start analyzing</p>
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-900 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-800">
                {/* Table Header */}
                <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-gray-50 dark:bg-gray-800/50 text-xs text-gray-600 dark:text-gray-400 font-medium border-b border-gray-200 dark:border-gray-800">
                  <div className="col-span-6">URL / File</div>
                  <div className="col-span-3">AI Probability</div>
                  <div className="col-span-3 text-right">Scanned on</div>
                </div>

                {/* Table Rows */}
                <div className="divide-y divide-gray-200 dark:divide-gray-800">
                  {scanHistory.map((scan) => (
                    <div
                      key={scan.id}
                      onClick={() => {
                        alert(`Scan Details:\n\nFile: ${scan.title}\nType: ${scan.type}\nAI Probability: ${scan.probability}%\nStatus: ${scan.status.toUpperCase()}\nTime: ${scan.time}\n\nAnalysis: ${scan.probability > 70 ? 'High probability of deepfake detected!' : scan.probability > 40 ? 'Medium probability - further investigation recommended' : 'Low probability - likely authentic'}`);
                      }}
                      className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors cursor-pointer"
                    >
                      <div className="col-span-6 text-sm text-gray-900 dark:text-gray-300 truncate flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          scan.type === 'video' ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400' :
                          scan.type === 'image' ? 'bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400' :
                          'bg-purple-100 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400'
                        }`}>
                          {scan.type}
                        </span>
                        {scan.title}
                      </div>
                      <div className="col-span-3">
                        <div className="flex items-center gap-3">
                          <div className="flex-1 bg-gray-200 dark:bg-gray-800 rounded-full h-1.5 max-w-[120px]">
                            <div
                              className={`h-1.5 rounded-full ${getStatusColor(scan.probability)}`}
                              style={{ width: `${scan.probability}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-600 dark:text-gray-400">{scan.probability}%</span>
                        </div>
                      </div>
                      <div className="col-span-3 text-sm text-gray-600 dark:text-gray-400 text-right">
                        {scan.time}
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
