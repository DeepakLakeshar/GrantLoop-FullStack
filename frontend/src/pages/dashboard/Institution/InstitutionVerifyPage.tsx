import { FeatureUnavailablePage } from "@/components/shared/FeatureUnavailablePage";

export function InstitutionVerifyPage() {
  return (
    <FeatureUnavailablePage 
      title="Verification Queue"
      featureName="Dedicated beneficiary verification"
      reason="because a dedicated verification REST workflow is deferred from the v1.0.0 milestone."
    />
  );
}
