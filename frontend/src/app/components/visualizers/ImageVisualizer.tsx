import { useState } from 'react';

interface ImageVisualizerProps {
  mediaUrl: string;
  aiSummary?: string;
  detectedTool?: string;
}

export function ImageVisualizer({ mediaUrl, aiSummary, detectedTool }: ImageVisualizerProps) {
  const [failedUrl, setFailedUrl] = useState('');
  return (
    <div className="w-full rounded-2xl overflow-hidden bg-[#0a0a14] border border-gray-800 shadow-2xl">
      <div className="relative w-full aspect-video bg-black flex items-center justify-center">
        {failedUrl === mediaUrl ? <p role="status" className="px-5 text-sm text-gray-400">This browser cannot preview the image format. The model result remains available.</p> : <img key={mediaUrl} src={mediaUrl} alt="Analysis target" className="absolute w-full h-full object-contain" onError={() => setFailedUrl(mediaUrl)} />}
      </div>
      <div className="p-4 text-sm leading-6 text-gray-400">
        {aiSummary && <p>{aiSummary}</p>}
        {detectedTool && detectedTool !== 'Unknown' && <p className="mt-2">Embedded software tag: {detectedTool}. Metadata is not proof of origin.</p>}
      </div>
    </div>
  );
}
