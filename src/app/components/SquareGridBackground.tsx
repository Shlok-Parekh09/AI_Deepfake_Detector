import React, { useEffect, useRef } from 'react';

export const SquareGridBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let mouse = { x: -1000, y: -1000 };
    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };
    window.addEventListener('mousemove', handleMouseMove);

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    let animationFrameId: number;

    const cellOpacities = new Map<string, number>();

    const render = () => {
      ctx.fillStyle = '#08080C';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const gridSize = 60;
      const cols = Math.ceil(canvas.width / gridSize);
      const rows = Math.ceil(canvas.height / gridSize);

      const hoveredCol = Math.floor(mouse.x / gridSize);
      const hoveredRow = Math.floor(mouse.y / gridSize);

      if (hoveredCol >= 0 && hoveredCol < cols && hoveredRow >= 0 && hoveredRow < rows) {
        cellOpacities.set(`${hoveredCol},${hoveredRow}`, 1.0);
      }

      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const x = i * gridSize;
          const y = j * gridSize;
          const key = `${i},${j}`;

          let opacity = cellOpacities.get(key) || 0;

          if (opacity > 0) {
            ctx.fillStyle = `rgba(56, 189, 248, ${opacity * 0.4})`; // glowing blue
            ctx.fillRect(x, y, gridSize, gridSize);
            ctx.strokeStyle = `rgba(56, 189, 248, ${Math.max(opacity, 0.05)})`;
            ctx.strokeRect(x, y, gridSize, gridSize);
            
            opacity -= 0.025; // Decay speed, allows trail of ~10-15 bubbles depending on mouse speed
            if (opacity <= 0) {
              cellOpacities.delete(key);
            } else {
              cellOpacities.set(key, opacity);
            }
          } else {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'; // grid lines
            ctx.strokeRect(x, y, gridSize, gridSize);
          }
        }
      }

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
        pointerEvents: 'none'
      }}
    />
  );
};
