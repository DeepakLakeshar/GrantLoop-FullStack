import { Loader2 } from "lucide-react";

interface SpinnerProps {
  size?: number;
  className?: string;
}

/** The one loading indicator for the whole app. No page should invent
 * its own — this is the single reusable spinner referenced by "use
 * existing design system components, no new loaders." None existed
 * before Phase 2, so this is the first and only one. */
export function Spinner({ size = 18, className = "" }: SpinnerProps) {
  return <Loader2 className={`animate-spin ${className}`} width={size} height={size} aria-hidden="true" />;
}
