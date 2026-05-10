import React, { useEffect, useRef } from 'react';

export const InteractiveGridBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouse = useRef({ x: -1000, y: -1000 });
  const targetMouse = useRef({ x: -1000, y: -1000 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    const gridSize = 40;
    const squares: { x: number; y: number; opacity: number; targetOpacity: number }[] = [];

    const handleMouseMove = (e: MouseEvent) => {
      targetMouse.current = { x: e.clientX, y: e.clientY };
    };

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initGrid();
    };

    const initGrid = () => {
      squares.length = 0;
      const cols = Math.ceil(canvas.width / gridSize);
      const rows = Math.ceil(canvas.height / gridSize);
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          squares.push({
            x: i * gridSize,
            y: j * gridSize,
            opacity: 0,
            targetOpacity: 0,
          });
        }
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('resize', resize);
    resize();

    const render = () => {
      // Smooth mouse follow
      mouse.current.x += (targetMouse.current.x - mouse.current.x) * 0.1;
      mouse.current.y += (targetMouse.current.y - mouse.current.y) * 0.1;

      ctx.fillStyle = '#05050f';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw Grid Lines (Subtle)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 0; x <= canvas.width; x += gridSize) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
      }
      for (let y = 0; y <= canvas.height; y += gridSize) {
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
      }
      ctx.stroke();

      const glowRadius = 150;

      for (const s of squares) {
        const dx = s.x + gridSize / 2 - mouse.current.x;
        const dy = s.y + gridSize / 2 - mouse.current.y;
        const dist = Math.hypot(dx, dy);

        if (dist < glowRadius) {
          s.targetOpacity = 1 - dist / glowRadius;
        } else {
          s.targetOpacity = 0;
        }

        // Smoothly interpolate opacity
        s.opacity += (s.targetOpacity - s.opacity) * 0.15;

        if (s.opacity > 0.01) {
          // Glow effect for the square
          ctx.fillStyle = `rgba(124, 58, 237, ${s.opacity * 0.15})`;
          ctx.fillRect(s.x, s.y, gridSize, gridSize);
          
          // Border glow
          ctx.strokeStyle = `rgba(167, 139, 250, ${s.opacity * 0.4})`;
          ctx.strokeRect(s.x + 0.5, s.y + 0.5, gridSize - 1, gridSize - 1);
        }
      }

      // Giant Cursor Glow
      const gradient = ctx.createRadialGradient(
        mouse.current.x, mouse.current.y, 0,
        mouse.current.x, mouse.current.y, glowRadius * 1.5
      );
      gradient.addColorStop(0, 'rgba(124, 58, 237, 0.15)');
      gradient.addColorStop(1, 'transparent');
      
      ctx.fillStyle = gradient;
      ctx.globalCompositeOperation = 'screen';
      ctx.beginPath();
      ctx.arc(mouse.current.x, mouse.current.y, glowRadius * 1.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalCompositeOperation = 'source-over';

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
      }}
    />
  );
};
