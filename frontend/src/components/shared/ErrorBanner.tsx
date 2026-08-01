import { WifiOff, ShieldAlert, ServerCrash, LogOut, AlertCircle } from "lucide-react";
import type { ApiErrorKind } from "@/lib/api/errors";

const KIND_CONFIG: Record<ApiErrorKind, { icon: React.ComponentType<{ className?: string }>; defaultMessage: string }> = {
  network: { icon: WifiOff, defaultMessage: "Unable to reach the server. Check your connection and try again." },
  unauthorized: { icon: LogOut, defaultMessage: "Your session has expired. Please sign in again." },
  forbidden: { icon: ShieldAlert, defaultMessage: "You don't have permission to do that." },
  server: { icon: ServerCrash, defaultMessage: "Something went wrong on our end. Please try again shortly." },
  validation: { icon: AlertCircle, defaultMessage: "Check the highlighted fields and try again." },
  unknown: { icon: AlertCircle, defaultMessage: "Something went wrong. Please try again." },
};

interface ErrorBannerProps {
  kind: ApiErrorKind;
  message?: string;
}

/** Reused anywhere an API call can fail in a way that isn't a per-field
 * validation error — not just auth. Same card styling as everything else
 * (border-outline-variant, error-container for the icon accent). */
export function ErrorBanner({ kind, message }: ErrorBannerProps) {
  const { icon: Icon, defaultMessage } = KIND_CONFIG[kind];
  return (
    <div className="flex items-start gap-3 p-4 bg-error-container/20 border border-error/20 rounded-lg" role="alert">
      <Icon className="w-5 h-5 text-error shrink-0 mt-0.5" />
      <p className="text-body-md text-on-error-container">{message ?? defaultMessage}</p>
    </div>
  );
}
