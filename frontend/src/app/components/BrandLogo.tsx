type BrandLogoProps = {
  size?: number;
  className?: string;
};

export default function BrandLogo({ size = 32, className = "" }: BrandLogoProps) {
  return (
    <img
      src="/synphi-logo.svg"
      alt="SynPhi logo"
      width={size}
      height={size}
      className={`shrink-0 object-contain ${className}`}
      style={{ width: size, height: size }}
    />
  );
}
