import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string;
  trend?: string;
  footer?: ReactNode;
}

export function MetricCard({ label, value, trend, footer }: MetricCardProps) {
  return (
    <div className="bg-surface-container-lowest p-6 border border-outline-variant rounded-lg flex flex-col justify-between">
      <div>
        <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">
          {label}
        </span>
        <h2 className="font-headline-md text-headline-md font-bold text-primary mt-2">{value}</h2>
      </div>
      {trend && (
        <div className="mt-4 flex items-center gap-2 text-secondary font-bold">
          <span className="text-data-table font-data-table">{trend}</span>
        </div>
      )}
      {footer && <div className="mt-4">{footer}</div>}
    </div>
  );
}
