import React from 'react';

export function NeuroLogo({ size = 24 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Downward Parabola */}
      <path d="M 1 18 Q 12 -5 23 18 Z" fill="#7c3aed" opacity="0.85" />
      {/* Upward Parabola */}
      <path d="M 1 6 Q 12 29 23 6 Z" fill="#06b6d4" opacity="0.85" style={{ mixBlendMode: 'screen' }} />
    </svg>
  );
}
