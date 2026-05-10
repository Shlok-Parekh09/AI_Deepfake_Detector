import React from 'react';
import { Brain } from 'lucide-react';

export default function HiddenGame() {
  return (
    <div style={{ 
      textAlign: 'center', 
      animation: 'fadeIn 0.8s ease-out forwards',
      background: 'rgba(5,5,15,0.7)',
      backdropFilter: 'blur(30px)',
      padding: '80px',
      borderRadius: '40px',
      border: '1px solid rgba(124,58,237,0.3)',
      boxShadow: '0 0 100px rgba(124,58,237,0.15)',
      width: '100%',
      maxWidth: 800,
      margin: '0 auto',
    }}>
      <div style={{
        width: 100, height: 100, borderRadius: 25, 
        background: 'rgba(124,58,237,0.1)', 
        border: '1px solid rgba(124,58,237,0.4)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 32px',
        boxShadow: '0 0 50px rgba(124,58,237,0.3)',
        animation: 'pulse 2s infinite'
      }}>
        <Brain size={50} color="#a78bfa" />
      </div>
      <h2 style={{ fontSize: 42, fontWeight: 900, marginBottom: 16, background: 'linear-gradient(90deg,#a78bfa,#60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        GAME UNLOCKED
      </h2>
      <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: 18, maxWidth: 450, margin: '0 auto' }}>
        Placeholder - I will design the game here later.
      </p>
    </div>
  );
}
