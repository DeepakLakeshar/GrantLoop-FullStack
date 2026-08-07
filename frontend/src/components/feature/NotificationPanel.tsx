import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { CheckCircle2 } from "lucide-react";
import { Spinner } from "@/components/shared/Spinner";
import { useNotifications, useMarkNotificationRead, useMarkAllNotificationsRead } from "@/hooks/useNotifications";
import { formatDate } from "@/lib/format";

interface NotificationPanelProps {
  onClose: () => void;
}

export function NotificationPanel({ onClose }: NotificationPanelProps) {
  const ref = useRef<HTMLDivElement>(null);
  const { data: notificationsData, isLoading } = useNotifications();
  const { mutate: markRead } = useMarkNotificationRead();
  const { mutate: markAllRead, isPending: isMarkingAll } = useMarkAllNotificationsRead();

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  const notifications = notificationsData?.results ?? [];

  return (
    <div
      ref={ref}
      className="absolute right-0 top-12 w-96 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-lg z-50 max-h-[480px] flex flex-col"
    >
      <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center">
        <h3 className="font-headline-sm text-headline-sm text-primary">Notifications</h3>
        {notifications.length > 0 && (
          <button
            onClick={() => markAllRead()}
            disabled={isMarkingAll}
            className="text-label-caps text-primary font-bold hover:underline disabled:opacity-50"
          >
            Mark all read
          </button>
        )}
      </div>
      <div className="overflow-y-auto flex-1">
        {isLoading ? (
          <div className="px-6 py-16 flex justify-center">
            <Spinner size={24} />
          </div>
        ) : notifications.length === 0 ? (
          <div className="px-6 py-16 text-center">
            <CheckCircle2 className="w-8 h-8 text-outline-variant mx-auto mb-3" />
            <p className="text-body-md text-on-surface-variant">You're all caught up.</p>
          </div>
        ) : (
          <ul className="divide-y divide-outline-variant">
            {notifications.map((n) => (
              <li
                key={n.id}
                className={`px-6 py-4 transition-colors relative ${
                  !n.is_read ? "bg-primary-fixed/20 hover:bg-primary-fixed/30 cursor-pointer" : "hover:bg-surface-container-low"
                }`}
                onClick={() => {
                  if (!n.is_read) markRead(n.id);
                }}
              >
                <p className="font-body-md font-bold text-primary">{n.title}</p>
                <p className="text-data-table text-on-surface-variant mt-1">{n.body}</p>
                <span className="text-label-caps font-label-caps text-on-surface-variant mt-1 block">
                  {formatDate(n.created_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="px-6 py-3 border-t border-outline-variant text-center">
        <Link to="/settings/notifications" className="text-label-caps text-primary font-bold hover:underline" onClick={onClose}>
          Notification settings
        </Link>
      </div>
    </div>
  );
}
