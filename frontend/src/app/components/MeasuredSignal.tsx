import { useEffect, useRef, useState } from 'react';

export interface SignalData {
  spectral_power: number[][];
  waveform_peaks: number[];
  duration_seconds: number;
  sample_rate: number;
  floor_db: number;
  ceiling_db: number;
}

export function MeasuredSignal({ signal, mode, position, seek }: {
  signal: SignalData; mode: 'spectrogram' | 'waveform'; position: number; seek: (seconds: number) => void;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [inspection, setInspection] = useState('Click the measured signal to seek.');
  useEffect(() => {
    const context = canvas.current?.getContext('2d');
    if (!context) return;
    const width = 720, height = 160;
    context.fillStyle = '#0a0c23'; context.fillRect(0, 0, width, height);
    if (mode === 'spectrogram') {
      const rows = signal.spectral_power;
      const pixels = context.createImageData(width, height);
      for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
        const row = rows[Math.floor((height - 1 - y) * rows.length / height)];
        const value = (row?.[Math.floor(x * row.length / width)] || 0) / 255;
        const index = (y * width + x) * 4;
        pixels.data[index] = Math.round(250 * value);
        pixels.data[index + 1] = Math.round(220 * Math.sin(value * Math.PI / 2));
        pixels.data[index + 2] = Math.round(35 + 110 * (1 - value));
        pixels.data[index + 3] = 255;
      }
      context.putImageData(pixels, 0, 0);
    } else {
      context.strokeStyle = '#32b9e8'; context.beginPath();
      signal.waveform_peaks.forEach((peak, index) => {
        const x = index * width / signal.waveform_peaks.length;
        const amplitude = Math.min(1, peak) * height / 2;
        context.moveTo(x, height / 2 - amplitude); context.lineTo(x, height / 2 + amplitude);
      }); context.stroke();
    }
    context.strokeStyle = '#ffffff'; context.lineWidth = 2;
    const x = Math.min(1, position / Math.max(.001, signal.duration_seconds)) * width;
    context.beginPath(); context.moveTo(x, 0); context.lineTo(x, height); context.stroke();
  }, [signal, mode, position]);
  return <div>
    <canvas ref={canvas} width={720} height={160} role="slider" tabIndex={0}
      aria-label="Measured audio signal; seek position" aria-valuemin={0} aria-valuemax={signal.duration_seconds}
      aria-valuenow={position} className="w-full h-44 rounded-md cursor-crosshair"
      onKeyDown={event => { if (['ArrowLeft', 'ArrowRight'].includes(event.key)) {
        event.preventDefault(); seek(Math.max(0, Math.min(signal.duration_seconds, position + (event.key === 'ArrowRight' ? 5 : -5))));
      } }}
      onClick={event => { const rect = event.currentTarget.getBoundingClientRect(); seek((event.clientX - rect.left) / rect.width * signal.duration_seconds); }}
      onPointerMove={event => {
        const rect = event.currentTarget.getBoundingClientRect();
        const x = Math.max(0, Math.min(.9999, (event.clientX - rect.left) / rect.width));
        const y = Math.max(0, Math.min(.9999, 1 - (event.clientY - rect.top) / rect.height));
        const row = signal.spectral_power[Math.floor(y * signal.spectral_power.length)];
        const power = row?.[Math.floor(x * row.length)] || 0;
        setInspection(mode === 'spectrogram' ? `${(x * signal.duration_seconds).toFixed(1)} s · ${Math.round(y * signal.sample_rate / 2)} Hz · ${(signal.floor_db + power / 255 * (signal.ceiling_db - signal.floor_db)).toFixed(1)} dB relative` : `${(x * signal.duration_seconds).toFixed(1)} s · peak envelope`);
      }} />
    <p className="text-xs text-gray-400 mt-2 tabular-nums">{inspection}</p>
  </div>;
}
