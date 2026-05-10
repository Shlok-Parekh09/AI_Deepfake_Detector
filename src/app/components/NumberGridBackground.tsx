import React, { useEffect, useRef } from 'react';

export const NumberGridBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let particles: any[] = [];
    let mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    let targetMouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };

    const handleMouseMove = (e: MouseEvent) => {
      targetMouse.x = e.clientX;
      targetMouse.y = e.clientY;
    };
    window.addEventListener('mousemove', handleMouseMove);

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    const initParticles = () => {
      particles = [];
      const spacing = 32;
      const cols = Math.ceil(canvas.width / spacing) + 2;
      const rows = Math.ceil(canvas.height / spacing) + 2;
      
      for (let i = -1; i < cols; i++) {
        for (let j = -1; j < rows; j++) {
          particles.push({
            baseX: i * spacing,
            baseY: j * spacing,
            char: Math.floor(Math.random() * 10).toString(),
            offsetX: (Math.random() - 0.5) * 12,
            offsetY: (Math.random() - 0.5) * 12,
            sizeOffset: Math.random() * 6,
            charSpeed: Math.random() * 0.03,
            charValue: Math.random() * 10,
          });
        }
      }
    };

    window.addEventListener('resize', resize);
    resize();

    const RADIUS = 140;

    const render = () => {
      // Smooth mouse follow
      mouse.x += (targetMouse.x - mouse.x) * 0.15;
      mouse.y += (targetMouse.y - mouse.y) * 0.15;

      // Dark background to wipe the frame
      ctx.fillStyle = '#08080C';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      for (let p of particles) {
        // Occasionally change character for a matrix feel
        p.charValue += p.charSpeed;
        if (p.charValue > 10) {
          p.charValue = 0;
          p.char = Math.floor(Math.random() * 10).toString();
        }

        const dx = p.baseX - mouse.x;
        const dy = p.baseY - mouse.y;
        const dist = Math.hypot(dx, dy);

        let x = p.baseX;
        let y = p.baseY;
        let opacity = 0.08;
        let fontSize = 13;
        let color = '56, 189, 248'; // Cyan color

        if (dist < RADIUS) {
          // Push outward
          const angle = Math.atan2(dy, dx);
          // Add some scatter based on their original position
          const pushRadius = RADIUS + p.offsetX; 
          x = mouse.x + Math.cos(angle) * pushRadius;
          y = mouse.y + Math.sin(angle) * pushRadius;
          
          opacity = 0.9;
          fontSize = 18 + p.sizeOffset;
          color = '167, 139, 250'; // Make edge slightly purple/cyan mix, let's use cyan '56, 189, 248'
        } else if (dist < RADIUS + 100) {
          // Glow area right outside the radius
          const intensity = 1 - (dist - RADIUS) / 100;
          opacity = 0.08 + 0.82 * intensity;
          fontSize = 13 + 5 * intensity;
        }

        ctx.font = `600 ${fontSize}px 'Inter', monospace`;
        ctx.fillStyle = `rgba(${color}, ${opacity})`;
        ctx.fillText(p.char, x, y);
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
