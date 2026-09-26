import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router';
import { Upload as UploadIcon, ArrowLeft, Youtube } from 'lucide-react';
import BrandLogo from '../components/BrandLogo';

export default function Upload() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const type = searchParams.get('type') || 'video';
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [ytUrl, setYtUrl] = useState('');
  const [isProcessingYt, setIsProcessingYt] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const typeConfig = {
    video: {
      title: 'Upload Video',
      accept: 'video/*',
      desc: 'MP4, WebM or Ogg (Max 100MB)',
      icon: <UploadIcon className="w-12 h-12 text-cyan-400 mb-4" />
    },
    audio: {
      title: 'Upload Audio',
      accept: 'audio/*',
      desc: 'MP3, WAV or OGG (Max 50MB)',
      icon: <UploadIcon className="w-12 h-12 text-cyan-400 mb-4" />
    },
    image: {
      title: 'Upload Image',
      accept: 'image/*',
      desc: 'JPG, PNG or WebP (Max 20MB)',
      icon: <UploadIcon className="w-12 h-12 text-cyan-400 mb-4" />
    }
  };

  const config = typeConfig[type as keyof typeof typeConfig] || typeConfig.video;

  // Background animation logic
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 20;
      const y = (e.clientY / window.innerHeight - 0.5) * 20;
      document.documentElement.style.setProperty('--mouse-x', `${x}px`);
      document.documentElement.style.setProperty('--mouse-y', `${y}px`);
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (file: File) => {
    setSelectedFile(file);
    setTimeout(() => {
      navigate('/dashboard', { state: { file, type } });
    }, 500);
  };

  const handleYtSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ytUrl) return;

    setIsProcessingYt(true);
    setTimeout(() => {
      navigate('/dashboard', { state: { url: ytUrl, type: 'video' } });
    }, 800);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute -top-[30%] -left-[10%] w-[70%] h-[70%] bg-cyan-500/10 rounded-full blur-[120px] mix-blend-screen transition-transform duration-1000"
          style={{ transform: 'translate(var(--mouse-x, 0), var(--mouse-y, 0))' }}
        ></div>
        <div
          className="absolute -bottom-[30%] -right-[10%] w-[70%] h-[70%] bg-indigo-500/10 rounded-full blur-[120px] mix-blend-screen transition-transform duration-1000"
          style={{ transform: 'translate(calc(var(--mouse-x, 0) * -1), calc(var(--mouse-y, 0) * -1))' }}
        ></div>
      </div>

      {/* Header */}
      <header className="absolute top-0 w-full p-6 flex justify-between items-center z-20">
        <div className="flex items-center gap-3">
          <BrandLogo size={40} />
          <span className="text-xl font-bold" style={{ fontFamily: "'Eagle Lake', serif" }}>
            SynPhi
          </span>
        </div>
        <button
          onClick={() => navigate('/analysis-type')}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors px-4 py-2 rounded-lg hover:bg-white/5"
        >
          <ArrowLeft size={16} />
          Change Type
        </button>
      </header>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-4">
        <div className="max-w-2xl w-full text-center mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <span className="inline-block px-4 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full text-blue-400 text-xs font-medium tracking-wider mb-6">
            STEP 2 OF 3
          </span>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
            {config.title}
          </h1>
          <p className="text-gray-400 text-lg">
            Upload your media file for forensic analysis.
          </p>
        </div>

        <div className="w-full max-w-xl animate-in fade-in slide-in-from-bottom-8 duration-700 delay-150">
          {/* YouTube/URL input for video type */}
          {type === 'video' && (
            <div className="bg-white/[0.02] border border-white/10 rounded-2xl p-6 shadow-2xl backdrop-blur-sm mb-6">
              <div className="flex items-center gap-2 mb-4">
                <Youtube className="text-red-500 w-5 h-5" />
                <h3 className="font-medium">Scan YouTube Video</h3>
              </div>
              <form onSubmit={handleYtSubmit} className="flex gap-3">
                <input
                  type="url"
                  placeholder="Paste YouTube or video URL here..."
                  value={ytUrl}
                  onChange={(e) => setYtUrl(e.target.value)}
                  className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-cyan-500/50 transition-colors"
                />
                <button
                  type="submit"
                  disabled={!ytUrl || isProcessingYt}
                  className="bg-cyan-600 hover:bg-cyan-500 text-white px-6 py-3 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 whitespace-nowrap"
                >
                  {isProcessingYt ? 'Processing...' : 'Scan URL'}
                </button>
              </form>
            </div>
          )}

          {/* File Upload Area */}
          <div className="bg-white/[0.02] border border-white/10 rounded-3xl p-8 shadow-2xl backdrop-blur-sm">
            <div
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ease-out flex flex-col items-center justify-center
                ${dragActive
                  ? 'border-cyan-400 bg-cyan-400/5 scale-[1.02] shadow-[0_0_30px_rgba(34,211,238,0.1)]'
                  : 'border-white/10 hover:border-white/20 hover:bg-white/[0.02]'
                }
                ${selectedFile ? 'border-emerald-500/50 bg-emerald-500/5' : ''}
              `}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept={config.accept}
                onChange={handleChange}
                className="hidden"
              />

              <div className={`transition-all duration-300 ${dragActive ? 'scale-110' : 'scale-100'}`}>
                {config.icon}
              </div>

              {selectedFile ? (
                <div className="animate-in zoom-in duration-300">
                  <p className="text-lg font-medium text-emerald-400 mb-2">File selected!</p>
                  <p className="text-sm text-gray-400">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500 mt-4 animate-pulse">Redirecting to analysis...</p>
                </div>
              ) : (
                <>
                  <h3 className="text-xl font-semibold mb-2">
                    Drag and drop your file here
                  </h3>
                  <p className="text-sm text-gray-400 mb-6">
                    or click to browse from your computer
                  </p>
                  <div className="inline-flex items-center justify-center px-6 py-2.5 border border-white/10 rounded-xl text-sm font-medium hover:bg-white/5 transition-colors cursor-pointer group">
                    Select File
                    <ArrowLeft className="w-4 h-4 ml-2 rotate-180 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </div>
                  <p className="text-xs text-gray-500 mt-6 mt-auto">
                    {config.desc}
                  </p>
                </>
              )}
            </div>
          </div>

          <p className="text-center text-xs text-gray-500 mt-6 max-w-md mx-auto leading-relaxed">
            By uploading a file, you agree to our Terms of Service. Files are processed securely and deleted immediately after analysis.
          </p>
        </div>
      </div>
    </div>
  );
}
