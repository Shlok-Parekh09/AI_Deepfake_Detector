export function GandivaBowLogo({ size = 40, className = '' }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path d="M 14 3 Q 40 24 14 45" stroke="#f97316" strokeWidth="3.5" fill="none" strokeLinecap="round" />
      <line x1="14" y1="3" x2="14" y2="45" stroke="#fbbf24" strokeWidth="1.2" strokeLinecap="round" />
      <line x1="14" y1="24" x2="38" y2="24" stroke="#fbbf24" strokeWidth="1.4" strokeLinecap="round" />
      <polygon points="36,20 44,24 36,28" fill="#f97316" />
      <circle cx="14" cy="3" r="1.5" fill="#fbbf24" />
      <circle cx="14" cy="45" r="1.5" fill="#fbbf24" />
    </svg>
  );
}
