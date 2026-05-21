import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router';
import { Upload as UploadIcon, ArrowLeft } from 'lucide-react';
import svgPaths from '../../imports/MacBookPro166/svg-vk1owfvmuu';

export default function Upload() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const type = searchParams.get('type') || 'video';
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const typeConfig = {
    video: {
      title: 'VIDEO ANALYSIS',
      formats: 'MP4, AVI, MOV, MKV, WEBM',
      accept: 'video/*',
      extensions: ['.MP4', '.AVI', '.MOV', '.MKV', '.WEBM'],
    },
    audio: {
      title: 'AUDIO ANALYSIS',
      formats: 'MP3, WAV, AAC, FLAC, OGG, M4A',
      accept: 'audio/*',
      extensions: ['.MP3', '.WAV', '.AAC', '.FLAC', '.OGG'],
    },
    image: {
      title: 'IMAGE ANALYSIS',
      formats: 'JPG, JPEG, PNG, WEBP, BMP, TIFF',
      accept: 'image/*',
      extensions: ['.JPG', '.JPEG', '.PNG', '.WEBP', '.BMP'],
    },
  };

  const config = typeConfig[type as keyof typeof typeConfig] || typeConfig.video;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = () => {
    if (selectedFile) {
      // Navigate to dashboard with file info
      navigate('/dashboard', { state: { file: selectedFile, type } });
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white relative overflow-hidden">
      {/* Animated background stars */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(100)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animation: `twinkle ${Math.random() * 3 + 2}s infinite`,
              animationDelay: `${Math.random() * 3}s`,
              opacity: Math.random() * 0.5 + 0.2,
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 0.8; }
        }
      `}</style>

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
          onClick={() => navigate('/analysis-type')}
          className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Back
        </button>
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-3xl mx-auto px-8 py-16">
        {/* Badge */}
        <div className="text-center mb-8">
          <span className="inline-block px-4 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full text-blue-400 text-xs font-medium tracking-wider">
            {config.title}
          </span>
        </div>

        {/* Title */}
        <h1 className="text-5xl md:text-6xl font-bold text-center mb-4">
          Upload Your File
        </h1>
        <p className="text-center text-gray-400 text-lg mb-12">
          Supported: {config.formats}
        </p>

        {/* Upload Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 ${
            isDragging
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-gray-700 bg-gray-900/50'
          }`}
        >
          <input
            type="file"
            id="file-upload"
            onChange={handleFileChange}
            accept={config.accept}
            className="hidden"
          />

          <label htmlFor="file-upload" className="cursor-pointer">
            {/* Upload Icon */}
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-blue-600/20 flex items-center justify-center">
              <UploadIcon size={40} className="text-blue-400" />
            </div>

            {/* Text */}
            <p className="text-xl font-semibold mb-2">
              {selectedFile ? selectedFile.name : 'Drop your file or click to browse'}
            </p>
            <p className="text-gray-500 text-sm mb-8">
              Maximum file size: 500MB
            </p>

            {/* Format Badges */}
            <div className="flex flex-wrap justify-center gap-2">
              {config.extensions.map((ext) => (
                <span
                  key={ext}
                  className="px-3 py-1 bg-gray-800 border border-gray-700 rounded text-gray-400 text-xs font-medium"
                >
                  {ext}
                </span>
              ))}
            </div>
          </label>
        </div>

        {/* Analyze Button */}
        {selectedFile && (
          <div className="mt-8 text-center">
            <button
              onClick={handleAnalyze}
              className="bg-blue-600 hover:bg-blue-700 text-white px-12 py-4 rounded-xl text-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Analyze File
            </button>
          </div>
        )}

        {/* Info */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 text-sm">
            🔒 Your file is processed securely and never stored permanently
          </p>
        </div>
      </div>
    </div>
  );
}
