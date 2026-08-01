import type { FundAllocation } from "@/types/entities";

interface FundAllocationChartProps {
  allocation: FundAllocation;
}

// Fixed to the schema's three real fields — Beneficiary/Execution/Platform.
// This replaces the original mockup's invented Hardware/Logistics/Ops
// categories, per the frozen Frontend Architecture Review's approved
// correction #2. Data mapping only — the donut itself is unchanged.
const SEGMENT_COLOR = {
  beneficiary: "#2c694e", // secondary
  execution: "#adc7f7", // primary-fixed-dim
  platform: "#002045", // primary
};

export function FundAllocationChart({ allocation }: FundAllocationChartProps) {
  const segments = [
    { label: "Beneficiary", value: allocation.beneficiary_percentage, color: SEGMENT_COLOR.beneficiary },
    { label: "Execution", value: allocation.execution_percentage, color: SEGMENT_COLOR.execution },
    { label: "Platform", value: allocation.platform_percentage, color: SEGMENT_COLOR.platform },
  ];

  const circumference = 2 * Math.PI * 40;
  let cumulativeOffset = 0;

  return (
    <div className="grid md:grid-cols-2 gap-gutter items-center">
      <div className="relative aspect-square flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" fill="transparent" r="40" stroke="#e2e8f0" strokeWidth="12" />
          {segments.map((seg) => {
            const dash = (seg.value / 100) * circumference;
            const el = (
              <circle
                key={seg.label}
                cx="50"
                cy="50"
                fill="transparent"
                r="40"
                stroke={seg.color}
                strokeDasharray={`${dash} ${circumference}`}
                strokeDashoffset={-cumulativeOffset}
                strokeWidth="12"
              />
            );
            cumulativeOffset += dash;
            return el;
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-headline-sm text-headline-sm text-primary">{allocation.beneficiary_percentage}%</span>
          <span className="font-label-caps text-label-caps text-on-surface-variant">DIRECT IMPACT</span>
        </div>
      </div>
      <div className="space-y-6">
        {segments.map((seg) => (
          <div key={seg.label} className="flex justify-between items-center border-b border-outline-variant pb-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: seg.color }} />
              <span className="font-medium">{seg.label}</span>
            </div>
            <span className="font-label-caps">{seg.value}%</span>
          </div>
        ))}
        <p className="text-body-md text-on-surface-variant italic pt-2">
          Platform fees are configurable per campaign and may be as low as 0%.
        </p>
      </div>
    </div>
  );
}
