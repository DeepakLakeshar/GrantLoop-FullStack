interface ProgressRingProps {
  percentage: number;
  size?: number;
  label?: string;
}

export function ProgressRing({ percentage, size = 80, label }: ProgressRingProps) {
  const radius = size / 2 - 6;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(100, percentage) / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          className="text-surface-container-high"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="currentColor"
          strokeWidth={8}
        />
        <circle
          className="text-secondary transition-all duration-1000"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="currentColor"
          strokeWidth={8}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="font-headline-sm text-primary">{label ?? `${Math.round(percentage)}%`}</span>
      </div>
    </div>
  );
}
