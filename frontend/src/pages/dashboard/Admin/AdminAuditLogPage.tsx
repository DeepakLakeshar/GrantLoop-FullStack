import { UnsupportedFeaturePage } from "@/components/shared/UnsupportedFeaturePage";

export function AdminAuditLogPage() {
  return (
    <UnsupportedFeaturePage 
      title="Audit Log"
      featureName="Detailed audit logging"
      reason="because comprehensive audit logging is scheduled for a future milestone."
    />
  );
}
