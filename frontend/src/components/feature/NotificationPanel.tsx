import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { CheckCircle2 } from "lucide-react";
import type { Notification } from "@/types/entities";

// Placeholder data shape until wired to GET /api/v1/notifications/.
// Structure matches the frozen Notification type exactly.
const MOCK_NOTIFICATIONS: Notification[] = [];

interface NotificationPanelProps {
  onClose: () => void;
}

/** Built from the same card/list styling already used everywhere else
 * (surface-container-lowest card, outline-variant border, label-caps
 * timestamps). No new visual pattern. */
export function NotificationPanel({ onClose }: NotificationPanelProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  return (
    <div
      ref={ref}
      className="absolute right-0 top-12 w-96 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-lg z-50 max-h-[480px] flex flex-col"
    >
      <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center">
        <h3 className="font-headline-sm text-headline-sm text-primary">Notifications</h3>
        <button className="text-label-caps text-primary font-bold hover:underline">
          Mark all read
        </button>
      </div>
      <div className="overflow-y-auto flex-1">
        {MOCK_NOTIFICATIONS.length === 0 ? (
          <div className="px-6 py-16 text-center">
            <CheckCircle2 className="w-8 h-8 text-outline-variant mx-auto mb-3" />
            <p className="text-body-md text-on-surface-variant">You're all caught up.</p>
          </div>
        ) : (
          <ul className="divide-y divide-outline-variant">
            {MOCK_NOTIFICATIONS.map((n) => (
              <li
                key={n.id}
                className={`px-6 py-4 hover:bg-surface-container-low transition-colors ${
                  !n.is_read ? "bg-primary-fixed/20" : ""
                }`}
              >
                <p className="font-body-md font-bold text-primary">{n.title}</p>
                <p className="text-data-table text-on-surface-variant mt-1">{n.body}</p>
                <span className="text-label-caps font-label-caps text-on-surface-variant mt-1 block">
                  {n.created_at}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="px-6 py-3 border-t border-outline-variant text-center">
        <Link to="/settings/notifications" className="text-label-caps text-primary font-bold hover:underline">
          Notification settings
        </Link>
      </div>
    </div>
  );
}
