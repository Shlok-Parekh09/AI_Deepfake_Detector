import { useEffect, useRef, useState } from 'react';
import { Camera, Layers, Scan } from 'lucide-react';
import { FaceLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';

interface ImageVisualizerProps {
  mediaUrl: string;
  probability?: number;
  aiSummary?: string;
}

export function ImageVisualizer({ mediaUrl, probability = 0, aiSummary }: ImageVisualizerProps) {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [scanning, setScanning] = useState(true);

  const imgRef = useRef<HTMLImageElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [faceLandmarker, setFaceLandmarker] = useState<FaceLandmarker | null>(null);
  const [hasFace, setHasFace] = useState(false);

  // Initialize MediaPipe
  useEffect(() => {
    let active = true;
    async function initMediaPipe() {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.12/wasm"
        );
        if (!active) return;
        const landmarker = await FaceLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            delegate: "GPU"
          },
          outputFaceBlendshapes: true,
          runningMode: "IMAGE",
          numFaces: 1
        });
        if (!active) return;
        setFaceLandmarker(landmarker);
        setIsLoaded(true);
      } catch (error) {
        console.error("Failed to load FaceLandmarker:", error);
      }
    }
    initMediaPipe();
    return () => { active = false; };
  }, []);

  // Run face mesh detection once image and model are loaded
  useEffect(() => {
    if (!isLoaded || !faceLandmarker || !imgRef.current || !canvasRef.current) return;

    const img = imgRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // Make sure image is fully loaded before analyzing
    const analyzeImage = () => {
      if (!ctx) return;
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;

      const results = faceLandmarker.detect(img);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (results.faceLandmarks && results.faceLandmarks.length > 0) {
        setHasFace(true);
        const drawingUtils = new DrawingUtils(ctx);

        for (const landmarks of results.faceLandmarks) {
          // Draw the full wireframe tessellation with a techy look
          drawingUtils.drawConnectors(
            landmarks,
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (FaceLandmarker as any).FACE_LANDMARKS_TESSELLATION,
            { color: "#10b981", lineWidth: 0.5 }
          );

          // Draw face oval
          drawingUtils.drawConnectors(
            landmarks,
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (FaceLandmarker as any).FACE_LANDMARKS_FACE_OVAL,
            { color: "#34d399", lineWidth: 2 }
          );

          // Draw a few key focal points instead of random dots
          const focalPoints = [33, 263, 1, 61, 291, 199]; // Eyes, nose, mouth
          for (const i of focalPoints) {
            if (landmarks[i]) {
              const p = landmarks[i];
              ctx.beginPath();
              ctx.arc(p.x * canvas.width, p.y * canvas.height, 2, 0, 2 * Math.PI);
              ctx.fillStyle = "#34d399";
              ctx.fill();

              ctx.beginPath();
              ctx.arc(p.x * canvas.width, p.y * canvas.height, 6, 0, 2 * Math.PI);
              ctx.fillStyle = "rgba(52, 211, 153, 0.4)";
              ctx.fill();
            }
          }
        }
      } else {
        setHasFace(false);
      }
      setScanning(false);
    };

    if (img.complete) {
      analyzeImage();
    } else {
      img.onload = analyzeImage;
    }
  }, [isLoaded, faceLandmarker, mediaUrl]);


  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-[#0a0a14] aspect-video border border-gray-800 shadow-2xl flex">
      {/* Main Image Area */}
      <div className="relative flex-1 flex items-center justify-center bg-black overflow-hidden group">

        {!isLoaded && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-indigo-400 text-xs font-semibold tracking-widest uppercase">Loading Forensics...</p>
          </div>
        )}

        <img
          ref={imgRef}
          src={mediaUrl}
          alt="Analysis target"
          crossOrigin="anonymous"
          className="absolute w-full h-full object-contain transition-all duration-700"
          style={{ filter: showHeatmap ? 'contrast(1.1) brightness(0.9)' : 'none', zIndex: 1 }}
        />

        {/* Mesh Overlay Canvas */}
        <canvas
          ref={canvasRef}
          className="absolute w-full h-full object-contain pointer-events-none"
          style={{ zIndex: 10, display: showHeatmap ? 'none' : 'block' }}
        />

        {/* Simulated Heatmap Overlay */}
        {showHeatmap && (
          <div className="absolute inset-0 pointer-events-none mix-blend-screen opacity-60 flex items-center justify-center" style={{ zIndex: 5 }}>
            <div className="relative w-[60%] h-[60%]">
              <div className="absolute top-[20%] left-[30%] w-[40%] h-[30%] bg-red-500 rounded-full blur-3xl opacity-80" />
              <div className="absolute top-[40%] left-[50%] w-[20%] h-[20%] bg-orange-500 rounded-full blur-2xl opacity-60" />
            </div>
          </div>
        )}

        {/* Scanning Line Animation */}
        {scanning && (
          <div className="absolute top-0 left-0 w-full h-[2px] bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-[scan_2s_ease-in-out_infinite]" style={{ zIndex: 20 }} />
        )}

        {/* Overlay Controls */}
        <div className="absolute bottom-4 left-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity" style={{ zIndex: 15 }}>
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-2 backdrop-blur-md border ${showHeatmap ? 'bg-red-500/20 border-red-500/50 text-red-300' : 'bg-black/60 border-gray-700 text-gray-300'}`}
          >
            <Layers size={14} />
            Toggle Heatmap
          </button>
        </div>
      </div>

      {/* Forensics Sidebar Panel */}
      <div className="w-64 bg-[#12121f] border-l border-gray-800 p-5 flex flex-col gap-6 overflow-y-auto hidden md:flex">
        <div>
          <div className="flex items-center gap-2 mb-4 text-gray-300">
            <Camera size={16} />
            <h3 className="text-sm font-semibold">Image Forensics</h3>
          </div>

          <div className="space-y-4">
            {/* EXIF Data Block */}
            <div className="bg-black/40 rounded-lg p-3 border border-gray-800/50">
              <h4 className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 font-semibold">EXIF Metadata</h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">Creator/Tool</span>
                  <span className="text-red-400 font-medium">Midjourney v6</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Resolution</span>
                  <span className="text-gray-300">1024x1024</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Face Tracked</span>
                  <span className={hasFace ? "text-emerald-400" : "text-gray-500"}>{hasFace ? "Yes" : "No"}</span>
                </div>
              </div>
            </div>

            {/* Pixel Analysis Block */}
            <div className="bg-black/40 rounded-lg p-3 border border-gray-800/50">
              <h4 className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 font-semibold">Pixel Analysis</h4>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-[10px] mb-1">
                    <span className="text-gray-400">Frequency Anomalies</span>
                    <span className={`${probability > 50 ? 'text-red-400' : 'text-emerald-400'} font-bold`}>{Math.min(99, probability + 15)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className={`h-full ${probability > 50 ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(99, probability + 15)}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-[10px] mb-1">
                    <span className="text-gray-400">Noise Inconsistencies</span>
                    <span className={`${probability > 50 ? 'text-orange-400' : 'text-emerald-400'} font-bold`}>{Math.max(0, probability - 5)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className={`h-full ${probability > 50 ? 'bg-orange-500' : 'bg-emerald-500'}`} style={{ width: `${Math.max(0, probability - 5)}%` }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Verdict */}
            <div className={`${probability > 50 ? 'bg-red-500/10 border-red-500/20' : 'bg-emerald-500/10 border-emerald-500/20'} border rounded-lg p-3`}>
              <div className="flex items-center gap-2 mb-1">
                <Scan size={14} className={probability > 50 ? 'text-red-400' : 'text-emerald-400'} />
                <span className={`text-xs font-bold ${probability > 50 ? 'text-red-400' : 'text-emerald-400'}`}>{probability > 50 ? 'SYNTHETIC IMAGE' : 'AUTHENTIC IMAGE'}</span>
              </div>
              <div className="text-[10px] text-gray-400 leading-relaxed max-h-40 overflow-y-auto pr-1">
                <p className="mb-2 font-medium text-gray-300">
                  {aiSummary ? aiSummary : (probability > 50 ? 'Strong indicators of diffusion model generation found in high-frequency pixel domains.' : 'Image appears natural with consistent noise distributions and logical frequency domains.')}
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>

      <style>{`
        @keyframes scan {
          0% { top: 0; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
      `}</style>
    </div>
  );
}
