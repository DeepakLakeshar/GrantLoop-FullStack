import { StatusBadge } from "@/components/shared/StatusBadge";
import { ProgressBar } from "@/components/shared/ProgressBar";
import type { Milestone } from "@/types/entities";
import { formatCurrency, formatDate } from "@/lib/format";

interface MilestoneCardProps {
  milestone: Milestone;
  currency: string;
}

export function MilestoneCard({ milestone, currency }: MilestoneCardProps) {
  const percentage = milestone.target_amount > 0 ? (milestone.released_amount / milestone.target_amount) * 100 : 0;

  return (
    <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-6 space-y-4">
      <div className="flex justify-between items-start gap-4">
        <div>
          <h4 className="font-body-md font-bold text-primary">{milestone.title}</h4>
          <p className="text-body-md text-on-surface-variant mt-1">{milestone.description}</p>
        </div>
        <StatusBadge status={milestone.status} />
      </div>
      <ProgressBar
        percentage={percentage}
        label={formatCurrency(milestone.released_amount, currency)}
        sublabel={`of ${formatCurrency(milestone.target_amount, currency)}`}
      />
      <div className="flex justify-between text-label-caps font-label-caps text-on-surface-variant">
        <span>{milestone.execution_partner?.organization ?? "Unassigned"}</span>
        {milestone.deadline && <span>Due {formatDate(milestone.deadline)}</span>}
      </div>
    </div>
  );
}
