import { useState, useEffect, useRef } from 'react';
import { Menu, ArrowRight, Upload, X, Monitor, Moon, Sun, Paperclip, ChevronLeft, ShieldAlert, ShieldCheck, Info } from 'lucide-react';
import BrandLogo from '../components/BrandLogo';
import { AudioReview, type AuditEvidence } from '../components/AudioReview';
import { AuditReportDownload } from '../components/AuditReportDownload';
import { loadScans, saveScan, clearScans, compactScans, type SavedScan, type AnalysisResult } from '../scanHistory';
import { fetchCloudResult } from '../firebaseHistory';
import { useAuth } from '../../contexts/AuthContext';
import { AccountControl } from '../components/AccountControl';
import { ManualVerification } from '../components/ManualVerification';
import { Link, useLocation } from 'react-router';
import './dashboard-workspace.css';

// Visualizers
import { ScanningView } from '../components/visualizers/ScanningView';
import { VideoVisualizer } from '../components/visualizers/VideoVisualizer';
import { ImageVisualizer } from '../components/visualizers/ImageVisualizer';

// Use the hosted backend consistently in local development and deployed builds.
const API_BASE_URL = 'https://shlok0829-deepfake.hf.space';

type Theme = 'system' | 'dark' | 'light';
type ScanState = 'idle' | 'scanning' | 'results';

export default function Dashboard() {
  const location = useLocation();
  const {user}=useAuth();
  const historyOwner=user?.uid || 'local-development';
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(() => {
    const incoming = (location.state as {file?:File} | null)?.file;
    return incoming instanceof File && incoming.size <= 1024 ** 3 ? incoming : null;
  });
  const [scanError, setScanError] = useState('');
  const [scanHistory, setScanHistory] = useState<SavedScan[]>([]);
  const [currentTitle, setCurrentTitle] = useState('');
  const [currentTime, setCurrentTime] = useState('');
  const [historyNotice, setHistoryNotice] = useState('');
  const activeRequest = useRef(0);
  const requestController = useRef<AbortController | null>(null);

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
  const [currentEvidence, setCurrentEvidence] = useState<AuditEvidence | null>(null);
  const [currentPdf, setCurrentPdf] = useState<string>();
  const [currentPdfFilename, setCurrentPdfFilename] = useState<string>();
  const [currentReportError, setCurrentReportError] = useState<string>();

  useEffect(() => {
    let active=true;
    void loadScans(historyOwner,setHistoryNotice).then(rows=>{if(active)setScanHistory(previous=>{
      const merged=new Map([...rows,...previous].map(scan=>[scan.id,scan]));
      return compactScans([...merged.values()].sort((a,b)=>b.createdAt-a.createdAt));
    });}).catch(()=>{if(active)setHistoryNotice('History is available for this session; browser storage is unavailable.');});
    return ()=>{active=false;requestController.current?.abort();};
  },[historyOwner]);

  function showResult(result: AnalysisResult, title: string, type: 'audio' | 'video' | 'image', timestamp: string) {
    setCurrentTitle(title);setCurrentTime(timestamp);setCurrentScanType(result.file_type || type);
    setCurrentIsFake(result.is_fake);setCurrentAudioNeedsReview(Boolean(result.review_required));
    setCurrentAiSummary(`Model prediction: ${result.is_fake ? 'Fake' : 'Real'}. This is not proof of authenticity.`);
    setCurrentDetectedTool(result.detected_tool || '');setCurrentEvidence(result.audit_report || null);
    setCurrentPdf(result.report_pdf_base64);setCurrentPdfFilename(result.report_filename);setCurrentReportError(result.report_error);
    setScanState('results');setMobileMenuOpen(false);
  }
  async function openSavedScan(scan: SavedScan) {
    const request=++activeRequest.current;requestController.current?.abort();
    let result=scan.result;
    try {if(!result)result=await fetchCloudResult(scan.id,historyOwner);}
    catch {setHistoryNotice('This saved account report could not be loaded. Please retry after checking your connection.');return;}
    if(activeRequest.current!==request)return;
    setCurrentMediaUrl(scan.mediaBlob ? URL.createObjectURL(scan.mediaBlob) : scan.sourceUrl
      ? `${API_BASE_URL}/api/v1/proxy-media?url=${encodeURIComponent(scan.sourceUrl)}` : '');
    showResult(result,scan.title,scan.type,scan.time);
  }

  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<Theme>(() => { try { return localStorage.getItem('synphi-theme') === 'light' ? 'light' : 'dark'; } catch { return 'dark'; } });
  useEffect(() => {
    document.documentElement.classList.toggle('dark', currentTheme !== 'light');
    try { localStorage.setItem('synphi-theme', currentTheme === 'light' ? 'light' : 'dark'); } catch { /* Storage can be disabled. */ }
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
      if (e.target.files[0].size > 1024 ** 3) { window.alert('Maximum file size is 1 GB.'); e.target.value = ''; return; }
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
    if (!urlInput.trim() && !selectedFile) return;
    if (!selectedFile) { try { const link = new URL(urlInput.trim()); if (!['https:', 'http:'].includes(link.protocol)) throw new Error(); } catch { setScanError('Enter a complete public http:// or https:// media link.'); return; } }
    if (selectedFile && selectedFile.size > 1024 ** 3) { window.alert('Maximum file size is 1 GB.'); return; }
    setScanError('');
    requestController.current?.abort();
    const controller=new AbortController();requestController.current=controller;
    const requestId=++activeRequest.current;
    const title=selectedFile ? selectedFile.name : urlInput;
    setCurrentTitle(title);

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
    setCurrentEvidence(null); setCurrentPdf(undefined); setCurrentPdfFilename(undefined); setCurrentReportError(undefined);
    setScanProgress(0);
    setScanStatusText('Initiating Scan...');

    // Mock scanning progression just for visual feedback while waiting for backend
    let progress = 0;
    const interval = window.setInterval(() => {
      if(activeRequest.current!==requestId){window.clearInterval(interval);return;}
      progress += Math.random() * 5 + 2;
      // Cap at 90% while waiting for the actual backend response
      if (progress > 90) progress = 90;
      setScanProgress(progress);

      setScanStatusText('Waiting for model analysis...');
    }, 400);

    try {
      let resultData: any;
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        const res = await fetch(`${API_BASE_URL}/api/v1/detect`, {
          method: 'POST',
          body: formData,
          signal: controller.signal,
        });
        resultData = await res.json().catch(()=>({detail:`Upload failed (HTTP ${res.status}). The hosting gateway returned a non-JSON response.`}));
        if (!res.ok) {
          throw new Error(resultData.detail || 'Backend scan failed');
        }
      } else {
        const res = await fetch(`${API_BASE_URL}/api/v1/detect/url`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: urlInput.trim() }),
          signal: controller.signal,
        });
        resultData = await res.json().catch(()=>({detail:`Request failed (HTTP ${res.status}). The hosting gateway returned a non-JSON response.`}));
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
      if(activeRequest.current!==requestId)return;
      setScanProgress(100);
      setScanStatusText('Finalizing report...');

        const createdAt=Date.now();
        const newScan: SavedScan = {
          id: crypto.randomUUID(), createdAt, result: resultData,
          title,
          type: ['audio', 'video', 'image'].includes(resultData.file_type) ? resultData.file_type : type,
          time: new Date(createdAt).toLocaleString(),
          status: resultData.is_fake ? 'high' : 'low',
          mediaBlob: selectedFile || undefined, sourceUrl: selectedFile ? undefined : urlInput,
        };
        setScanHistory(prev => compactScans([newScan, ...prev]));
        showResult(resultData,title,newScan.type,newScan.time);
        void saveScan(newScan,historyOwner,setHistoryNotice).catch(()=>saveScan({...newScan,mediaBlob:undefined},historyOwner,setHistoryNotice)).catch(()=>{
          setHistoryNotice('This result is available for this session, but could not be saved to browser storage.');
        });

    } catch (error) {
      console.error("Backend scan failed:", error);
      window.clearInterval(interval);
      if(controller.signal.aborted || activeRequest.current!==requestId)return;
      setScanStatusText(error instanceof Error ? error.message : 'Scan failed. Ensure backend is running.');
      setScanError(error instanceof Error ? error.message : 'Upload or analysis failed. Please retry.');
      setScanState('idle');
    }
  };

  const handleThemeChange = (theme: Theme) => {
    setCurrentTheme(theme);
    setShowThemeMenu(false);

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
                <button type="button" onClick={() => openSavedScan(scan)} title={scan.title}
                  key={scan.id}
                  className="w-full text-left min-h-10 text-[11px] text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white py-1.5 px-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-colors flex items-center gap-2 focus-visible:outline focus-visible:outline-cyan-400"
                >
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${scan.status === 'high' ? 'bg-red-500' : 'bg-emerald-500'}`}></div>
                  <span className="truncate">{scan.title}</span>
                </button>
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
          <AccountControl />
          {scanHistory.length>0 && <button type="button" onClick={async()=>{
            if(!window.confirm(`Delete saved history ${user?'for this account':'on this browser'}? This cannot be undone.`))return;
            try {await clearScans(historyOwner);setScanHistory([]);setScanState('idle');setCurrentMediaUrl('');setCurrentEvidence(null);setCurrentPdf(undefined);}
            catch {setHistoryNotice('History could not be completely removed. Check your connection and retry.');}
          }} className="w-full min-h-10 rounded-lg px-3 text-xs text-gray-400 hover:bg-gray-800">Clear saved history</button>}
          <div className="flex justify-center gap-4 text-[10px] text-gray-500 pt-2"><Link to="/terms">Terms</Link><Link to="/privacy">Privacy</Link></div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="synphi-workspace flex-1 flex flex-col min-w-0 min-h-0 relative">
        <header className="flex items-center gap-3 border-b border-gray-200 dark:border-gray-800/50 bg-white dark:bg-[#0e0e18] px-3 py-2 lg:hidden"><button aria-label="Open navigation" aria-expanded={mobileMenuOpen} aria-controls="dashboard-navigation" onClick={() => setMobileMenuOpen(true)} className="flex min-h-11 min-w-11 items-center justify-center text-gray-500 dark:text-gray-300"><Menu size={22} /></button><BrandLogo size={25} /><span className="text-sm font-semibold">SynPhi</span></header>

        {scanState === 'idle' && (
          <div className="workspace-idle flex-1 overflow-y-auto">
            <div className="workspace-topbar"><span className="workspace-mode">Media analysis</span><span className="text-xs text-gray-500">SynPhi workspace</span></div>
            <div className="workspace-welcome">
              <div className="jelly-orb" aria-hidden="true"><span /><i /></div>
              <p className="workspace-greeting">{user?.displayName ? `Welcome, ${user.displayName.split(' ')[0]}` : 'Welcome to SynPhi'}</p>
              <h1>What would you like to verify?</h1>
              <p className="workspace-subtitle">A closer look at audio, images and video. Start with a file or a link.</p>
            </div>
            <div className="workspace-body p-4 sm:p-8">
              <div className="max-w-4xl mx-auto">
                {/* Input Bar */}
                <div className="workspace-composer mb-4">
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
                        <div className="workspace-file min-w-0 flex-1 flex items-center gap-2">
                          <Paperclip size={18} className="text-indigo-400 flex-shrink-0" />
                          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{selectedFile.name}</span>
                          <span className="workspace-file-size text-xs text-gray-400 flex-shrink-0">({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)</span>
                          <button type="button" aria-label="Remove selected file" onClick={() => { setSelectedFile(null); if (fileInputRef.current) fileInputRef.current.value = ''; }} className="workspace-remove"><X size={16} /></button>
                        </div>
                      ) : (
                        <input
                          type="text"
                          value={urlInput}
                          onChange={(e) => setUrlInput(e.target.value)}
                          onKeyDown={(e) => { if (e.key === 'Enter') handleAnalyze(); }}
                          aria-label="Media URL" placeholder="Paste a media link, or attach your file..."
                          className="min-w-0 flex-1 bg-transparent px-3 sm:px-5 py-4 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none text-base sm:text-sm"
                        />
                      )}
                      {!selectedFile && (
                        <button onClick={() => { if (fileInputRef.current) { fileInputRef.current.accept = '*/*'; fileInputRef.current.click(); } }} className="px-4 text-gray-400 hover:text-indigo-400 transition-colors" title="Attach large file"><Upload size={20} /></button>
                      )}
                      <button
                        onClick={handleAnalyze}
                        disabled={!urlInput && !selectedFile}
                        aria-label="Analyse media" className="workspace-submit bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-800 disabled:text-gray-500 text-white w-full sm:w-auto justify-center px-4 sm:px-6 py-4 transition-colors flex items-center gap-2 text-sm font-semibold flex-shrink-0"
                      >
                        <span className="workspace-submit-label">Analyse</span><ArrowRight size={16} />
                      </button>
                    </div>
                  </div>
                </div>

                <div className="workspace-upload-hint flex items-center gap-3 mb-10 text-xs text-gray-400 dark:text-gray-500 px-2">
                  <span>Supports media files up to 1 GB</span>
                </div>

                {scanError && <div role="alert" className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"><p>{scanError}</p><p className="mt-2 text-xs text-gray-400">Your selected file is retained. Retry with Analyse.</p></div>}
                <div className="workspace-shortcuts">{(['Image', 'Audio', 'Video'] as const).map(kind => <button key={kind} type="button" onClick={() => { if (fileInputRef.current) { fileInputRef.current.accept = kind.toLowerCase() + '/*'; fileInputRef.current.click(); } }}><span>{kind === 'Image' ? '▧' : kind === 'Audio' ? '≋' : '▷'}</span><strong>{kind} analysis</strong><ArrowRight size={16} /><small>{kind === 'Audio' ? 'Assess speech for synthetic patterns. Inspect its waveform and frequency energy.' : kind === 'Video' ? 'Assess faces across sampled frames. Review the footage alongside the model result.' : 'Assess face regions for manipulation. Inspect the original and download a report.'}</small></button>)}</div>
              </div>
            </div>
          </div>
        )}

        {/* SCANNING STATE */}
        {scanState === 'scanning' && (
          <div className="flex-1 flex flex-col p-4 sm:p-8 items-center justify-center bg-[#08080e]">
            {/* Top Toast */}
            <div className="w-full max-w-4xl mb-5 bg-emerald-500/10 border border-emerald-500/30 px-4 py-3 rounded-xl flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-emerald-400">Media submitted for scanning</p>
                <p className="text-xs text-gray-400 mt-1">Detailed forensics will be available shortly.</p>
              </div>
            </div>

            <div className="w-full max-w-4xl">
              <div className="flex items-center gap-3 mb-6 text-gray-400">
                <span title={currentTitle} className="block w-full min-w-0 break-words [overflow-wrap:anywhere] font-mono text-xs sm:text-sm uppercase tracking-wider">{currentTitle}</span>
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
          <div className="flex-1 min-h-0 flex flex-col bg-[#08080e] overflow-y-auto md:overflow-hidden">
            {/* Header / Back button */}
            <div className="shrink-0 p-4 border-b border-gray-800/50 flex items-center gap-4 bg-[#0e0e18]">
              <button onClick={() => setScanState('idle')} className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors">
                <ChevronLeft size={20} />
              </button>
              <div className="min-w-0">
                <h2 title={currentTitle} className="text-base sm:text-lg font-bold text-white truncate max-w-md">{currentTitle}</h2>
                <p className="text-[10px] sm:text-xs text-gray-400 font-mono uppercase tracking-wider break-words">Analysis Complete · {currentScanType} · {currentTime}</p>
              </div>
            </div>

            <div className="flex-1 min-h-0 flex flex-col md:flex-row md:overflow-hidden">
              {/* Left Panel: Summary Classification */}
              <div className="w-full md:w-72 xl:w-80 border-b md:border-b-0 md:border-r border-gray-800/50 bg-[#0a0a14] p-4 xl:p-6 md:overflow-y-auto flex-shrink-0">
                <h3 className="text-sm font-bold text-white mb-6 uppercase tracking-wider">Classification</h3>

                {/* Binary model prediction; no confidence score is displayed. */}
                <div className={`p-5 rounded-2xl border mb-6 ${currentIsFake ? 'bg-red-500/10 border-red-500/30' : 'bg-emerald-500/10 border-emerald-500/30'}`}>
                  <div className="flex items-center gap-3">{currentIsFake ? <ShieldAlert className="text-red-400 shrink-0" size={22} /> : <ShieldCheck className="text-emerald-400 shrink-0" size={22} />}<p className="text-lg font-bold text-white">{currentIsFake ? (currentScanType === 'audio' ? 'Fake (Synthetic audio)' : 'Fake') : 'Real'}</p></div>
                  <p className="mt-3 text-xs leading-6 text-gray-300">{currentScanType === 'audio' ? `The speech detector classified the recording as ${currentIsFake ? 'synthetic' : 'real'} from sampled speech windows. This recording-level decision does not confirm specific manipulated segments.` : (currentEvidence?.scope || 'Model prediction based on the analyzed regions.') + ' This result is not proof of authenticity.'}</p>
                </div>
                <div className="hidden md:flex gap-2.5 rounded-xl border border-gray-800 bg-[#12121f] p-4 mb-4 text-xs leading-5 text-gray-300"><Info size={17} className="shrink-0 mt-0.5 text-gray-400" /><p>This automated assessment is a prediction, not definitive proof. Review the original file and the report before drawing conclusions.</p></div>
                {currentScanType === 'audio' && (
                  <div className="hidden md:block space-y-4">
                    <div className="bg-[#12121f] rounded-xl p-4 border border-gray-800">
                      <p className="text-[10px] text-gray-500 font-mono mb-3">DETECTION DETAILS</p>
                      <div className="space-y-3">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Detector</span>
                          <span className="text-white font-medium">
                            SynPhi Audio
                          </span>
                        </div>
                        <div className="flex justify-between gap-3 text-xs"><span className="text-gray-400">Analysis</span><span className="text-gray-200 text-right">{currentEvidence?.coverage?.window_count ? `${currentEvidence.coverage.window_count} windows / ${Math.round(currentEvidence.coverage.analyzed_seconds || 0)}s assessed` : 'Coverage not recorded'}</span></div>
                        <div className="flex justify-between gap-3 text-xs"><span className="text-gray-400">Output</span><span className="text-gray-200">Binary (Real / Fake)</span></div>
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
                {currentScanType !== 'audio' && <>
                  <div className="hidden md:block rounded-xl border border-gray-800 bg-[#12121f] p-4 text-xs space-y-3">
                    <p className="text-[10px] text-gray-500 font-mono">DETECTION DETAILS</p>
                    <div className="flex justify-between gap-3"><span className="text-gray-400">Detector</span><span className="text-white text-right">SynPhi {currentScanType === 'video' ? 'Video' : 'Image'}</span></div>
                    <div className="flex justify-between gap-3"><span className="text-gray-400">Output</span><span className="text-gray-200">Binary (Real / Fake)</span></div>
                    <div className="flex justify-between gap-3"><span className="text-gray-400">Assessment</span><span className="text-white">{currentIsFake?'Fake':'Real'}</span></div>
                  </div>
                </>}
              </div>

              {/* Main Visualizer Area */}
              <div className="min-w-0 min-h-0 flex-1 p-4 sm:p-6 xl:p-8 bg-black/20 md:overflow-y-auto flex items-start justify-center">
                <div className="w-full min-w-0 max-w-5xl shrink-0">
                  {!currentMediaUrl && <p role="status" className="mb-4 text-sm text-gray-400">The saved result and report are available. This recording’s preview was not retained in browser storage.</p>}
                  {currentScanType === 'video' && currentMediaUrl && (
                    <div className="flex flex-col gap-6">
                      <VideoVisualizer
                        mediaUrl={currentMediaUrl || '/placeholder.mp4'}
                        externalVideoRef={videoElementRef}
                      />
                    </div>
                  )}
                  {currentScanType === 'audio' && (
                    <div className="space-y-4">
                      <AudioReview key={currentMediaUrl} mediaUrl={currentMediaUrl} evidence={currentEvidence} />
                    </div>
                  )}
                  {currentScanType === 'image' && currentMediaUrl && <ImageVisualizer mediaUrl={currentMediaUrl} aiSummary={currentAiSummary} detectedTool={currentDetectedTool} />}
                  {currentScanType !== 'audio' && <ManualVerification key={currentTitle} type={currentScanType} />}
                  <AuditReportDownload key={currentEvidence?.report_id || currentTitle} pdf={currentPdf} filename={currentPdfFilename} evidence={currentEvidence} error={currentReportError} />
                  {historyNotice && <p role="status" className="mt-3 text-xs text-orange-300">{historyNotice}</p>}

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
