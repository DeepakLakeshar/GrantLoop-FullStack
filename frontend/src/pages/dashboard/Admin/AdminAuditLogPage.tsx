import { FeatureUnavailablePage } from "@/components/shared/FeatureUnavailablePage";

export function AdminAuditLogPage() {
  return (
    <FeatureUnavailablePage 
      title="Audit Log"
      featureName="Detailed audit logging"
      reason="because comprehensive audit logging is scheduled for a future milestone."
    />
  );
}
