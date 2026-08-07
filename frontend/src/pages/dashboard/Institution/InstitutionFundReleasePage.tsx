import { UnsupportedFeaturePage } from "@/components/shared/UnsupportedFeaturePage";

export function InstitutionFundReleasePage() {
  return (
    <UnsupportedFeaturePage 
      title="Fund Releases"
      featureName="Fund release management"
      reason="because fund release workflows are deferred from the v1.0.0 milestone."
    />
  );
}
