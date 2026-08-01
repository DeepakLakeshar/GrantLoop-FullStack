import { ShieldCheck } from "lucide-react";

interface VerificationBadgeProps {
  label?: string;
}

/** The recurring "checkmark + institutional trust" pill seen across
 * Cause Listing, Campaign Detail, and Case Submission. */
export function VerificationBadge({ label = "Verified" }: VerificationBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <ShieldCheck className="w-[18px] h-[18px] text-primary" strokeWidth={2.5} />
      <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">
        {label}
      </span>
    </div>
  );
}
