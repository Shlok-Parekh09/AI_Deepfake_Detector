import React, { useEffect, useRef, useState } from 'react';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  opacity: number;
  id: number;
}

const TechnicalBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize particles
    const particleCount = 50;
    const particles: Particle[] = [];
    
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        opacity: Math.random() * 0.5 + 0.1,
        id: i
      });
    }
    
    particlesRef.current = particles;

    const drawDotGrid = () => {
      const gridSize = 30;
      const dotSize = 1;
      
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
      
      // Draw vertical lines
      for (let x = 0; x <= canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      
      // Draw horizontal lines
      for (let y = 0; y <= canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }
      
      // Draw dots at intersections
      for (let x = 0; x <= canvas.width; x += gridSize) {
        for (let y = 0; y <= canvas.height; y += gridSize) {
          ctx.beginPath();
          ctx.arc(x, y, dotSize, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    };

    const drawParticles = () => {
      const particles = particlesRef.current;
      const maxDistance = 150;
      
      // Update particle positions
      particles.forEach(particle => {
        particle.x += particle.vx;
        particle.y += particle.vy;
        
        // Bounce off edges
        if (particle.x <= 0 || particle.x >= canvas.width) {
          particle.vx *= -1;
        }
        if (particle.y <= 0 || particle.y >= canvas.height) {
          particle.vy *= -1;
        }
        
        // Fade particles near edges
        const edgeDistance = 100;
        const distToLeft = particle.x;
        const distToRight = canvas.width - particle.x;
        const distToTop = particle.y;
        const distToBottom = canvas.height - particle.y;
        
        const minEdgeDist = Math.min(distToLeft, distToRight, distToTop, distToBottom);
        
        if (minEdgeDist < edgeDistance) {
          particle.opacity = Math.max(0.05, (minEdgeDist / edgeDistance) * 0.4);
        } else {
          particle.opacity = Math.random() * 0.3 + 0.1;
        }
      });
      
      // Draw connections
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 0.5;
      
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < maxDistance) {
            const opacity = (1 - distance / maxDistance) * 0.2;
            ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
      
      // Draw particles
      particles.forEach(particle => {
        ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, 2, 0, Math.PI * 2);
        ctx.fill();
      });
    };

    const animate = () => {
      ctx.fillStyle = '#0D0D12';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      drawDotGrid();
      drawParticles();
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
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
        zIndex: 2,
      }}
    />
  );
};

export default TechnicalBackground;
