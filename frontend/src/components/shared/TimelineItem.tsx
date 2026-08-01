import type { ReactNode } from "react";

interface TimelineItemProps {
  title: string;
  timestamp: string;
  description?: string;
  state?: "completed" | "active" | "pending";
  isLast?: boolean;
  children?: ReactNode; // e.g. evidence thumbnails, amount details
}

const DOT_STYLES: Record<NonNullable<TimelineItemProps["state"]>, string> = {
  completed: "bg-secondary",
  active: "bg-primary ring-4 ring-primary-fixed",
  pending: "bg-outline-variant",
};

export function TimelineItem({
  title,
  timestamp,
  description,
  state = "completed",
  isLast = false,
  children,
}: TimelineItemProps) {
  return (
    <div className="relative pl-10">
      {!isLast && <div className="absolute left-[11px] top-6 bottom-[-24px] w-[2px] bg-outline-variant" />}
      <div className={`absolute left-0 top-1 w-6 h-6 rounded-full flex items-center justify-center z-10 ${DOT_STYLES[state]}`} />
      <div className={state === "pending" ? "opacity-50" : ""}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-1 mb-2">
          <h4 className="font-body-md text-body-md font-bold text-primary">{title}</h4>
          <span className="font-label-caps text-label-caps text-on-surface-variant">{timestamp}</span>
        </div>
        {description && (
          <p className="font-body-md text-body-md text-on-surface-variant mb-2">{description}</p>
        )}
        {children}
      </div>
    </div>
  );
}
