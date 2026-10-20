import { useEffect, useState } from 'react';

type Waveform = { path: string; duration: number };
const formatTime = (seconds: number) => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;

export function AudioWaveform({ mediaUrl }: { mediaUrl: string }) {
  const [waveform, setWaveform] = useState<Waveform | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    let disposed = false;
    let context: AudioContext | undefined;
    setWaveform(null);
    setError(false);
    async function decode() {
      try {
        const response = await fetch(mediaUrl, { signal: controller.signal });
        if (!response.ok) throw new Error('Audio unavailable');
        const data = await response.arrayBuffer();
        if (disposed) return;
        context = new AudioContext();
        const audio = await context.decodeAudioData(data);
        if (disposed) return;
        const channels = Array.from({ length: audio.numberOfChannels }, (_, i) => audio.getChannelData(i));
        const bins = Math.min(600, audio.length);
        const paths: string[] = [];
        for (let bin = 0; bin < bins; bin++) {
          let low = 0, high = 0;
          const start = Math.floor(bin * audio.length / bins);
          const end = Math.floor((bin + 1) * audio.length / bins);
          for (const channel of channels) {
            for (let i = start; i < end; i++) {
              low = Math.min(low, channel[i]);
              high = Math.max(high, channel[i]);
            }
          }
          const x = 40 + bin * 940 / Math.max(1, bins - 1);
          paths.push(`M${x.toFixed(1)},${(90 - Math.min(1, high) * 65).toFixed(1)}V${(90 - Math.max(-1, low) * 65).toFixed(1)}`);
        }
        setWaveform({ path: paths.join(' '), duration: audio.duration });
      } catch {
        if (!disposed) setError(true);
      } finally {
        if (context && context.state !== 'closed') void context.close().catch(() => {});
      }
    }
    if (mediaUrl) void decode();
    return () => {
      disposed = true;
      controller.abort();
      if (context && context.state !== 'closed') void context.close().catch(() => {});
    };
  }, [mediaUrl]);

  return (
    <section className="rounded-xl border border-gray-800 bg-[#12121f] p-4" aria-label="Audio waveform">
      <h3 className="text-sm font-semibold text-white">Audio waveform</h3>
      {waveform ? <>
        <svg viewBox="0 0 1000 190" className="w-full mt-3" role="img" aria-label={`Amplitude waveform for ${formatTime(waveform.duration)} of audio`}>
          <path d="M40 25V155H980 M40 90H980" stroke="#475569" fill="none" />
          <g fill="#94a3b8" fontSize="12"><text x="4" y="30">+1</text><text x="12" y="94">0</text><text x="4" y="155">−1</text></g>
          <path d={waveform.path} stroke="#38bdf8" strokeWidth="1.3" fill="none" />
          <g fill="#94a3b8" fontSize="12"><text x="40" y="180">0:00</text><text x="510" y="180" textAnchor="middle">{formatTime(waveform.duration / 2)}</text><text x="980" y="180" textAnchor="end">{formatTime(waveform.duration)}</text></g>
        </svg>
        <p className="text-xs text-gray-400">Signal amplitude over time. The waveform alone does not establish whether audio is real or fake.</p>
      </> : <p className="py-8 text-sm text-gray-400" role="status">{error ? 'Waveform preview is unavailable for this format. You can still play the recording above.' : 'Loading audio waveform…'}</p>}
    </section>
  );
}
