import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { ROLE_HOME } from "@/lib/auth/roleRedirect";
import { Spinner } from "@/components/shared/Spinner";
import type { UserRole } from "@/types/entities";

function SessionRestoring() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Spinner size={28} className="text-primary" />
    </div>
  );
}

/** Wraps auth pages (Login/Register/etc). Already-authenticated users are
 * bounced to their role's dashboard instead of seeing the login form
 * again. */
export function PublicRoute() {
  const { status, user } = useAuth();

  if (status === "restoring") return <SessionRestoring />;
  if (status === "authenticated" && user) return <Navigate to={ROLE_HOME[user.role]} replace />;
  return <Outlet />;
}

/** Wraps any page that requires a logged-in user, regardless of role. */
export function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "restoring") return <SessionRestoring />;
  if (status === "unauthenticated") return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}

/** Wraps a page that requires a logged-in user AND one of the given
 * roles. A logged-in user with the wrong role is redirected to their own
 * dashboard, not to /login — they're authenticated, just not authorized
 * for this specific page. */
export function RoleProtectedRoute({ allowedRoles }: { allowedRoles: UserRole[] }) {
  const { status, user } = useAuth();
  const location = useLocation();

  if (status === "restoring") return <SessionRestoring />;
  if (status === "unauthenticated" || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to={ROLE_HOME[user.role]} replace />;
  }
  return <Outlet />;
}
