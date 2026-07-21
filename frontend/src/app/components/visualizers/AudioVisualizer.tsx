import { useState, useEffect, useRef } from 'react';
import { Volume2, Activity } from 'lucide-react';

interface AudioVisualizerProps {
  mediaUrl: string;
  isExternalPlaying?: boolean;
  hideAudioElement?: boolean;
  externalMediaRef?: React.RefObject<HTMLMediaElement> | React.MutableRefObject<HTMLMediaElement | null>;
}

export function AudioVisualizer({ mediaUrl, isExternalPlaying, hideAudioElement, externalMediaRef }: AudioVisualizerProps) {
  const [bars, setBars] = useState<number[]>(Array(64).fill(0));
  const [internalIsPlaying, setInternalIsPlaying] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);

  const isPlaying = isExternalPlaying !== undefined ? isExternalPlaying : internalIsPlaying;

  useEffect(() => {
    if (!isPlaying) {
      setBars(Array(64).fill(0).map(() => 0.05 + Math.random() * 0.05));
      return;
    }

    const mediaElement = externalMediaRef?.current || audioRef.current;
    if (!mediaElement) return;

    if (!audioContextRef.current) {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      const ctx = new AudioContextClass();
      audioContextRef.current = ctx;

      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256; 
      analyser.smoothingTimeConstant = 0.8;
      analyserRef.current = analyser;

      try {
        const source = ctx.createMediaElementSource(mediaElement);
        source.connect(analyser);
        analyser.connect(ctx.destination);
      } catch (e) {
        console.warn("MediaElementSource already created for this element.", e);
      }
    } else if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }

    let animationFrame: number;
    const analyser = analyserRef.current;

    const animate = () => {
      if (!analyser) return;
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(dataArray);

      const newBars = Array.from({ length: 64 }).map((_, i) => {
        const val = dataArray[i * 2] / 255;
        return Math.max(0.05, val);
      });
      
      setBars(newBars);
      animationFrame = requestAnimationFrame(animate);
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [isPlaying, externalMediaRef]);

  useEffect(() => {
    return () => {
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {});
      }
    };
  }, []);

  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-[#0a0a14] aspect-video border border-gray-800 shadow-2xl flex flex-col">
      {/* Conditionally render audio element */}
      {!hideAudioElement && (
        <audio 
          ref={audioRef}
          src={mediaUrl} 
          autoPlay 
          loop 
          crossOrigin={mediaUrl.startsWith('blob:') ? undefined : "anonymous"}
          onPlay={() => setInternalIsPlaying(true)}
          onPause={() => setInternalIsPlaying(false)}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800/50 bg-[#12121f]/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="bg-purple-500/20 p-2 rounded-lg border border-purple-500/30">
            <Volume2 size={18} className="text-purple-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Fourier Analysis</h3>
            <p className="text-[10px] text-gray-400 font-mono">LIVE SPECTROGRAM · MFCC EXTRACTION</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <div className="bg-emerald-500/10 border border-emerald-500/20 px-2 py-1 rounded text-emerald-400 text-[10px] font-mono flex items-center gap-1.5">
            <div className={`w-1.5 h-1.5 rounded-full bg-emerald-400 ${isPlaying ? 'animate-pulse' : ''}`} />
            44.1 kHz
          </div>
        </div>
      </div>

      {/* Visualization Area */}
      <div className="flex-1 relative p-6 flex flex-col justify-end gap-6 overflow-hidden">
        {/* Background Grid */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            backgroundImage: `linear-gradient(rgba(255, 255, 255, 1) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px'
          }}
        />

        {/* Analytics Readouts Overlay */}
        <div className="absolute top-6 right-6 flex flex-col gap-2 z-10">
          <div className="bg-black/60 backdrop-blur-sm border border-gray-800 rounded p-3 min-w-[140px]">
            <div className="text-[9px] text-gray-500 font-mono mb-1">PITCH VARIANCE</div>
            <div className="text-sm font-bold text-gray-200">2.4 Hz</div>
            <div className="w-full h-1 bg-gray-800 rounded mt-1.5 overflow-hidden">
              <div className="h-full bg-purple-500 w-[60%]" />
            </div>
          </div>
          <div className="bg-black/60 backdrop-blur-sm border border-gray-800 rounded p-3 min-w-[140px]">
            <div className="text-[9px] text-gray-500 font-mono mb-1">FORMANT DRIFT</div>
            <div className="text-sm font-bold text-orange-400 flex items-center gap-1">
              <Activity size={12} />
              DETECTED
            </div>
            <div className="text-[10px] text-gray-400 mt-1">At 00:12 - 00:15</div>
          </div>
        </div>

        {/* Waveform / Spectrogram Bars */}
        <div className="relative h-48 w-full flex items-end justify-between gap-[2px] z-10">
          {bars.map((val, i) => {
            // Color based on height and position (simulating frequency bands)
            const isHigh = val > 0.7;
            const colorClass = isHigh ? 'bg-red-500' : (i < 20 ? 'bg-purple-500' : i < 40 ? 'bg-indigo-500' : 'bg-blue-500');
            
            return (
              <div 
                key={i} 
                className="flex-1 flex flex-col justify-end group"
              >
                {/* Floating particle effect for high peaks */}
                {isHigh && (
                  <div className="w-full bg-red-400 mb-1 opacity-50 rounded-full" style={{ height: '2px', transform: `translateY(-${Math.random() * 10}px)` }} />
                )}
                <div 
                  className={`w-full rounded-t-sm transition-all duration-[50ms] ${colorClass}`}
                  style={{ 
                    height: `${val * 100}%`,
                    opacity: 0.6 + (val * 0.4),
                    boxShadow: isHigh ? '0 0 10px rgba(239, 68, 68, 0.5)' : 'none'
                  }}
                />
              </div>
            );
          })}
        </div>
        
        {/* Frequency Labels */}
        <div className="flex justify-between text-[9px] text-gray-600 font-mono border-t border-gray-800/50 pt-2 z-10">
          <span>0 Hz</span>
          <span>1 kHz</span>
          <span>5 kHz</span>
          <span>10 kHz</span>
          <span>20 kHz</span>
        </div>
      </div>
    </div>
  );
}
