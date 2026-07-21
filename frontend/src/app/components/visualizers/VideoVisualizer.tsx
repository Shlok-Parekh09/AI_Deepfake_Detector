import { useEffect, useRef, useState } from 'react';
import { FaceLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';

interface VideoVisualizerProps {
  mediaUrl: string;
  onPlayStateChange?: (playing: boolean) => void;
  externalVideoRef?: React.MutableRefObject<HTMLVideoElement | null>;
}

export function VideoVisualizer({ mediaUrl, onPlayStateChange, externalVideoRef }: VideoVisualizerProps) {
  const internalVideoRef = useRef<HTMLVideoElement>(null);
  const videoRef = externalVideoRef || internalVideoRef;
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [faceLandmarker, setFaceLandmarker] = useState<FaceLandmarker | null>(null);
  const [hasFace, setHasFace] = useState(false);

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
          runningMode: "VIDEO",
          numFaces: 1 // Optimize for single face, increase if needed
        });
        
        if (!active) return;
        setFaceLandmarker(landmarker);
        setIsLoaded(true);
      } catch (error) {
        console.error("Failed to load FaceLandmarker:", error);
      }
    }

    initMediaPipe();

    return () => {
      active = false;
    };
  }, []);

  // Play video only after ML model is loaded
  useEffect(() => {
    if (isLoaded && videoRef.current) {
      videoRef.current.play().catch(e => console.error("Video play prevented:", e));
    }
  }, [isLoaded]);

  useEffect(() => {
    let animationFrameId: number;
    let lastVideoTime = -1;

    const renderLoop = async () => {
      if (
        !faceLandmarker ||
        !videoRef.current ||
        !canvasRef.current ||
        videoRef.current.readyState < 2
      ) {
        animationFrameId = requestAnimationFrame(renderLoop);
        return;
      }

      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");

      if (!ctx) return;

      // Sync canvas dimensions with video native resolution
      if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }

      const startTimeMs = performance.now();
      
      if (video.currentTime !== lastVideoTime) {
        lastVideoTime = video.currentTime;
        
        // Detect faces
        const results = faceLandmarker.detectForVideo(video, startTimeMs);
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (results.faceLandmarks && results.faceLandmarks.length > 0) {
          setHasFace(true);
          const drawingUtils = new DrawingUtils(ctx);
          
          for (const landmarks of results.faceLandmarks) {
            // Draw tessellation (the fine wireframe mesh across the whole face)
            drawingUtils.drawConnectors(
              landmarks,
              FaceLandmarker.FACE_LANDMARKS_TESSELATION,
              { color: "rgba(255, 255, 255, 0.2)", lineWidth: 0.5, fillColor: "transparent" }
            );
            
            // Draw key facial contours for AI analysis emphasis (Cyan/Blue glowing effect)
            drawingUtils.drawConnectors(
              landmarks,
              FaceLandmarker.FACE_LANDMARKS_FACE_OVAL,
              { color: "rgba(96, 165, 250, 0.8)", lineWidth: 1.5 }
            );
            drawingUtils.drawConnectors(
              landmarks,
              FaceLandmarker.FACE_LANDMARKS_RIGHT_EYE,
              { color: "rgba(96, 165, 250, 0.8)", lineWidth: 1.5 }
            );
            drawingUtils.drawConnectors(
              landmarks,
              FaceLandmarker.FACE_LANDMARKS_LEFT_EYE,
              { color: "rgba(96, 165, 250, 0.8)", lineWidth: 1.5 }
            );
            drawingUtils.drawConnectors(
              landmarks,
              FaceLandmarker.FACE_LANDMARKS_LIPS,
              { color: "rgba(96, 165, 250, 0.8)", lineWidth: 1.5 }
            );
          }
        } else {
          setHasFace(false);
        }
      }

      animationFrameId = requestAnimationFrame(renderLoop);
    };

    if (isLoaded) {
      animationFrameId = requestAnimationFrame(renderLoop);
    }

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [isLoaded, faceLandmarker]);

  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-black aspect-video border border-gray-800 shadow-2xl flex items-center justify-center">
      {/* Loading overlay if ML model is booting */}
      {!isLoaded && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-indigo-400 text-xs font-semibold tracking-widest uppercase">Loading Face Mesh Model...</p>
        </div>
      )}

      <video
        ref={videoRef}
        src={mediaUrl}
        className="absolute w-full h-full object-contain"
        muted={false}
        loop
        playsInline
        crossOrigin={mediaUrl.startsWith('blob:') ? undefined : "anonymous"}
        onPlay={() => onPlayStateChange?.(true)}
        onPause={() => onPlayStateChange?.(false)}
      />
      
      {/* Canvas for the mesh overlay */}
      <canvas
        ref={canvasRef}
        className="absolute w-full h-full object-contain pointer-events-none"
        style={{ zIndex: 10 }}
      />

      {/* Analytics Overlay (only shows when face is detected) */}
      <div className={`absolute top-4 left-4 flex gap-2 transition-opacity duration-300 ${hasFace ? 'opacity-100' : 'opacity-0'}`} style={{ zIndex: 15 }}>
        <div className="bg-black/60 backdrop-blur-sm border border-emerald-500/30 px-3 py-1.5 rounded-md flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] uppercase tracking-wider font-semibold text-emerald-400">Face Tracked</span>
        </div>
      </div>
    </div>
  );
}
