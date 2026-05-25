import React from 'react';

interface ScanningViewProps {
  progress: number;
  statusText: string;
  mediaUrl?: string;
  mediaType?: 'video' | 'image' | 'audio';
}

export function ScanningView({ progress, statusText, mediaUrl, mediaType }: ScanningViewProps) {
  // Calculate SVG circle properties for the progress ring
  const radius = 120;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative w-full h-[500px] bg-[#0e0e18] rounded-2xl border border-gray-800 overflow-hidden flex flex-col items-center justify-center">
      {/* Background Blur Overlay (simulate analyzing) */}
      <div className="absolute inset-0 z-0 overflow-hidden opacity-30">
        {mediaType === 'video' && mediaUrl ? (
          <video 
            src={mediaUrl} 
            className="w-full h-full object-cover blur-xl scale-110 grayscale" 
            autoPlay 
            muted 
            loop 
            playsInline 
          />
        ) : mediaType === 'image' && mediaUrl ? (
          <img 
            src={mediaUrl} 
            alt="Scanning preview" 
            className="w-full h-full object-cover blur-xl scale-110 grayscale" 
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-indigo-900/40 to-violet-900/40" />
        )}
      </div>

      {/* Grid overlay */}
      <div 
        className="absolute inset-0 z-0 opacity-20"
        style={{
          backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px)`,
          backgroundSize: '40px 40px'
        }}
      />

      {/* Progress Circle Container */}
      <div className="relative z-10 flex flex-col items-center">
        <div className="relative flex items-center justify-center mb-6">
          {/* Background circle */}
          <svg
            height={radius * 2}
            width={radius * 2}
            className="transform -rotate-90"
          >
            <circle
              stroke="rgba(255,255,255,0.05)"
              fill="transparent"
              strokeWidth={stroke}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              // Segmented circle effect
              strokeDasharray="20 10" 
            />
            {/* Progress circle */}
            <circle
              stroke="url(#progressGradient)"
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + ' ' + circumference}
              style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.5s ease-in-out' }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            <defs>
              <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#818CF8" />
                <stop offset="100%" stopColor="#A78BFA" />
              </linearGradient>
            </defs>
          </svg>

          {/* Percentage Text inside circle */}
          <div className="absolute flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-white tracking-tighter">
              {Math.round(progress)}<span className="text-xl text-gray-400 ml-1">%</span>
            </span>
          </div>
        </div>

        {/* Status Text with typing/pulse effect */}
        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-lg font-medium text-gray-300 tracking-wide">
            {statusText}
          </span>
        </div>
      </div>
    </div>
  );
}
