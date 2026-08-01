import { TimelineItem } from "@/components/shared/TimelineItem";
import type { TransparencyLogEntry } from "@/types/entities";
import { formatDate } from "@/lib/format";

interface TransparencyTimelineProps {
  entries: TransparencyLogEntry[];
}

export function TransparencyTimeline({ entries }: TransparencyTimelineProps) {
  if (entries.length === 0) {
    return <p className="text-body-md text-on-surface-variant">No activity logged yet.</p>;
  }

  // Most recent first — matches the mockup's evidence timeline ordering.
  const sorted = [...entries].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <div className="space-y-6">
      {sorted.map((entry, i) => (
        <TimelineItem
          key={entry.id}
          title={entry.action}
          timestamp={formatDate(entry.timestamp)}
          state="completed"
          isLast={i === sorted.length - 1}
        />
      ))}
    </div>
  );
}
