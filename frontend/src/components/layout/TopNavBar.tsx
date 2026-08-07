import { Link, NavLink } from "react-router-dom";
import { Bell } from "lucide-react";
import { useState } from "react";
import { NotificationPanel } from "@/components/feature/NotificationPanel";
import { useAuth } from "@/context/AuthContext";
import { useUnreadNotificationsCount } from "@/hooks/useNotifications";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive
    ? "text-primary border-b-2 border-primary font-bold pb-1"
    : "text-on-surface-variant font-medium hover:text-primary transition-colors";

export function TopNavBar() {
  const { status, user } = useAuth();
  const isAuthenticated = status === "authenticated" && !!user;
  const { data: unreadCount = 0 } = useUnreadNotificationsCount(isAuthenticated);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 flex justify-between items-center px-margin-desktop w-full h-16 max-w-container-max mx-auto bg-surface-container-lowest border-b border-outline-variant">
      <div className="flex items-center gap-8">
        <Link to="/" className="text-headline-md font-headline-md font-bold text-primary">
          GrantLoop
        </Link>
        <nav className="hidden md:flex gap-6 items-center">
          <NavLink to="/causes" className={navLinkClass}>Causes</NavLink>
          <NavLink to="/pricing" className={navLinkClass}>Transparency</NavLink>
          <NavLink to="/how-it-works" className={navLinkClass}>How it Works</NavLink>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        {isAuthenticated ? (
          <>
            <div className="relative">
              <button
                aria-label="Notifications"
                onClick={() => setNotificationsOpen((v) => !v)}
                className="relative p-2 text-on-surface-variant hover:bg-surface-container-high rounded-full transition-colors"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 bg-error text-on-error text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </button>
              {notificationsOpen && (
                <NotificationPanel onClose={() => setNotificationsOpen(false)} />
              )}
            </div>
            <Link
              to="/profile"
              className="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center text-primary font-bold text-label-caps"
            >
              {user.username.slice(0, 1).toUpperCase()}
            </Link>
          </>
        ) : (
          <>
            <Link to="/login" className="text-on-surface-variant font-medium hover:text-primary transition-all">
              Sign In
            </Link>
            <Link
              to="/causes"
              className="bg-primary text-white px-6 py-2 rounded font-bold hover:bg-primary-container transition-all active:scale-95"
            >
              Donate Now
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
