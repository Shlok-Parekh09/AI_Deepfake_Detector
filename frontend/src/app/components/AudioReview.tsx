import { useRef, useState } from 'react';
import { AudioWaveform } from './visualizers/AudioWaveform';
import { MeasuredSignal, type SignalData } from './MeasuredSignal';

export interface AuditEvidence {
  report_id: string;
  generated_at: string;
  model?: { arch?: string; source?: string; revision?: string };
  metrics?: Record<string, string>;
  coverage?: { analyzed_seconds?: number; window_count?: number };
  spectrogram_png_base64?: string;
  signal?: SignalData;
  scope?: string;
  decision_method?: string;
}

const checks = [
  ['Pacing and breathing', 'Listen for abrupt word joins, unusual pauses, and changes in breath or emotional flow.'],
  ['Background continuity', 'Check for sudden changes in room tone, music, noise, or recording quality.'],
  ['Speech transitions', 'Listen for slurs, clicks, glitches, and words that sound awkwardly joined.'],
  ['Pitch and expression', 'Compare vocal inflection and emphasis with an independently sourced genuine recording.'],
];
const time = (n: number) => `${Math.floor(n / 60)}:${String(Math.floor(n % 60)).padStart(2, '0')}`;

export function AudioReview({ mediaUrl, evidence }: { mediaUrl: string; evidence: AuditEvidence | null }) {
  const audio = useRef<HTMLAudioElement>(null);
  const [tab, setTab] = useState<'spectrogram' | 'waveform'>('spectrogram');
  const [rate, setRate] = useState('1');
  const [position, setPosition] = useState(0);
  const duration = Number.parseFloat(evidence?.metrics?.['Recording duration'] || '0');
  return <div className="space-y-4">
    <div className="flex flex-col sm:flex-row sm:items-center gap-3">
      <audio ref={audio} onTimeUpdate={event => setPosition(event.currentTarget.currentTime)} controls preload="metadata" src={mediaUrl || undefined} className="w-full min-w-0" aria-label="Original recording" />
      <label className="flex shrink-0 items-center gap-2 text-xs text-gray-400">
        Playback
        <select aria-label="Playback speed" value={rate} onChange={event => {
          setRate(event.target.value);
          if (audio.current) { audio.current.preservesPitch = true; audio.current.playbackRate = Number(event.target.value); }
        }} className="rounded-md bg-[#12121f] border border-gray-700 px-2 py-2 text-white">
          <option value="0.75">0.75x</option><option value="1">1x</option><option value="1.25">1.25x</option>
        </select>
      </label>
    </div>
    <section className="rounded-xl border border-gray-800 bg-[#12121f] p-4" aria-label="Audio signal inspection">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h3 className="text-sm font-semibold text-white">Spectrogram &amp; waveform</h3>
        <div className="inline-flex rounded-lg border border-gray-700 p-0.5 gap-0.5" aria-label="Signal view">
          {(['spectrogram', 'waveform'] as const).map(view => <button key={view} type="button" aria-pressed={tab === view}
            onClick={() => setTab(view)} className={`min-h-9 px-3 rounded-md text-xs capitalize focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-400 ${tab === view ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}>{view}</button>)}
        </div>
      </div>
      {evidence?.signal ? <><MeasuredSignal signal={evidence.signal} mode={tab} position={position} seek={seconds => { if (audio.current && mediaUrl) { audio.current.currentTime = seconds; setPosition(seconds); } }} /><p className="text-xs leading-5 text-gray-400 mt-3">Measured from this recording. Spectral colors show relative frequency energy; waveform bars show peak amplitude. These are sampled signal views, not manipulation attribution.</p></> : tab === 'waveform' ? (mediaUrl ? <AudioWaveform mediaUrl={mediaUrl} /> : <p className="py-8 text-sm text-gray-400">The waveform needs the original recording, which is not available in this saved preview.</p>) : evidence?.spectrogram_png_base64 ? <>
        <div className="relative pl-9">
          <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-[10px] text-gray-400"><span>8 kHz</span><span>4 kHz</span><span>0</span></div>
          <img src={`data:image/png;base64,${evidence.spectrogram_png_base64}`} alt="Measured spectral power across uniformly sampled audio windows. This is not a manipulation heatmap." className="w-full h-36 sm:h-44 rounded-md object-fill" />
        </div>
        <div className="flex justify-between text-[10px] text-gray-400 mt-2 pl-9"><span>0:00</span><span>{time(duration / 2)}</span><span>{time(duration)}</span></div>
        <p className="text-xs leading-5 text-gray-400 mt-3">Measured frequency energy across the recording. Brighter colors indicate stronger energy, not fake regions. This sampled overview does not explain the model’s verdict.</p>
      </> : <p role="status" className="py-9 text-sm text-gray-400">No measured spectrogram was returned for this scan. Select Waveform to inspect the recording.</p>}
    </section>
    <section className="rounded-xl border border-gray-800 bg-[#12121f] p-4 sm:p-5">
      <h3 className="text-sm font-semibold text-white">How to manually verify this clip</h3>
      <p className="text-xs leading-5 text-gray-400 mt-1 mb-4">These are listening prompts, not model findings or proof of synthesis. Check a box after reviewing that aspect.</p>
      <div className="space-y-3">
        {checks.map(([title, description]) => <label key={title} className="flex items-start gap-3 cursor-pointer text-sm leading-6 text-gray-300">
          <input type="checkbox" className="mt-1.5 h-4 w-4 shrink-0 accent-cyan-400" />
          <span><strong className="font-semibold text-white">{title}: </strong>{description}</span>
        </label>)}
      </div>
      <p className="text-xs text-gray-500 leading-5 mt-4">The classifier does not verify specific manipulated timestamps. Natural human speech can also contain irregular pitch, pauses, edits, and noise changes.</p>
    </section>
  </div>;
}
