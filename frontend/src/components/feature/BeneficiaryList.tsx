import { Users } from "lucide-react";
import type { Beneficiary } from "@/types/entities";
import { StatusBadge } from "@/components/shared/StatusBadge";

interface BeneficiaryListProps {
  beneficiaries: Beneficiary[];
}

export function BeneficiaryList({ beneficiaries }: BeneficiaryListProps) {
  if (beneficiaries.length === 0) return null;

  return (
    <div className="space-y-3">
      {beneficiaries.map((b) => (
        <div key={b.id} className="flex items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant rounded-lg">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-primary shrink-0" />
            <div>
              <p className="font-body-md font-bold text-primary">{b.name}</p>
              <p className="text-data-table text-on-surface-variant">{b.contact_email}</p>
            </div>
          </div>
          <StatusBadge status={b.verification_status} />
        </div>
      ))}
    </div>
  );
}
