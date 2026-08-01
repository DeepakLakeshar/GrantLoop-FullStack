interface ProgressBarProps {
  percentage: number; // 0-100
  label?: string;
  sublabel?: string;
  height?: "sm" | "md";
}

export function ProgressBar({ percentage, label, sublabel, height = "sm" }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, percentage));
  const barHeight = height === "sm" ? "h-1.5" : "h-2";

  return (
    <div className="space-y-1">
      {(label || sublabel) && (
        <div className="flex justify-between font-label-caps text-label-caps">
          {label && <span className="font-bold text-primary">{label}</span>}
          {sublabel && <span className="text-on-surface-variant">{sublabel}</span>}
        </div>
      )}
      <div className={`w-full bg-surface-container-highest rounded-full overflow-hidden ${barHeight}`}>
        <div
          className="h-full bg-secondary transition-all duration-1000"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
