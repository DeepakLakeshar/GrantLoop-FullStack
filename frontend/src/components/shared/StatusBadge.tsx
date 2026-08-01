import { CheckCircle2, Clock, XCircle, ShieldAlert } from "lucide-react";

type BadgeTone = "success" | "pending" | "error" | "neutral";

const TONE_STYLES: Record<BadgeTone, string> = {
  success: "bg-secondary-container text-on-secondary-container",
  pending: "bg-surface-container-high text-on-surface-variant",
  error: "bg-error-container text-on-error-container",
  neutral: "bg-surface-container-highest text-on-surface-variant",
};

const TONE_ICON: Record<BadgeTone, React.ComponentType<{ className?: string }>> = {
  success: CheckCircle2,
  pending: Clock,
  error: XCircle,
  neutral: ShieldAlert,
};

// Maps every status value that appears anywhere in the frozen schema to a
// tone. Add new statuses here, never invent a new visual style per status.
const STATUS_TONE_MAP: Record<string, BadgeTone> = {
  // Campaign
  draft: "neutral",
  pending_verification: "pending",
  live: "success",
  completed: "success",
  rejected: "error",
  archived: "neutral",
  // Verification / FundRelease / Document
  pending: "pending",
  approved: "success",
  released: "success",
  verified: "success",
  more_info_requested: "pending",
  suspended: "error",
  // Donation
  success: "success",
  failed: "error",
  refunded: "neutral",
  // Milestone
  in_progress: "pending",
};

interface StatusBadgeProps {
  status: string;
  label?: string; // override display text; falls back to the status value
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const tone = STATUS_TONE_MAP[status] ?? "neutral";
  const Icon = TONE_ICON[tone];
  const displayText = (label ?? status).replace(/_/g, " ").toUpperCase();

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-label-caps font-bold tracking-wide ${TONE_STYLES[tone]}`}
    >
      <Icon className="w-3.5 h-3.5" />
      {displayText}
    </span>
  );
}
