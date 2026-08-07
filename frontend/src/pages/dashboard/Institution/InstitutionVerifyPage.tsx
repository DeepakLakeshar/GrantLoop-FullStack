import { UnsupportedFeaturePage } from "@/components/shared/UnsupportedFeaturePage";

export function InstitutionVerifyPage() {
  return (
    <UnsupportedFeaturePage 
      title="Verification Queue"
      featureName="Dedicated beneficiary verification"
      reason="because a dedicated verification REST workflow is deferred from the v1.0.0 milestone."
    />
  );
}
